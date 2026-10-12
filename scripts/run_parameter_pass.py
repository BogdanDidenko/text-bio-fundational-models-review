"""Parameter pass over release 1.2.0: are declared operation parameters stated anywhere in the paper?

Operations are fixed (consensus decisions of protocol v3.1). For every library call and declared
parameter (a slot), a Codex run answers stated (value + verbatim evidence) or unspecified, reading
the full paper text. Design and gate: analysis/operation_decomposition_v31_2026-10-12/parameter_pass/GATE.md.

  python3 scripts/run_parameter_pass.py run --set dev --iteration p1 --runs 3
  python3 scripts/run_parameter_pass.py measure --set heldout4 --iteration p_h --k 3
"""

import argparse
import json
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import operation_decomposition_v3 as v3  # noqa: E402
from scripts.operation_decomposition import CATALOG, EVIDENCE_KINDS, _obj, build_packet, canonicalize_quotes, sha  # noqa: E402
from scripts.run_operation_decomposition import packet_text, run_codex, write_json, now  # noqa: E402

REL = ROOT / "analysis/operation_decomposition_v31_2026-10-12"
BASE = REL / "parameter_pass"
STAB = ROOT / "analysis/operation_decomposition_2026-10-07/stabilization"
GLOSSARY = ROOT / "protocol/OPERATION_PARAMETER_GLOSSARY.md"
PROTOCOL = "parameter-pass-v1"

RULES = """Task: for every parameter slot listed below, decide from the paper text whether the paper STATES
the value of that operation parameter for that data path. The operations are fixed; do not question
or change them. Answer every slot_id exactly once.

status "stated": the paper text (any section, appendix, table or figure caption) states the value for
this model and this data path. Give value = the value in a few words, using the paper's own terms and
copying numbers exactly, and 1-2 evidence quotes copied VERBATIM (exact substring) from the cited
section that contain or directly establish the value.
status "unspecified": the paper does not state it for this path. value = null, evidence = [].

What counts as stated:
- Naming a specific resource states what it determines: "we use the Llama-3 tokenizer" states the
  tokenize vocabulary and segmentation; "a two-layer MLP" states the project method.
- A value stated once for the model's input processing applies to every configuration of that model
  that uses the same step, unless the paper says otherwise.
- parameter_state / trainability: stated only when the paper says the component is trained, frozen,
  fine-tuned or kept fixed in the lifecycle phase given for the slot (or in all phases).
- The value must answer the glossary question with information beyond the operation's own name or the
  chain element wording. "row-wise normalization" does not state the normalize method (it states its
  axes: per row); "a DNA-specific tokenizer" or "the tokenizer" does not state a vocabulary. A paper-
  introduced tokenizer states its vocabulary only if the paper describes its units or size; the
  tokenizer of a specifically named pretrained model (e.g. "the Llama-2 tokenizer", "tokenized by
  BioBERT") states vocabulary and segmentation as that model's.
- serialize order is stated only by a shown template or example, or an explicit sequence ("first ...
  then ..."); a list of what the prompt contains ("provide X and Y") does not state an order.
- serialize lexical_mapping is stated when the paper says how items or values appear as words (gene
  symbols / gene names, numbers with given precision, category words such as "high"/"low");
  "natural-language descriptions" or "text" alone does not state it.
- rank order is stated when the ranking key and direction are given; "top" or "highest" wording states
  descending order by that key.
- Per-sample scaling ("each cell normalised to a total of 10,000") states normalize scope = each
  sample (cell) and axes = across features of that sample.
What does NOT count: values that only follow from convention or from the usual defaults of a library,
from released code, from a cited paper, or from a different model or baseline described in the paper.
A parameter that does not apply to this use (e.g. no forced inclusions described) is unspecified.
Slots with identical operation, chain element and model get identical answers unless the paper
distinguishes them.

The parameter meanings are defined in the glossary below; answer the question in its third column.
"""


def slots_for(record):
    """Library-call parameter slots of the 1.2.0 consensus decisions, with their context."""
    dec = json.loads((REL / "records" / record / "consensus_decisions.json").read_text())
    catalog = {b["operation_id"]: b for b in json.loads(CATALOG.read_text())["blocks"]}
    ctx = {}
    for cfg in v3.atlas_skeleton(record):
        for r in cfg["routes"]:
            for sid, el in zip(r["expected_step_ids"], r["transformation_chain_verbatim"]):
                ctx[sid] = {"model": cfg["model_name"], "lifecycle_phase": cfg["lifecycle_phase"],
                            "configuration": cfg["task_or_configuration_verbatim"], "chain_element": el,
                            "route": f"{r['source_object_verbatim']} -> {r['model_visible_form_verbatim']}",
                            "chain": r["transformation_chain_verbatim"]}
    calls, slots = [], []
    for d in sorted(dec["decisions"], key=lambda d: d["step_id"]):
        if d["category"] != "library_operation":
            continue
        for j, c in enumerate(d["calls"], 1):
            call_id = f"{d['step_id']}#c{j}"
            params = catalog[c["operation_id"]]["parameters"]
            calls.append({"call_id": call_id, "operation_id": c["operation_id"], **ctx[d["step_id"]],
                          "step_evidence": [e["quote"] for e in d["evidence"]], "parameters": params})
            slots += [f"{call_id}#{p}" for p in params]
    return calls, slots


def schema(slots):
    ev = _obj({"section_id": {"type": "string"}, "quote": {"type": "string"}, "kind": {"type": "string", "enum": EVIDENCE_KINDS}})
    ans = _obj({"slot_id": {"type": "string", "enum": slots}, "status": {"type": "string", "enum": ["stated", "unspecified"]},
                "value": {"type": ["string", "null"]}, "evidence": {"type": "array", "items": ev}})
    return _obj({"record_id": {"type": "string"}, "answers": {"type": "array", "items": ans}})


def prompt(record, calls, manifest, sections, glossary, previous=None, feedback=None):
    parts = ["You are a data-charting agent for a PRISMA-ScR scoping review of generative foundation models that "
             "combine text with biological data.", RULES, "== Parameter glossary ==\n" + glossary,
             "== Calls and their parameter slots (slot_id = call_id#parameter) ==\n" + json.dumps(calls, ensure_ascii=False, indent=1)]
    if previous is not None:
        parts += ["== Your previous answer ==\n" + json.dumps(previous, ensure_ascii=False),
                  "== Required corrections ==\n" + feedback + "\nReturn the COMPLETE corrected answer."]
    parts.append(f"== Paper full text: record {record}, packet {manifest['packet_sha256']} ==\n" + packet_text(manifest, sections))
    return "\n\n".join(parts)


def check(doc, record, slots, sections):
    errors = []
    if doc.get("record_id") != record:
        errors.append(f"record_id must be {record}")
    got = [a["slot_id"] for a in doc.get("answers", [])]
    if set(slots) - set(got):
        errors.append(f"missing slots {sorted(set(slots) - set(got))}")
    dup = sorted({s for s in got if got.count(s) > 1})
    if dup:
        errors.append(f"slots answered more than once {dup}")
    wrapped = {"trajectories": [{"trajectory_id": "answers", "evidence": [e for a in doc.get("answers", []) for e in a["evidence"]],
                                 "nodes": [], "steps": []}]}
    canonicalize_quotes(wrapped, sections)
    for a in doc.get("answers", []):
        if a["status"] == "stated":
            if not (a["value"] or "").strip():
                errors.append(f"{a['slot_id']}: stated needs a value")
            if not a["evidence"]:
                errors.append(f"{a['slot_id']}: stated needs at least one verbatim quote")
        elif a["value"] is not None or a["evidence"]:
            errors.append(f"{a['slot_id']}: unspecified must have value null and no evidence")
        for e in a["evidence"]:
            s = sections.get(e["section_id"])
            if s is None:
                errors.append(f"{a['slot_id']}: unknown section {e['section_id']}")
            elif not e["quote"].strip() or e["quote"] not in s["text"]:
                errors.append(f"{a['slot_id']}: quote is not a literal substring of {e['section_id']}: {e['quote']!r}")
    return errors


def job(record, run_dir, args, glossary):
    folder = run_dir / record
    if (folder / "status.json").exists():
        return json.loads((folder / "status.json").read_text())
    calls, slots = slots_for(record)
    manifest, sections = build_packet(record)
    if not slots:
        write_json(folder / "final_answers.json", {"record_id": record, "answers": []})
        status = {"record_id": record, "status": "valid", "slots": 0, "attempts": []}
        write_json(folder / "status.json", status)
        return status
    sch, doc, log, errors = schema(slots), None, [], []
    for attempt in range(args.repairs + 1):
        feedback = None if attempt == 0 else "Mechanical validation failed:\n- " + "\n- ".join(errors)
        new, meta = run_codex(prompt(record, calls, manifest, sections, glossary, doc if attempt else None, feedback),
                              sch, folder / "attempts" / f"{attempt + 1:02d}", args.model, args.timeout, args.reasoning_effort)
        log.append({"attempt": attempt + 1, "status": meta["status"], "elapsed_seconds": meta["elapsed_seconds"]})
        if new is None:
            errors = ["agent returned no parseable document"]
            continue
        doc = new
        errors = check(doc, record, slots, sections)
        if not errors:
            write_json(folder / "final_answers.json", doc)
            status = {"record_id": record, "status": "valid", "slots": len(slots), "attempts": log}
            write_json(folder / "status.json", status)
            return status
    status = {"record_id": record, "status": "failed_validation", "slots": len(slots), "attempts": log, "errors": errors}
    write_json(folder / "status.json", status)
    return status


def set_records(name):
    return json.loads((STAB / ("dev_set.json" if name == "dev" else f"{name}_set.json")).read_text())


def run(args):
    glossary = GLOSSARY.read_text(encoding="utf-8")
    records = set_records(args.set)
    out = BASE / args.iteration
    write_json(out / "run_config.json", {"started_at": now(), "protocol": PROTOCOL, "set": args.set, "records": records,
               "runs": args.runs, "model": args.model, "reasoning_effort": args.reasoning_effort,
               "rules_sha256": sha(RULES), "glossary_sha256": sha(glossary)})
    jobs = [(r, out / f"run_{k}") for k in range(1, args.runs + 1) for r in records]
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(job, r, d, args, glossary): (r, d.name) for r, d in jobs}
        for n, f in enumerate(as_completed(futures), 1):
            r, d = futures[f]
            try:
                s = f.result()["status"]
            except Exception as exc:  # recorded, batch continues
                s = f"runner_error {exc!r}"
            print(f"[{n}/{len(jobs)}] {d} {r} {s}", flush=True)
    measure(args)


def norm_value(v):
    return re.sub(r"[^a-z0-9.]+", " ", (v or "").lower()).strip()


def load(out, run, record):
    p = out / run / record / "final_answers.json"
    return {a["slot_id"]: a for a in json.loads(p.read_text())["answers"]} if p.exists() else None


def consensus(answer_maps):
    out = {}
    for sid in answer_maps[0]:
        votes = [m[sid]["status"] for m in answer_maps]
        status = Counter(votes).most_common(1)[0][0]
        out[sid] = next(m[sid] for m in answer_maps if m[sid]["status"] == status) | {"support": votes.count(status)}
    return out


def param_of(sid):
    call, p = sid.rsplit("#", 1)
    return p


def measure(args):
    out = BASE / args.iteration
    records = set_records(args.set)
    runs = sorted(p.name for p in out.glob("run_*") if p.is_dir())
    valid = all(load(out, r, rec) is not None for r in runs for rec in records)
    pair_eq = pair_n = 0
    for rec in records:
        maps = {r: load(out, r, rec) for r in runs}
        for a, b in combinations([r for r in runs if maps[r] is not None], 2):
            for sid in maps[a]:
                pair_n += 1
                pair_eq += maps[a][sid]["status"] == maps[b][sid]["status"]
    report = {"iteration": args.iteration, "set": args.set, "runs": runs, "P1_all_runs_valid": valid,
              "single_run_pair_status_agreement": round(pair_eq / pair_n, 3) if pair_n else None}
    k = args.k
    if len(runs) >= 2 * k and valid:
        halves = [[f"run_{i}" for i in range(1, k + 1)], [f"run_{i}" for i in range(k + 1, 2 * k + 1)]]
        eq = n = veq = vn = 0
        share = {0: Counter(), 1: Counter()}
        total = Counter()
        disagreements = []
        for rec in records:
            ca, cb = (consensus([load(out, r, rec) for r in h]) for h in halves)
            for sid in ca:
                n += 1
                same = ca[sid]["status"] == cb[sid]["status"]
                eq += same
                total[param_of(sid)] += 1
                share[0][param_of(sid)] += ca[sid]["status"] == "unspecified"
                share[1][param_of(sid)] += cb[sid]["status"] == "unspecified"
                if not same:
                    disagreements.append({"record_id": rec, "slot_id": sid, "a": [ca[sid]["status"], ca[sid]["value"]],
                                          "b": [cb[sid]["status"], cb[sid]["value"]]})
                elif ca[sid]["status"] == "stated":
                    vn += 1
                    veq += norm_value(ca[sid]["value"]) == norm_value(cb[sid]["value"])
        diffs = {p: round(abs(share[0][p] - share[1][p]) / total[p], 3) for p in total if total[p] >= 20}
        report.update({"P2_consensus_status_agreement": round(eq / n, 3), "slots": n,
                       "P3_unspecified_share_diff": diffs, "P3_max_diff": max(diffs.values()) if diffs else None,
                       "value_agreement_among_stated": round(veq / vn, 3) if vn else None,
                       "gate_met": bool(valid and eq / n >= 0.90 and (not diffs or max(diffs.values()) <= 0.10)),
                       "consensus_disagreements": disagreements})
    write_json(out / "measure.json", report)
    print(json.dumps({k2: v for k2, v in report.items() if k2 != "consensus_disagreements"}, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["run", "measure"])
    p.add_argument("--iteration", required=True)
    p.add_argument("--set", default="dev")
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--k", type=int, default=3)
    p.add_argument("--model", default="gpt-5.6-luna")
    p.add_argument("--reasoning-effort", default="high")
    p.add_argument("--repairs", type=int, default=4)
    p.add_argument("--timeout", type=int, default=2700)
    p.add_argument("--max-workers", type=int, default=12)
    a = p.parse_args()
    run(a) if a.command == "run" else measure(a)


if __name__ == "__main__":
    main()
