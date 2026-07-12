#!/usr/bin/env python3
"""Freeze the scope-adjudicated crop ledger and render its exact canonical panels."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from build_atlas_crop_crossvalidation_ledger import figure_manifests, png_dimensions
from prepare_atlas_crop_crossvalidation import (
    OUTPUT_ROOT as RUN_ROOT,
    ROOT,
    compact_route,
    make_crop_panel,
    read_json,
    write_json,
)


ATLAS_PATH = ROOT / "docs/input-representation-atlas/data/atlas.json"


def load_batch_reviews(role: str) -> dict[str, dict[str, Any]]:
    result = {}
    for path in (RUN_ROOT / "subagents" / role).glob("batch_*/response.json"):
        for review in read_json(path)["reviews"]:
            result[review["model_id"]] = review
    return result


def load_single(role: str, key: str) -> dict[str, dict[str, Any]]:
    result = {}
    for path in (RUN_ROOT / "subagents" / role).glob("*/response.json"):
        value = read_json(path)[key]
        result[value["model_id"]] = value
    return result


def main() -> int:
    atlas = read_json(ATLAS_PATH)
    architectures = {item["model_id"]: item for item in atlas["architectures"]}
    base = read_json(RUN_ROOT / "post_role_crossvalidated_crop_ledger.json")
    preview_reviews = load_batch_reviews("post_role_preview_validator")
    integrity_reviews = load_batch_reviews("post_role_input_integrity_validator")
    adjudications = load_single("post_role_scope_adjudicator", "adjudication")
    replacements = load_single("post_role_scope_replacement_cropper", "crop")
    figures = figure_manifests()
    ledger = []
    changed_ids = []

    for original in base:
        model_id = original["model_id"]
        cross_validation = dict(original.get("cross_validation") or {})
        if model_id in preview_reviews:
            cross_validation["post_role_preview_validation"] = preview_reviews[model_id]
            cross_validation["post_role_input_integrity_validation"] = integrity_reviews[model_id]
        decision = adjudications.get(model_id)
        if decision is None:
            item = dict(original)
            item["cross_validation"] = cross_validation
            ledger.append(item)
            continue
        cross_validation["post_role_scope_adjudication"] = decision
        if decision["decision"] == "no_suitable_figure":
            ledger.append(
                {
                    "model_id": model_id,
                    "record_id": original["record_id"],
                    "status": "no_suitable_figure",
                    "figure": None,
                    "crop_box": None,
                    "panel_label": "",
                    "visible_input_object": "",
                    "visible_model_interface": "",
                    "figure_suitability": "unsuitable",
                    "confidence": decision["confidence"],
                    "rationale": decision["rationale"],
                    "annotation_pass": "post_role_scope_adjudicator_no_figure",
                    "cross_validation": cross_validation,
                }
            )
            continue
        if decision["decision"] in {"accept_current", "adjust_current"}:
            item = dict(original)
            if decision["final_crop_box"] is not None:
                item["crop_box"] = decision["final_crop_box"]
            item["confidence"] = decision["confidence"]
            item["rationale"] = decision["rationale"]
            item["annotation_pass"] = f"post_role_scope_adjudicator_{decision['decision']}"
            item["cross_validation"] = cross_validation
            ledger.append(item)
            if decision["decision"] == "adjust_current":
                changed_ids.append(model_id)
            continue
        replacement = replacements[model_id]
        figure = figures[architectures[model_id]["record_id"]][int(replacement["figure_index"])]
        source = ROOT / figure["image_path"]
        width, height = png_dimensions(source)
        cross_validation["post_role_scope_replacement_crop"] = replacement
        ledger.append(
            {
                "model_id": model_id,
                "record_id": original["record_id"],
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
                "confidence": replacement["confidence"],
                "rationale": replacement["rationale"],
                "selection_rationale": decision["rationale"],
                "annotation_pass": "post_role_scope_adjudicator_replacement_crop",
                "cross_validation": cross_validation,
            }
        )
        changed_ids.append(model_id)

    crops = [item for item in ledger if item["status"] == "cropped_source_figure"]
    no_figure = [item for item in ledger if item["status"] == "no_suitable_figure"]
    if len(ledger) != 111 or len(crops) != 79 or len(no_figure) != 32:
        raise RuntimeError(f"Unexpected canonical counts: {len(ledger)}/{len(crops)}/{len(no_figure)}")
    if len(changed_ids) != 6:
        raise RuntimeError(f"Expected six final changed crops, got {len(changed_ids)}")
    write_json(RUN_ROOT / "final_crossvalidated_crop_ledger.json", ledger)

    panel_root = RUN_ROOT / "review_panels/canonical_final_crops"
    if panel_root.exists():
        shutil.rmtree(panel_root)
    panel_root.mkdir(parents=True)
    manifest = []
    for item in crops:
        architecture = architectures[item["model_id"]]
        panel = make_crop_panel(item, panel_root / f"{item['model_id']}.jpg")
        manifest.append(
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
            }
        )
    write_json(RUN_ROOT / "canonical_preview_manifest.json", manifest)
    write_json(
        RUN_ROOT / "canonical_changed_preview_manifest.json",
        [item for item in manifest if item["model_id"] in changed_ids],
    )
    report = {
        "status": "pending_final_changed_crop_verification",
        "models": len(ledger),
        "crops": len(crops),
        "no_suitable_figure": len(no_figure),
        "final_scope_adjudications": len(adjudications),
        "accepted_current": sum(item["decision"] == "accept_current" for item in adjudications.values()),
        "adjusted_current": sum(item["decision"] == "adjust_current" for item in adjudications.values()),
        "replacement_figures": sum(item["decision"] == "replace_figure" for item in adjudications.values()),
        "removed_as_no_figure": sum(item["decision"] == "no_suitable_figure" for item in adjudications.values()),
        "changed_ids": changed_ids,
    }
    write_json(RUN_ROOT / "canonical_ledger_interim_report.json", report)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
