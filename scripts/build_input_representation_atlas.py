#!/usr/bin/env python3
"""Build the static input-representation taxonomy atlas and its evidence data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_ROOT = ROOT / "data/input_representation_taxonomy_2026-07-11"
CORPUS_ROOT = ROOT / "data/docling_include_vlm_52_2026-07-10_nolimits"
DEFAULT_OUTPUT = ROOT / "docs/input-representation-atlas"
CROP_LEDGER = (
    ROOT
    / "data/input_representation_atlas_crop_crossvalidation_2026-07-12/final_crossvalidated_crop_ledger.json"
)

FAMILY_META = {
    "text_native_token_stream": {
        "code": "F1",
        "label": "Text-native token streams",
        "short": "Lexical",
        "color": "#bd3150",
    },
    "discrete_biological_symbol_stream": {
        "code": "F2",
        "label": "Discrete biological symbol streams",
        "short": "Discrete bio",
        "color": "#13856f",
    },
    "dense_continuous_carrier": {
        "code": "F3",
        "label": "Dense continuous carriers",
        "short": "Continuous",
        "color": "#2d63a7",
    },
    "visual_raster_carrier": {
        "code": "F4",
        "label": "Visual raster carriers",
        "short": "Visual",
        "color": "#c66a12",
    },
    "geometric_or_diffusion_state_carrier": {
        "code": "F5",
        "label": "Geometric and diffusion-state carriers",
        "short": "Geometric",
        "color": "#7450a8",
    },
}

FAMILY_CODE_TO_ID = {
    meta["code"]: family_id for family_id, meta in FAMILY_META.items()
}

LEAF_CODE_TO_SUBTYPE = {
    "F1.L1": "plain_language_prompt_or_question",
    "F1.L2": "structured_biological_prompt_or_task_scaffold",
    "F1.L3": "serialized_biological_context_or_ordered_profile",
    "F2.L1": "native_biological_token_stream",
    "F2.L2": "multi_track_structural_symbol_stream",
    "F2.L3": "learned_quantized_id_or_codebook_token",
    "F3.L1": "direct_projected_embedding",
    "F3.L2": "virtual_token_prefix",
    "F3.L3": "connector_mediated_embedding",
    "F3.L4": "pooled_or_aggregated_embedding",
    "F4.L1": "raw_slide_or_patch_input",
    "F4.L2": "patch_context_or_case_level_visual_reasoning",
    "F5.L1": "noisy_diffusion_state",
    "F5.L2": "coordinate_backbone_or_shape_conditioning",
    "F5.L3": "symbolic_structural_constraint",
}

SUBTYPE_EXAMPLES = {
    "plain_language_prompt_or_question": {
        "input": "What phenotype does this cell exhibit?",
        "carrier": "[What] [phenotype] [does] [this] [cell] ...",
        "model": "ordinary tokenizer → LLM",
        "note": "Natural-language instructions or questions remain ordinary lexical tokens.",
    },
    "structured_biological_prompt_or_task_scaffold": {
        "input": "<TASK:cell_type> genes: IL7R, LTB, MALAT1",
        "carrier": "task tag + labeled biological fields",
        "model": "template tokenizer → LLM",
        "note": "A controlled scaffold tells the model what biological operation to perform.",
    },
    "serialized_biological_context_or_ordered_profile": {
        "input": "GAPDH|8.2; ACTB|7.9; IL7R|6.4; ...",
        "carrier": "ordered textual cell/profile sentence",
        "model": "serializer → tokenizer → LLM",
        "note": "A biological vector or set is deterministically rendered as ordered text.",
    },
    "native_biological_token_stream": {
        "input": "A C G T G C A ...",
        "carrier": "native nucleotide/amino-acid token IDs",
        "model": "biological tokenizer → generator",
        "note": "The biological alphabet itself forms the discrete sequence consumed by the model.",
    },
    "multi_track_structural_symbol_stream": {
        "input": "AA: M K T ...   SS: H H C ...",
        "carrier": "aligned sequence + structure tracks",
        "model": "multi-track tokenizer → generator",
        "note": "Several synchronized symbolic tracks encode sequence and structure together.",
    },
    "learned_quantized_id_or_codebook_token": {
        "input": "continuous biology → quantizer",
        "carrier": "[BIO_187] [BIO_042] [BIO_913]",
        "model": "VQ/RVQ codebook IDs → generator",
        "note": "A learned codebook turns continuous biological states into discrete IDs.",
    },
    "direct_projected_embedding": {
        "input": "RNA vector x ∈ ℝᵍ",
        "carrier": "Wproj x = [0.14, −0.82, 0.31, ...]",
        "model": "projected vectors → generative backbone",
        "note": "An external biological representation is linearly or nonlinearly projected into model space.",
    },
    "virtual_token_prefix": {
        "input": "cell embedding + prompt",
        "carrier": "<bio₁> <bio₂> ... <bioₖ> [prompt tokens]",
        "model": "soft prefix → LLM stream",
        "note": "Continuous vectors occupy token-like prefix positions without ordinary token IDs.",
    },
    "connector_mediated_embedding": {
        "input": "image / omics encoder states",
        "carrier": "Q-Former or adapter query vectors",
        "model": "connector → LLM cross-modal interface",
        "note": "A learned connector selects or transforms encoder states before language generation.",
    },
    "pooled_or_aggregated_embedding": {
        "input": "{gene/cell/patch embeddings}",
        "carrier": "mean/attention pool = one compact vector",
        "model": "aggregator → generator",
        "note": "Many local states are summarized before they reach the generative component.",
    },
    "raw_slide_or_patch_input": {
        "input": "whole-slide image",
        "carrier": "224×224 RGB tissue patches",
        "model": "patch encoder → multimodal generator",
        "note": "Pixels or image patches are the model-facing carrier.",
    },
    "patch_context_or_case_level_visual_reasoning": {
        "input": "ROI + neighboring patches + case context",
        "carrier": "ordered visual token bank",
        "model": "context aggregator → multimodal LLM",
        "note": "Visual evidence is organized across regions or slides before reasoning.",
    },
    "noisy_diffusion_state": {
        "input": "biological state x₀ + noise ε",
        "carrier": "xₜ = √αₜx₀ + √(1−αₜ)ε",
        "model": "conditioned denoiser / flow model",
        "note": "The generator consumes an evolving noisy state rather than a token stream.",
    },
    "coordinate_backbone_or_shape_conditioning": {
        "input": "residue/atom coordinates (xᵢ,yᵢ,zᵢ)",
        "carrier": "equivariant geometric state",
        "model": "geometry-aware generator",
        "note": "Coordinates, backbones, or explicit shapes condition generation directly.",
    },
    "symbolic_structural_constraint": {
        "input": "motif anchors + distance constraints",
        "carrier": "symbolic geometry/structure constraints",
        "model": "constraint-conditioned generator",
        "note": "Explicit structural rules constrain what the model may generate.",
    },
}

STOPWORDS = {
    "model", "input", "data", "text", "image", "sequence", "embedding",
    "embeddings", "generation", "prediction", "analysis", "task", "route",
    "for", "with", "from", "into", "the", "and", "via", "using",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tokens(value: Any) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", str(value or "").casefold())
        if len(token) > 2 and token not in STOPWORDS
    }


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def resolve_source_image(value: str, artifact_roots: list[Path]) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    candidates = [ROOT / path, *((root / path) for root in artifact_roots)]
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[0])


def collection_metadata(record_id: str) -> dict[str, str]:
    """Recover the immutable review iteration encoded in canonical record IDs."""
    batch_id = record_id.split("__", 1)[0]
    match = re.search(r"(\d{4}-\d{2}-\d{2})$", batch_id)
    if not match:
        raise ValueError(f"Record ID does not encode a collection date: {record_id}")
    collection_date = match.group(1)
    date.fromisoformat(collection_date)
    return {"batch_id": batch_id, "date": collection_date}


def figure_text(figure: dict[str, Any]) -> str:
    annotations = " ".join(
        str(item.get("text") or "") for item in figure.get("annotations") or []
    )
    return f"{figure.get('caption') or ''} {annotations}".strip()


def choose_figure(
    routes: list[dict[str, Any]], figures: list[dict[str, Any]]
) -> tuple[dict[str, Any], int, list[str]]:
    model_name = routes[0]["model_name"]
    model_tokens = tokens(model_name)
    ranked = []
    for figure in figures:
        text = figure_text(figure)
        text_tokens = tokens(text)
        lowered = text.casefold()
        score = 0
        reasons = []
        if model_name.casefold() in lowered:
            score += 80
            reasons.append("model name appears in figure text")
        overlap = len(model_tokens & text_tokens)
        if overlap:
            score += 12 * overlap
            reasons.append(f"{overlap} model-name tokens match")
        for route in routes:
            cited_numbers = {
                int(value)
                for value in re.findall(
                    r"(?i)(?:fig(?:ure)?\.?\s*)(\d+)",
                    str(route.get("supporting_figure_or_table") or ""),
                )
            }
            if figure["figure_index"] in cited_numbers:
                score += 35
                reasons.append("route cites this figure number")
            route_tokens = tokens(
                " ".join(
                    str(route.get(field) or "")
                    for field in (
                        "route_label",
                        "source_object_verbatim",
                        "model_visible_form_verbatim",
                        "insertion_or_fusion_verbatim",
                    )
                )
            )
            score += min(12, len(route_tokens & text_tokens))
        if any(
            term in lowered
            for term in ("architecture", "framework", "workflow", "schematic", "overview")
        ):
            score += 8
            reasons.append("architecture/workflow figure")
        ranked.append((score, -int(figure["figure_index"]), figure, sorted(set(reasons))))
    if not ranked:
        raise RuntimeError(f"No source-paper figures for {routes[0]['record_id']}")
    score, _, figure, reasons = max(ranked, key=lambda item: item[:2])
    return figure, score, reasons


def compact_route(route: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "route_id", "configuration_id", "route_label", "lifecycle_phase",
        "task_or_configuration_verbatim", "source_object_verbatim",
        "source_object_normalized", "source_modality_normalized",
        "transformation_chain_verbatim", "model_visible_form_verbatim",
        "carrier_family", "carrier_subtype", "insertion_or_fusion_verbatim",
        "fusion_topology", "text_role", "input_status", "evidence_quote",
        "section_heading", "supporting_figure_or_table", "evidence_status",
        "uncertainty", "pages", "doc_item_refs", "source_candidate_refs",
        "dense_candidate_refs", "final_grounding_valid",
    )
    return {field: route.get(field) for field in fields}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--taxonomy-root", type=Path, default=TAXONOMY_ROOT)
    parser.add_argument(
        "--corpus-root",
        type=Path,
        action="append",
        default=[],
        help="Docling corpus root containing figures/; repeat for living snapshots.",
    )
    parser.add_argument("--crop-ledger", type=Path, default=CROP_LEDGER)
    parser.add_argument(
        "--artifact-root",
        type=Path,
        action="append",
        default=[],
        help="Additional root for repository-relative Docling figure paths.",
    )
    parser.add_argument(
        "--prior-atlas-root",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Reuse already validated baseline crop assets when recovered source figures are absent.",
    )
    args = parser.parse_args()
    output = args.output_dir.resolve()
    taxonomy_root = args.taxonomy_root.resolve()
    corpus_roots = [path.resolve() for path in args.corpus_root] or [CORPUS_ROOT]
    crop_ledger_path = args.crop_ledger.resolve()
    artifact_roots = [path.resolve() for path in args.artifact_root]
    prior_atlas_root = args.prior_atlas_root.resolve()
    prior_architectures: dict[str, dict[str, Any]] = {}
    prior_atlas_path = prior_atlas_root / "data/atlas.json"
    if prior_atlas_path.exists() and prior_atlas_root != output:
        prior_architectures = {
            row["model_id"]: row for row in read_json(prior_atlas_path).get("architectures", [])
        }
        for relative in (
            ".nojekyll",
            "index.html",
            "README.md",
            "QA.md",
            "assets/app.js",
            "assets/styles.css",
            "assets/social-preview.png",
        ):
            source = prior_atlas_root / relative
            if source.is_file():
                target = output / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    assets = output / "assets/figures"
    if assets.exists():
        shutil.rmtree(assets)
    assets.mkdir(parents=True, exist_ok=True)

    routes = [
        json.loads(line)
        for line in (taxonomy_root / "route_annotations.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    taxonomy = read_json(taxonomy_root / "taxonomy_tree.json")
    crop_ledger = {
        item["model_id"]: item for item in read_json(crop_ledger_path)
    }
    with (taxonomy_root / "study_model_registry.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        registry = {row["record_id"]: row for row in csv.DictReader(stream)}

    figures_by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for corpus_root in corpus_roots:
        for manifest_path in sorted((corpus_root / "figures").glob("*/figures_manifest.json")):
            for figure in read_json(manifest_path):
                figures_by_record[figure["candidate_id"]].append(figure)

    routes_by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for route in routes:
        routes_by_model[route["model_id"]].append(route)

    copied: dict[str, str] = {}
    architectures = []
    for model_id, model_routes in sorted(
        routes_by_model.items(),
        key=lambda item: (item[1][0]["model_name"].casefold(), item[0]),
    ):
        first = model_routes[0]
        record_id = first["record_id"]
        crop_annotation = crop_ledger[model_id]
        figure_payload = None
        if crop_annotation["status"] == "cropped_source_figure":
            crop_figure = crop_annotation["figure"]
            figure = next(
                (
                    item
                    for item in figures_by_record[record_id]
                    if int(item["figure_index"]) == int(crop_figure["figure_index"])
                ),
                None,
            )
            prior_figure = (prior_architectures.get(model_id) or {}).get("figure")
            if figure is not None:
                source_image = resolve_source_image(figure["image_path"], artifact_roots)
                if not source_image.is_file() and prior_figure and prior_figure.get("asset"):
                    source_image = prior_atlas_root / prior_figure["asset"]
            elif prior_figure and prior_figure.get("asset"):
                source_image = prior_atlas_root / prior_figure["asset"]
            else:
                raise RuntimeError(
                    f"Missing source and validated prior crop asset for {model_id}"
                )
            if not source_image.exists():
                raise RuntimeError(f"Missing figure image: {source_image}")
            source_key = str(source_image.resolve())
            if source_key not in copied:
                filename = (
                    f"{slug(record_id)}_figure_{int(crop_figure['figure_index']):03d}"
                    f"{source_image.suffix.casefold()}"
                )
                target = assets / filename
                shutil.copy2(source_image, target)
                copied[source_key] = f"assets/figures/{filename}"
            description = (
                next(
                    (
                        item.get("text")
                        for item in figure.get("annotations") or []
                        if item.get("kind") == "description" and item.get("text")
                    ),
                    "",
                )
                if figure is not None
                else str(prior_figure.get("description") or "")
            )
            figure_payload = {
                "status": crop_annotation["status"],
                "asset": copied[source_key],
                "source_path": (
                    figure["image_path"] if figure is not None else prior_figure.get("source_path", "")
                ),
                "figure_index": int(crop_figure["figure_index"]),
                "caption": (
                    figure.get("caption") or "" if figure is not None else prior_figure.get("caption", "")
                ),
                "description": description or "",
                "page_no": figure.get("page_no") if figure is not None else prior_figure.get("page_no"),
                "sha256": hashlib.sha256(source_image.read_bytes()).hexdigest(),
                "pixel_width": crop_figure["pixel_width"],
                "pixel_height": crop_figure["pixel_height"],
                "crop_box": crop_annotation["crop_box"],
                "panel_label": crop_annotation["panel_label"],
                "visible_input_object": crop_annotation["visible_input_object"],
                "visible_model_interface": crop_annotation["visible_model_interface"],
                "suitability": crop_annotation["figure_suitability"],
                "confidence": crop_annotation["confidence"],
                "rationale": crop_annotation["rationale"],
                "annotation_pass": crop_annotation["annotation_pass"],
            }
        record = registry[record_id]
        collection = collection_metadata(record_id)
        family_counts = Counter(route["carrier_family"] for route in model_routes)
        subtype_counts = Counter(route["carrier_subtype"] for route in model_routes)
        primary_subtype = max(
            subtype_counts,
            key=lambda key: (subtype_counts[key], key),
        )
        illustrative_examples = []
        for subtype_id in sorted(subtype_counts):
            representative = next(
                route for route in model_routes if route["carrier_subtype"] == subtype_id
            )
            example = SUBTYPE_EXAMPLES[subtype_id]
            illustrative_examples.append(
                {
                    "subtype_id": subtype_id,
                    "family_id": representative["carrier_family"],
                    "route_id": representative["route_id"],
                    "example_input": example["input"],
                    "example_carrier": example["carrier"],
                    "example_interface": example["model"],
                    "actual_source": representative["source_object_verbatim"],
                    "actual_model_visible_form": representative["model_visible_form_verbatim"],
                }
            )
        architectures.append(
            {
                "model_id": model_id,
                "model_name": first["model_name"],
                "record_id": record_id,
                "collection_batch_id": collection["batch_id"],
                "collection_date": collection["date"],
                "review_iteration": collection["date"],
                "study_id": first["study_id"],
                "paper_title": first["title"],
                "doi": record.get("doi") or "",
                "paper_url": (
                    f"https://doi.org/{record['doi']}" if record.get("doi") else ""
                ),
                "route_count": len(model_routes),
                "configuration_count": len(
                    {route["configuration_id"] for route in model_routes}
                ),
                "family_counts": dict(family_counts),
                "subtype_counts": dict(subtype_counts),
                "families": sorted(family_counts, key=lambda key: FAMILY_META[key]["code"]),
                "subtypes": sorted(subtype_counts),
                "primary_subtype": primary_subtype,
                "modalities": sorted(
                    {route["source_modality_normalized"] for route in model_routes}
                ),
                "lifecycle_phases": sorted(
                    {route["lifecycle_phase"] for route in model_routes}
                ),
                "fusion_topologies": sorted(
                    {route["fusion_topology"] for route in model_routes}
                ),
                "text_roles": sorted({route["text_role"] for route in model_routes}),
                "figure": figure_payload,
                "figure_status": crop_annotation["status"],
                "no_figure_rationale": (
                    crop_annotation["rationale"] if figure_payload is None else ""
                ),
                "illustrative_examples": illustrative_examples,
                "routes": [compact_route(route) for route in model_routes],
            }
        )

    family_counts = Counter(route["carrier_family"] for route in routes)
    family_models: dict[str, set[str]] = defaultdict(set)
    subtype_counts = Counter(route["carrier_subtype"] for route in routes)
    subtype_models: dict[str, set[str]] = defaultdict(set)
    for route in routes:
        family_models[route["carrier_family"]].add(route["model_id"])
        subtype_models[route["carrier_subtype"]].add(route["model_id"])

    record_collection_dates = {
        record_id: collection_metadata(record_id)["date"] for record_id in registry
    }
    collection_batches = []
    for collection_date in sorted(set(record_collection_dates.values()), reverse=True):
        batch_record_ids = {
            record_id
            for record_id, value in record_collection_dates.items()
            if value == collection_date
        }
        batch_architectures = [
            architecture
            for architecture in architectures
            if architecture["collection_date"] == collection_date
        ]
        collection_batches.append(
            {
                "iteration_id": f"review_iteration_{collection_date}",
                "date": collection_date,
                "record_count": len(batch_record_ids),
                "record_ids": sorted(batch_record_ids),
                "model_count": len(batch_architectures),
                "route_count": sum(item["route_count"] for item in batch_architectures),
            }
        )

    taxonomy_families = []
    for family in taxonomy["families"]:
        family_code = family["family_id"]
        family_id = FAMILY_CODE_TO_ID[family_code]
        subtypes = []
        for subtype in family["leaves"]:
            subtype_id = LEAF_CODE_TO_SUBTYPE[subtype["leaf_id"]]
            subtypes.append(
                {
                    **subtype,
                    "subtype_id": subtype_id,
                    "route_count": subtype_counts[subtype_id],
                    "model_count": len(subtype_models[subtype_id]),
                    "example": SUBTYPE_EXAMPLES[subtype_id],
                }
            )
        taxonomy_families.append(
            {
                **family,
                **FAMILY_META[family_id],
                "family_id": family_id,
                "route_count": family_counts[family_id],
                "model_count": len(family_models[family_id]),
                "subtypes": subtypes,
            }
        )

    subtype_catalog = {
        subtype["subtype_id"]: {
            **subtype,
            "family_id": family["family_id"],
        }
        for family in taxonomy_families
        for subtype in family["subtypes"]
    }
    membership_groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for architecture in architectures:
        signature = tuple(sorted(architecture["subtypes"]))
        membership_groups[signature].append(architecture)

    graph_nodes = [
        {
            "id": "taxonomy_root",
            "type": "root",
            "label": "Model-visible input representation",
        }
    ]
    graph_edges = []
    for family in taxonomy_families:
        family_node = f"family::{family['family_id']}"
        graph_nodes.append(
            {
                "id": family_node,
                "type": "family",
                "label": family["name"],
                "family_id": family["family_id"],
                "code": family["code"],
            }
        )
        graph_edges.append(
            {
                "id": f"edge::root::{family['family_id']}",
                "source": "taxonomy_root",
                "target": family_node,
                "type": "contains_family",
            }
        )
        for subtype in family["subtypes"]:
            subtype_node = f"subtype::{subtype['subtype_id']}"
            graph_nodes.append(
                {
                    "id": subtype_node,
                    "type": "subtype",
                    "label": subtype["name"],
                    "subtype_id": subtype["subtype_id"],
                    "family_id": family["family_id"],
                    "leaf_id": subtype["leaf_id"],
                }
            )
            graph_edges.append(
                {
                    "id": f"edge::{family['family_id']}::{subtype['subtype_id']}",
                    "source": family_node,
                    "target": subtype_node,
                    "type": "contains_subtype",
                }
            )
    for signature in sorted(membership_groups):
        signature_text = "|".join(signature)
        group_id = f"membership_{hashlib.sha1(signature_text.encode('utf-8')).hexdigest()[:12]}"
        group_node = f"group::{group_id}"
        group_models = sorted(
            membership_groups[signature], key=lambda item: item["model_name"].casefold()
        )
        family_ids = sorted(
            {subtype_catalog[subtype_id]["family_id"] for subtype_id in signature},
            key=lambda family_id: FAMILY_META[family_id]["code"],
        )
        leaf_ids = [subtype_catalog[subtype_id]["leaf_id"] for subtype_id in signature]
        graph_nodes.append(
            {
                "id": group_node,
                "type": "membership_group",
                "label": " + ".join(leaf_ids),
                "group_id": group_id,
                "subtype_ids": list(signature),
                "family_ids": family_ids,
                "model_ids": [item["model_id"] for item in group_models],
                "model_count": len(group_models),
            }
        )
        for subtype_id in signature:
            graph_edges.append(
                {
                    "id": f"edge::{subtype_id}::{group_id}",
                    "source": f"subtype::{subtype_id}",
                    "target": group_node,
                    "type": "defines_membership_group",
                }
            )
        for architecture in group_models:
            architecture["membership_group_id"] = group_id
            model_node = f"model::{architecture['model_id']}"
            graph_nodes.append(
                {
                    "id": model_node,
                    "type": "model",
                    "label": architecture["model_name"],
                    "model_id": architecture["model_id"],
                    "membership_group_id": group_id,
                }
            )
            graph_edges.append(
                {
                    "id": f"edge::{group_id}::{architecture['model_id']}",
                    "source": group_node,
                    "target": model_node,
                    "type": "contains_model",
                }
            )

    payload = {
        "meta": {
            "title": "Atlas of Input Representation Methods",
            "taxonomy_version": taxonomy["taxonomy_version"],
            "generated_from": str(taxonomy_root.relative_to(ROOT)),
            "canonical_corpus": [display_path(path) for path in corpus_roots],
            "artifact_roots": [display_path(path) for path in artifact_roots],
            "record_count": len(registry),
            "study_count": len({row["study_id"] for row in registry.values()}),
            "model_count": len(architectures),
            "configuration_count": len({r["configuration_id"] for r in routes}),
            "route_count": len(routes),
            "membership_group_count": len(membership_groups),
            "source_figure_count": len(copied),
            "models_with_cropped_figure": sum(
                architecture["figure_status"] == "cropped_source_figure"
                for architecture in architectures
            ),
            "models_without_suitable_figure": sum(
                architecture["figure_status"] == "no_suitable_figure"
                for architecture in architectures
            ),
            "crop_ledger": display_path(crop_ledger_path),
            "classification_unit": taxonomy["classification_unit"],
            "organizing_principle": taxonomy["organizing_principle"],
        },
        "families": taxonomy_families,
        "architectures": architectures,
        "graph": {
            "nodes": graph_nodes,
            "edges": graph_edges,
            "counts": {
                "root": 1,
                "families": len(taxonomy_families),
                "subtypes": sum(len(family["subtypes"]) for family in taxonomy_families),
                "membership_groups": len(membership_groups),
                "models": len(architectures),
                "edges": len(graph_edges),
            },
        },
        "filter_values": {
            "review_iterations": collection_batches,
            # Backward-compatible alias for previously published atlas clients.
            "collection_batches": collection_batches,
            "modalities": sorted({route["source_modality_normalized"] for route in routes}),
            "lifecycle_phases": sorted({route["lifecycle_phase"] for route in routes}),
            "fusion_topologies": sorted({route["fusion_topology"] for route in routes}),
            "text_roles": sorted({route["text_role"] for route in routes}),
        },
    }
    write_json(output / "data/atlas.json", payload)
    write_json(
        output / "data/build_report.json",
        {
            "status": "ok",
            "models": len(architectures),
            "routes": len(routes),
            "configurations": payload["meta"]["configuration_count"],
            "source_figures": len(copied),
            "models_without_figure": sum(not item.get("figure") for item in architectures),
            "models_with_model_specific_crop": sum(
                bool(item.get("figure") and item["figure"].get("crop_box"))
                for item in architectures
            ),
            "graph_nodes": len(graph_nodes),
            "graph_edges": len(graph_edges),
            "routes_without_grounding": sum(
                not route.get("final_grounding_valid") for route in routes
            ),
            "family_route_counts": dict(family_counts),
            "subtype_route_counts": dict(subtype_counts),
            "review_iterations": collection_batches,
            "collection_batches": collection_batches,
        },
    )
    print(json.dumps(payload["meta"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
