# Reproducible Systematic Review Search

This script reproduces the literature search for:
**"Generative Foundation Models Bridging Text and Biological Data: A Scoping Review"**

It queries 7 academic databases and produces structured JSON exports for each.

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
| `semantic_scholar` | https://www.semanticscholar.org/product/api#api-key | Semantic Scholar |
| `springernature_Meta_API` | https://dev.springernature.com/ | SpringerNature (Meta) |
| `springernature_Open_Access_API` | https://dev.springernature.com/ | SpringerNature (OA) |

Notes:
- arXiv, EuropePMC (bioRxiv/medRxiv), and Google Scholar do not require API keys.
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

Use cached Google Scholar results (recommended — see note below):
```bash
python reproduce_search.py --keys api_keys.json \
  --gs-fallback data/exports/google_scholar_2026-02-06.json
```

## Output

Results are saved to `output/` (default):
- `pubmed_YYYY-MM-DD.json` — PubMed records
- `scopus_YYYY-MM-DD.json` — Scopus records
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

The latest completed update search covers **2026-06-11 to 2026-07-06**.

## Notes

- **SpringerNature** searches full-text body (title/abstract restriction is premium-only). A mandatory post-retrieval validation step filters records to those matching all 3 concept blocks in the title or abstract. Expect ~98% noise removal.
- **Google Scholar** has no official API. This script uses the `scholarly` Python library, which scrapes Google Scholar and is aggressively rate-limited (typically after ~4 queries). Use `--gs-fallback` to provide the original search results file. When the live search returns fewer results than the fallback, the cached results are used automatically. The original results from the review search are included at `data/exports/google_scholar_2026-02-06.json`.
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
