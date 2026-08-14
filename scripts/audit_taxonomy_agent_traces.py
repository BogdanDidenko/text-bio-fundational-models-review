#!/usr/bin/env python3
"""Compare the original and full-cohort taxonomy execution traces."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--old",
        type=Path,
        default=Path("data/input_representation_taxonomy_2026-07-11"),
    )
    parser.add_argument(
        "--current",
        type=Path,
        default=Path("data/living_catalog/taxonomy_rerun_preflight_2026-08-12"),
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def truthy(value: Any) -> bool:
    return str(value).casefold() == "true"


def discovery_summaries(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in root.rglob("taxonomy_extraction_summary.json"):
        row = load_json(path)
        record_id = row.get("record_id")
        if record_id and record_id not in rows:
            rows[record_id] = row
    return rows


def route_evidence_stats(routes: list[dict[str, Any]]) -> dict[str, Any]:
    quote_words = [len((row.get("evidence_quote") or "").split()) for row in routes]
    quote_counts = Counter((row.get("evidence_quote") or "").strip() for row in routes)
    dense_only = [
        row
        for row in routes
        if row.get("dense_candidate_refs") and not row.get("source_candidate_refs")
    ]
    return {
        "routes": len(routes),
        "models": len({row["model_id"] for row in routes}),
        "configurations": len({row["configuration_id"] for row in routes}),
        "quote_words_median": statistics.median(quote_words) if quote_words else None,
        "quote_under_4_words": sum(value < 4 for value in quote_words),
        "quote_under_8_words": sum(value < 8 for value in quote_words),
        "rows_with_reused_quote": sum(
            count for quote, count in quote_counts.items() if quote and count > 1
        ),
        "reused_quote_groups": sum(
            1 for quote, count in quote_counts.items() if quote and count > 1
        ),
        "missing_section_heading": sum(not row.get("section_heading") for row in routes),
        "empty_transformation_chain": sum(
            not row.get("transformation_chain_verbatim") for row in routes
        ),
        "with_uncertainty": sum(bool(row.get("uncertainty")) for row in routes),
        "evidence_status": dict(Counter(row.get("evidence_status") for row in routes)),
        "dense_only_final_routes": len(dense_only),
        "dense_only_under_4_word_quote": sum(
            len((row.get("evidence_quote") or "").split()) < 4 for row in dense_only
        ),
        "dense_only_with_uncertainty": sum(
            bool(row.get("uncertainty")) for row in dense_only
        ),
        "picture_only_accepted": sum(truthy(row.get("picture_only_provenance")) for row in routes),
        "invalid_final_grounding": sum(not truthy(row.get("final_grounding_valid")) for row in routes),
    }


def registry_stats(rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "records": len(rows),
        "studies": len({row["study_id"] for row in rows}),
        "canonical_records": sum(truthy(row.get("canonical_record_for_study")) for row in rows),
        "exact_duplicate_rows": sum(truthy(row.get("exact_duplicate")) for row in rows),
        "exact_duplicate_studies": len(
            {
                row["study_id"]
                for row in rows
                if truthy(row.get("exact_duplicate"))
            }
        ),
    }


def call_stage(path: Path) -> str:
    value = path.as_posix()
    if "/runs/discovery/" in value:
        return "discovery"
    if "/classification_fixed_r1/" in value:
        return "direct_r1"
    if "/classification_fixed_r2/" in value:
        return "direct_r2"
    if "/classification_fixed_r3/" in value:
        return "direct_r3"
    if "/classification_dense/" in value:
        return "dense"
    if "/adjudication/" in value:
        return "adjudication"
    return "other"


def llm_trace_stats(root: Path) -> dict[str, Any]:
    stages: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "requests": 0,
            "responses": 0,
            "empty_responses": 0,
            "request_prompt_chars": [],
            "response_hashes": Counter(),
            "models": set(),
            "temperatures": set(),
            "max_tokens": set(),
            "finish_reasons": Counter(),
        }
    )
    for path in root.rglob("llm_calls.jsonl"):
        stage = call_stage(path)
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("event") == "request":
                stages[stage]["requests"] += 1
                stages[stage]["request_prompt_chars"].append(len(row.get("prompt") or ""))
                stages[stage]["models"].add(row.get("model"))
                stages[stage]["temperatures"].add(row.get("temperature"))
                stages[stage]["max_tokens"].add(row.get("max_tokens"))
            elif row.get("event") == "response":
                content = row.get("content") or ""
                stages[stage]["responses"] += 1
                stages[stage]["empty_responses"] += not content.strip()
                stages[stage]["response_hashes"][
                    hashlib.sha256(content.encode("utf-8")).hexdigest()
                ] += 1
                stages[stage]["finish_reasons"][row.get("finish_reason")] += 1

    result: dict[str, Any] = {}
    for stage, values in sorted(stages.items()):
        prompt_chars = values.pop("request_prompt_chars")
        hashes = values.pop("response_hashes")
        result[stage] = {
            **values,
            "models": sorted(str(value) for value in values["models"]),
            "temperatures": sorted(str(value) for value in values["temperatures"]),
            "max_tokens": sorted(str(value) for value in values["max_tokens"]),
            "finish_reasons": dict(values["finish_reasons"]),
            "unique_response_hashes": len(hashes),
            "max_identical_response_multiplicity": max(hashes.values(), default=0),
            "median_request_prompt_chars": (
                statistics.median(prompt_chars) if prompt_chars else None
            ),
            "maximum_request_prompt_chars": max(prompt_chars, default=0),
        }
    return result


def crop_trace_stats(root: Path) -> dict[str, Any]:
    role_stats: dict[str, Any] = {}
    for role in (
        "sufficiency_selector",
        "specificity_selector",
        "adjudicator",
        "cropper",
    ):
        responses = list((root / "models").glob(f"*/{role}/response.json"))
        hashes = Counter(sha256(path) for path in responses)
        role_stats[role] = {
            "responses": len(responses),
            "nonempty": sum(path.stat().st_size > 0 for path in responses),
            "unique_response_hashes": len(hashes),
            "max_identical_response_multiplicity": max(hashes.values(), default=0),
        }
    return role_stats


def main() -> int:
    args = parse_args()
    old = args.old
    current = args.current
    current_taxonomy = current / "taxonomy"

    old_routes = load_jsonl(old / "route_annotations.jsonl")
    current_routes = load_jsonl(current_taxonomy / "route_annotations.jsonl")
    old_registry = load_csv(old / "study_model_registry.csv")
    current_registry = load_csv(current_taxonomy / "study_model_registry.csv")
    old_discovery = discovery_summaries(old / "runs/discovery_open_r1")
    current_discovery = discovery_summaries(current_taxonomy / "runs/discovery")

    shared_records = sorted(set(old_discovery) & set(current_discovery))
    markdown_deltas = [
        current_discovery[record_id]["source_markdown_chars"]
        - old_discovery[record_id]["source_markdown_chars"]
        for record_id in shared_records
    ]

    old_route_counts = Counter(row["record_id"] for row in old_routes)
    current_route_counts = Counter(row["record_id"] for row in current_routes)
    route_deltas = [
        {
            "record_id": record_id,
            "old_routes": old_route_counts[record_id],
            "current_routes": current_route_counts[record_id],
            "delta": current_route_counts[record_id] - old_route_counts[record_id],
        }
        for record_id in shared_records
    ]

    old_models: dict[str, set[str]] = defaultdict(set)
    current_models: dict[str, set[str]] = defaultdict(set)
    for row in old_routes:
        old_models[row["record_id"]].add((row.get("model_name") or "").strip().casefold())
    for row in current_routes:
        current_models[row["record_id"]].add(
            (row.get("model_name") or "").strip().casefold()
        )

    commands = (current / "commands.sh").read_text(encoding="utf-8")
    methods = (current_taxonomy / "manuscript_methods.md").read_text(encoding="utf-8")
    current_metrics = load_json(current_taxonomy / "agreement_metrics.json")
    current_summary = load_json(current_taxonomy / "registry_summary.json")
    old_tree = old / "taxonomy_tree.json"
    current_tree = current / "snapshot_full_55/taxonomy_tree.json"

    result = {
        "scope": {
            "old": str(old),
            "current": str(current),
            "shared_records": len(shared_records),
        },
        "registry": {
            "old": registry_stats(old_registry),
            "current": registry_stats(current_registry),
            "current_registry_summary": current_summary,
            "current_reported_final_counts": current_metrics.get("final_counts", {}),
        },
        "taxonomy": {
            "old_tree_sha256": sha256(old_tree),
            "current_tree_sha256": sha256(current_tree),
            "unchanged": sha256(old_tree) == sha256(current_tree),
            "current_commands_run_three_taxonomy_proposals": all(
                value in commands for value in ("proposal_r1", "proposal_r2", "proposal_r3")
            ),
            "current_commands_use_inventory_only": "--mode inventory" in commands,
        },
        "source_markdown_drift": {
            "same_sha256": sum(
                old_discovery[record_id].get("source_markdown_sha256")
                == current_discovery[record_id].get("source_markdown_sha256")
                for record_id in shared_records
            ),
            "changed_sha256": sum(
                old_discovery[record_id].get("source_markdown_sha256")
                != current_discovery[record_id].get("source_markdown_sha256")
                for record_id in shared_records
            ),
            "same_length": sum(delta == 0 for delta in markdown_deltas),
            "increased_length": sum(delta > 0 for delta in markdown_deltas),
            "decreased_length": sum(delta < 0 for delta in markdown_deltas),
            "total_character_delta": sum(markdown_deltas),
            "median_character_delta": statistics.median(markdown_deltas),
            "minimum_character_delta": min(markdown_deltas),
            "maximum_character_delta": max(markdown_deltas),
        },
        "route_output_drift": {
            "old": route_evidence_stats(old_routes),
            "current": route_evidence_stats(current_routes),
            "current_shared_52_routes": sum(current_route_counts[r] for r in shared_records),
            "shared_records_increased": sum(row["delta"] > 0 for row in route_deltas),
            "shared_records_unchanged": sum(row["delta"] == 0 for row in route_deltas),
            "shared_records_decreased": sum(row["delta"] < 0 for row in route_deltas),
            "largest_absolute_deltas": sorted(
                route_deltas, key=lambda row: (-abs(row["delta"]), row["record_id"])
            )[:15],
            "same_model_name_sets": sum(
                old_models[record_id] == current_models[record_id]
                for record_id in shared_records
            ),
            "different_model_name_sets": sum(
                old_models[record_id] != current_models[record_id]
                for record_id in shared_records
            ),
        },
        "llm_trace": llm_trace_stats(current_taxonomy),
        "crop_trace": {
            "initial": load_json(current / "crops/run_summary.json"),
            "final": load_json(current / "crops_final/run_summary.json"),
            "initial_role_responses": crop_trace_stats(current / "crops"),
            "old_crossvalidation_present": (
                Path("data/input_representation_atlas_crop_crossvalidation_2026-07-12")
                / "CROP_CROSSVALIDATION.md"
            ).exists(),
        },
        "reproduction_script": {
            "set_e": "set -euo pipefail" in commands,
            "contains_repair_commands": "repair_" in commands,
            "contains_crop_pipeline": "run_incremental_atlas_crop_pipeline.py" in commands,
            "contains_snapshot_freeze": "freeze_full_cohort_snapshot.py" in commands,
            "contains_atlas_build": "build_input_representation_atlas.py" in commands,
        },
        "methods_stale_claims": {
            "claims_52_records": "comprised 52 accepted screening records" in methods,
            "claims_583_candidates": "Its 583 grounded candidate routes" in methods,
            "claims_three_new_syntheses": (
                "Three independent\ntaxonomy syntheses were reconciled" in methods
            ),
            "claims_four_replays": "Four already logged full-adjudication responses were replayed" in methods,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "shared_records": len(shared_records)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
