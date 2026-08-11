#!/usr/bin/env python3
"""Validate and index a complete native Docling profile corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from difflib import SequenceMatcher
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def normalized_doi(value: str) -> str:
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I)
    return re.sub(r"^doi:\s*", "", value, flags=re.I).strip().casefold()


def document_identity(title: str, doi: str, markdown: str) -> dict[str, Any]:
    front = markdown[:20_000]
    expected_title = normalized_text(title)
    front_normalized = normalized_text(front)
    expected_doi = normalized_doi(doi)
    doi_match = bool(expected_doi and expected_doi in markdown.casefold())
    exact_title_in_front = bool(expected_title and expected_title in front_normalized)
    headings = [
        re.sub(r"^#{1,8}\s+", "", line).strip()
        for line in front.splitlines()
        if re.match(r"^#{1,8}\s+\S", line)
    ][:20]
    heading_similarities = [
        SequenceMatcher(None, expected_title, normalized_text(heading)).ratio()
        for heading in headings
        if expected_title and normalized_text(heading)
    ]
    best_heading_similarity = max(heading_similarities, default=0.0)
    title_tokens = {token for token in expected_title.split() if len(token) > 2}
    front_tokens = set(front_normalized.split())
    token_coverage = len(title_tokens & front_tokens) / len(title_tokens) if title_tokens else 0.0
    verified = bool(
        doi_match
        or exact_title_in_front
        or best_heading_similarity >= 0.90
        or (len(title_tokens) >= 5 and token_coverage >= 0.90)
    )
    return {
        "status": "verified" if verified else "unverified",
        "doi_match": doi_match,
        "exact_normalized_title_in_first_20000_chars": exact_title_in_front,
        "best_heading_title_similarity": round(best_heading_similarity, 6),
        "title_token_coverage_in_first_20000_chars": round(token_coverage, 6),
        "front_heading_candidates": headings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--expected-records", type=int, default=0)
    args = parser.parse_args()

    root = args.profile_root.resolve()
    config_path = root / "manifests/run_config.json"
    run_manifest_path = root / "manifests/docling_smoke_manifest.json"
    config = read_json(config_path)
    run_manifest = read_json(run_manifest_path)
    run_rows = {str(row.get("candidate_id") or ""): row for row in run_manifest["results"]}
    if "" in run_rows or len(run_rows) != len(run_manifest["results"]):
        raise RuntimeError("Docling run manifest has duplicate or empty candidate_id values")
    profile_rows: list[dict[str, Any]] = []
    identity_audit: list[dict[str, Any]] = []

    items = config.get("documents") or config.get("pdfs") or []
    item_ids = [str(item.get("candidate_id") or "") for item in items]
    if not all(item_ids) or len(set(item_ids)) != len(item_ids):
        raise RuntimeError("Docling run config has duplicate or empty candidate_id values")
    if set(item_ids) != set(run_rows):
        raise RuntimeError(
            "Docling run manifest does not match configured candidates; "
            f"missing={sorted(set(item_ids) - set(run_rows))}, "
            f"extra={sorted(set(run_rows) - set(item_ids))}"
        )
    vlm_enabled = config.get("settings", {}).get("picture_description_backend") != "none"
    for item in items:
        candidate_id = item["candidate_id"]
        run_row = run_rows.get(candidate_id)
        if run_row is None or run_row.get("status") != "ok":
            raise RuntimeError(f"Missing successful Docling result: {candidate_id}")
        source_document = Path(str(item["path"])).resolve()
        run_source = Path(str(run_row.get("source_document") or ""))
        if not run_source.is_absolute():
            run_source = REPO / run_source
        if run_source.resolve() != source_document or not source_document.is_file():
            raise RuntimeError(f"Docling source-document mismatch: {candidate_id}")
        if sha256_file(source_document) != str(run_row.get("source_document_sha256") or ""):
            raise RuntimeError(f"Docling source-document hash mismatch: {candidate_id}")

        # New profiles provide a collision-resistant stem. The fallback keeps
        # historical corpus manifests readable without rewriting them.
        stem = str(run_row.get("artifact_stem") or slug(candidate_id))
        docling_json = root / "documents" / f"{stem}.docling.json"
        markdown = root / "markdown" / f"{stem}.md"
        figures_manifest = root / "figures" / stem / "figures_manifest.json"
        if not all(path.is_file() for path in [docling_json, markdown, figures_manifest]):
            raise RuntimeError(f"Incomplete native Docling profile: {candidate_id}")
        for path, field in (
            (docling_json, "docling_json_sha256"),
            (markdown, "markdown_sha256"),
            (figures_manifest, "figures_manifest_sha256"),
        ):
            if sha256_file(path) != str(run_row.get(field) or ""):
                raise RuntimeError(f"Native Docling artifact hash mismatch ({field}): {candidate_id}")

        figures = read_json(figures_manifest)
        identity = document_identity(
            str(item.get("title") or ""),
            str(item.get("doi") or ""),
            markdown.read_text(encoding="utf-8", errors="replace"),
        )
        identity_audit.append({"candidate_id": candidate_id, **identity})
        labels = Counter()
        descriptions = 0
        for figure in figures:
            text = ((figure.get("meta") or {}).get("description") or {}).get("text") or ""
            if text:
                descriptions += 1
                labels[text.split("\n", 1)[0]] += 1
        if vlm_enabled and descriptions != len(figures):
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
                "source_document": item["path"],
                "source_document_sha256": run_row.get("source_document_sha256", ""),
                "source_document_kind": item.get("kind") or Path(item["path"]).suffix.lstrip("."),
                "source_pdf": item["path"] if Path(item["path"]).suffix.lower() == ".pdf" else "",
                "profile_status": "complete",
                "document_identity_status": identity["status"],
                "document_identity_evidence": json.dumps(identity, ensure_ascii=False),
                "profile_kind": (
                    "native_docling_vlm_full_conversion"
                    if vlm_enabled
                    else "native_docling_full_conversion"
                ),
                "docling_json": rel(docling_json),
                "docling_json_sha256": run_row["docling_json_sha256"],
                "markdown": rel(markdown),
                "markdown_sha256": run_row["markdown_sha256"],
                "figures_manifest": rel(figures_manifest),
                "figures_manifest_sha256": run_row["figures_manifest_sha256"],
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
                "picture_description_backend": config["settings"].get("picture_description_backend", "none"),
                "picture_description_model": config["settings"].get("openai_model", ""),
                "picture_description_area_threshold": config["settings"].get("picture_description_area_threshold", ""),
                "picture_description_max_tokens": config["settings"].get("picture_description_max_tokens"),
                "picture_description_scale": config["settings"].get("picture_description_scale", ""),
            }
        )

    expected = args.expected_records or len(items)
    if len(profile_rows) != expected:
        raise RuntimeError(f"Expected {expected} profiles, found {len(profile_rows)}")

    identity_audit_path = root / "manifests/document_identity_audit.json"
    identity_audit_path.write_text(
        json.dumps(identity_audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    unverified = [row["candidate_id"] for row in identity_audit if row["status"] != "verified"]
    if unverified:
        raise RuntimeError(
            "Docling document identity could not be verified for candidate IDs: "
            f"{unverified}. See {identity_audit_path}"
        )

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
                "# Canonical Docling Profiles",
                "",
                f"- Profiles: {len(profile_rows)}",
                f"- Source document conversions: {len(profile_rows)} successful",
                f"- Extracted and described images: {figures}/{figures}",
                f"- Scientific figures: {scientific}",
                f"- Non-scientific images: {non_scientific}",
                f"- Picture descriptions enabled: {vlm_enabled}",
                f"- VLM model: {config['settings'].get('openai_model', 'none') if vlm_enabled else 'none'}",
                f"- Picture area threshold: {config['settings'].get('picture_description_area_threshold', 'n/a')}",
                f"- VLM output-token cap: {config['settings'].get('picture_description_max_tokens')}",
                "- RAG chunks: intentionally absent; HybridChunker was not run.",
                "",
                "## Profile contents",
                "",
                "Every profile has a full native `DoclingDocument` JSON, markdown export, "
                "extracted picture images, and a figure manifest. VLM-enabled runs store "
                "picture descriptions natively in those profiles. Each profile is produced "
                "by a fresh full-text conversion rather than by patching an older corpus.",
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
