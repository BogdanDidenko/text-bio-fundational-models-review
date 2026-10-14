"""Integrated analysis dataset (release 1.3.0) for the discovery analyses.

Tables (parquet, analysis/discovery_2026-10-14/):
  models.parquet  one row per atlas model (109): paper, year, modalities, families, phases, motifs, archetypes
  routes.parquet  one row per atlas route (585): atlas labels, axes/archetype (agent routes), chain summary
  steps.parquet   one row per decomposed step (agent papers): chain element, category, operations, support, evidence
  slots.parquet   one row per parameter slot (agent papers): operation, parameter, status, stated value, evidence
Pilot papers keep atlas-level rows; their operation graphs are in the public assemblies.

  python3 scripts/build_integrated_dataset.py
"""
import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/discovery_2026-10-14"
REL = ROOT / "analysis/operation_decomposition_v32_2026-10-14"
ATLAS = ROOT / "docs/input-representation-atlas/data/atlas.json"
CHAINS = ROOT / "analysis/motif_library_2026-10-14/chains_1.3.0.json"
MOTIFS = ROOT / "analysis/motif_library_2026-10-14/motifs.json"
CODEBOOK = ROOT / "analysis/design_taxonomy_2026-10-13/taxonomy_codebook.csv"
CHARTING = ROOT / "analysis/review_synthesis_2026-10-07/charting_table_models.csv"
WITHDRAWN = {"full_2026-07-06__rec_001277"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    atlas = json.loads(ATLAS.read_text())
    chart = pd.read_csv(CHARTING)
    year = chart.groupby("record_id").year.first().to_dict()
    cb = pd.read_csv(CODEBOOK).set_index(["record_id", "route_id"])
    motifs = json.loads(MOTIFS.read_text())
    model_motifs = json.loads((ROOT / "analysis/motif_library_2026-10-14/model_motif_composition.json").read_text())["model_motifs"]
    chains = {(c["record_id"], c["route_id"]): c for c in json.loads(CHAINS.read_text())}

    models, routes, steps, slots = [], [], [], []
    for m in atlas["architectures"]:
        rec = m["record_id"]
        if rec in WITHDRAWN:
            continue
        mm = model_motifs.get(f"{rec}|{m['model_name']}", [])
        arch = sorted({cb.loc[(rec, r["route_id"]), "archetype"] for r in m["routes"] if (rec, r["route_id"]) in cb.index} - {"TEXT"})
        models.append({"record_id": rec, "model_id": m["model_id"], "model_name": m["model_name"], "paper_title": m["paper_title"],
                       "doi": m["doi"], "year": year.get(rec), "n_routes": len(m["routes"]),
                       "n_configurations": m["configuration_count"], "families": "|".join(m["families"]),
                       "modalities": "|".join(m["modalities"]), "lifecycle_phases": "|".join(m["lifecycle_phases"]),
                       "fusion_topologies": "|".join(m["fusion_topologies"]), "text_roles": "|".join(m["text_roles"]),
                       "motifs": "|".join(mm), "archetypes": "|".join(arch), "agent_decomposed": rec not in {"full_2026-07-06__rec_000771", "full_2026-07-06__rec_001319", "full_2026-07-06__rec_003517", "full_2026-07-06__rec_003852"}})
        for r in m["routes"]:
            key = (rec, r["route_id"])
            row = {"record_id": rec, "model_id": m["model_id"], "model_name": m["model_name"], "year": year.get(rec),
                   **{k: r[k] for k in ("route_id", "configuration_id", "route_label", "lifecycle_phase", "task_or_configuration_verbatim",
                                        "source_object_verbatim", "source_object_normalized", "source_modality_normalized",
                                        "model_visible_form_verbatim", "carrier_family", "carrier_subtype", "insertion_or_fusion_verbatim",
                                        "fusion_topology", "text_role", "input_status", "evidence_quote", "section_heading")},
                   "chain_verbatim": " | ".join(r["transformation_chain_verbatim"] or [])}
            if key in cb.index:
                c = cb.loc[key]
                row.update({k: c[k] for k in ("A1_carrier_formation", "A2_interface", "A3_information", "A3_modifiers", "A4_text_role",
                                              "A5_transparency", "opaque_step_share", "stated_parameter_share", "archetype", "operation_chain")})
            routes.append(row)
            ch = chains.get(key)
            if not ch:
                continue
            dec = json.loads((REL / "records" / rec / "consensus_decisions.json").read_text())
            by = {d["step_id"]: d for d in dec["decisions"]}
            params = json.loads((REL / "records" / rec / "parameter_consensus.json").read_text())
            for k, s in enumerate(ch["steps"], 1):
                d = by[s["step_id"]]
                steps.append({"record_id": rec, "model_name": m["model_name"], "route_id": r["route_id"], "step_index": k,
                              "n_steps": len(ch["steps"]), "step_id": s["step_id"], "chain_element": s["chain_element"],
                              "category": s["category"], "operations": "+".join(c["operation_id"] for c in s["calls"]),
                              "support": dec["support"].get(s["step_id"], 0), "rationale": d.get("rationale"),
                              "uncertainty": d.get("uncertainty"),
                              "evidence": " || ".join(e["quote"] for e in d.get("evidence", []))})
                for j, c in enumerate(d["calls"] if d["category"] == "library_operation" else [], 1):
                    for sid, a in params.items():
                        if sid.startswith(f"{s['step_id']}#c{j}#"):
                            slots.append({"record_id": rec, "model_name": m["model_name"], "route_id": r["route_id"],
                                          "step_id": s["step_id"], "operation_id": c["operation_id"], "parameter": sid.rsplit("#", 1)[1],
                                          "status": a["status"], "value": a.get("value"), "support": a.get("support"),
                                          "evidence": " || ".join(e["quote"] for e in a.get("evidence", []))})
    for name, rows in (("models", models), ("routes", routes), ("steps", steps), ("slots", slots)):
        pd.DataFrame(rows).to_parquet(OUT / f"{name}.parquet", index=False)
    slot_dedup = pd.DataFrame(slots).drop_duplicates(["record_id", "step_id", "operation_id", "parameter"])
    print(json.dumps({"models": len(models), "routes": len(routes), "steps": len(steps), "slots_rows": len(slots),
                      "unique_slots": len(slot_dedup), "papers": len({m["record_id"] for m in models})}))


if __name__ == "__main__":
    main()
