#!/usr/bin/env python3
"""Blindly reconcile three fixed classifications and dense Graph coverage."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.docling.docling_graph_litellm_client import (
    LiteLLMEndpointClient,
    strict_json_schema,
)
from scripts.docling_graph_templates.input_representation_taxonomy import (
    FinalAdjudicatedTaxonomyDocument,
)

DEFAULT_MANIFEST = (
    ROOT
    / "data/docling_include_vlm_52_2026-07-10_nolimits/manifests"
    / "canonical_docling_profile_manifest.csv"
)
DEFAULT_INVENTORY = (
    ROOT
    / "data/input_representation_taxonomy_2026-07-11/taxonomy_synthesis"
    / "open_route_inventory.json"
)
DEFAULT_OUTPUT = ROOT / "data/input_representation_taxonomy_2026-07-11/adjudication"
FAMILY_SUBTYPES = {
    "text_native_token_stream": {
        "plain_language_prompt_or_question",
        "structured_biological_prompt_or_task_scaffold",
        "serialized_biological_context_or_ordered_profile",
    },
    "discrete_biological_symbol_stream": {
        "native_biological_token_stream",
        "multi_track_structural_symbol_stream",
        "learned_quantized_id_or_codebook_token",
    },
    "dense_continuous_carrier": {
        "direct_projected_embedding",
        "virtual_token_prefix",
        "connector_mediated_embedding",
        "pooled_or_aggregated_embedding",
    },
    "visual_raster_carrier": {
        "raw_slide_or_patch_input",
        "patch_context_or_case_level_visual_reasoning",
    },
    "geometric_or_diffusion_state_carrier": {
        "noisy_diffusion_state",
        "coordinate_backbone_or_shape_conditioning",
        "symbolic_structural_constraint",
    },
}
REQUIRED_COMPOSITE_SOURCE_REFS = {
    "full_2026-07-06__rec_000090::route_032",
    "june_update_2026-06-10__rec_000121::route_006",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalized(value: str) -> str:
    return "".join(char for char in str(value or "").casefold() if char.isalnum())


SUPPORT_TEXT_FIELDS = (
    "evidence_quote",
    "source_object_verbatim",
    "model_visible_form_verbatim",
    "insertion_or_fusion_verbatim",
    "task_or_configuration_verbatim",
)


def candidate_support_texts(item: dict[str, Any]) -> list[tuple[str, str]]:
    candidate = item.get("route") or item
    return [
        (field, str(candidate.get(field) or ""))
        for field in SUPPORT_TEXT_FIELDS
        if candidate.get(field)
    ]


def load_native_item_texts(path: Path) -> dict[str, str]:
    document = read_json(path)
    texts: dict[str, str] = {}
    for collection in ("texts", "pictures", "tables", "key_value_items", "form_items"):
        for item in document.get(collection) or []:
            ref = str(item.get("self_ref") or "")
            text = str(item.get("text") or item.get("orig") or "").strip()
            if ref and text:
                texts[ref] = text
    return texts


def cited_native_texts(
    cited: list[dict[str, Any]], native_items: dict[str, str]
) -> list[tuple[str, str]]:
    out = []
    for item in cited:
        for ref in (item.get("grounding") or {}).get("doc_item_refs") or []:
            if str(ref) in native_items:
                out.append((str(ref), native_items[str(ref)]))
    return out


def group_inventory(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["record_id"], []).append(row)
    return grouped


def load_fixed_run(root: Path) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("**/fixed_candidate_classification.json")):
        payload = read_json(path)
        if payload.get("status") == "ok":
            found[payload["record_id"]] = payload
    return found


def load_dense_run(root: Path) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("**/taxonomy_extraction_summary.json")):
        payload = read_json(path)
        if payload.get("status") == "ok" and payload.get("stage") == "coded":
            found[payload["record_id"]] = payload
    return found


def dense_candidates(
    record_id: str, summary: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = []
    automatic_exclusions = []
    for index, item in enumerate(summary.get("routes") or [], 1):
        route = item.get("route") or {}
        candidate_ref = f"dense::{record_id}::{index:04d}"
        candidate = {
            "candidate_ref": candidate_ref,
            "route": route,
            "grounding": {
                "grounding_valid": item.get("grounding_valid"),
                "pages": item.get("pages") or [],
                "doc_item_refs": item.get("doc_item_refs") or [],
                "provenance_match": item.get("provenance_match"),
                "picture_only_provenance": item.get("picture_only_provenance", False),
                "taxonomy_consistent": item.get("taxonomy_consistent"),
            },
        }
        eligible = bool(
            item.get("accepted_input_candidate")
            and item.get("grounding_valid")
            and item.get("taxonomy_consistent")
            and not item.get("picture_only_provenance")
        )
        if eligible:
            candidates.append(candidate)
            continue
        status = route.get("input_status")
        if item.get("picture_only_provenance"):
            decision = "exclude_figure_only"
        elif not item.get("grounding_valid") or not item.get("taxonomy_consistent"):
            decision = "exclude_ungrounded_or_taxonomy_invalid"
        elif status == "training_only_target":
            decision = "exclude_training_only_target"
        elif status == "generated_output":
            decision = "exclude_generated_output"
        elif status in {"baseline_only", "ablation_only"}:
            decision = "exclude_baseline_or_ablation"
        else:
            decision = "exclude_not_a_source_to_model_route"
        automatic_exclusions.append(
            {
                "candidate_ref": candidate_ref,
                "decision": decision,
                "linked_route_labels": [],
                "reason": (
                    "Deterministic dense eligibility gate: candidate was not simultaneously "
                    "an accepted-input candidate, grounded, taxonomy-consistent, and "
                    "non-picture-only."
                ),
                "uncertainty": route.get("uncertainty"),
            }
        )
    return candidates, automatic_exclusions


def fixed_payload(summary: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "route_label",
        "model_name",
        "lifecycle_phase",
        "task_or_configuration_verbatim",
        "source_object_verbatim",
        "model_visible_form_verbatim",
        "carrier_family",
        "carrier_subtype",
        "fusion_topology",
        "input_status",
        "evidence_quote",
        "section_heading",
        "uncertainty",
        "source_candidate_refs",
    )
    return {
        "input_routes": [
            {field: route.get(field) for field in fields}
            for route in summary.get("input_routes") or []
        ],
        "excluded_candidates": summary.get("excluded_candidates") or [],
        "unverified_quote_routes": summary.get("unverified_quote_routes") or [],
    }


def requires_split(candidate: dict[str, Any]) -> bool:
    return str(candidate.get("route_ref") or "") in REQUIRED_COMPOSITE_SOURCE_REFS


def prompt_for_record(
    row: dict[str, str],
    markdown: str,
    taxonomy: dict[str, Any],
    discovery: list[dict[str, Any]],
    fixed_sets: list[dict[str, Any]],
    dense: list[dict[str, Any]],
    schema: dict[str, Any],
) -> str:
    return f"""Act as a blinded fourth annotator for input-representation routes.

Reconcile three anonymized repeated classifications against the complete canonical paper,
the original grounded discovery inventory, and an independent dense Docling Graph coverage
pass. Return the final source-to-model input routes, not one label per paper.

Rules:
- Every discovery route_ref must appear either in input_routes.source_candidate_refs or
  excluded_candidates.candidate_ref, exactly once at the decision level. A ref may support
  several split routes, but cannot also be excluded.
- Every eligible dense candidate_ref shown below must receive one
  dense_candidate_dispositions entry. Ineligible dense candidates were already excluded by
  logged objective grounding/taxonomy/input-status gates and are not shown to you.
- Every final route starts from exactly one source object and one lifecycle
  phase/configuration. Split multimodal or hybrid candidates into their independent routes.
- Accept only actual model inputs or paired alignment inputs. Explicitly exclude targets,
  outputs, baselines, ablations, evaluation-only datasets, duplicates, and non-routes.
- Use only frozen family/subtype pairs; never use other_evidence_grounded.
- Classify the first model-facing carrier before routine embedding/encoder processing.
- Every final evidence_quote must be one contiguous verbatim passage in the canonical paper.
  Prefer a quote already present in a cited discovery or dense candidate.
- VLM descriptions may locate evidence but cannot alone establish a route.
- Link dense evidence to an accepted route when it confirms the same route. Use
  accepted_as_dense_only_route only for a valid route absent from all fixed classifications.
- Preserve unresolved ambiguity explicitly; do not force an unsupported route.

Return only strict-schema JSON:
{json.dumps(schema, ensure_ascii=False)}

Frozen taxonomy:
{json.dumps(taxonomy, ensure_ascii=False)}

Record:
{json.dumps({'record_id': row['candidate_id'], 'title': row['title'], 'doi': row.get('doi', '')}, ensure_ascii=False)}

Grounded discovery inventory:
{json.dumps(discovery, ensure_ascii=False)}

Anonymized repeated classifications:
{json.dumps(fixed_sets, ensure_ascii=False)}

Dense coverage candidates:
{json.dumps(dense, ensure_ascii=False)}

Complete canonical Docling Markdown:
{markdown}
"""


def validate_result(
    result: FinalAdjudicatedTaxonomyDocument,
    discovery: list[dict[str, Any]],
    dense: list[dict[str, Any]],
    markdown: str,
    native_items: dict[str, str],
) -> list[str]:
    errors = []
    discovery_by_ref = {item["route_ref"]: item for item in discovery}
    dense_by_ref = {item["candidate_ref"]: item for item in dense}
    expected_source = {item["route_ref"] for item in discovery}
    expected_dense = {item["candidate_ref"] for item in dense}
    used_source = {
        ref for route in result.input_routes for ref in route.source_candidate_refs
    }
    excluded_source = {item.candidate_ref for item in result.excluded_candidates}
    observed_dense = {item.candidate_ref for item in result.dense_candidate_dispositions}
    used_dense = {ref for route in result.input_routes for ref in route.dense_candidate_refs}
    route_labels = [route.route_label for route in result.input_routes]
    if len(route_labels) != len(set(route_labels)):
        errors.append("duplicate final route labels")
    if len(result.excluded_candidates) != len(excluded_source):
        errors.append("duplicate discovery exclusions")
    if len(result.dense_candidate_dispositions) != len(observed_dense):
        errors.append("duplicate dense dispositions")
    if used_source & excluded_source:
        errors.append(f"source refs both accepted and excluded: {sorted(used_source & excluded_source)}")
    if expected_source != used_source | excluded_source:
        errors.append(
            f"source coverage missing={sorted(expected_source - used_source - excluded_source)} "
            f"unexpected={sorted((used_source | excluded_source) - expected_source)}"
        )
    if expected_dense != observed_dense:
        errors.append(
            f"dense coverage missing={sorted(expected_dense - observed_dense)} "
            f"unexpected={sorted(observed_dense - expected_dense)}"
        )
    if used_dense - expected_dense:
        errors.append(f"routes cite ineligible dense refs: {sorted(used_dense - expected_dense)}")
    labels = set(route_labels)
    for route in result.input_routes:
        if not route.source_candidate_refs and not route.dense_candidate_refs:
            errors.append(f"route has no candidate refs: {route.route_label}")
        if route.carrier_family not in FAMILY_SUBTYPES or (
            route.carrier_subtype not in FAMILY_SUBTYPES[route.carrier_family]
        ):
            errors.append(f"invalid family/subtype: {route.route_label}")
        if route.input_status not in {"actual_model_input", "paired_alignment_input"}:
            errors.append(f"non-input accepted route: {route.route_label}")
        quote_key = normalized(route.evidence_quote)
        cited = [
            discovery_by_ref[ref]
            for ref in route.source_candidate_refs
            if ref in discovery_by_ref
        ]
        cited += [
            dense_by_ref[ref]
            for ref in route.dense_candidate_refs
            if ref in dense_by_ref
        ]
        native_support = cited_native_texts(cited, native_items)
        quote_is_native = any(
            quote_key == normalized(text) for _, text in native_support
        )
        if not quote_key or (
            quote_key not in normalized(markdown) and not quote_is_native
        ):
            errors.append(f"non-verbatim quote: {route.route_label}")
        if not any(
            quote_key == normalized(text)
            for item in cited
            for _, text in candidate_support_texts(item)
        ) and not quote_is_native:
            errors.append(f"quote does not match a cited candidate: {route.route_label}")
        if not any(
            (item.get("grounding") or {}).get("doc_item_refs")
            and (item.get("grounding") or {}).get("provenance_match")
            and not (
                item.get("picture_only_provenance", False)
                or (item.get("grounding") or {}).get("picture_only_provenance", False)
            )
            for item in cited
        ):
            errors.append(f"no non-picture Docling provenance: {route.route_label}")
    source_counts: dict[str, int] = {}
    for route in result.input_routes:
        for ref in route.source_candidate_refs:
            source_counts[ref] = source_counts.get(ref, 0) + 1
    required_split = {item["route_ref"] for item in discovery if requires_split(item)}
    unsplit = sorted(ref for ref in required_split & used_source if source_counts.get(ref, 0) < 2)
    if unsplit:
        errors.append(f"combined candidates not split: {unsplit}")
    dense_by_ref = {item.candidate_ref: item for item in result.dense_candidate_dispositions}
    route_dense_refs = {ref for route in result.input_routes for ref in route.dense_candidate_refs}
    for ref, disposition in dense_by_ref.items():
        bad_labels = set(disposition.linked_route_labels) - labels
        if bad_labels:
            errors.append(f"dense {ref} links unknown labels: {sorted(bad_labels)}")
        if disposition.decision in {"supports_accepted_route", "accepted_as_dense_only_route"}:
            if not disposition.linked_route_labels or ref not in route_dense_refs:
                errors.append(f"accepted/supporting dense ref not linked from route: {ref}")
    return errors


def repair_route_quotes(
    result: FinalAdjudicatedTaxonomyDocument,
    discovery: list[dict[str, Any]],
    dense: list[dict[str, Any]],
    markdown: str,
    native_items: dict[str, str],
) -> list[dict[str, str]]:
    """Bind final routes to the strongest verbatim quote among their cited refs."""
    by_ref = {item["route_ref"]: item for item in discovery}
    by_ref.update({item["candidate_ref"]: item for item in dense})
    repairs = []
    markdown_key = normalized(markdown)
    for route in result.input_routes:
        refs = [*route.source_candidate_refs, *route.dense_candidate_refs]
        cited = [(ref, by_ref[ref]) for ref in refs if ref in by_ref]
        cited_items = [item for _, item in cited]
        native_support = cited_native_texts(cited_items, native_items)
        current_key = normalized(route.evidence_quote)
        current_is_candidate = any(
            current_key == normalized(text)
            for _, item in cited
            for _, text in candidate_support_texts(item)
        )
        current_is_native = any(
            current_key == normalized(text) for _, text in native_support
        )
        if (current_key in markdown_key or current_is_native) and (
            current_is_candidate or current_is_native
        ):
            continue
        eligible = []
        for ref, item in cited:
            grounding = item.get("grounding") or {}
            for field, quote in candidate_support_texts(item):
                quote_key = normalized(quote)
                if (
                    quote_key
                    and quote_key in markdown_key
                    and grounding.get("doc_item_refs")
                    and grounding.get("provenance_match")
                    and not (
                        item.get("picture_only_provenance", False)
                        or grounding.get("picture_only_provenance", False)
                    )
                ):
                    eligible.append((len(quote_key), ref, field, quote))
        target_tokens = set(
            re.findall(
                r"[a-z0-9]+",
                " ".join(
                    [
                        route.route_label,
                        route.source_object_verbatim,
                        route.model_visible_form_verbatim,
                        route.task_or_configuration_verbatim,
                        route.evidence_quote,
                    ]
                ).casefold(),
            )
        )
        for doc_ref, text in native_support:
            text_key = normalized(text)
            overlap = len(target_tokens & set(re.findall(r"[a-z0-9]+", text.casefold())))
            if text_key and overlap:
                eligible.append((overlap * 1_000_000 - len(text_key), doc_ref, "native_item_text", text))
        if not eligible:
            continue
        _, candidate_ref, candidate_field, replacement = max(eligible)
        repairs.append(
            {
                "route_label": route.route_label,
                "original_quote": route.evidence_quote,
                "replacement_quote": replacement,
                "candidate_ref": candidate_ref,
                "candidate_field": candidate_field,
                "method": (
                    "best lexical-overlap cited native Docling item"
                    if candidate_field == "native_item_text"
                    else "longest cited non-picture Docling-grounded verbatim support field"
                ),
            }
        )
        route.evidence_quote = replacement
    return repairs


def repair_dense_links(
    result: FinalAdjudicatedTaxonomyDocument,
) -> list[dict[str, str]]:
    """Mirror the LLM's explicit dense disposition link onto its named routes."""
    routes = {route.route_label: route for route in result.input_routes}
    repairs = []
    for disposition in result.dense_candidate_dispositions:
        if disposition.decision not in {
            "supports_accepted_route",
            "accepted_as_dense_only_route",
        }:
            continue
        existing_route_labels = [
            route.route_label
            for route in result.input_routes
            if disposition.candidate_ref in route.dense_candidate_refs
        ]
        if not disposition.linked_route_labels and existing_route_labels:
            disposition.linked_route_labels = existing_route_labels
            repairs.append(
                {
                    "candidate_ref": disposition.candidate_ref,
                    "route_label": "|".join(existing_route_labels),
                    "method": "mirror existing route citation into dense disposition links",
                }
            )
        for label in disposition.linked_route_labels:
            route = routes.get(label)
            if route is None or disposition.candidate_ref in route.dense_candidate_refs:
                continue
            route.dense_candidate_refs.append(disposition.candidate_ref)
            repairs.append(
                {
                    "candidate_ref": disposition.candidate_ref,
                    "route_label": label,
                    "method": "mirror explicit dense disposition link onto named route",
                }
            )
    return repairs


def repair_candidate_ref_namespaces(
    result: FinalAdjudicatedTaxonomyDocument,
) -> list[dict[str, str]]:
    """Move refs to the schema field implied by their immutable namespace."""
    repairs = []
    misplaced_dense_exclusions = [
        item
        for item in result.excluded_candidates
        if item.candidate_ref.startswith("dense::")
    ]
    if misplaced_dense_exclusions:
        result.excluded_candidates = [
            item
            for item in result.excluded_candidates
            if not item.candidate_ref.startswith("dense::")
        ]
        for item in misplaced_dense_exclusions:
            repairs.append(
                {
                    "candidate_ref": item.candidate_ref,
                    "route_label": "",
                    "method": "remove dense namespace ref from discovery exclusion list",
                }
            )
    for route in result.input_routes:
        misplaced_dense = [
            ref for ref in route.source_candidate_refs if ref.startswith("dense::")
        ]
        misplaced_source = [
            ref for ref in route.dense_candidate_refs if not ref.startswith("dense::")
        ]
        if misplaced_dense:
            route.source_candidate_refs = [
                ref for ref in route.source_candidate_refs if ref not in misplaced_dense
            ]
            route.dense_candidate_refs = list(
                dict.fromkeys([*route.dense_candidate_refs, *misplaced_dense])
            )
        if misplaced_source:
            route.dense_candidate_refs = [
                ref for ref in route.dense_candidate_refs if ref not in misplaced_source
            ]
            route.source_candidate_refs = list(
                dict.fromkeys([*route.source_candidate_refs, *misplaced_source])
            )
        for ref in misplaced_dense:
            repairs.append(
                {
                    "candidate_ref": ref,
                    "route_label": route.route_label,
                    "method": "move dense namespace ref from source to dense field",
                }
            )
        for ref in misplaced_source:
            repairs.append(
                {
                    "candidate_ref": ref,
                    "route_label": route.route_label,
                    "method": "move discovery namespace ref from dense to source field",
                }
            )
    return repairs


def invoke(
    client: LiteLLMEndpointClient,
    prompt: str,
    schema: dict[str, Any],
    discovery: list[dict[str, Any]],
    dense: list[dict[str, Any]],
    markdown: str,
    native_items: dict[str, str],
    retries: int,
) -> tuple[
    FinalAdjudicatedTaxonomyDocument,
    int,
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    current = prompt
    error: Exception | None = None
    corrections: list[str] = []
    for attempt in range(1, retries + 2):
        try:
            raw = client.get_json_response(
                current,
                json.dumps(schema),
                structured_output=True,
                response_schema_name="final_taxonomy_adjudication",
            )
            result = FinalAdjudicatedTaxonomyDocument.model_validate(raw)
            repairs = repair_route_quotes(
                result, discovery, dense, markdown, native_items
            )
            namespace_repairs = repair_candidate_ref_namespaces(result)
            dense_link_repairs = repair_dense_links(result)
            errors = validate_result(
                result, discovery, dense, markdown, native_items
            )
            if not errors:
                return result, attempt, repairs, namespace_repairs, dense_link_repairs
            corrections.append("\n".join(f"- {item}" for item in errors))
            error = RuntimeError("; ".join(errors))
            current = (
                prompt
                + "\n\nCORRECTIONS REQUIRED FOR PRIOR OUTPUTS:\n"
                + "\n".join(corrections)
                + "\nReturn the complete corrected JSON object."
            )
        except Exception as exc:
            error = exc
    raise RuntimeError(f"Adjudication failed: {error!r}")


def aggregate_grounding(
    route: dict[str, Any],
    discovery_by_ref: dict[str, dict[str, Any]],
    dense_by_ref: dict[str, dict[str, Any]],
    markdown: str,
    native_items: dict[str, str],
) -> dict[str, Any]:
    evidence = [
        discovery_by_ref[ref]
        for ref in route["source_candidate_refs"]
        if ref in discovery_by_ref
    ]
    evidence += [
        dense_by_ref[ref] for ref in route["dense_candidate_refs"] if ref in dense_by_ref
    ]
    pages: set[int] = set()
    refs: set[str] = set()
    matches: set[str] = set()
    non_picture = False
    candidate_support: list[str] = []
    for item in evidence:
        grounding = item.get("grounding") or {}
        pages.update(int(value) for value in grounding.get("pages") or [])
        refs.update(str(value) for value in grounding.get("doc_item_refs") or [])
        if grounding.get("provenance_match"):
            matches.add(str(grounding["provenance_match"]))
        if not (
            item.get("picture_only_provenance", False)
            or grounding.get("picture_only_provenance", False)
        ):
            non_picture = True
        candidate_support.extend(text for _, text in candidate_support_texts(item))
    quote_key = normalized(route["evidence_quote"])
    native_support = cited_native_texts(evidence, native_items)
    native_match = any(quote_key == normalized(text) for _, text in native_support)
    return {
        "pages": sorted(pages),
        "doc_item_refs": sorted(refs),
        "provenance_match": sorted(matches),
        "picture_only_provenance": bool(evidence and not non_picture),
        "candidate_quote_match": (
            any(quote_key == normalized(value) for value in candidate_support)
            or native_match
        ),
        "quote_verified_in_canonical_markdown": bool(
            quote_key and quote_key in normalized(markdown)
        ),
        "quote_verified_in_native_items": native_match,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direct-run", action="append", type=Path, required=True)
    parser.add_argument("--dense-run", type=Path, required=True)
    parser.add_argument("--taxonomy", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--canonical-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--record-id", action="append", default=[])
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765/v1")
    parser.add_argument("--api-key", default="local-codex")
    parser.add_argument("--model", default="openai/gpt-5.4-mini")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    if len(args.direct_run) != 3:
        raise RuntimeError("Expected exactly three direct run roots")
    with args.canonical_manifest.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("profile_status") == "complete"]
    inventory = group_inventory(read_json(args.inventory))
    direct_maps = [load_fixed_run(root) for root in args.direct_run]
    dense_map = load_dense_run(args.dense_run)
    if args.record_id:
        selected_ids = set(args.record_id)
        for root, mapping in zip(args.direct_run, direct_maps):
            missing = selected_ids - set(mapping)
            if missing:
                raise RuntimeError(f"Missing requested fixed records in {root}: {sorted(missing)}")
        missing_dense = selected_ids - set(dense_map)
        if missing_dense:
            raise RuntimeError(f"Missing requested dense records: {sorted(missing_dense)}")
        rows = [row for row in rows if row["candidate_id"] in selected_ids]
    else:
        for root, mapping in zip(args.direct_run, direct_maps):
            if len(mapping) != 52:
                raise RuntimeError(f"Expected 52 fixed records in {root}, found {len(mapping)}")
        if len(dense_map) != 52:
            raise RuntimeError(f"Expected 52 dense records, found {len(dense_map)}")
    rows = rows[args.shard_index :: args.shard_count]
    taxonomy = read_json(args.taxonomy)
    schema = strict_json_schema(FinalAdjudicatedTaxonomyDocument.model_json_schema())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "schema.json", schema)
    write_json(
        args.output_dir / "run_config.json",
        {
            "model": args.model,
            "temperature": 0.0,
            "max_tokens": None,
            "context_limit": None,
            "blinded_fixed_replicates": 3,
            "dense_coverage_pass": 1,
            "shard_index": args.shard_index,
            "shard_count": args.shard_count,
        },
    )
    client = LiteLLMEndpointClient(
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        timeout_s=args.timeout,
        max_tokens=None,
        temperature=0.0,
        log_path=args.output_dir / "llm_calls.jsonl",
    )
    summaries = []
    for row in rows:
        record_id = row["candidate_id"]
        markdown = (ROOT / row["markdown"]).read_text(encoding="utf-8")
        native_items = load_native_item_texts(ROOT / row["docling_json"])
        discovery = inventory[record_id]
        dense, automatic_dense_exclusions = dense_candidates(record_id, dense_map[record_id])
        fixed_sets = [
            {"set_id": chr(65 + index), **fixed_payload(mapping[record_id])}
            for index, mapping in enumerate(direct_maps)
        ]
        random.Random(f"20260711:{record_id}").shuffle(fixed_sets)
        prompt = prompt_for_record(
            row, markdown, taxonomy, discovery, fixed_sets, dense, schema
        )
        record_dir = args.output_dir / "records" / re.sub(r"[^A-Za-z0-9._-]", "_", record_id)
        record_dir.mkdir(parents=True, exist_ok=True)
        (record_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        started = time.time()
        try:
            (
                result,
                attempt,
                quote_repairs,
                namespace_repairs,
                dense_link_repairs,
            ) = invoke(
                client,
                prompt,
                schema,
                discovery,
                dense,
                markdown,
                native_items,
                args.retries,
            )
            payload = result.model_dump(mode="json")
            discovery_by_ref = {item["route_ref"]: item for item in discovery}
            dense_by_ref = {item["candidate_ref"]: item for item in dense}
            for route in payload["input_routes"]:
                route["adjudicated_grounding"] = aggregate_grounding(
                    route,
                    discovery_by_ref,
                    dense_by_ref,
                    markdown,
                    native_items,
                )
            summary = {
                "status": "ok",
                "record_id": record_id,
                "title": row["title"],
                "doi": row.get("doi", ""),
                "model": args.model,
                "temperature": 0.0,
                "max_tokens": None,
                "context_limit": None,
                "source_markdown": row["markdown"],
                "source_markdown_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
                "discovery_candidate_count": len(discovery),
                "dense_candidate_count": len(dense) + len(automatic_dense_exclusions),
                "eligible_dense_candidate_count": len(dense),
                "automatic_dense_exclusion_count": len(automatic_dense_exclusions),
                "automatic_dense_exclusions": automatic_dense_exclusions,
                "attempt": attempt,
                "quote_repair_count": len(quote_repairs),
                "quote_repairs": quote_repairs,
                "candidate_ref_namespace_repair_count": len(namespace_repairs),
                "candidate_ref_namespace_repairs": namespace_repairs,
                "dense_link_repair_count": len(dense_link_repairs),
                "dense_link_repairs": dense_link_repairs,
                "elapsed_seconds": round(time.time() - started, 2),
                **payload,
            }
            write_json(record_dir / "adjudicated_routes.json", summary)
        except Exception as exc:
            summary = {
                "status": "error",
                "record_id": record_id,
                "title": row["title"],
                "error": repr(exc),
                "elapsed_seconds": round(time.time() - started, 2),
            }
        summaries.append(summary)
        print(json.dumps({"record_id": record_id, "status": summary["status"]}), flush=True)
    write_json(args.output_dir / "run_summary.json", summaries)
    ok = sum(item["status"] == "ok" for item in summaries)
    print(json.dumps({"selected": len(rows), "ok": ok, "errors": len(rows) - ok}))
    return 0 if ok == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
