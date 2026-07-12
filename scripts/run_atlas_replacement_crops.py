#!/usr/bin/env python3
"""Crop adjudicator-selected replacement figures at full resolution."""

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
FIGURE_ROOT = ROOT / "data/docling_include_vlm_52_2026-07-10_nolimits/figures"
MODEL = "gpt-5.4"


SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["crop"],
    "properties": {
        "crop": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "model_id", "figure_index", "crop_box", "route_ids_supported",
                "visible_input_object", "visible_model_interface", "panel_label",
                "rationale", "confidence",
            ],
            "properties": {
                "model_id": {"type": "string"},
                "figure_index": {"type": "integer"},
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
                "rationale": {"type": "string"},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            },
        }
    },
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def manifests() -> dict[str, dict[int, dict[str, Any]]]:
    result = {}
    for path in FIGURE_ROOT.glob("*/figures_manifest.json"):
        figures = read_json(path)
        if figures:
            result[figures[0]["candidate_id"]] = {
                int(figure["figure_index"]): figure for figure in figures
            }
    return result


def adjudications(role: str) -> dict[str, dict[str, Any]]:
    result = {}
    for path in (RUN_ROOT / "subagents" / role).glob("*/response.json"):
        value = read_json(path)["adjudication"]
        result[value["model_id"]] = value
    return result


def prompt(item: dict[str, Any], decision: dict[str, Any], figure: dict[str, Any]) -> str:
    descriptions = [
        annotation.get("text")
        for annotation in figure.get("annotations") or []
        if annotation.get("text")
    ]
    return f"""You are cropping a full-resolution original-paper figure selected by a prior visual adjudicator. Identify the smallest coherent rectangle that visibly and readably shows the model input route named below.

Retain the source object, transformation, labels/arrows, and immediate model-facing interface needed for interpretation. Exclude outputs, downstream results, performance panels, and unrelated branches. Coordinates are normalized to the full attached figure. Ensure x+width <= 1 and y+height <= 1. Do not infer content that is not visible and do not claim hidden chain-of-thought.

Model and route record:
{json.dumps({
    'model_id': item['model_id'],
    'model_name': item['model_name'],
    'paper_title': item['paper_title'],
    'selected_figure_index': decision['final_figure_index'],
    'adjudicator_route_ids_supported': decision['route_ids_supported'],
    'adjudicator_rationale': decision['rationale'],
    'routes': item['routes'],
    'figure_caption': figure.get('caption') or '',
    'figure_descriptions': descriptions,
}, ensure_ascii=False, indent=2)}"""


def run_one(
    item: dict[str, Any], decision: dict[str, Any], figure: dict[str, Any], output_role: str
) -> dict[str, Any]:
    model_id = item["model_id"]
    output_dir = RUN_ROOT / "subagents" / output_role / model_id
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "schema": output_dir / "output_schema.json",
        "prompt": output_dir / "prompt.txt",
        "response": output_dir / "response.json",
        "stdout": output_dir / "stdout.jsonl",
        "stderr": output_dir / "stderr.log",
        "metadata": output_dir / "metadata.json",
    }
    write_json(paths["schema"], SCHEMA)
    prompt_value = prompt(item, decision, figure)
    paths["prompt"].write_text(prompt_value + "\n", encoding="utf-8")
    image = ROOT / figure["image_path"]
    command = [
        "codex", "exec", "--model", MODEL, "--cd", str(ROOT), "--sandbox", "read-only",
        "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
        "--output-last-message", str(paths["response"]), "--output-schema", str(paths["schema"]),
        "--image", str(image), "-",
    ]
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
        paths["stdout"].write_text(result.stdout, encoding="utf-8")
        paths["stderr"].write_text(result.stderr, encoding="utf-8")
        if returncode:
            status = "error_returncode"
            error = result.stderr[-4000:]
        elif not paths["response"].exists():
            status = "missing_response"
            error = "Missing replacement crop response"
    except Exception as exc:  # pragma: no cover
        status = "exception"
        error = repr(exc)
        paths["stdout"].write_text("", encoding="utf-8")
        paths["stderr"].write_text(error + "\n", encoding="utf-8")
    metadata = {
        "model_id": model_id, "status": status, "model": MODEL,
        "image": str(image.relative_to(ROOT)), "command": command,
        "started_at": started.isoformat(), "finished_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.monotonic() - clock, 3), "returncode": returncode,
        "error": error,
    }
    write_json(paths["metadata"], metadata)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--decision-role",
        choices=("adjudicator", "input_role_adjudicator", "post_role_scope_adjudicator"),
        default="adjudicator",
    )
    args = parser.parse_args()
    if args.decision_role == "adjudicator":
        manifest_path = RUN_ROOT / "adjudication_manifest.json"
        output_role = "replacement_cropper"
    elif args.decision_role == "input_role_adjudicator":
        manifest_path = RUN_ROOT / "input_role_adjudication_manifest.json"
        output_role = "input_role_replacement_cropper"
    else:
        manifest_path = RUN_ROOT / "post_role_scope_adjudication_manifest.json"
        output_role = "post_role_scope_replacement_cropper"
    manifest = {item["model_id"]: item for item in read_json(manifest_path)}
    decisions = {
        model_id: decision
        for model_id, decision in adjudications(args.decision_role).items()
        if decision["decision"] == "replace_figure"
    }
    figure_map = manifests()
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = [
            future.result()
            for future in as_completed([
                pool.submit(
                    run_one,
                    manifest[model_id],
                    decision,
                    figure_map[manifest[model_id]["record_id"]][int(decision["final_figure_index"])],
                    output_role,
                )
                for model_id, decision in decisions.items()
            ])
        ]
    write_json(
        RUN_ROOT / "subagents" / output_role / "run_summary.json",
        {"results": sorted(results, key=lambda item: item["model_id"])},
    )
    print(json.dumps({"models": len(results), "ok": sum(item["status"] == "ok" for item in results)}))
    return 0 if all(item["status"] == "ok" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
