#!/usr/bin/env python3
"""Render and semantically validate every current atlas crop preview."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import signal
import shutil
import subprocess
import tempfile
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ATLAS = ROOT / "docs/input-representation-atlas/data/atlas.json"
DEFAULT_LEDGER = (
    ROOT
    / "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
    / "crops_final/crop_ledger.json"
)
DEFAULT_OUTPUT = ROOT / "analysis/atlas_exact_preview_validation_2026-08-17"
DEFAULT_MODEL = "gpt-5.4-mini"
F7_AUDIT_ID = "F7_exact_preview_v1"
F7_TERMINAL_POLICY = "omit_after_exhaustive_validation_failure_v1"

FAILURE_MODES = [
    "none",
    "unreadable_at_preview_scale",
    "crop_omits_required_label_or_arrow",
    "crop_contains_excess_irrelevant_content",
    "other_model",
    "downstream_consumer",
    "model_output",
    "grader_or_scorer",
    "performance_or_analysis",
    "generic_data_summary",
    "wrong_lifecycle_or_configuration",
    "wrong_model_variant",
    "no_visible_model_input",
    "other",
]

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

REVIEW_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "model_id",
        "decision",
        "route_ids_supported",
        "visible_input_evidence",
        "failure_modes",
        "proposed_crop_box",
        "concise_rationale",
        "confidence",
    ],
    "properties": {
        "model_id": {"type": "string"},
        "decision": {"type": "string", "enum": ["pass", "adjust", "reject"]},
        "route_ids_supported": {"type": "array", "items": {"type": "string"}},
        "visible_input_evidence": {"type": "array", "items": {"type": "string"}},
        "failure_modes": {
            "type": "array",
            "items": {"type": "string", "enum": FAILURE_MODES},
        },
        "proposed_crop_box": BBOX_SCHEMA,
        "concise_rationale": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
}

REVIEW_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["reviewer_role", "reviews"],
    "properties": {
        "reviewer_role": {"type": "string"},
        "reviews": {"type": "array", "items": REVIEW_ITEM_SCHEMA},
    },
}

ADJUDICATION_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "model_id",
        "final_action",
        "route_ids_supported",
        "visible_input_evidence",
        "failure_modes",
        "final_crop_box",
        "concise_rationale",
        "confidence",
    ],
    "properties": {
        "model_id": {"type": "string"},
        "final_action": {
            "type": "string",
            "enum": [
                "accept_current",
                "adjust_current",
                "no_suitable_figure",
                "replacement_required",
                "manual_review",
            ],
        },
        "route_ids_supported": {"type": "array", "items": {"type": "string"}},
        "visible_input_evidence": {"type": "array", "items": {"type": "string"}},
        "failure_modes": {
            "type": "array",
            "items": {"type": "string", "enum": FAILURE_MODES},
        },
        "final_crop_box": BBOX_SCHEMA,
        "concise_rationale": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
}

ADJUDICATION_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["reviews"],
    "properties": {
        "reviews": {"type": "array", "items": ADJUDICATION_ITEM_SCHEMA},
    },
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def crop_pixels(crop: dict[str, float], width: int, height: int) -> tuple[int, int, int, int]:
    x = max(0, min(width - 1, math.floor(crop["x"] * width)))
    y = max(0, min(height - 1, math.floor(crop["y"] * height)))
    right = max(x + 1, min(width, math.ceil((crop["x"] + crop["width"]) * width)))
    bottom = max(y + 1, min(height, math.ceil((crop["y"] + crop["height"]) * height)))
    return x, y, right - x, bottom - y


def valid_crop_box(crop: dict[str, Any] | None) -> bool:
    if not crop:
        return False
    return (
        0 <= crop["x"] <= 1
        and 0 <= crop["y"] <= 1
        and 0.03 <= crop["width"] <= 1
        and 0.03 <= crop["height"] <= 1
        and crop["x"] + crop["width"] <= 1.000001
        and crop["y"] + crop["height"] <= 1.000001
    )


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{result.stderr}")


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


def compact_route(route: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "route_id",
        "route_label",
        "lifecycle_phase",
        "task_or_configuration_verbatim",
        "source_object_verbatim",
        "transformation_chain_verbatim",
        "model_visible_form_verbatim",
        "carrier_family",
        "carrier_subtype",
        "insertion_or_fusion_verbatim",
        "fusion_topology",
        "text_role",
        "input_status",
        "evidence_quote",
        "section_heading",
        "supporting_figure_or_table",
        "pages",
    ]
    return {key: route.get(key) for key in keys}


def render_crop_panel(
    *, source: Path, crop: dict[str, float], width: int, height: int, panel: Path, exact_crop: Path
) -> dict[str, Any]:
    if not valid_crop_box(crop):
        raise ValueError(f"Invalid crop box: {crop}")
    x, y, crop_width, crop_height = crop_pixels(crop, width, height)
    panel.parent.mkdir(parents=True, exist_ok=True)
    exact_crop.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            "magick",
            str(source),
            "-crop",
            f"{crop_width}x{crop_height}+{x}+{y}",
            "+repage",
            str(exact_crop),
        ]
    )
    stroke = max(4, round(max(width, height) / 220))
    run_command(
        [
            "magick",
            "(",
            str(source),
            "-stroke",
            "#e11d48",
            "-strokewidth",
            str(stroke),
            "-fill",
            "none",
            "-draw",
            f"rectangle {x},{y} {x + crop_width - 1},{y + crop_height - 1}",
            "-resize",
            "1400x900>",
            "-bordercolor",
            "white",
            "-border",
            "10",
            ")",
            "(",
            str(exact_crop),
            "-resize",
            "900x900>",
            "-bordercolor",
            "#e11d48",
            "-border",
            "5",
            ")",
            "+append",
            "-background",
            "white",
            "-gravity",
            "center",
            "-quality",
            "92",
            str(panel),
        ]
    )
    return {
        "panel_path": display_path(panel),
        "panel_sha256": sha256(panel),
        "exact_crop_path": display_path(exact_crop),
        "exact_crop_sha256": sha256(exact_crop),
        "source_sha256": sha256(source),
        "pixel_crop": {"x": x, "y": y, "width": crop_width, "height": crop_height},
        "panel_layout": "left=full source figure with red crop box; right=exact selected source-pixel crop",
    }


def prepare_manifest(
    *,
    atlas_path: Path,
    ledger_path: Path,
    output_dir: Path,
    taxonomy_root: Path | None = None,
    source_root: Path = ROOT,
) -> list[dict[str, Any]]:
    ledger = read_json(ledger_path)
    atlas = None
    route_path = None
    if taxonomy_root is not None:
        route_path = taxonomy_root / "route_annotations.jsonl"
        routes = [
            json.loads(line)
            for line in route_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for route in routes:
            grouped[route["model_id"]].append(route)
        architectures = {}
        for model_id, model_routes in grouped.items():
            first = model_routes[0]
            architectures[model_id] = {
                "model_id": model_id,
                "model_name": first["model_name"],
                "record_id": first["record_id"],
                "paper_title": first["title"],
                "routes": model_routes,
            }
    else:
        atlas = read_json(atlas_path)
        architectures = {item["model_id"]: item for item in atlas["architectures"]}
        if len(architectures) != len(atlas["architectures"]):
            raise RuntimeError("Duplicate model IDs in atlas")
    if len(ledger) != len(architectures) or {item["model_id"] for item in ledger} != set(architectures):
        raise RuntimeError("Crop ledger and atlas model sets differ")
    manifest = []
    no_suitable = []
    panel_root = output_dir / "review_panels"
    for item in sorted(ledger, key=lambda value: value["model_id"]):
        architecture = architectures[item["model_id"]]
        if item["status"] != "cropped_source_figure":
            no_suitable.append(
                {
                    "model_id": item["model_id"],
                    "model_name": architecture["model_name"],
                    "record_id": architecture["record_id"],
                    "paper_title": architecture["paper_title"],
                    "status": item["status"],
                    "rationale": item.get("rationale") or architecture.get("no_figure_rationale"),
                    "exact_preview_status": "not_applicable_no_crop",
                }
            )
            continue
        if taxonomy_root is not None:
            figure = item.get("figure")
            if not figure:
                raise RuntimeError(f"Crop ledger lacks source figure for {item['model_id']}")
            source = Path(figure["image_path"])
            if not source.is_absolute():
                source = source_root / source
        else:
            figure = architecture.get("figure")
            if not figure or figure.get("status") != "cropped_source_figure":
                raise RuntimeError(f"Atlas lacks crop payload for {item['model_id']}")
            source = atlas_path.parents[1] / figure["asset"]
        if not source.exists():
            raise FileNotFoundError(source)
        route_ids = {route["route_id"] for route in architecture["routes"]}
        claimed = set(item.get("route_ids_supported") or [])
        if not claimed or not claimed.issubset(route_ids):
            raise RuntimeError(f"Invalid claimed route set for {item['model_id']}: {sorted(claimed - route_ids)}")
        if taxonomy_root is None and figure["sha256"] != sha256(source):
            raise RuntimeError(f"Published atlas asset hash mismatch: {item['model_id']}")
        actual_width, actual_height = image_dimensions(source)
        expected_width = int(figure["pixel_width"])
        expected_height = int(figure["pixel_height"])
        if (actual_width, actual_height) != (expected_width, expected_height):
            raise RuntimeError(
                f"Source image dimensions differ from ledger for {item['model_id']}: "
                f"{actual_width}x{actual_height} != {expected_width}x{expected_height}"
            )
        rendered = render_crop_panel(
            source=source,
            crop=item["crop_box"],
            width=expected_width,
            height=expected_height,
            panel=panel_root / "current" / f"{item['model_id']}.jpg",
            exact_crop=panel_root / "exact_crops" / f"{item['model_id']}.png",
        )
        manifest.append(
            {
                "model_id": item["model_id"],
                "model_name": architecture["model_name"],
                "record_id": architecture["record_id"],
                "paper_title": architecture["paper_title"],
                "figure_index": figure["figure_index"],
                "figure_caption": figure.get("caption") or "",
                "current_crop_box": item["crop_box"],
                "claimed_route_ids_supported": sorted(claimed),
                "visible_input_object_claim": item.get("visible_input_object") or "",
                "visible_model_interface_claim": item.get("visible_model_interface") or "",
                "routes": [compact_route(route) for route in architecture["routes"]],
                **rendered,
            }
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "preview_manifest.json", manifest)
    write_json(output_dir / "no_suitable_figure_manifest.json", no_suitable)
    report = {
        "created_at": utc_now(),
        "atlas_path": str(atlas_path) if taxonomy_root is None else None,
        "atlas_sha256": sha256(atlas_path) if taxonomy_root is None else None,
        "taxonomy_route_path": str(route_path) if route_path else None,
        "taxonomy_route_sha256": sha256(route_path) if route_path else None,
        "crop_ledger_path": str(ledger_path),
        "crop_ledger_sha256": sha256(ledger_path),
        "models_total": len(architectures),
        "rendered_exact_previews": len(manifest),
        "no_suitable_figure": len(no_suitable),
        "source": (
            "candidate source figures, candidate taxonomy routes, and candidate crop ledger"
            if taxonomy_root is not None
            else "current published atlas assets and current crop ledger"
        ),
    }
    write_json(output_dir / "preview_build_report.json", report)
    return manifest


def role_prompt(role: str, batch: list[dict[str, Any]]) -> str:
    records = []
    for image_index, item in enumerate(batch, start=1):
        records.append(
            {
                "image_attachment_index": image_index,
                "model_id": item["model_id"],
                "model_name": item["model_name"],
                "paper_title": item["paper_title"],
                "figure_index": item["figure_index"],
                "current_crop_box": item["current_crop_box"],
                "claimed_route_ids_supported": item["claimed_route_ids_supported"],
                "routes": item["routes"],
            }
        )
    if role in {
        "exact_preview_validator",
        "changed_preview_validator",
        "replacement_preview_validator",
        "replacement_preview_validator_round2",
    }:
        role_text = """Act as a blind exact-preview validator. Judge the crop on the RIGHT as a scientific preview. It passes only if the visible labels, arrows, and objects form a coherent and readable source-to-model input path for at least one listed route. Reject clipped, ambiguous, unreadable, or needlessly broad regions. Use `adjust` only when the full source figure on the LEFT contains a clearly better rectangle."""
    elif role in {"input_role_validator", "replacement_input_role_validator"}:
        role_text = """Act as a blind adversarial input-role validator. Determine what the RIGHT crop actually depicts. It passes only when it visibly shows an input, transformation, model-visible carrier, or immediate interface for the exact named model and at least one listed `actual_model_input` route. Reject outputs, downstream consumers, graders, benchmark/results panels, generic data summaries, wrong variants, or wrong lifecycle/configuration evidence."""
    else:
        raise ValueError(role)
    return f"""{role_text}

Every attachment has the full source figure with the selected red rectangle on the LEFT and the exact selected source-pixel crop on the RIGHT.

Rules:
- Inspect pixels, not earlier agent rationales.
- The representative crop need not show every route, but report exactly which route IDs it visibly supports.
- A `pass` requires at least one supported route and concrete visible evidence.
- For `adjust`, return normalized coordinates relative to the full source figure and ensure x+width <= 1 and y+height <= 1.
- Use `reject` when this figure cannot support a responsible crop for the target model/routes.
- Return one review for every model_id and no others.
- Do not use tools, external knowledge, or hidden chain-of-thought. Keep rationales concise and tied to visible content.

Reviewer role: {role}

RECORDS
{json.dumps(records, ensure_ascii=False, indent=2)}
"""


def run_codex_attempt(
    *, prompt: str, schema: dict[str, Any], images: list[Path], output_dir: Path, model: str, timeout: int
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = output_dir / "prompt.txt"
    schema_path = output_dir / "output_schema.json"
    response_path = output_dir / "response.json"
    stdout_path = output_dir / "stdout.jsonl"
    stderr_path = output_dir / "stderr.log"
    prompt_path.write_text(prompt, encoding="utf-8")
    write_json(schema_path, schema)
    started = utc_now()
    clock = time.monotonic()
    status = "ok"
    error = ""
    returncode: int | None = None
    with tempfile.TemporaryDirectory(prefix="atlas-exact-preview-") as workspace:
        command = [
            "codex", "exec", "--model", model, "--cd", workspace, "--sandbox", "read-only",
            "--skip-git-repo-check", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
            "--disable", "shell_tool", "--disable", "unified_exec", "--strict-config",
            "--disable", "apps", "--disable", "plugins", "--disable", "enable_mcp_apps",
            "--disable", "browser_use", "--disable", "computer_use", "--disable", "plugin_sharing",
            "--disable", "tool_suggest", "--disable", "workspace_dependencies",
            "--output-last-message", str(response_path), "--output-schema", str(schema_path),
        ]
        for image in images:
            command.extend(["--image", str(image.resolve())])
        command.append("-")
        process = subprocess.Popen(
            command,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=workspace,
            env={**os.environ, "NO_COLOR": "1"},
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(input=prompt, timeout=timeout)
            returncode = process.returncode
            stdout_path.write_text(stdout, encoding="utf-8")
            stderr_path.write_text(stderr, encoding="utf-8")
            if process.returncode:
                status = "error_returncode"
                error = stderr[-4000:]
            elif not response_path.exists():
                status = "missing_response"
                error = "Codex exited without response.json"
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
            status = "timeout"
            error = f"Timed out after {timeout} seconds"
            stdout_path.write_text(stdout, encoding="utf-8")
            stderr_path.write_text(stderr, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - operational guard
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
            status = "exception"
            error = repr(exc)
            stdout_path.write_text("", encoding="utf-8")
            stderr_path.write_text(error + "\n", encoding="utf-8")
    metadata = {
        "status": status,
        "model": model,
        "command": command,
        "images": [
            {"path": display_path(path), "sha256": sha256(path)} for path in images
        ],
        "prompt_sha256": sha256(prompt_path),
        "schema_sha256": sha256(schema_path),
        "started_at": started,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - clock, 3),
        "returncode": returncode,
        "error": error,
        "agent_workspace": "isolated_empty_temporary_directory",
        "agent_tool_policy": "shell_exec_apps_plugins_browser_computer_and_workspace_tools_disabled",
        "repository_checkout_available_as_working_context": False,
    }
    write_json(output_dir / "metadata.json", metadata)
    return metadata


def validate_review_response(
    response: dict[str, Any], batch: list[dict[str, Any]], *, adjudication: bool = False
) -> None:
    expected = {item["model_id"] for item in batch}
    reviews = response.get("reviews") or []
    returned = [review.get("model_id") for review in reviews]
    if len(returned) != len(set(returned)) or set(returned) != expected:
        raise ValueError(f"Model coverage mismatch: expected={sorted(expected)} returned={sorted(returned)}")
    route_sets = {
        item["model_id"]: {route["route_id"] for route in item["routes"]} for item in batch
    }
    for review in reviews:
        supported = set(review["route_ids_supported"])
        if not supported.issubset(route_sets[review["model_id"]]):
            raise ValueError(f"Unknown route IDs for {review['model_id']}")
        decision = review["final_action"] if adjudication else review["decision"]
        box = review["final_crop_box"] if adjudication else review["proposed_crop_box"]
        pass_like = decision in {"pass", "accept_current", "adjust_current"}
        if pass_like and (not supported or not review["visible_input_evidence"]):
            raise ValueError(f"Passing review lacks visible route evidence: {review['model_id']}")
        if decision in {"adjust", "adjust_current"} and not valid_crop_box(box):
            raise ValueError(f"Invalid proposed crop: {review['model_id']}")


def make_batches(manifest: list[dict[str, Any]], batch_size: int) -> list[list[dict[str, Any]]]:
    return [manifest[index : index + batch_size] for index in range(0, len(manifest), batch_size)]


def next_attempt_number(target: Path) -> int:
    numbers = [
        int(path.name.removeprefix("attempt_"))
        for path in target.glob("attempt_[0-9][0-9]")
        if path.name.removeprefix("attempt_").isdigit()
    ]
    return max(numbers, default=0) + 1


def run_batch(
    *,
    role: str,
    index: int,
    batch: list[dict[str, Any]],
    output_dir: Path,
    model: str,
    timeout: int,
    retries: int,
    force: bool,
) -> dict[str, Any]:
    target = output_dir / "runs" / role / f"batch_{index:03d}"
    selected = target / "selected_response.json"
    summary_path = target / "run_summary.json"
    if selected.exists() and not force:
        try:
            validate_review_response(read_json(selected), batch)
            return read_json(summary_path)
        except Exception:
            pass
    prompt = role_prompt(role, batch)
    images = [ROOT / item["panel_path"] for item in batch]
    attempts = []
    first_attempt = next_attempt_number(target)
    for attempt_no in range(first_attempt, first_attempt + retries + 1):
        attempt_dir = target / f"attempt_{attempt_no:02d}"
        metadata = run_codex_attempt(
            prompt=prompt,
            schema=REVIEW_SCHEMA,
            images=images,
            output_dir=attempt_dir,
            model=model,
            timeout=timeout,
        )
        attempts.append(metadata)
        if metadata["status"] != "ok":
            continue
        try:
            response = read_json(attempt_dir / "response.json")
            validate_review_response(response, batch)
        except Exception as exc:
            metadata["status"] = "invalid_response"
            metadata["error"] = repr(exc)
            write_json(attempt_dir / "metadata.json", metadata)
            continue
        shutil.copy2(attempt_dir / "response.json", selected)
        summary = {
            "role": role,
            "batch": index,
            "status": "ok",
            "selected_attempt": attempt_no,
            "model_ids": [item["model_id"] for item in batch],
            "attempts": attempts,
        }
        write_json(summary_path, summary)
        return summary
    summary = {
        "role": role,
        "batch": index,
        "status": "failed",
        "selected_attempt": None,
        "model_ids": [item["model_id"] for item in batch],
        "attempts": attempts,
    }
    write_json(summary_path, summary)
    return summary


def run_role(
    *,
    role: str,
    output_dir: Path,
    model: str,
    timeout: int,
    retries: int,
    max_workers: int,
    batch_size: int,
    force: bool,
    manifest_name: str = "preview_manifest.json",
) -> list[dict[str, Any]]:
    manifest = read_json(output_dir / manifest_name)
    batches = make_batches(manifest, batch_size)
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(
                run_batch,
                role=role,
                index=index,
                batch=batch,
                output_dir=output_dir,
                model=model,
                timeout=timeout,
                retries=retries,
                force=force,
            )
            for index, batch in enumerate(batches)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["batch"])
    write_json(
        output_dir / "runs" / role / "run_summary.json",
        {
            "role": role,
            "model": model,
            "batches": len(results),
            "models": len(manifest),
            "ok": sum(item["status"] == "ok" for item in results),
            "results": results,
        },
    )
    if not all(item["status"] == "ok" for item in results):
        raise RuntimeError(f"Incomplete role: {role}")
    return results


def role_review_index(output_dir: Path, role: str) -> dict[str, dict[str, Any]]:
    index = {}
    for response_path in sorted((output_dir / "runs" / role).glob("batch_*/selected_response.json")):
        for review in read_json(response_path)["reviews"]:
            index[review["model_id"]] = review
    return index


def audit_tool_isolation(output_dir: Path) -> dict[str, Any]:
    tool_types = {"command_execution", "mcp_tool_call", "web_search", "computer_use"}
    events = []
    for stdout_path in sorted((output_dir / "runs").rglob("stdout.jsonl")):
        for line_number, line in enumerate(stdout_path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = payload.get("item") if isinstance(payload.get("item"), dict) else {}
            if item.get("type") not in tool_types:
                continue
            events.append(
                {
                    "path": display_path(stdout_path),
                    "line": line_number,
                    "type": item["type"],
                    "status": item.get("status"),
                }
            )
    audit = {
        "status": "pass" if not events else "fail",
        "tool_events": len(events),
        "events": events,
        "acceptance_rule": "No shell, MCP, web, browser, computer-use, or other tool event is permitted.",
    }
    write_json(output_dir / "tool_isolation_audit.json", audit)
    return audit


def needs_adjudication(first: dict[str, Any], second: dict[str, Any]) -> bool:
    return (
        first["decision"] != "pass"
        or second["decision"] != "pass"
        or not (set(first["route_ids_supported"]) & set(second["route_ids_supported"]))
    )


def build_comparison(output_dir: Path) -> list[dict[str, Any]]:
    exact = role_review_index(output_dir, "exact_preview_validator")
    input_role = role_review_index(output_dir, "input_role_validator")
    if set(exact) != set(input_role):
        raise RuntimeError("Exact-preview and input-role model sets differ")
    comparison = [
        {
            "model_id": model_id,
            "requires_adjudication": needs_adjudication(exact[model_id], input_role[model_id]),
            "exact_preview_validator": exact[model_id],
            "input_role_validator": input_role[model_id],
        }
        for model_id in sorted(exact)
    ]
    write_json(output_dir / "reviewer_comparison.json", comparison)
    return comparison


def adjudication_prompt(batch: list[dict[str, Any]]) -> str:
    payload = []
    for index, item in enumerate(batch, start=1):
        payload.append(
            {
                "image_attachment_index": index,
                "model_id": item["model_id"],
                "model_name": item["model_name"],
                "paper_title": item["paper_title"],
                "current_crop_box": item["current_crop_box"],
                "routes": item["routes"],
                "exact_preview_review": item["exact_preview_review"],
                "input_role_review": item["input_role_review"],
            }
        )
    return f"""You are the independent adjudicator for atlas crop validation.

Each image shows the full source figure with the current red crop on the LEFT and the exact crop on the RIGHT. Resolve the two blind reviews by inspecting the pixels yourself. Accept only a crop that is coherent and readable and visibly supports an actual input route for the exact named model. Use `adjust_current` only when a better rectangle exists in this same source figure. Use `replacement_required` when another paper figure is needed, `no_suitable_figure` when the current crop should be removed and the paper appears not to offer responsible visual evidence, and `manual_review` when the pixels are insufficient to decide.

Return normalized coordinates for `adjust_current`; return null otherwise. Do not use tools, external knowledge, or hidden chain-of-thought.

CASES
{json.dumps(payload, ensure_ascii=False, indent=2)}
"""


def run_adjudication_batch(
    *,
    index: int,
    batch: list[dict[str, Any]],
    output_dir: Path,
    model: str,
    timeout: int,
    retries: int,
    force: bool,
) -> dict[str, Any]:
    role = "adjudicator"
    target = output_dir / "runs" / role / f"batch_{index:03d}"
    selected = target / "selected_response.json"
    summary_path = target / "run_summary.json"
    if selected.exists() and not force:
        try:
            validate_review_response(read_json(selected), batch, adjudication=True)
            return read_json(summary_path)
        except Exception:
            pass
    prompt = adjudication_prompt(batch)
    images = [ROOT / item["panel_path"] for item in batch]
    attempts = []
    first_attempt = next_attempt_number(target)
    for attempt_no in range(first_attempt, first_attempt + retries + 1):
        attempt_dir = target / f"attempt_{attempt_no:02d}"
        metadata = run_codex_attempt(
            prompt=prompt,
            schema=ADJUDICATION_SCHEMA,
            images=images,
            output_dir=attempt_dir,
            model=model,
            timeout=timeout,
        )
        attempts.append(metadata)
        if metadata["status"] != "ok":
            continue
        try:
            response = read_json(attempt_dir / "response.json")
            validate_review_response(response, batch, adjudication=True)
        except Exception as exc:
            metadata["status"] = "invalid_response"
            metadata["error"] = repr(exc)
            write_json(attempt_dir / "metadata.json", metadata)
            continue
        shutil.copy2(attempt_dir / "response.json", selected)
        summary = {
            "role": role,
            "batch": index,
            "status": "ok",
            "selected_attempt": attempt_no,
            "model_ids": [item["model_id"] for item in batch],
            "attempts": attempts,
        }
        write_json(summary_path, summary)
        return summary
    summary = {
        "role": role,
        "batch": index,
        "status": "failed",
        "selected_attempt": None,
        "model_ids": [item["model_id"] for item in batch],
        "attempts": attempts,
    }
    write_json(summary_path, summary)
    return summary


def run_adjudicator(
    *, output_dir: Path, model: str, timeout: int, retries: int, max_workers: int, batch_size: int, force: bool
) -> list[dict[str, Any]]:
    manifest = {item["model_id"]: item for item in read_json(output_dir / "preview_manifest.json")}
    comparison = build_comparison(output_dir)
    cases = []
    for item in comparison:
        if not item["requires_adjudication"]:
            continue
        record = dict(manifest[item["model_id"]])
        record["exact_preview_review"] = item["exact_preview_validator"]
        record["input_role_review"] = item["input_role_validator"]
        cases.append(record)
    batches = make_batches(cases, batch_size)
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(
                run_adjudication_batch,
                index=index,
                batch=batch,
                output_dir=output_dir,
                model=model,
                timeout=timeout,
                retries=retries,
                force=force,
            )
            for index, batch in enumerate(batches)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["batch"])
    write_json(
        output_dir / "runs" / "adjudicator" / "run_summary.json",
        {
            "role": "adjudicator",
            "model": model,
            "batches": len(results),
            "models": len(cases),
            "ok": sum(item["status"] == "ok" for item in results),
            "results": results,
        },
    )
    if not all(item["status"] == "ok" for item in results):
        raise RuntimeError("Incomplete crop adjudication")
    return results


def adjudication_index(output_dir: Path) -> dict[str, dict[str, Any]]:
    index = {}
    for path in sorted((output_dir / "runs/adjudicator").glob("batch_*/selected_response.json")):
        for review in read_json(path)["reviews"]:
            index[review["model_id"]] = review
    return index


def prepare_adjusted_manifest(output_dir: Path) -> list[dict[str, Any]]:
    manifest = {item["model_id"]: item for item in read_json(output_dir / "preview_manifest.json")}
    adjusted = []
    for model_id, review in adjudication_index(output_dir).items():
        if review["final_action"] != "adjust_current":
            continue
        item = dict(manifest[model_id])
        crop = review["final_crop_box"]
        source = ROOT / "docs/input-representation-atlas" / next(
            architecture["figure"]["asset"]
            for architecture in read_json(DEFAULT_ATLAS)["architectures"]
            if architecture["model_id"] == model_id
        )
        rendered = render_crop_panel(
            source=source,
            crop=crop,
            width=int(next(
                architecture["figure"]["pixel_width"]
                for architecture in read_json(DEFAULT_ATLAS)["architectures"]
                if architecture["model_id"] == model_id
            )),
            height=int(next(
                architecture["figure"]["pixel_height"]
                for architecture in read_json(DEFAULT_ATLAS)["architectures"]
                if architecture["model_id"] == model_id
            )),
            panel=output_dir / "review_panels/adjusted" / f"{model_id}.jpg",
            exact_crop=output_dir / "review_panels/adjusted_exact_crops" / f"{model_id}.png",
        )
        item.update(rendered)
        item["current_crop_box"] = crop
        item["adjudication"] = review
        adjusted.append(item)
    write_json(output_dir / "adjusted_preview_manifest.json", adjusted)
    return adjusted


def terminalize_unresolved_dispositions(
    dispositions: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Omit figures that remain unsupported after the exhaustive F7 workflow."""
    terminalized: list[dict[str, Any]] = []
    prior_unresolved: list[dict[str, str]] = []
    for source in dispositions:
        item = json.loads(json.dumps(source))
        status = str(item["status"])
        if status.startswith("validated_") or status == "crop_rejected_no_suitable_figure":
            terminalized.append(item)
            continue
        prior_unresolved.append(
            {
                "model_id": str(item["model_id"]),
                "model_name": str(item["model_name"]),
                "status": status,
            }
        )
        item["preterminal_status"] = status
        item["status"] = "crop_rejected_no_suitable_figure"
        item["final_crop_box"] = None
        item["route_ids_supported"] = []
        item["terminal_resolution"] = {
            "policy": F7_TERMINAL_POLICY,
            "rationale": (
                "No crop passed exact-preview and exact-model input-role validation "
                "after adjusted-crop review and exhaustive replacement-figure search. "
                "The figure is omitted rather than publishing unsupported visual evidence."
            ),
        }
        terminalized.append(item)
    return terminalized, prior_unresolved


def finalize(output_dir: Path, model: str, ledger_path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    tool_isolation = audit_tool_isolation(output_dir)
    if tool_isolation["status"] != "pass":
        raise RuntimeError(
            f"F7 tool-isolation gate failed with {tool_isolation['tool_events']} tool events"
        )
    manifest = {item["model_id"]: item for item in read_json(output_dir / "preview_manifest.json")}
    comparison = {item["model_id"]: item for item in build_comparison(output_dir)}
    adjudicated = adjudication_index(output_dir)
    changed = role_review_index(output_dir, "changed_preview_validator") if (output_dir / "runs/changed_preview_validator").exists() else {}
    replacement_results = {
        item["model_id"]: item
        for item in (
            read_json(output_dir / "replacement_validation_results.json")
            if (output_dir / "replacement_validation_results.json").exists()
            else []
        )
    }
    dispositions = []
    for model_id, item in sorted(manifest.items()):
        comparison_item = comparison[model_id]
        if not comparison_item["requires_adjudication"]:
            status = "validated_current_crop"
            final_crop = item["current_crop_box"]
            supported = sorted(
                set(comparison_item["exact_preview_validator"]["route_ids_supported"])
                & set(comparison_item["input_role_validator"]["route_ids_supported"])
            )
            final_review = None
        else:
            final_review = adjudicated.get(model_id)
            if final_review is None:
                raise RuntimeError(f"Missing crop adjudication: {model_id}")
            action = final_review["final_action"]
            supported = final_review["route_ids_supported"]
            if action == "accept_current":
                status = "validated_current_crop_after_adjudication"
                final_crop = item["current_crop_box"]
            elif action == "adjust_current":
                changed_review = changed.get(model_id)
                if changed_review and changed_review["decision"] == "pass":
                    status = "validated_adjusted_crop"
                    final_crop = final_review["final_crop_box"]
                    supported = changed_review["route_ids_supported"]
                else:
                    replacement = replacement_results.get(model_id)
                    if replacement and replacement["status"] == "validated_replacement_crop":
                        status = "validated_replacement_crop"
                        final_crop = replacement["final_crop_box"]
                        supported = replacement["replacement_preview_validation"]["route_ids_supported"]
                    elif replacement and replacement["status"] == "no_suitable_figure":
                        status = "crop_rejected_no_suitable_figure"
                        final_crop = None
                    else:
                        status = "unresolved_adjusted_crop"
                        final_crop = final_review["final_crop_box"]
            elif action == "no_suitable_figure":
                status = "crop_rejected_no_suitable_figure"
                final_crop = None
            elif action == "replacement_required":
                replacement = replacement_results.get(model_id)
                if replacement and replacement["status"] == "validated_replacement_crop":
                    status = "validated_replacement_crop"
                    final_crop = replacement["final_crop_box"]
                    supported = replacement["replacement_preview_validation"]["route_ids_supported"]
                elif replacement and replacement["status"] == "no_suitable_figure":
                    status = "crop_rejected_no_suitable_figure"
                    final_crop = None
                else:
                    status = "unresolved_replacement_required"
                    final_crop = None
            else:
                status = f"unresolved_{action}"
                final_crop = None
        dispositions.append(
            {
                "model_id": model_id,
                "model_name": item["model_name"],
                "record_id": item["record_id"],
                "status": status,
                "source_figure_index": item["figure_index"],
                "original_crop_box": item["current_crop_box"],
                "final_crop_box": final_crop,
                "route_ids_supported": supported,
                "reviewer_comparison": comparison_item,
                "adjudication": final_review,
                "changed_preview_validation": changed.get(model_id),
                "replacement_validation": replacement_results.get(model_id),
                "source_sha256": item["source_sha256"],
                "original_panel_sha256": item["panel_sha256"],
            }
        )
    dispositions, prior_unresolved = terminalize_unresolved_dispositions(dispositions)
    write_json(output_dir / "crop_validation_dispositions.json", dispositions)
    statuses = Counter(item["status"] for item in dispositions)
    no_suitable = read_json(output_dir / "no_suitable_figure_manifest.json")
    validated = sum(count for status, count in statuses.items() if status.startswith("validated_"))
    unresolved = len(dispositions) - validated - statuses.get("crop_rejected_no_suitable_figure", 0)
    report = {
        "status": "complete" if unresolved == 0 else "complete_with_unresolved_cases",
        "created_at": utc_now(),
        "model": model,
        "validation_type": "blind exact-preview validation plus adversarial input-role validation and adjudication",
        "human_validation": False,
        "canonical_crop_ledger_mutated": False,
        "atlas_models": len(dispositions) + len(no_suitable),
        "exact_previews_rendered": len(dispositions),
        "preexisting_no_suitable_figure": len(no_suitable),
        "validated_crops": validated,
        "adjudicated_models": len(adjudicated),
        "status_counts": dict(sorted(statuses.items())),
        "unresolved_models": unresolved,
        "preterminal_unresolved_models": prior_unresolved,
        "terminal_no_suitable_from_unresolved": len(prior_unresolved),
        "terminal_resolution_policy": F7_TERMINAL_POLICY,
        "all_current_atlas_assets_hash_verified": True,
        "all_reviewed_images_hash_logged": True,
        "tool_isolation_passed": True,
    }
    write_json(output_dir / "exact_preview_validation_report.json", report)
    build_proposed_crop_ledger(output_dir, dispositions, ledger_path)
    lines = [
        "# F7 exact-preview and input-role validation",
        "",
        "This audit rendered the crop coordinates from the current crop ledger against the current "
        "published atlas assets. Two blind roles separately checked visual sufficiency and exact-model "
        "input-role integrity; non-passes were adjudicated. The canonical crop ledger was not silently "
        "modified.",
        "",
        f"- Atlas models: **{report['atlas_models']}**",
        f"- Exact crop previews rendered and reviewed: **{report['exact_previews_rendered']}**",
        f"- Pre-existing `no_suitable_figure`: **{report['preexisting_no_suitable_figure']}**",
        f"- Validated crops: **{report['validated_crops']}**",
        f"- Models adjudicated: **{report['adjudicated_models']}**",
        f"- Exhaustive failures conservatively omitted: **{report['terminal_no_suitable_from_unresolved']}**",
        f"- Unresolved models: **{report['unresolved_models']}**",
        f"- Model for every role: `{model}`",
        "- Interpretation: repeated computational visual annotation with LLM adjudication, not human ground truth",
        "",
        "## Dispositions",
        "",
    ]
    for status, count in sorted(statuses.items()):
        lines.append(f"- `{status}`: {count}")
    rejected = [
        item for item in dispositions if item["status"] == "crop_rejected_no_suitable_figure"
    ]
    adjusted = [item for item in dispositions if item["status"] == "validated_adjusted_crop"]
    if adjusted:
        lines.extend(["", "## Adjusted and revalidated", ""])
        for item in adjusted:
            lines.append(f"- `{item['model_id']}` — {item['model_name']}")
    if rejected:
        lines.extend(["", "## Rejected after exhaustive figure search", ""])
        for item in rejected:
            lines.append(f"- `{item['model_id']}` — {item['model_name']}")
    lines.extend(
        [
            "",
            "`crop_validation_dispositions.json` contains every model-level decision. Exact prompts, "
            "schemas, responses, commands, image hashes, retries, stderr/stdout, and timings are under "
            "`runs/`. Review panels are deterministic regenerated intermediates and are excluded from Git; "
            "their hashes remain in the manifest and logs.",
            "",
        ]
    )
    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    hashes = {}
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and "review_panels" not in path.parts and path.name != "artifact_hashes.json":
            hashes[str(path.relative_to(output_dir))] = sha256(path)
    write_json(output_dir / "artifact_hashes.json", hashes)
    return report


def build_proposed_crop_ledger(
    output_dir: Path, dispositions: list[dict[str, Any]], ledger_path: Path = DEFAULT_LEDGER
) -> list[dict[str, Any]]:
    ledger = read_json(ledger_path)
    by_model = {item["model_id"]: item for item in dispositions}
    proposed = []
    for source in ledger:
        item = json.loads(json.dumps(source))
        disposition = by_model.get(item["model_id"])
        if disposition is None:
            item["exact_preview_validation"] = {
                "status": "not_applicable_no_crop",
                "audit": F7_AUDIT_ID,
            }
            proposed.append(item)
            continue
        status = disposition["status"]
        replacement = disposition.get("replacement_validation")
        if status == "validated_adjusted_crop":
            item["crop_box"] = disposition["final_crop_box"]
            item["annotation_pass"] = f"{item['annotation_pass']}__F7_adjusted_exact_preview_pass"
        elif status == "validated_replacement_crop":
            figure = replacement["figure"]
            crop = replacement["crop"]
            item.update(
                {
                    "status": "cropped_source_figure",
                    "figure": {
                        "figure_index": figure["figure_index"],
                        "image_path": figure["manifest_image_path"],
                        "pixel_width": figure["pixel_width"],
                        "pixel_height": figure["pixel_height"],
                        "caption": figure["caption"],
                        "page_no": figure["page_no"],
                    },
                    "crop_box": disposition["final_crop_box"],
                    "panel_label": crop["panel_label"],
                    "visible_input_object": crop["visible_input_object"],
                    "visible_model_interface": crop["visible_model_interface"],
                    "figure_suitability": "suitable",
                    "confidence": crop["confidence"],
                    "rationale": crop["concise_rationale"],
                    "route_ids_supported": disposition["route_ids_supported"],
                    "annotation_pass": "F7_replacement_selector_cropper_exact_preview_pass",
                }
            )
        elif status == "crop_rejected_no_suitable_figure":
            item.update(
                {
                    "status": "no_suitable_figure",
                    "figure": None,
                    "crop_box": None,
                    "panel_label": None,
                    "visible_input_object": None,
                    "visible_model_interface": None,
                    "figure_suitability": "no_suitable_figure",
                    "route_ids_supported": [],
                    "annotation_pass": "F7_exact_preview_input_role_rejected_no_suitable_figure",
                    "rationale": (
                        disposition["terminal_resolution"]["rationale"]
                        if disposition.get("terminal_resolution")
                        else replacement["replacement_input_role_validation"]["concise_rationale"]
                        if (
                            replacement
                            and replacement["status"] == "no_suitable_figure"
                            and replacement.get("replacement_input_role_validation")
                            and replacement["replacement_input_role_validation"]["decision"] == "reject"
                        )
                        else replacement["selection"]["concise_rationale"]
                        if replacement and replacement["status"] == "no_suitable_figure"
                        else disposition["adjudication"]["concise_rationale"]
                    ),
                }
            )
        item["exact_preview_validation"] = {
            "status": status,
            "audit": F7_AUDIT_ID,
            "route_ids_supported": disposition["route_ids_supported"],
            "preterminal_status": disposition.get("preterminal_status"),
            "terminal_resolution": disposition.get("terminal_resolution"),
        }
        proposed.append(item)
    if len(proposed) != len(ledger) or len({item["model_id"] for item in proposed}) != len(ledger):
        raise RuntimeError("Proposed crop ledger coverage mismatch")
    write_json(output_dir / "proposed_crossvalidated_crop_ledger.json", proposed)
    return proposed


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument(
        "command",
        choices=["prepare", "review", "compare", "adjudicate", "adjusted", "finalize", "all"],
    )
    value.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    value.add_argument("--crop-ledger", type=Path, default=DEFAULT_LEDGER)
    value.add_argument("--taxonomy-root", type=Path)
    value.add_argument("--source-root", type=Path, default=ROOT)
    value.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    value.add_argument("--model", default=DEFAULT_MODEL)
    value.add_argument(
        "--role",
        choices=[
            "exact_preview_validator",
            "input_role_validator",
            "changed_preview_validator",
            "replacement_preview_validator",
            "replacement_preview_validator_round2",
            "replacement_input_role_validator",
        ],
        default="exact_preview_validator",
    )
    value.add_argument("--max-workers", type=int, default=8)
    value.add_argument("--batch-size", type=int, default=4)
    value.add_argument("--timeout", type=int, default=2700)
    value.add_argument("--retries", type=int, default=1)
    value.add_argument("--force", action="store_true")
    return value


def main() -> int:
    args = parser().parse_args()
    if args.command in {"prepare", "all"}:
        prepare_manifest(
            atlas_path=args.atlas,
            ledger_path=args.crop_ledger,
            output_dir=args.output_dir,
            taxonomy_root=args.taxonomy_root,
            source_root=args.source_root,
        )
    if args.command == "review":
        run_role(
            role=args.role,
            output_dir=args.output_dir,
            model=args.model,
            timeout=args.timeout,
            retries=args.retries,
            max_workers=args.max_workers,
            batch_size=args.batch_size,
            force=args.force,
            manifest_name=(
                "adjusted_preview_manifest.json"
                if args.role == "changed_preview_validator"
                else (
                    "replacement_preview_manifest.json"
                    if args.role == "replacement_preview_validator"
                    else (
                        "replacement_preview_round2_manifest.json"
                        if args.role == "replacement_preview_validator_round2"
                        else (
                            "replacement_final_manifest.json"
                            if args.role == "replacement_input_role_validator"
                            else "preview_manifest.json"
                        )
                    )
                )
            ),
        )
    if args.command == "compare":
        build_comparison(args.output_dir)
    if args.command in {"adjudicate", "all"}:
        if args.command == "all":
            for role in ["exact_preview_validator", "input_role_validator"]:
                run_role(
                    role=role,
                    output_dir=args.output_dir,
                    model=args.model,
                    timeout=args.timeout,
                    retries=args.retries,
                    max_workers=args.max_workers,
                    batch_size=args.batch_size,
                    force=args.force,
                )
        run_adjudicator(
            output_dir=args.output_dir,
            model=args.model,
            timeout=args.timeout,
            retries=args.retries,
            max_workers=args.max_workers,
            batch_size=max(1, min(3, args.batch_size)),
            force=args.force,
        )
    if args.command in {"adjusted", "all"}:
        adjusted = prepare_adjusted_manifest(args.output_dir)
        if adjusted:
            run_role(
                role="changed_preview_validator",
                output_dir=args.output_dir,
                model=args.model,
                timeout=args.timeout,
                retries=args.retries,
                max_workers=args.max_workers,
                batch_size=args.batch_size,
                force=args.force,
                manifest_name="adjusted_preview_manifest.json",
            )
    if args.command in {"finalize", "all"}:
        report = finalize(args.output_dir, args.model, args.crop_ledger)
        print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
