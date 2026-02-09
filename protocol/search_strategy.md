# Search Strategy

## Review Question
What foundation-model-style approaches exist for multi-modal single-cell data, and what modalities, objectives, and evaluation tasks do they cover?

## Core Concept Blocks

### Block A — Single-cell domain
"single cell" OR "single-cell" OR scRNA-seq OR "single cell RNA-seq" OR scATAC-seq OR "single-cell multi-omics" OR "single-cell multiomics" OR "single-cell multimodal" OR multiome OR "CITE-seq" OR "REAP-seq" OR "spatial transcriptomics"

### Block B — Multi-modal / multi-omics integration
multimodal OR "multi-modal" OR "multi-omic" OR multiomics OR integrative OR "cross-modal" OR "cross-modality" OR "multi-omics integration" OR "modality alignment"

### Block C — Foundation model / deep learning
"foundation model" OR "pretrained model" OR "pre-trained model" OR "self-supervised" OR "contrastive learning" OR transformer OR "large language model" OR LLM OR "masked modeling" OR "representation learning" OR "generative model" OR "attention mechanism" OR "deep generative"

## Query Structure
`(Block A) AND (Block B) AND (Block C)`

## Filters (applied per-database)
- **Date range**: 2018-01-01 to 2026-12-31
- **Language**: English
- **Access**: Open Access only
- **Document types**: Articles + Conference papers + Preprints

## Databases (7 total)

| # | Database | Interface | Query File |
|---|----------|-----------|------------|
| 1 | PubMed | NCBI Entrez API | `queries/pubmed.txt` |
| 2 | Scopus | Elsevier API | `queries/scopus.txt` |
| 3 | SpringerNature | Meta API v2 + OA API | `queries/springernature.txt` |
| 4 | arXiv | paper-search-mcp | `queries/arxiv.txt` |
| 5 | bioRxiv / medRxiv | paper-search-mcp | `queries/biorxiv_medrxiv.txt` |
| 6 | Google Scholar | paper-search-mcp | `queries/google_scholar.txt` |
| 7 | Semantic Scholar | S2 Graph API | `queries/semantic_scholar.txt` |

## Changes from Initial Draft (v2, 2026-02-03)
- Added "spatial transcriptomics" to Block A
- Added "multi-omics integration", "modality alignment" to Block B
- Added "attention mechanism", "deep generative" to Block C
- Created SpringerNature query (new database)
- Created arXiv, bioRxiv/medRxiv, Semantic Scholar query files
- Removed Web of Science (no API access)
- Added OA, language, and document type filters

See `protocol/queries/` for database-specific query strings.
