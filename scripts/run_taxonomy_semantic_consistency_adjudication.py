#!/usr/bin/env python3
"""Resolve within-paper inconsistencies created by independent F6.1 route batches."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import run_taxonomy_semantic_correction as correction


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_ROOT = (
    ROOT
    / "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
    / "taxonomy_derived_correction_2026-08-16"
)
CORRECTION_ROOT = ROOT / "analysis/taxonomy_semantic_correction_2026-08-17"

CASES = {
    "procyon_database_sources": {
        "record_id": "full_2026-07-06__rec_000086",
        "route_ids": [
            "route_18a49a03ed5f",
            "route_67d60756e8b4",
            "route_7d3bbc8ca354",
            "route_ba110b719918",
        ],
        "question": (
            "Apply one criterion to all four database/source labels. Decide whether each label "
            "establishes a distinct source-to-model route through PROCYON-INSTRUCT curation and "
            "instruction templating. Do not repurpose an invalid source-label route into an unrelated "
            "inference example such as the bupropion case."
        ),
    },
    "xcell_primary_t_contexts": {
        "record_id": "full_2026-07-06__rec_003517",
        "route_ids": [
            "route_cb00fd160f0d",
            "route_8a01f73645e7",
            "route_2b4d0b79d9e9",
            "route_f278942a47d6",
            "route_e0fbfe069c31",
            "route_2f2691a4449a",
        ],
        "question": (
            "Apply one criterion to all six donor/time context routes. Decide whether donor and "
            "stimulation conditions are legitimate task/input configurations under the route-level "
            "unit or merely labels duplicated by a broader primary-T-cell route. If they are valid, "
            "code all six against the same explicitly described X-Cell expression interface."
        ),
    },
}


def prompt(
    *,
    case_name: str,
    case: dict[str, Any],
    routes: list[dict[str, Any]],
    prior_decisions: list[dict[str, Any]],
    codebook: str,
    document: str,
    document_sha256: str,
) -> str:
    return f"""You are the final within-paper consistency adjudicator for a biomedical input-route taxonomy.

Independent route batches produced inconsistent dispositions for structurally parallel routes. Review the listed routes together against the COMPLETE canonical paper and return one coherent set of final decisions.

Case: {case_name}
Consistency question: {case['question']}

Rules:
- Use the classification unit study -> model -> lifecycle phase -> task/input configuration -> input route.
- A route must describe a real source object transformed into a model-visible input for the named model/configuration.
- Normalized taxonomy labels are analyst coding and need not appear verbatim when the underlying mechanism is explicit.
- A source database can ground a route when the paper explicitly connects that source through curation/transformation to model input; a label floating in a figure without that connection cannot.
- Apply the same evidentiary criterion to sibling routes. Explain any differing disposition with route-specific evidence.
- Do not repurpose a route into an unrelated missing route. Do not invent or split routes or change stable IDs.
- Return the complete corrected field set. Copy supported current values exactly and change only what is necessary.
- `changed_fields` must list every changed field; the deterministic validator will recompute it.
- The primary evidence quote and optional supporting quotes must be short verbatim excerpts from the document.
- Do not use external knowledge or provide hidden chain-of-thought.

Record: {case['record_id']}
Canonical Markdown SHA-256: {document_sha256}

CURRENT ROUTES
{json.dumps(routes, ensure_ascii=False, indent=2)}

INDEPENDENT-BATCH DECISIONS TO RECONCILE
{json.dumps(prior_decisions, ensure_ascii=False, indent=2)}

FROZEN TAXONOMY CODEBOOK
{codebook}

COMPLETE CANONICAL DOCLING MARKDOWN
--- BEGIN DOCUMENT ---
{document}
--- END DOCUMENT ---
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxonomy-root", type=Path, default=TAXONOMY_ROOT)
    parser.add_argument("--correction-root", type=Path, default=CORRECTION_ROOT)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()

    routes = {
        row["route_id"]: row
        for row in correction.read_jsonl(args.taxonomy_root / "route_annotations.jsonl")
    }
    decision_path = args.correction_root / "correction_decisions.jsonl"
    prior_rows = correction.read_jsonl(decision_path)
    prior = {row["route_id"]: row for row in prior_rows}
    manifest = correction.read_json(args.correction_root / "correction_manifest.json")
    record_source: dict[str, dict[str, Any]] = {}
    for row in manifest:
        record_source.setdefault(row["record_id"], row)
    codebook = (args.taxonomy_root / "taxonomy_codebook.md").read_text(encoding="utf-8")

    output_root = args.correction_root / "consistency_adjudication"
    overrides: dict[str, dict[str, Any]] = {}
    case_reports = []
    for case_name, case in CASES.items():
        source = record_source[case["record_id"]]
        document = Path(source["canonical_markdown_local_path"]).read_text(encoding="utf-8")
        case_routes = [routes[route_id] for route_id in case["route_ids"]]
        case_prior = [prior[route_id] for route_id in case["route_ids"]]
        record = {
            "record_id": case["record_id"],
            "routes": [{"current_route": route} for route in case_routes],
        }
        target = output_root / case_name / "attempt_01"
        metadata = correction.run_codex(
            prompt(
                case_name=case_name,
                case=case,
                routes=case_routes,
                prior_decisions=case_prior,
                codebook=codebook,
                document=document,
                document_sha256=source["canonical_markdown_sha256"],
            ),
            target,
            args.model,
            args.timeout,
        )
        if metadata["status"] != "ok":
            raise RuntimeError(f"Consistency adjudication failed: {case_name}: {metadata}")
        response, normalization_log = correction.validate_response(
            correction.read_json(target / "response.json"), record, document
        )
        correction.write_json(target / "validated_response.json", response)
        correction.write_json(target / "normalization_log.json", normalization_log)
        for decision in response["decisions"]:
            if decision["route_id"] in overrides:
                raise RuntimeError(f"Duplicate consistency override: {decision['route_id']}")
            overrides[decision["route_id"]] = {
                "record_id": case["record_id"],
                **decision,
                "consistency_adjudication": {
                    "case": case_name,
                    "model": args.model,
                    "prior_decision": prior[decision["route_id"]]["decision"],
                },
            }
        case_reports.append(
            {
                "case": case_name,
                "record_id": case["record_id"],
                "routes": len(case["route_ids"]),
                "decision_counts": dict(Counter(row["decision"] for row in response["decisions"])),
            }
        )

    backup = args.correction_root / "correction_decisions_pre_consistency.jsonl"
    if not backup.exists():
        shutil.copy2(decision_path, backup)
    final_rows = [overrides.get(row["route_id"], row) for row in prior_rows]
    correction.write_jsonl(decision_path, final_rows)
    report = {
        "status": "complete",
        "model": args.model,
        "cases": case_reports,
        "overridden_routes": sorted(overrides),
        "final_decision_counts": dict(Counter(row["decision"] for row in final_rows)),
        "supporting_quotes_verified": True,
        "human_validation": False,
    }
    report["tool_isolation"] = correction.audit_tool_isolation(args.correction_root)
    correction.write_json(output_root / "report.json", report)
    correction.write_json(
        args.correction_root / "correction_report.json",
        {
            **correction.read_json(args.correction_root / "correction_report.json"),
            "consistency_adjudication": report,
            "decision_counts": report["final_decision_counts"],
        },
    )
    correction.artifact_hashes(args.correction_root)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
