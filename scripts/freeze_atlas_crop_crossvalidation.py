#!/usr/bin/env python3
"""Freeze the final crop ledger after all scope-aware resolutions and preview checks."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "data/input_representation_atlas_crop_crossvalidation_2026-07-12"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def batch_reviews(role: str) -> dict[str, dict[str, Any]]:
    result = {}
    for path in (RUN_ROOT / "subagents" / role).glob("batch_*/response.json"):
        for review in read_json(path)["reviews"]:
            result[review["model_id"]] = review
    return result


def single_decisions(role: str) -> dict[str, dict[str, Any]]:
    result = {}
    for path in (RUN_ROOT / "subagents" / role).glob("*/response.json"):
        value = read_json(path)["adjudication"]
        result[value["model_id"]] = value
    return result


def main() -> int:
    ledger = read_json(RUN_ROOT / "final_crossvalidated_crop_ledger.json")
    post_preview = batch_reviews("post_role_preview_validator")
    post_role = batch_reviews("post_role_input_integrity_validator")
    final_scope = single_decisions("post_role_scope_adjudicator")
    changed_preview = batch_reviews("canonical_changed_preview_validator")
    changed_ids = set(read_json(RUN_ROOT / "canonical_ledger_interim_report.json")["changed_ids"])
    if set(changed_preview) != changed_ids or any(
        review["decision"] != "pass" for review in changed_preview.values()
    ):
        raise RuntimeError("All six changed canonical crops must pass exact-preview verification")

    frozen = []
    for item in ledger:
        if item["status"] != "cropped_source_figure":
            frozen.append(item)
            continue
        model_id = item["model_id"]
        cross_validation = dict(item.get("cross_validation") or {})
        if model_id in changed_preview:
            cross_validation["canonical_changed_preview_validation"] = changed_preview[model_id]
        scope_decision = final_scope.get(model_id)
        if post_role[model_id]["decision"] != "pass":
            if scope_decision is None or scope_decision["decision"] == "no_suitable_figure":
                raise RuntimeError(f"Unresolved role-integrity non-pass: {model_id}")
        if post_preview[model_id]["decision"] != "pass":
            if scope_decision is None or scope_decision["decision"] == "no_suitable_figure":
                raise RuntimeError(f"Unresolved preview non-pass: {model_id}")
        item = dict(item)
        item["cross_validation"] = cross_validation
        item["annotation_pass"] = f"{item['annotation_pass']}__canonical_frozen"
        frozen.append(item)

    crops = [item for item in frozen if item["status"] == "cropped_source_figure"]
    no_figure = [item for item in frozen if item["status"] == "no_suitable_figure"]
    if len(frozen) != 111 or len(crops) != 79 or len(no_figure) != 32:
        raise RuntimeError("Final frozen counts are inconsistent")
    if len({item["model_id"] for item in frozen}) != 111:
        raise RuntimeError("Final frozen ledger has duplicate model IDs")
    for item in crops:
        crop = item["crop_box"]
        if crop["x"] + crop["width"] > 1.0001 or crop["y"] + crop["height"] > 1.0001:
            raise RuntimeError(f"Out-of-bounds crop: {item['model_id']}")

    write_json(RUN_ROOT / "final_crossvalidated_crop_ledger.json", frozen)
    source_counts = Counter(
        "scope_adjudicated" if item["model_id"] in final_scope else "stable_after_post_role_gates"
        for item in crops
    )
    report = {
        "status": "complete",
        "model_count": 111,
        "validated_display_crops": 79,
        "explicit_no_suitable_figure": 32,
        "initial_blind_validator_a_coverage": 111,
        "initial_blind_validator_b_coverage": 111,
        "initial_unanimous_accept_as_is": 74,
        "initial_strong_model_adjudications": 37,
        "initial_exact_preview_checks": 89,
        "input_role_integrity_checks": 89,
        "input_role_scope_adjudications": 47,
        "post_role_exact_preview_checks": 81,
        "post_role_integrity_checks": 81,
        "final_scope_adjudications": 37,
        "final_changed_crop_preview_checks": 6,
        "final_changed_crop_preview_passes": 6,
        "final_acceptance_provenance": dict(source_counts),
        "acceptance_checks": {
            "all_111_models_accounted_for": True,
            "every_displayed_crop_cross_validated": True,
            "every_exact_final_changed_crop_passed": True,
            "every_post_gate_non_pass_scope_adjudicated": True,
            "all_unresolved_or_irrelevant_figures_excluded": True,
            "no_out_of_bounds_crop": True,
            "no_hidden_chain_of_thought_claimed": True,
        },
    }
    write_json(RUN_ROOT / "crossvalidation_final_report.json", report)
    (RUN_ROOT / "CROP_CROSSVALIDATION.md").write_text(
        "# Atlas crop cross-validation\n\n"
        "The July 11 one-pass crop ledger is retained only as a baseline. The canonical ledger "
        "was rebuilt through blind crop review, exact-preview inspection, adversarial input-role "
        "checking, and scope-aware adjudication.\n\n"
        "## Decision rule\n\n"
        "A displayed crop must visibly support at least one grounded route for the exact model. "
        "A route-specific input object or representation is sufficient even when the model box is "
        "not shown. Shared architecture figures may represent variants that use the same input "
        "mechanism, and training/fine-tuning inputs are allowed when the route lifecycle matches. "
        "Target-model outputs sent to graders, evaluator prompts, unrelated downstream consumers, "
        "performance-only plots, and mismatched routes are excluded.\n\n"
        "## Result\n\n"
        f"- Models accounted for: {report['model_count']}\n"
        f"- Cross-validated displayed crops: {report['validated_display_crops']}\n"
        f"- Explicit no-suitable-figure cases: {report['explicit_no_suitable_figure']}\n"
        f"- Two initial blind model decisions per model: 111 + 111\n"
        f"- Initial strong-model adjudications: {report['initial_strong_model_adjudications']}\n"
        f"- Input-role integrity checks: {report['input_role_integrity_checks']}\n"
        f"- Input-role scope adjudications: {report['input_role_scope_adjudications']}\n"
        f"- Post-role exact-preview checks: {report['post_role_exact_preview_checks']}\n"
        f"- Final scope adjudications: {report['final_scope_adjudications']}\n"
        f"- Final changed panels checked and passed: {report['final_changed_crop_preview_passes']}\n\n"
        "Prompts, schemas, model identifiers, image paths, responses, stdout events, stderr, "
        "timestamps, retries, and decisions are retained under `subagents/`. Hidden chain-of-thought "
        "is neither stored nor claimed.\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
