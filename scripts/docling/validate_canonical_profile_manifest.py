#!/usr/bin/env python3
"""Read-only validation of a canonical Docling profile manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from profile_artifact_contract import resolve_artifact, validate_profile_artifacts


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rebase_row(
    row: dict[str, Any], original_run_root: Path, restored_run_root: Path
) -> dict[str, Any]:
    """Point manifest paths at a restored copy without changing recorded hashes."""
    rebased = dict(row)
    original = original_run_root.resolve()
    restored = restored_run_root.resolve()
    for field in ("source_document", "docling_json", "markdown", "figures_manifest"):
        current = resolve_artifact(str(row.get(field) or "")).resolve()
        try:
            relative = current.relative_to(original)
        except ValueError as exc:
            raise RuntimeError(
                f"Cannot rebase {field} outside original run root: {current}"
            ) from exc
        rebased[field] = str(restored / relative)
    return rebased


def validate_row(row: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(row.get("candidate_id") or "")
    docling_json, markdown = validate_profile_artifacts(row)
    source = resolve_artifact(str(row.get("source_document") or ""))
    figures = resolve_artifact(str(row.get("figures_manifest") or ""))
    for field, path, hash_field in (
        ("source_document", source, "source_document_sha256"),
        ("figures_manifest", figures, "figures_manifest_sha256"),
    ):
        expected = str(row.get(hash_field) or "")
        if not path.is_file() or not expected:
            raise RuntimeError(f"Missing or unbound {field} for {candidate_id}")
        if sha256(path) != expected:
            raise RuntimeError(f"Hash mismatch for {candidate_id}: {field}")
    figures_payload = json.loads(figures.read_text(encoding="utf-8"))
    if not isinstance(figures_payload, list):
        raise RuntimeError(f"Figure manifest is not a list for {candidate_id}")
    if len(figures_payload) != int(row.get("figure_count") or 0):
        raise RuntimeError(f"Figure count mismatch for {candidate_id}")
    return {
        "candidate_id": candidate_id,
        "docling_json": str(docling_json),
        "markdown": str(markdown),
        "source_document": str(source),
        "figures_manifest": str(figures),
        "figure_count": len(figures_payload),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-records", type=int, default=0)
    parser.add_argument("--original-run-root", type=Path)
    parser.add_argument("--restored-run-root", type=Path)
    args = parser.parse_args()

    if bool(args.original_run_root) != bool(args.restored_run_root):
        raise RuntimeError(
            "--original-run-root and --restored-run-root must be supplied together"
        )

    manifest = args.manifest.resolve()
    with manifest.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if args.original_run_root and args.restored_run_root:
        rows = [
            rebase_row(row, args.original_run_root, args.restored_run_root)
            for row in rows
        ]
    candidate_ids = [str(row.get("candidate_id") or "") for row in rows]
    if not all(candidate_ids) or len(set(candidate_ids)) != len(candidate_ids):
        raise RuntimeError("Canonical manifest contains empty or duplicate candidate IDs")
    expected = args.expected_records or len(rows)
    if len(rows) != expected:
        raise RuntimeError(f"Expected {expected} profiles, found {len(rows)}")
    validated = [validate_row(row) for row in rows]
    print(
        json.dumps(
            {
                "ok": True,
                "manifest": str(manifest),
                "manifest_sha256": sha256(manifest),
                "profiles_validated": len(validated),
                "figures_validated": sum(row["figure_count"] for row in validated),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
