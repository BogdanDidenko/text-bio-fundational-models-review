#!/usr/bin/env python3
"""Build an immutable record/study registry for a Docling taxonomy cohort."""

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
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def assemble_registry(
    source_rows: list[dict[str, str]],
    prior_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Preserve prior study identity without treating record reuse as duplication."""
    prior_by_hash: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in prior_rows:
        source_hash = row.get("source_document_sha256") or row.get("source_pdf_sha256")
        if source_hash:
            prior_by_hash[source_hash].append(row)

    by_document: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_rows:
        by_document[row["source_document_sha256"]].append(row)

    registry: list[dict[str, Any]] = []
    exact_duplicate_groups: list[dict[str, Any]] = []
    for document_hash, group in sorted(by_document.items()):
        current_ids = {row["candidate_id"] for row in group}
        prior_group = prior_by_hash.get(document_hash, [])
        prior_ids = {row["record_id"] for row in prior_group}
        all_record_ids = sorted(current_ids | prior_ids)

        prior_canonical = next(
            (
                row
                for row in sorted(prior_group, key=lambda item: item["record_id"])
                if row.get("canonical_record_for_study", "").casefold() == "true"
            ),
            None,
        )
        prior_anchor = prior_canonical or (
            sorted(prior_group, key=lambda item: item["record_id"])[0]
            if prior_group
            else None
        )
        current_canonical = sorted(group, key=lambda row: row["candidate_id"])[0]
        canonical_record_id = (
            prior_anchor["record_id"] if prior_anchor else current_canonical["candidate_id"]
        )
        study_id = (
            prior_anchor["study_id"]
            if prior_anchor
            else stable_id("study", current_canonical["candidate_id"])
        )
        exact_duplicate = len(all_record_ids) > 1

        if exact_duplicate:
            exact_duplicate_groups.append(
                {
                    "group_id": stable_id("duplicate", document_hash),
                    "source_pdf_sha256": document_hash,
                    "record_ids": all_record_ids,
                    "canonical_record_id": canonical_record_id,
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
                    "source_pdf_sha256": document_hash,
                    "source_document_sha256": document_hash,
                    "canonical_record_for_study": record_id == canonical_record_id,
                    "exact_duplicate": exact_duplicate,
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
    return registry, exact_duplicate_groups


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--expected-records", type=int, default=0)
    parser.add_argument(
        "--prior-registry",
        type=Path,
        help="Optional prior registry used only to preserve study IDs for exact file duplicates.",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.canonical_manifest.open(newline="", encoding="utf-8") as stream:
        source_rows = [
            row for row in csv.DictReader(stream) if row.get("profile_status") == "complete"
        ]
    expected = args.expected_records or len(source_rows)
    if len(source_rows) != expected:
        raise RuntimeError(f"Expected {expected} records, found {len(source_rows)}")

    prior_rows: list[dict[str, str]] = []
    if args.prior_registry:
        with args.prior_registry.open(newline="", encoding="utf-8") as stream:
            prior_rows = list(csv.DictReader(stream))
    for row in source_rows:
        source_document = row.get("source_document") or row.get("source_pdf")
        if not source_document:
            raise RuntimeError(f"Missing source document for {row.get('candidate_id')}")
        row["source_document_sha256"] = sha256(resolve(source_document))
    registry, exact_duplicate_groups = assemble_registry(source_rows, prior_rows)
    write_csv(args.output_dir / "study_model_registry.csv", registry)
    registry_ids = {row["record_id"] for row in registry}
    omnina_present = {OMNINA_PREPRINT, OMNINA_JOURNAL} <= registry_ids
    payload = {
        "screening_record_count": len(registry),
        "primary_study_count_in_cohort": len({row["study_id"] for row in registry}),
        "primary_study_count": len({row["study_id"] for row in registry}),
        "sensitivity_study_count_if_omnina_linked": (
            len({row["study_id"] for row in registry}) - 1 if omnina_present else None
        ),
        "prior_registry_records": len(prior_rows),
        "exact_duplicate_groups": exact_duplicate_groups,
        "possible_version_links": (
            [
                {
                    "linkage_id": "omnina_preprint_journal",
                    "record_ids": [OMNINA_PREPRINT, OMNINA_JOURNAL],
                    "primary_analysis": "kept_separate",
                    "sensitivity_analysis": "linked_as_one_study",
                }
            ]
            if omnina_present
            else []
        ),
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
