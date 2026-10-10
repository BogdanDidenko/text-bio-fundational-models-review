"""Per-step majority consensus over independent v3 decomposition runs, and its split-half stability.

The protocol output for a paper is the per-step majority of k independent runs (default k = 3):
  1. gate label = ordered operation ids, or '<boundary>' for every boundary category;
  2. the majority gate label wins (> k/2 runs); no majority -> '<tie>' (left for the steward);
  3. within the winning label the majority category wins (boundary steps), ties broken by the
     lowest run number; the decision (evidence, parameters) is copied from the lowest-numbered run
     holding the winning category + label, so the output is deterministic given the runs.

Stability of the protocol itself is measured split-half: consensus(runs 1..k) vs consensus(runs
k+1..2k), with the same G1-G3 definitions as GATE.md (one comparison pair per paper).

  python3 scripts/decomposition_consensus.py measure --iteration v3_h2 --set heldout2 --k 3
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import operation_decomposition_v3 as v3  # noqa: E402
from scripts.operation_decomposition import CATALOG  # noqa: E402

BASE = ROOT / "analysis/operation_decomposition_2026-10-07/stabilization"
TIE = "<tie>"


def gate_label(d):
    return tuple(c["operation_id"] for c in d["calls"]) if d["category"] == "library_operation" else ("<boundary>",)


def consensus(decision_docs):
    """decision_docs: list of v3 decision documents in run order. Returns (decision_doc, ties, support)."""
    by_run = [{d["step_id"]: d for d in doc["decisions"]} for doc in decision_docs]
    k = len(by_run)
    out, ties, support = [], [], {}
    for sid in by_run[0]:
        labels = [gate_label(r[sid]) for r in by_run]
        label, n = Counter(labels).most_common(1)[0]
        if n * 2 <= k:
            ties.append(sid)
            support[sid] = 0
            continue
        holders = [r[sid] for r in by_run if gate_label(r[sid]) == label]
        cats = Counter(d["category"] for d in holders)
        top = max(cats.values())
        cat = next(d["category"] for d in holders if cats[d["category"]] == top)
        out.append(next(d for d in holders if d["category"] == cat))
        support[sid] = n
    proposals = [p for doc in decision_docs[:1] for p in doc.get("operation_proposals", [])
                 if p["step_id"] in {d["step_id"] for d in out if d["category"] == "no_catalog_operation"}]
    return {"record_id": decision_docs[0]["record_id"], "decisions": out, "operation_proposals": proposals}, ties, support


def route_labels(dec_doc, ties, skeleton):
    d = {x["step_id"]: x for x in dec_doc["decisions"]}
    out = {}
    for cfg in skeleton:
        for r in cfg["routes"]:
            seq = []
            for sid in r["expected_step_ids"]:
                seq += ([TIE + sid] if sid in ties else list(gate_label(d[sid]))) + ["|"]
            out[r["route_id"]] = tuple(seq)
    return out


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def measure(args):
    out = BASE / args.iteration
    records = json.loads((BASE / ("dev_set.json" if args.set == "dev" else f"{args.set}_set.json")).read_text())
    groups = [[f"run_{i}" for i in range(1, args.k + 1)], [f"run_{i}" for i in range(args.k + 1, 2 * args.k + 1)]]
    per_paper, route_cmp, route_eq, step_cmp, step_eq, pj, missing, n_ties = {}, 0, 0, 0, 0, [], [], 0
    for r in records:
        skeleton = v3.atlas_skeleton(r)
        cons = []
        for g in groups:
            paths = [out / run / "records" / r / "final_decisions.json" for run in g]
            if not all(p.exists() for p in paths):
                missing.append((r, [str(p.parent.parent.parent.name) for p in paths if not p.exists()]))
                break
            cons.append(consensus([json.loads(p.read_text()) for p in paths]))
        if len(cons) < 2:
            continue
        (a, ta, _), (b, tb, _) = cons
        n_ties += len(ta) + len(tb)
        ra, rb = route_labels(a, ta, skeleton), route_labels(b, tb, skeleton)
        eq = sum(ra[x] == rb[x] and TIE not in "".join(map(str, ra[x])) for x in ra)
        route_cmp += len(ra)
        route_eq += eq
        da = {d["step_id"]: gate_label(d) for d in a["decisions"]}
        db = {d["step_id"]: gate_label(d) for d in b["decisions"]}
        steps = [s for c in skeleton for rt in c["routes"] for s in rt["expected_step_ids"]]
        se = sum(s in da and s in db and da[s] == db[s] for s in steps)
        step_cmp += len(steps)
        step_eq += se
        oa = {o for x in da.values() for o in x if o != "<boundary>"}
        ob = {o for x in db.values() for o in x if o != "<boundary>"}
        pj.append(jaccard(oa, ob))
        per_paper[r] = {"route_agreement": round(eq / len(ra), 3), "step_agreement": round(se / len(steps), 3),
                        "operation_set_jaccard": round(pj[-1], 3), "ties": [len(ta), len(tb)],
                        "route_disagreements": [x for x in ra if ra[x] != rb[x]]}
    g1 = not missing
    g2 = route_eq / route_cmp if route_cmp else 0.0
    report = {"iteration": args.iteration, "set": args.set, "k": args.k, "groups": groups, "G1_all_runs_valid": g1,
              "missing": missing, "G2_route_agreement": round(g2, 3),
              "step_agreement": round(step_eq / step_cmp, 3) if step_cmp else None, "ties": n_ties,
              "G3_paper_jaccard_median": round(median(pj), 3) if pj else None,
              "G3_paper_jaccard_min": round(min(pj), 3) if pj else None,
              "gate_met": bool(g1 and g2 >= 0.90 and pj and median(pj) >= 0.90 and min(pj) >= 0.75),
              "per_paper": per_paper}
    (out / f"consensus_split_k{args.k}.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(json.dumps({k: v for k, v in report.items() if k != "per_paper"}))


def build(args):
    """Write the consensus decision + compiled document for each record from runs 1..k."""
    out = BASE / args.iteration
    catalog = json.loads(CATALOG.read_text())
    records = json.loads((BASE / ("dev_set.json" if args.set == "dev" else f"{args.set}_set.json")).read_text())
    for r in records:
        docs = [json.loads((out / f"run_{i}" / "records" / r / "final_decisions.json").read_text()) for i in range(1, args.k + 1)]
        dec, ties, support = consensus(docs)
        folder = out / "consensus" / r
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "consensus_decisions.json").write_text(json.dumps({**dec, "ties": ties, "support": support}, indent=1, ensure_ascii=False))
        if not ties:
            (folder / "final_document.json").write_text(json.dumps(v3.compile_v3(dec, r, v3.atlas_skeleton(r), catalog), indent=1, ensure_ascii=False))
        print(r, "ties", len(ties))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["measure", "build"])
    p.add_argument("--iteration", required=True)
    p.add_argument("--set", default="dev")
    p.add_argument("--k", type=int, default=3)
    a = p.parse_args()
    measure(a) if a.command == "measure" else build(a)


if __name__ == "__main__":
    main()
