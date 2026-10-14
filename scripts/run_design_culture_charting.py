#!/usr/bin/env python3
"""Targeted discovery charting for the design-culture analysis (protocol design-culture-charting-v1).

For every included record, an agent reads the complete paper text and charts, with verbatim evidence:
representation comparisons inside the paper, tests of whether outputs depend on the biological input,
evaluation formats, outputs, adaptation of the language model and biological encoders, disclosure of
LLM-generated text, and stated reasons for the chosen input representation.

Each record is charted by independent runs (default 2). Every quote is checked mechanically against
the paper text; failures are sent back for repair. The complete paper is always passed; nothing is
truncated or split.
"""
import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.operation_decomposition import build_packet, sha  # noqa: E402
from scripts.run_operation_decomposition import packet_text, run_codex, write_json, now  # noqa: E402

PROTOCOL = "design-culture-charting-v1.1"  # v1 = two-paper pilot (2026-10-14); v1.1 adds comparison_kind,
# the hybrid arm category and sharper rules for dependence-test results
BASE = ROOT / "analysis/design_culture_charting_2026-10-14"

EVIDENCE_KINDS = ["paper_text", "table", "caption", "equation_context", "vlm_description"]
REPR = ["verbalised_text", "symbolic_tokens", "soft_token_embedding", "cross_attention_or_qformer",
        "contrastive_alignment_only", "conditioning_vector", "image_rendering", "retrieval_or_tool",
        "hybrid_text_plus_embedding", "no_biological_input", "other"]
COMP_KIND = ["representation_form", "encoder_or_feature_source", "information_amount", "ordering_or_values",
             "interface_mechanism", "other"]
MODALITY = ["transcriptomics", "dna_rna_sequence", "protein", "molecule", "image", "graph_or_knowledge",
            "epigenomics", "clinical_or_tabular", "multiple", "other"]
TEST = ["remove_biological_input", "mismatched_or_shuffled_input", "random_or_noise_input",
        "text_only_or_llm_only_baseline", "perturb_content_of_input", "order_or_value_ablation"]
RESULT = ["clear_drop", "small_drop", "no_change", "improved", "mixed", "not_reported"]
EVAL = ["closed_set_classification", "multiple_choice_or_yes_no", "candidate_label_selection",
        "retrieval_or_ranking", "numeric_regression", "open_text_automatic_metrics", "open_text_llm_judge",
        "open_text_human_judge", "generated_biology_computational_metrics", "wet_lab_validation",
        "likelihood_or_perplexity_scoring", "other"]
OUTPUT = ["natural_language", "closed_set_label", "biological_sequence", "expression_or_cell_profile",
          "molecule", "image", "structure", "embedding_or_score", "tool_or_code_actions", "other"]
LLM_STATE = ["frozen", "lora_or_adapter", "full_finetune", "trained_from_scratch", "prompted_only", "unspecified"]
ENC_STATE = ["frozen", "finetuned", "trained_from_scratch", "unspecified"]
CONNECTOR = ["none", "linear", "mlp", "qformer_or_resampler", "cross_attention_layers", "other", "unspecified"]
CONN_STATE = ["trained", "frozen", "not_applicable", "unspecified"]
PROMPTS = ["full_prompts", "partial_or_examples", "none"]
VERIFY = ["human", "automatic", "both", "none_reported"]
REASON = ["leverage_llm_knowledge", "no_architecture_change", "scalability_or_efficiency", "context_length_cost",
          "quantitative_fidelity", "interpretability_or_transparency", "multimodal_generality", "other"]
STANCE = ["for_own_choice", "against_alternative", "limitation_of_own_choice"]


def _obj(props):
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


def _enum(values):
    return {"type": "string", "enum": values}


def _str():
    return {"type": "string"}


def _nstr():
    return {"type": ["string", "null"]}


def _arr(item):
    return {"type": "array", "items": item}


EVIDENCE = _obj({"section_id": _str(), "quote": _str(), "kind": _enum(EVIDENCE_KINDS)})


def schema():
    comp_arm = _obj({"label": _str(), "category": _enum(REPR)})
    return _obj({
        "record_id": _str(),
        "proposed_models": _arr(_str()),
        "representation_comparisons": _arr(_obj({
            "arms": _arr(comp_arm), "comparison_kind": _enum(COMP_KIND), "modality": _enum(MODALITY),
            "design": _enum(["controlled_ablation", "between_systems"]),
            "task": _str(), "metric": _str(), "better_arm": _nstr(), "result_summary": _str(),
            "numbers_stated": _nstr(), "evidence": _arr(EVIDENCE)})),
        "biology_dependence_tests": _arr(_obj({
            "test_type": _enum(TEST), "on_proposed_model": {"type": "boolean"}, "result": _enum(RESULT),
            "result_summary": _str(), "evidence": _arr(EVIDENCE)})),
        "evaluation_formats": _arr(_obj({"format": _enum(EVAL), "task": _str(), "evidence": _arr(EVIDENCE)})),
        "outputs": _arr(_obj({"output": _enum(OUTPUT), "evidence": _arr(EVIDENCE)})),
        "llm_backbones": _arr(_obj({"name": _str(), "size": _nstr(), "state": _enum(LLM_STATE),
                                    "vocabulary_extended": _enum(["yes", "no", "unspecified"]),
                                    "evidence": _arr(EVIDENCE)})),
        "biological_encoders": _arr(_obj({"name": _str(), "state": _enum(ENC_STATE), "evidence": _arr(EVIDENCE)})),
        "connectors": _arr(_obj({"type": _enum(CONNECTOR), "state": _enum(CONN_STATE), "evidence": _arr(EVIDENCE)})),
        "synthetic_text_generators": _arr(_obj({
            "name": _str(), "text_kind": _str(), "version_stated": {"type": "boolean"},
            "prompts_disclosed": _enum(PROMPTS), "decoding_params_stated": {"type": "boolean"},
            "verification": _enum(VERIFY), "used_for": _enum(["training", "evaluation", "both"]),
            "evidence": _arr(EVIDENCE)})),
        "representation_rationale": _arr(_obj({"reason": _enum(REASON), "stance": _enum(STANCE), "summary": _str(),
                                               "evidence": _arr(EVIDENCE)})),
        "coverage_notes": _nstr()})


RULES = """You chart one paper for a PRISMA-ScR scoping review of generative foundation models that combine
natural language with biological data. Read the COMPLETE paper text below and return one JSON object
matching the output schema. Chart only what the paper states; do not infer from general knowledge.

Evidence contract (checked mechanically; failures are returned to you):
- Every item needs at least one evidence entry. `quote` must be copied VERBATIM from the text between the
  cited section's markers (exact characters, including Markdown, LaTeX and spacing). Quote the shortest
  span that states the claim. `section_id` is the id in the SECTION marker.
- Use empty arrays when the paper reports nothing for a field. Never invent items to fill a field.

Fields:
1. proposed_models: the models the authors propose or train (not baselines or data-generation tools).
2. representation_comparisons: experiments that compare two or more WAYS OF DELIVERING biological data to a
   language model, e.g. a gene list written as text vs an expression embedding, soft tokens vs symbolic
   tokens, different numbers of genes, rank vs values, cross-attention vs prefix tokens. One item per
   comparison (task x metric family). `arms` lists the compared representations with the paper's label
   and a category. `design` = controlled_ablation when the same system/backbone is varied only in the
   representation; between_systems when different models that use different representations are
   compared (e.g. the authors' embedding model vs a published text-based model). `better_arm` is the label
   of the arm the paper reports as better (null if no winner or not reported). Copy key numbers into
   numbers_stated when given. `comparison_kind`: representation_form (different forms, e.g. text vs
   embedding vs tokens; an arm that combines text and embedding is hybrid_text_plus_embedding);
   encoder_or_feature_source (same form, different encoder or feature source); information_amount
   (e.g. number of genes, truncation, context length); ordering_or_values (rank vs values, gene order);
   interface_mechanism (e.g. prefix vs cross-attention vs Q-Former). Do NOT put "with vs without
   biological input" here; that is field 3. A baseline that receives the biological data written as
   text (e.g. a gene list given to a text-only LLM) is a representation comparison here, not field 3.
3. biology_dependence_tests: experiments that test whether outputs depend on the biological input:
   removing it, replacing it with mismatched/shuffled/random/noise input, comparing with a text-only or
   LLM-only baseline that receives NO biological data on the same task, perturbing its content, or
   ablating order/values. Component or training-stage ablations that keep the biological input are NOT
   tests here. `result` is the change in performance WITHOUT (or with corrupted) biological input
   relative to the proposed model with its normal input: clear_drop (clearly worse without biology),
   small_drop, no_change, improved (better without biology), mixed, or not_reported.
4. evaluation_formats: the formats used to evaluate the proposed models' main claims. Multiple-choice,
   yes/no and candidate-label selection count separately from free classification. Open text is
   split by how it is scored (automatic metrics, LLM judge, human judge). Use likelihood_or_perplexity_scoring
   when answers are scored by model likelihood instead of generated.
5. outputs: what the proposed models generate or return at use time.
6. llm_backbones: language models inside the proposed system, with size and training state as stated
   (frozen; LoRA/adapter; full fine-tuning; trained from scratch; prompted only; unspecified), and whether
   the vocabulary is extended with new tokens.
7. biological_encoders: pretrained or trained encoders for biological data inside the proposed system and
   their state (frozen; fine-tuned; trained from scratch; unspecified).
8. connectors: modules that map biological representations into the language model (linear, MLP,
   Q-Former/resampler, cross-attention layers, other) and whether they are trained.
9. synthetic_text_generators: other language models used to write, rewrite, paraphrase, annotate or
   summarise text used to train or evaluate the proposed models (not LLM judges, not baselines). Record
   whether the model version is stated, whether prompts are disclosed (full prompts, partial/examples,
   none), whether decoding parameters are stated, and how generated text was verified.
10. representation_rationale: reasons the authors give FOR their own input representation, AGAINST an
   alternative representation, or as a LIMITATION of their own representation.
11. coverage_notes: anything the paper leaves ambiguous for these fields (or null).
"""


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def strip_line_numbers(text):
    """Some preprint PDFs carry margin line numbers that Docling interleaves with the prose
    ("generated based 94 on the advanced"). For a second-chance match only, standalone 1-4 digit
    tokens are removed from both the quote and the paper text."""
    return re.sub(r"(?<!\S)\d{1,4}(?!\S)", " ", text).split()


def evidence_items(doc):
    for field, items in doc.items():
        if isinstance(items, list):
            for i, item in enumerate(items):
                if isinstance(item, dict):
                    for j, ev in enumerate(item.get("evidence") or []):
                        yield f"{field}[{i}].evidence[{j}]", item, ev


def validate(doc, record_id, sections):
    errors = []
    if doc.get("record_id") != record_id:
        errors.append(f"record_id must be {record_id}")
    full = {sid: norm(s["text"]) for sid, s in sections.items()}
    for field, items in doc.items():
        if isinstance(items, list):
            for i, item in enumerate(items):
                if isinstance(item, dict) and not item.get("evidence"):
                    errors.append(f"{field}[{i}] has no evidence")
    for path, item, ev in evidence_items(doc):
        q = norm(ev.get("quote", ""))
        if not q:
            errors.append(f"{path}: empty quote")
            continue
        sid = ev.get("section_id")
        if sid in full and q in full[sid]:
            continue
        hits = [s for s, t in full.items() if q in t]
        if hits:
            ev["section_id"] = hits[0]  # quote is verbatim but cited in the wrong section: correct the id
            continue
        qs = " ".join(strip_line_numbers(q))
        hits = [s for s, t in full.items() if qs and qs in " ".join(strip_line_numbers(t))]
        if hits:
            ev["section_id"] = hits[0]
            ev["match"] = "line_numbers_removed"
            continue
        errors.append(f"{path}: quote not found verbatim in the paper: {ev.get('quote')!r}")
    return errors


def prompt(record_id, manifest, sections, models, previous=None, feedback=None):
    parts = [RULES, "== Models listed for this record in the review atlas (roles from the review) ==\n"
             + json.dumps(models, ensure_ascii=False, indent=1)]
    if previous is not None:
        parts.append("== Your previous document ==\n" + json.dumps(previous, ensure_ascii=False))
        parts.append("== Required corrections ==\n" + feedback + "\nReturn the COMPLETE corrected document.")
    parts.append(f"== Paper full text: record {record_id}, packet {manifest['packet_sha256']} ==\n"
                 + packet_text(manifest, sections))
    return "\n\n".join(parts)


def job(record_id, run_dir, args, models):
    folder = run_dir / "records" / record_id
    status_path = folder / "status.json"
    if status_path.exists():
        return json.loads(status_path.read_text())
    manifest, sections = build_packet(record_id)
    log, doc, errors = [], None, []
    for attempt in range(args.repairs + 1):
        feedback = None if attempt == 0 else "Mechanical validation failed:\n- " + "\n- ".join(errors)
        stage = "extract" if attempt == 0 else "repair"
        new, meta = run_codex(prompt(record_id, manifest, sections, models, doc if attempt else None, feedback),
                              schema(), folder / "attempts" / f"{attempt + 1:02d}_{stage}", args.model,
                              args.timeout, args.reasoning_effort)
        log.append({"attempt": f"{attempt + 1:02d}_{stage}", "status": meta["status"],
                    "elapsed_seconds": meta["elapsed_seconds"]})
        if new is None:
            errors = ["agent returned no parseable document"]
            continue
        doc = new
        errors = validate(doc, record_id, sections)
        if not errors:
            write_json(folder / "final_document.json", doc)
            status = {"record_id": record_id, "status": "valid", "attempts": log}
            write_json(status_path, status)
            return status
    if doc is not None:
        write_json(folder / "last_invalid_document.json", doc)
    status = {"record_id": record_id, "status": "failed_validation", "attempts": log, "errors": errors}
    write_json(status_path, status)
    return status


def run(args):
    records = json.loads(Path(args.records).read_text())
    roles = json.loads(Path(args.roles).read_text())
    out = BASE / args.iteration
    write_json(out / "run_config.json", {"started_at": now(), "protocol": PROTOCOL, "records": records,
                                          "runs": args.runs, "model": args.model,
                                          "reasoning_effort": args.reasoning_effort, "repairs": args.repairs,
                                          "rules_sha256": sha(RULES), "schema_sha256": sha(json.dumps(schema(), sort_keys=True))})
    jobs = [(r, out / f"run_{k}") for k in range(1, args.runs + 1) for r in records]
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(job, r, d, args, roles.get(r, [])): (r, d.name) for r, d in jobs}
        for n, f in enumerate(as_completed(futures), 1):
            r, d = futures[f]
            try:
                s = f.result()
                print(f"[{n}/{len(jobs)}] {d} {r} {s['status']}", flush=True)
            except Exception as exc:  # keep the pool running; the record is retried on the next invocation
                print(f"[{n}/{len(jobs)}] {d} {r} ERROR {exc!r}", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--records", required=True, help="JSON list of record ids")
    p.add_argument("--roles", required=True, help="JSON {record_id: [{model_name, role}]}")
    p.add_argument("--iteration", required=True)
    p.add_argument("--runs", type=int, default=2)
    p.add_argument("--model", default="gpt-5.6-luna")
    p.add_argument("--reasoning-effort", default="high")
    p.add_argument("--repairs", type=int, default=3)
    p.add_argument("--timeout", type=int, default=2700)
    p.add_argument("--max-workers", type=int, default=12)
    run(p.parse_args())
