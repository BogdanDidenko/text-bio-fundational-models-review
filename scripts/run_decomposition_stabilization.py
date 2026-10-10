"""Iterate the decomposition protocol on the development set until the predeclared gate is met.

Each iteration runs every development paper N times independently (extract + mechanical repair, no
reviewer loop) and measures stability against stabilization/GATE.md.

  python3 scripts/run_decomposition_stabilization.py run --iteration v2_i1 --runs 3
  python3 scripts/run_decomposition_stabilization.py measure --iteration v2_i1
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import combinations
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.operation_decomposition import (  # noqa: E402
    CATALOG, build_packet, canonicalize_quotes, encoded, sha,
)
from scripts.operation_decomposition_v2 import (  # noqa: E402
    PROTOCOL, RULES_V2, atlas_skeleton, extraction_schema_v2, route_signatures, validate_v2,
)
from scripts import operation_decomposition_v3 as v3  # noqa: E402
from scripts.run_operation_decomposition import packet_text, run_codex, write_json, now  # noqa: E402

BASE = ROOT / "analysis/operation_decomposition_2026-10-07/stabilization"
GUIDE = ROOT / "protocol/REPRESENTATION_LIBRARY_GUIDE.md"
DEV_SET = ROOT / "analysis/operation_decomposition_2026-10-07/stabilization/dev_set.json"


def prompt_v2(record_id, skeleton, manifest, sections, guide, catalog, previous=None, feedback=None, rules=RULES_V2):
    parts = ["You are an operation-decomposition agent for a PRISMA-ScR scoping review of generative foundation "
             "models that combine text with biological data. For the fixed input routes below, reconstruct from the "
             "paper text how each route's data are transformed, as calls to library operations.",
             "== Shared agent protocol ==\n" + guide,
             "== Operation catalog (the only allowed operation_ids, ports and declared parameters) ==\n"
             + json.dumps(catalog, ensure_ascii=False, indent=1),
             rules,
             "== Atlas skeleton for this record (fixed structure; reviewed input routes) ==\n"
             + json.dumps(skeleton, ensure_ascii=False, indent=1)]
    if previous is not None:
        parts.append("== Your previous document ==\n" + json.dumps(previous, ensure_ascii=False))
        parts.append("== Required corrections ==\n" + feedback + "\nReturn the COMPLETE corrected document.")
    parts.append(f"== Paper full text: record {record_id}, packet {manifest['packet_sha256']} ==\n"
                 + packet_text(manifest, sections))
    return "\n\n".join(parts)


def job(record_id, run_dir, args, catalog, library_sha256, guide):
    folder = run_dir / "records" / record_id
    status_path = folder / "status.json"
    if status_path.exists():
        return json.loads(status_path.read_text())
    manifest, sections = build_packet(record_id)
    is_v3 = args.protocol == "v3"
    skeleton = v3.atlas_skeleton(record_id) if is_v3 else atlas_skeleton(record_id)
    schema = v3.extraction_schema_v3(catalog, skeleton) if is_v3 else extraction_schema_v2(catalog, skeleton)
    rules = v3.RULES_V3 if is_v3 else RULES_V2
    log, doc = [], None
    for attempt in range(args.repairs + 1):
        feedback = None if attempt == 0 else "Mechanical validation failed:\n- " + "\n- ".join(errors)
        stage = "extract" if attempt == 0 else "repair"
        doc_new, meta = run_codex(prompt_v2(record_id, skeleton, manifest, sections, guide, catalog,
                                            doc if attempt else None, feedback, rules),
                                  schema, folder / "attempts" / f"{attempt + 1:02d}_{stage}", args.model, args.timeout, args.reasoning_effort)
        log.append({"attempt": f"{attempt + 1:02d}_{stage}", "status": meta["status"], "elapsed_seconds": meta["elapsed_seconds"]})
        if doc_new is None:
            errors = ["agent returned no parseable document"]
            continue
        doc = doc_new
        if is_v3:
            errors = v3.check_decisions(doc, record_id, skeleton, catalog)
            if errors:
                continue
            full = v3.compile_v3(doc, record_id, skeleton, catalog)
        else:
            full = doc
        replaced = canonicalize_quotes(full, sections)
        errors, _, assemblies = validate_v2(full, record_id, sections, catalog, library_sha256, "stabilization", skeleton)
        errors = list(dict.fromkeys(e.split(" / ", 1)[-1] if is_v3 else e for e in errors))
        if not errors:
            if is_v3:
                write_json(folder / "final_decisions.json", doc)
            write_json(folder / "final_document.json", full)
            status = {"record_id": record_id, "status": "valid", "attempts": log, "whitespace_canonicalized": replaced}
            write_json(status_path, status)
            return status
    if doc is not None:
        write_json(folder / "last_invalid_document.json", doc)
    status = {"record_id": record_id, "status": "failed_validation", "attempts": log, "errors": errors}
    write_json(status_path, status)
    return status


def run(args):
    catalog = json.loads(CATALOG.read_text())
    library_sha256 = sha(encoded(catalog))
    guide = GUIDE.read_text(encoding="utf-8")
    records = json.loads((DEV_SET if args.set == "dev" else DEV_SET.with_name(f"{args.set}_set.json")).read_text())
    out = BASE / args.iteration
    write_json(out / "run_config.json", {"started_at": now(), "protocol": v3.PROTOCOL if args.protocol == "v3" else PROTOCOL, "records": records, "set": args.set, "runs": args.runs,
               "model": args.model, "reasoning_effort": args.reasoning_effort, "repairs": args.repairs,
               "rules_sha256": sha(v3.RULES_V3 if args.protocol == "v3" else RULES_V2), "guide_sha256": sha(guide), "library_sha256": library_sha256})
    jobs = [(r, out / f"run_{k}") for k in range(1, args.runs + 1) for r in records]
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(job, r, d, args, catalog, library_sha256, guide): (r, d.name) for r, d in jobs}
        for n, f in enumerate(as_completed(futures), 1):
            r, d = futures[f]
            try:
                s = f.result()["status"]
            except Exception as exc:  # recorded, batch continues
                s = f"runner_error {exc!r}"
            print(f"[{n}/{len(jobs)}] {d} {r} {s}", flush=True)
    measure(args)


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def measure(args):
    out = BASE / args.iteration
    records = json.loads((DEV_SET if args.set == "dev" else DEV_SET.with_name(f"{args.set}_set.json")).read_text())
    runs = sorted(p.name for p in out.glob("run_*") if p.is_dir())
    docs = {(run, r): json.loads((out / run / "records" / r / "final_document.json").read_text())
            for run in runs for r in records if (out / run / "records" / r / "final_document.json").exists()}
    valid = len(docs) == len(runs) * len(records)
    route_cmp, route_eq, paper_j, per_paper, disagreements = 0, 0, [], {}, []
    for r in records:
        sigs = {run: route_signatures(docs[(run, r)]) for run in runs if (run, r) in docs}
        opsets = {run: {c["operation_id"] for t in docs[(run, r)]["trajectories"] for s in t["steps"]
                        for c in s["decomposition"] if c["operation_id"]} for run in sigs}
        pj = [jaccard(opsets[a], opsets[b]) for a, b in combinations(sigs, 2)]
        paper_j += pj
        eq = cmp = 0
        for a, b in combinations(sigs, 2):
            for route in sorted(set(sigs[a]) | set(sigs[b])):
                cmp += 1
                if sigs[a].get(route) == sigs[b].get(route):
                    eq += 1
                elif a == runs[0]:
                    disagreements.append({"record_id": r, "route_id": route, a: sigs[a].get(route), b: sigs[b].get(route)})
        route_cmp += cmp
        route_eq += eq
        per_paper[r] = {"runs_valid": len(sigs), "route_agreement": round(eq / cmp, 3) if cmp else None,
                        "operation_set_jaccard": [round(x, 3) for x in pj]}
    g2 = route_eq / route_cmp if route_cmp else 0.0
    report = {"iteration": args.iteration, "runs": runs, "all_runs_valid": valid,
              "G1_coverage_all_valid": valid, "G2_route_agreement": round(g2, 3),
              "G3_paper_jaccard_median": round(median(paper_j), 3) if paper_j else None,
              "G3_paper_jaccard_min": round(min(paper_j), 3) if paper_j else None,
              "gate_met": bool(valid and g2 >= 0.90 and paper_j and median(paper_j) >= 0.90 and min(paper_j) >= 0.75),
              "per_paper": per_paper, "route_disagreements_vs_run_1": disagreements}
    cat = []
    for r in records:
        decs = {run: out / run / "records" / r / "final_decisions.json" for run in runs}
        decs = {k: v3.decision_signatures(json.loads(v.read_text())) for k, v in decs.items() if v.exists()}
        for a, b in combinations(sorted(decs), 2):
            for sid in sorted(set(decs[a]) & set(decs[b])):
                if decs[a][sid] != decs[b][sid]:
                    cat.append({"record_id": r, "step_id": sid, a: list(decs[a][sid]), b: list(decs[b][sid])})
    report["step_decision_disagreements"] = cat
    write_json(out / "stability.json", report)
    print(json.dumps({k: v for k, v in report.items() if k not in ("per_paper", "route_disagreements_vs_run_1", "step_decision_disagreements")}, indent=1))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["run", "measure"])
    parser.add_argument("--iteration", required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--reasoning-effort", default="high")
    parser.add_argument("--repairs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=2700)
    parser.add_argument("--max-workers", type=int, default=12)
    parser.add_argument("--protocol", choices=["v2", "v3"], default="v3")
    parser.add_argument("--set", default="dev", help="dev or <name> for stabilization/<name>_set.json")
    args = parser.parse_args()
    run(args) if args.command == "run" else measure(args)


if __name__ == "__main__":
    main()
