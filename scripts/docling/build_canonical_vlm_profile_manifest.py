#!/usr/bin/env python3
"""Validate and index the canonical no-limit Docling VLM corpus."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO / "data/docling_include_vlm_52_2026-07-10_nolimits"


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def slug(text: str, limit: int = 96) -> str:
    import re

    value = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")
    return value[:limit] or "document"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()

    root = args.profile_root.resolve()
    config_path = root / "manifests/run_config.json"
    run_manifest_path = root / "manifests/docling_smoke_manifest.json"
    config = read_json(config_path)
    run_manifest = read_json(run_manifest_path)
    run_rows = {row["candidate_id"]: row for row in run_manifest["results"]}
    profile_rows: list[dict[str, Any]] = []

    for item in config["pdfs"]:
        candidate_id = item["candidate_id"]
        run_row = run_rows.get(candidate_id)
        if run_row is None or run_row.get("status") != "ok":
            raise RuntimeError(f"Missing successful Docling result: {candidate_id}")

        stem = slug(candidate_id)
        docling_json = root / "documents" / f"{stem}.docling.json"
        markdown = root / "markdown" / f"{stem}.md"
        figures_manifest = root / "figures" / stem / "figures_manifest.json"
        if not all(path.is_file() for path in [docling_json, markdown, figures_manifest]):
            raise RuntimeError(f"Incomplete native Docling profile: {candidate_id}")

        figures = read_json(figures_manifest)
        labels = Counter()
        descriptions = 0
        for figure in figures:
            text = ((figure.get("meta") or {}).get("description") or {}).get("text") or ""
            if text:
                descriptions += 1
                labels[text.split("\n", 1)[0]] += 1
        if descriptions != len(figures):
            raise RuntimeError(
                f"Picture-description coverage incomplete for {candidate_id}: "
                f"{descriptions}/{len(figures)}"
            )

        profile_rows.append(
            {
                "candidate_id": candidate_id,
                "source_record_id": item.get("source_record_id", ""),
                "title": item.get("title", ""),
                "doi": item.get("doi", ""),
                "source_pdf": item["path"],
                "profile_status": "complete",
                "profile_kind": "native_docling_vlm_full_conversion",
                "docling_json": rel(docling_json),
                "markdown": rel(markdown),
                "figures_manifest": rel(figures_manifest),
                "figure_count": len(figures),
                "picture_description_count": descriptions,
                "scientific_figure_count": labels["SCIENTIFIC_FIGURE"],
                "non_scientific_image_count": labels["NON_SCIENTIFIC_IMAGE"],
                "chunks": "",
                "chunks_status": (
                    "not_generated: no-limit VLM profile intentionally skips "
                    "HybridChunker; derive a RAG chunk view separately when a "
                    "retrieval token budget is explicitly chosen"
                ),
                "picture_description_backend": config["settings"]["picture_description_backend"],
                "picture_description_model": config["settings"]["openai_model"],
                "picture_description_area_threshold": config["settings"]["picture_description_area_threshold"],
                "picture_description_max_tokens": config["settings"]["picture_description_max_tokens"],
                "picture_description_scale": config["settings"]["picture_description_scale"],
            }
        )

    if len(profile_rows) != 52:
        raise RuntimeError(f"Expected 52 profiles, found {len(profile_rows)}")

    output_csv = root / "manifests/canonical_docling_profile_manifest.csv"
    output_json = root / "manifests/canonical_docling_profile_manifest.json"
    output_summary = root / "manifests/canonical_docling_profile_summary.md"
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(profile_rows[0]))
        writer.writeheader()
        writer.writerows(profile_rows)
    output_json.write_text(json.dumps(profile_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    figures = sum(row["figure_count"] for row in profile_rows)
    scientific = sum(row["scientific_figure_count"] for row in profile_rows)
    non_scientific = sum(row["non_scientific_image_count"] for row in profile_rows)
    output_summary.write_text(
        "\n".join(
            [
                "# Canonical No-Limit Docling VLM Profiles",
                "",
                f"- Profiles: {len(profile_rows)}",
                f"- Source PDF conversions: {len(profile_rows)} successful",
                f"- Extracted and described images: {figures}/{figures}",
                f"- Scientific figures: {scientific}",
                f"- Non-scientific images: {non_scientific}",
                "- VLM model: gpt-5.5 via local OpenAI-compatible Codex wrapper",
                "- Picture area threshold: 0.0 (all extracted pictures described)",
                "- VLM output-token cap: none",
                "- RAG chunks: intentionally absent; HybridChunker was not run.",
                "",
                "## Profile contents",
                "",
                "Every profile has a full native `DoclingDocument` JSON, markdown export, "
                "extracted picture images, and figure manifest with the native VLM annotations. "
                "The corpus is a fresh PDF conversion, not a patch applied to the previous "
                "no-VLM corpus.",
                "",
                "## Artifacts",
                "",
                "- `canonical_docling_profile_manifest.csv`",
                "- `canonical_docling_profile_manifest.json`",
                "- `docling_smoke_manifest.json`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "profiles": len(profile_rows),
                "figures": figures,
                "scientific_figures": scientific,
                "non_scientific_images": non_scientific,
                "manifest": rel(output_csv),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
