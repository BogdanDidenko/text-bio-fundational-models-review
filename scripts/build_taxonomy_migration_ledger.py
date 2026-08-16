#!/usr/bin/env python3
"""Build a deterministic cross-version ledger for taxonomy routes.

The ledger deliberately separates stable identifiers from inferred lineage. Route
IDs are content hashes and are therefore not expected to survive a re-extraction.
No LLM is used: candidate links are scored from controlled taxonomy fields and
normalized text, followed by a maximum-weight one-to-one assignment per record.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import scipy
from scipy.optimize import linear_sum_assignment


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OLD = ROOT / "data/input_representation_taxonomy_2026-07-11/route_annotations.jsonl"
DEFAULT_CURRENT = (
    ROOT
    / "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
    / "taxonomy_derived_correction_2026-08-16/route_annotations.jsonl"
)
DEFAULT_OUTPUT = ROOT / "analysis/input_taxonomy_migration_2026-08-17"

ALGORITHM_VERSION = "deterministic-route-lineage-v1"
TOP_CANDIDATES_PER_ROUTE = 3
MIN_CANDIDATE_SCORE = 0.45
PRESERVED_REVIEW_FILES = {"largest_delta_review.md"}

SCORE_WEIGHTS = {
    "model_name": 0.13,
    "carrier_family": 0.13,
    "carrier_subtype": 0.09,
    "source_modality": 0.09,
    "lifecycle_phase": 0.07,
    "fusion_topology": 0.06,
    "text_role": 0.05,
    "source_object": 0.12,
    "model_visible_form": 0.07,
    "transformation_chain": 0.07,
    "task_or_configuration": 0.05,
    "route_label": 0.03,
    "evidence_quote": 0.04,
}

CONTROLLED_FIELDS = {
    "carrier_family": "carrier_family",
    "carrier_subtype": "carrier_subtype",
    "source_modality": "source_modality_normalized",
    "lifecycle_phase": "lifecycle_phase",
    "fusion_topology": "fusion_topology",
    "text_role": "text_role",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def portable_path(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


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


def normalize(value: Any) -> str:
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").casefold()))


def text_similarity(left: Any, right: Any) -> float:
    left_norm = normalize(left)
    right_norm = normalize(right)
    if not left_norm and not right_norm:
        return 1.0
    if not left_norm or not right_norm:
        return 0.0
    left_tokens = set(left_norm.split())
    right_tokens = set(right_norm.split())
    token_jaccard = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    sequence_ratio = difflib.SequenceMatcher(None, left_norm, right_norm).ratio()
    return max(token_jaccard, sequence_ratio)


def controlled_equal(left: Any, right: Any) -> float:
    left_norm = normalize(left)
    right_norm = normalize(right)
    return float(bool(left_norm) and left_norm == right_norm)


def route_similarity(
    old: dict[str, Any], current: dict[str, Any]
) -> tuple[float, dict[str, float]]:
    components = {
        "model_name": text_similarity(old.get("model_name"), current.get("model_name")),
        "carrier_family": controlled_equal(
            old.get("carrier_family"), current.get("carrier_family")
        ),
        "carrier_subtype": controlled_equal(
            old.get("carrier_subtype"), current.get("carrier_subtype")
        ),
        "source_modality": controlled_equal(
            old.get("source_modality_normalized"),
            current.get("source_modality_normalized"),
        ),
        "lifecycle_phase": controlled_equal(
            old.get("lifecycle_phase"), current.get("lifecycle_phase")
        ),
        "fusion_topology": controlled_equal(
            old.get("fusion_topology"), current.get("fusion_topology")
        ),
        "text_role": controlled_equal(old.get("text_role"), current.get("text_role")),
        "source_object": text_similarity(
            old.get("source_object_normalized"),
            current.get("source_object_normalized"),
        ),
        "model_visible_form": text_similarity(
            old.get("model_visible_form_verbatim"),
            current.get("model_visible_form_verbatim"),
        ),
        "transformation_chain": text_similarity(
            old.get("transformation_chain_normalized"),
            current.get("transformation_chain_normalized"),
        ),
        "task_or_configuration": text_similarity(
            old.get("task_or_configuration_verbatim"),
            current.get("task_or_configuration_verbatim"),
        ),
        "route_label": text_similarity(old.get("route_label"), current.get("route_label")),
        "evidence_quote": text_similarity(
            old.get("evidence_quote"), current.get("evidence_quote")
        ),
    }
    score = sum(SCORE_WEIGHTS[key] * value for key, value in components.items())
    return score, components


def structural_core_equal(components: dict[str, float]) -> bool:
    return all(
        components[field] == 1.0
        for field in (
            "carrier_family",
            "carrier_subtype",
            "source_modality",
            "lifecycle_phase",
        )
    )


def lineage_link_accepted(
    score: float,
    components: dict[str, float],
    old: dict[str, Any],
    current: dict[str, Any],
) -> bool:
    """Conservative acceptance rule; low-scoring assignment pairs stay unmatched."""
    if score >= 0.72:
        return True
    if (
        score >= 0.60
        and old.get("model_id") == current.get("model_id")
        and structural_core_equal(components)
    ):
        return True
    return bool(
        score >= 0.65
        and components["model_name"] >= 0.80
        and components["carrier_family"] == 1.0
        and components["carrier_subtype"] == 1.0
    )


def changed_controlled_fields(
    old: dict[str, Any], current: dict[str, Any]
) -> list[str]:
    return [
        name
        for name, field in CONTROLLED_FIELDS.items()
        if normalize(old.get(field)) != normalize(current.get(field))
    ]


def route_brief(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row.get(key)
        for key in (
            "route_id",
            "configuration_id",
            "model_id",
            "model_name",
            "lifecycle_phase",
            "route_label",
            "source_object_normalized",
            "source_modality_normalized",
            "carrier_family",
            "carrier_subtype",
            "fusion_topology",
            "text_role",
            "task_or_configuration_verbatim",
            "evidence_quote",
            "section_heading",
        )
    }


def candidate_row(
    record_id: str,
    old: dict[str, Any],
    current: dict[str, Any],
    score: float,
    components: dict[str, float],
) -> dict[str, Any]:
    changed = changed_controlled_fields(old, current)
    return {
        "record_id": record_id,
        "old_route_id": old["route_id"],
        "current_route_id": current["route_id"],
        "score": round(score, 6),
        "accepted_by_rule": lineage_link_accepted(score, components, old, current),
        "structural_core_equal": structural_core_equal(components),
        "same_model_id": old.get("model_id") == current.get("model_id"),
        "changed_controlled_fields": ";".join(changed),
        **{f"score_{key}": round(value, 6) for key, value in components.items()},
        "old_model_name": old.get("model_name"),
        "current_model_name": current.get("model_name"),
        "old_route_label": old.get("route_label"),
        "current_route_label": current.get("route_label"),
    }


def record_route_matches(
    record_id: str,
    old_routes: list[dict[str, Any]],
    current_routes: list[dict[str, Any]],
) -> dict[str, Any]:
    if not old_routes or not current_routes:
        return {
            "primary": [],
            "candidate_edges": [],
            "old_unmatched": old_routes,
            "current_unmatched": current_routes,
        }

    score_matrix: list[list[float]] = []
    details: dict[tuple[int, int], tuple[float, dict[str, float]]] = {}
    for old_index, old in enumerate(old_routes):
        row = []
        for current_index, current in enumerate(current_routes):
            score, components = route_similarity(old, current)
            row.append(score)
            details[(old_index, current_index)] = (score, components)
        score_matrix.append(row)

    old_indexes, current_indexes = linear_sum_assignment(score_matrix, maximize=True)
    assigned = {(int(old_i), int(current_i)) for old_i, current_i in zip(old_indexes, current_indexes)}
    primary: list[dict[str, Any]] = []
    accepted_old: set[int] = set()
    accepted_current: set[int] = set()
    for old_index, current_index in sorted(assigned):
        score, components = details[(old_index, current_index)]
        old = old_routes[old_index]
        current = current_routes[current_index]
        if not lineage_link_accepted(score, components, old, current):
            continue
        changed = changed_controlled_fields(old, current)
        if score >= 0.82 and not changed:
            interpretation = "high_confidence_rewording_or_same_route"
            confidence = "high"
        elif structural_core_equal(components):
            interpretation = "same_structural_core_with_textual_or_interface_change"
            confidence = "moderate"
        else:
            interpretation = "probable_modified_route"
            confidence = "moderate"
        primary.append(
            {
                **candidate_row(record_id, old, current, score, components),
                "relationship": "primary_one_to_one",
                "confidence": confidence,
                "interpretation": interpretation,
                "old_configuration_id": old.get("configuration_id"),
                "current_configuration_id": current.get("configuration_id"),
                "old_model_id": old.get("model_id"),
                "current_model_id": current.get("model_id"),
            }
        )
        accepted_old.add(old_index)
        accepted_current.add(current_index)

    old_rankings: dict[int, list[int]] = {}
    current_rankings: dict[int, list[int]] = {}
    for old_index in range(len(old_routes)):
        old_rankings[old_index] = sorted(
            range(len(current_routes)),
            key=lambda current_index: (
                -details[(old_index, current_index)][0],
                current_routes[current_index]["route_id"],
            ),
        )
    for current_index in range(len(current_routes)):
        current_rankings[current_index] = sorted(
            range(len(old_routes)),
            key=lambda old_index: (
                -details[(old_index, current_index)][0],
                old_routes[old_index]["route_id"],
            ),
        )

    candidate_pairs: set[tuple[int, int]] = set()
    for old_index, ranking in old_rankings.items():
        candidate_pairs.update(
            (old_index, current_index)
            for current_index in ranking[:TOP_CANDIDATES_PER_ROUTE]
            if details[(old_index, current_index)][0] >= MIN_CANDIDATE_SCORE
        )
    for current_index, ranking in current_rankings.items():
        candidate_pairs.update(
            (old_index, current_index)
            for old_index in ranking[:TOP_CANDIDATES_PER_ROUTE]
            if details[(old_index, current_index)][0] >= MIN_CANDIDATE_SCORE
        )

    primary_pairs = {
        (row["old_route_id"], row["current_route_id"]) for row in primary
    }
    candidate_edges: list[dict[str, Any]] = []
    for old_index, current_index in sorted(candidate_pairs):
        score, components = details[(old_index, current_index)]
        old = old_routes[old_index]
        current = current_routes[current_index]
        candidate_edges.append(
            {
                **candidate_row(record_id, old, current, score, components),
                "old_rank": old_rankings[old_index].index(current_index) + 1,
                "current_rank": current_rankings[current_index].index(old_index) + 1,
                "primary_assignment": (
                    old["route_id"], current["route_id"]
                )
                in primary_pairs,
            }
        )

    return {
        "primary": primary,
        "candidate_edges": candidate_edges,
        "old_unmatched": [
            route for index, route in enumerate(old_routes) if index not in accepted_old
        ],
        "current_unmatched": [
            route
            for index, route in enumerate(current_routes)
            if index not in accepted_current
        ],
    }


def entity_ledger(
    entity: str,
    old_routes: list[dict[str, Any]],
    current_routes: list[dict[str, Any]],
    primary: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    id_field = f"{entity}_id"
    old_entities: dict[str, list[dict[str, Any]]] = defaultdict(list)
    current_entities: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in old_routes:
        old_entities[str(row[id_field])].append(row)
    for row in current_routes:
        current_entities[str(row[id_field])].append(row)

    support: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in primary:
        support[(str(row[f"old_{id_field}"]), str(row[f"current_{id_field}"]))].append(
            float(row["score"])
        )
    for stable_id in set(old_entities) & set(current_entities):
        support.setdefault((stable_id, stable_id), [])

    old_degree = Counter(old_id for old_id, _ in support)
    current_degree = Counter(current_id for _, current_id in support)
    output: list[dict[str, Any]] = []
    paired_old: set[str] = set()
    paired_current: set[str] = set()
    for (old_id, current_id), scores in sorted(support.items()):
        paired_old.add(old_id)
        paired_current.add(current_id)
        old = old_entities[old_id][0]
        current = current_entities[current_id][0]
        row = {
            "record_id": old["record_id"],
            f"old_{id_field}": old_id,
            f"current_{id_field}": current_id,
            "mapping_status": "stable_id" if old_id == current_id else "route_supported_mapping",
            "supporting_primary_routes": len(scores),
            "mean_route_score": round(statistics.mean(scores), 6) if scores else "",
            "old_split_degree": old_degree[old_id],
            "current_merge_degree": current_degree[current_id],
            "old_route_count": len(old_entities[old_id]),
            "current_route_count": len(current_entities[current_id]),
        }
        if entity == "model":
            row.update(
                {
                    "old_model_name": old.get("model_name"),
                    "current_model_name": current.get("model_name"),
                    "name_similarity": round(
                        text_similarity(old.get("model_name"), current.get("model_name")), 6
                    ),
                }
            )
        else:
            row.update(
                {
                    "old_lifecycle_phase": old.get("lifecycle_phase"),
                    "current_lifecycle_phase": current.get("lifecycle_phase"),
                    "old_task": old.get("task_or_configuration_verbatim"),
                    "current_task": current.get("task_or_configuration_verbatim"),
                }
            )
        output.append(row)

    for old_id in sorted(set(old_entities) - paired_old):
        old = old_entities[old_id][0]
        output.append(
            {
                "record_id": old["record_id"],
                f"old_{id_field}": old_id,
                f"current_{id_field}": "",
                "mapping_status": "old_only_unmapped",
                "supporting_primary_routes": 0,
                "old_route_count": len(old_entities[old_id]),
                "current_route_count": 0,
                **(
                    {"old_model_name": old.get("model_name"), "current_model_name": ""}
                    if entity == "model"
                    else {
                        "old_lifecycle_phase": old.get("lifecycle_phase"),
                        "current_lifecycle_phase": "",
                        "old_task": old.get("task_or_configuration_verbatim"),
                        "current_task": "",
                    }
                ),
            }
        )
    for current_id in sorted(set(current_entities) - paired_current):
        current = current_entities[current_id][0]
        output.append(
            {
                "record_id": current["record_id"],
                f"old_{id_field}": "",
                f"current_{id_field}": current_id,
                "mapping_status": "current_only_unmapped",
                "supporting_primary_routes": 0,
                "old_route_count": 0,
                "current_route_count": len(current_entities[current_id]),
                **(
                    {"old_model_name": "", "current_model_name": current.get("model_name")}
                    if entity == "model"
                    else {
                        "old_lifecycle_phase": "",
                        "current_lifecycle_phase": current.get("lifecycle_phase"),
                        "old_task": "",
                        "current_task": current.get("task_or_configuration_verbatim"),
                    }
                ),
            }
        )
    return sorted(
        output,
        key=lambda row: (
            row.get("record_id", ""),
            row.get(f"old_{id_field}", ""),
            row.get(f"current_{id_field}", ""),
        ),
    )


def compact_counts(rows: list[dict[str, Any]], field: str) -> str:
    counts = Counter(str(row.get(field) or "") for row in rows)
    return "; ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def entity_mapping_stats(
    entity: str,
    rows: list[dict[str, Any]],
    old_routes: list[dict[str, Any]],
    current_routes: list[dict[str, Any]],
) -> dict[str, int]:
    id_field = f"{entity}_id"
    old_ids = {str(row[id_field]) for row in old_routes}
    current_ids = {str(row[id_field]) for row in current_routes}
    mapped = [
        row
        for row in rows
        if row["mapping_status"] in {"stable_id", "route_supported_mapping"}
    ]
    mapped_old = {str(row[f"old_{id_field}"]) for row in mapped}
    mapped_current = {str(row[f"current_{id_field}"]) for row in mapped}
    old_degree = Counter(str(row[f"old_{id_field}"]) for row in mapped)
    current_degree = Counter(str(row[f"current_{id_field}"]) for row in mapped)
    return {
        "old_entities": len(old_ids),
        "current_entities": len(current_ids),
        "stable_ids": len(old_ids & current_ids),
        "mapping_edges": len(mapped),
        "mapped_old_entities": len(mapped_old),
        "mapped_current_entities": len(mapped_current),
        "unmapped_old_entities": len(old_ids - mapped_old),
        "unmapped_current_entities": len(current_ids - mapped_current),
        "old_entities_with_multiple_successors": sum(
            degree > 1 for degree in old_degree.values()
        ),
        "current_entities_with_multiple_predecessors": sum(
            degree > 1 for degree in current_degree.values()
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", type=Path, default=DEFAULT_OLD)
    parser.add_argument("--current", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--created-at",
        default="",
        help="Fixed ISO timestamp for byte-reproducible reports; defaults to current UTC.",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    old_path = args.old.resolve()
    current_path = args.current.resolve()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()) and not args.force:
        raise RuntimeError(f"Refusing to overwrite non-empty output: {output}")
    output.mkdir(parents=True, exist_ok=True)
    if args.force:
        for path in output.iterdir():
            if path.is_file() and path.name not in PRESERVED_REVIEW_FILES:
                path.unlink()

    old_routes = read_jsonl(old_path)
    current_routes = read_jsonl(current_path)
    old_by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    current_by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in old_routes:
        old_by_record[str(row["record_id"])].append(row)
    for row in current_routes:
        current_by_record[str(row["record_id"])].append(row)

    old_records = set(old_by_record)
    current_records = set(current_by_record)
    shared_records = sorted(old_records & current_records)
    all_primary: list[dict[str, Any]] = []
    all_candidates: list[dict[str, Any]] = []
    record_summaries: list[dict[str, Any]] = []
    review_packets: list[dict[str, Any]] = []
    route_ledger: list[dict[str, Any]] = []

    for record_id in shared_records:
        old = sorted(old_by_record[record_id], key=lambda row: row["route_id"])
        current = sorted(current_by_record[record_id], key=lambda row: row["route_id"])
        matches = record_route_matches(record_id, old, current)
        primary = matches["primary"]
        candidates = matches["candidate_edges"]
        all_primary.extend(primary)
        all_candidates.extend(candidates)
        primary_by_old = {row["old_route_id"]: row for row in primary}
        primary_by_current = {row["current_route_id"]: row for row in primary}

        for row in primary:
            route_ledger.append({"status": "linked", **row})
        for row in matches["old_unmatched"]:
            best = next(
                (
                    edge
                    for edge in sorted(
                        candidates,
                        key=lambda edge: (edge["old_route_id"], edge["old_rank"]),
                    )
                    if edge["old_route_id"] == row["route_id"]
                ),
                None,
            )
            route_ledger.append(
                {
                    "status": "old_unmatched_removed_or_consolidated",
                    "record_id": record_id,
                    "old_route_id": row["route_id"],
                    "current_route_id": "",
                    "old_model_id": row.get("model_id"),
                    "current_model_id": "",
                    "old_configuration_id": row.get("configuration_id"),
                    "current_configuration_id": "",
                    "old_model_name": row.get("model_name"),
                    "current_model_name": "",
                    "old_route_label": row.get("route_label"),
                    "current_route_label": "",
                    "best_candidate_route_id": best.get("current_route_id") if best else "",
                    "best_candidate_score": best.get("score") if best else "",
                }
            )
        for row in matches["current_unmatched"]:
            best = next(
                (
                    edge
                    for edge in sorted(
                        candidates,
                        key=lambda edge: (edge["current_route_id"], edge["current_rank"]),
                    )
                    if edge["current_route_id"] == row["route_id"]
                ),
                None,
            )
            route_ledger.append(
                {
                    "status": "current_unmatched_added_or_split",
                    "record_id": record_id,
                    "old_route_id": "",
                    "current_route_id": row["route_id"],
                    "old_model_id": "",
                    "current_model_id": row.get("model_id"),
                    "old_configuration_id": "",
                    "current_configuration_id": row.get("configuration_id"),
                    "old_model_name": "",
                    "current_model_name": row.get("model_name"),
                    "old_route_label": "",
                    "current_route_label": row.get("route_label"),
                    "best_candidate_route_id": best.get("old_route_id") if best else "",
                    "best_candidate_score": best.get("score") if best else "",
                }
            )

        record_summaries.append(
            {
                "record_id": record_id,
                "title": old[0].get("title") or current[0].get("title"),
                "study_id_stable": {row["study_id"] for row in old}
                == {row["study_id"] for row in current},
                "old_routes": len(old),
                "current_routes": len(current),
                "route_delta": len(current) - len(old),
                "accepted_primary_links": len(primary),
                "high_confidence_links": sum(
                    row["confidence"] == "high" for row in primary
                ),
                "moderate_confidence_links": sum(
                    row["confidence"] == "moderate" for row in primary
                ),
                "old_unmatched": len(matches["old_unmatched"]),
                "current_unmatched": len(matches["current_unmatched"]),
                "old_models": len({row["model_id"] for row in old}),
                "current_models": len({row["model_id"] for row in current}),
                "old_configurations": len({row["configuration_id"] for row in old}),
                "current_configurations": len(
                    {row["configuration_id"] for row in current}
                ),
                "old_family_counts": compact_counts(old, "carrier_family"),
                "current_family_counts": compact_counts(current, "carrier_family"),
                "old_model_names": "; ".join(
                    sorted({str(row.get("model_name") or "") for row in old})
                ),
                "current_model_names": "; ".join(
                    sorted({str(row.get("model_name") or "") for row in current})
                ),
            }
        )
        review_packets.append(
            {
                "record_id": record_id,
                "title": old[0].get("title") or current[0].get("title"),
                "old_route_count": len(old),
                "current_route_count": len(current),
                "delta": len(current) - len(old),
                "old_routes": [route_brief(row) for row in old],
                "current_routes": [route_brief(row) for row in current],
                "primary_links": primary,
                "candidate_edges": candidates,
                "unmatched_old_route_ids": [
                    row["route_id"] for row in matches["old_unmatched"]
                ],
                "unmatched_current_route_ids": [
                    row["route_id"] for row in matches["current_unmatched"]
                ],
            }
        )

    for record_id in sorted(old_records - current_records):
        rows = old_by_record[record_id]
        record_summaries.append(
            {
                "record_id": record_id,
                "title": rows[0].get("title"),
                "study_id_stable": False,
                "old_routes": len(rows),
                "current_routes": 0,
                "route_delta": -len(rows),
                "accepted_primary_links": 0,
                "old_unmatched": len(rows),
                "current_unmatched": 0,
            }
        )
    for record_id in sorted(current_records - old_records):
        rows = current_by_record[record_id]
        record_summaries.append(
            {
                "record_id": record_id,
                "title": rows[0].get("title"),
                "study_id_stable": False,
                "old_routes": 0,
                "current_routes": len(rows),
                "route_delta": len(rows),
                "accepted_primary_links": 0,
                "old_unmatched": 0,
                "current_unmatched": len(rows),
            }
        )

    shared_old = [row for row in old_routes if row["record_id"] in shared_records]
    shared_current = [
        row for row in current_routes if row["record_id"] in shared_records
    ]
    model_ledger = entity_ledger("model", shared_old, shared_current, all_primary)
    configuration_ledger = entity_ledger(
        "configuration", shared_old, shared_current, all_primary
    )

    study_rows: list[dict[str, Any]] = []
    for record_id in sorted(old_records | current_records):
        old = old_by_record.get(record_id, [])
        current = current_by_record.get(record_id, [])
        old_studies = sorted({row["study_id"] for row in old})
        current_studies = sorted({row["study_id"] for row in current})
        if old and current:
            status = (
                "shared_stable_study_id"
                if old_studies == current_studies
                else "shared_changed_study_id"
            )
        elif current:
            status = "current_only_record"
        else:
            status = "old_only_record"
        study_rows.append(
            {
                "record_id": record_id,
                "status": status,
                "old_study_ids": ";".join(old_studies),
                "current_study_ids": ";".join(current_studies),
                "title": (old or current)[0].get("title"),
                "old_routes": len(old),
                "current_routes": len(current),
            }
        )

    plausible_edges = [row for row in all_candidates if row["accepted_by_rule"]]
    plausible_old_degree = Counter(row["old_route_id"] for row in plausible_edges)
    plausible_current_degree = Counter(row["current_route_id"] for row in plausible_edges)
    for row in all_candidates:
        row["split_candidate_degree"] = plausible_old_degree[row["old_route_id"]]
        row["merge_candidate_degree"] = plausible_current_degree[row["current_route_id"]]

    primary_old_ids = [row["old_route_id"] for row in all_primary]
    primary_current_ids = [row["current_route_id"] for row in all_primary]
    if len(primary_old_ids) != len(set(primary_old_ids)):
        raise RuntimeError("Primary migration links reuse an old route")
    if len(primary_current_ids) != len(set(primary_current_ids)):
        raise RuntimeError("Primary migration links reuse a current route")
    if len(route_ledger) != len(shared_old) + len(shared_current) - len(all_primary):
        raise RuntimeError("Route migration ledger does not reconcile both versions")
    if not all(
        row["status"] == "shared_stable_study_id"
        for row in study_rows
        if row["record_id"] in shared_records
    ):
        raise RuntimeError("A shared record changed study identity")

    summary = {
        "schema_version": 1,
        "created_at": args.created_at or now_iso(),
        "reproduction_command": (
            ".venv-docling/bin/python scripts/build_taxonomy_migration_ledger.py "
            f"--created-at {args.created_at or '<ISO_TIMESTAMP>'} --force"
        ),
        "implementation": {
            "path": portable_path(Path(__file__)),
            "sha256": sha256(Path(__file__).resolve()),
            "python_version": sys.version.split()[0],
            "requirements": {
                "path": "scripts/docling/requirements-docling.txt",
                "sha256": sha256(ROOT / "scripts/docling/requirements-docling.txt"),
            },
        },
        "algorithm": {
            "version": ALGORITHM_VERSION,
            "llm_used": False,
            "assignment": "scipy.optimize.linear_sum_assignment(maximize=True), per record",
            "scipy_version": scipy.__version__,
            "weights": SCORE_WEIGHTS,
            "candidate_floor": MIN_CANDIDATE_SCORE,
            "candidate_limit_per_side": TOP_CANDIDATES_PER_ROUTE,
            "acceptance_rule": (
                "score>=0.72 OR score>=0.60 with stable model_id and exact structural core "
                "OR score>=0.65 with model-name similarity>=0.80 and exact family/subtype"
            ),
        },
        "inputs": {
            "old": {
                "path": portable_path(old_path),
                "sha256": sha256(old_path),
                "records": len(old_records),
                "studies": len({row["study_id"] for row in old_routes}),
                "models": len({row["model_id"] for row in old_routes}),
                "configurations": len(
                    {row["configuration_id"] for row in old_routes}
                ),
                "routes": len(old_routes),
            },
            "current": {
                "path": portable_path(current_path),
                "sha256": sha256(current_path),
                "records": len(current_records),
                "studies": len({row["study_id"] for row in current_routes}),
                "models": len({row["model_id"] for row in current_routes}),
                "configurations": len(
                    {row["configuration_id"] for row in current_routes}
                ),
                "routes": len(current_routes),
            },
        },
        "shared_cohort": {
            "records": len(shared_records),
            "stable_study_ids": sum(
                row["status"] == "shared_stable_study_id" for row in study_rows
            ),
            "old_routes": len(shared_old),
            "current_routes": len(shared_current),
            "route_delta": len(shared_current) - len(shared_old),
            "accepted_primary_route_links": len(all_primary),
            "high_confidence_primary_links": sum(
                row["confidence"] == "high" for row in all_primary
            ),
            "moderate_confidence_primary_links": sum(
                row["confidence"] == "moderate" for row in all_primary
            ),
            "old_routes_without_accepted_primary_link": len(shared_old)
            - len(all_primary),
            "current_routes_without_accepted_primary_link": len(shared_current)
            - len(all_primary),
            "old_routes_with_multiple_plausible_current_links": sum(
                degree > 1 for degree in plausible_old_degree.values()
            ),
            "current_routes_with_multiple_plausible_old_links": sum(
                degree > 1 for degree in plausible_current_degree.values()
            ),
            "records_increased": sum(
                row["route_delta"] > 0 and row["record_id"] in shared_records
                for row in record_summaries
            ),
            "records_unchanged": sum(
                row["route_delta"] == 0 and row["record_id"] in shared_records
                for row in record_summaries
            ),
            "records_decreased": sum(
                row["route_delta"] < 0 and row["record_id"] in shared_records
                for row in record_summaries
            ),
        },
        "new_records": {
            "count": len(current_records - old_records),
            "routes": sum(
                len(current_by_record[record_id])
                for record_id in current_records - old_records
            ),
            "record_ids": sorted(current_records - old_records),
        },
        "model_mapping": entity_mapping_stats(
            "model", model_ledger, shared_old, shared_current
        ),
        "configuration_mapping": entity_mapping_stats(
            "configuration", configuration_ledger, shared_old, shared_current
        ),
        "largest_absolute_record_deltas": sorted(
            [row for row in record_summaries if row["record_id"] in shared_records],
            key=lambda row: (-abs(int(row["route_delta"])), row["record_id"]),
        )[:15],
    }

    write_csv(output / "study_migration.csv", study_rows)
    write_csv(output / "model_migration.csv", model_ledger)
    write_csv(output / "configuration_migration.csv", configuration_ledger)
    write_csv(output / "route_migration.csv", route_ledger)
    write_csv(output / "route_candidate_edges.csv", all_candidates)
    write_csv(
        output / "record_summary.csv",
        sorted(record_summaries, key=lambda row: row["record_id"]),
    )
    write_jsonl(
        output / "record_review_packets.jsonl",
        sorted(
            review_packets,
            key=lambda row: (-abs(row["delta"]), row["record_id"]),
        ),
    )
    write_json(output / "migration_summary.json", summary)

    largest = summary["largest_absolute_record_deltas"]
    priority_lines = [
        "# Priority migration review",
        "",
        "This queue is sorted by absolute route-count change. Automated links are",
        "candidate lineage, not scientific ground truth; inspect the corresponding",
        "packet in `record_review_packets.jsonl` before resolving a split or merge.",
        "",
        "| Record | Old | Current | Delta | Linked | Old unmatched | Current unmatched |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in largest:
        priority_lines.append(
            f"| `{row['record_id']}` | {row['old_routes']} | {row['current_routes']} | "
            f"{row['route_delta']:+d} | {row['accepted_primary_links']} | "
            f"{row['old_unmatched']} | {row['current_unmatched']} |"
        )
    (output / "priority_review.md").write_text(
        "\n".join(priority_lines) + "\n", encoding="utf-8"
    )

    readme = f"""# Taxonomy migration ledger

This directory compares the original 52-record taxonomy with the corrected
55-record full-cohort classification. It addresses cross-version interpretability;
it does not modify either canonical input and does not invoke an LLM.

## Denominators

- Shared records: {summary['shared_cohort']['records']}.
- Old routes in those records: {summary['shared_cohort']['old_routes']}.
- Current routes in those records: {summary['shared_cohort']['current_routes']}.
- Net route change: {summary['shared_cohort']['route_delta']:+d}.
- Current-only records/routes: {summary['new_records']['count']}/{summary['new_records']['routes']}.
- Accepted conservative primary route links: {summary['shared_cohort']['accepted_primary_route_links']}.
- Mapped old/current models: {summary['model_mapping']['mapped_old_entities']}/{summary['model_mapping']['mapped_current_entities']}.
- Mapped old/current configurations: {summary['configuration_mapping']['mapped_old_entities']}/{summary['configuration_mapping']['mapped_current_entities']}.

## Interpretation contract

Study identity is compared exactly. Model and configuration ledgers preserve stable
IDs and aggregate support from accepted route links. Route IDs are regenerated
content hashes, so route lineage is estimated conservatively from controlled taxonomy
fields and normalized text. Maximum-weight assignment prevents a convenient new route
from being used as the primary match for several old routes. Low-scoring assignments
are not forced; top alternative candidates remain in `route_candidate_edges.csv` so
possible split/merge cases are visible.

The automated ledger establishes where versions are stable, reworded, structurally
changed, added, consolidated, or ambiguous. It cannot determine which annotation is
scientifically preferable and must not be reported as human validation.

## Reproduce

```bash
.venv-docling/bin/python scripts/build_taxonomy_migration_ledger.py \\
  --created-at {args.created_at or '<ISO_TIMESTAMP>'} --force
```

## Files

- `study_migration.csv`: exact record/study continuity, including three new records.
- `model_migration.csv`: stable and route-supported model mappings.
- `configuration_migration.csv`: stable and route-supported configuration mappings.
- `route_migration.csv`: accepted primary links plus all unmatched routes.
- `route_candidate_edges.csv`: scored alternatives and split/merge degrees.
- `record_summary.csv`: per-record denominators and family/model changes.
- `record_review_packets.jsonl`: complete compact route evidence for manual review.
- `priority_review.md`: largest absolute count changes.
- `migration_summary.json`: source hashes, algorithm, thresholds, and aggregate counts.

See `largest_delta_review.md` for the separate analyst review of the largest changes.
"""
    (output / "README.md").write_text(readme, encoding="utf-8")

    artifacts = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "artifact_hashes.json":
            artifacts.append(
                {
                    "path": path.name,
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    write_json(output / "artifact_hashes.json", artifacts)
    print(json.dumps(summary["shared_cohort"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
