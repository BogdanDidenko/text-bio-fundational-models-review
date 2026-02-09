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

Ground truth: 11/11 must-find models detected across all databases.

## Search Configuration

All queries are stored in `search_config.json`. The file contains the exact Boolean queries, filters, and validation patterns used in the review. Do not modify unless intentionally changing the search strategy.
