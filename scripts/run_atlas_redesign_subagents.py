#!/usr/bin/env python3
"""Run logged Codex subagents for the graph-first taxonomy atlas redesign."""

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
ATLAS_PATH = ROOT / "docs/input-representation-atlas/data/atlas.json"
OUTPUT_ROOT = ROOT / "data/input_representation_atlas_redesign_2026-07-11/subagents"
MODEL = "gpt-5.4-mini"


PLANNING_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["role", "findings", "recommended_graph", "risks", "acceptance_checks"],
    "properties": {
        "role": {"type": "string"},
        "findings": {"type": "array", "items": {"type": "string"}},
        "recommended_graph": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "acceptance_checks": {"type": "array", "items": {"type": "string"}},
    },
}

CROP_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["annotations"],
    "properties": {
        "annotations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "model_id", "figure_index", "figure_suitability", "crop_box",
                    "panel_label", "visible_input_object", "visible_model_interface",
                    "rationale", "confidence", "recommended_alternative_figure_index",
                ],
                "properties": {
                    "model_id": {"type": "string"},
                    "figure_index": {"type": "integer"},
                    "figure_suitability": {
                        "type": "string",
                        "enum": ["suitable", "partially_suitable", "unsuitable"],
                    },
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
                    "panel_label": {"type": "string"},
                    "visible_input_object": {"type": "string"},
                    "visible_model_interface": {"type": "string"},
                    "rationale": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "recommended_alternative_figure_index": {
                        "type": ["integer", "null"]
                    },
                },
            },
        }
    },
}

FIGURE_SELECTION_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["selections"],
    "properties": {
        "selections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["model_id", "figure_index", "rationale", "confidence"],
                "properties": {
                    "model_id": {"type": "string"},
                    "figure_index": {"type": ["integer", "null"]},
                    "rationale": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                },
            },
        }
    },
}


PLANNING_ROLES = {
    "graph_architect": """You are an information-visualization architect. Inspect the current static atlas implementation and atlas data. Propose a graph-first composition whose explicit links are root -> carrier family -> subtype -> model, with route-level detail on focus. Model nodes must remain readable while representing multi-family models. Keep the existing catalog and evidence table secondary. Focus on interaction, layout, mobile behavior, and implementation using standard web graph mechanisms. Do not edit files.""",
    "crop_methodologist": """You are a scientific-figure and evidence-provenance methodologist. Inspect the current atlas figure-selection logic and sample atlas entries. Define a reproducible policy for selecting the smallest original-paper crop that shows what enters each model and the model-facing interface. Address multi-panel figures, shared figures, unsuitable figures, attribution, crop coordinates, uncertainty, and scientific integrity. Do not edit files.""",
    "atlas_reviewer": """You are an independent biomedical methods reviewer. Audit whether the requested graph atlas can faithfully distinguish taxonomy categories, concrete model inputs, illustrative examples, and original-paper evidence. Recommend a composition and acceptance checks that prevent decorative but misleading figures. Inspect the current implementation and data, but do not edit files.""",
}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_codex(
    *,
    name: str,
    prompt: str,
    images: list[Path],
    schema: dict[str, Any],
    output_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    schema_path = output_dir / "output_schema.json"
    prompt_path = output_dir / "prompt.txt"
    response_path = output_dir / "response.json"
    stdout_path = output_dir / "stdout.jsonl"
    stderr_path = output_dir / "stderr.log"
    metadata_path = output_dir / "metadata.json"
    write_json(schema_path, schema)
    prompt_path.write_text(prompt.rstrip() + "\n", encoding="utf-8")

    command = [
        "codex", "exec", "--model", MODEL, "--cd", str(ROOT),
        "--sandbox", "read-only", "--ignore-user-config", "--ignore-rules",
        "--ephemeral", "--json", "--output-last-message", str(response_path),
        "--output-schema", str(schema_path),
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
            command,
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            cwd=ROOT,
            env={**os.environ, "NO_COLOR": "1"},
        )
        returncode = result.returncode
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")
        if result.returncode != 0:
            status = "error_returncode"
            error = result.stderr[-4000:]
        elif not response_path.exists():
            status = "missing_response"
            error = "Codex exited without writing the requested final response."
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        error = f"Timed out after {timeout_seconds} seconds"
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        stderr_path.write_text(exc.stderr or "", encoding="utf-8")
    except Exception as exc:  # pragma: no cover - operational logging
        status = "exception"
        error = repr(exc)
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(error + "\n", encoding="utf-8")

    metadata = {
        "name": name,
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


def planning_prompt(role_prompt: str) -> str:
    return f"""{role_prompt}

Workspace: {ROOT}
Read these canonical artifacts:
- docs/input-representation-atlas/index.html
- docs/input-representation-atlas/assets/app.js
- docs/input-representation-atlas/assets/styles.css
- docs/input-representation-atlas/data/atlas.json
- scripts/build_input_representation_atlas.py

The corpus has 111 model entities, 489 grounded routes, five carrier families, and fifteen subtypes. The user rejected a catalog-first layout and wants a taxonomic graph with explicit relationships. Every model node should combine a tightly relevant crop from its original paper figure with a small illustrative example of the actual model input.

Return only the requested structured review. Distinguish evidence-backed source imagery from explanatory examples. Do not claim hidden chain-of-thought."""


def compact_architecture(architecture: dict[str, Any], image_index: int) -> dict[str, Any]:
    return {
        "model_id": architecture["model_id"],
        "model_name": architecture["model_name"],
        "paper_title": architecture["paper_title"],
        "record_id": architecture["record_id"],
        "image_attachment_index": image_index,
        "figure_index": architecture["figure"]["figure_index"],
        "figure_caption": architecture["figure"]["caption"],
        "figure_description": architecture["figure"]["description"],
        "routes": [
            {
                "route_label": route["route_label"],
                "source_object": route["source_object_verbatim"],
                "transformation_chain": route["transformation_chain_verbatim"],
                "model_visible_form": route["model_visible_form_verbatim"],
                "carrier_family": route["carrier_family"],
                "carrier_subtype": route["carrier_subtype"],
                "fusion": route["insertion_or_fusion_verbatim"],
                "supporting_figure_or_table": route["supporting_figure_or_table"],
            }
            for route in architecture["routes"]
        ],
    }


def crop_prompt(architectures: list[dict[str, Any]], images: list[Path]) -> str:
    image_index = {str(path): index + 1 for index, path in enumerate(images)}
    records = [
        compact_architecture(
            architecture,
            image_index[str(ROOT / architecture["figure"]["source_path"])],
        )
        for architecture in architectures
    ]
    return f"""You are a scientific vision annotator. For every model below, inspect its attached original-paper figure and identify the smallest rectangular crop that visibly communicates the biological/textual input object and, where present, the interface by which it enters that model.

Rules:
- Coordinates are normalized to the full attached image: x and y are the top-left; width and height are extents, all in [0,1]. Ensure x+width <= 1 and y+height <= 1.
- Keep labels, arrows, legends, or immediate model-interface elements required to interpret the input. Exclude unrelated outputs, benchmarks, training losses, performance plots, and downstream results.
- A shared image may receive different crops for different models.
- Use route evidence to decide what is relevant, but report only what is actually visible in the image.
- Mark the figure unsuitable when it does not show the model's input representation or a directly relevant input example. A valid full-image crop is allowed only when nearly every panel is required; otherwise crop tightly.
- If unsuitable, still return the best available crop, use low confidence, and set recommended_alternative_figure_index from a figure number cited by the route when one is available; otherwise null.
- Do not infer scientific content that is not visible. Do not claim hidden chain-of-thought.

The attached images are indexed in command order. Model records:
{json.dumps(records, ensure_ascii=False, indent=2)}

Return exactly one annotation for every listed model_id and no others."""


def load_crop_annotations() -> dict[str, dict[str, Any]]:
    annotations: dict[str, dict[str, Any]] = {}
    for path in sorted((OUTPUT_ROOT / "crops").glob("batch_*/response.json")):
        for annotation in json.loads(path.read_text(encoding="utf-8"))["annotations"]:
            annotations[annotation["model_id"]] = annotation
    return annotations


def load_figure_manifests() -> dict[str, list[dict[str, Any]]]:
    manifests: dict[str, list[dict[str, Any]]] = {}
    figure_root = ROOT / "data/docling_include_vlm_52_2026-07-10_nolimits/figures"
    for path in sorted(figure_root.glob("*/figures_manifest.json")):
        figures = json.loads(path.read_text(encoding="utf-8"))
        if figures:
            manifests[figures[0]["candidate_id"]] = figures
    return manifests


def target_architectures(atlas: dict[str, Any]) -> list[dict[str, Any]]:
    first_pass = load_crop_annotations()
    return [
        architecture
        for architecture in atlas["architectures"]
        if architecture["model_id"] not in first_pass
        or first_pass[architecture["model_id"]]["figure_suitability"] == "unsuitable"
    ]


def compact_figure_candidate(figure: dict[str, Any]) -> dict[str, Any]:
    descriptions = [
        item.get("text")
        for item in figure.get("annotations") or []
        if item.get("text")
    ]
    return {
        "figure_index": figure["figure_index"],
        "page_no": figure.get("page_no"),
        "caption": figure.get("caption") or "",
        "vlm_descriptions": descriptions,
    }


def figure_selection_prompt(
    architectures: list[dict[str, Any]], figures: list[dict[str, Any]]
) -> str:
    models = []
    for architecture in architectures:
        models.append(
            {
                "model_id": architecture["model_id"],
                "model_name": architecture["model_name"],
                "previous_figure_index": architecture["figure"]["figure_index"],
                "routes": compact_architecture(architecture, 0)["routes"],
            }
        )
    candidates = [compact_figure_candidate(figure) for figure in figures]
    return f"""You are selecting original-paper evidence figures for an atlas of model input representations. The previous automatic figure choice was missing or rejected by a vision reviewer.

For each model, select the single candidate figure most likely to visibly show either:
1. the concrete biological/textual object entering the model;
2. its transformation into tokens, embeddings, pixels, geometric state, or another model-visible carrier; or
3. the immediate architecture interface where that carrier enters the model.

Prefer architecture/workflow/prompt/input-example figures. Reject performance plots, loss curves, output-only results, logos, and decorative imagery. A figure may be reused for multiple model variants. Return null if none of the candidates plausibly shows the input route; never choose a decorative figure merely to fill the atlas. Use the route evidence and the figure caption/VLM description. Do not edit files and do not claim hidden chain-of-thought.

Paper: {architectures[0]['paper_title']}
Models:
{json.dumps(models, ensure_ascii=False, indent=2)}

Figure candidates:
{json.dumps(candidates, ensure_ascii=False, indent=2)}

Return exactly one selection for every model_id and no others."""


def run_reselect(max_workers: int) -> int:
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    manifests = load_figure_manifests()
    by_record: dict[str, list[dict[str, Any]]] = {}
    for architecture in target_architectures(atlas):
        by_record.setdefault(architecture["record_id"], []).append(architecture)
    root = OUTPUT_ROOT / "reselect"
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for index, (record_id, architectures) in enumerate(sorted(by_record.items())):
            name = f"paper_{index:02d}_{record_id.replace('/', '_')}"
            futures.append(
                pool.submit(
                    run_codex,
                    name=name,
                    prompt=figure_selection_prompt(architectures, manifests[record_id]),
                    images=[],
                    schema=FIGURE_SELECTION_SCHEMA,
                    output_dir=root / name,
                    timeout_seconds=2700,
                )
            )
        results = [future.result() for future in as_completed(futures)]
    write_json(root / "run_summary.json", {"results": sorted(results, key=lambda x: x["name"])})
    return 0 if all(result["status"] == "ok" for result in results) else 1


def load_reselections() -> dict[str, dict[str, Any]]:
    selections: dict[str, dict[str, Any]] = {}
    for path in sorted((OUTPUT_ROOT / "reselect").glob("paper_*/response.json")):
        for selection in json.loads(path.read_text(encoding="utf-8"))["selections"]:
            selections[selection["model_id"]] = selection
    return selections


def recrop_prompt(
    architectures: list[dict[str, Any]], images: list[Path], selections: dict[str, dict[str, Any]]
) -> str:
    image_index = {str(path): index + 1 for index, path in enumerate(images)}
    records = []
    for architecture in architectures:
        selection = selections[architecture["model_id"]]
        source_path = architecture["recrop_source_path"]
        record = compact_architecture(architecture, image_index[str(source_path)])
        record["figure_index"] = selection["figure_index"]
        record["figure_selection_rationale"] = selection["rationale"]
        records.append(record)
    return f"""You are the second-pass scientific vision annotator. A separate evidence selector has chosen a replacement original-paper figure for every model below. Inspect each attached figure and identify the smallest rectangular crop that visibly communicates the biological/textual input object and, where present, the immediate interface by which it enters that model.

Coordinates are normalized to the full image: x/y top-left and width/height extents. Keep necessary labels/arrows; exclude unrelated outputs and evaluation panels. Mark unsuitable if the replacement still does not visibly support the input route. A full-image crop is valid only when almost all content is necessary. Do not infer content that is not visible. Return exactly one annotation per model_id and no others.

Models:
{json.dumps(records, ensure_ascii=False, indent=2)}"""


def run_recrop(batch_size: int, max_workers: int) -> int:
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    manifests = load_figure_manifests()
    selections = load_reselections()
    by_id = {architecture["model_id"]: architecture for architecture in atlas["architectures"]}
    targets = []
    for model_id, selection in sorted(selections.items()):
        if selection["figure_index"] is None:
            continue
        architecture = dict(by_id[model_id])
        figure = next(
            item
            for item in manifests[architecture["record_id"]]
            if item["figure_index"] == selection["figure_index"]
        )
        architecture["recrop_source_path"] = ROOT / figure["image_path"]
        targets.append(architecture)
    batches = [targets[index:index + batch_size] for index in range(0, len(targets), batch_size)]
    root = OUTPUT_ROOT / "recrop"
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for index, batch in enumerate(batches):
            images: list[Path] = []
            seen: set[str] = set()
            for architecture in batch:
                path = architecture["recrop_source_path"]
                if str(path) not in seen:
                    images.append(path)
                    seen.add(str(path))
            name = f"batch_{index:02d}"
            futures.append(
                pool.submit(
                    run_codex,
                    name=name,
                    prompt=recrop_prompt(batch, images, selections),
                    images=images,
                    schema=CROP_SCHEMA,
                    output_dir=root / name,
                    timeout_seconds=2700,
                )
            )
        results = [future.result() for future in as_completed(futures)]
    write_json(root / "run_summary.json", {"results": sorted(results, key=lambda x: x["name"])})
    return 0 if all(result["status"] == "ok" for result in results) else 1


def run_planning(max_workers: int) -> int:
    root = OUTPUT_ROOT / "planning"
    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for role, role_prompt in PLANNING_ROLES.items():
            tasks.append(
                pool.submit(
                    run_codex,
                    name=role,
                    prompt=planning_prompt(role_prompt),
                    images=[],
                    schema=PLANNING_SCHEMA,
                    output_dir=root / role,
                    timeout_seconds=2700,
                )
            )
        results = [future.result() for future in as_completed(tasks)]
    write_json(root / "run_summary.json", {"results": sorted(results, key=lambda x: x["name"])})
    return 0 if all(result["status"] == "ok" for result in results) else 1


def run_crops(batch_size: int, max_workers: int) -> int:
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    architectures = atlas["architectures"]
    batches = [architectures[index:index + batch_size] for index in range(0, len(architectures), batch_size)]
    root = OUTPUT_ROOT / "crops"
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for index, batch in enumerate(batches):
            images = []
            seen = set()
            for architecture in batch:
                path = ROOT / architecture["figure"]["source_path"]
                if str(path) not in seen:
                    images.append(path)
                    seen.add(str(path))
            name = f"batch_{index:02d}"
            futures.append(
                pool.submit(
                    run_codex,
                    name=name,
                    prompt=crop_prompt(batch, images),
                    images=images,
                    schema=CROP_SCHEMA,
                    output_dir=root / name,
                    timeout_seconds=2700,
                )
            )
        results = [future.result() for future in as_completed(futures)]
    write_json(root / "run_summary.json", {"results": sorted(results, key=lambda x: x["name"])})
    return 0 if all(result["status"] == "ok" for result in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("planning", "crops", "reselect", "recrop"))
    parser.add_argument("--batch-size", type=int, default=7)
    parser.add_argument("--max-workers", type=int, default=8)
    args = parser.parse_args()
    if args.mode == "planning":
        return run_planning(min(args.max_workers, len(PLANNING_ROLES)))
    if args.mode == "crops":
        return run_crops(args.batch_size, args.max_workers)
    if args.mode == "reselect":
        return run_reselect(args.max_workers)
    return run_recrop(args.batch_size, args.max_workers)


if __name__ == "__main__":
    raise SystemExit(main())
