#!/usr/bin/env python3
"""Run a stronger-model visual adjudication for every contested atlas crop."""

from __future__ import annotations

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
                "route_ids_supported", "visible_input_evidence", "excluded_content",
                "rationale", "confidence",
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
                "visible_input_evidence": {"type": "array", "items": {"type": "string"}},
                "excluded_content": {"type": "array", "items": {"type": "string"}},
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


def prompt(item: dict[str, Any]) -> str:
    record = {
        key: item[key]
        for key in (
            "model_id", "model_name", "paper_title", "current_status",
            "current_figure_index", "current_crop_box", "routes", "figure_candidates",
            "candidate_figure_order", "review_a", "review_b",
        )
    }
    return f"""You are the blinded adjudicator for a biomedical input-representation atlas. Resolve two independent crop reviews using visible evidence, not majority voting.

Image 1 is the current review panel. For an existing crop, its LEFT side is the full source figure with a red rectangle and its RIGHT side is the exact rendered crop. For a no-figure baseline, it is the original contact sheet.
Image 2 is a contact sheet of all source-paper figure candidates in `candidate_figure_order`, left-to-right and top-to-bottom.

Decision rules:
- `accept_current`: the exact right crop clearly and readably shows a source object, transformation, model-visible carrier, or immediate model-facing interface for at least one listed `actual_model_input` route.
- `adjust_current`: the current figure is correct but the rectangle must change. Return final normalized coordinates relative to the full original figure.
- `replace_figure`: another visible candidate is better. Return its figure index and null crop; a separate high-resolution crop pass will follow.
- `no_suitable_figure`: no source figure visibly supports the model input route. Return null figure and crop. Do not substitute outputs, performance plots, generic data summaries, or unrelated training diagrams.
- A crop may represent one core route rather than every route, but `route_ids_supported` must identify exactly what it supports.
- Preserve labels/arrows necessary to interpret the input path while excluding unrelated outputs/results.
- Ensure x+width <= 1 and y+height <= 1.
- Do not claim hidden chain-of-thought. Give concise visible-evidence rationale.

Record and blind reviews:
{json.dumps(record, ensure_ascii=False, indent=2)}"""


def run_one(item: dict[str, Any]) -> dict[str, Any]:
    model_id = item["model_id"]
    output_dir = RUN_ROOT / "subagents/adjudicator" / model_id
    output_dir.mkdir(parents=True, exist_ok=True)
    schema_path = output_dir / "output_schema.json"
    prompt_path = output_dir / "prompt.txt"
    response_path = output_dir / "response.json"
    stdout_path = output_dir / "stdout.jsonl"
    stderr_path = output_dir / "stderr.log"
    metadata_path = output_dir / "metadata.json"
    write_json(schema_path, SCHEMA)
    prompt_value = prompt(item)
    prompt_path.write_text(prompt_value + "\n", encoding="utf-8")
    images = [ROOT / item["panel_path"], ROOT / item["candidate_panel_path"]]
    command = [
        "codex", "exec", "--model", MODEL, "--cd", str(ROOT), "--sandbox", "read-only",
        "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
        "--output-last-message", str(response_path), "--output-schema", str(schema_path),
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
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")
        if returncode:
            status = "error_returncode"
            error = result.stderr[-4000:]
        elif not response_path.exists():
            status = "missing_response"
            error = "Missing adjudication response"
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        error = "Timed out after 2700 seconds"
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        stderr_path.write_text(exc.stderr or "", encoding="utf-8")
    except Exception as exc:  # pragma: no cover
        status = "exception"
        error = repr(exc)
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(error + "\n", encoding="utf-8")
    metadata = {
        "model_id": model_id,
        "status": status,
        "model": MODEL,
        "images": [str(path.relative_to(ROOT)) for path in images],
        "command": command,
        "started_at": started.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.monotonic() - clock, 3),
        "returncode": returncode,
        "error": error,
    }
    write_json(metadata_path, metadata)
    return metadata


def main() -> int:
    manifest = read_json(RUN_ROOT / "adjudication_manifest.json")
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = [future.result() for future in as_completed([pool.submit(run_one, item) for item in manifest])]
    write_json(
        RUN_ROOT / "subagents/adjudicator/run_summary.json",
        {"results": sorted(results, key=lambda item: item["model_id"])},
    )
    print(json.dumps({"models": len(results), "status_counts": _counts(results)}, ensure_ascii=False))
    return 0 if all(item["status"] == "ok" for item in results) else 1


def _counts(results: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    return counts


if __name__ == "__main__":
    raise SystemExit(main())
