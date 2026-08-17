import sys
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_atlas_exact_preview_validation import (  # noqa: E402
    build_proposed_crop_ledger,
    crop_pixels,
    needs_adjudication,
    valid_crop_box,
)


def crop_review(decision="pass", routes=None):
    return {
        "decision": decision,
        "route_ids_supported": routes or ["route_1"],
    }


def test_crop_pixels_use_floor_start_and_ceil_end():
    assert crop_pixels({"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4}, 101, 99) == (
        10,
        19,
        31,
        41,
    )


def test_crop_box_rejects_overflow():
    assert valid_crop_box({"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4})
    assert not valid_crop_box({"x": 0.8, "y": 0.2, "width": 0.3, "height": 0.4})


def test_shared_supported_route_skips_adjudication():
    assert not needs_adjudication(crop_review(routes=["route_1"]), crop_review(routes=["route_1", "route_2"]))


def test_nonpass_or_disjoint_routes_require_adjudication():
    assert needs_adjudication(crop_review("adjust"), crop_review())
    assert needs_adjudication(crop_review(routes=["route_1"]), crop_review(routes=["route_2"]))


def test_proposed_ledger_uses_explicit_candidate_ledger(tmp_path):
    ledger_path = tmp_path / "candidate_ledger.json"
    ledger_path.write_text(
        json.dumps(
            [
                {
                    "model_id": "model_candidate",
                    "status": "no_suitable_figure",
                    "rationale": "No source figure",
                }
            ]
        )
    )

    proposed = build_proposed_crop_ledger(tmp_path, [], ledger_path)

    assert proposed[0]["model_id"] == "model_candidate"
    assert proposed[0]["exact_preview_validation"]["status"] == "not_applicable_no_crop"
