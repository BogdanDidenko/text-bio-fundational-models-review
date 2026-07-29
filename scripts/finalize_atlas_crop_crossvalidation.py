#!/usr/bin/env python3
"""Apply final preview verdicts and freeze the validated atlas crop ledger."""

from __future__ import annotations

import glob
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


def final_preview_reviews() -> dict[str, dict[str, Any]]:
    reviews = {}
    for path_value in glob.glob(str(RUN_ROOT / "subagents/final_preview_validator/batch_*/response.json")):
        for review in read_json(Path(path_value))["reviews"]:
            reviews[review["model_id"]] = review
    return reviews


def main() -> int:
    provisional = read_json(RUN_ROOT / "provisional_crossvalidated_crop_ledger.json")
    preview_reviews = final_preview_reviews()
    final_rejects = {
        item["model_id"]
        for item in preview_reviews.values()
        if item["decision"] == "reject"
    }
    if len(preview_reviews) != 89 or final_rejects != {"model_e113b973b85a"}:
        raise RuntimeError("Unexpected final preview validation coverage or rejects")

    final_ledger = []
    for item in provisional:
        model_id = item["model_id"]
        cross_validation = dict(item.get("cross_validation") or {})
        preview = preview_reviews.get(model_id)
        if preview:
            cross_validation["final_preview_validation"] = preview
        if model_id in final_rejects:
            adjudication = read_json(
                RUN_ROOT / "subagents/adjudicator" / model_id / "response.json"
            )["adjudication"]
            if adjudication["decision"] != "no_suitable_figure":
                raise RuntimeError(f"Final reject did not resolve to no_suitable_figure: {model_id}")
            cross_validation["final_reject_adjudication"] = adjudication
            final_ledger.append(
                {
                    "model_id": model_id,
                    "record_id": item["record_id"],
                    "status": "no_suitable_figure",
                    "figure": None,
                    "crop_box": None,
                    "panel_label": "",
                    "visible_input_object": "",
                    "visible_model_interface": "",
                    "figure_suitability": "unsuitable",
                    "confidence": adjudication["confidence"],
                    "rationale": adjudication["rationale"],
                    "annotation_pass": "final_preview_reject_plus_gpt54_no_figure",
                    "cross_validation": cross_validation,
                }
            )
            continue
        if item["status"] == "cropped_source_figure":
            if preview is None or preview["decision"] != "pass":
                raise RuntimeError(f"Accepted crop lacks final pass: {model_id}")
            item = dict(item)
            item["annotation_pass"] = f"{item['annotation_pass']}__final_preview_pass"
            item["cross_validation"] = cross_validation
        final_ledger.append(item)

    if len(final_ledger) != 111 or len({item["model_id"] for item in final_ledger}) != 111:
        raise RuntimeError("Final ledger must cover 111 unique model IDs")
    crops = [item for item in final_ledger if item["status"] == "cropped_source_figure"]
    no_figure = [item for item in final_ledger if item["status"] == "no_suitable_figure"]
    if len(crops) != 88 or len(no_figure) != 23:
        raise RuntimeError("Expected 88 validated crops and 23 explicit no-figure cases")
    for item in crops:
        crop = item["crop_box"]
        if crop["x"] + crop["width"] > 1.0001 or crop["y"] + crop["height"] > 1.0001:
            raise RuntimeError(f"Out-of-bounds final crop: {item['model_id']}")

    write_json(RUN_ROOT / "crossvalidated_crop_ledger.json", final_ledger)
    source_counts = Counter(item["annotation_pass"].split("__final_preview_pass")[0] for item in crops)
    report = {
        "status": "complete",
        "model_count": len(final_ledger),
        "validated_crops": len(crops),
        "explicit_no_suitable_figure": len(no_figure),
        "validator_a_coverage": 111,
        "validator_b_coverage": 111,
        "unanimous_initial_accept": 74,
        "strong_model_adjudications": 38,
        "replacement_full_resolution_crops": 5,
        "final_preview_validation_coverage": len(preview_reviews),
        "final_preview_pass": sum(item["decision"] == "pass" for item in preview_reviews.values()),
        "final_preview_reject": len(final_rejects),
        "final_rejects_resolved": len(final_rejects),
        "accepted_crop_provenance": dict(source_counts),
        "acceptance_checks": {
            "all_111_models_accounted_for": True,
            "every_accepted_crop_has_final_rendered_preview_pass": True,
            "every_non_pass_is_excluded_or_adjudicated": True,
            "no_out_of_bounds_crop": True,
            "no_hidden_chain_of_thought_claimed": True,
        },
    }
    write_json(RUN_ROOT / "crossvalidation_final_report.json", report)
    (RUN_ROOT / "CROP_CROSSVALIDATION.md").write_text(
        "# Atlas crop cross-validation\n\n"
        "The previous one-pass crop ledger was treated as a baseline and was not overwritten. "
        "Every model decision was independently reviewed by two blind `gpt-5.4-mini` roles. "
        "All non-unanimous-pass cases were resolved by a separate `gpt-5.4` visual adjudicator "
        "with access to the current crop and all source-paper figures. Replacement figures were "
        "cropped from their full-resolution originals. A third blind reviewer then inspected the "
        "exact rendered final crop previews. Its single rejection was separately adjudicated and "
        "removed from the visual atlas.\n\n"
        f"- Models accounted for: {report['model_count']}\n"
        f"- Validated original-paper crops: {report['validated_crops']}\n"
        f"- Explicit no-suitable-figure cases: {report['explicit_no_suitable_figure']}\n"
        f"- Initial blind coverage: {report['validator_a_coverage']} + {report['validator_b_coverage']}\n"
        f"- Strong-model adjudications: {report['strong_model_adjudications']}\n"
        f"- Final rendered previews checked: {report['final_preview_validation_coverage']}\n"
        f"- Final rendered preview passes: {report['final_preview_pass']}\n"
        f"- Final rejection resolved as no-suitable-figure: {report['final_preview_reject']}\n\n"
        "A crop is accepted only when it visibly supports at least one grounded actual-model-input "
        "route for the exact model. Output-only panels, performance plots, unrelated architectures, "
        "and downstream use of another model's embeddings are excluded.\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
