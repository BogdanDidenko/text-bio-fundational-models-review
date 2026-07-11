#!/usr/bin/env python3
"""Build the native Docling VLM-enrichment config for the canonical 52 records."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCREENING_ROOT = (
    REPO
    / "data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10"
)
FINAL_RESULTS = SCREENING_ROOT / "final_screening_results.json"
MANUAL_RESOLUTION = SCREENING_ROOT / "manual_resolution_2026-07-10.csv"
SOURCE_MANIFESTS = sorted(
    REPO.glob("data/docling_*/manifests/docling*_manifest.json")
)
COVERAGE_MANIFESTS = [
    REPO / "data/docling_include_final_coverage_2026-07-09/final_docling_manifest.csv",
    REPO / "data/docling_uncertain_final_coverage_2026-07-09/final_docling_manifest.csv",
]
OUT_ROOT = REPO / "data/docling_include_vlm_52_2026-07-10"
OUT_MANIFEST_DIR = OUT_ROOT / "manifests"

STRICT_SCIENTIFIC_FIGURE_PROMPT = (
    "This is an extracted image from a biomedical or scientific paper. First "
    "decide if it is a real scientific figure/panel with data, workflow, model "
    "architecture, biological diagram, microscopy, plot, table-like visual, or "
    "experiment result. If it is only a publisher logo, journal header, author "
    "icon, email icon, social/media icon, decorative symbol, page header/footer, "
    "or non-data branding, start the answer with NON_SCIENTIFIC_IMAGE and briefly "
    "say why. Otherwise start with SCIENTIFIC_FIGURE and describe it for retrieval: "
    "figure type; visible axes, panels, labels, or legend; biological/model quantity "
    "measured or shown; and the main visible finding. Be precise and concise. Do not "
    "invent details."
)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO / path


def load_manual_decisions() -> dict[str, dict[str, str]]:
    with MANUAL_RESOLUTION.open(newline="", encoding="utf-8") as handle:
        return {row["record_id"]: row for row in csv.DictReader(handle)}


def load_source_manifest_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for manifest_path in SOURCE_MANIFESTS:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for row in payload.get("results", []):
            markdown = row.get("markdown")
            if markdown:
                index[str(markdown)] = row
    for coverage_path in COVERAGE_MANIFESTS:
        with coverage_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                markdown = row.get("markdown")
                source_pdf = row.get("pdf_path") or row.get("source_file")
                if markdown and source_pdf:
                    index[str(markdown)] = {"source_pdf": source_pdf}
    return index


def main() -> int:
    final_records = json.loads(FINAL_RESULTS.read_text(encoding="utf-8"))["records"]
    manual = load_manual_decisions()
    source_index = load_source_manifest_index()

    selected: list[dict[str, Any]] = []
    for record in final_records:
        override = manual.get(record["record_id"])
        decision = override["manual_decision"] if override else record["final_decision"]
        if decision != "INCLUDE":
            continue

        markdown = record["docling_markdown"]
        source = source_index.get(markdown)
        if source is None:
            raise RuntimeError(f"No source manifest entry for {record['record_id']}: {markdown}")
        pdf_path = repo_path(str(source["source_pdf"]))
        if not pdf_path.is_file():
            raise RuntimeError(f"Missing source PDF for {record['record_id']}: {pdf_path}")

        selected.append(
            {
                "candidate_id": record["record_id"],
                "source_record_id": record["source_record_id"],
                "title": record["title"],
                "doi": record.get("doi", ""),
                "automated_decision": record["final_decision"],
                "manual_decision": override["manual_decision"] if override else "",
                "manual_resolution_applied": bool(override),
                "source_docling_markdown": markdown,
                "source_pdf": rel(pdf_path),
                "pdf_bytes": pdf_path.stat().st_size,
            }
        )

    if len(selected) != 52:
        raise RuntimeError(f"Expected 52 canonical INCLUDE records, found {len(selected)}")
    manual_includes = sum(row["manual_resolution_applied"] for row in selected)
    if manual_includes != 2:
        raise RuntimeError(f"Expected 2 manually resolved INCLUDE records, found {manual_includes}")

    config = {
        "name": "docling_include_vlm_52_2026-07-10",
        "description": (
            "Native Docling picture-description enrichment for the canonical "
            "52-record full-text eligibility set: 50 automated INCLUDE plus 2 "
            "human-confirmed manual INCLUDE records."
        ),
        "output_root": rel(OUT_ROOT),
        "input_screening_artifact": rel(FINAL_RESULTS),
        "manual_resolution_artifact": rel(MANUAL_RESOLUTION),
        "records_total": len(selected),
        "automated_include_records": len(selected) - manual_includes,
        "manual_include_records": manual_includes,
        "settings": {
            "picture_description_backend": "openai-api",
            "openai_base_url": "http://127.0.0.1:8765/v1/chat/completions",
            "openai_model": "gpt-5.5",
            "picture_description_timeout": 600,
            "picture_description_concurrency": 1,
            "picture_description_max_tokens": None,
            "picture_description_temperature": 0,
            "picture_description_scale": 2,
            "picture_description_area_threshold": 0.0,
            "picture_description_prompt": STRICT_SCIENTIFIC_FIGURE_PROMPT,
            "skip_chunks": True,
        },
        "pdfs": [
            {
                "path": row["source_pdf"],
                "candidate_id": row["candidate_id"],
                "source_record_id": row["source_record_id"],
                "title": row["title"],
                "doi": row["doi"],
            }
            for row in selected
        ],
    }

    OUT_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    config_path = OUT_MANIFEST_DIR / "run_config.json"
    mapping_path = OUT_MANIFEST_DIR / "input_records.csv"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with mapping_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(selected[0].keys()))
        writer.writeheader()
        writer.writerows(selected)

    print(
        json.dumps(
            {
                "records_total": len(selected),
                "automated_include_records": len(selected) - manual_includes,
                "manual_include_records": manual_includes,
                "config": rel(config_path),
                "input_records": rel(mapping_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
