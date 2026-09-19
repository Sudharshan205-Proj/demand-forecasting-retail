#!/usr/bin/env python3
"""Audit helper: compare current artifact digests against the baseline manifest.

Reads  docs/final-audit/execution/baseline-checksums.tsv and re-hashes each file.
Writes docs/final-audit/execution/phase-17/artifact-drift-report.tsv and prints
a summary grouped by classification.
"""
from __future__ import annotations

import hashlib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXEC = os.path.join(ROOT, "docs", "final-audit", "execution")
BASELINE = os.path.join(EXEC, "baseline-checksums.tsv")
INVENTORY = os.path.join(EXEC, "baseline-inventory.tsv")
REPORT = os.path.join(EXEC, "phase-17", "artifact-drift-report.tsv")


def classify(rel: str) -> str:
    p = rel.replace("\\", "/")
    for prefix, name in (
        ("data/raw/", "raw-data"),
        ("data/processed/", "generated-processed"),
        ("data/analysis/", "generated-analysis"),
        ("deploy/", "deployment"),
        ("tableau/", "tableau"),
        ("r/", "r-analysis"),
    ):
        if p.startswith(prefix):
            return name
    return "other"


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    rows = []
    with open(BASELINE, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            rel, old_hash, old_size = parts
            full = os.path.join(ROOT, rel)
            if not os.path.exists(full):
                rows.append((rel, classify(rel), old_hash, "", "MISSING"))
                continue
            new_hash = sha256(full)
            status = "IDENTICAL" if new_hash == old_hash else "DIFFERS"
            rows.append((rel, classify(rel), old_hash, new_hash, status))

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8", newline="") as out:
        out.write("path\tclassification\tbaseline_sha256\tcurrent_sha256\tstatus\n")
        for r in rows:
            out.write("\t".join(r) + "\n")

    from collections import Counter
    by_cls = Counter()
    by_cls_status = Counter()
    for rel, cls, _o, _n, status in rows:
        by_cls[cls] += 1
        by_cls_status[(cls, status)] += 1
    print(f"compared: {len(rows)} artifacts")
    for cls in sorted(by_cls):
        ident = by_cls_status[(cls, "IDENTICAL")]
        diff = by_cls_status[(cls, "DIFFERS")]
        missing = by_cls_status[(cls, "MISSING")]
        print(f"  {cls:20s} identical={ident:3d} differs={diff:3d} missing={missing:3d}")
    print(f"report: {REPORT}")


if __name__ == "__main__":
    main()
