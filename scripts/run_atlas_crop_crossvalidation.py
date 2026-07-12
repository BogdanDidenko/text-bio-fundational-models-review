#!/usr/bin/env python3
"""Run blind, logged Codex crop-validation passes for every atlas model."""

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


ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "data/input_representation_atlas_crop_crossvalidation_2026-07-12"
MANIFEST_PATH = RUN_ROOT / "validation_manifest.json"
MODEL = "gpt-5.4-mini"


BBOX_SCHEMA: dict[str, Any] = {
    "type": ["object", "null"],
    "additionalProperties": False,
    "required": ["x", "y", "width", "height"],
    "properties": {
        "x": {"type": "number", "minimum": 0, "maximum": 1},
        "y": {"type": "number", "minimum": 0, "maximum": 1},
        "width": {"type": "number", "minimum": 0.03, "maximum": 1},
        "height": {"type": "number", "minimum": 0.03, "maximum": 1},
    },
}

VALIDATION_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["reviewer_role", "reviews"],
    "properties": {
        "reviewer_role": {"type": "string"},
        "reviews": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "model_id", "decision", "route_ids_supported", "representative_scope",
                    "required_input_elements_visible", "missing_or_irrelevant_elements",
                    "proposed_figure_index", "proposed_crop_box", "rationale", "confidence",
                ],
                "properties": {
                    "model_id": {"type": "string"},
                    "decision": {
                        "type": "string",
                        "enum": [
                            "accept_as_is", "adjust_crop", "replace_figure",
                            "confirm_no_suitable_figure", "select_figure",
                        ],
                    },
                    "route_ids_supported": {"type": "array", "items": {"type": "string"}},
                    "representative_scope": {
                        "type": "string",
                        "enum": ["core_route", "single_route", "multiple_routes", "none"],
                    },
                    "required_input_elements_visible": {
                        "type": "array", "items": {"type": "string"}
                    },
                    "missing_or_irrelevant_elements": {
                        "type": "array", "items": {"type": "string"}
                    },
                    "proposed_figure_index": {"type": ["integer", "null"]},
                    "proposed_crop_box": BBOX_SCHEMA,
                    "rationale": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                },
            },
        },
    },
}


REVIEWER_PROMPTS = {
    "validator_a": """You are the sufficiency reviewer. Judge whether the exact rendered crop contains enough visible evidence to understand what enters this specific model. Require a concrete source object, its model-visible representation, or the immediate model-facing interface. Give priority to route-specific correctness and readable labels.""",
    "validator_b": """You are the relevance and minimality reviewer. Actively look for misleading crops: output-only panels, benchmark/results plots, generic architecture without the stated input, unrelated training data, or rectangles that omit the necessary labels/arrows. Require the smallest coherent region that still explains a grounded model input route.""",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_codex(
    *, name: str, reviewer: str, prompt: str, images: list[Path], output_dir: Path
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    schema_path = output_dir / "output_schema.json"
    prompt_path = output_dir / "prompt.txt"
    response_path = output_dir / "response.json"
    stdout_path = output_dir / "stdout.jsonl"
    stderr_path = output_dir / "stderr.log"
    metadata_path = output_dir / "metadata.json"
    write_json(schema_path, VALIDATION_SCHEMA)
    prompt_path.write_text(prompt.rstrip() + "\n", encoding="utf-8")
    command = [
        "codex", "exec", "--model", MODEL, "--cd", str(ROOT), "--sandbox", "read-only",
        "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
        "--output-last-message", str(response_path), "--output-schema", str(schema_path),
    ]
    for image in images:
        command.extend(["--image", str(image)])
    command.append("-")
    started = datetime.now(timezone.utc)
    started_clock = time.monotonic()
    status = "ok"
    returncode: int | None = None
    error = ""
    try:
        result = subprocess.run(
            command, input=prompt, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=2700, cwd=ROOT, env={**os.environ, "NO_COLOR": "1"},
        )
        returncode = result.returncode
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")
        if result.returncode:
            status = "error_returncode"
            error = result.stderr[-4000:]
        elif not response_path.exists():
            status = "missing_response"
            error = "Codex exited without the required response file."
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        error = "Timed out after 2700 seconds"
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        stderr_path.write_text(exc.stderr or "", encoding="utf-8")
    except Exception as exc:  # pragma: no cover - operational logging
        status = "exception"
        error = repr(exc)
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(error + "\n", encoding="utf-8")
    metadata = {
        "name": name,
        "reviewer": reviewer,
        "status": status,
        "model": MODEL,
        "command": command,
        "images": [str(path.relative_to(ROOT)) for path in images],
        "started_at": started.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.monotonic() - started_clock, 3),
        "returncode": returncode,
        "error": error,
    }
    write_json(metadata_path, metadata)
    return metadata


def prompt_for_batch(reviewer: str, batch: list[dict[str, Any]]) -> str:
    records = []
    for image_index, item in enumerate(batch, start=1):
        records.append(
            {
                "image_attachment_index": image_index,
                "model_id": item["model_id"],
                "model_name": item["model_name"],
                "paper_title": item["paper_title"],
                "current_status": item["current_status"],
                "current_figure_index": item["current_figure_index"],
                "current_crop_box": item["current_crop_box"],
                "panel_layout": item["panel_layout"],
                "figure_order": item.get("figure_order"),
                "routes": item["routes"],
                "figure_candidates": item["figure_candidates"],
            }
        )
    return f"""{REVIEWER_PROMPTS[reviewer]}

This is a blind cross-validation pass. Do not inspect or infer the other reviewer's decisions.

Acceptance rule:
- A crop passes only if its RIGHT-HAND exact crop visibly and readably depicts a source object, transformation, model-visible carrier, or immediate insertion/fusion interface for at least one grounded `actual_model_input` route of this exact model.
- Output-only panels, downstream performance, generic results, decorative elements, and unrelated training/data summaries are not valid input-representation evidence.
- A general architecture panel is insufficient unless the relevant input and interface are visible in the crop.
- Prefer a minimal coherent crop, but retain labels/arrows needed to interpret the input path.
- If the current figure is right but the rectangle is wrong, choose `adjust_crop` and return normalized coordinates relative to the FULL SOURCE FIGURE shown on the left.
- If another candidate figure is required, choose `replace_figure` and return its figure index. Do not invent coordinates for an unseen replacement figure.
- For a current `no_suitable_figure` record, the attachment is a contact sheet ordered by `figure_order`. Choose `select_figure` only when a candidate visibly appears to contain relevant input evidence; otherwise confirm the absence.
- The representative crop does not need to cover every route of a multi-route model. State exactly which route IDs it supports.
- Ensure proposed x+width <= 1 and y+height <= 1.
- Do not claim hidden chain-of-thought. Return concise, visible-evidence-based judgments only.

Records:
{json.dumps(records, ensure_ascii=False, indent=2)}

Return exactly one review for every listed model_id and no others."""


def make_batches(manifest: list[dict[str, Any]], crop_batch_size: int) -> list[list[dict[str, Any]]]:
    cropped = [item for item in manifest if item["current_status"] == "cropped_source_figure"]
    no_figure = [item for item in manifest if item["current_status"] == "no_suitable_figure"]
    batches = [
        cropped[index:index + crop_batch_size]
        for index in range(0, len(cropped), crop_batch_size)
    ]
    batches.extend([[item] for item in no_figure])
    return batches


def run_validation(reviewers: list[str], batch_size: int, max_workers: int) -> int:
    manifest = read_json(MANIFEST_PATH)
    batches = make_batches(manifest, batch_size)
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for reviewer in reviewers:
            root = RUN_ROOT / "subagents" / reviewer
            for index, batch in enumerate(batches):
                name = f"batch_{index:02d}"
                images = [ROOT / item["panel_path"] for item in batch]
                futures.append(
                    pool.submit(
                        run_codex,
                        name=name,
                        reviewer=reviewer,
                        prompt=prompt_for_batch(reviewer, batch),
                        images=images,
                        output_dir=root / name,
                    )
                )
        results = [future.result() for future in as_completed(futures)]
    by_reviewer: dict[str, list[dict[str, Any]]] = {reviewer: [] for reviewer in reviewers}
    for result in results:
        by_reviewer[result["reviewer"]].append(result)
    for reviewer, reviewer_results in by_reviewer.items():
        write_json(
            RUN_ROOT / "subagents" / reviewer / "run_summary.json",
            {"results": sorted(reviewer_results, key=lambda item: item["name"])},
        )
    return 0 if all(result["status"] == "ok" for result in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("validate-a", "validate-b", "validate-both"))
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--max-workers", type=int, default=10)
    args = parser.parse_args()
    reviewers = {
        "validate-a": ["validator_a"],
        "validate-b": ["validator_b"],
        "validate-both": ["validator_a", "validator_b"],
    }[args.mode]
    return run_validation(reviewers, args.batch_size, args.max_workers)


if __name__ == "__main__":
    raise SystemExit(main())
