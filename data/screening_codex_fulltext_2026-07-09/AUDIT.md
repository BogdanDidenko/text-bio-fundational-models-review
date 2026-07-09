# Full-Text Codex Screening Rerun Audit

Created: `2026-07-09`

This audit documents the full-text rerun of the existing agentic screening
pipeline. Unlike earlier title/abstract-only screening, this run supplied each
agent with Docling-derived full-text section evidence: abstract, introduction,
discussion/conclusion, and data/model/input representation sections where
available.

## Why This Rerun Exists

The previous agentic pipeline screened records mainly from title and abstract.
For candidate full-text/manual eligibility decisions, we reran the same
screening topology with richer evidence extracted from Docling markdown.

The goal was not to replace manual eligibility review, but to produce a
transparent, section-grounded machine screening pass with preserved per-role
logs for every decision.

## Source Inputs

The full-text screening input was built from two final Docling coverage
manifests:

- `data/docling_include_final_coverage_2026-07-09/final_docling_manifest.csv`
- `data/docling_uncertain_final_coverage_2026-07-09/final_docling_manifest.csv`

Only rows with `final_docling_status == docling_ok` were eligible for this
rerun.

Input cohort after filtering:

- Total records: **235**
- From prior INCLUDE corpus: **148**
- From prior UNCERTAIN corpus: **87**

The generated agent input file is:

- `data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_screening_input.json`

The Docling markdown source files used by the extractor are preserved under:

- `data/docling_include_no_vlm_2026-07-09/markdown/`
- `data/docling_uncertain_biorxiv_chrome_no_vlm_2026-07-08/markdown/`
- `data/docling_uncertain_chrome_remaining_no_vlm_2026-07-08/markdown/`
- `data/docling_uncertain_html_no_vlm_2026-07-08/markdown/`
- `data/docling_uncertain_manual_downloads2_no_vlm_2026-07-08/markdown/`
- `data/docling_uncertain_manual_downloads3_no_vlm_2026-07-09/markdown/`
- `data/docling_uncertain_manual_downloads_no_vlm_2026-07-08/markdown/`
- `data/docling_uncertain_no_vlm_2026-07-08/markdown/`
- `data/docling_uncertain_no_vlm_retry_2026-07-08/markdown/`
- `data/docling_uncertain_problem_retry2_no_vlm_2026-07-08/markdown/`
- `data/docling_uncertain_problem_retry_no_vlm_2026-07-08/markdown/`

The generated input also records `docling_chunks` paths where available, but
the section extraction script for this rerun read the Docling markdown files,
not the chunk JSONL files.

The section extraction audit for every record is:

- `data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_section_audit.csv`

The heading frequency audit is:

- `data/fulltext_screening_context_2026-07-09_compact_v2/heading_frequency.json`

## Docling Section Extraction

Script:

- `scripts/docling/build_fulltext_screening_context.py`

Command:

```bash
python3 scripts/docling/build_fulltext_screening_context.py \
  --output-dir data/fulltext_screening_context_2026-07-09_compact_v2
```

Output:

```json
{
  "records": 235,
  "output": "data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_screening_input.json",
  "audit": "data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_section_audit.csv",
  "heading_frequency": "data/fulltext_screening_context_2026-07-09_compact_v2/heading_frequency.json"
}
```

The extractor parsed Docling markdown headings and selected up to:

- 1 abstract-like section
- 1 introduction/background-like section
- 2 discussion/conclusion-like sections
- 4 data/model/input representation-like sections

The maximum selected section text length was **1600 characters** per section.

Context coverage:

- `ok`: **225**
- `fallback_document_opening`: **10**
- `no_matching_sections`: **0** after fallback

Fallback behavior:

- If no matching headings were found, the builder used the first meaningful
  Docling markdown text block as `document_opening`.
- This fallback was explicitly marked in `section_evidence` and
  `fulltext_section_audit.csv`; it was not labeled as abstract,
  introduction, methods, or discussion.

Most frequent selected headings:

- `abstract | abstract`: 173
- `introduction | introduction`: 171
- `discussion_conclusion | discussion`: 148
- `data_representation | methods`: 66
- `discussion_conclusion | conclusion`: 63
- `data_representation | datasets`: 32
- `data_representation | model architecture`: 25
- `document_opening | Docling opening text`: 10

## What Each Agent Received As Input

The runner input was:

- `data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_screening_input.json`

Each record in that JSON included the standard screening metadata plus
Docling-derived evidence:

- `record_id`
- `candidate_id`
- `source_record_id`
- `source_corpus`
- `title`
- `abstract`
- `doi`
- `year`
- `venue`
- `full_text_context`
- `section_evidence`
- `docling_markdown`
- `docling_chunks`
- `docling_status`

For each agent batch, the runner created a complete prompt containing:

- the role prompt template from `protocol/screening_prompt_templates/`
- a full-text evidence mode instruction
- the per-record JSON payload
- strict JSON output schema requirements

Batch size was **1**, so every prompt contains exactly one record. This makes
the input to each agent decision directly inspectable.

Per-batch prompt files are stored at:

- `data/screening_codex_fulltext_2026-07-09/role_logs/scope_reviewer/batch_*.prompt.txt`
- `data/screening_codex_fulltext_2026-07-09/role_logs/architecture_reviewer/batch_*.prompt.txt`
- `data/screening_codex_fulltext_2026-07-09/role_logs/adjudicator/batch_*.prompt.txt`

Each corresponding response and parsed output is stored beside the prompt:

- `batch_*.response.txt`
- `batch_*.parsed.json`
- `batch_*.meta.json`
- `batch_*.stdout.log`
- `batch_*.stderr.log`

## Agentic Pipeline

Script:

- `scripts/run_codex_screening_pipeline.py`

Model:

- `gpt-5.4-mini`

Topology:

1. `scope_reviewer`
2. `architecture_reviewer`
3. Python gate logic
4. `adjudicator` only for unresolved or conflicting cases
5. Final aggregation

The runner was updated for this rerun to preserve full-text context fields and
to add full-text instructions to the existing prompts. It still uses the same
role topology and structured output schemas.

Initial full run command:

```bash
python3 scripts/run_codex_screening_pipeline.py \
  --input data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_screening_input.json \
  --output-dir data/screening_codex_fulltext_2026-07-09 \
  --model gpt-5.4-mini \
  --batch-size 1 \
  --adjudicator-batch-size 1 \
  --max-workers 16
```

Recovery commands used after isolated long-running CLI calls:

```bash
python3 scripts/run_codex_screening_pipeline.py \
  --input data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_screening_input.json \
  --output-dir data/screening_codex_fulltext_2026-07-09 \
  --model gpt-5.4-mini \
  --batch-size 1 \
  --adjudicator-batch-size 1 \
  --max-workers 1 \
  --start-at architecture
```

```bash
python3 scripts/run_codex_screening_pipeline.py \
  --input data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_screening_input.json \
  --output-dir data/screening_codex_fulltext_2026-07-09 \
  --model gpt-5.4-mini \
  --batch-size 1 \
  --adjudicator-batch-size 1 \
  --max-workers 16 \
  --start-at adjudicator
```

The runner skips existing `batch_*.parsed.json` files on restart, so these
recovery commands resumed incomplete work without overwriting completed agent
decisions.

## Pipeline Outputs

Run metadata:

- `data/screening_codex_fulltext_2026-07-09/run_metadata.json`

Final summary:

- `data/screening_codex_fulltext_2026-07-09/summary.json`

Final screening outputs:

- `data/screening_codex_fulltext_2026-07-09/final_screening_results.csv`
- `data/screening_codex_fulltext_2026-07-09/final_screening_results.json`

Intermediate structured outputs:

- `data/screening_codex_fulltext_2026-07-09/scope_reviewer.jsonl`
- `data/screening_codex_fulltext_2026-07-09/architecture_reviewer.jsonl`
- `data/screening_codex_fulltext_2026-07-09/python_gate_outputs.json`
- `data/screening_codex_fulltext_2026-07-09/adjudication_queue.json`
- `data/screening_codex_fulltext_2026-07-09/adjudicator.jsonl`

Final decision counts:

- `INCLUDE`: **56**
- `EXCLUDE`: **168**
- `UNCERTAIN`: **11**

Final source counts:

- `python_gate`: **151**
- `adjudicator`: **84**

Final exclusion/decision code counts:

- `EC2_no_text_component`: 123
- `none`: 67
- `review_editorial`: 15
- `EC3_not_generative`: 14
- `application_wrapper`: 13
- `EC1_no_bio_modality`: 1
- `benchmark_resource`: 1
- `EC2_no_substantive_text_bio_bridge`: 1

## Log Completeness

Role log completeness:

- `scope_reviewer`: **235/235** parsed batch outputs
- `architecture_reviewer`: **235/235** parsed batch outputs
- `adjudicator`: **84/84** parsed batch outputs

There were no parse errors and no nonzero-returncode batch failures in the
final completed artifact set.

The complete log tree is:

- `data/screening_codex_fulltext_2026-07-09/role_logs/`

For every role and every batch, the log tree contains:

- input prompt: `batch_*.prompt.txt`
- raw final model message: `batch_*.response.txt`
- parsed structured output: `batch_*.parsed.json`
- execution metadata: `batch_*.meta.json`
- CLI stdout: `batch_*.stdout.log`
- CLI stderr: `batch_*.stderr.log`

## Known Runtime Issue

In three batches, the model returned the expected record plus an extra
hallucinated row. Because batch size was 1 and the expected `record_id` was
present, the runner discarded the extra row and recorded the discarded ID in
`batch_*.meta.json`.

Logged cases:

- `scope_reviewer/batch_0197.meta.json`
  - expected: `full_2026-07-06__rec_003095`
  - removed: `full_2026-07-06__rec_003096`
- `architecture_reviewer/batch_0145.meta.json`
  - expected: `july_update_2026-07-06__rec_000060`
  - removed: `...`
- `architecture_reviewer/batch_0217.meta.json`
  - expected: `full_2026-07-06__rec_003328`
  - removed: `full_2026-07-06__rec_003329`

This issue did not create missing outputs. The expected records have parsed
outputs, and the discarded rows are traceable in metadata.

## Reproducibility Notes

The full-text context file is the exact machine-readable input to the agentic
pipeline. The per-role prompt logs are the exact prompts sent to `codex exec`.
The raw response logs are the exact final model messages captured by the
runner. The parsed JSON files are the structured records used for aggregation.

This commit intentionally preserves both the compact full-text input context
and the full role log tree so that every final decision can be traced from:

1. source Docling manifest row,
2. selected Docling markdown sections,
3. per-agent prompt,
4. per-agent raw response,
5. parsed criterion output,
6. Python gate/adjudicator decision,
7. final CSV/JSON row.
