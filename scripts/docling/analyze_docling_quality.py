#!/usr/bin/env python3
"""Summarize structural quality of a Docling batch output."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]


def resolve_repo_path(value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else REPO / path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def description_text(figure: dict[str, Any]) -> str:
    meta = figure.get("meta")
    if isinstance(meta, dict):
        description = meta.get("description")
        if isinstance(description, dict) and isinstance(description.get("text"), str):
            return description["text"].strip()
    for annotation in figure.get("annotations") or []:
        if isinstance(annotation, dict) and isinstance(annotation.get("text"), str):
            return annotation["text"].strip()
    return ""


def looks_like_non_scientific_figure(text: str) -> bool:
    value = text.lower()
    if value.startswith("scientific_figure"):
        return False
    if value.startswith("non_scientific_image"):
        return True
    markers = [
        "not a scientific",
        "not a data figure",
        "no scientific result",
        "no scientific finding",
        "no scientific data",
        "no scientific result or trend",
        "publisher logo",
        "journal/logo",
        "logo graphic",
        "logo/branding",
        "icon/logo",
        "identifier/logo",
        "publisher/logo",
        "publisher mark",
        "publisher branding",
        "journal header",
        "header graphic",
        "wordmark",
        "branding",
        "generic graphical icon",
        "small icon",
        "mail symbol",
    ]
    return any(marker in value for marker in markers)


def rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def median(values: list[int]) -> float | None:
    return round(float(statistics.median(values)), 2) if values else None


def analyze_manifest(manifest_path: Path, output_root: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    picture_description_enabled = any(
        item.get("picture_description_backend") != "none"
        for item in manifest.get("results", [])
    )
    rows = []
    total_figures = 0
    described_figures = 0
    total_chunks = 0
    ok_docs = 0

    for item in manifest.get("results", []):
        status = item.get("status")
        flags = []
        row: dict[str, Any] = {
            "candidate_id": item.get("candidate_id"),
            "status": status,
            "elapsed_sec": item.get("elapsed_sec"),
            "source_pdf": item.get("source_pdf"),
            "chunk_count": item.get("chunk_count", 0),
            "figure_count": item.get("figure_count", 0),
        }
        if status != "ok":
            flags.append("conversion_failed")
            row["flags"] = flags
            rows.append(row)
            continue

        ok_docs += 1
        chunk_path = resolve_repo_path(item.get("chunks"))
        markdown_path = resolve_repo_path(item.get("markdown"))
        doc_json_path = resolve_repo_path(item.get("docling_json"))
        figures_manifest_path = resolve_repo_path(item.get("figures_manifest"))

        markdown_text = markdown_path.read_text(encoding="utf-8") if markdown_path else ""
        chunks = read_jsonl(chunk_path) if chunk_path else []
        figures = read_json(figures_manifest_path) if figures_manifest_path else []
        descriptions = [description_text(fig) for fig in figures]
        desc_lengths = [len(text) for text in descriptions if text]

        empty_chunks = sum(1 for chunk in chunks if not (chunk.get("text") or "").strip())
        chunk_lengths = [len((chunk.get("text") or "").strip()) for chunk in chunks]
        figure_count = len(figures)
        figure_images = sum(1 for fig in figures if fig.get("image_path"))
        figure_descriptions = sum(1 for text in descriptions if text)
        short_descriptions = sum(1 for text in descriptions if 0 < len(text) < 80)
        non_scientific = sum(
            1 for text in descriptions if looks_like_non_scientific_figure(text)
        )

        total_chunks += len(chunks)
        total_figures += figure_count
        described_figures += figure_descriptions

        if len(markdown_text.strip()) < 3000:
            flags.append("low_markdown_chars")
        if len(chunks) < 5:
            flags.append("low_chunk_count")
        if chunks and empty_chunks / len(chunks) > 0.05:
            flags.append("empty_chunk_fraction_gt_5pct")
        if picture_description_enabled and figure_count and figure_descriptions < figure_count:
            flags.append("missing_figure_descriptions")
        if short_descriptions:
            flags.append("short_figure_descriptions")
        non_scientific_fraction = (
            non_scientific / figure_descriptions if figure_descriptions else None
        )
        non_scientific_item_fraction = (
            non_scientific / figure_count if figure_count else None
        )
        useful_descriptions = figure_descriptions - non_scientific
        if (
            non_scientific_fraction is not None
            and figure_descriptions >= 3
            and non_scientific_fraction > 0.3
        ):
            flags.append("high_non_scientific_description_fraction")

        row.update(
            {
                "markdown_chars": len(markdown_text),
                "markdown_headings": sum(
                    1 for line in markdown_text.splitlines() if line.startswith("#")
                ),
                "docling_json_bytes": doc_json_path.stat().st_size
                if doc_json_path
                else None,
                "chunk_count_actual": len(chunks),
                "empty_chunks": empty_chunks,
                "median_chunk_chars": median(chunk_lengths),
                "figure_count_actual": figure_count,
                "figure_images": figure_images,
                "figure_descriptions": figure_descriptions,
                "figure_description_coverage": round(
                    figure_descriptions / figure_count, 3
                )
                if figure_count
                else None,
                "median_description_chars": median(desc_lengths),
                "short_descriptions": short_descriptions,
                "non_scientific_or_logo_descriptions": non_scientific,
                "useful_figure_descriptions": useful_descriptions,
                "non_scientific_or_logo_fraction": round(non_scientific_fraction, 3)
                if non_scientific_fraction is not None
                else None,
                "non_scientific_or_logo_item_fraction": round(
                    non_scientific_item_fraction, 3
                )
                if non_scientific_item_fraction is not None
                else None,
                "useful_description_fraction": round(
                    useful_descriptions / figure_descriptions, 3
                )
                if figure_descriptions
                else None,
                "flags": flags,
                "markdown": rel(markdown_path),
                "chunks": rel(chunk_path),
                "figures_manifest": rel(figures_manifest_path),
            }
        )
        rows.append(row)

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "manifest": rel(manifest_path),
        "output_root": rel(output_root),
        "documents_total": len(manifest.get("results", [])),
        "documents_ok": ok_docs,
        "documents_failed": len(manifest.get("results", [])) - ok_docs,
        "success_rate": round(ok_docs / max(1, len(manifest.get("results", []))), 3),
        "total_chunks": total_chunks,
        "total_figures": total_figures,
        "described_figures": described_figures,
        "figure_description_coverage": round(described_figures / total_figures, 3)
        if total_figures
        else None,
        "non_scientific_or_logo_descriptions": sum(
            row.get("non_scientific_or_logo_descriptions", 0)
            for row in rows
            if row.get("status") == "ok"
        ),
        "useful_figure_descriptions": sum(
            row.get("useful_figure_descriptions", 0)
            for row in rows
            if row.get("status") == "ok"
        ),
        "documents_with_flags": sum(1 for row in rows if row.get("flags")),
        "picture_description_enabled": picture_description_enabled,
    }
    if summary["described_figures"]:
        summary["non_scientific_or_logo_fraction"] = round(
            summary["non_scientific_or_logo_descriptions"]
            / summary["described_figures"],
            3,
        )
        summary["useful_description_fraction"] = round(
            summary["useful_figure_descriptions"] / summary["described_figures"], 3
        )
    else:
        summary["non_scientific_or_logo_fraction"] = None
        summary["useful_description_fraction"] = None
    return {"summary": summary, "documents": rows}


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# Docling Codex batch quality report",
        "",
        "## Summary",
        "",
        f"- Documents: {summary['documents_ok']}/{summary['documents_total']} ok",
        f"- Success rate: {summary['success_rate']}",
        f"- Total chunks: {summary['total_chunks']}",
        f"- Total figures: {summary['total_figures']}",
        f"- Described figures: {summary['described_figures']}",
        f"- Figure description coverage: {summary['figure_description_coverage']}",
        f"- Non-scientific/logo descriptions: {summary['non_scientific_or_logo_descriptions']}",
        f"- Useful figure descriptions: {summary['useful_figure_descriptions']}",
        f"- Useful description fraction: {summary['useful_description_fraction']}",
        f"- Documents with QA flags: {summary['documents_with_flags']}",
        "",
        "## Documents",
        "",
        "| Candidate | Status | Chunks | Markdown chars | Figures described | Useful descriptions | Non-scientific/logo | Flags |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["documents"]:
        fig_desc = (
            f"{row.get('figure_descriptions', 0)}/{row.get('figure_count_actual', row.get('figure_count', 0))}"
            if row.get("status") == "ok"
            else ""
        )
        lines.append(
            "| {candidate} | {status} | {chunks} | {chars} | {fig_desc} | {useful} | {noise} | {flags} |".format(
                candidate=row.get("candidate_id", ""),
                status=row.get("status", ""),
                chunks=row.get("chunk_count_actual", row.get("chunk_count", "")),
                chars=row.get("markdown_chars", ""),
                fig_desc=fig_desc,
                useful=row.get("useful_figure_descriptions", ""),
                noise=row.get("non_scientific_or_logo_descriptions", ""),
                flags=", ".join(row.get("flags") or []),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    output_root = args.out.resolve()
    manifest_path = output_root / "manifests" / "docling_smoke_manifest.json"
    report = analyze_manifest(manifest_path, output_root)

    report_json = output_root / "manifests" / "quality_report.json"
    report_md = output_root / "manifests" / "quality_report.md"
    report_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_markdown(report, report_md)
    print(json.dumps({"report_json": str(report_json), "report_md": str(report_md)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
