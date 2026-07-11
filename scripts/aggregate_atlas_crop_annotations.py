#!/usr/bin/env python3
"""Aggregate the two-pass figure crop review into one validated model ledger."""

from __future__ import annotations

import json
import struct
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "docs/input-representation-atlas/data/atlas.json"
SUBAGENTS = ROOT / "data/input_representation_atlas_redesign_2026-07-11/subagents"
OUTPUT_ROOT = ROOT / "data/input_representation_atlas_redesign_2026-07-11"
CORPUS_FIGURES = ROOT / "data/docling_include_vlm_52_2026-07-10_nolimits/figures"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def collect(pattern: str, field: str, key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(SUBAGENTS.glob(pattern)):
        for item in read_json(path)[field]:
            if item[key] in result:
                raise RuntimeError(f"Duplicate {key}={item[key]} in {path}")
            result[item[key]] = item
    return result


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        signature = stream.read(24)
    if signature[:8] != b"\x89PNG\r\n\x1a\n" or signature[12:16] != b"IHDR":
        raise RuntimeError(f"Expected PNG figure: {path}")
    return struct.unpack(">II", signature[16:24])


def manifests() -> dict[str, dict[int, dict[str, Any]]]:
    result: dict[str, dict[int, dict[str, Any]]] = {}
    for path in sorted(CORPUS_FIGURES.glob("*/figures_manifest.json")):
        figures = read_json(path)
        if figures:
            result[figures[0]["candidate_id"]] = {
                int(figure["figure_index"]): figure for figure in figures
            }
    return result


def validate_crop(model_id: str, crop: dict[str, float]) -> None:
    for key in ("x", "y", "width", "height"):
        if not 0 <= float(crop[key]) <= 1:
            raise RuntimeError(f"{model_id}: crop {key} outside [0,1]")
    if crop["width"] <= 0 or crop["height"] <= 0:
        raise RuntimeError(f"{model_id}: empty crop")
    if crop["x"] + crop["width"] > 1.0001 or crop["y"] + crop["height"] > 1.0001:
        raise RuntimeError(f"{model_id}: crop extends outside image")


def main() -> int:
    atlas = read_json(ATLAS)
    first = collect("crops/batch_*/response.json", "annotations", "model_id")
    selections = collect("reselect/paper_*/response.json", "selections", "model_id")
    second = collect("recrop/batch_*/response.json", "annotations", "model_id")
    retry = collect("recrop_retry/*/response.json", "annotations", "model_id")
    overlap = set(second) & set(retry)
    if overlap:
        raise RuntimeError(f"Duplicate recrop retry models: {sorted(overlap)}")
    second.update(retry)
    figure_manifests = manifests()

    ledger = []
    for architecture in atlas["architectures"]:
        model_id = architecture["model_id"]
        selection = selections.get(model_id)
        if selection and selection["figure_index"] is None:
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
                    "confidence": selection["confidence"],
                    "rationale": selection["rationale"],
                    "annotation_pass": "figure_reselection",
                }
            )
            continue

        if selection:
            annotation = second.get(model_id)
            if annotation is None:
                raise RuntimeError(f"Missing second-pass crop for {model_id}")
            figure_index = int(selection["figure_index"])
            annotation_pass = "reselection_and_recrop"
            selection_rationale = selection["rationale"]
        else:
            annotation = first.get(model_id)
            if annotation is None:
                raise RuntimeError(f"Missing first-pass crop for {model_id}")
            if annotation["figure_suitability"] == "unsuitable":
                raise RuntimeError(f"Unresolved unsuitable first-pass crop for {model_id}")
            figure_index = int(annotation["figure_index"])
            annotation_pass = "initial_crop"
            selection_rationale = architecture["figure"].get("selection_reasons", [])

        crop = annotation["crop_box"]
        validate_crop(model_id, crop)
        figure = figure_manifests[architecture["record_id"]][figure_index]
        source_path = ROOT / figure["image_path"]
        width, height = png_dimensions(source_path)
        ledger.append(
            {
                "model_id": model_id,
                "record_id": architecture["record_id"],
                "status": "cropped_source_figure",
                "figure": {
                    "figure_index": figure_index,
                    "image_path": figure["image_path"],
                    "caption": figure.get("caption") or "",
                    "page_no": figure.get("page_no"),
                    "pixel_width": width,
                    "pixel_height": height,
                },
                "crop_box": crop,
                "panel_label": annotation["panel_label"],
                "visible_input_object": annotation["visible_input_object"],
                "visible_model_interface": annotation["visible_model_interface"],
                "figure_suitability": annotation["figure_suitability"],
                "confidence": annotation["confidence"],
                "rationale": annotation["rationale"],
                "selection_rationale": selection_rationale,
                "annotation_pass": annotation_pass,
            }
        )

    model_ids = [item["model_id"] for item in ledger]
    expected = [item["model_id"] for item in atlas["architectures"]]
    if len(model_ids) != 111 or set(model_ids) != set(expected):
        raise RuntimeError("Crop ledger does not cover exactly the 111 atlas models")
    status_counts = Counter(item["status"] for item in ledger)
    suitability_counts = Counter(item["figure_suitability"] for item in ledger)
    confidence_counts = Counter(item["confidence"] for item in ledger)
    report = {
        "status": "ok",
        "model_count": len(ledger),
        "status_counts": dict(status_counts),
        "suitability_counts": dict(suitability_counts),
        "confidence_counts": dict(confidence_counts),
        "full_or_near_full_crops": sum(
            bool(item["crop_box"])
            and item["crop_box"]["width"] >= 0.9
            and item["crop_box"]["height"] >= 0.9
            for item in ledger
        ),
        "initial_crops": sum(item["annotation_pass"] == "initial_crop" for item in ledger),
        "reselected_and_recropped": sum(
            item["annotation_pass"] == "reselection_and_recrop" for item in ledger
        ),
        "explicit_no_suitable_figure": status_counts["no_suitable_figure"],
        "subagent_log_root": str(SUBAGENTS.relative_to(ROOT)),
    }
    write_json(OUTPUT_ROOT / "model_crop_annotations.json", ledger)
    write_json(OUTPUT_ROOT / "crop_annotation_audit.json", report)
    (OUTPUT_ROOT / "crop_annotation_audit.md").write_text(
        "# Model figure crop audit\n\n"
        "This ledger preserves model-specific source-figure selection and normalized crop "
        "coordinates. Source pixels are not altered; the web atlas applies the recorded crop "
        "as a viewport over the canonical PNG.\n\n"
        f"- Models: {report['model_count']}\n"
        f"- Cropped source figures: {status_counts['cropped_source_figure']}\n"
        f"- Explicit no-suitable-figure cases: {status_counts['no_suitable_figure']}\n"
        f"- Initial crops retained: {report['initial_crops']}\n"
        f"- Figures reselected and recropped: {report['reselected_and_recropped']}\n"
        f"- Full or near-full crops: {report['full_or_near_full_crops']}\n"
        f"- Subagent logs: `{report['subagent_log_root']}`\n\n"
        "A `no_suitable_figure` status is intentional: performance plots, outputs, logos, and "
        "other non-input figures are not used as visual evidence.\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
