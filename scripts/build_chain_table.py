"""One row per agent-decomposed atlas route (release 1.2.1): atlas labels + ordered step decisions + parameter status.

Pilot papers (author-curated, not route-indexed) and the withdrawn OKR-Cell record are excluded.
  python3 scripts/build_chain_table.py
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import operation_decomposition_v3 as v3  # noqa: E402

REL = ROOT / "analysis/operation_decomposition_v31_2026-10-12"
OUT = ROOT / "analysis/design_taxonomy_2026-10-13/chains.json"
AGENT = json.loads((ROOT / "analysis/operation_decomposition_2026-10-07/stabilization/all50_set.json").read_text())


def main():
    import argparse
    global REL, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-dir", type=Path, default=REL)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    REL, OUT = (a.release_dir if a.release_dir.is_absolute() else ROOT / a.release_dir), (a.out if a.out.is_absolute() else ROOT / a.out)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    atlas = json.loads((ROOT / "docs/input-representation-atlas/data/atlas.json").read_text())
    years = {}
    rows = []
    for m in atlas["architectures"]:
        if m["record_id"] not in AGENT:
            continue
        dec = json.loads((REL / "records" / m["record_id"] / "consensus_decisions.json").read_text())
        params = json.loads((REL / "records" / m["record_id"] / "parameter_consensus.json").read_text())
        by_step = {d["step_id"]: d for d in dec["decisions"]}
        ties = set(dec["ties"])
        skel = {r["route_id"]: r for cfg in v3.atlas_skeleton(m["record_id"]) for r in cfg["routes"]}
        for r in m["routes"]:
            sk = skel[r["route_id"]]
            steps = []
            for sid, el in zip(sk["expected_step_ids"], sk["transformation_chain_verbatim"]):
                d = by_step[sid]
                cat = "consensus_tie" if sid in ties else d["category"]
                calls = []
                for j, c in enumerate(d["calls"] if cat == "library_operation" else [], 1):
                    ps = {k.rsplit("#", 1)[1]: v["status"] for k, v in params.items() if k.startswith(f"{sid}#c{j}#")}
                    calls.append({"operation_id": c["operation_id"], "parameter_status": ps})
                steps.append({"step_id": sid, "chain_element": el, "category": cat, "calls": calls,
                              "support": dec["support"].get(sid, 0)})
            rows.append({"record_id": m["record_id"], "model_id": m["model_id"], "model_name": m["model_name"],
                         "doi": m["doi"], "collection_batch_id": m["collection_batch_id"],
                         "configuration_id": r["configuration_id"], "route_id": r["route_id"], "route_label": r["route_label"],
                         "lifecycle_phase": r["lifecycle_phase"], "source_object": r["source_object_verbatim"],
                         "source_modality": r["source_modality_normalized"], "model_visible_form": r["model_visible_form_verbatim"],
                         "carrier_family": r["carrier_family"], "carrier_subtype": r["carrier_subtype"],
                         "fusion_topology": r["fusion_topology"], "text_role": r["text_role"],
                         "insertion_or_fusion": r["insertion_or_fusion_verbatim"], "chain_recorded": sk["chain_recorded"],
                         "steps": steps})
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    print(json.dumps({"routes": len(rows), "papers": len({r['record_id'] for r in rows}), "models": len({r['model_id'] for r in rows}),
                      "steps": sum(len(r['steps']) for r in rows)}))


if __name__ == "__main__":
    main()
