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
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_ROOT = ROOT / "data/input_representation_taxonomy_2026-07-11"
CORPUS_ROOT = ROOT / "data/docling_include_vlm_52_2026-07-10_nolimits"
DEFAULT_OUTPUT = ROOT / "docs/input-representation-atlas"

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
    args = parser.parse_args()
    output = args.output_dir.resolve()
    assets = output / "assets/figures"
    assets.mkdir(parents=True, exist_ok=True)

    routes = [
        json.loads(line)
        for line in (TAXONOMY_ROOT / "route_annotations.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    taxonomy = read_json(TAXONOMY_ROOT / "taxonomy_tree.json")
    with (TAXONOMY_ROOT / "study_model_registry.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        registry = {row["record_id"]: row for row in csv.DictReader(stream)}

    figures_by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for manifest_path in sorted((CORPUS_ROOT / "figures").glob("*/figures_manifest.json")):
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
        figure, figure_score, selection_reasons = choose_figure(
            model_routes, figures_by_record[record_id]
        )
        source_image = ROOT / figure["image_path"]
        if not source_image.exists():
            raise RuntimeError(f"Missing figure image: {source_image}")
        source_key = str(source_image.resolve())
        if source_key not in copied:
            filename = (
                f"{slug(record_id)}_figure_{int(figure['figure_index']):03d}"
                f"{source_image.suffix.casefold()}"
            )
            target = assets / filename
            shutil.copy2(source_image, target)
            copied[source_key] = f"assets/figures/{filename}"
        record = registry[record_id]
        description = next(
            (
                item.get("text")
                for item in figure.get("annotations") or []
                if item.get("kind") == "description" and item.get("text")
            ),
            "",
        )
        family_counts = Counter(route["carrier_family"] for route in model_routes)
        subtype_counts = Counter(route["carrier_subtype"] for route in model_routes)
        architectures.append(
            {
                "model_id": model_id,
                "model_name": first["model_name"],
                "record_id": record_id,
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
                "figure": {
                    "asset": copied[source_key],
                    "source_path": figure["image_path"],
                    "figure_index": figure["figure_index"],
                    "caption": figure.get("caption") or "",
                    "description": description or "",
                    "page_no": figure.get("page_no"),
                    "selection_score": figure_score,
                    "selection_reasons": selection_reasons,
                    "sha256": hashlib.sha256(source_image.read_bytes()).hexdigest(),
                },
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

    payload = {
        "meta": {
            "title": "Atlas of Input Representation Methods",
            "taxonomy_version": taxonomy["taxonomy_version"],
            "generated_from": str(TAXONOMY_ROOT.relative_to(ROOT)),
            "canonical_corpus": str(CORPUS_ROOT.relative_to(ROOT)),
            "record_count": 52,
            "study_count": 51,
            "model_count": len(architectures),
            "configuration_count": len({r["configuration_id"] for r in routes}),
            "route_count": len(routes),
            "source_figure_count": len(copied),
            "classification_unit": taxonomy["classification_unit"],
            "organizing_principle": taxonomy["organizing_principle"],
        },
        "families": taxonomy_families,
        "architectures": architectures,
        "filter_values": {
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
            "routes_without_grounding": sum(
                not route.get("final_grounding_valid") for route in routes
            ),
            "family_route_counts": dict(family_counts),
            "subtype_route_counts": dict(subtype_counts),
        },
    )
    print(json.dumps(payload["meta"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
