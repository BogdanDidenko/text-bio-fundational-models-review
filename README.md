# Generative Foundation Models Bridging Text and Biological Data: A Scoping Review

Reproducible PRISMA-ScR literature review on generative foundation models that combine **text** (natural language or gene tokens) with **biological data** (any omics modality).

## Current Status

| Step | Status | Details |
|------|--------|---------|
| 0. Review of reviews | Done | `data/existing_reviews_compilation.md` |
| 1. Protocol | Done | `protocol/PRISMA_protocol.md`, `protocol/eligibility_criteria.md` |
| 2. Search queries (v3.1) | Done | `protocol/queries/`, `scripts/search_config.json` |
| 3. Search execution | Done | 7 databases, 2 rounds |
| 4. Deduplication | Done | `scripts/deduplicate.py` |
| 5. Abstract enrichment | Done | `scripts/enrich_abstracts.py` |
| 6. Title/Abstract screening | **Next** | 4,027 records |

## Search Results

### v3.1 (2026-02-15) — initial search
- Date range: 2018-01-01 to 2026-02-28
- PubMed: 631, Scopus: 1,021, S2: 2,192, arXiv: 187, bioRxiv: 669, SN: 272, GS: 562
- Total: 5,534 → 3,555 unique (dedup) → 3,371 for screening (after enrichment + exclusion)

### Update (2026-04-14) — new publications
- Date range: 2026-03-01 to 2026-04-14
- PubMed: 46, Scopus: 32, S2: 201, arXiv: 14, bioRxiv: 5, SN: 33, GS: 536
- Total: 867 → 762 unique (internal dedup) → 668 new (cross-dedup with v3.1)
- Abstract enrichment: 29/41 enriched, 12 excluded
- **Combined: 3,371 + 668 − 12 = 4,027 records for screening**

## Repo Structure

```
protocol/           PRISMA protocol, eligibility criteria, search strategy
protocol/queries/   Database-specific search strings
scripts/
  reproduce_search.py       Reproducible search across 7 databases
  search_config.json        v3.1 search configuration
  search_config_update.json Update search configuration (Mar-Apr 2026)
  deduplicate.py            Conservative exact-match deduplication
  enrich_abstracts.py       Abstract enrichment via S2/CrossRef/PubMed APIs
data/
  deduplicated_records.json Master record set (4,027 records with abstracts)
  excluded_no_abstract.json Records excluded for missing abstracts
  exports/                  v3.0 database exports (2026-02-06)
  exports_v31/              v3.1 database exports (2026-02-15)
  exports_update/           Update exports (2026-04-14)
```

## Databases

| Database | API | Notes |
|----------|-----|-------|
| PubMed | NCBI Entrez | `[Title/Abstract]` field tags, `free full text[sb]` |
| Scopus | Elsevier Search API | `OPENACCESS(1)`, post-filter by date |
| Semantic Scholar | `/paper/search/bulk` | Boolean support, year filter |
| arXiv | arXiv API | Category filter, multi-query merge |
| bioRxiv/medRxiv | EuropePMC (`SRC:PPR`) | Full Boolean |
| SpringerNature | Meta + OA APIs | Full-text search → mandatory post-retrieval validation |
| Google Scholar | `scholarly` library | Rate-limited, supplementary source |

## Ground Truth Models

Must-find (11): scGPT, tGPT, LangCell, ChatCell, CellWhisperer, CellPLM, Nicheformer, EpiAgent, GenePT, GeneGPT, PathOmCLIP

All 11 found across combined databases in v3.1.

## Reproducibility

```bash
pip install requests scholarly
# Copy api_keys.template.json → api_keys.json and fill in your keys
python scripts/reproduce_search.py --keys api_keys.json --output-dir results/
python scripts/deduplicate.py --exports-dir results/
python scripts/enrich_abstracts.py --keys api_keys.json
```
