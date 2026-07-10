# Full-Text Section Screening: Executed Method and Audit Trail

## Status and purpose

This document records the executed second-stage, machine-assisted screening
run performed on 2026-07-10. It supplements, rather than replaces, the
title/abstract screening procedure in `protocol/screening_process.md`.

The objective was to reassess records using targeted full-text evidence about
the biological data and its model input representation. The stage produces
auditable automated decisions for the review workflow; it does not replace the
subsequent human/manual eligibility confirmation and data-charting steps.

## Corpus and flow checkpoint

| Stage | Records | Operational definition |
|---|---:|---|
| Full-text records available to Docling Graph | 235 | Records with a Docling-converted source document in the full-text corpus. |
| Records with a valid `data_source` and `input_representation` section | 221 | Both targeted sections were required after provenance resolution and structural quality checks. |
| Records without a valid dual-section evidence input | 14 | Retained in the audit as a preprocessing limitation; not counted as a semantic PRISMA exclusion. |
| Automated full-text-section decisions | 221 | Final decisions after the two role passes, Python gate, and adjudication where needed. |
| Automated INCLUDE | 50 | Candidates for the next manual eligibility/data-extraction stage. |
| Automated EXCLUDE | 165 | Exclusion code is retained per record in the final output. |
| Automated UNCERTAIN | 6 | Retained for manual review. |
| Adjudicated | 67 | Records sent to the adjudicator because the first-pass criteria were unresolved or conflicted. |

The 14 records without a valid dual-section input must remain visible in the
PRISMA-style accounting. They were not excluded for topic, model, or paper
type. They could not enter this specific evidence-based screening pass because
one or both required targeted sections were absent, unresolved, or
document-level rather than a meaningful section.

## Stage A: Docling conversion and Docling Graph evidence extraction

The input consisted of previously generated `.docling.json` documents. The
runner was `scripts/docling/run_docling_graph_screening_evidence.py` with the
`BiomedicalScreeningEvidence` Pydantic template, `extraction_contract=direct`,
and `provenance=detailed`.

`direct` means that Docling Graph asked `gpt-5.4-mini` for one structured
extraction from each paper's Docling markdown. No `context_limit`, input text
cap, or output `max_tokens` cap was supplied for this run. The local
OpenAI-compatible Codex wrapper was used only to expose `gpt-5.4-mini` to
Docling Graph; the Graph template produced the structured evidence nodes.

The completed Graph run used 16 shards and covered all 235 records. The
public run summary and shard logs are in:

- `data/docling_graph_screening_evidence_full_2026-07-10_gpt54mini_direct_nolimits_16shards/parallel_run_summary.json`
- `data/docling_graph_screening_evidence_full_2026-07-10_gpt54mini_direct_nolimits_16shards/logs/`

For each record, the public `screening_evidence_summary.json` preserves the
Graph entities, evidence quotes, provenance links, heading trails, resolved
chunks, and derived full-section payloads. The raw intermediate Docling
documents are not committed because the complete local artifact is about 8 GB;
the summaries required to inspect the evidence-selection decision are tracked.

## Stage B: From Graph provenance to complete targeted sections

The section builder was
`scripts/docling/build_docling_graph_pipeline_input.py`. It did not use a
heading-name regex to choose a section. Its sequence was:

1. Read a Graph `DataSourceEvidence` or `InputRepresentationEvidence` node.
2. Resolve the node's Docling Graph provenance chunk and its heading trail.
3. Deterministically reconstruct the complete source section from that heading
   to the next sibling or ancestor heading in Docling markdown.
4. Consider all provenance-grounded alternatives for each of the two target
   types: `data_source` and `input_representation`.
5. Prefer a specific, non-root grounded section; preserve the complete section
   text without a character cap or truncation.

The clean-input controls were applied before the second-stage reviewer calls:

- one chosen section per target type, with an identical section emitted once
  even if it supports both types;
- reject a reconstructed section covering at least 90% of the source markdown;
- treat a root heading covering at least 80% of a multi-heading document as a
  document-level container rather than a targeted section;
- require both target types with `--require-both-targets`.

The resulting input contains 221 records, 221 `data_source` sections, and 221
`input_representation` sections. It records 11 rejected document-level section
alternatives. The exact selection audit, including all 14 records that did not
meet the dual-section requirement, is in:

- `data/fulltext_screening_context_2026-07-10_docling_graph_direct_all235_clean_both_targets/run_metadata.json`
- `data/fulltext_screening_context_2026-07-10_docling_graph_direct_all235_clean_both_targets/fulltext_section_audit.csv`
- `data/fulltext_screening_context_2026-07-10_docling_graph_direct_all235_clean_both_targets/fulltext_screening_input.json`

## Stage C: Evidence payload sent to the screening roles

For the final valid run, each first-pass reviewer received a record containing
only the following substantive evidence fields:

```text
title
abstract
selected_full_text_sections
```

`record_id` and stable source identifiers were present solely to preserve the
record-to-output mapping. The full source `docling_markdown` and the structured
`section_evidence` payload remained in the local screening-input artifact for
auditability, but were explicitly not rendered into the reviewer prompt. This
avoids sending the whole article or duplicating the selected section text.

The adjudicator additionally received the structured outputs of the two
first-pass roles for the records routed to adjudication. It did not receive raw
PDFs or whole-document markdown.

## Stage D: Role-based decision workflow

The runner was `scripts/run_codex_screening_pipeline.py` using
`--evidence-mode full_text_sections`, `gpt-5.4-mini`, one record per batch,
and up to eight concurrent workers. Canonical runtime prompts and JSON schemas
are versioned in `protocol/screening_prompt_templates/`.

1. `scope_reviewer` assessed paper type, biological modality, substantive text
   component, and substantive text-biology bridge.
2. `architecture_reviewer` assessed paper type where relevant, generative-model
   evidence, and foundation-model evidence.
3. The Python gate combined criterion-level outputs. It directly finalized
   unequivocal INCLUDE/EXCLUDE cases and routed conflict or uncertainty cases
   to the adjudicator.
4. `adjudicator` resolved the 67 queued records using the same selected
   sections plus first-pass structured outputs.
5. The runner generated the final decision, exclusion code, uncertainty reason,
   provenance fields, and concise evidence/rationale fields for every record.

The two first-pass roles are distinct prompts and schemas executed by the same
underlying model. They are not a substitute for two independent human
reviewers. This limitation and the remaining manual-review role for UNCERTAIN
records must be reported in the manuscript.

## Final run outputs and logs

The canonical final output is:

`data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10/`

| Artifact | Purpose |
|---|---|
| `input_records.json` | Exact normalized 221-record input used by the runner. |
| `scope_reviewer.jsonl` | Structured scope outputs for all 221 records. |
| `architecture_reviewer.jsonl` | Structured architecture outputs for all 221 records. |
| `python_gate_outputs.json` | Deterministic gate inputs and routing rationale. |
| `adjudication_queue.json` | The 67 records routed to adjudication. |
| `adjudicator.jsonl` | Structured adjudicator outputs for all 67 queued records. |
| `final_screening_results.json` and `.csv` | Final 221-record decisions and codes. |
| `role_logs/<role>/batch_*.prompt.txt` | Exact operative prompt for each model call. |
| `role_logs/<role>/batch_*.response.txt` | Raw final model message. |
| `role_logs/<role>/batch_*.parsed.json` | Schema-validated structured result. |
| `role_logs/<role>/batch_*.meta.json` | Model, status, timing, record ID(s), and artifact paths. |
| `role_logs/<role>/batch_*.stdout.log` and `.stderr.log` | CLI diagnostics retained for runtime audit. |

The logs preserve concise decision rationales and evidence snippets, not hidden
chain-of-thought. Final validation found 221 unique scope outputs, 221 unique
architecture outputs, 67 unique adjudicator outputs, and 221 unique final
records; all retained final batch metadata has `status: ok`.

## Operational amendment and limitation

Early exploratory full-text runs mistakenly rendered both the whole
`docling_markdown` and `section_evidence.text` alongside the selected sections.
Those fields respectively exposed whole-document content and duplicated the
targeted section text. The exploratory outputs were discarded and are not part
of the reported decision set. The final run above used the corrected payload
contract stated in Stage C.

Some native `codex exec` children also persisted after an otherwise completed
call. The runner was made timeout-aware, and the final canonical output was
validated after explicit retries of failed calls. This is an operational
reproducibility issue, not a content-based exclusion rule. The final repository
artifact contains only successful, schema-validated role outputs.

## Manuscript-ready reporting statement

> We conducted a targeted full-text evidence screening stage after
> title/abstract screening. Docling Graph, using detailed provenance, located
> evidence for the biological data source and model input representation; the
> complete markdown section bounded by the provenance-derived heading was then
> reconstructed deterministically. We retained only records with both targeted
> sections and rejected document-level reconstructions. Role-separated Codex
> reviewers assessed title, abstract, and the complete selected sections; a
> deterministic gate routed unresolved or conflicting records to an adjudicator.
> We retained prompts, raw responses, schema-validated outputs, routing data,
> and final decisions for every processed record. The two reviewer roles used
> different prompts but the same underlying model and were therefore not
> independent human reviewers.
