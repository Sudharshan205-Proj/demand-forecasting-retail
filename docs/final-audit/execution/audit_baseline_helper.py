#!/usr/bin/env python3
"""Audit helper: baseline SHA-256 manifest and file inventory (read-only).

Writes:
  docs/final-audit/execution/baseline-checksums.tsv
  docs/final-audit/execution/baseline-inventory.tsv
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime

# This file lives at <root>/docs/final-audit/execution/, so the project root is
# four dirname levels up from the script file itself.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

SKIP_DIRS = {".git", ".venv", ".pytest_cache", "__pycache__", ".freebuff", ".vscode", ".streamlit"}

CHUNK = 1024 * 1024


def classify(relpath: str) -> str:
    p = relpath.replace("\\", "/")
    if p.startswith("docs/"):
        return "documentation"
    if p.startswith("tests/"):
        return "test"
    if p.startswith("scripts/"):
        return "source-script"
    if p.startswith("app/"):
        return "application"
    if p.startswith("r/"):
        return "r-analysis"
    if p.startswith("sql/"):
        return "sql"
    if p.startswith("tableau/"):
        return "tableau"
    if p.startswith("deploy/"):
        return "deployment"
    if p.startswith("data/raw/"):
        return "raw-data"
    if p.startswith("data/processed/"):
        return "generated-processed"
    if p.startswith("data/analysis/"):
        return "generated-analysis"
    if p.startswith("reports/"):
        return "report"
    if p in ("requirements.txt", "pyproject.toml", ".python-version", ".gitignore"):
        return "configuration"
    if p == "README.md":
        return "documentation"
    return "unknown"


def iter_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT)
            yield full, rel


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(CHUNK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "final-audit", "execution")
    now = datetime.now().isoformat(timespec="seconds")

    sum_path = os.path.join(out_dir, "baseline-checksums.tsv")
    inv_path = os.path.join(out_dir, "baseline-inventory.tsv")

    with open(sum_path, "w", encoding="utf-8", newline="") as sums, \
         open(inv_path, "w", encoding="utf-8", newline="") as inv:
        sums.write("path\tsha256\tbytes\n")
        inv.write("path\tclassification\tbytes\tmodified_utc\n")
        for full, rel in iter_files():
            size = os.path.getsize(full)
            mtime = datetime.utcfromtimestamp(os.path.getmtime(full)).isoformat(timespec="seconds")
            cls = classify(rel)
            inv.write(f"{rel}\t{cls}\t{size}\t{mtime}\n")
            if cls in ("raw-data", "generated-processed", "generated-analysis", "deployment", "tableau", "r-analysis"):
                digest = sha256(full)
                sums.write(f"{rel}\t{digest}\t{size}\n")
    print(f"inventory: {inv_path}")
    print(f"checksums: {sum_path}")
    print(f"completed: {now}")


if __name__ == "__main__":
    main()
