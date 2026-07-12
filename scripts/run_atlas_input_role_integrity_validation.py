#!/usr/bin/env python3
"""Verify that each crop depicts input to the exact target model, not a neighboring role."""

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
MODEL = "gpt-5.4"


SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["reviews"],
    "properties": {
        "reviews": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "model_id", "decision", "depicted_subject", "target_model_input_match",
                    "failure_mode", "route_ids_supported", "proposed_crop_box",
                    "rationale", "confidence",
                ],
                "properties": {
                    "model_id": {"type": "string"},
                    "decision": {"type": "string", "enum": ["pass", "adjust", "reject"]},
                    "depicted_subject": {"type": "string"},
                    "target_model_input_match": {"type": "boolean"},
                    "failure_mode": {
                        "type": "string",
                        "enum": [
                            "none", "other_model", "downstream_consumer", "model_output",
                            "grader_or_scorer", "performance_or_analysis", "generic_data_summary",
                            "wrong_lifecycle", "wrong_model_variant", "crop_omits_interface", "other",
                        ],
                    },
                    "route_ids_supported": {"type": "array", "items": {"type": "string"}},
                    "proposed_crop_box": {
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
                    "rationale": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                },
            },
        }
    },
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prompt(batch: list[dict[str, Any]]) -> str:
    records = []
    for index, item in enumerate(batch, start=1):
        records.append(
            {
                "image_attachment_index": index,
                "model_id": item["model_id"],
                "model_name": item["model_name"],
                "paper_title": item["paper_title"],
                "final_figure_index": item["final_figure_index"],
                "final_crop_box": item["final_crop_box"],
                "routes": item["routes"],
            }
        )
    return f"""You are an adversarial input-role integrity reviewer. Inspect the exact final crop on the RIGHT of each attached panel and determine what entity and role it actually depicts.

The crop passes only when it visibly shows input to the exact named target model for at least one listed actual_model_input route. Reject these correlated error modes even when the image is scientifically related:
- embeddings or outputs produced by the target model and consumed by a different downstream architecture;
- the target model's generated output being evaluated by a grader/scorer;
- a prompt or input to a grader, reward model, or evaluator rather than to the target model;
- performance plots, output examples, post-hoc analyses, or generic dataset summaries;
- an input route for another model variant or lifecycle phase;
- a general architecture crop where the stated source object and immediate target-model interface are absent.

Use `adjust` only if the full source figure on the LEFT visibly contains a correct region for the same target model and route; provide normalized coordinates. Otherwise reject. Ensure x+width <= 1 and y+height <= 1. Do not rely on earlier reviewer decisions and do not claim hidden chain-of-thought.

Records:
{json.dumps(records, ensure_ascii=False, indent=2)}

Return exactly one review per model_id."""


def run_batch(index: int, batch: list[dict[str, Any]], output_role: str) -> dict[str, Any]:
    name = f"batch_{index:02d}"
    output = RUN_ROOT / "subagents" / output_role / name
    output.mkdir(parents=True, exist_ok=True)
    schema = output / "output_schema.json"
    prompt_path = output / "prompt.txt"
    response = output / "response.json"
    stdout = output / "stdout.jsonl"
    stderr = output / "stderr.log"
    metadata_path = output / "metadata.json"
    write_json(schema, SCHEMA)
    prompt_value = prompt(batch)
    prompt_path.write_text(prompt_value + "\n", encoding="utf-8")
    images = [ROOT / item["panel_path"] for item in batch]
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
            error = "Missing role-integrity response"
    except Exception as exc:  # pragma: no cover
        status = "exception"
        error = repr(exc)
        stdout.write_text("", encoding="utf-8")
        stderr.write_text(error + "\n", encoding="utf-8")
    metadata = {
        "name": name, "status": status, "model": MODEL,
        "images": [str(path.relative_to(ROOT)) for path in images], "command": command,
        "started_at": started.isoformat(), "finished_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.monotonic() - clock, 3), "returncode": returncode,
        "error": error,
    }
    write_json(metadata_path, metadata)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="final_preview_validation_manifest.json")
    parser.add_argument("--output-role", default="input_role_integrity_validator")
    args = parser.parse_args()
    manifest = read_json(RUN_ROOT / args.manifest)
    batches = [manifest[index:index + 4] for index in range(0, len(manifest), 4)]
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = [future.result() for future in as_completed([pool.submit(run_batch, index, batch, args.output_role) for index, batch in enumerate(batches)])]
    write_json(
        RUN_ROOT / "subagents" / args.output_role / "run_summary.json",
        {"results": sorted(results, key=lambda item: item["name"])},
    )
    print(json.dumps({"batches": len(results), "ok": sum(item["status"] == "ok" for item in results)}))
    return 0 if all(item["status"] == "ok" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
