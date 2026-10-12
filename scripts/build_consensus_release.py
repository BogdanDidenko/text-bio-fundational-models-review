"""Build per-record decomposition folders from protocol v3.1 consensus (majority of 3 runs).

Output folders have the layout read by build_operation_corpus.py (packet_manifest.json, sections/,
final_document.json, assemblies.json, evidence.json, review_round_1.json, status.json).

- Majority label (> 1/2 of runs) per step wins (scripts/decomposition_consensus.py).
- A step without a majority becomes an unresolved boundary (category consensus_tie) and a BLOCKING
  finding for the steward; the record is then accepted_with_open_findings.
- A step decided by 2 of 3 runs gets a MINOR finding listing the dissenting label.
- review_round_1.json records this consensus check; it is not a reviewer-agent pass.

  python3 scripts/build_consensus_release.py --out analysis/operation_decomposition_v31_2026-10-12
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import operation_decomposition_v3 as v3  # noqa: E402
from scripts.decomposition_consensus import consensus, gate_label  # noqa: E402
from scripts.operation_decomposition import (  # noqa: E402
    CATALOG, build_packet, canonicalize_quotes, encoded, evidence_entries, sha,
)

STAB = ROOT / "analysis/operation_decomposition_2026-10-07/stabilization"
SOURCES = [("dev_set.json", "v3_i8"), ("heldout4_set.json", "v3_h4"), ("rest30_set.json", "v31_rest30")]
RUNS = ["run_1", "run_2", "run_3"]


def label_text(d):
    return d["category"] if d["category"] != "library_operation" else "+".join(c["operation_id"] for c in d["calls"])


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value) if not isinstance(value, str) else value.encode("utf-8"))


def build_record(record, iteration, out, catalog, library_sha256, rules_sha):
    paths = [STAB / iteration / run / "records" / record / "final_decisions.json" for run in RUNS]
    docs = [json.loads(p.read_text()) for p in paths]
    dec, ties, support = consensus(docs)
    skeleton = v3.atlas_skeleton(record)
    by_run = [{d["step_id"]: d for d in doc["decisions"]} for doc in docs]
    traj_of = {s: cfg["configuration_id"] for cfg in skeleton for r in cfg["routes"] for s in r["expected_step_ids"]}
    element = {s: e for cfg in skeleton for r in cfg["routes"] for s, e in zip(r["expected_step_ids"], r["transformation_chain_verbatim"])}
    findings = []
    for sid in ties:
        labels = [label_text(r[sid]) for r in by_run]
        dec["decisions"].append({**by_run[0][sid], "category": "consensus_tie", "calls": [],
                                 "rationale": "no majority across 3 runs: " + " | ".join(labels),
                                 "uncertainty": "unresolved by consensus; steward decision required"})
        findings.append({"trajectory_id": traj_of[sid], "step_id": sid, "issue_type": "other", "severity": "blocking",
                         "detail": f"Consensus tie for chain element {element[sid]!r}: runs gave " + " | ".join(labels),
                         "required_change": "Steward decides the operation for this step."})
    for sid, n in support.items():
        if n and n < len(RUNS):
            labels = Counter(label_text(r[sid]) for r in by_run)
            won = "+".join(gate_label(next(d for d in dec["decisions"] if d["step_id"] == sid)))
            findings.append({"trajectory_id": traj_of[sid], "step_id": sid, "issue_type": "other", "severity": "minor",
                             "detail": f"Majority {n}/{len(RUNS)} for chain element {element[sid]!r} (kept: {won}); "
                                       f"run labels: " + ", ".join(f"{k} x{v}" for k, v in labels.items()),
                             "required_change": "Steward confirms or overrides the majority decision."})
    manifest, sections = build_packet(record)
    full = v3.compile_v3(dec, record, skeleton, catalog)
    replaced = canonicalize_quotes(full, sections)
    errors, warnings, assemblies = v3.validate_v2(full, record, sections, catalog, library_sha256, catalog["release"], skeleton)
    if errors:
        raise ValueError(f"{record}: consensus document invalid: {errors[:3]}")
    base = out / "records" / record
    write(base / "packet_manifest.json", manifest)
    for sid, s in sections.items():
        write(base / "sections" / f"{sid}.md", s["text"])
    write(base / "consensus_decisions.json", {**dec, "ties": ties, "support": support, "source_runs": [str(p.relative_to(ROOT)) for p in paths]})
    write(base / "final_document.json", full)
    write(base / "assemblies.json", assemblies)
    write(base / "evidence.json", sorted(evidence_entries(record, assemblies, sections, manifest).values(), key=lambda e: e["evidence_id"]))
    write(base / "review_round_1.json", {"record_id": record, "verdict": "revise" if ties else "accept", "findings": findings,
                                         "coverage_summary": "Consensus check over 3 independent protocol v3.1 runs "
                                                             "(majority per step); not a reviewer-agent pass."})
    calls = [c for a in assemblies for c in a["calls"]]
    status = {"record_id": record, "status": "accepted_with_open_findings" if ties else "accepted",
              "protocol": v3.PROTOCOL + ".1-consensus3", "rules_sha256": rules_sha, "source_iteration": iteration,
              "steps": len(element), "ties": len(ties), "majority_2_of_3": sum(1 for n in support.values() if n == 2),
              "unanimous": sum(1 for n in support.values() if n == 3), "trajectories": len(assemblies), "calls": len(calls),
              "library_calls": sum(1 for c in calls if c["operation_id"]),
              "unexpanded": sum(1 for c in calls if not c["operation_id"]),
              "open_blocking_findings": len(ties), "warnings": warnings, "whitespace_canonicalized": replaced,
              "operation_proposals": dec.get("operation_proposals", [])}
    write(base / "status.json", status)
    return status


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    out = a.out if a.out.is_absolute() else ROOT / a.out
    catalog = json.loads(CATALOG.read_text())
    library_sha256 = sha(encoded(catalog))
    rules_sha = sha(v3.RULES_V3)
    rows = []
    for set_file, iteration in SOURCES:
        cfg = json.loads((STAB / iteration / "run_config.json").read_text())
        if cfg["rules_sha256"] != rules_sha:
            raise SystemExit(f"{iteration}: runs used rules {cfg['rules_sha256'][:12]}, current {rules_sha[:12]}")
        for record in json.loads((STAB / set_file).read_text()):
            rows.append(build_record(record, iteration, out, catalog, library_sha256, rules_sha))
    keys = ("steps", "unanimous", "majority_2_of_3", "ties", "library_calls", "unexpanded")
    summary = {"protocol": v3.PROTOCOL + ".1-consensus3", "rules_sha256": rules_sha, "records": len(rows),
               "accepted": sum(r["status"] == "accepted" for r in rows),
               "accepted_with_open_findings": sum(r["status"] != "accepted" for r in rows),
               **{k: sum(r[k] for r in rows) for k in keys}}
    write(out / "run_summary.json", summary)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
