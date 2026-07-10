# Docling corpus processing

This folder contains the first Docling smoke pipeline for downloaded review PDFs.

## Environment

Use an isolated local environment:

```bash
/Users/bogdan.didenko/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m venv .venv-docling
.venv-docling/bin/python -m pip install --upgrade pip setuptools wheel
.venv-docling/bin/python -m pip install -r scripts/docling/requirements-docling.txt
```

The local env is ignored by git via `.venv-docling/`.

## Docling smoke

```bash
.venv-docling/bin/python scripts/docling/run_docling_smoke.py --limit 5
```

Outputs:

- `data/docling_corpus_2026-07-08/documents/*.docling.json`
- `data/docling_corpus_2026-07-08/markdown/*.md`
- `data/docling_corpus_2026-07-08/chunks/*.jsonl`
- `data/docling_corpus_2026-07-08/figures/<candidate_id>/*.png`
- `data/docling_corpus_2026-07-08/manifests/docling_smoke_manifest.json`

By default, this extracts figures but does not call a remote VLM.

## Native Docling picture descriptions via Codex

To make VLM descriptions part of the Docling conversion itself, start the
local OpenAI-compatible wrapper over `codex exec`:

```bash
.venv-docling/bin/python scripts/docling/codex_openai_compat_server.py \
  --host 127.0.0.1 \
  --port 8765 \
  --model gpt-5.5
```

Then point Docling's native picture-description stage at that endpoint:

```bash
.venv-docling/bin/python scripts/docling/run_docling_smoke.py \
  --limit 1 \
  --picture-description-backend openai-api \
  --openai-base-url http://127.0.0.1:8765/v1/chat/completions \
  --openai-model gpt-5.5 \
  --picture-description-area-threshold 0.0
```

This sets:

- `PdfPipelineOptions.enable_remote_services = True`
- `PdfPipelineOptions.do_picture_description = True`
- `PdfPipelineOptions.picture_description_options = PictureDescriptionVlmEngineOptions(...)`
- `ApiVlmEngineOptions(engine_type=VlmEngineType.API_OPENAI, url=...)`

The generated descriptions are stored inside the `DoclingDocument` picture annotations/meta and are also reflected in each `figures_manifest.json`.

## Ten-paper Codex QA batch

The first 10-paper quality probe is configured here:

```text
scripts/docling/config_docling_codex_10_2026-07-08.json
```

Run it with:

```bash
.venv-docling/bin/python scripts/docling/run_docling_from_config.py \
  --config scripts/docling/config_docling_codex_10_2026-07-08.json
```

Then summarize structural quality:

```bash
.venv-docling/bin/python scripts/docling/analyze_docling_quality.py \
  --out data/docling_corpus_2026-07-08_codex_10
```

The QA report checks conversion success, chunk counts, markdown size, figure
image extraction, figure-description coverage, and noisy non-scientific/logo
picture descriptions. Reports are written to:

```text
data/docling_corpus_2026-07-08_codex_10/manifests/quality_report.json
data/docling_corpus_2026-07-08_codex_10/manifests/quality_report.md
```

## VLM parameter iterations

Run the comparable parameter grid over the same 10 PDFs:

```bash
.venv-docling/bin/python scripts/docling/run_docling_iterations.py \
  --config scripts/docling/config_docling_codex_iterations_2026-07-08.json \
  --skip-existing
```

Then rebuild the comparison table:

```bash
.venv-docling/bin/python scripts/docling/compare_docling_iterations.py \
  --iteration-config scripts/docling/config_docling_codex_iterations_2026-07-08.json
```

Comparison outputs:

```text
data/docling_iteration_comparison_2026-07-08/comparison_report.json
data/docling_iteration_comparison_2026-07-08/comparison_report.md
```

Current best setting from the 10-paper probe:

```json
{
  "picture_description_area_threshold": 0.01,
  "picture_description_prompt": "strict SCIENTIFIC_FIGURE / NON_SCIENTIFIC_IMAGE prompt from config_docling_codex_iterations_2026-07-08.json"
}
```

This retained the same useful VLM descriptions as the threshold-only runs while
reducing runtime relative to the `threshold=0.0` baseline.

## Docling Graph extraction via Codex

This is the current path for extracting the full-text evidence sections that
will be passed into the later screening pipeline. The goal is not to classify
the paper here. The goal is to identify the section that describes:

- `data_source`: what biological data the model was trained/evaluated on.
- `input_representation`: how those data are represented as model input.

The same wrapper can serve text-only OpenAI-compatible chat requests from
Docling Graph. For parity with the Codex screening pipeline, start it with
`gpt-5.4-mini`:

```bash
.venv-docling/bin/python scripts/docling/codex_openai_compat_server.py \
  --host 127.0.0.1 \
  --port 8765 \
  --model gpt-5.4-mini \
  --timeout 600
```

Use the OpenAI-compatible base URL without the final endpoint path:

```bash
export CUSTOM_LLM_BASE_URL=http://127.0.0.1:8765/v1
export CUSTOM_LLM_API_KEY=local-codex
```

For Docling Graph API usage, this repo passes a custom LiteLLM-compatible client
to `PipelineConfig(llm_client=...)`. The wrapper supports:

- `GET /health` and `GET /v1/health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- OpenAI `response_format={"type":"json_object"}`
- OpenAI `response_format={"type":"json_schema", ...}` via
  `codex exec --output-schema`

It does not support streaming; keep `stream=false` or omit the field.

### Current extraction method

The current method is deliberately simple:

1. Use existing `.docling.json` files as input.
2. Run Docling Graph with the
   `scripts.docling_graph_templates.biomedical_screening_evidence.BiomedicalScreeningEvidence`
   Pydantic template.
3. Use `extraction_contract=direct`: Docling Graph asks `gpt-5.4-mini` for one
   structured evidence extraction over the paper markdown.
4. Keep Docling Graph `provenance=detailed`.
5. For each extracted `DataSourceEvidence` or `InputRepresentationEvidence`
   node, resolve `node.__provenance__.chunks` through
   `docling_graph/provenance.json`.
6. Take the grounded chunk's Docling `headings` trail.
7. Reconstruct the full source section from the Docling markdown by taking text
   from that heading until the next sibling or ancestor heading.
8. Save the selected `data_source` and `input_representation` sections in
   `section_grounding.sections_for_screening`.

This is not a regex section selector. The section is selected from Docling Graph
evidence provenance: graph node -> provenance chunk/span -> chunk headings ->
full section. By default the runner does not set `max_tokens` or
`context_limit`; pass them only when an explicit diagnostic cap is wanted.

Run the screening-evidence extractor on existing `.docling.json` artifacts:

```bash
.venv-docling/bin/python scripts/docling/run_docling_graph_screening_evidence.py \
  --include-manifest data/docling_include_final_coverage_2026-07-09/final_docling_manifest.csv \
  --uncertain-manifest data/docling_uncertain_final_coverage_2026-07-09/final_docling_manifest.csv \
  --base-url http://127.0.0.1:8765/v1 \
  --model openai/gpt-5.4-mini \
  --extraction-contract direct \
  --provenance detailed \
  --output-dir data/docling_graph_screening_evidence_2026-07-09
```

Each per-record `screening_evidence_summary.json` includes:

- `models`: Docling Graph entities extracted with the
  `BiomedicalScreeningEvidence` Pydantic template.
- `graph` and `provenance_*`: Docling Graph nodes, edges, and grounding
  diagnostics.
- `section_grounding`: Docling Graph native provenance projected into screening
  inputs. The runner resolves each extracted graph node's `__provenance__.chunks`
  through `docling_graph/provenance.json`, preserving the chunk `text`,
  `headings` trail, pages, Docling item refs, geometry, and character spans.
  This is not an independent regex/LLM section selector.
- `derived_full_section`: a deterministic full-section reconstruction attached
  to each grounded chunk. It takes the chunk's Docling Graph `headings` trail,
  finds the matching heading in the Docling markdown, and returns all text until
  the next sibling or ancestor heading. This is marked as derived from Docling
  structure; the native provenance unit remains the chunk/span.
- `sections_for_screening`: primary data-source and input-representation chunks
  with their attached `derived_full_section` payloads.

For reproducible smoke sampling:

```bash
.venv-docling/bin/python scripts/docling/run_docling_graph_screening_evidence.py \
  --sample-size 10 \
  --sample-seed 20260709 \
  --base-url http://127.0.0.1:8765/v1 \
  --model openai/gpt-5.4-mini \
  --extraction-contract direct \
  --provenance detailed \
  --output-dir data/docling_graph_screening_evidence_random10_2026-07-09
```

The sample writes `selected_records.json`, per-record
`screening_evidence_summary.json`, and Docling Graph export artifacts. The
default `direct` contract asks Docling Graph for one evidence extraction over the
paper markdown, then the runner uses Docling Graph provenance to reconstruct the
full source section for screening.

The latest no-default-length-cap smoke was:

```bash
.venv-docling/bin/python scripts/docling/run_docling_graph_screening_evidence.py \
  --sample-size 2 \
  --limit 0 \
  --sample-seed 20260710 \
  --base-url http://127.0.0.1:8765/v1 \
  --model openai/gpt-5.4-mini \
  --timeout 600 \
  --extraction-contract direct \
  --provenance detailed \
  --output-dir data/docling_graph_screening_evidence_smoke_2026-07-10_gpt54mini_direct_nolimits_n2
```

It returned both target sections for both smoke records with grounded evidence
quotes and `0` unresolved provenance nodes:

| record | data_source section | input_representation section |
|---|---|---|
| `rec_003328` MAMMAL | `3 Methods > 3.4 Pretraining` | `3 Methods > 3.2 Entity Representation` |
| `rec_001313` PlantBiMoE | `II. MATERIALS AND METHODS > 1) A pre-training dataset comprising genomic sequences from 42 plant species` | `III. RESULTS > 1) Tokenization` |

### Build screening-pipeline input from a Graph run

After the Graph run, convert its grounded full sections to the existing
`full_text_sections` screening contract:

```bash
.venv-docling/bin/python scripts/docling/build_docling_graph_pipeline_input.py \
  --graph-output data/docling_graph_screening_evidence_sample10_2026-07-10_gpt54mini_direct_nolimits \
  --base-records data/screening_codex_fulltext_2026-07-09/input_records.json \
  --output-dir data/fulltext_screening_context_2026-07-10_docling_graph_direct_sample10_selected_sections
```

The output `fulltext_screening_input.json` is directly accepted by
`scripts/run_codex_screening_pipeline.py --evidence-mode full_text_sections`.
Each record contains the existing title/abstract fields plus
`selected_full_text_sections` and `section_evidence` built from complete
heading-boundary sections. The builder evaluates all Graph provenance
alternatives for `data_source` and `input_representation`, then:

- keeps at most one section per target role and deduplicates a section shared by
  both roles;
- rejects root/document-level sections whose reconstructed text covers at least
  90% of the source markdown;
- records every rejected alternative and the reason in
  `section_selection_audit`;
- supports `--require-both-targets` to exclude records without a valid section
  for both target roles.

There is no section-length cap or truncation. `fulltext_screening_input.jsonl`,
`fulltext_section_audit.csv`, and `run_metadata.json` provide line-oriented,
tabular, and run-level audit views. Use the strict form for a clean rerun:

```bash
.venv-docling/bin/python scripts/docling/build_docling_graph_pipeline_input.py \
  --graph-output data/docling_graph_screening_evidence_full_2026-07-10_gpt54mini_direct_nolimits_16shards \
  --base-records data/screening_codex_fulltext_2026-07-09/input_records.json \
  --require-both-targets \
  --output-dir data/fulltext_screening_context_2026-07-10_docling_graph_direct_all235_clean_both_targets
```

## Fallback/diagnostic Codex figure descriptions

This path is not the primary pipeline. It is useful only for comparing Docling-native enrichment with a separate Codex CLI pass:

```bash
.venv-docling/bin/python scripts/docling/codex_describe_figures.py --limit 5 --model gpt-5.5
```

The structured model output is in `codex_result.final_message` inside:

```text
data/docling_corpus_2026-07-08/codex_descriptions/*.jsonl
```

`stderr_tail` is retained only for debugging noisy Codex CLI runs.

## UNCERTAIN full-text Docling coverage

The no-VLM full-text preprocessing pass for records with an `UNCERTAIN`
screening decision is tracked with one final per-record coverage manifest:

```bash
.venv-docling/bin/python scripts/docling/build_uncertain_final_coverage.py
```

Current accounting:

- 88 `UNCERTAIN` records total
- 87 records with usable Docling artifacts
- 81 processed from PDF
- 6 processed from HTML/article pages
- 1 unavailable/gated publisher full text

Final outputs:

```text
data/docling_uncertain_final_coverage_2026-07-09/final_docling_manifest.csv
data/docling_uncertain_final_coverage_2026-07-09/final_docling_manifest.json
data/docling_uncertain_final_coverage_2026-07-09/final_docling_coverage_summary.md
```

The only unresolved full-text item is:

```text
rec_002409 — Generative AI Models for the Protein Scaffold Filling Problem
DOI: 10.1089/cmb.2024.0510
status: unavailable_gated
```

## INCLUDE full-text Docling coverage

The no-VLM full-text preprocessing pass for records with an `INCLUDE`
screening decision is configured here:

```text
scripts/docling/config_docling_include_no_vlm_2026-07-09.json
```

The config is generated from the full-text master manifest:

```bash
.venv-docling/bin/python scripts/docling/build_include_docling_config.py
```

Run the configured Docling pass with:

```bash
.venv-docling/bin/python scripts/docling/run_docling_from_config.py \
  --config scripts/docling/config_docling_include_no_vlm_2026-07-09.json
```

The final per-record coverage manifest is built from the PDF mapping and the
actual candidate-id artifacts:

```bash
.venv-docling/bin/python scripts/docling/build_include_final_coverage.py
```

Current accounting:

- 155 `INCLUDE` records total
- 152 records with PDF available before Docling
- 148 records with usable Docling artifacts
- 4 records with PDF present but failed/missing Docling artifacts
- 3 records without a PDF after automated, web/manual-link, and user manual retry
- 18,340 selected chunks and 1,447 selected figures
- 1 low-quality but successful artifact flagged for manual review
- 3 duplicate PDF-hash groups among `INCLUDE` records

The final INCLUDE PDF retry audit is:

```text
data/full_text_include_missing_retry_2026-07-09/download_retry_summary.md
```

That audit records 25 initially missing INCLUDE PDFs, 22 recovered after all
retry passes, and 3 marked `not_found_after_manual_retry`.

Final outputs:

```text
data/docling_include_final_coverage_2026-07-09/final_docling_manifest.csv
data/docling_include_final_coverage_2026-07-09/final_docling_manifest.json
data/docling_include_final_coverage_2026-07-09/final_docling_coverage_summary.md
```

Docling artifacts are stored under:

```text
data/docling_include_no_vlm_2026-07-09/documents/
data/docling_include_no_vlm_2026-07-09/markdown/
data/docling_include_no_vlm_2026-07-09/chunks/
data/docling_include_no_vlm_2026-07-09/figures/
```

The missing-PDF retry evidence is stored in:

```text
data/full_text_include_missing_retry_2026-07-09/download_retry_summary.md
data/full_text_include_missing_retry_2026-07-09/pass1_existing_downloader/
data/full_text_include_missing_retry_2026-07-09/pass2_direct_pdf_links/
data/full_text_include_missing_retry_2026-07-09/pass3_manual_url_hits/
```

The four failed/missing-artifact conversions are:

```text
full_2026-07-06__rec_001263 — A Suite of Foundation Models Captures the Contextual Interplay Between Codons
full_2026-07-06__rec_001314 — A contextualised protein language model reveals the functional syntax of bacterial evolution
full_2026-07-06__rec_002102 — CellTok: Early-Fusion Multimodal Large Language Model for Single-Cell Transcriptomics via Tokenization
full_2026-07-06__rec_002120 — Extending Protein Language Models to a Viral Genomic Scale Using Biologically Induced Sparse Attention
```

The low-quality successful artifact flagged for manual review is:

```text
full_2026-07-06__rec_001487 — Universal Single-Cell Transcriptomic Aging Clock powered by LLMs reveals targets to slow cellular aging
flags: low_chunk_count; low_markdown_chars; no_figures
```
