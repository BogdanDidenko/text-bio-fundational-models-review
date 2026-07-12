#!/usr/bin/env python3
"""Aggregate blind reviews and prepare every non-unanimous-pass case for adjudication."""

from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path
from typing import Any

from prepare_atlas_crop_crossvalidation import (
    OUTPUT_ROOT,
    ROOT,
    make_no_figure_panel,
    read_json,
    write_json,
)


def load_reviews(reviewer: str) -> dict[str, dict[str, Any]]:
    reviews: dict[str, dict[str, Any]] = {}
    pattern = OUTPUT_ROOT / "subagents" / reviewer / "batch_*" / "response.json"
    for path_value in sorted(glob.glob(str(pattern))):
        path = Path(path_value)
        for review in read_json(path)["reviews"]:
            model_id = review["model_id"]
            if model_id in reviews:
                raise RuntimeError(f"Duplicate {reviewer} review for {model_id}")
            reviews[model_id] = review
    return reviews


def main() -> int:
    manifest = read_json(OUTPUT_ROOT / "validation_manifest.json")
    validator_a = load_reviews("validator_a")
    validator_b = load_reviews("validator_b")
    expected = {item["model_id"] for item in manifest}
    if set(validator_a) != expected or set(validator_b) != expected:
        raise RuntimeError("Both validators must cover all 111 models exactly once")

    consensus = []
    adjudication = []
    for item in manifest:
        model_id = item["model_id"]
        review_a = validator_a[model_id]
        review_b = validator_b[model_id]
        unanimous_accept = (
            review_a["decision"] == "accept_as_is"
            and review_b["decision"] == "accept_as_is"
        )
        consensus_item = {
            "model_id": model_id,
            "model_name": item["model_name"],
            "current_status": item["current_status"],
            "review_a": review_a,
            "review_b": review_b,
            "unanimous_accept_as_is": unanimous_accept,
            "requires_adjudication": not unanimous_accept,
        }
        consensus.append(consensus_item)
        if unanimous_accept:
            continue
        candidate_panel = OUTPUT_ROOT / "review_panels/adjudication_candidates" / f"{model_id}.jpg"
        candidate_meta = make_no_figure_panel(
            model_id,
            [
                {
                    "figure_index": candidate["figure_index"],
                    "image_path": next(
                        figure["image_path"]
                        for figure in _figure_manifest(item["record_id"])
                        if int(figure["figure_index"]) == int(candidate["figure_index"])
                    ),
                }
                for candidate in item["figure_candidates"]
            ],
            candidate_panel,
        )
        adjudication.append(
            {
                **item,
                "review_a": review_a,
                "review_b": review_b,
                "candidate_panel_path": candidate_meta["panel_path"],
                "candidate_panel_sha256": candidate_meta["panel_sha256"],
                "candidate_figure_order": candidate_meta["figure_order"],
            }
        )

    write_json(OUTPUT_ROOT / "validation_consensus.json", consensus)
    write_json(OUTPUT_ROOT / "adjudication_manifest.json", adjudication)
    pair_counts = Counter(
        (item["review_a"]["decision"], item["review_b"]["decision"])
        for item in consensus
    )
    report = {
        "status": "ok",
        "models": len(consensus),
        "unanimous_accept_as_is": sum(item["unanimous_accept_as_is"] for item in consensus),
        "requires_adjudication": len(adjudication),
        "decision_pairs": {
            f"{left}__{right}": count for (left, right), count in sorted(pair_counts.items())
        },
    }
    write_json(OUTPUT_ROOT / "crossvalidation_interim_report.json", report)
    print(json.dumps(report, ensure_ascii=False))
    return 0


def _figure_manifest(record_id: str) -> list[dict[str, Any]]:
    figure_root = ROOT / "data/docling_include_vlm_52_2026-07-10_nolimits/figures"
    for path in figure_root.glob("*/figures_manifest.json"):
        figures = read_json(path)
        if figures and figures[0]["candidate_id"] == record_id:
            return figures
    raise RuntimeError(f"Missing figure manifest for {record_id}")


if __name__ == "__main__":
    raise SystemExit(main())
