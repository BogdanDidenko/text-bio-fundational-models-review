#!/usr/bin/env python3
"""Aggregate repeated fixed-candidate runs, adjudication, and final artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data/input_representation_taxonomy_2026-07-11"
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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def norm(value: Any) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").casefold()))


def stable_id(prefix: str, *values: Any) -> str:
    source = "|".join(norm(value) for value in values)
    return f"{prefix}_{hashlib.sha256(source.encode()).hexdigest()[:12]}"


def load_fixed_run(root: Path) -> dict[str, dict[str, Any]]:
    found = {}
    for path in sorted(root.glob("**/fixed_candidate_classification.json")):
        payload = read_json(path)
        if payload.get("status") == "ok":
            record_id = payload["record_id"]
            if record_id in found:
                raise RuntimeError(f"Duplicate successful fixed classification for {record_id}: {root}")
            found[record_id] = payload
    return found


def load_dense_run(root: Path) -> dict[str, dict[str, Any]]:
    found = {}
    for path in sorted(root.glob("**/taxonomy_extraction_summary.json")):
        payload = read_json(path)
        if payload.get("stage") == "coded" and payload.get("status") == "ok":
            record_id = payload["record_id"]
            if record_id in found:
                raise RuntimeError(f"Duplicate successful dense classification for {record_id}: {root}")
            found[record_id] = payload
    return found


def load_adjudication(root: Path) -> dict[str, dict[str, Any]]:
    found = {}
    for path in sorted(root.glob("**/adjudicated_routes.json")):
        payload = read_json(path)
        if payload.get("status") == "ok":
            record_id = payload["record_id"]
            if record_id in found:
                raise RuntimeError(f"Duplicate successful adjudication for {record_id}: {root}")
            payload["_selected_artifact_path"] = str(path.resolve().relative_to(ROOT))
            payload["_selected_artifact_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            found[record_id] = payload
    return found


def accepted_refs(summary: dict[str, Any]) -> set[str]:
    return {
        ref
        for route in summary.get("input_routes") or []
        for ref in route.get("source_candidate_refs") or []
    }


def family_ratings(summary: dict[str, Any]) -> dict[str, str]:
    values: dict[str, set[str]] = defaultdict(set)
    for route in summary.get("input_routes") or []:
        for ref in route.get("source_candidate_refs") or []:
            values[ref].add(str(route.get("carrier_family")))
    return {ref: "|".join(sorted(families)) for ref, families in values.items()}


def nominal_alpha(ratings_by_unit: dict[str, dict[int, str]]) -> float | None:
    observed_num = observed_den = 0
    pooled = Counter()
    for ratings in ratings_by_unit.values():
        counts = Counter(ratings.values())
        n = sum(counts.values())
        pooled.update(counts)
        if n >= 2:
            observed_num += n * n - sum(value * value for value in counts.values())
            observed_den += n * (n - 1)
    total = sum(pooled.values())
    if not observed_den or total < 2:
        return None
    observed = observed_num / observed_den
    expected = (total * total - sum(value * value for value in pooled.values())) / (
        total * (total - 1)
    )
    return None if expected == 0 else 1 - observed / expected


def agreement(direct_runs: list[dict[str, dict[str, Any]]]) -> dict[str, Any]:
    ref_sets = [
        {ref for summary in run.values() for ref in accepted_refs(summary)}
        for run in direct_runs
    ]
    jaccards = []
    family_pairs = []
    ratings: dict[str, dict[int, str]] = defaultdict(dict)
    run_ratings: list[dict[str, str]] = []
    for run_index, run in enumerate(direct_runs, 1):
        mapping = {}
        for summary in run.values():
            mapping.update(family_ratings(summary))
        run_ratings.append(mapping)
        for ref, value in mapping.items():
            ratings[ref][run_index] = value
    for (left_index, left), (right_index, right) in combinations(enumerate(ref_sets, 1), 2):
        union = left | right
        common = left & right
        family_agree = sum(
            run_ratings[left_index - 1][ref] == run_ratings[right_index - 1][ref]
            for ref in common
        )
        jaccards.append(
            {
                "run_pair": f"r{left_index}-r{right_index}",
                "intersection": len(common),
                "union": len(union),
                "jaccard": len(common) / len(union) if union else 1.0,
            }
        )
        family_pairs.append(
            {
                "run_pair": f"r{left_index}-r{right_index}",
                "comparable_accepted_candidate_refs": len(common),
                "exact_family_set_agreements": family_agree,
                "exact_family_set_agreement": family_agree / len(common) if common else None,
            }
        )
    family_comparisons = sum(item["comparable_accepted_candidate_refs"] for item in family_pairs)
    family_agreements = sum(item["exact_family_set_agreements"] for item in family_pairs)
    return {
        "classification_unit": "fixed open-discovery route_ref",
        "accepted_candidate_ref_counts": [len(values) for values in ref_sets],
        "final_route_counts": [
            sum(len(summary.get("input_routes") or []) for summary in run.values())
            for run in direct_runs
        ],
        "unverified_quote_counts": [
            sum(int(summary.get("unverified_quote_count") or 0) for summary in run.values())
            for run in direct_runs
        ],
        "pairwise_route_detection": jaccards,
        "minimum_pairwise_jaccard": min(item["jaccard"] for item in jaccards),
        "pairwise_carrier_family": family_pairs,
        "carrier_family_comparable_pair_count": family_comparisons,
        "carrier_family_exact_agreement": (
            family_agreements / family_comparisons if family_comparisons else None
        ),
        "carrier_family_krippendorff_alpha": nominal_alpha(
            {ref: values for ref, values in ratings.items() if len(values) >= 2}
        ),
        "candidate_refs_accepted_in_all_runs": len(set.intersection(*ref_sets)),
        "candidate_refs_accepted_in_any_run": len(set.union(*ref_sets)),
    }


def flatten_final(
    adjudication: dict[str, dict[str, Any]],
    registry: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    dense_dispositions: list[dict[str, Any]] = []
    for record_id, summary in sorted(adjudication.items()):
        record = registry[record_id]
        for item in summary.get("input_routes") or []:
            route = dict(item)
            grounding = route.pop("adjudicated_grounding", {}) or {}
            family = route.get("carrier_family")
            subtype = route.get("carrier_subtype")
            consistent = family in FAMILY_SUBTYPES and subtype in FAMILY_SUBTYPES[family]
            model_id = stable_id("model", record["study_id"], route.get("model_name"))
            configuration_id = stable_id(
                "config",
                model_id,
                route.get("lifecycle_phase"),
                route.get("task_or_configuration_verbatim"),
            )
            route_id = stable_id(
                "route",
                record_id,
                configuration_id,
                route.get("route_label"),
                route.get("source_candidate_refs"),
                route.get("dense_candidate_refs"),
                route.get("source_object_normalized"),
                family,
                subtype,
                route.get("fusion_topology"),
                route.get("evidence_quote"),
            )
            row = {
                "candidate_type": "accepted_input_route",
                "route_id": route_id,
                "configuration_id": configuration_id,
                "model_id": model_id,
                "study_id": record["study_id"],
                "record_id": record_id,
                "title": summary.get("title"),
                **route,
                **grounding,
                "taxonomy_consistent": consistent,
            }
            row["final_grounding_valid"] = bool(
                (
                    grounding.get("quote_verified_in_canonical_markdown")
                    or grounding.get("quote_verified_in_native_items")
                )
                and grounding.get("candidate_quote_match")
                and grounding.get("doc_item_refs")
                and grounding.get("provenance_match")
                and not grounding.get("picture_only_provenance")
            )
            accepted.append(row)
            candidates.append(row)
        for item in summary.get("excluded_candidates") or []:
            candidates.append(
                {
                    "candidate_type": "excluded_discovery_candidate",
                    "record_id": record_id,
                    "study_id": record["study_id"],
                    "title": summary.get("title"),
                    **item,
                }
            )
        for item in summary.get("dense_candidate_dispositions") or []:
            row = {
                "candidate_type": "dense_candidate_disposition",
                "record_id": record_id,
                "study_id": record["study_id"],
                "title": summary.get("title"),
                **item,
            }
            candidates.append(row)
            dense_dispositions.append(row)
        for item in summary.get("automatic_dense_exclusions") or []:
            row = {
                "candidate_type": "automatic_dense_exclusion",
                "record_id": record_id,
                "study_id": record["study_id"],
                "title": summary.get("title"),
                **item,
            }
            candidates.append(row)
            dense_dispositions.append(row)
    return accepted, candidates, dense_dispositions


def csv_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value
        for key, value in row.items()
    }


def counts(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    return [
        {field: key, "route_count": value}
        for key, value in sorted(Counter(str(row.get(field) or "") for row in rows).items())
    ]


def markdown_table(rows: list[dict[str, Any]], key: str) -> list[str]:
    lines = [f"| {key} | routes |", "|---|---:|"]
    lines.extend(f"| {row[key]} | {row['route_count']} |" for row in rows)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direct-run", action="append", type=Path, required=True)
    parser.add_argument("--dense-run", type=Path, required=True)
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=DEFAULT_OUTPUT / "study_model_registry.csv")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--expected-records", type=int, default=52)
    parser.add_argument("--cohort-label", default="52-paper baseline corpus")
    parser.add_argument("--incremental", action="store_true")
    parser.add_argument(
        "--allow-alpha-na",
        action="store_true",
        help="Treat alpha as not applicable when a small cohort has no estimable disagreement.",
    )
    args = parser.parse_args()
    if len(args.direct_run) != 3:
        raise RuntimeError("Expected exactly three --direct-run roots")
    direct_runs = [load_fixed_run(path) for path in args.direct_run]
    dense = load_dense_run(args.dense_run)
    adjudication = load_adjudication(args.adjudication)
    expected = args.expected_records
    for path, run in zip(args.direct_run, direct_runs):
        if len(run) != expected:
            raise RuntimeError(f"Expected {expected} records in {path}, found {len(run)}")
    if len(dense) != expected or len(adjudication) != expected:
        raise RuntimeError(
            f"Expected {expected} dense/adjudicated records, found {len(dense)}/{len(adjudication)}"
        )
    with args.registry.open(newline="", encoding="utf-8") as stream:
        registry_rows = list(csv.DictReader(stream))
    registry = {row["record_id"]: row for row in registry_rows}

    adjudication_resolution = [
        {
            "record_id": record_id,
            "selected_artifact": summary["_selected_artifact_path"],
            "selected_artifact_sha256": summary["_selected_artifact_sha256"],
        }
        for record_id, summary in sorted(adjudication.items())
    ]
    write_csv(
        args.output_dir / "adjudication_resolution_manifest.csv",
        adjudication_resolution,
    )

    metrics = agreement(direct_runs)
    accepted, all_candidates, dense_dispositions = flatten_final(adjudication, registry)
    evidence_ledger = [
        {
            "route_id": row["route_id"],
            "record_id": row["record_id"],
            "source_candidate_refs": row.get("source_candidate_refs"),
            "dense_candidate_refs": row.get("dense_candidate_refs"),
            "heading": row.get("section_heading"),
            "quote": row.get("evidence_quote"),
            "pages": row.get("pages"),
            "doc_item_refs": row.get("doc_item_refs"),
            "supporting_figure_or_table": row.get("supporting_figure_or_table"),
            "evidence_status": row.get("evidence_status"),
            "provenance_match": row.get("provenance_match"),
            "candidate_quote_match": row.get("candidate_quote_match"),
            "quote_verified_in_canonical_markdown": row.get(
                "quote_verified_in_canonical_markdown"
            ),
            "quote_verified_in_native_items": row.get(
                "quote_verified_in_native_items"
            ),
            "final_grounding_valid": row.get("final_grounding_valid"),
        }
        for row in accepted
    ]
    uncertainties = [
        row
        for row in all_candidates
        if row.get("uncertainty")
        or row.get("decision") in {"uncertain", "unresolved"}
        or (row.get("candidate_type") == "accepted_input_route" and not row["final_grounding_valid"])
        or (row.get("candidate_type") == "accepted_input_route" and not row["taxonomy_consistent"])
    ]
    model_rows = {}
    for row in accepted:
        model_rows[(row["record_id"], row["model_id"])] = {
            "record_id": row["record_id"],
            "study_id": row["study_id"],
            "model_id": row["model_id"],
            "model_name": row.get("model_name"),
            "title": row.get("title"),
        }

    write_jsonl(args.output_dir / "route_annotations.jsonl", accepted)
    write_csv(args.output_dir / "route_annotations.csv", [csv_view(row) for row in accepted])
    write_jsonl(args.output_dir / "route_candidates_all.jsonl", all_candidates)
    write_jsonl(args.output_dir / "evidence_ledger.jsonl", evidence_ledger)
    write_jsonl(args.output_dir / "uncertainty_cases.jsonl", uncertainties)
    write_csv(args.output_dir / "model_registry.csv", list(model_rows.values()))
    table_rows = {}
    for field in [
        "carrier_family",
        "carrier_subtype",
        "lifecycle_phase",
        "fusion_topology",
        "text_role",
        "source_modality_normalized",
    ]:
        table_rows[field] = counts(accepted, field)
        write_csv(args.output_dir / "tables" / f"routes_by_{field}.csv", table_rows[field])

    unresolved_dense = [
        row for row in dense_dispositions if row.get("decision") == "unresolved"
    ]
    output_derived_text_inputs = [
        row
        for row in accepted
        if row.get("text_role") == "generated_output"
        and str(row.get("source_modality_normalized") or "").casefold() == "text"
    ]
    dense_only = [
        row
        for row in dense_dispositions
        if row.get("decision") == "accepted_as_dense_only_route"
    ]
    expected_dense_count = sum(
        len(summary.get("routes") or []) for summary in dense.values()
    )
    metrics["dense_candidate_count"] = len(dense_dispositions)
    metrics["expected_dense_candidate_count"] = expected_dense_count
    metrics["dense_only_accepted_candidate_count"] = len(dense_only)
    metrics["unresolved_dense_candidate_count"] = len(unresolved_dense)
    alpha = metrics["carrier_family_krippendorff_alpha"]
    acceptance = {
        "all_direct_runs_complete": all(len(run) == expected for run in direct_runs),
        "dense_run_complete": len(dense) == expected,
        "adjudication_complete": len(adjudication) == expected,
        "all_adjudicated_routes_grounded": bool(accepted)
        and all(row["final_grounding_valid"] for row in accepted),
        "all_adjudicated_routes_taxonomy_consistent": all(
            row["taxonomy_consistent"] for row in accepted
        ),
        "no_non_input_or_other_accepted": all(
            row.get("input_status") in {"actual_model_input", "paired_alignment_input"}
            and row.get("carrier_family") != "other_evidence_grounded"
            for row in accepted
        ),
        "output_derived_inputs_explicit": all(
            row.get("source_candidate_refs") or row.get("dense_candidate_refs")
            for row in output_derived_text_inputs
        ),
        "pairwise_jaccard_ge_0_80": metrics["minimum_pairwise_jaccard"] >= 0.80,
        "carrier_agreement_ge_0_90": (
            metrics["carrier_family_exact_agreement"] is not None
            and metrics["carrier_family_exact_agreement"] >= 0.90
        ),
        "krippendorff_alpha_ge_0_80_or_not_applicable": (
            (alpha is not None and alpha >= 0.80)
            or (alpha is None and args.allow_alpha_na)
        ),
        "every_dense_candidate_accounted": (
            len(dense_dispositions) == expected_dense_count
        ),
        "unresolved_dense_candidates_explicit": all(
            row.get("reason") and row.get("uncertainty")
            for row in unresolved_dense
        ),
    }
    metrics["acceptance"] = acceptance
    metrics["krippendorff_alpha_applicable"] = alpha is not None
    metrics["expected_records"] = expected
    metrics["cohort_label"] = args.cohort_label
    metrics["acceptance_passed"] = all(acceptance.values())
    canonical_rows = [
        row
        for row in registry_rows
        if row.get("canonical_record_for_study", "").casefold() == "true"
    ]
    metrics["final_counts"] = {
        "screening_records": expected,
        "primary_studies": len({row["study_id"] for row in registry_rows}),
        "sensitivity_studies_omniNA_linked": len(
            {row.get("possible_version_group") or row["study_id"] for row in canonical_rows}
        ),
        "models": len({row["model_id"] for row in accepted}),
        "configurations": len({row["configuration_id"] for row in accepted}),
        "accepted_input_routes": len(accepted),
        "excluded_discovery_candidates": sum(
            row["candidate_type"] == "excluded_discovery_candidate" for row in all_candidates
        ),
        "dense_candidates": len(dense_dispositions),
        "dense_only_accepted_candidates": len(dense_only),
        "uncertainty_cases": len(uncertainties),
        "output_derived_text_inputs": len(output_derived_text_inputs),
    }
    write_json(args.output_dir / "agreement_metrics.json", metrics)

    special_cases: list[dict[str, Any]] = []
    for row in registry_rows:
        if row.get("exact_duplicate", "").casefold() == "true":
            special_cases.append(
                {
                    "case_type": "exact_pdf_duplicate",
                    "record_id": row["record_id"],
                    "study_id": row["study_id"],
                    "title": row["title"],
                    "source_pdf_sha256": row["source_pdf_sha256"],
                    "primary_analysis_linkage": row["primary_analysis_linkage"],
                }
            )
        if row.get("possible_version_group"):
            special_cases.append(
                {
                    "case_type": "possible_version_linkage",
                    "record_id": row["record_id"],
                    "study_id": row["study_id"],
                    "title": row["title"],
                    "possible_version_group": row["possible_version_group"],
                    "primary_analysis_linkage": row["primary_analysis_linkage"],
                }
            )
    for row in all_candidates:
        searchable = " ".join(
            str(row.get(field) or "")
            for field in (
                "decision",
                "reason",
                "uncertainty",
                "evidence_status",
                "lifecycle_phase",
            )
        ).casefold()
        case_types = []
        if row.get("picture_only_provenance") or "picture-only" in searchable or "figure-only" in searchable:
            case_types.append("figure_only_evidence")
        if any(term in searchable for term in ("training-only", "training_only", "lifecycle", "target", "output")):
            case_types.append("lifecycle_or_input_status_conflict")
        if row.get("candidate_type") == "excluded_discovery_candidate" or row.get("decision") == "unresolved":
            case_types.append("excluded_or_unmatched_candidate")
        for case_type in sorted(set(case_types)):
            special_cases.append(
                {
                    "case_type": case_type,
                    "record_id": row.get("record_id"),
                    "study_id": row.get("study_id"),
                    "candidate_type": row.get("candidate_type"),
                    "candidate_ref": row.get("candidate_ref"),
                    "decision": row.get("decision"),
                    "reason": row.get("reason"),
                    "uncertainty": row.get("uncertainty"),
                }
            )
    for row in output_derived_text_inputs:
        special_cases.append(
            {
                "case_type": "generated_output_reused_as_input",
                "record_id": row["record_id"],
                "study_id": row["study_id"],
                "candidate_type": row["candidate_type"],
                "candidate_ref": "|".join(
                    [
                        *(row.get("source_candidate_refs") or []),
                        *(row.get("dense_candidate_refs") or []),
                    ]
                ),
                "decision": "accepted_actual_model_input",
                "reason": (
                    "A generated textual object from an earlier reasoning stage is "
                    "explicitly reused as an input to a verifier or corrector stage."
                ),
                "uncertainty": row.get("uncertainty"),
            }
        )
    write_jsonl(args.output_dir / "special_cases.jsonl", special_cases)

    report = [
        "# Input-Representation Taxonomy Agreement Report",
        "",
        "- Unit for route detection: fixed open-discovery route_ref.",
        "- Unit for carrier agreement: exact carrier-family set assigned to a",
        "  candidate accepted in both compared runs; split routes remain visible.",
        f"- Screening records: {expected}",
        f"- Accepted final input routes: {len(accepted)}",
        f"- Minimum pairwise route-detection Jaccard: {metrics['minimum_pairwise_jaccard']:.3f}",
        f"- Carrier-family exact agreement: {metrics['carrier_family_exact_agreement']}",
        f"- Carrier-family Krippendorff alpha: {metrics['carrier_family_krippendorff_alpha']}",
        f"- Dense-only accepted candidates: {len(dense_only)}",
        f"- Acceptance passed: {metrics['acceptance_passed']}",
        "",
        "## Pairwise route detection",
        "",
        "| pair | intersection | union | Jaccard |",
        "|---|---:|---:|---:|",
        *[
            f"| {row['run_pair']} | {row['intersection']} | {row['union']} | {row['jaccard']:.3f} |"
            for row in metrics["pairwise_route_detection"]
        ],
        "",
        "## Acceptance checks",
        "",
        *[f"- {name}: {value}" for name, value in acceptance.items()],
    ]
    (args.output_dir / "agreement_report.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )

    inventory_candidate_count = sum(
        int(summary.get("candidate_count") or 0)
        for summary in direct_runs[0].values()
    )
    if args.incremental:
        corpus_description = [
            f"This incremental post-eligibility cohort comprised {expected} newly accepted",
            "screening records represented by complete VLM-enriched Docling profiles.",
            "The carrier-family hierarchy and leaf definitions were held fixed at taxonomy v1;",
            "the update did not re-synthesize or silently revise the baseline taxonomy.",
            "Exact source-document duplicates inherited the prior study identifier and remained",
            "explicit in the registry.",
            "",
            "Open route discovery used Docling Graph direct extraction over each complete new",
            "document, including body text, tables, captions, appendices, and native VLM picture",
            f"descriptions. Its {inventory_candidate_count} candidates formed the fixed inventory",
            "for this update.",
        ]
    else:
        corpus_description = [
            "The post-eligibility corpus comprised 52 accepted screening records represented",
            "by complete VLM-enriched Docling profiles. One exact Cell2Text PDF duplicate was",
            "retained at the record level but collapsed for study-level reporting. OmniNA",
            "versions were separate in the primary analysis and linked in sensitivity analysis.",
            "",
            "Open route discovery used Docling Graph direct extraction over each complete",
            "canonical document, including body text, tables, captions, appendices, and VLM",
            "picture descriptions. The open extractor was not shown the eventual taxonomy.",
            "Its 583 grounded candidate routes formed a fixed inventory. Three independent",
            "taxonomy syntheses were reconciled into taxonomy v1 before classification.",
        ]
    family_agreement_text = (
        f"{metrics['carrier_family_exact_agreement']:.3f}"
        if metrics["carrier_family_exact_agreement"] is not None
        else "not estimable"
    )
    alpha_text = (
        f"{metrics['carrier_family_krippendorff_alpha']:.3f}"
        if metrics["carrier_family_krippendorff_alpha"] is not None
        else "not estimable in this cohort"
    )
    methods = [
        "# Manuscript-Ready Methods: Post-Eligibility Input-Representation Taxonomy",
        "",
        *corpus_description,
        "",
        "Each of three repeated classifications received the same fixed per-paper candidate",
        "inventory and complete canonical Markdown. Separate routes represented source",
        "objects within each model, lifecycle phase, and task/input configuration. Runs used",
        "gpt-5.4-mini, temperature 0, strict JSON schemas, no configured output-token cap,",
        "no configured context cap, and the local OpenAI-compatible Codex wrapper. A separate",
        "Docling Graph dense scoped-fill pass audited coverage. A blinded fourth invocation",
        "reconciled the three repeated classifications and explicitly dispositioned every",
        "dense candidate.",
        "",
        "Final routes required a verbatim match in canonical Markdown or a cited native",
        "Docling item, Docling item references,",
        "non-figure-only provenance, a valid frozen family/subtype pair, and an actual-input",
        "or paired-alignment status. VLM descriptions could locate evidence but could not",
        "independently establish a route. Targets, outputs, baselines, and ablations were",
        "explicitly excluded. Non-verbatim quotations were deterministically rebound only",
        "to cited candidate support or native Docling items. Reciprocal candidate links and",
        "immutable candidate namespaces were normalized without changing model decisions.",
        "Four already logged full-adjudication responses were replayed through the final",
        "validator after these normalization rules were frozen; the source response line,",
        "request index, and log hash are retained. This is repeated computational annotation with LLM",
        "adjudication, not human-validated ground truth.",
        "",
        "Agreement was calculated on fixed discovery candidate references. Route detection",
        "used pairwise Jaccard; carrier agreement used exact family-set agreement and nominal",
        "Krippendorff alpha. All prompts, schemas, responses, retries, hashes, provenance,",
        "and errors were retained in the versioned output directory.",
        "",
        f"The final corpus contained {len(accepted)} accepted input routes across",
        f"{len({row['model_id'] for row in accepted})} models and",
        f"{len({row['configuration_id'] for row in accepted})} configurations.",
        f"The minimum pairwise route-detection Jaccard was {metrics['minimum_pairwise_jaccard']:.3f};",
        f"carrier-family exact agreement was {family_agreement_text},",
        f"and nominal Krippendorff alpha was {alpha_text}.",
        f"All {len(dense_dispositions)} dense candidates were dispositioned, with",
        f"{len(dense_only)} accepted as dense-only evidence and {len(unresolved_dense)} retained as",
        "explicitly reasoned unresolved cases rather than forced into a taxonomy category.",
        f"{len(output_derived_text_inputs)} output-derived textual objects were retained only where the paper explicitly",
        f"reused them as inputs to a downstream verifier or corrector stage.",
    ]
    (args.output_dir / "manuscript_methods.md").write_text(
        "\n".join(methods) + "\n", encoding="utf-8"
    )

    taxonomy_tables = ["# Manuscript-Ready Taxonomy Tables", ""]
    for field in ("carrier_family", "carrier_subtype", "lifecycle_phase", "fusion_topology"):
        taxonomy_tables += [f"## {field.replace('_', ' ').title()}", ""]
        taxonomy_tables += markdown_table(table_rows[field], field)
        taxonomy_tables += [""]
    (args.output_dir / "manuscript_taxonomy_tables.md").write_text(
        "\n".join(taxonomy_tables), encoding="utf-8"
    )

    failures = [
        "# Failure Modes and Uncertainty",
        "",
        f"- Unverified quotes in direct replicates: {metrics['unverified_quote_counts']}.",
        f"- Final routes failing grounding policy: {sum(not row['final_grounding_valid'] for row in accepted)}.",
        f"- Dense candidates retained as dense-only routes: {len(dense_only)}.",
        f"- Dense candidates unresolved: {len(unresolved_dense)}.",
        f"- Explicit uncertainty rows: {len(uncertainties)}.",
        "",
        "Raw failed pilots, errors, retries, and corrected runs remain in runs/. They are",
        "not mixed into the final annotations.",
    ]
    (args.output_dir / "failure_mode_report.md").write_text(
        "\n".join(failures) + "\n", encoding="utf-8"
    )
    special_counts = Counter(row["case_type"] for row in special_cases)
    special_report = [
        "# Duplicate, Version, Figure, Lifecycle, and Unmatched Cases",
        "",
        "This audit is generated from the registry and the complete final candidate ledger.",
        "A row may carry more than one case type; these are audit flags, not taxonomy labels.",
        "",
        *[f"- {key}: {value}" for key, value in sorted(special_counts.items())],
        "",
        "Machine-readable rows are stored in `special_cases.jsonl`.",
    ]
    (args.output_dir / "special_cases_report.md").write_text(
        "\n".join(special_report) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics["final_counts"] | {"acceptance_passed": metrics["acceptance_passed"]}))
    return 0 if metrics["acceptance_passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
