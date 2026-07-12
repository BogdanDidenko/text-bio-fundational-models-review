#!/usr/bin/env python3
"""Blindly validate every exact provisional final crop preview."""

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
MODEL = "gpt-5.4-mini"


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
                    "model_id", "decision", "route_ids_supported", "visible_input_evidence",
                    "problem", "proposed_crop_box", "rationale", "confidence",
                ],
                "properties": {
                    "model_id": {"type": "string"},
                    "decision": {"type": "string", "enum": ["pass", "adjust", "reject"]},
                    "route_ids_supported": {"type": "array", "items": {"type": "string"}},
                    "visible_input_evidence": {"type": "array", "items": {"type": "string"}},
                    "problem": {"type": "string"},
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
                "panel_layout": item["panel_layout"],
                "routes": item["routes"],
            }
        )
    return f"""You are the final blind visual verifier. You have not seen earlier reviews.

Each attachment shows the full original figure with the final red crop rectangle on the LEFT and the exact final rendered crop on the RIGHT.

Pass only when the RIGHT crop visibly and readably shows a source object, transformation, model-visible carrier, or immediate model-facing interface for at least one listed `actual_model_input` route of that exact model. Reject output-only panels, results, generic data summaries, or architecture regions that do not show the stated input. Use `adjust` only when the same figure has a clearly better normalized rectangle. Preserve necessary labels/arrows and avoid unrelated panels. Ensure x+width <= 1 and y+height <= 1. Do not claim hidden chain-of-thought.

Records:
{json.dumps(records, ensure_ascii=False, indent=2)}

Return exactly one review for each model_id and no others."""


def run_batch(index: int, batch: list[dict[str, Any]], output_role: str) -> dict[str, Any]:
    name = f"batch_{index:02d}"
    output_dir = RUN_ROOT / "subagents" / output_role / name
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = output_dir / "output_schema.json"
    prompt_path = output_dir / "prompt.txt"
    response = output_dir / "response.json"
    stdout = output_dir / "stdout.jsonl"
    stderr = output_dir / "stderr.log"
    metadata_path = output_dir / "metadata.json"
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
            error = "Missing final validation response"
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
    parser.add_argument("--output-role", default="final_preview_validator")
    args = parser.parse_args()
    manifest = read_json(RUN_ROOT / args.manifest)
    batches = [manifest[index:index + 5] for index in range(0, len(manifest), 5)]
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
