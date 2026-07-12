#!/usr/bin/env python3
"""Adjudicate every non-pass from the adversarial input-role integrity gate."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prepare_atlas_crop_crossvalidation import (
    OUTPUT_ROOT as RUN_ROOT,
    ROOT,
    make_no_figure_panel,
    read_json,
    write_json,
)


MODEL = "gpt-5.4"


SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["adjudication"],
    "properties": {
        "adjudication": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "model_id", "decision", "final_figure_index", "final_crop_box",
                "route_ids_supported", "depicted_input", "rationale", "confidence",
            ],
            "properties": {
                "model_id": {"type": "string"},
                "decision": {
                    "type": "string",
                    "enum": ["accept_current", "adjust_current", "replace_figure", "no_suitable_figure"],
                },
                "final_figure_index": {"type": ["integer", "null"]},
                "final_crop_box": {
                    "type": ["object", "null"],
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
                "depicted_input": {"type": "string"},
                "rationale": {"type": "string"},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            },
        }
    },
}


def load_role_reviews(role: str) -> dict[str, dict[str, Any]]:
    result = {}
    for path in (RUN_ROOT / "subagents" / role).glob("batch_*/response.json"):
        for review in read_json(path)["reviews"]:
            result[review["model_id"]] = review
    return result


def figure_manifests() -> dict[str, list[dict[str, Any]]]:
    result = {}
    root = ROOT / "data/docling_include_vlm_52_2026-07-10_nolimits/figures"
    for path in root.glob("*/figures_manifest.json"):
        figures = read_json(path)
        if figures:
            result[figures[0]["candidate_id"]] = figures
    return result


def prepare_manifest(
    *, review_role: str, preview_manifest_name: str, preview_review_role: str | None,
    candidate_folder: str,
) -> list[dict[str, Any]]:
    role_reviews = load_role_reviews(review_role)
    preview_reviews = load_role_reviews(preview_review_role) if preview_review_role else {}
    final_preview = {
        item["model_id"]: item for item in read_json(RUN_ROOT / preview_manifest_name)
    }
    validation = {
        item["model_id"]: item for item in read_json(RUN_ROOT / "validation_manifest.json")
    }
    figures = figure_manifests()
    output = []
    for model_id, review in role_reviews.items():
        preview_review = preview_reviews.get(model_id)
        if review["decision"] == "pass" and (
            preview_review is None or preview_review["decision"] == "pass"
        ):
            continue
        preview = final_preview[model_id]
        source = validation[model_id]
        candidate = make_no_figure_panel(
            model_id,
            figures[source["record_id"]],
            RUN_ROOT / "review_panels" / candidate_folder / f"{model_id}.jpg",
        )
        output.append(
            {
                **preview,
                "role_integrity_review": review,
                "rendered_preview_review": preview_review,
                "figure_candidates": source["figure_candidates"],
                "candidate_panel_path": candidate["panel_path"],
                "candidate_figure_order": candidate["figure_order"],
            }
        )
    manifest_name = (
        "input_role_adjudication_manifest.json"
        if review_role == "input_role_integrity_validator"
        else "post_role_scope_adjudication_manifest.json"
    )
    write_json(RUN_ROOT / manifest_name, output)
    return output


def prompt(item: dict[str, Any]) -> str:
    record = {
        key: item[key]
        for key in (
            "model_id", "model_name", "paper_title", "final_figure_index", "final_crop_box",
            "routes", "role_integrity_review", "rendered_preview_review",
            "figure_candidates", "candidate_figure_order",
        )
    }
    return f"""You are the final scope-aware adjudicator for a biomedical input-representation atlas.

Image 1: full current figure with red rectangle on the LEFT and exact current crop on the RIGHT.
Image 2: all source-paper figures ordered by `candidate_figure_order`.

Resolve the adversarial role-integrity review using these precise atlas rules:
- A crop is valid when it visibly shows the source object, serialized/tokenized/embedded representation, transformation, or immediate interface for at least one listed actual_model_input route.
- A model box is NOT mandatory when the figure clearly depicts the route-specific input object or representation that the paper states is supplied to the model.
- A shared architecture figure may validly illustrate multiple named variants from the same paper when their route uses the same depicted input mechanism; the exact variant name need not appear in the crop.
- Training or fine-tuning input is valid when the listed route lifecycle is training/fine_tuning. Do not impose inference-only scope.
- A panel showing both input and output may be cropped to the input portion if the input is clearly identifiable.
- Invalid: target-model output passed to a grader/scorer, prompts to an evaluator rather than the target model, another model consuming target-model embeddings, performance/post-hoc plots without an input path, or an unrelated model/route.
- Use `adjust_current` when the same full figure contains a better region; `replace_figure` when another source figure is visibly better; `no_suitable_figure` when no figure is defensible.
- Return exact supported route IDs. Ensure x+width <= 1 and y+height <= 1.
- Do not claim hidden chain-of-thought.

Record:
{json.dumps(record, ensure_ascii=False, indent=2)}"""


def run_one(item: dict[str, Any], output_role: str) -> dict[str, Any]:
    model_id = item["model_id"]
    output = RUN_ROOT / "subagents" / output_role / model_id
    output.mkdir(parents=True, exist_ok=True)
    schema = output / "output_schema.json"
    prompt_path = output / "prompt.txt"
    response = output / "response.json"
    stdout = output / "stdout.jsonl"
    stderr = output / "stderr.log"
    metadata_path = output / "metadata.json"
    write_json(schema, SCHEMA)
    prompt_value = prompt(item)
    prompt_path.write_text(prompt_value + "\n", encoding="utf-8")
    images = [ROOT / item["panel_path"], ROOT / item["candidate_panel_path"]]
    command = [
        "codex", "exec", "--model", MODEL, "--cd", str(ROOT), "--sandbox", "read-only",
        "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
        "--output-last-message", str(response), "--output-schema", str(schema),
    ]
    for image in images:
        command.extend(["--image", str(image)])
    command.append("-")
    started = datetime.now(timezone.utc)
    clock = time.monotonic()
    status = "ok"
    error = ""
    returncode: int | None = None
    try:
        result = subprocess.run(
            command, input=prompt_value, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=2700, cwd=ROOT, env={**os.environ, "NO_COLOR": "1"},
        )
        returncode = result.returncode
        stdout.write_text(result.stdout, encoding="utf-8")
        stderr.write_text(result.stderr, encoding="utf-8")
        if returncode:
            status = "error_returncode"
            error = result.stderr[-4000:]
        elif not response.exists():
            status = "missing_response"
            error = "Missing input-role adjudication response"
    except Exception as exc:  # pragma: no cover
        status = "exception"
        error = repr(exc)
        stdout.write_text("", encoding="utf-8")
        stderr.write_text(error + "\n", encoding="utf-8")
    metadata = {
        "model_id": model_id, "status": status, "model": MODEL,
        "images": [str(path.relative_to(ROOT)) for path in images], "command": command,
        "started_at": started.isoformat(), "finished_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.monotonic() - clock, 3), "returncode": returncode,
        "error": error,
    }
    write_json(metadata_path, metadata)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-role", default="input_role_integrity_validator")
    parser.add_argument("--preview-manifest", default="final_preview_validation_manifest.json")
    parser.add_argument("--preview-review-role")
    parser.add_argument("--output-role", default="input_role_adjudicator")
    parser.add_argument("--candidate-folder", default="input_role_adjudication_candidates")
    args = parser.parse_args()
    manifest = prepare_manifest(
        review_role=args.review_role,
        preview_manifest_name=args.preview_manifest,
        preview_review_role=args.preview_review_role,
        candidate_folder=args.candidate_folder,
    )
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = [future.result() for future in as_completed([pool.submit(run_one, item, args.output_role) for item in manifest])]
    write_json(
        RUN_ROOT / "subagents" / args.output_role / "run_summary.json",
        {"results": sorted(results, key=lambda item: item["model_id"])},
    )
    print(json.dumps({"models": len(results), "ok": sum(item["status"] == "ok" for item in results)}))
    return 0 if all(item["status"] == "ok" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
