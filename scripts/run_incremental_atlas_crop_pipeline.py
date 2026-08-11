#!/usr/bin/env python3
"""Select and crop source-paper figures for newly classified atlas models."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SELECTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["decision", "figure_index", "route_ids_supported", "rationale", "confidence"],
    "properties": {
        "decision": {"type": "string", "enum": ["select_figure", "no_suitable_figure"]},
        "figure_index": {"type": ["integer", "null"]},
        "route_ids_supported": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
}

CROP_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "crop_box", "panel_label", "visible_input_object", "visible_model_interface",
        "route_ids_supported", "rationale", "confidence",
    ],
    "properties": {
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
        "route_ids_supported": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        },
        "rationale": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe(value: str) -> str:
    readable = "".join(char if char.isalnum() or char in "._-" else "_" for char in value)[:120]
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{readable}_{digest}"


def canonical_profile_manifest(corpus_root: Path) -> Path:
    path = corpus_root / "manifests/canonical_docling_profile_manifest.csv"
    if not path.is_file():
        raise RuntimeError(f"Crop validation requires a canonical Docling profile manifest: {path}")
    return path


def load_figures_by_record(corpus_root: Path) -> dict[str, list[dict[str, Any]]]:
    """Bind native figure manifests through the profile manifest, not filename guesses."""
    profiles = read_csv(canonical_profile_manifest(corpus_root))
    complete = [row for row in profiles if row.get("profile_status") == "complete"]
    profile_by_candidate = {str(row.get("candidate_id") or ""): row for row in complete}
    if "" in profile_by_candidate or len(profile_by_candidate) != len(complete):
        raise RuntimeError("Canonical Docling profile manifest has duplicate or empty candidate_id values")
    figures_by_record: dict[str, list[dict[str, Any]]] = {}
    for candidate_id, profile in profile_by_candidate.items():
        figures_path = Path(str(profile.get("figures_manifest") or ""))
        if not figures_path.is_absolute():
            figures_path = ROOT / figures_path
        if not figures_path.is_file():
            raise RuntimeError(f"Profile figures manifest is missing for {candidate_id}: {figures_path}")
        figures = read_json(figures_path)
        for figure in figures:
            if str(figure.get("candidate_id") or "") != candidate_id:
                raise RuntimeError(f"Figure manifest candidate_id mismatch in {figures_path}")
        record_ids = {candidate_id, str(profile.get("source_record_id") or "")}
        for record_id in record_ids - {""}:
            figures_by_record.setdefault(record_id, []).extend(figures)
    return figures_by_record


def run_logged(command: list[str], output_dir: Path, stdin: str | None = None, timeout: int = 2700) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    result = subprocess.run(
        command,
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
        timeout=timeout,
        env={**os.environ, "NO_COLOR": "1"},
    )
    (output_dir / "stdout.log").write_text(result.stdout, encoding="utf-8")
    (output_dir / "stderr.log").write_text(result.stderr, encoding="utf-8")
    write_json(
        output_dir / "metadata.json",
        {
            "created": now_iso(),
            "command": command,
            "returncode": result.returncode,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        },
    )
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}")


def codex_json(
    *, prompt: str, schema: dict[str, Any], images: list[Path], model: str,
    output_dir: Path, timeout: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    schema_path = output_dir / "schema.json"
    response_path = output_dir / "response.json"
    prompt_path = output_dir / "prompt.txt"
    write_json(schema_path, schema)
    prompt_path.write_text(prompt.rstrip() + "\n", encoding="utf-8")
    command = [
        "codex", "-a", "never", "exec", "--model", model, "--cd", str(ROOT),
        "--sandbox", "read-only", "--ignore-user-config", "--ignore-rules",
        "--ephemeral", "--output-schema", str(schema_path),
        "--output-last-message", str(response_path),
    ]
    for image in images:
        command.extend(["--image", str(image)])
    command.append("-")
    run_logged(command, output_dir, stdin=prompt, timeout=timeout)
    if not response_path.exists():
        raise RuntimeError(f"Codex produced no structured response in {output_dir}")
    return read_json(response_path)


def image_size(path: Path) -> tuple[int, int]:
    result = subprocess.run(
        ["magick", "identify", "-format", "%w %h", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    width, height = result.stdout.strip().split()
    return int(width), int(height)


def contact_sheet_font() -> Path:
    configured = os.environ.get("CONTACT_SHEET_FONT")
    candidates = [
        Path(configured) if configured else None,
        Path("/System/Library/Fonts/HelveticaNeue.ttc"),
        Path("/System/Library/Fonts/LucidaGrande.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise RuntimeError(
        "No contact-sheet font found. Set CONTACT_SHEET_FONT to a readable TTF, TTC, or OTF file."
    )


def build_contact_sheet(
    model_id: str, figures: list[dict[str, Any]], output_root: Path
) -> Path:
    model_root = output_root / "contact_sheets" / safe(model_id)
    tiles = model_root / "tiles"
    if model_root.exists():
        shutil.rmtree(model_root)
    tiles.mkdir(parents=True)
    font = contact_sheet_font()
    tile_paths = []
    for figure in sorted(figures, key=lambda item: int(item["figure_index"])):
        source = ROOT / figure["image_path"]
        target = tiles / f"figure_{int(figure['figure_index']):03d}.jpg"
        command = [
            "magick", str(source), "-thumbnail", "760x480>", "-background", "white",
            "-gravity", "center", "-extent", "780x540", "-font", str(font), "-fill", "#111111",
            "-pointsize", "28", "-gravity", "southwest", "-annotate", "+16+12",
            f"Figure {int(figure['figure_index'])}", "-quality", "92", str(target),
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        tile_paths.append(target)
    contact = model_root / "all_figures.jpg"
    subprocess.run(
        [
            "magick", "montage", "-font", str(font), *map(str, tile_paths), "-tile", "3x", "-geometry",
            "+12+12", "-background", "white", "-quality", "92", str(contact),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return contact


def compact_routes(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields = [
        "route_id", "route_label", "lifecycle_phase", "task_or_configuration_verbatim",
        "source_object_verbatim", "transformation_chain_verbatim",
        "model_visible_form_verbatim", "carrier_family", "carrier_subtype",
        "insertion_or_fusion_verbatim", "evidence_quote", "section_heading",
        "supporting_figure_or_table",
    ]
    return [{field: route.get(field) for field in fields} for route in routes]


def figure_context(figures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
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
    ]


def validate_selection(
    decision: dict[str, Any], valid_figure_indices: set[int], valid_route_ids: set[str]
) -> None:
    supported = set(decision.get("route_ids_supported") or [])
    if not supported <= valid_route_ids:
        raise RuntimeError(
            f"Figure decision cites unknown routes: {sorted(supported - valid_route_ids)}"
        )
    if decision.get("decision") == "select_figure":
        if decision.get("figure_index") is None:
            raise RuntimeError("Figure decision selected a figure without figure_index")
        if int(decision["figure_index"]) not in valid_figure_indices:
            raise RuntimeError(f"Figure decision selected an unknown index: {decision['figure_index']}")
        if not supported:
            raise RuntimeError("A selected figure must support at least one grounded route")
    elif decision.get("figure_index") is not None:
        raise RuntimeError("no_suitable_figure must not carry a figure_index")


def selection_prompt(role: str, model: dict[str, Any], figures: list[dict[str, Any]]) -> str:
    emphasis = (
        "Prioritize sufficiency: the selected figure must visibly establish at least one "
        "actual source-to-model input route."
        if role == "sufficiency_selector"
        else "Prioritize specificity: reject output-only, benchmark, generic data-summary, "
        "or architecture figures that do not visibly show the stated model input/interface."
    )
    return f"""You are the {role} in a blind scientific-figure selection pass.

{emphasis}
The attached contact sheet contains every extracted source-paper figure, labelled by
figure_index. Select one figure only if it visibly shows a grounded source object,
transformation, model-visible carrier, or immediate insertion/fusion interface for at
least one listed route. A VLM description can help locate a figure but is not evidence
by itself. Otherwise return no_suitable_figure. Do not provide hidden chain-of-thought;
return only concise visible-evidence justification in the required JSON.

Model and grounded routes:
{json.dumps(model, ensure_ascii=False)}

Figure captions and native VLM descriptions:
{json.dumps(figure_context(figures), ensure_ascii=False)}
"""


def adjudication_prompt(
    model: dict[str, Any], figures: list[dict[str, Any]], decisions: list[dict[str, Any]]
) -> str:
    return f"""Adjudicate two blind source-figure selections for one model.

Return to the attached complete contact sheet and the grounded route evidence. Select a
figure only when its visible content supports an actual input route or immediate model
interface; reject outputs, benchmarks, decorative images, and merely generic diagrams.
Do not decide by majority alone. Return concise evidence, not hidden chain-of-thought.

Model and routes:
{json.dumps(model, ensure_ascii=False)}

Figure metadata:
{json.dumps(figure_context(figures), ensure_ascii=False)}

Blind decisions:
{json.dumps(decisions, ensure_ascii=False)}
"""


def crop_prompt(model: dict[str, Any], figure: dict[str, Any]) -> str:
    return f"""Crop the attached source-paper figure for a scientific taxonomy atlas.

Return the smallest coherent normalized crop that keeps readable labels and arrows needed
to understand at least one grounded actual input route: source object, transformation,
model-visible carrier, or immediate insertion/fusion interface. Exclude output-only and
irrelevant panels. Coordinates are relative to the full attached image; require x+width
<=1 and y+height<=1. Return concise visible evidence, not hidden chain-of-thought.

Model and routes:
{json.dumps(model, ensure_ascii=False)}

Selected figure metadata:
{json.dumps(figure_context([figure])[0], ensure_ascii=False)}
"""


def process_model(
    model_id: str, routes: list[dict[str, Any]], figures: list[dict[str, Any]],
    output_root: Path, model_name: str, timeout: int,
) -> dict[str, Any]:
    first = routes[0]
    context = {
        "model_id": model_id,
        "model_name": first.get("model_name"),
        "record_id": first.get("record_id"),
        "paper_title": first.get("title"),
        "routes": compact_routes(routes),
    }
    model_root = output_root / "models" / safe(model_id)
    if not figures:
        return {
            "model_id": model_id,
            "record_id": first["record_id"],
            "status": "no_suitable_figure",
            "figure": None,
            "crop_box": None,
            "panel_label": "",
            "visible_input_object": "",
            "visible_model_interface": "",
            "figure_suitability": "unsuitable",
            "confidence": "high",
            "rationale": "The native Docling profile contains no extracted source-paper figures.",
            "annotation_pass": "two_blind_selectors_plus_adjudicator_and_cropper",
        }
    contact = build_contact_sheet(model_id, figures, output_root)
    valid_indices = {int(figure["figure_index"]) for figure in figures}
    valid_route_ids = {str(route["route_id"]) for route in routes}
    selections = []
    for role in ("sufficiency_selector", "specificity_selector"):
        selection = codex_json(
            prompt=selection_prompt(role, context, figures),
            schema=SELECTION_SCHEMA,
            images=[contact],
            model=model_name,
            output_dir=model_root / role,
            timeout=timeout,
        )
        validate_selection(selection, valid_indices, valid_route_ids)
        selections.append({"role": role, **selection})
    decision = codex_json(
        prompt=adjudication_prompt(context, figures, selections),
        schema=SELECTION_SCHEMA,
        images=[contact],
        model=model_name,
        output_dir=model_root / "adjudicator",
        timeout=timeout,
    )
    validate_selection(decision, valid_indices, valid_route_ids)
    if decision["decision"] == "no_suitable_figure":
        return {
            "model_id": model_id,
            "record_id": first["record_id"],
            "status": "no_suitable_figure",
            "figure": None,
            "crop_box": None,
            "panel_label": "",
            "visible_input_object": "",
            "visible_model_interface": "",
            "figure_suitability": "unsuitable",
            "confidence": decision["confidence"],
            "rationale": decision["rationale"],
            "annotation_pass": "two_blind_selectors_plus_adjudicator_and_cropper",
            "selection_decisions": selections,
            "adjudication": decision,
        }
    figure_index = int(decision["figure_index"])
    if figure_index not in valid_indices:
        raise RuntimeError(f"Invalid selected figure {figure_index} for {model_id}")
    figure = next(item for item in figures if int(item["figure_index"]) == figure_index)
    source = ROOT / figure["image_path"]
    crop = codex_json(
        prompt=crop_prompt(context, figure),
        schema=CROP_SCHEMA,
        images=[source],
        model=model_name,
        output_dir=model_root / "cropper",
        timeout=timeout,
    )
    crop_route_id_list = crop["route_ids_supported"]
    crop_route_ids = set(crop_route_id_list)
    if len(crop_route_ids) != len(crop_route_id_list):
        raise RuntimeError(f"Crop cites duplicate route IDs for {model_id}")
    if not crop_route_ids <= valid_route_ids:
        raise RuntimeError(
            f"Crop cites unknown routes: {sorted(crop_route_ids - valid_route_ids)}"
        )
    box = crop["crop_box"]
    if box["x"] + box["width"] > 1.000001 or box["y"] + box["height"] > 1.000001:
        raise RuntimeError(f"Invalid crop bounds for {model_id}: {box}")
    width, height = image_size(source)
    return {
        "model_id": model_id,
        "record_id": first["record_id"],
        "status": "cropped_source_figure",
        "figure": {
            "figure_index": figure_index,
            "image_path": figure["image_path"],
            "pixel_width": width,
            "pixel_height": height,
            "caption": figure.get("caption") or "",
            "page_no": figure.get("page_no"),
        },
        "crop_box": box,
        "panel_label": crop["panel_label"],
        "visible_input_object": crop["visible_input_object"],
        "visible_model_interface": crop["visible_model_interface"],
        "figure_suitability": "suitable",
        "confidence": crop["confidence"],
        "rationale": crop["rationale"],
        "annotation_pass": "two_blind_selectors_plus_adjudicator_and_cropper",
        "route_ids_supported": crop["route_ids_supported"],
        "selection_decisions": selections,
        "adjudication": decision,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxonomy-root", type=Path, required=True)
    parser.add_argument("--corpus-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=2700)
    parser.add_argument(
        "--exclude-model-ledger",
        type=Path,
        help="Prior crop ledger; models already dispositioned there are not re-annotated.",
    )
    args = parser.parse_args()
    if shutil.which("magick") is None:
        raise RuntimeError("ImageMagick `magick` is required for complete contact sheets")

    routes = read_jsonl(args.taxonomy_root / "route_annotations.jsonl")
    excluded_model_ids: set[str] = set()
    if args.exclude_model_ledger:
        excluded_model_ids = {
            str(row.get("model_id"))
            for row in read_json(args.exclude_model_ledger)
            if row.get("model_id")
        }
    routes_by_model: dict[str, list[dict[str, Any]]] = {}
    for route in routes:
        if route["model_id"] in excluded_model_ids:
            continue
        routes_by_model.setdefault(route["model_id"], []).append(route)
    figures_by_record = load_figures_by_record(args.corpus_root)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results, errors = [], []
    with ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as pool:
        futures = {
            pool.submit(
                process_model,
                model_id,
                model_routes,
                figures_by_record.get(model_routes[0]["record_id"], []),
                args.output_dir,
                args.model,
                args.timeout,
            ): model_id
            for model_id, model_routes in routes_by_model.items()
        }
        for future in as_completed(futures):
            model_id = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(json.dumps({"model_id": model_id, "status": result["status"]}), flush=True)
            except Exception as exc:
                errors.append({"model_id": model_id, "error": repr(exc)})
                print(json.dumps({"model_id": model_id, "status": "error", "error": repr(exc)}), flush=True)
    results.sort(key=lambda item: item["model_id"])
    write_json(args.output_dir / "crop_ledger.json", results)
    write_json(
        args.output_dir / "run_summary.json",
        {
            "created": now_iso(),
            "model": args.model,
            "models_expected": len(routes_by_model),
            "prior_models_skipped": len(
                {row["model_id"] for row in routes} & excluded_model_ids
            ),
            "models_completed": len(results),
            "cropped_source_figure": sum(item["status"] == "cropped_source_figure" for item in results),
            "no_suitable_figure": sum(item["status"] == "no_suitable_figure" for item in results),
            "errors": errors,
        },
    )
    return 0 if not errors and len(results) == len(routes_by_model) else 2


if __name__ == "__main__":
    raise SystemExit(main())
