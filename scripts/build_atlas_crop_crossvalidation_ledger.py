#!/usr/bin/env python3
"""Build the provisional cross-validated ledger and exact final preview panels."""

from __future__ import annotations

import json
import shutil
import struct
from pathlib import Path
from typing import Any

from prepare_atlas_crop_crossvalidation import (
    FIGURE_ROOT,
    OUTPUT_ROOT,
    ROOT,
    compact_route,
    make_crop_panel,
    read_json,
    write_json,
)


BASELINE_LEDGER = ROOT / "data/input_representation_atlas_redesign_2026-07-11/model_crop_annotations.json"
ATLAS_PATH = ROOT / "docs/input-representation-atlas/data/atlas.json"


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise RuntimeError(f"Expected PNG: {path}")
    return struct.unpack(">II", header[16:24])


def load_responses(root: Path, value_key: str) -> dict[str, dict[str, Any]]:
    result = {}
    for path in root.glob("*/response.json"):
        value = read_json(path)[value_key]
        result[value["model_id"]] = value
    return result


def figure_manifests() -> dict[str, dict[int, dict[str, Any]]]:
    result = {}
    for path in FIGURE_ROOT.glob("*/figures_manifest.json"):
        figures = read_json(path)
        if figures:
            result[figures[0]["candidate_id"]] = {
                int(figure["figure_index"]): figure for figure in figures
            }
    return result


def confidence_min(left: str, right: str) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    return left if order[left] <= order[right] else right


def main() -> int:
    atlas = read_json(ATLAS_PATH)
    architectures = {item["model_id"]: item for item in atlas["architectures"]}
    baseline = {item["model_id"]: item for item in read_json(BASELINE_LEDGER)}
    consensus = {item["model_id"]: item for item in read_json(OUTPUT_ROOT / "validation_consensus.json")}
    adjudications = load_responses(OUTPUT_ROOT / "subagents/adjudicator", "adjudication")
    replacements = load_responses(OUTPUT_ROOT / "subagents/replacement_cropper", "crop")
    figures = figure_manifests()

    ledger = []
    for model_id, architecture in architectures.items():
        consensus_item = consensus[model_id]
        cross_validation = {
            "validator_a": consensus_item["review_a"],
            "validator_b": consensus_item["review_b"],
            "adjudication": adjudications.get(model_id),
            "replacement_crop": replacements.get(model_id),
        }
        if consensus_item["unanimous_accept_as_is"]:
            item = dict(baseline[model_id])
            item["confidence"] = confidence_min(
                consensus_item["review_a"]["confidence"],
                consensus_item["review_b"]["confidence"],
            )
            item["annotation_pass"] = "two_blind_validators_accept"
            item["cross_validation"] = cross_validation
            ledger.append(item)
            continue

        decision = adjudications[model_id]
        if decision["decision"] == "no_suitable_figure" or (
            decision["decision"] == "accept_current"
            and baseline[model_id]["status"] == "no_suitable_figure"
        ):
            ledger.append(
                {
                    "model_id": model_id,
                    "record_id": architecture["record_id"],
                    "status": "no_suitable_figure",
                    "figure": None,
                    "crop_box": None,
                    "panel_label": "",
                    "visible_input_object": "",
                    "visible_model_interface": "",
                    "figure_suitability": "unsuitable",
                    "confidence": decision["confidence"],
                    "rationale": decision["rationale"],
                    "annotation_pass": "two_blind_validators_plus_adjudicator_no_figure",
                    "cross_validation": cross_validation,
                }
            )
            continue

        if decision["decision"] in {"accept_current", "adjust_current"}:
            item = dict(baseline[model_id])
            if not item.get("figure"):
                raise RuntimeError(f"Adjudicator accepted missing current figure for {model_id}")
            if decision["final_crop_box"] is not None:
                item["crop_box"] = decision["final_crop_box"]
            item["confidence"] = decision["confidence"]
            item["rationale"] = decision["rationale"]
            item["annotation_pass"] = f"two_blind_validators_plus_adjudicator_{decision['decision']}"
            item["cross_validation"] = cross_validation
            ledger.append(item)
            continue

        replacement = replacements[model_id]
        figure = figures[architecture["record_id"]][int(replacement["figure_index"])]
        source = ROOT / figure["image_path"]
        width, height = png_dimensions(source)
        ledger.append(
            {
                "model_id": model_id,
                "record_id": architecture["record_id"],
                "status": "cropped_source_figure",
                "figure": {
                    "figure_index": int(figure["figure_index"]),
                    "image_path": figure["image_path"],
                    "caption": figure.get("caption") or "",
                    "page_no": figure.get("page_no"),
                    "pixel_width": width,
                    "pixel_height": height,
                },
                "crop_box": replacement["crop_box"],
                "panel_label": replacement["panel_label"],
                "visible_input_object": replacement["visible_input_object"],
                "visible_model_interface": replacement["visible_model_interface"],
                "figure_suitability": "suitable",
                "confidence": confidence_min(decision["confidence"], replacement["confidence"]),
                "rationale": replacement["rationale"],
                "selection_rationale": decision["rationale"],
                "annotation_pass": "two_blind_validators_plus_adjudicator_replacement_crop",
                "cross_validation": cross_validation,
            }
        )

    if len(ledger) != 111 or len({item["model_id"] for item in ledger}) != 111:
        raise RuntimeError("Provisional ledger must contain 111 unique models")
    write_json(OUTPUT_ROOT / "provisional_crossvalidated_crop_ledger.json", ledger)

    final_panels = OUTPUT_ROOT / "review_panels/final_crops"
    if final_panels.exists():
        shutil.rmtree(final_panels)
    final_panels.mkdir(parents=True)
    final_manifest = []
    for item in ledger:
        architecture = architectures[item["model_id"]]
        if item["status"] != "cropped_source_figure":
            continue
        panel = make_crop_panel(item, final_panels / f"{item['model_id']}.jpg")
        final_manifest.append(
            {
                "model_id": item["model_id"],
                "model_name": architecture["model_name"],
                "paper_title": architecture["paper_title"],
                "record_id": architecture["record_id"],
                "final_figure_index": item["figure"]["figure_index"],
                "final_crop_box": item["crop_box"],
                "panel_path": panel["panel_path"],
                "panel_sha256": panel["panel_sha256"],
                "panel_layout": panel["panel_layout"],
                "routes": [compact_route(route) for route in architecture["routes"]],
                "cross_validation": item["cross_validation"],
            }
        )
    write_json(OUTPUT_ROOT / "final_preview_validation_manifest.json", final_manifest)
    report = {
        "status": "ok",
        "models": len(ledger),
        "final_crops_pending_preview_validation": len(final_manifest),
        "no_suitable_figure": sum(item["status"] == "no_suitable_figure" for item in ledger),
        "unanimous_current_crops": sum(item["annotation_pass"] == "two_blind_validators_accept" for item in ledger),
        "adjudicated_current_crops": sum("adjudicator_accept_current" in item["annotation_pass"] for item in ledger),
        "adjusted_current_crops": sum("adjudicator_adjust_current" in item["annotation_pass"] for item in ledger),
        "replacement_crops": sum("replacement_crop" in item["annotation_pass"] for item in ledger),
    }
    write_json(OUTPUT_ROOT / "provisional_ledger_report.json", report)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
