"""Run-to-run agreement of the agent operation decomposition (original run + replicate runs).

For each paper present in every run, compares: the set of library operations used (Jaccard),
operation call counts (weighted Jaccard), the set of model variants covered (normalised
names, Jaccard), number of trajectories, share of steps left unexpanded, and the open
blocking reviewer findings. Pairwise values are reported for every pair of runs.
"""

import json
import re
from collections import Counter
from itertools import combinations
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "analysis/operation_decomposition_2026-10-07"
RUNS = {"run_1": BASE, "run_2": BASE / "replicates/run_2", "run_3": BASE / "replicates/run_3"}


def norm(name):
    return re.sub(r"[^a-z0-9]+", "", name.lower())


ATLAS = json.loads((ROOT / "docs/input-representation-atlas/data/atlas.json").read_text())
ATLAS_MODELS = {}
for _m in ATLAS["architectures"]:
    ATLAS_MODELS.setdefault(_m["record_id"], set()).add(_m["model_name"])


def covered_models(record, assemblies):
    """Atlas models (normalised name) that appear inside any trajectory's model_variant."""
    variants = [norm(a["model_variant"]) for a in assemblies]
    return {name for name in ATLAS_MODELS.get(record, set()) if any(norm(name) in v for v in variants)}


def profile(run_dir, record):
    folder = run_dir / "records" / record
    status = json.loads((folder / "status.json").read_text())
    if not status["status"].startswith("accepted"):
        return {"status": status["status"]}
    assemblies = json.loads((folder / "assemblies.json").read_text())
    calls = [c for a in assemblies for c in a["calls"]]
    ops = Counter(c["operation_id"] for c in calls if c["operation_id"])
    return {"status": status["status"], "operations": set(ops), "op_counts": ops,
            "models": covered_models(record, assemblies), "trajectories": len(assemblies),
            "unexpanded_share": sum(1 for c in calls if not c["operation_id"]) / len(calls) if calls else 0.0,
            "open_blocking": status.get("open_blocking_findings", 0)}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def weighted_jaccard(a, b):
    keys = set(a) | set(b)
    den = sum(max(a[k], b[k]) for k in keys)
    return sum(min(a[k], b[k]) for k in keys) / den if den else 1.0


def main():
    records = sorted(p.parent.name for p in (RUNS["run_2"] / "records").glob("*/status.json"))
    rows, pairs = [], {f"{x}-{y}": [] for x, y in combinations(RUNS, 2)}
    for record in records:
        prof = {run: profile(path, record) for run, path in RUNS.items()}
        row = {"record_id": record, "status": {r: p["status"] for r, p in prof.items()}}
        if all("operations" in p for p in prof.values()):
            for x, y in combinations(RUNS, 2):
                a, b = prof[x], prof[y]
                metrics = {"operation_set_jaccard": jaccard(a["operations"], b["operations"]),
                           "operation_count_weighted_jaccard": weighted_jaccard(a["op_counts"], b["op_counts"]),
                           "atlas_model_coverage_jaccard": jaccard(a["models"], b["models"]),
                           "unexpanded_share_abs_diff": abs(a["unexpanded_share"] - b["unexpanded_share"])}
                row[f"{x}-{y}"] = metrics
                pairs[f"{x}-{y}"].append(metrics)
            row["trajectories"] = {r: p["trajectories"] for r, p in prof.items()}
            row["open_blocking"] = {r: p["open_blocking"] for r, p in prof.items()}
            row["operations"] = {r: sorted(p["operations"]) for r, p in prof.items()}
            row["atlas_models"] = sorted(ATLAS_MODELS.get(record, set()))
            row["covered_models"] = {r: sorted(p["models"]) for r, p in prof.items()}
            row["trajectory_count_cv"] = (lambda xs: (sum((x - sum(xs) / len(xs)) ** 2 for x in xs) / len(xs)) ** 0.5 / (sum(xs) / len(xs)))(list(row["trajectories"].values()))
        rows.append(row)
    summary = {}
    for pair, values in pairs.items():
        summary[pair] = {k: {"median": round(median(v[k] for v in values), 3), "min": round(min(v[k] for v in values), 3)}
                         for k in (values[0] if values else {})} | {"papers": len(values)}
    all_values = [v for values in pairs.values() for v in values]
    pooled = {k: {"median": round(median(v[k] for v in all_values), 3), "min": round(min(v[k] for v in all_values), 3)}
              for k in (all_values[0] if all_values else {})}
    union_ops = Counter(op for r in rows if "operations" in r for op in set().union(*map(set, r["operations"].values())))
    stable_ops = Counter(op for r in rows if "operations" in r for op in set.intersection(*map(set, r["operations"].values())))
    cvs = [r["trajectory_count_cv"] for r in rows if "trajectory_count_cv" in r]
    summary["trajectory_count_cv"] = {"median": round(median(cvs), 3), "max": round(max(cvs), 3)} if cvs else None
    out = {"runs": list(RUNS), "papers": len(records), "papers_compared": len(all_values) // max(1, len(pairs)),
           "pairwise": summary, "pooled_pairs": pooled,
           "operation_stability": {op: {"papers_any_run": union_ops[op], "papers_all_runs": stable_ops[op]}
                                   for op in sorted(union_ops, key=lambda o: -union_ops[o])},
           "per_paper": rows}
    target = BASE / "replicates/agreement.json"
    target.write_text(json.dumps(out, indent=2, default=list) + "\n")
    print(json.dumps({k: out[k] for k in ("papers", "papers_compared", "pooled_pairs")} | {"trajectory_count_cv": summary["trajectory_count_cv"]}, indent=1))


if __name__ == "__main__":
    main()
