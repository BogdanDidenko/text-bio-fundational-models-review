"""Decompose every included paper's model input data flow with native `codex exec` agents.

Per record (resumable; every attempt keeps prompt, schema, response, JSONL events, stderr):
  1. extract   - extractor agent returns trajectories + operation decomposition (strict schema)
  2. repair    - deterministic validation errors are returned to the extractor (<= --repairs)
  3. review    - an independent reviewer agent in a fresh context audits steps against quotes
  4. revise    - blocking findings go back to the extractor, then validation + review again
                 (<= --review-rounds)
Final per-record status: accepted | accepted_with_open_findings | failed_validation | agent_failed.
The codex invocation mirrors scripts/run_taxonomy_semantic_correction.py (read-only sandbox,
ephemeral, tools disabled, prompt on stdin, --output-schema). No API client is used.
"""

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.operation_decomposition import (  # noqa: E402
    ATLAS, CATALOG, PILOT_RECORDS, atlas_seed, build_packet, canonicalize_quotes, coverage_warnings, encoded,
    evidence_entries, extraction_schema, review_schema, sha, validate_document,
)

OUT = ROOT / "analysis/operation_decomposition_2026-10-07"
GUIDE = ROOT / "protocol/REPRESENTATION_LIBRARY_GUIDE.md"
EXAMPLES = ROOT / "analysis/operation_decomposition_2026-10-07/worked_examples.json"
# gpt-5.4-mini / gpt-5.4 (earlier repo standard) are no longer served to ChatGPT-account Codex
# (HTTP 400, checked 2026-10-08); author chose gpt-5.6-luna for both roles.
DEFAULT_MODEL = "gpt-5.6-luna"
RELEASE = "corpus-candidate"


CHILDREN = set()


def _terminate_children(signum, _frame):
    """Stop every running codex process group, then exit (codex runs in its own session)."""
    for proc in list(CHILDREN):
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    os._exit(128 + signum)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def run_codex(prompt, schema, folder, model, timeout, effort):
    """One native codex exec call; same flags as the repo's taxonomy correction runner."""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "prompt.txt").write_text(prompt, encoding="utf-8")
    write_json(folder / "output_schema.json", schema)
    response = folder / "response.json"
    started, clock = now(), time.monotonic()
    with tempfile.TemporaryDirectory(prefix="operation-decomposition-") as workspace:
        command = ["codex", "exec", "--model", model, "--cd", workspace, "--sandbox", "read-only",
                   "--skip-git-repo-check", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
                   "--disable", "shell_tool", "--disable", "unified_exec", "--strict-config",
                   "--disable", "apps", "--disable", "plugins", "--disable", "enable_mcp_apps",
                   "--disable", "browser_use", "--disable", "computer_use", "--disable", "plugin_sharing",
                   "--disable", "tool_suggest", "--disable", "workspace_dependencies"]
        if effort:
            command += ["-c", f'model_reasoning_effort="{effort}"']
        command += ["--output-last-message", str(response.resolve()), "--output-schema",
                    str((folder / "output_schema.json").resolve()), "-"]
        process = subprocess.Popen(command, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, cwd=workspace, start_new_session=True,
                                   env={**os.environ, "NO_COLOR": "1"})
        CHILDREN.add(process)
        try:
            stdout, stderr = process.communicate(input=prompt, timeout=timeout)
            status = "ok" if process.returncode == 0 and response.is_file() else "failed"
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                stdout, stderr = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
            status, returncode = "timeout", None
        finally:
            CHILDREN.discard(process)
    (folder / "stdout.jsonl").write_text(stdout or "", encoding="utf-8")
    (folder / "stderr.log").write_text(stderr or "", encoding="utf-8")
    meta = {"status": status, "returncode": returncode, "model": model, "reasoning_effort": effort,
            "command": command, "started_at": started, "elapsed_seconds": round(time.monotonic() - clock, 1),
            "prompt_sha256": sha(prompt)}
    parsed = None
    if status == "ok":
        try:
            parsed = json.loads(response.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            meta.update(status="unparseable_response", error=str(exc))
    else:
        meta["error"] = (stderr or "")[-4000:]
    write_json(folder / "meta.json", meta)
    return parsed, meta


# ---------------------------------------------------------------- prompts

def packet_text(manifest, sections):
    parts = []
    for item in manifest["sections"]:
        sid = item["section_id"]
        parts.append(f"<<<SECTION {sid} | heading_path: {' > '.join(item['heading_path'])}>>>\n"
                     f"{sections[sid]['text']}<<<END {sid}>>>")
    return "\n".join(parts)


RULES = """Output contract (enforced mechanically; violations are returned to you):
- Return one JSON object matching the output schema. record_id must equal the record below.
- Evidence quotes must be copied VERBATIM from the cited section's text between its SECTION markers
  (exact characters, including Markdown, LaTeX and spacing). Quote the shortest span that states the
  claim. Never paraphrase inside `quote`. Every node, step and trajectory needs evidence.
- One trajectory per documented model variant x task configuration x lifecycle phase x receiving
  component. Cover every model listed in the atlas seed; when the paper does not document a model's
  input path, say so in coverage_questions instead of inventing one.
- `nodes` are source data/resources (measured data, token IDs, parameter tables, prompts...). Node IDs
  are unique within a trajectory. Symbolic shapes use named axes only; never concrete widths.
- `steps` are the source-stated transformations in the paper's own terms (operation_type is a snake_case
  description of what the paper says happens). Each step's `decomposition` lists library calls:
    * every call uses an operation_id from the catalog and binds named ports exactly as declared;
    * every parameter the catalog declares for that operation must be present; use the value
      "unspecified" when the paper does not establish it; extra documented parameters are allowed;
    * calls must consume every step input and produce every step output; a new intermediate between
      calls goes in `intermediate_nodes` with node_id "<step_id>::<name>" and origin
      documented_intermediate (or implicit_parameter for an unstated parameter table);
    * decompose into several calls ONLY when the paper states the operations and their order;
    * when the internal computation cannot be established, return EXACTLY ONE decomposition entry with
      operation_id null and empty inputs/outputs/parameters: the step stays an unexpanded boundary;
    * never assign addition, concatenation or any algebra from architectural convention.
- Conditional application goes in `condition`; a documented skip goes in `bypasses`.
- A computation that no catalog operation represents stays an unexpanded boundary and is listed in
  operation_proposals with the compared operation_ids. Do not invent operation_ids.
"""


def extraction_prompt(record_id, seed, manifest, sections, guide, catalog, examples, previous=None, feedback=None):
    head = ["You are an operation-decomposition agent for a PRISMA-ScR scoping review of generative foundation "
            "models that combine text with biological data. Reconstruct, from the paper text only, how each "
            "model's inputs are transformed into what the model receives.",
            "== Shared agent protocol ==\n" + guide,
            "== Operation catalog (the only allowed operation_ids, ports and declared parameters) ==\n"
            + json.dumps(catalog, ensure_ascii=False, indent=1),
            RULES,
            "== Worked examples from the reviewed pilot (same output format; their quotes come from other papers) ==\n"
            + json.dumps(examples, ensure_ascii=False),
            "== Atlas seed for this record (coverage checklist; the paper text is authoritative) ==\n"
            + json.dumps(seed, ensure_ascii=False, indent=1)]
    if previous is not None:
        head.append("== Your previous document ==\n" + json.dumps(previous, ensure_ascii=False))
        head.append("== Required corrections ==\n" + feedback +
                    "\nReturn the COMPLETE corrected document (not a diff). Keep everything that was correct.")
    head.append(f"== Paper full text: record {record_id}, packet {manifest['packet_sha256']} ==\n"
                + packet_text(manifest, sections))
    return "\n\n".join(head)


def review_prompt(record_id, seed, manifest, sections, guide, catalog, document, warnings):
    return "\n\n".join([
        "You are an independent reviewer for a PRISMA-ScR scoping review. Another agent reconstructed the model "
        "input data flow of this paper as operation calls. You did not write it. Check it against the paper text.",
        "== Shared agent protocol ==\n" + guide,
        "== Operation catalog ==\n" + json.dumps(catalog, ensure_ascii=False, indent=1),
        "Review procedure:\n"
        "- For every step, read its quotes in the paper text. Flag a step whose quotes do not support the stated "
        "transformation, whose decomposition asserts operations or an order the paper does not state, whose port "
        "bindings put a table among keys (or similar), or whose parameter values are not established by the text.\n"
        "- Flag missing documented steps, branches, conditional bypasses, models, tasks or lifecycle phases.\n"
        "- Treat a justified unexpanded boundary as correct. Do not ask for algebra the paper omits.\n"
        "- severity=blocking for anything that makes the graph wrong or unsupported; minor otherwise.\n"
        "- verdict=accept only when there are no blocking findings. Cite paper evidence verbatim in findings.",
        "== Atlas seed ==\n" + json.dumps(seed, ensure_ascii=False, indent=1),
        "== Mechanical warnings ==\n" + (json.dumps(warnings, ensure_ascii=False) if warnings else "none"),
        "== Document under review ==\n" + json.dumps(document, ensure_ascii=False),
        f"== Paper full text: record {record_id} ==\n" + packet_text(manifest, sections),
    ])


# ---------------------------------------------------------------- per-record pipeline

def process_record(record_id, args, catalog, library_sha256, guide, examples, atlas):
    base = args.output / "records" / record_id
    status_path = base / "status.json"
    if status_path.exists() and not args.force:
        status = json.loads(status_path.read_text())
        if status["status"] in {"accepted", "accepted_with_open_findings"} or not args.retry_failed:
            return status
    if base.exists() and args.force:
        shutil.rmtree(base)
    manifest, sections = build_packet(record_id)
    write_json(base / "packet_manifest.json", manifest)
    for sid, s in sections.items():
        path = base / "sections" / f"{sid}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(s["text"], encoding="utf-8")
    seed = atlas_seed(record_id, atlas)
    attempts = sorted((base / "attempts").glob("*")) if (base / "attempts").exists() else []
    counter = [len(attempts)]
    canonicalized = [0]
    log = []

    def attempt(stage, prompt, schema):
        counter[0] += 1
        folder = base / "attempts" / f"{counter[0]:02d}_{stage}"
        parsed, meta = run_codex(prompt, schema, folder, args.model if stage != "review" else args.review_model,
                                 args.timeout, args.reasoning_effort)
        log.append({"attempt": folder.name, "status": meta["status"], "elapsed_seconds": meta["elapsed_seconds"]})
        return parsed

    def finish(status, **extra):
        value = {"record_id": record_id, "status": status, "finished_at": now(), "attempts": log,
                 "packet_sha256": manifest["packet_sha256"], "source_sha256": manifest["source_sha256"],
                 "whitespace_canonicalized_quotes": canonicalized[0], **extra}
        write_json(status_path, value)
        return value

    def extract_until_valid(previous=None, feedback=None):
        doc = attempt("extract" if previous is None else "revise",
                      extraction_prompt(record_id, seed, manifest, sections, guide, catalog, examples, previous, feedback),
                      extraction_schema(catalog))
        for _ in range(args.repairs + 1):
            if doc is None:
                return None, ["agent returned no parseable document"], [], []
            canonicalized[0] += canonicalize_quotes(doc, sections)
            errors, warnings, assemblies = validate_document(doc, record_id, sections, catalog, library_sha256, RELEASE)
            if not errors:
                return doc, [], warnings + coverage_warnings(doc, seed), assemblies
            if _ == args.repairs:
                return doc, errors, warnings, []
            doc = attempt("repair", extraction_prompt(record_id, seed, manifest, sections, guide, catalog, examples, doc,
                                                      "Mechanical validation failed:\n- " + "\n- ".join(errors)),
                          extraction_schema(catalog))
        return doc, ["unreachable"], [], []

    doc, errors, warnings, assemblies = extract_until_valid()
    if doc is None:
        return finish("agent_failed", errors=errors)
    if errors:
        write_json(base / "last_invalid_document.json", doc)
        return finish("failed_validation", errors=errors)
    review = None
    for round_index in range(args.review_rounds + 1):
        review = attempt("review", review_prompt(record_id, seed, manifest, sections, guide, catalog, doc, warnings), review_schema())
        if review is None:
            return finish("agent_failed", errors=["reviewer returned no parseable verdict"])
        write_json(base / f"review_round_{round_index + 1}.json", review)
        blocking = [f for f in review["findings"] if f["severity"] == "blocking"]
        if review["verdict"] == "accept" and not blocking:
            break
        if round_index == args.review_rounds:
            break
        feedback = "Independent reviewer findings:\n" + json.dumps(review["findings"], ensure_ascii=False, indent=1)
        revised, errors, warnings_new, assemblies_new = extract_until_valid(doc, feedback)
        if revised is None or errors:
            break  # keep the last valid document; its open findings stay recorded
        doc, warnings, assemblies = revised, warnings_new, assemblies_new
    open_blocking = [f for f in review["findings"] if f["severity"] == "blocking"] if review else []
    write_json(base / "final_document.json", doc)
    write_json(base / "assemblies.json", assemblies)
    write_json(base / "evidence.json", sorted(evidence_entries(record_id, assemblies, sections, manifest).values(),
                                              key=lambda e: e["evidence_id"]))
    calls = [c for a in assemblies for c in a["calls"]]
    return finish("accepted" if not open_blocking else "accepted_with_open_findings",
                  trajectories=len(assemblies), calls=len(calls),
                  library_calls=sum(1 for c in calls if c["operation_id"]),
                  unexpanded=sum(1 for c in calls if not c["operation_id"]),
                  open_blocking_findings=len(open_blocking), warnings=warnings,
                  operation_proposals=doc.get("operation_proposals", []))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--records", nargs="*", help="Record IDs (default: every included record not in the pilot)")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--review-model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning-effort", default="high", help="codex model_reasoning_effort; empty string = codex default")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=2700)
    parser.add_argument("--repairs", type=int, default=4)
    parser.add_argument("--review-rounds", type=int, default=2, help="Revision rounds after the first review")
    parser.add_argument("--force", action="store_true", help="Discard previous attempts for selected records")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Write packets and prompts; call no agent")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, _terminate_children)
    signal.signal(signal.SIGINT, _terminate_children)
    if not args.dry_run and shutil.which("codex") is None:
        raise SystemExit("`codex` CLI not found on PATH")
    catalog = json.loads(CATALOG.read_text())
    library_sha256 = sha(encoded(catalog))
    guide = GUIDE.read_text(encoding="utf-8")
    examples = json.loads(EXAMPLES.read_text())
    atlas = json.loads(ATLAS.read_text())
    included = sorted({m["record_id"] for m in atlas["architectures"]})
    records = args.records or [r for r in included if r not in PILOT_RECORDS]
    unknown = set(records) - set(included)
    if unknown:
        raise SystemExit(f"Not included records: {sorted(unknown)}")
    if args.limit:
        records = records[:args.limit]
    write_json(args.output / "run_config.json", {"started_at": now(), "records": records, "model": args.model,
               "review_model": args.review_model, "reasoning_effort": args.reasoning_effort,
               "repairs": args.repairs, "review_rounds": args.review_rounds, "library_sha256": library_sha256,
               "catalog_release": catalog["release"], "guide_sha256": sha(guide)})

    if args.dry_run:
        for record_id in records:
            manifest, sections = build_packet(record_id)
            prompt = extraction_prompt(record_id, atlas_seed(record_id, atlas), manifest, sections, guide, catalog, examples)
            folder = args.output / "dry_run" / record_id
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "extract_prompt.txt").write_text(prompt, encoding="utf-8")
            write_json(folder / "packet_manifest.json", manifest)
            print(f"{record_id}\tsections={len(sections)}\tprompt_chars={len(prompt)}")
        write_json(args.output / "dry_run" / "output_schema.json", extraction_schema(catalog))
        return

    results = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(process_record, r, args, catalog, library_sha256, guide, examples, atlas): r for r in records}
        for future in as_completed(futures):
            record_id = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # keep the batch going; the error is recorded per record
                result = {"record_id": record_id, "status": "runner_error", "errors": [repr(exc)]}
                write_json(args.output / "records" / record_id / "status.json", result)
            results.append(result)
            print(f"[{len(results)}/{len(records)}] {record_id} {result['status']} "
                  f"trajectories={result.get('trajectories', '-')} calls={result.get('calls', '-')}", flush=True)
    summarize(args.output)


def summarize(output):
    rows = [json.loads(p.read_text()) for p in sorted((output / "records").glob("*/status.json"))]
    summary = {"generated_at": now(), "records": len(rows),
               "by_status": {s: sum(1 for r in rows if r["status"] == s) for s in sorted({r["status"] for r in rows})},
               "trajectories": sum(r.get("trajectories", 0) for r in rows),
               "calls": sum(r.get("calls", 0) for r in rows),
               "library_calls": sum(r.get("library_calls", 0) for r in rows),
               "unexpanded": sum(r.get("unexpanded", 0) for r in rows),
               "open_blocking_findings": sum(r.get("open_blocking_findings", 0) for r in rows),
               "operation_proposals": [dict(p, record_id=r["record_id"]) for r in rows for p in r.get("operation_proposals", [])],
               "records_detail": [{k: r.get(k) for k in ("record_id", "status", "trajectories", "calls", "unexpanded",
                                                         "open_blocking_findings")} for r in rows]}
    write_json(output / "corpus_status.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in {"records_detail", "operation_proposals"}}, indent=2))


if __name__ == "__main__":
    main()
