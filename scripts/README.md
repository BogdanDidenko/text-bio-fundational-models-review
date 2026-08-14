# Reproducible Systematic Review Search

This script reproduces the literature search for:
**"Generative Foundation Models Bridging Text and Biological Data: A Scoping Review"**

It queries 8 academic databases and produces structured JSON exports for each.

## Setup

```bash
pip install -r requirements.txt
```

## API Keys

Copy the template and fill in your own keys:

```bash
cp api_keys.template.json api_keys.json
```

| Key | Source | Required for |
|---|---|---|
| `ncbi` | https://www.ncbi.nlm.nih.gov/account/settings/ | PubMed |
| `scopus` | https://dev.elsevier.com/ | Scopus |
| `openalex` or `OPENALEX_API_KEY` | https://openalex.org/settings/api | OpenAlex |
| `semantic_scholar` | https://www.semanticscholar.org/product/api#api-key | Semantic Scholar |
| `springernature_Meta_API` | https://dev.springernature.com/ | SpringerNature (Meta) |
| `springernature_Open_Access_API` | https://dev.springernature.com/ | SpringerNature (OA) |
| `serpapi` | https://serpapi.com/google-scholar-api | Provider-mediated Google Scholar capture |

Notes:
- arXiv and EuropePMC (bioRxiv/medRxiv) do not require API keys. Canonical
  Google Scholar capture uses the external SerpAPI provider.
- SpringerNature keys are NOT interchangeable between Meta and OA endpoints.

## Usage

Search all databases:
```bash
python reproduce_search.py --keys api_keys.json
```

Search specific databases:
```bash
python reproduce_search.py --keys api_keys.json --databases pubmed,arxiv,biorxiv_medrxiv
```

Custom output directory:
```bash
python reproduce_search.py --keys api_keys.json --output-dir my_results/
```

Use a provider-mediated, signature-matched Google Scholar capture for an
incremental canonical run:
```bash
python reproduce_search.py --keys api_keys.json \
  --gs-provider-export data/living_catalog_updates/update_YYYY-MM-DD/00_search/google_scholar_provider_export.json
```

For a living update, use the first-class
`run_living_review_pipeline.py scholar-capture` and `scholar-validate`
commands. They build the dated config, invoke the SerpAPI collector, and apply
the signed provider-export validator. The lower-level template and collector
scripts remain available for provider diagnostics.
The legacy `--gs-fallback` option is diagnostic only and is not accepted by the
incremental configuration.

## Output

Results are saved to `output/` (default):
- `pubmed_YYYY-MM-DD.json` — PubMed records
- `scopus_YYYY-MM-DD.json` — Scopus records
- `openalex_YYYY-MM-DD.json` — normalized OpenAlex records
- `openalex_raw_YYYY-MM-DD.json` — native OpenAlex Works records and query membership
- `semantic_scholar_YYYY-MM-DD.json` — Semantic Scholar records
- `arxiv_YYYY-MM-DD.json` — arXiv records
- `biorxiv_medrxiv_YYYY-MM-DD.json` — bioRxiv/medRxiv records
- `springernature_YYYY-MM-DD.json` — SpringerNature validated records
- `springernature_raw_YYYY-MM-DD.json` — SpringerNature raw (before validation)
- `google_scholar_YYYY-MM-DD.json` — Google Scholar records
- `search_summary_YYYY-MM-DD.json` — counts and ground truth validation

## Date Range

All searches cover **2018-01-01 to 2026-02-28**. For databases without month-level date filtering (Scopus, Semantic Scholar), a post-retrieval date filter is applied.

For update searches, use a dated config file instead of editing the baseline
configuration:

```bash
python3 scripts/reproduce_search.py \
  --config scripts/search_config_update_2026-07-06.json \
  --keys api_keys.json \
  --output-dir data/exports_update_2026-07-06
```

The latest completed update search covers **2026-07-07 to 2026-08-09**.

## Living search-to-atlas updates

The earlier top-up scripts are now connected to the complete post-search review
workflow by `run_living_review_pipeline.py`. The runner resumes by stage, logs
commands and hashes, stops at explicit manual gates, classifies newly eligible
papers with the frozen taxonomy, validates source-figure crops, and stages a
rebuilt visual atlas before publication.

Use [`protocol/LIVING_REVIEW_RUNBOOK.md`](../protocol/LIVING_REVIEW_RUNBOOK.md)
as the canonical operator checklist. Begin every update with `doctor`; a run is
not complete until both `verify-live` and the final `doctor` succeed.

```bash
# Check state/snapshot/atlas consistency and obtain the next action.
python3 scripts/run_living_review_pipeline.py doctor

# Show the next interval and all stages without executing them.
python3 scripts/run_living_review_pipeline.py plan --date-to 2026-08-09

# Verify local binaries, API-key names, environments, and baseline artifacts.
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to 2026-08-09
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to 2026-08-09
python3 scripts/run_living_review_pipeline.py preflight --date-to 2026-08-09

# Run or resume the full update; start the local Codex API wrapper as needed.
python3 scripts/run_living_review_pipeline.py run \
  --date-to 2026-08-09 \
  --manage-server

# Publish only after the complete staged run and browser QA succeed.
python3 scripts/run_living_review_pipeline.py publish \
  --run-id update_2026-08-09

# After committing and deploying docs/input-representation-atlas.
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$(git rev-parse HEAD)" --check-assets
```

Missed records discovered before publication enter through
`register-supplemental` and rerun from cumulative deduplication onward. A
prompt/schema change or failed taxonomy acceptance threshold is prepared with
`taxonomy-rerun-preflight`; it refuses partial-cohort execution and writes the
native-Docling regeneration and full rerun commands. Deployment completion and
incidents are stored under `data/living_catalog/releases/`.

The living configuration is `config/living_review_pipeline.json`. Immutable run
artifacts are written under `data/living_catalog_updates/`; the published pointer
is `data/living_catalog/current.json`. Published state keeps an append-only
`prisma_update_history` with the date range and fact-table path for every update. See
[`protocol/living_review_update_pipeline_2026-08-09.md`](../protocol/living_review_update_pipeline_2026-08-09.md)
for the complete evidence and manual-resolution contract. The historical
crosswalk is in
[`analysis/living_review_pipeline_audit_2026-08-09.md`](../analysis/living_review_pipeline_audit_2026-08-09.md).

## Notes

- **SpringerNature** searches broader metadata/full text because title/abstract restriction is premium-only. Mandatory post-retrieval validation labels 3/3 concept-block matches as the primary stratum and retains 2/3 near-misses as a recall stratum; 0/3 and 1/3 records are rejected.
- **Google Scholar** has no official bulk API. Incremental canonical runs require a provider-mediated capture with all configured query pages, raw-response hashes, and a signed query bundle; see `protocol/google_scholar_provider_export_schema.md`. The legacy `scholarly` mode remains diagnostic only. An arbitrary older JSON list is never substituted into a new interval.
- **Semantic Scholar** uses the `/paper/search/bulk` endpoint (not `/paper/search`, which does not support Boolean queries).
- **bioRxiv/medRxiv** are searched via EuropePMC API (the native bioRxiv API does not support content search).

## Expected Results

Results from the original search (2026-02-06). Re-running will produce similar but not identical counts due to ongoing database indexing:

| Database | Records |
|---|---|
| PubMed | ~620 |
| Scopus | ~1,010 |
| Semantic Scholar | ~2,150 |
| arXiv | ~185 |
| bioRxiv/medRxiv | ~670 |
| SpringerNature | ~250 (validated) |
| Google Scholar | ~514 |

Ground truth: 13/13 must-find models detected across all databases (after the
2026-04-14 update search added Cell2Seq and X-Cell to the original 11). See
[`protocol/ground_truth_models.md`](../protocol/ground_truth_models.md) for
the full list and per-model expected criterion labels.

## Update Search Runs

| Search date | Date range | Raw records | Internal dedup | New after master cross-dedup | Screening-ready | Notes |
|---|---|---:|---:|---:|---:|---|
| 2026-04-14 | 2026-03-01 to 2026-04-14 | 867 | 762 | 668 | 668 | Google Scholar rate-limited after query 5/7. |
| 2026-06-10 | 2026-04-15 to 2026-06-10 | 933 | 785 | 447 | 431 | CrossRef audit removed 2 hidden duplicates and enriched 126 DOIs. |
| 2026-07-06 | 2026-06-11 to 2026-07-06 | 197 | 155 | 134 | 119 | Google Scholar returned 0 due full rate-limit; CrossRef audit found no hidden duplicates. |
| 2026-08-09 | 2026-07-07 to 2026-08-09 | 639 | 514 | 285 | 285 | Eight complete sources; one-query Scholar capture returned 252 records; Crossref audit removed 2 hidden duplicates. |

## Search Configuration

All queries are stored in `search_config.json`. The file contains the exact Boolean queries, filters, and validation patterns used in the review. Do not modify unless intentionally changing the search strategy.

## Pilot Screening With LatteReview

The main screening-related scripts are:

- `screen_test.py`
  - **deprecated** v0.1 one-shot INCLUDE/EXCLUDE/UNCERTAIN classifier
  - retained as historical reference only
  - does NOT implement the current criterion-by-criterion workflow
- `run_lattereview_pilot.py`
  - older OpenRouter-oriented pilot
  - useful as historical reference
- `run_lattereview_guideline_pilot.py`
  - current literature-aligned runner
  - uses the criterion-by-criterion workflow documented in `protocol/`
  - intended to run against an already served OpenAI-compatible endpoint such as vLLM
- `compare_screening_replicates.py`
  - compares two completed runs and reports decision drift
- `build_prompt_regression_set.py`
  - builds a compact regression CSV from benchmark, stable, and unstable cases

### Minimal setup for the current runner

```bash
bash scripts/setup_lattereview_runtime.sh
```

This clones `LatteReview` into `external/LatteReview` and installs the minimal
Python dependencies listed in `requirements_lattereview_pilot.txt`.

### Run the current guideline-aligned pipeline

```bash
python3 scripts/run_lattereview_guideline_pilot.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model qwen3-30b-a3b \
  --input-csv /path/to/input.csv \
  --output-dir /path/to/output_dir
```

Expected input:

- CSV with at least `title` and `abstract` columns
- template: `data/screening_input_template.csv`

Optional:

- `--lattereview-path /path/to/LatteReview` if you do not want to use the default `external/LatteReview`
- `--prompt-dir /path/to/protocol/screening_prompt_templates`
- `--max-records N`
- `--max-concurrent N`

### Compare repeated screening runs

Use `compare_screening_replicates.py` after two full runs to quantify
nondeterministic decision drift and export mismatch cases for prompt audit:

```bash
python3 scripts/compare_screening_replicates.py \
  --run-a runs/first_full_run \
  --run-b runs/second_full_run \
  --output-dir runs/second_full_run/repeatability_audit
```

Use `build_prompt_regression_set.py` to build a compact CSV of benchmark,
stable-include, and unstable decision cases for targeted prompt regression
checks:

```bash
python3 scripts/build_prompt_regression_set.py \
  --run-a runs/first_full_run \
  --run-b runs/second_full_run \
  --compare-dir runs/second_full_run/repeatability_audit
```
