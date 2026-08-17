#!/usr/bin/env python3
"""Select and crop replacement figures for unresolved F7 atlas previews."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from run_atlas_exact_preview_validation import (
    DEFAULT_ATLAS,
    DEFAULT_MODEL,
    DEFAULT_OUTPUT,
    ROOT,
    adjudication_index,
    compact_route,
    read_json,
    render_crop_panel,
    role_review_index,
    run_codex_attempt,
    sha256,
    valid_crop_box,
    validate_review_response,
    write_json,
)


SELECTOR_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "model_id",
        "decision",
        "figure_index",
        "route_ids_supported",
        "visible_input_evidence",
        "concise_rationale",
        "confidence",
    ],
    "properties": {
        "model_id": {"type": "string"},
        "decision": {"type": "string", "enum": ["select_figure", "no_suitable_figure"]},
        "figure_index": {"type": ["integer", "null"]},
        "route_ids_supported": {"type": "array", "items": {"type": "string"}},
        "visible_input_evidence": {"type": "array", "items": {"type": "string"}},
        "concise_rationale": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
}

CROPPER_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "model_id",
        "crop_box",
        "route_ids_supported",
        "visible_input_object",
        "visible_model_interface",
        "panel_label",
        "concise_rationale",
        "confidence",
    ],
    "properties": {
        "model_id": {"type": "string"},
        "crop_box": {
            "type": "object",
            "additionalProperties": False,
            "required": ["x", "y", "width", "height"],
            "properties": {
                "x": {"type": "number", "minimum": 0, "maximum": 1},
                "y": {"type": "number", "minimum": 0, "maximum": 1},
                "width": {"type": "number", "minimum": 0.03, "maximum": 1},
                "height": {"type": "number", "minimum": 0.03, "maximum": 1},
            },
        },
        "route_ids_supported": {"type": "array", "items": {"type": "string"}},
        "visible_input_object": {"type": "string"},
        "visible_model_interface": {"type": "string"},
        "panel_label": {"type": "string"},
        "concise_rationale": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
}


def figure_text(figure: dict[str, Any]) -> list[str]:
    return [
        annotation.get("text") or ""
        for annotation in figure.get("annotations") or []
        if annotation.get("text")
    ]


def run_magick(command: list[str]) -> None:
    from run_atlas_exact_preview_validation import run_command

    run_command(command)


def image_dimensions(path: Path) -> tuple[int, int]:
    result = subprocess.run(
        ["magick", "identify", "-format", "%w %h", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(f"Could not identify {path}: {result.stderr}")
    width, height = result.stdout.strip().split()
    return int(width), int(height)


def make_contact_sheet(model_id: str, figures: list[dict[str, Any]], output_dir: Path) -> Path:
    thumb_dir = output_dir / "review_panels/replacement_thumbnails" / model_id
    if thumb_dir.exists():
        shutil.rmtree(thumb_dir)
    thumb_dir.mkdir(parents=True, exist_ok=True)
    thumbnails = []
    for figure in figures:
        source = Path(figure["local_image_path"])
        target = thumb_dir / f"figure_{int(figure['figure_index']):03d}.jpg"
        run_magick(
            [
                "magick",
                str(source),
                "-thumbnail",
                "620x400>",
                "-background",
                "white",
                "-gravity",
                "center",
                "-extent",
                "640x440",
                "-gravity",
                "north",
                "-fill",
                "#111111",
                "-font",
                "/System/Library/Fonts/Helvetica.ttc",
                "-pointsize",
                "22",
                "-annotate",
                "+0+8",
                f"Figure {int(figure['figure_index'])}",
                "-bordercolor",
                "#94a3b8",
                "-border",
                "3",
                str(target),
            ]
        )
        thumbnails.append(target)
    sheet = output_dir / "review_panels/replacement_contact_sheets" / f"{model_id}.jpg"
    sheet.parent.mkdir(parents=True, exist_ok=True)
    run_magick(
        [
            "magick",
            "montage",
            *map(str, thumbnails),
            "-font",
            "/System/Library/Fonts/Helvetica.ttc",
            "-tile",
            "3x",
            "-geometry",
            "+8+8",
            "-background",
            "white",
            "-quality",
            "92",
            str(sheet),
        ]
    )
    shutil.rmtree(thumb_dir)
    return sheet


def replacement_model_ids(output_dir: Path) -> set[str]:
    ids = {
        model_id
        for model_id, review in adjudication_index(output_dir).items()
        if review["final_action"] == "replacement_required"
    }
    changed = role_review_index(output_dir, "changed_preview_validator")
    ids.update(model_id for model_id, review in changed.items() if review["decision"] != "pass")
    return ids


def prepare(
    *, output_dir: Path, profile_manifest: Path, source_root: Path
) -> list[dict[str, Any]]:
    preview = {item["model_id"]: item for item in read_json(output_dir / "preview_manifest.json")}
    target_ids = replacement_model_ids(output_dir)
    with profile_manifest.open(encoding="utf-8", newline="") as stream:
        profiles = {row["candidate_id"]: row for row in csv.DictReader(stream)}
    cases = []
    for model_id in sorted(target_ids):
        item = preview[model_id]
        profile = profiles[item["record_id"]]
        figures_manifest = Path(profile["figures_manifest"])
        if not figures_manifest.is_absolute():
            figures_manifest = source_root / figures_manifest
        figures = read_json(figures_manifest)
        candidates = []
        for figure in figures:
            image_path = Path(figure["image_path"])
            if not image_path.is_absolute():
                image_path = source_root / image_path
            if not image_path.exists():
                raise FileNotFoundError(image_path)
            width, height = image_dimensions(image_path)
            candidates.append(
                {
                    "figure_index": int(figure["figure_index"]),
                    "page_no": figure.get("page_no"),
                    "caption": figure.get("caption") or "",
                    "vlm_descriptions": figure_text(figure),
                    "manifest_image_path": figure["image_path"],
                    "local_image_path": str(image_path),
                    "image_sha256": sha256(image_path),
                    "pixel_width": width,
                    "pixel_height": height,
                }
            )
        contact_sheet = make_contact_sheet(model_id, candidates, output_dir)
        cases.append(
            {
                **item,
                "replacement_reason": (
                    adjudication_index(output_dir).get(model_id)
                    or role_review_index(output_dir, "changed_preview_validator").get(model_id)
                ),
                "figure_candidates": candidates,
                "contact_sheet_path": str(contact_sheet.relative_to(ROOT)),
                "contact_sheet_sha256": sha256(contact_sheet),
            }
        )
    write_json(output_dir / "replacement_selection_manifest.json", cases)
    return cases


def selector_prompt(case: dict[str, Any]) -> str:
    figures = [
        {
            "figure_index": figure["figure_index"],
            "page_no": figure["page_no"],
            "caption": figure["caption"],
            "vlm_descriptions": figure["vlm_descriptions"],
        }
        for figure in case["figure_candidates"]
    ]
    return f"""You are a blind replacement-figure selector for a scientific input-representation atlas.

The attached contact sheet shows every available source-paper figure, numbered in ascending order. Select a figure only if its visible pixels can support a coherent crop showing an actual input, transformation, model-visible carrier, or immediate interface for the exact named model and at least one listed route. Reject outputs, downstream consumers, graders, benchmark/results panels, generic summaries, wrong variants, and wrong lifecycle/configurations. If no figure responsibly supports a route, return `no_suitable_figure`.

Do not use tools, external knowledge, earlier crop decisions, or hidden chain-of-thought.

MODEL
{json.dumps({key: case[key] for key in ['model_id', 'model_name', 'paper_title', 'record_id', 'routes', 'replacement_reason']}, ensure_ascii=False, indent=2)}

FIGURE ORDER AND METADATA
{json.dumps(figures, ensure_ascii=False, indent=2)}
"""


def cropper_prompt(case: dict[str, Any], selection: dict[str, Any], figure: dict[str, Any]) -> str:
    return f"""You are a source-figure cropper for a scientific input-representation atlas.

The attached image is the selected full source figure. Return the smallest coherent normalized rectangle that visibly and readably shows an actual input, transformation, model-visible carrier, or immediate interface for the exact named model and at least one listed route. Preserve labels and arrows needed to understand the input path. Exclude outputs, results, downstream consumers, unrelated variants, and decorative content. Ensure x+width <= 1 and y+height <= 1.

Do not use tools, external knowledge, or hidden chain-of-thought.

CASE
{json.dumps({key: case[key] for key in ['model_id', 'model_name', 'paper_title', 'record_id', 'routes']}, ensure_ascii=False, indent=2)}

SELECTION
{json.dumps(selection, ensure_ascii=False, indent=2)}

FIGURE
{json.dumps({key: figure[key] for key in ['figure_index', 'page_no', 'caption', 'vlm_descriptions', 'pixel_width', 'pixel_height']}, ensure_ascii=False, indent=2)}
"""


def run_single(
    *,
    role: str,
    model_id: str,
    prompt: str,
    schema: dict[str, Any],
    image: Path,
    output_dir: Path,
    model: str,
    timeout: int,
    force: bool,
) -> dict[str, Any]:
    target = output_dir / "runs" / role / model_id
    selected = target / "selected_response.json"
    if selected.exists() and not force:
        return read_json(selected)
    attempt = 1 + max(
        [int(path.name.removeprefix("attempt_")) for path in target.glob("attempt_[0-9][0-9]")],
        default=0,
    )
    attempt_dir = target / f"attempt_{attempt:02d}"
    metadata = run_codex_attempt(
        prompt=prompt,
        schema=schema,
        images=[image],
        output_dir=attempt_dir,
        model=model,
        timeout=timeout,
    )
    if metadata["status"] != "ok":
        raise RuntimeError(f"{role} failed for {model_id}: {metadata['error']}")
    response = read_json(attempt_dir / "response.json")
    shutil.copy2(attempt_dir / "response.json", selected)
    write_json(
        target / "run_summary.json",
        {"role": role, "model_id": model_id, "status": "ok", "selected_attempt": attempt},
    )
    return response


def validate_selector(case: dict[str, Any], response: dict[str, Any]) -> None:
    if response["model_id"] != case["model_id"]:
        raise ValueError("Selector model mismatch")
    route_ids = {route["route_id"] for route in case["routes"]}
    if not set(response["route_ids_supported"]).issubset(route_ids):
        raise ValueError("Selector returned unknown route IDs")
    indexes = {figure["figure_index"] for figure in case["figure_candidates"]}
    if response["decision"] == "select_figure":
        if response["figure_index"] not in indexes or not response["route_ids_supported"]:
            raise ValueError("Invalid selected figure or empty route support")
    elif response["figure_index"] is not None:
        raise ValueError("No-suitable selector must return null figure_index")


def validate_cropper(case: dict[str, Any], selection: dict[str, Any], response: dict[str, Any]) -> None:
    if response["model_id"] != case["model_id"] or not valid_crop_box(response["crop_box"]):
        raise ValueError("Invalid cropper model or bbox")
    allowed = set(selection["route_ids_supported"])
    supported = set(response["route_ids_supported"])
    if not supported or not supported.issubset(allowed):
        raise ValueError("Cropper route support must be a nonempty subset of selector support")


def run_pipeline(
    *, output_dir: Path, model: str, timeout: int, force: bool
) -> list[dict[str, Any]]:
    cases = read_json(output_dir / "replacement_selection_manifest.json")
    preview_manifest = []
    results = []
    for case in cases:
        contact_sheet = ROOT / case["contact_sheet_path"]
        selection = run_single(
            role="replacement_selector",
            model_id=case["model_id"],
            prompt=selector_prompt(case),
            schema=SELECTOR_SCHEMA,
            image=contact_sheet,
            output_dir=output_dir,
            model=model,
            timeout=timeout,
            force=force,
        )
        validate_selector(case, selection)
        result = {"model_id": case["model_id"], "selection": selection, "crop": None}
        if selection["decision"] == "select_figure":
            figure = next(
                item
                for item in case["figure_candidates"]
                if item["figure_index"] == selection["figure_index"]
            )
            crop = run_single(
                role="replacement_cropper",
                model_id=case["model_id"],
                prompt=cropper_prompt(case, selection, figure),
                schema=CROPPER_SCHEMA,
                image=Path(figure["local_image_path"]),
                output_dir=output_dir,
                model=model,
                timeout=timeout,
                force=force,
            )
            validate_cropper(case, selection, crop)
            panel = render_crop_panel(
                source=Path(figure["local_image_path"]),
                crop=crop["crop_box"],
                width=figure["pixel_width"],
                height=figure["pixel_height"],
                panel=output_dir / "review_panels/replacements" / f"{case['model_id']}.jpg",
                exact_crop=output_dir / "review_panels/replacement_exact_crops" / f"{case['model_id']}.png",
            )
            preview_manifest.append(
                {
                    **{key: case[key] for key in ["model_id", "model_name", "record_id", "paper_title", "routes"]},
                    "figure_index": figure["figure_index"],
                    "figure_caption": figure["caption"],
                    "current_crop_box": crop["crop_box"],
                    "claimed_route_ids_supported": crop["route_ids_supported"],
                    "replacement_source": figure,
                    "replacement_selection": selection,
                    "replacement_crop": crop,
                    **panel,
                }
            )
            result["crop"] = crop
            result["figure"] = figure
        results.append(result)
    write_json(output_dir / "replacement_preview_manifest.json", preview_manifest)
    write_json(output_dir / "replacement_pipeline_results.json", results)
    return results


def finalize(output_dir: Path) -> dict[str, Any]:
    results = read_json(output_dir / "replacement_pipeline_results.json")
    previews = role_review_index(output_dir, "replacement_preview_validator")
    round2_previews = role_review_index(output_dir, "replacement_preview_validator_round2")
    previews.update(round2_previews)
    input_role_reviews = role_review_index(output_dir, "replacement_input_role_validator")
    round2_manifest = {
        item["model_id"]: item
        for item in (
            read_json(output_dir / "replacement_preview_round2_manifest.json")
            if (output_dir / "replacement_preview_round2_manifest.json").exists()
            else []
        )
    }
    final = []
    for item in results:
        selection = item["selection"]
        if selection["decision"] == "no_suitable_figure":
            status = "no_suitable_figure"
        else:
            preview = previews.get(item["model_id"])
            input_role = input_role_reviews.get(item["model_id"])
            shared_routes = (
                set(preview["route_ids_supported"]) & set(input_role["route_ids_supported"])
                if preview and input_role
                else set()
            )
            if (
                preview
                and preview["decision"] == "pass"
                and input_role
                and input_role["decision"] == "pass"
                and shared_routes
            ):
                status = "validated_replacement_crop"
            elif input_role and input_role["decision"] == "reject":
                status = "no_suitable_figure"
            else:
                status = "unresolved_replacement_crop"
        final_crop_box = None
        if status == "validated_replacement_crop":
            final_crop_box = (
                round2_manifest[item["model_id"]]["current_crop_box"]
                if item["model_id"] in round2_manifest
                else item["crop"]["crop_box"]
            )
        final.append(
            {
                **item,
                "status": status,
                "final_crop_box": final_crop_box,
                "replacement_preview_validation": previews.get(item["model_id"]),
                "replacement_input_role_validation": input_role_reviews.get(item["model_id"]),
            }
        )
    write_json(output_dir / "replacement_validation_results.json", final)
    report = {
        "models": len(final),
        "validated_replacement_crops": sum(item["status"] == "validated_replacement_crop" for item in final),
        "no_suitable_figure": sum(item["status"] == "no_suitable_figure" for item in final),
        "unresolved": sum(item["status"] == "unresolved_replacement_crop" for item in final),
    }
    write_json(output_dir / "replacement_validation_report.json", report)
    return report


def prepare_round2(output_dir: Path) -> list[dict[str, Any]]:
    manifest = {
        item["model_id"]: item
        for item in read_json(output_dir / "replacement_preview_manifest.json")
    }
    reviews = role_review_index(output_dir, "replacement_preview_validator")
    round2 = []
    for model_id, review in reviews.items():
        if review["decision"] != "adjust" or not valid_crop_box(review["proposed_crop_box"]):
            continue
        item = dict(manifest[model_id])
        source = Path(item["replacement_source"]["local_image_path"])
        crop = review["proposed_crop_box"]
        rendered = render_crop_panel(
            source=source,
            crop=crop,
            width=item["replacement_source"]["pixel_width"],
            height=item["replacement_source"]["pixel_height"],
            panel=output_dir / "review_panels/replacements_round2" / f"{model_id}.jpg",
            exact_crop=output_dir / "review_panels/replacement_round2_exact_crops" / f"{model_id}.png",
        )
        item.update(rendered)
        item["current_crop_box"] = crop
        item["round1_preview_validation"] = review
        round2.append(item)
    write_json(output_dir / "replacement_preview_round2_manifest.json", round2)
    final_manifest = dict(manifest)
    final_manifest.update({item["model_id"]: item for item in round2})
    write_json(
        output_dir / "replacement_final_manifest.json",
        [final_manifest[model_id] for model_id in sorted(final_manifest)],
    )
    return round2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "run", "round2", "finalize"])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--profile-manifest",
        type=Path,
        default=(
            ROOT
            / "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
            / "canonical_docling_profile_manifest.csv"
        ),
    )
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=2700)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(
            output_dir=args.output_dir,
            profile_manifest=args.profile_manifest,
            source_root=args.source_root,
        )
    elif args.command == "run":
        run_pipeline(
            output_dir=args.output_dir,
            model=args.model,
            timeout=args.timeout,
            force=args.force,
        )
    elif args.command == "round2":
        print(json.dumps({"round2_models": len(prepare_round2(args.output_dir))}))
    else:
        print(json.dumps(finalize(args.output_dir), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
