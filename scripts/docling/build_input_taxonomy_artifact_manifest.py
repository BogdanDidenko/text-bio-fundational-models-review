#!/usr/bin/env python3
"""Hash every taxonomy artifact and record reproducible filesystem metadata."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT_ROOT = ROOT / "data/input_representation_taxonomy_2026-07-11"
MANIFEST_NAMES = {"artifact_manifest.csv", "artifact_manifest_summary.json"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def category(relative: Path) -> str:
    parts = relative.parts
    if parts and parts[0] == "runs" and len(parts) == 2:
        return "run_logs"
    if parts and parts[0] == "runs" and len(parts) > 2:
        return f"run:{parts[1]}"
    if parts and parts[0] == "taxonomy_synthesis":
        return "taxonomy_synthesis"
    if parts and parts[0] == "adjudication":
        return "adjudication"
    return "final_or_documentation"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    args = parser.parse_args()
    artifact_root = args.artifact_root.resolve()
    files = sorted(
        path
        for path in artifact_root.rglob("*")
        if path.is_file() and path.name not in MANIFEST_NAMES
    )
    rows = []
    for path in files:
        stat = path.stat()
        relative = path.relative_to(artifact_root)
        rows.append(
            {
                "relative_path": str(relative),
                "category": category(relative),
                "size_bytes": stat.st_size,
                "mtime_utc": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(),
                "sha256": sha256(path),
            }
        )
    manifest = artifact_root / "artifact_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    summary = {
        "artifact_root": str(artifact_root),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(rows),
        "total_size_bytes": sum(row["size_bytes"] for row in rows),
        "categories": dict(Counter(row["category"] for row in rows)),
        "manifest_sha256": sha256(manifest),
    }
    (artifact_root / "artifact_manifest_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
