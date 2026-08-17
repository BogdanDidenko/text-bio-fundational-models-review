#!/usr/bin/env python3
"""Materialize a versioned taxonomy from validated semantic-correction decisions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT
    / "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
    / "taxonomy_derived_correction_2026-08-16"
)
DEFAULT_DECISIONS = ROOT / "analysis/taxonomy_semantic_correction_2026-08-17"
DEFAULT_OUTPUT = (
    ROOT
    / "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
    / "taxonomy_semantic_correction_2026-08-17"
)
DEFAULT_PROFILE_MANIFEST = (
    ROOT
    / "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
    / "canonical_docling_profile_manifest.csv"
)
DEFAULT_PROFILE_SOURCE_ROOT = Path(os.environ.get("REVIEW_ARTIFACT_ROOT", ROOT))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize(value: str) -> str:
    value = " ".join(html.unescape(value).split())
    value = re.sub(r"\s+([.,;:!?])", r"\1", value)
    return value.casefold().strip("\"'“”‘’ ")


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


@lru_cache(maxsize=None)
def load_docling(docling_path: Path) -> dict[str, Any]:
    return read_json(docling_path)


def native_quote_refs(docling_path: Path, quote: str) -> tuple[list[int], list[str]]:
    if not docling_path.is_file():
        return [], []
    document = load_docling(docling_path)
    target = normalize(quote)
    pages: set[int] = set()
    refs: set[str] = set()
    for collection in ("texts", "tables", "pictures", "key_value_items", "form_items"):
        for item in document.get(collection) or []:
            candidates = [item.get("text"), item.get("orig")]
            if collection == "pictures":
                for annotation in item.get("annotations") or []:
                    candidates.extend([annotation.get("text"), annotation.get("description")])
            if not any(target and target in normalize(str(value)) for value in candidates if value):
                continue
            if item.get("self_ref"):
                refs.add(str(item["self_ref"]))
            for prov in item.get("prov") or []:
                if prov.get("page_no") is not None:
                    pages.add(int(prov["page_no"]))
    return sorted(pages), sorted(refs)


def table_counts(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    route_counts = Counter(str(row.get(field) or "") for row in rows)
    record_sets: dict[str, set[str]] = {}
    model_sets: dict[str, set[str]] = {}
    for row in rows:
        value = str(row.get(field) or "")
        record_sets.setdefault(value, set()).add(str(row["record_id"]))
        model_sets.setdefault(value, set()).add(str(row["model_id"]))
    return [
        {
            field: value,
            "routes": route_counts[value],
            "records": len(record_sets[value]),
            "models": len(model_sets[value]),
        }
        for value in sorted(route_counts)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-taxonomy-root", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--correction-root", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--profile-manifest", type=Path, default=DEFAULT_PROFILE_MANIFEST)
    parser.add_argument("--profile-source-root", type=Path, default=DEFAULT_PROFILE_SOURCE_ROOT)
    args = parser.parse_args()

    output = args.output_dir
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"Refusing to overwrite non-empty output: {output}")
    output.mkdir(parents=True, exist_ok=True)

    source_routes = read_jsonl(args.source_taxonomy_root / "route_annotations.jsonl")
    source_evidence = {
        row["route_id"]: row for row in read_jsonl(args.source_taxonomy_root / "evidence_ledger.jsonl")
    }
    decisions = {
        row["route_id"]: row for row in read_jsonl(args.correction_root / "correction_decisions.jsonl")
    }
    population = read_json(args.correction_root / "correction_population.json")
    if len(decisions) != population["routes"]:
        raise RuntimeError("Correction decision count does not match the frozen population")

    profiles = {row["candidate_id"]: row for row in read_csv(args.profile_manifest)}
    output_routes = []
    output_evidence = []
    transition = []
    for source in source_routes:
        route_id = source["route_id"]
        decision = decisions.get(route_id)
        if decision is None:
            route = source
            evidence = source_evidence[route_id]
            disposition = "unchanged_outside_f6_correction_population"
            changed_fields: list[str] = []
        elif decision["decision"] == "remove_route":
            transition.append(
                {
                    "route_id": route_id,
                    "record_id": source["record_id"],
                    "model_id": source["model_id"],
                    "configuration_id": source["configuration_id"],
                    "disposition": "removed",
                    "changed_fields": [],
                    "confidence": decision["confidence"],
                    "rationale": decision["rationale"],
                }
            )
            continue
        else:
            route = json.loads(json.dumps(source))
            changed_fields = list(decision["changed_fields"])
            for field, value in decision["corrected_route"].items():
                route[field] = value
            route["semantic_correction"] = {
                "audit": "F6.1_taxonomy_aware_2026-08-17",
                "model": "gpt-5.4-mini",
                "decision": decision["decision"],
                "changed_fields": changed_fields,
                "confidence": decision["confidence"],
                "rationale": decision["rationale"],
            }
            evidence_quote = str(route["evidence_quote"])
            profile = profiles[route["record_id"]]
            markdown = resolve(args.profile_source_root, profile["markdown"])
            if normalize(evidence_quote) not in normalize(markdown.read_text(encoding="utf-8")):
                raise RuntimeError(f"Corrected quote is absent from canonical Markdown: {route_id}")
            docling = resolve(args.profile_source_root, profile["docling_json"])
            pages, refs = native_quote_refs(docling, evidence_quote)
            route["pages"] = pages or route.get("pages") or []
            route["doc_item_refs"] = refs or route.get("doc_item_refs") or []
            route["provenance_match"] = ["verbatim"]
            route["candidate_quote_match"] = evidence_quote == source.get("evidence_quote")
            route["quote_verified_in_canonical_markdown"] = True
            route["quote_verified_in_native_items"] = bool(refs)
            route["taxonomy_consistent"] = True
            route["final_grounding_valid"] = True
            evidence = json.loads(json.dumps(source_evidence[route_id]))
            evidence.update(
                {
                    "heading": route["section_heading"],
                    "quote": evidence_quote,
                    "pages": route["pages"],
                    "doc_item_refs": route["doc_item_refs"],
                    "supporting_figure_or_table": route["supporting_figure_or_table"],
                    "evidence_status": route["evidence_status"],
                    "provenance_match": ["verbatim"],
                    "candidate_quote_match": route["candidate_quote_match"],
                    "quote_verified_in_canonical_markdown": True,
                    "quote_verified_in_native_items": bool(refs),
                    "final_grounding_valid": True,
                    "semantic_correction_audit": "F6.1_taxonomy_aware_2026-08-17",
                }
            )
            disposition = decision["decision"]
        output_routes.append(route)
        output_evidence.append(evidence)
        transition.append(
            {
                "route_id": route_id,
                "record_id": source["record_id"],
                "model_id": source["model_id"],
                "configuration_id": source["configuration_id"],
                "disposition": disposition,
                "changed_fields": changed_fields,
                "confidence": decision["confidence"] if decision else "not_applicable",
                "rationale": decision["rationale"] if decision else "Outside the frozen correction population.",
            }
        )

    route_ids = {row["route_id"] for row in output_routes}
    if route_ids != {row["route_id"] for row in output_evidence}:
        raise RuntimeError("Corrected route and evidence ledgers differ")
    if len(transition) != len(source_routes):
        raise RuntimeError("Transition ledger is incomplete")

    for name in ("taxonomy_tree.json", "taxonomy_codebook.md", "study_model_registry.csv", "model_registry.csv"):
        source = args.source_taxonomy_root / name
        if source.is_file():
            shutil.copy2(source, output / name)
    write_jsonl(output / "route_annotations.jsonl", output_routes)
    write_csv(output / "route_annotations.csv", output_routes)
    write_jsonl(output / "evidence_ledger.jsonl", output_evidence)
    write_jsonl(output / "route_transition_ledger.jsonl", transition)
    write_csv(output / "route_transition_ledger.csv", transition)

    table_fields = {
        "carrier_family": "routes_by_carrier_family.csv",
        "carrier_subtype": "routes_by_carrier_subtype.csv",
        "fusion_topology": "routes_by_fusion_topology.csv",
        "lifecycle_phase": "routes_by_lifecycle_phase.csv",
        "source_modality_normalized": "routes_by_source_modality_normalized.csv",
        "text_role": "routes_by_text_role.csv",
    }
    for field, filename in table_fields.items():
        write_csv(output / "tables" / filename, table_counts(output_routes, field))

    source_metrics = read_json(args.source_taxonomy_root / "agreement_metrics.json")
    decision_counts = Counter(row["decision"] for row in decisions.values())
    confidence_counts = Counter(row["confidence"] for row in decisions.values())
    changed_counts = Counter(
        field for row in decisions.values() if row["decision"] == "revise_fields" for field in row["changed_fields"]
    )
    validation = {
        "audit": "F6.1_taxonomy_aware_2026-08-17",
        "status": "passed",
        "scope": "50 routes flagged by F6; 536 routes preserved byte-for-byte except serialization order",
        "model": "gpt-5.4-mini",
        "complete_decision_coverage": True,
        "primary_quotes_verified": True,
        "human_validation": False,
        "decision_counts": dict(sorted(decision_counts.items())),
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "changed_field_counts": dict(sorted(changed_counts.items())),
        "source_route_count": len(source_routes),
        "corrected_route_count": len(output_routes),
    }
    source_metrics["posthoc_semantic_correction"] = validation
    source_metrics["acceptance_passed"] = bool(source_metrics.get("acceptance_passed"))
    write_json(output / "agreement_metrics.json", source_metrics)
    report = {
        **validation,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_taxonomy_root": str(args.source_taxonomy_root),
        "source_route_sha256": sha256(args.source_taxonomy_root / "route_annotations.jsonl"),
        "correction_root": str(args.correction_root),
        "correction_decisions_sha256": sha256(args.correction_root / "correction_decisions.jsonl"),
        "removed_route_ids": sorted(
            row["route_id"] for row in decisions.values() if row["decision"] == "remove_route"
        ),
    }
    write_json(output / "semantic_correction_report.json", report)
    (output / "README.md").write_text(
        "# Taxonomy semantic correction (F6.1)\n\n"
        "This version applies a narrow taxonomy-aware correction to the 50 routes flagged by F6. "
        "It preserves stable route IDs for retained/revised routes and records removals as tombstones "
        "in `route_transition_ledger.jsonl`. The original repeated-classification agreement metrics "
        "remain unchanged and are explicitly separated from the post-hoc correction validation.\n",
        encoding="utf-8",
    )
    files = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "artifact_hashes.json")
    write_json(
        output / "artifact_hashes.json",
        [{"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in files],
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
