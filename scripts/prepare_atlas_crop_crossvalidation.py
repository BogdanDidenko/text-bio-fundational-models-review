#!/usr/bin/env python3
"""Create exact crop-review panels for independent atlas cross-validation."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASELINE_ROOT = ROOT / "data/input_representation_atlas_redesign_2026-07-11"
OUTPUT_ROOT = ROOT / "data/input_representation_atlas_crop_crossvalidation_2026-07-12"
ATLAS_PATH = ROOT / "docs/input-representation-atlas/data/atlas.json"
LEDGER_PATH = BASELINE_ROOT / "model_crop_annotations.json"
FIGURE_ROOT = ROOT / "data/docling_include_vlm_52_2026-07-10_nolimits/figures"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str]) -> None:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stderr}")


def figure_manifests() -> dict[str, list[dict[str, Any]]]:
    manifests: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(FIGURE_ROOT.glob("*/figures_manifest.json")):
        figures = read_json(path)
        if figures:
            manifests[figures[0]["candidate_id"]] = figures
    return manifests


def compact_route(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "route_id": route["route_id"],
        "route_label": route["route_label"],
        "lifecycle_phase": route["lifecycle_phase"],
        "input_status": route["input_status"],
        "source_object_verbatim": route["source_object_verbatim"],
        "transformation_chain_verbatim": route["transformation_chain_verbatim"],
        "model_visible_form_verbatim": route["model_visible_form_verbatim"],
        "carrier_family": route["carrier_family"],
        "carrier_subtype": route["carrier_subtype"],
        "insertion_or_fusion_verbatim": route["insertion_or_fusion_verbatim"],
        "evidence_quote": route["evidence_quote"],
        "section_heading": route["section_heading"],
        "supporting_figure_or_table": route["supporting_figure_or_table"],
        "pages": route["pages"],
    }


def crop_pixels(crop: dict[str, float], width: int, height: int) -> tuple[int, int, int, int]:
    x = max(0, min(width - 1, math.floor(crop["x"] * width)))
    y = max(0, min(height - 1, math.floor(crop["y"] * height)))
    right = max(x + 1, min(width, math.ceil((crop["x"] + crop["width"]) * width)))
    bottom = max(y + 1, min(height, math.ceil((crop["y"] + crop["height"]) * height)))
    return x, y, right - x, bottom - y


def make_crop_panel(item: dict[str, Any], output: Path) -> dict[str, Any]:
    figure = item["figure"]
    source = ROOT / figure["image_path"]
    width = int(figure["pixel_width"])
    height = int(figure["pixel_height"])
    x, y, crop_width, crop_height = crop_pixels(item["crop_box"], width, height)
    stroke = max(4, round(max(width, height) / 220))
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "magick",
        "(", str(source), "-stroke", "#e11d48", "-strokewidth", str(stroke),
        "-fill", "none", "-draw", f"rectangle {x},{y} {x + crop_width - 1},{y + crop_height - 1}",
        "-resize", "1400x900>", "-bordercolor", "white", "-border", "10", ")",
        "(", str(source), "-crop", f"{crop_width}x{crop_height}+{x}+{y}", "+repage",
        "-resize", "900x900>", "-bordercolor", "#e11d48", "-border", "5", ")",
        "+append", "-background", "white", "-gravity", "center", "-quality", "92", str(output),
    ]
    run(command)
    return {
        "panel_path": str(output.relative_to(ROOT)),
        "panel_sha256": sha256(output),
        "pixel_crop": {"x": x, "y": y, "width": crop_width, "height": crop_height},
        "panel_layout": "left=full source figure with red crop rectangle; right=exact rendered crop",
    }


def make_no_figure_panel(
    model_id: str, figures: list[dict[str, Any]], output: Path
) -> dict[str, Any]:
    thumbnails = OUTPUT_ROOT / "review_panels/no_figure_thumbnails" / model_id
    if thumbnails.exists():
        shutil.rmtree(thumbnails)
    thumbnails.mkdir(parents=True, exist_ok=True)
    paths = []
    for figure in figures:
        source = ROOT / figure["image_path"]
        target = thumbnails / f"figure_{int(figure['figure_index']):03d}.jpg"
        run([
            "magick", str(source), "-thumbnail", "620x420>", "-background", "white",
            "-gravity", "center", "-extent", "640x460", "-bordercolor", "#aab6bd",
            "-border", "3", "-quality", "90", str(target),
        ])
        paths.append(target)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [paths[index:index + 3] for index in range(0, len(paths), 3)]
    command = ["magick"]
    for row in rows:
        command.extend(["(", *map(str, row)])
        if len(row) < 3:
            for _ in range(3 - len(row)):
                command.extend(["-size", "646x466", "xc:white"])
        command.extend(["+append", ")"])
    command.extend(["-append", "-quality", "92", str(output)])
    run(command)
    shutil.rmtree(thumbnails)
    return {
        "panel_path": str(output.relative_to(ROOT)),
        "panel_sha256": sha256(output),
        "panel_layout": "all source-paper figures in ascending figure_index, left-to-right then top-to-bottom",
        "figure_order": [int(figure["figure_index"]) for figure in figures],
    }


def main() -> int:
    atlas = read_json(ATLAS_PATH)
    ledger = read_json(LEDGER_PATH)
    architectures = {item["model_id"]: item for item in atlas["architectures"]}
    manifests = figure_manifests()
    panels = OUTPUT_ROOT / "review_panels"
    if panels.exists():
        shutil.rmtree(panels)
    panels.mkdir(parents=True)

    validation_manifest = []
    for ledger_item in ledger:
        model_id = ledger_item["model_id"]
        architecture = architectures[model_id]
        figures = manifests[architecture["record_id"]]
        record = {
            "model_id": model_id,
            "model_name": architecture["model_name"],
            "record_id": architecture["record_id"],
            "paper_title": architecture["paper_title"],
            "current_status": ledger_item["status"],
            "current_figure_index": (
                ledger_item["figure"]["figure_index"] if ledger_item["figure"] else None
            ),
            "current_crop_box": ledger_item["crop_box"],
            "current_rationale": ledger_item["rationale"],
            "routes": [compact_route(route) for route in architecture["routes"]],
            "figure_candidates": [
                {
                    "figure_index": int(figure["figure_index"]),
                    "page_no": figure.get("page_no"),
                    "caption": figure.get("caption") or "",
                    "vlm_descriptions": [
                        annotation.get("text")
                        for annotation in figure.get("annotations") or []
                        if annotation.get("text")
                    ],
                }
                for figure in figures
            ],
        }
        if ledger_item["status"] == "cropped_source_figure":
            record.update(
                make_crop_panel(
                    ledger_item,
                    panels / "current_crops" / f"{model_id}.jpg",
                )
            )
        else:
            record.update(
                make_no_figure_panel(
                    model_id,
                    figures,
                    panels / "no_figure_contact_sheets" / f"{model_id}.jpg",
                )
            )
        validation_manifest.append(record)

    if len(validation_manifest) != 111 or len({item["model_id"] for item in validation_manifest}) != 111:
        raise RuntimeError("Validation manifest must cover 111 unique models")
    write_json(OUTPUT_ROOT / "validation_manifest.json", validation_manifest)
    report = {
        "status": "ok",
        "model_count": len(validation_manifest),
        "crop_panels": sum(item["current_status"] == "cropped_source_figure" for item in validation_manifest),
        "no_figure_contact_sheets": sum(item["current_status"] == "no_suitable_figure" for item in validation_manifest),
        "baseline_ledger": str(LEDGER_PATH.relative_to(ROOT)),
        "output_root": str(OUTPUT_ROOT.relative_to(ROOT)),
    }
    write_json(OUTPUT_ROOT / "panel_build_report.json", report)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
