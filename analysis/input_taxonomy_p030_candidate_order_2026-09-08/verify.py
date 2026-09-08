"""Verify the bounded candidate-order correction; never open the scoring key."""

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "b3c38ac74073aa266bb133b2ffacd29c749e1d18"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(ROOT / "scripts"))
    from apply_atlas_review_amendments import reviewed_view
    record_path = ROOT / "data/input_representation_audit_amendments/2026-09-08_p030_candidate_order.json"
    record = json.loads(record_path.read_text())
    code = HERE / "sources/match_qa.py"
    assert sha(code) == record["supporting_sources"][0]["sha256"]
    module = ast.parse(code.read_text())
    function = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == "build_one_qa")
    assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "sorted" and isinstance(n.args[0], ast.Name) and n.args[0].id == "chosen_types" for n in ast.walk(function))
    paper = ROOT / record["evidence_source"]["path"]
    assert sha(paper) == record["evidence_source"]["sha256"]
    assert "randomly shuffled to remove positional biases" in paper.read_text().splitlines()[60]
    baseline = json.loads(subprocess.check_output(["git", "show", BASE + ":docs/input-representation-atlas/data/atlas.json"], cwd=ROOT))
    atlas = json.loads((ROOT / "docs/input-representation-atlas/data/atlas.json").read_text())
    expected = reviewed_view(atlas, sorted((ROOT / "data/input_representation_audit_amendments").glob("*.json")), ROOT)
    assert atlas == expected, "Reviewed projection is stale"
    old_routes = {r["route_id"]: r for m in baseline["architectures"] for r in m["routes"]}
    new_routes = {r["route_id"]: r for m in atlas["architectures"] for r in m["routes"]}
    assert old_routes.keys() == new_routes.keys()
    changed = [key for key in old_routes if old_routes[key] != new_routes[key]]
    assert changed == [record["route_id"]], changed
    current = new_routes[record["route_id"]]
    for field in old_routes[record["route_id"]]:
        if field != "uncertainty":
            assert current[field] == old_routes[record["route_id"]][field], field
    assert current["reviewed_transformation_chain"] == record["updates"]["reviewed_transformation_chain"]
    assert atlas["graph"] == baseline["graph"]
    assert atlas["families"] == baseline["families"]
    assert atlas["filter_values"] == baseline["filter_values"]
    for previous, updated in zip(baseline["architectures"], atlas["architectures"]):
        assert previous["model_id"] == updated["model_id"]
        assert previous["figure"] == updated["figure"]
    protected = [
        "data/living_catalog/taxonomy_rerun_preflight_2026-08-12/snapshot_full_55_semantic_correction_2026-08-17/route_annotations.jsonl",
        "data/living_catalog/taxonomy_rerun_preflight_2026-08-12/snapshot_full_55_semantic_correction_2026-08-17/evidence_ledger.jsonl",
        "data/living_catalog/taxonomy_rerun_preflight_2026-08-12/taxonomy/adjudication/shard_02/records/full_2026-07-06__rec_001617_76b0056d59c3/adjudicated_routes.json",
        "data/living_catalog/taxonomy_rerun_preflight_2026-08-12/taxonomy/adjudication/shard_02/records/full_2026-07-06__rec_001617_76b0056d59c3/prompt.txt",
        "data/input_representation_taxonomy_2026-07-11/taxonomy_tree.json",
        "scripts/build_input_representation_atlas.py",
        "protocol/LIVING_REVIEW_RUNBOOK.md",
        "protocol/living_review_method_lock_v1.json",
    ]
    hashes = {}
    for file in protected:
        original = subprocess.check_output(["git", "show", BASE + ":" + file], cwd=ROOT)
        assert (ROOT / file).read_bytes() == original, file
        hashes[file] = sha(ROOT / file)
    output = {"date": "2026-09-08", "base_commit": BASE, "changed_routes": changed, "original_reported_transformation_preserved": True, "reviewed_transformation_is_separately_named": True, "classification_graph_filters_and_figures_preserved": True, "raw_artifact_and_method_hashes": hashes, "source_code_sha256": sha(code), "audit_status": "P030 remains held", "sealed_key_opened": False, "real_audit_scored": False, "author_code_executed": False}
    (HERE / "verification.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
