"""Reconcile a Tableau workbook's cached textscan schema with its CSV sources.

A ``.twb`` workbook embeds a cached description of each text data source,
including the field order (``ordinal``) of every CSV column. The Phase 13
audit regenerated the analytical CSVs and added ``season_length`` and
``order``, which shifted the ordinals of every later column. The cached
description in ``tableau/Retail_Demand_Forecasting.twb`` therefore no longer
matched the files it points at.

This script reads each data source's CSV headers, rebuilds the cached
``<columns>`` block and the column ``<metadata-record>`` entries to match,
and writes the workbook back only when something actually changed. It is
idempotent: a second run reports no changes.

A data source that carries an extract has two cached descriptions. The live
relation lists every CSV column in header order; the extract lists no field the
workbook hides, and numbers its own columns contiguously within what remains.
Tableau does that deliberately, so this script reproduces it rather than
fighting it: the live blocks are reconciled against the full header order and
the extract blocks against the visible subset. A field declared ``hidden`` is
never re-introduced, and a record outside the expected schema is preserved
rather than deleted.

Usage::

    python scripts/sync_tableau_workbook_schema.py --check
    python scripts/sync_tableau_workbook_schema.py
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# Tableau's remote-type codes for the textscan connector, with the local
# type, the default aggregation and any extra elements the type needs.
TYPE_MAP = {
    "integer": ("20", "Sum", ""),
    "real": ("5", "Sum", ""),
    "string": (
        "129",
        "Count",
        "{indent2}<scale>1</scale>\n",
        "{indent2}<width>1073741823</width>\n",
        "{indent2}<collation flag='0' name='LEN_RGB' />\n",
    ),
    "date": ("133", "Count", ""),
    "boolean": ("11", "Count", ""),
}

DATASOURCE_START = re.compile(
    r"<datasource caption='(?P<caption>[^']*)' inline='true' "
    r"name='(?P<name>[^']*)'"
)
TEXTSCAN = re.compile(r"<connection class='textscan'[^>]*filename='([^']+)'")
COLUMNS_BLOCK = re.compile(
    r"(?P<open><columns\b[^>]*>)(?P<body>.*?)(?P<close></columns>)",
    re.DOTALL,
)
COLUMN_LINE = re.compile(
    r"<column datatype='(?P<datatype>[^']+)' "
    r"name='(?P<name>[^']+)' ordinal='(?P<ordinal>\d+)' />"
)
METADATA_BLOCK = re.compile(
    r"(?P<open><metadata-records>)(?P<body>.*?)(?P<close></metadata-records>)",
    re.DOTALL,
)
METADATA_RECORD = re.compile(
    r"<metadata-record class='(?P<kind>[^']+)'>(?P<body>.*?)"
    r"</metadata-record>",
    re.DOTALL,
)
REMOTE_NAME = re.compile(r"<remote-name>([^<]*)</remote-name>")
ORDINAL = re.compile(r"<ordinal>\d+</ordinal>")
OBJECT_ID = re.compile(r"<object-id>\[([^\]]*)\]</object-id>")
COLUMN_ELEMENT = re.compile(r"<column[\s>][^>]*>")
COLUMN_NAME = re.compile(r"\bname='\[([^']+)\]'")
PARENT_NAME = re.compile(r"<parent-name>([^<]*)</parent-name>")


@dataclass
class SyncResult:
    """The outcome of reconciling one workbook."""

    workbook: Path
    datasources: dict[str, list[str]]
    changed: bool


def discover_project_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` looking for the project root marker."""
    current = (start or Path.cwd()).resolve()

    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate

    raise FileNotFoundError(
        "Could not locate the project root (no pyproject.toml found)."
    )


def infer_datatype(series: pd.Series) -> str:
    """Infer a Tableau textscan datatype from a CSV column.

    A column with no values at all is treated as ``string``: Tableau's
    textscan connector has nothing to sample and falls back to text.
    """
    values = series.dropna()

    if values.empty:
        return "string"

    if pd.api.types.is_bool_dtype(values):
        return "boolean"
    if pd.api.types.is_integer_dtype(values):
        return "integer"
    if pd.api.types.is_float_dtype(values):
        return "real"
    if pd.api.types.is_datetime64_any_dtype(values):
        return "date"

    return "string"


def read_source_schema(csv_path: Path) -> list[tuple[str, str]]:
    """Return ``(column name, datatype)`` pairs for a CSV source."""
    frame = pd.read_csv(csv_path)

    return [
        (str(name), infer_datatype(frame[name]))
        for name in frame.columns
    ]


def _find_datasource_spans(text: str) -> list[tuple[int, int]]:
    """Return the character spans of every top-level datasource block."""
    spans: list[tuple[int, int]] = []

    for match in DATASOURCE_START.finditer(text):
        end = text.find("</datasource>", match.start())
        if end == -1:
            continue
        spans.append((match.start(), end + len("</datasource>")))

    return spans


def _line_indent(text: str, position: int) -> str:
    """Return the whitespace that precedes ``position`` on its line."""
    line_start = text.rfind("\n", 0, position)
    if line_start == -1:
        return ""
    return text[line_start + 1 : position]


def _columns_body(body: str, schema: list[tuple[str, str]]) -> str:
    """Rebuild the body of one cached ``<columns>`` block."""
    existing = COLUMN_LINE.search(body)
    indent = (
        _line_indent(body, existing.start())
        if existing is not None
        else " " * 12
    )
    close_indent = body[body.rfind("\n") + 1 :]

    lines = [
        f"{indent}<column datatype='{datatype}' name='{name}' "
        f"ordinal='{ordinal}' />"
        for ordinal, (name, datatype) in enumerate(schema)
    ]

    return "\n" + "\n".join(lines) + "\n" + close_indent


def _rename_record(record: str, old: str, new: str, ordinal: int) -> str:
    """Retarget a cloned metadata record at a different column."""
    record = record.replace(f">{old}</remote-name>", f">{new}</remote-name>")
    record = record.replace(f">[{old}]</local-name>", f">[{new}]</local-name>")
    record = record.replace(
        f">{old}</remote-alias>", f">{new}</remote-alias>"
    )
    return ORDINAL.sub(f"<ordinal>{ordinal}</ordinal>", record, count=1)


def _force_type(record: str, datatype: str) -> str:
    """Force a cloned record's type elements onto the target datatype."""
    remote_type, aggregation, _ = TYPE_MAP.get(datatype, TYPE_MAP["string"])

    record = re.sub(
        r"<remote-type>\d+</remote-type>",
        f"<remote-type>{remote_type}</remote-type>",
        record,
        count=1,
    )
    record = re.sub(
        r"<local-type>[^<]*</local-type>",
        f"<local-type>{datatype}</local-type>",
        record,
        count=1,
    )
    return re.sub(
        r"<aggregation>[^<]*</aggregation>",
        f"<aggregation>{aggregation}</aggregation>",
        record,
        count=1,
    )


def _metadata_body(
    body: str,
    schema: list[tuple[str, str]],
    datatypes: dict[str, str],
) -> str:
    """Rebuild the column records of one ``<metadata-records>`` block.

    Existing records are kept verbatim apart from their ordinal. A newly
    added column clones the block's own record for the same datatype, so the
    extract flavour (which carries ``family`` and ``approx-count``) and the
    live flavour are both reproduced exactly.
    """
    records = list(METADATA_RECORD.finditer(body))
    if not records:
        return body

    indent = _line_indent(body, records[0].start())
    close_indent = body[body.rfind("\n") + 1 :]

    capability: list[str] = []
    existing: dict[str, str] = {}
    templates: dict[str, str] = {}
    donors: dict[str, str] = {}
    listed: set[str] = set()

    for record in records:
        if record.group("kind") != "column":
            capability.append(indent + record.group(0))
            continue

        found = REMOTE_NAME.search(record.group("body"))
        if found is None:
            continue

        text = indent + record.group(0)
        name = found.group(1)
        existing[name] = text

        local_type = datatypes.get(name, "string")
        templates.setdefault(local_type, text)
        donors.setdefault(local_type, name)

    rebuilt: list[str] = []

    for ordinal, (name, _) in enumerate(schema):
        listed.add(name)
        raw = existing.get(name)
        if raw is not None:
            rebuilt.append(
                ORDINAL.sub(f"<ordinal>{ordinal}</ordinal>", raw, count=1)
            )
            continue

        datatype = datatypes.get(name, "string")
        template = templates.get(datatype)
        if template is None:
            fallback = next(iter(templates.values()), None)
            if fallback is None:
                continue
            template = fallback

        rebuilt.append(
            _force_type(
                _rename_record(
                    template,
                    donors.get(datatype, name),
                    name,
                    ordinal,
                ),
                datatype,
            )
        )

    # A record the caller's schema does not describe is kept as written. The
    # reconciliation repairs cached drift; it never removes a field the
    # workbook still carries (a hidden one, for instance).
    rebuilt.extend(
        text for name, text in existing.items() if name not in listed
    )

    return "\n" + "\n".join(capability + rebuilt) + "\n" + close_indent


def _replace_all_bodies(text: str, pattern: re.Pattern, rebuild) -> str:
    """Rebuild the body of every match of ``pattern``, last match first."""
    for match in reversed(list(pattern.finditer(text))):
        text = (
            text[: match.start("body")]
            + rebuild(match.group("body"))
            + text[match.end("body") :]
        )
    return text


def hidden_columns(block: str) -> set[str]:
    """Return the names of the fields a datasource declares as hidden."""
    return {
        found.group(1)
        for element in COLUMN_ELEMENT.findall(block)
        if "hidden='true'" in element
        for found in COLUMN_NAME.finditer(element)
    }


def _target_schema(
    body: str,
    source: str,
    full: list[tuple[str, str]],
    visible: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Choose the schema one cached metadata block is reconciled against.

    A block whose records name the CSV is the live relation and is reconciled
    against the full header order. A block that names only ``[Extract]``
    describes the extract, which Tableau writes without the hidden fields.
    """
    parents = {name.strip("[]") for name in PARENT_NAME.findall(body)}

    if not parents or source in parents:
        return full

    return visible


def declared_datatypes(block: str) -> dict[str, str]:
    """Return the datatypes the workbook already declares for its columns."""
    match = COLUMNS_BLOCK.search(block)
    if match is None:
        return {}

    return {
        found.group("name"): found.group("datatype")
        for found in COLUMN_LINE.finditer(match.group("body"))
    }


def merge_schema(
    schema: list[tuple[str, str]],
    declared: dict[str, str],
) -> list[tuple[str, str]]:
    """Keep declared datatypes, inferring only genuinely new columns."""
    return [
        (name, declared.get(name, datatype)) for name, datatype in schema
    ]


def sync_datasource(
    block: str,
    schema: list[tuple[str, str]],
) -> str:
    """Reconcile every cached schema block in one datasource.

    The live relation carries every CSV column, so it is reconciled against
    the full header order. An extract omits the workbook's hidden fields and
    numbers its own columns continuously, so that block is reconciled against
    the visible subset instead.
    """
    merged = merge_schema(schema, declared_datatypes(block))
    datatypes = dict(merged)
    hidden = hidden_columns(block)
    visible = [column for column in merged if column[0] not in hidden]

    found = TEXTSCAN.search(block)
    source = Path(found.group(1)).name if found else ""

    block = _replace_all_bodies(
        block,
        COLUMNS_BLOCK,
        lambda body: _columns_body(body, merged),
    )
    return _replace_all_bodies(
        block,
        METADATA_BLOCK,
        lambda body: _metadata_body(
            body,
            _target_schema(body, source, merged, visible),
            datatypes,
        ),
    )


def sync_workbook(
    workbook: Path,
    analysis_dir: Path,
    *,
    dry_run: bool = False,
) -> SyncResult:
    """Reconcile every data source in a workbook with its CSV headers."""
    text = workbook.read_text(encoding="utf-8")
    original = text
    datasources: dict[str, list[str]] = {}

    for start, end in reversed(_find_datasource_spans(text)):
        block = text[start:end]

        found = TEXTSCAN.search(block)
        if found is None:
            continue

        filename = found.group(1)
        csv_path = analysis_dir / filename

        if not csv_path.is_file():
            raise FileNotFoundError(
                f"Workbook data source {filename!r} has no matching CSV at "
                f"{csv_path}"
            )

        schema = read_source_schema(csv_path)
        datasources[filename] = [name for name, _ in schema]

        text = text[:start] + sync_datasource(block, schema) + text[end:]

    changed = text != original

    if changed and not dry_run:
        workbook.write_text(text, encoding="utf-8")

    return SyncResult(
        workbook=workbook,
        datasources=datasources,
        changed=changed,
    )


def main(argv: list[str] | None = None) -> int:
    """Reconcile the project's Tableau workbook with its CSV sources."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift without writing the workbook",
    )
    parser.add_argument(
        "--workbook",
        default="tableau/Retail_Demand_Forecasting.twb",
    )
    parser.add_argument(
        "--analysis-dir",
        default="data/analysis",
    )
    args = parser.parse_args(argv)

    root = discover_project_root()
    result = sync_workbook(
        root / args.workbook,
        root / args.analysis_dir,
        dry_run=args.check,
    )

    for filename, columns in sorted(result.datasources.items()):
        print(f"{filename}: {len(columns)} column(s) reconciled")

    if result.changed:
        print("Workbook schema was out of date." if args.check else "Workbook schema updated.")
        return 1 if args.check else 0

    print("Workbook schema already matches its sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
