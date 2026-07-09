#!/usr/bin/env python3
"""Compare Docling/Codex iteration QA reports."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]


def as_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO / path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float | None) -> str:
    if value is None:
        return ""
    return f"{100 * value:.1f}%"


def safe_div(num: float, den: float) -> float | None:
    return round(num / den, 3) if den else None


def load_iteration(output_root: Path) -> dict[str, Any]:
    qa = read_json(output_root / "manifests" / "quality_report.json")
    manifest = read_json(output_root / "manifests" / "docling_smoke_manifest.json")
    config_path = output_root / "manifests" / "iteration_config.json"
    if not config_path.exists():
        config_path = output_root / "manifests" / "run_config.json"
    config = read_json(config_path)
    summary = qa["summary"]
    elapsed_values = [row.get("elapsed_sec", 0) for row in manifest.get("results", [])]
    total_elapsed = sum(float(v or 0) for v in elapsed_values)
    useful = summary.get("useful_figure_descriptions", 0)
    described = summary.get("described_figures", 0)
    noise = summary.get("non_scientific_or_logo_descriptions", 0)
    settings = config.get("settings", {})
    return {
        "name": config.get("name") or output_root.name,
        "output_root": str(output_root.relative_to(REPO)),
        "threshold": settings.get("picture_description_area_threshold"),
        "prompt": "strict" if settings.get("picture_description_prompt") else "default",
        "documents_ok": summary.get("documents_ok"),
        "documents_failed": summary.get("documents_failed"),
        "chunks": summary.get("total_chunks"),
        "total_picture_items": summary.get("total_figures"),
        "vlm_descriptions": described,
        "useful_descriptions": useful,
        "noise_descriptions": noise,
        "coverage": summary.get("figure_description_coverage"),
        "useful_fraction": summary.get("useful_description_fraction"),
        "noise_fraction": summary.get("non_scientific_or_logo_fraction"),
        "documents_with_flags": summary.get("documents_with_flags"),
        "elapsed_sec": round(total_elapsed, 2),
        "elapsed_min": round(total_elapsed / 60, 2),
        "sec_per_vlm_description": safe_div(total_elapsed, described),
        "sec_per_useful_description": safe_div(total_elapsed, useful),
        "median_doc_elapsed_sec": round(float(statistics.median(elapsed_values)), 2)
        if elapsed_values
        else None,
    }


def write_markdown(rows: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Docling Codex VLM iteration comparison",
        "",
        f"Generated at: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}",
        "",
        "Notes:",
        "",
        "- Coverage is measured over all Docling picture items, including small icons/logos.",
        "- For thresholded runs, lower coverage can be intentional because small picture items are skipped before VLM.",
        "- Flags are inherited from the structural QA report and include expected `missing_figure_descriptions` in thresholded runs.",
        "",
        "| Iteration | Threshold | Prompt | OK | VLM desc | Useful | Noise | Useful fraction | Coverage | Time min | sec/useful | Flags |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {name} | {threshold} | {prompt} | {ok} | {vlm} | {useful} | {noise} | {useful_fraction} | {coverage} | {elapsed} | {sec_useful} | {flags} |".format(
                name=row["name"],
                threshold=row["threshold"],
                prompt=row["prompt"],
                ok=row["documents_ok"],
                vlm=row["vlm_descriptions"],
                useful=row["useful_descriptions"],
                noise=row["noise_descriptions"],
                useful_fraction=pct(row["useful_fraction"]),
                coverage=pct(row["coverage"]),
                elapsed=row["elapsed_min"],
                sec_useful=row["sec_per_useful_description"],
                flags=row["documents_with_flags"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iteration-config", type=Path, required=True)
    args = parser.parse_args()

    config = read_json(args.iteration_config)
    output_dir = as_path(config.get("comparison_output", "data/docling_iteration_comparison_2026-07-08"))
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [load_iteration(as_path(item["output_root"])) for item in config["iterations"]]
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "iteration_config": str(args.iteration_config),
        "iterations": rows,
    }
    report_json = output_dir / "comparison_report.json"
    report_md = output_dir / "comparison_report.md"
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(rows, report_md)
    print(json.dumps({"report_json": str(report_json), "report_md": str(report_md)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
