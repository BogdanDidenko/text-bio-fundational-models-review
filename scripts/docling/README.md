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
