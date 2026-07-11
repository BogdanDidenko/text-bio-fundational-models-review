#!/usr/bin/env python3
"""Build the immutable record/study registry for the 52-paper taxonomy corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = (
    ROOT
    / "data/docling_include_vlm_52_2026-07-10_nolimits/manifests"
    / "canonical_docling_profile_manifest.csv"
)
DEFAULT_OUTPUT = ROOT / "data/input_representation_taxonomy_2026-07-11"
OMNINA_PREPRINT = "full_2026-07-06__rec_002327"
OMNINA_JOURNAL = "full_2026-07-06__rec_003394"


def resolve(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_id(prefix: str, value: str) -> str:
    normalized = " ".join(re.findall(r"[a-z0-9]+", value.casefold()))
    return f"{prefix}_{hashlib.sha256(normalized.encode()).hexdigest()[:12]}"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.canonical_manifest.open(newline="", encoding="utf-8") as stream:
        source_rows = [
            row for row in csv.DictReader(stream) if row.get("profile_status") == "complete"
        ]
    if len(source_rows) != 52:
        raise RuntimeError(f"Expected 52 records, found {len(source_rows)}")

    by_pdf: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_rows:
        row["source_pdf_sha256"] = sha256(resolve(row["source_pdf"]))
        by_pdf[row["source_pdf_sha256"]].append(row)

    registry: list[dict[str, Any]] = []
    exact_duplicate_groups: list[dict[str, Any]] = []
    for pdf_hash, group in sorted(by_pdf.items()):
        canonical = sorted(group, key=lambda row: row["candidate_id"])[0]
        study_id = stable_id("study", canonical["candidate_id"])
        if len(group) > 1:
            exact_duplicate_groups.append(
                {
                    "group_id": stable_id("duplicate", pdf_hash),
                    "source_pdf_sha256": pdf_hash,
                    "record_ids": [row["candidate_id"] for row in group],
                    "canonical_record_id": canonical["candidate_id"],
                    "study_id": study_id,
                }
            )
        for row in group:
            record_id = row["candidate_id"]
            registry.append(
                {
                    "record_id": record_id,
                    "source_record_id": row.get("source_record_id", ""),
                    "study_id": study_id,
                    "title": row.get("title", ""),
                    "doi": row.get("doi", ""),
                    "source_pdf_sha256": pdf_hash,
                    "canonical_record_for_study": record_id == canonical["candidate_id"],
                    "exact_duplicate": len(group) > 1,
                    "possible_version_group": "omnina_preprint_journal"
                    if record_id in {OMNINA_PREPRINT, OMNINA_JOURNAL}
                    else "",
                    "primary_analysis_linkage": "separate"
                    if record_id in {OMNINA_PREPRINT, OMNINA_JOURNAL}
                    else "exact_pdf_only",
                    "docling_json": row["docling_json"],
                    "markdown": row["markdown"],
                }
            )

    registry.sort(key=lambda row: row["record_id"])
    write_csv(args.output_dir / "study_model_registry.csv", registry)
    payload = {
        "screening_record_count": 52,
        "primary_study_count": len({row["study_id"] for row in registry}),
        "sensitivity_study_count_if_omnina_linked": len({row["study_id"] for row in registry}) - 1,
        "exact_duplicate_groups": exact_duplicate_groups,
        "possible_version_links": [
            {
                "linkage_id": "omnina_preprint_journal",
                "record_ids": [OMNINA_PREPRINT, OMNINA_JOURNAL],
                "primary_analysis": "kept_separate",
                "sensitivity_analysis": "linked_as_one_study",
            }
        ],
        "model_registry_status": (
            "Model IDs are assigned after open extraction because a paper may contain "
            "multiple generative models."
        ),
    }
    (args.output_dir / "registry_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
