#!/usr/bin/env python3
"""Classify a fixed open-discovery route inventory against canonical full text."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
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
    FixedCandidateClassificationDocument,
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
DEFAULT_TAXONOMY = ROOT / "data/input_representation_taxonomy_2026-07-11/taxonomy_tree.json"
DEFAULT_OUTPUT = ROOT / "data/input_representation_taxonomy_2026-07-11/runs/fixed_candidates_smoke"
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
FROZEN_IDS = {
    "F1": "text_native_token_stream",
    "F2": "discrete_biological_symbol_stream",
    "F3": "dense_continuous_carrier",
    "F4": "visual_raster_carrier",
    "F5": "geometric_or_diffusion_state_carrier",
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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalized(value: str) -> str:
    return "".join(char for char in value.casefold() if char.isalnum())


def group_inventory(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["record_id"], []).append(row)
    return grouped


def requires_split(candidate: dict[str, Any]) -> bool:
    return str(candidate.get("route_ref") or "") in REQUIRED_COMPOSITE_SOURCE_REFS


def frozen_example_labels(
    taxonomy: dict[str, Any], candidates: list[dict[str, Any]]
) -> dict[str, list[dict[str, str]]]:
    wanted = {candidate["route_ref"] for candidate in candidates}
    labels: dict[str, list[dict[str, str]]] = {}
    for family in taxonomy.get("families") or []:
        family_value = FROZEN_IDS.get(str(family.get("family_id")))
        for leaf in family.get("leaves") or []:
            subtype_value = FROZEN_IDS.get(str(leaf.get("leaf_id")))
            if not family_value or not subtype_value:
                continue
            for ref in leaf.get("positive_route_refs") or []:
                if ref in wanted:
                    labels.setdefault(ref, []).append(
                        {
                            "carrier_family": family_value,
                            "carrier_subtype": subtype_value,
                        }
                    )
    return labels


def prompt_for_record(
    record: dict[str, str],
    markdown: str,
    candidates: list[dict[str, Any]],
    taxonomy: dict[str, Any],
    schema: dict[str, Any],
    prompt_version: str,
) -> str:
    v2 = ""
    if prompt_version == "v2-decision-table":
        anchors = frozen_example_labels(taxonomy, candidates)
        v2 = f"""

DETERMINISTIC CARRIER DECISION TABLE (prompt v2):
1. Standard prose, prompts, questions, or deterministic text serialization consumed
   through the ordinary text tokenizer: text_native_token_stream.
2. Native DNA/RNA/protein symbols, aligned structural alphabets, or learned VQ/RVQ/
   codebook IDs consumed as discrete IDs: discrete_biological_symbol_stream.
3. An external encoder/projector/resampler/query connector/pooled representation that
   explicitly produces continuous vectors entering the generative backbone:
   dense_continuous_carrier.
4. Pixels, patches, slides, or a visual case context consumed through a raster/vision
   interface, without evidence that projected vectors are instead the relevant carrier:
   visual_raster_carrier.
5. Noisy diffusion states, coordinates/backbones/shapes, or structural constraints
   directly organizing generation: geometric_or_diffusion_state_carrier.

Decide from the explicit transformation and model-visible form, not source modality alone.
Do not invent an encoder or projection. If both a raster and a projected embedding are
separate documented interfaces/configurations, retain separate routes. The following
candidate-specific labels are frozen positive examples from the codebook. Treat a single
label as a binding audit anchor unless the complete paper proves the frozen example wrong;
multiple labels indicate a combined candidate that must be split into those carrier routes:
{json.dumps(anchors, ensure_ascii=False)}
"""
    return f"""Classify a fixed, evidence-grounded candidate inventory for one paper.

Use the complete canonical paper to decide which candidates represent actual source-to-model input routes. Every candidate route_ref must be accounted for in input_routes.source_candidate_refs or excluded_candidates.candidate_ref. Do not invent candidate refs.

An accepted route begins with exactly one source object and belongs to one lifecycle phase and task/input configuration. Split a combined or hybrid candidate into separate routes for its independent source objects, repeating the candidate ref in each split route. Merge discovery duplicates only when they describe the same model, phase, configuration, source object, carrier, and fusion mechanism. Do not merge routes merely because they occur in one multimodal configuration.

Exclude training-only targets, generated outputs, baselines, ablations, evaluation datasets that are not actually consumed by the focal model, and statements that are not source-to-model routes. Keep genuine uncertainty explicit. Every accepted route must use the frozen family and leaf definitions and one contiguous verbatim evidence quote. Figure descriptions alone cannot establish an accepted route without textual/caption/table corroboration. Learned VQ/RVQ/codebook IDs are distinct from native biological tokens and continuous embeddings.

Carrier decision boundary: classify the first model-facing representation after semantic preprocessing but before routine embedding lookup or encoder processing. Ordinary text tokens remain text-native; native or learned biological token IDs remain discrete; pixels/patches remain visual; coordinates/noisy states remain geometric/diffusion. Use dense_continuous_carrier only when a separate encoder, projector, pooling operation, or learned soft-token mechanism produces continuous vectors that enter the generative backbone without using the ordinary tokenizer, discrete-symbol, raster, or geometric-state interface. Do not classify a token route as dense merely because token embeddings are computed later.
{v2}

Return only JSON conforming to this strict schema:
{json.dumps(schema, ensure_ascii=False)}

Frozen taxonomy:
{json.dumps(taxonomy, ensure_ascii=False)}

Fixed discovery candidates:
{json.dumps(candidates, ensure_ascii=False)}

Record metadata:
{json.dumps({'record_id': record['candidate_id'], 'title': record['title'], 'doi': record.get('doi', '')}, ensure_ascii=False)}

Complete canonical Docling Markdown:
{markdown}
"""


def validate_coverage(
    result: FixedCandidateClassificationDocument,
    expected_refs: set[str],
    required_split_refs: set[str],
    markdown: str,
) -> tuple[set[str], set[str], list[str], list[str], list[str]]:
    observed = {
        ref for route in result.input_routes for ref in route.source_candidate_refs
    } | {candidate.candidate_ref for candidate in result.excluded_candidates}
    bad_quotes = [
        route.route_label
        for route in result.input_routes
        if not normalized(route.evidence_quote)
        or normalized(route.evidence_quote) not in normalized(markdown)
    ]
    ref_counts: dict[str, int] = {}
    for route in result.input_routes:
        for ref in route.source_candidate_refs:
            ref_counts[ref] = ref_counts.get(ref, 0) + 1
    excluded_refs = {candidate.candidate_ref for candidate in result.excluded_candidates}
    unsplit = sorted(
        ref
        for ref in required_split_refs
        if ref not in excluded_refs and ref_counts.get(ref, 0) < 2
    )
    invalid_taxonomy = [
        route.route_label
        for route in result.input_routes
        if route.carrier_family == "other_evidence_grounded"
        or route.carrier_family not in FAMILY_SUBTYPES
        or route.carrier_subtype not in FAMILY_SUBTYPES[route.carrier_family]
        or route.input_status not in {"actual_model_input", "paired_alignment_input"}
    ]
    return (
        expected_refs - observed,
        observed - expected_refs,
        bad_quotes,
        unsplit,
        invalid_taxonomy,
    )


def invoke(
    client: LiteLLMEndpointClient,
    prompt: str,
    schema: dict[str, Any],
    expected_refs: set[str],
    required_split_refs: set[str],
    markdown: str,
    retries: int,
) -> tuple[FixedCandidateClassificationDocument, int]:
    current_prompt = prompt
    error: Exception | None = None
    correction_history: list[str] = []
    for attempt in range(1, retries + 2):
        try:
            raw = client.get_json_response(
                current_prompt,
                json.dumps(schema),
                structured_output=True,
                response_schema_name="fixed_candidate_taxonomy",
            )
            result = FixedCandidateClassificationDocument.model_validate(raw)
            missing, unexpected, bad_quotes, unsplit, invalid_taxonomy = validate_coverage(
                result, expected_refs, required_split_refs, markdown
            )
            if not missing and not unexpected and not unsplit and not invalid_taxonomy:
                return result, attempt
            correction = (
                "CORRECTION REQUIRED FOR A PREVIOUS OUTPUT:\n"
                + f"Missing candidate refs: {sorted(missing)}\n"
                + f"Unexpected candidate refs: {sorted(unexpected)}\n"
                + f"Routes with non-verbatim quotes: {bad_quotes}\n"
                + f"Accepted combined candidates that still require source-specific splitting: {unsplit}\n"
                + f"Routes with invalid/other taxonomy or non-input status: {invalid_taxonomy}\n"
            )
            correction_history.append(correction)
            error = RuntimeError(correction.replace("\n", " "))
            current_prompt = (
                prompt
                + "\n\nCUMULATIVE CORRECTIONS; ALL MUST REMAIN SATISFIED:\n"
                + "\n".join(correction_history)
                + "\nReturn a complete corrected object without regressing earlier fixes."
            )
        except Exception as exc:
            error = exc
    raise RuntimeError(f"Fixed-candidate classification failed: {error!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--replicate-id", required=True)
    parser.add_argument(
        "--prompt-version",
        choices=["v1", "v2-decision-table"],
        default="v1",
    )
    parser.add_argument("--record-id", action="append", default=[])
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765/v1")
    parser.add_argument("--api-key", default="local-codex")
    parser.add_argument("--model", default="openai/gpt-5.4-mini")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    with args.canonical_manifest.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("profile_status") == "complete"]
    inventory = group_inventory(read_json(args.inventory))
    if len(rows) != 52 or len(inventory) != 52:
        raise RuntimeError(f"Expected 52 manifest/inventory records, found {len(rows)}/{len(inventory)}")
    if args.record_id:
        requested = set(args.record_id)
        rows = [row for row in rows if row["candidate_id"] in requested]
    rows = rows[args.shard_index :: args.shard_count]
    taxonomy = read_json(args.taxonomy)
    schema = strict_json_schema(FixedCandidateClassificationDocument.model_json_schema())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "schema.json", schema)
    write_json(
        args.output_dir / "run_config.json",
        {
            "replicate_id": args.replicate_id,
            "prompt_version": args.prompt_version,
            "record_count": len(rows),
            "model": args.model,
            "temperature": 0.0,
            "max_tokens": None,
            "context_limit": None,
            "classification_unit": "fixed open-discovery route candidates",
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
        candidates = inventory[record_id]
        expected = {candidate["route_ref"] for candidate in candidates}
        required_split_refs = {
            candidate["route_ref"] for candidate in candidates if requires_split(candidate)
        }
        prompt = prompt_for_record(
            row, markdown, candidates, taxonomy, schema, args.prompt_version
        )
        record_dir = args.output_dir / "records" / re.sub(r"[^A-Za-z0-9._-]", "_", record_id)
        record_dir.mkdir(parents=True, exist_ok=True)
        (record_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        started = time.time()
        try:
            result, attempt = invoke(
                client,
                prompt,
                schema,
                expected,
                required_split_refs,
                markdown,
                args.retries,
            )
            payload = result.model_dump(mode="json")
            unverified_quotes = [
                route["route_label"]
                for route in payload["input_routes"]
                if not normalized(route["evidence_quote"])
                or normalized(route["evidence_quote"]) not in normalized(markdown)
            ]
            summary = {
                "status": "ok",
                "record_id": record_id,
                "title": row["title"],
                "doi": row.get("doi", ""),
                "replicate_id": args.replicate_id,
                "prompt_version": args.prompt_version,
                "taxonomy_version": payload["taxonomy_version"],
                "source_markdown": row["markdown"],
                "source_markdown_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
                "candidate_count": len(candidates),
                "required_split_candidate_count": len(required_split_refs),
                "accepted_route_count": len(payload["input_routes"]),
                "excluded_candidate_count": len(payload["excluded_candidates"]),
                "unverified_quote_count": len(unverified_quotes),
                "unverified_quote_routes": unverified_quotes,
                "attempt": attempt,
                "elapsed_seconds": round(time.time() - started, 2),
                **payload,
            }
            write_json(record_dir / "fixed_candidate_classification.json", summary)
        except Exception as exc:
            summary = {
                "status": "error",
                "record_id": record_id,
                "title": row["title"],
                "replicate_id": args.replicate_id,
                "error": repr(exc),
                "elapsed_seconds": round(time.time() - started, 2),
            }
        summaries.append(summary)
        print(json.dumps({"record_id": record_id, "status": summary["status"]}), flush=True)
    write_json(args.output_dir / "run_summary.json", summaries)
    ok = sum(row["status"] == "ok" for row in summaries)
    print(json.dumps({"selected": len(rows), "ok": ok, "errors": len(rows) - ok}))
    return 0 if ok == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
