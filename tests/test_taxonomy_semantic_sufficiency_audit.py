import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_taxonomy_semantic_sufficiency_audit import (  # noqa: E402
    FIELD_NAMES,
    field_verdicts,
    is_risky_route,
    needs_adjudication,
    sanitize_supporting_quotes,
    validate_reviews,
)


def review(overall="sufficient", action="retain_as_is", verdict="supported"):
    return {
        "route_id": "route_1",
        "overall_sufficiency": overall,
        "recommended_action": action,
        "field_reviews": [
            {"field": field, "verdict": verdict, "explanation": "supported"}
            for field in FIELD_NAMES
        ],
        "supporting_quotes": ["exact evidence"],
        "unsupported_assertions": [],
        "concise_rationale": "supported",
        "confidence": "high",
    }


def test_risky_union_includes_dense_only_and_inferred():
    assert is_risky_route({"dense_candidate_refs": ["x"], "source_candidate_refs": []})
    assert is_risky_route({"evidence_status": "inferred"})
    assert not is_risky_route(
        {"dense_candidate_refs": ["x"], "source_candidate_refs": ["direct"], "evidence_status": "explicit_text"}
    )


def test_agreed_complete_reviews_skip_adjudication():
    first = review()
    second = review()
    assert field_verdicts(first) == field_verdicts(second)
    assert not needs_adjudication(first, second)


def test_any_partial_field_requires_adjudication():
    first = review()
    second = review()
    second["field_reviews"][2]["verdict"] = "partially_supported"
    assert needs_adjudication(first, second)


def test_quote_and_complete_field_contract_are_validated():
    response = {"reviewer_role": "test", "reviews": [review()]}
    validate_reviews(response, {"route_1"}, "This contains exact evidence in the paper.")


def test_outer_typographic_quote_wrappers_do_not_break_verbatim_match():
    response = {"reviewer_role": "test", "reviews": [review()]}
    response["reviews"][0]["supporting_quotes"] = ["“exact evidence”"]
    validate_reviews(response, {"route_1"}, "This contains exact evidence in the paper.")


def test_unmatched_extra_quote_is_removed_when_partial_review_has_verified_quote():
    response = {"reviewer_role": "test", "reviews": [review(overall="partial", action="revise_fields")]}
    response["reviews"][0]["supporting_quotes"] = ["exact evidence", "invented ... quote"]
    cleaned, report = sanitize_supporting_quotes(response, "This contains exact evidence in the paper.")
    assert cleaned["reviews"][0]["supporting_quotes"] == ["exact evidence"]
    assert report[0]["unmatched_quotes_removed_from_validated_response"] == ["invented ... quote"]
