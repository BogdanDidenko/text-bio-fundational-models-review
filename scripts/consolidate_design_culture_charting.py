#!/usr/bin/env python3
"""Consolidate the two independent design-culture charting runs (protocol design-culture-charting-v1.1).

Outputs (in the iteration folder):
- agreement.json: per-field agreement between runs (record-level presence agreement and Cohen's kappa
  for every category, mean Jaccard for set-valued fields);
- consensus_items.csv: one row per (record, field, category) with presence in run 1 / run 2;
- comparisons.csv, tests.csv, generators.csv, backbones.csv, encoders.csv: item tables from both runs
  with evidence, for steward adjudication.
"""
import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "analysis/design_culture_charting_2026-10-14"

SET_FIELDS = {
    "evaluation_formats": "format", "outputs": "output", "biology_dependence_tests": "test_type",
    "representation_rationale": "reason", "connectors": "type",
}


def load(run_dir):
    docs = {}
    for status in (run_dir / "records").glob("*/status.json"):
        rec = status.parent.name
        s = json.loads(status.read_text())
        if s["status"] == "valid":
            docs[rec] = json.loads((status.parent / "final_document.json").read_text())
    return docs


def norm_name(name):
    n = name.lower()
    n = re.sub(r"\(.*?\)", "", n)
    n = re.sub(r"[^a-z0-9.]+", " ", n).strip()
    return n


def kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else round((po - pe) / (1 - pe), 3)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--iteration", default="v11")
    args = p.parse_args()
    out = BASE / args.iteration
    runs = {k: load(out / f"run_{k}") for k in (1, 2)}
    recs = sorted(set(runs[1]) & set(runs[2]))
    agreement = {"records_both_valid": len(recs), "run1_valid": len(runs[1]), "run2_valid": len(runs[2]), "fields": {}}
    rows = []
    for field, key in {**SET_FIELDS, "llm_state": None, "encoder_state": None, "has_comparison": None,
                       "has_synthetic_text": None}.items():
        def cats(doc):
            if field == "llm_state":
                return {b["state"] for b in doc["llm_backbones"]}
            if field == "encoder_state":
                return {b["state"] for b in doc["biological_encoders"]}
            if field == "has_comparison":
                return {"yes"} if doc["representation_comparisons"] else set()
            if field == "has_synthetic_text":
                return {"yes"} if doc["synthetic_text_generators"] else set()
            return {item[key] for item in doc[field]}
        allc = sorted(set().union(*[cats(runs[k][r]) for k in (1, 2) for r in recs]) or {"yes"})
        per_cat = {}
        for c in allc:
            a = [c in cats(runs[1][r]) for r in recs]
            b = [c in cats(runs[2][r]) for r in recs]
            per_cat[c] = {"n_run1": sum(a), "n_run2": sum(b), "agree": round(sum(x == y for x, y in zip(a, b)) / len(recs), 3),
                          "kappa": kappa(a, b)}
            for r, x, y in zip(recs, a, b):
                rows.append({"record_id": r, "field": field, "category": c, "run1": int(x), "run2": int(y)})
        jac = []
        for r in recs:
            s1, s2 = cats(runs[1][r]), cats(runs[2][r])
            jac.append(1.0 if not (s1 | s2) else len(s1 & s2) / len(s1 | s2))
        agreement["fields"][field] = {"mean_jaccard": round(sum(jac) / len(jac), 3), "categories": per_cat}
    (out / "agreement.json").write_text(json.dumps(agreement, indent=1))
    with open(out / "consensus_items.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    tables = defaultdict(list)
    for k in (1, 2):
        for r, d in runs[k].items():
            ev = lambda item: " || ".join(f"[{e['section_id']}] {e['quote']}" for e in item["evidence"])
            for i, c in enumerate(d["representation_comparisons"]):
                tables["comparisons"].append({"record_id": r, "run": k, "i": i, "kind": c["comparison_kind"], "design": c["design"],
                                              "modality": c["modality"], "arms": " | ".join(f"{a['label']} <{a['category']}>" for a in c["arms"]),
                                              "task": c["task"], "metric": c["metric"], "better_arm": c["better_arm"],
                                              "numbers": c["numbers_stated"], "summary": c["result_summary"], "evidence": ev(c)})
            for i, t in enumerate(d["biology_dependence_tests"]):
                tables["tests"].append({"record_id": r, "run": k, "i": i, "test_type": t["test_type"], "on_proposed": t["on_proposed_model"],
                                        "result": t["result"], "summary": t["result_summary"], "evidence": ev(t)})
            for i, g in enumerate(d["synthetic_text_generators"]):
                tables["generators"].append({"record_id": r, "run": k, "i": i, "name": g["name"], "name_norm": norm_name(g["name"]),
                                             "text_kind": g["text_kind"], "version_stated": g["version_stated"],
                                             "prompts": g["prompts_disclosed"], "decoding": g["decoding_params_stated"],
                                             "verification": g["verification"], "used_for": g["used_for"], "evidence": ev(g)})
            for i, b in enumerate(d["llm_backbones"]):
                tables["backbones"].append({"record_id": r, "run": k, "i": i, "name": b["name"], "size": b["size"], "state": b["state"],
                                            "vocab": b["vocabulary_extended"], "evidence": ev(b)})
            for i, b in enumerate(d["biological_encoders"]):
                tables["encoders"].append({"record_id": r, "run": k, "i": i, "name": b["name"], "state": b["state"], "evidence": ev(b)})
            for i, x in enumerate(d["representation_rationale"]):
                tables["rationale"].append({"record_id": r, "run": k, "i": i, "reason": x["reason"], "stance": x["stance"],
                                            "summary": x["summary"], "evidence": ev(x)})
            for i, x in enumerate(d["evaluation_formats"]):
                tables["evaluation"].append({"record_id": r, "run": k, "i": i, "format": x["format"], "task": x["task"], "evidence": ev(x)})
    for name, items in tables.items():
        with open(out / f"{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(items[0]))
            w.writeheader()
            w.writerows(items)
    print(json.dumps({k: v for k, v in agreement.items() if k != "fields"}))
    for field, v in agreement["fields"].items():
        print(field, v["mean_jaccard"], {c: (x["n_run1"], x["n_run2"], x["kappa"]) for c, x in v["categories"].items()})


if __name__ == "__main__":
    main()
