# PRISMA-S Protocol: Generative Foundation Models Bridging Text and Biological Data

**Version**: 3.0
**Date**: 2026-02-06
**Type**: Scoping review with PRISMA-S compliant search methodology

---

## 1. Review Question

What generative foundation models exist that combine text modality (natural language or gene tokens) with biological data modalities, and how do they bridge language and biology?

## 2. Objectives

1. Identify foundation models that combine text/language with biological data (omics, expression, genomics)
2. Summarize model architectures, text integration strategies, and supported biological modalities
3. Compare datasets, downstream tasks, and evaluation metrics across models
4. Map the landscape of text+biology generative FM methods (2018-2026)

## 3. Registration

Protocol prepared according to PRISMA 2020 and PRISMA-S (search extension) guidelines. Not pre-registered.

---

## 4. Eligibility Criteria

See [eligibility_criteria.md](eligibility_criteria.md) for full criteria.

**Summary**:
- **Include**: Text modality (NL or gene tokens) + biological data modality + generative architecture + FM characteristics + OA + English + 2018-2026
- **Exclude**: No bio data, no text component, encoder-only architecture, no FM component, reviews, non-scholarly

---

## 5. Information Sources

### 5.1 Databases (7)

| # | Database | Interface | Type |
|---|----------|-----------|------|
| 1 | PubMed / MEDLINE | NCBI Entrez E-utilities API | Direct API |
| 2 | Scopus | Elsevier API | Direct API |
| 3 | SpringerNature | Meta API v2 + Open Access API | Direct API |
| 4 | Semantic Scholar | S2 Academic Graph API (bulk search) | Direct API |
| 5 | arXiv | arXiv API | Direct API |
| 6 | bioRxiv / medRxiv | EuropePMC REST API | Direct API |
| 7 | Google Scholar | paper-search-mcp | Supplementary |

### 5.2 Justification
- **PubMed**: Primary biomedical database, strong coverage of computational biology
- **Scopus**: Broadest multidisciplinary coverage, includes conference proceedings
- **SpringerNature**: Covers Nature journals (Nature Methods, Nature Biotechnology), provides JATS full-text for OA articles
- **Semantic Scholar**: AI/ML focused, good preprint coverage, citation graph; bulk search supports Boolean
- **arXiv**: Primary preprint server for ML/AI methods
- **bioRxiv/medRxiv**: Primary preprint servers for biology/medicine; searched via EuropePMC (full Boolean)
- **Google Scholar**: Supplementary — broadest coverage, used for validation

### 5.3 Grey Literature
- Preprints from arXiv, bioRxiv, medRxiv included as primary sources
- Conference papers (NeurIPS, ICML, ICLR, RECOMB, ISMB) captured via Scopus, Semantic Scholar, and Google Scholar

---

## 6. Search Strategy

### 6.1 Concept Blocks

Three concept blocks combined with AND:

| Block | Concept | Terms |
|-------|---------|-------|
| A | Biological data | "single cell", "single-cell", scRNA-seq, "RNA-seq", "gene expression", scATAC-seq, "ATAC-seq", "chromatin accessibility", CITE-seq, "spatial transcriptomics", "multi-omics", multiomics, transcriptomics, genomics, proteomics, epigenomics, "cell type", "gene regulatory" |
| B | Text / language | "language model", LLM, "large language model", "natural language", GPT, CLIP, "cross-modal", multimodal, "multi-modal", tokeniz*, "gene token", prompt, chat, "text generation", "cell-to-text", "text-to-cell", NLP |
| C | FM + generativity | "foundation model", pretrain*, "pre-train*", "self-supervised", transformer, generative, decoder, autoregressive, "transfer learning", "zero-shot", "few-shot", "masked modeling", "attention mechanism", "deep learning" |

### 6.2 Query Adaptation

Each database receives an adapted query following its syntax rules:
- **Full Boolean** (PubMed, Scopus, SpringerNature, EuropePMC): Direct translation with field tags
- **Boolean bulk** (Semantic Scholar): Translated using `+`/`|`/`-` operators on `/paper/search/bulk`
- **Moderate simplification** (arXiv): Reduced operators with `ti:`/`abs:` field prefixes, category filter
- **Extreme simplification** (Google Scholar): Shortest form + supplementary model name searches

All query files: [protocol/queries/](queries/)

### 6.3 Filters Applied

| Filter | Value | Databases |
|--------|-------|-----------|
| Date range | 2018-01-01 to 2026-12-31 | All |
| Language | English | PubMed, Scopus |
| Open Access | OA only | PubMed, Scopus, SpringerNature (OA API), S2 (openAccessPdf) |
| Document type | Articles + Conference papers | Scopus |

### 6.4 Search Dates

All searches to be executed on the same date. Date will be recorded in the PRISMA-S search log.

---

## 7. Study Selection

### 7.1 Process

1. **Import**: Export results from all 7 databases to `data/exports/<database>_<date>.json`
2. **Deduplication**: Match by DOI (primary), then fuzzy title+author matching
3. **Title/Abstract screening**: Apply eligibility criteria decision tree (see [eligibility_criteria.md](eligibility_criteria.md))
4. **Full-text screening**: For records passing title/abstract screen, verify all inclusion criteria on full text
5. **Conflict resolution**: Disagreements resolved by discussion (single reviewer with documented rationale)

### 7.2 Exclusion Codes

| Code | Reason |
|------|--------|
| EC1 | No biological data modality |
| EC2 | No text/language component |
| EC3 | Encoder-only architecture (note in supplementary) |
| EC4 | No foundation model component |
| EC5 | Non-computational |
| EC6 | Non-scholarly source |
| EC7 | Review article |
| EC8 | Duplicate publication |
| EC9 | Not English |
| EC10 | Not Open Access |

---

## 8. Data Extraction

See [data_extraction.md](data_extraction.md) for extraction template.

**Key fields**:
- Bibliographic (title, authors, year, venue, DOI)
- Biological modalities supported
- Text integration strategy (NL, gene tokens, tokenizer, embeddings)
- Architecture type (decoder, encoder-decoder, CLIP, etc.)
- Pretraining objective and dataset
- Downstream tasks and evaluation metrics
- Code/data availability

---

## 9. PRISMA-S Search Log

To be populated after search execution:

| Database | Interface | Date | Query (ref) | Filters | Results | Notes |
|----------|-----------|------|-------------|---------|---------|-------|
| PubMed | Entrez API | TBD | queries/pubmed.txt | OA, EN, 2018-2026 | TBD | |
| Scopus | Elsevier API | TBD | queries/scopus.txt | OA, EN, 2018-2026, AR+CP | TBD | |
| SpringerNature | Meta API v2 | TBD | queries/springernature.txt | 2018-2026 | TBD | |
| SpringerNature | OA API | TBD | queries/springernature.txt | 2018-2026, OA only | TBD | |
| arXiv | arXiv API | TBD | queries/arxiv.txt | 2018-2026 | TBD | Inherently OA |
| bioRxiv/medRxiv | EuropePMC API | TBD | queries/biorxiv_medrxiv.txt | 2018-2026, SRC:PPR | TBD | Inherently OA |
| Google Scholar | paper-search-mcp | TBD | queries/google_scholar.txt | 2018-2026 | TBD | Supplementary |
| Semantic Scholar | S2 Bulk API | TBD | queries/semantic_scholar.txt | 2018-2026, OA | TBD | |

---

## 10. PRISMA Flow Diagram

See [prisma_flow_template.md](prisma_flow_template.md) — to be populated after screening.

---

## 11. Validation

### Ground Truth Models (from existing reviews + known models)

Models our search MUST capture:
- scGPT (gene tokens + RNA + ATAC + CITE-seq, generative)
- tGPT (gene tokens + RNA, decoder-only)
- LangCell (NL + scRNA)
- ChatCell (NL + scRNA, generative chat)
- CellWhisperer (NL + scRNA)
- CellPLM (gene tokens + spatial, encoder-decoder)
- Nicheformer (gene tokens + spatial, encoder-decoder)
- EpiAgent (LLM agent + epigenomics)
- PathOmCLIP (text + omics via CLIP)

Related but excluded (encoder-only, for supplementary):
- scBERT, Geneformer, scFoundation, UCE, GeneCompass, SCimilarity

See [data/existing_reviews_compilation.md](../data/existing_reviews_compilation.md) for full ground truth list.

---

## 12. Review of Reviews (Step 0 — completed)

| Review | Journal | Year | Models Found | Method |
|--------|---------|------|-------------|--------|
| Baek et al. | Exp Mol Med | 2025 | 13 scFMs (Table 1) | Narrative |
| Yiu et al. | J Transl Med | 2025 | 43 models (141 papers) | Systematic (PRISMA) |
| Szalata et al. | Nature Methods | 2024 | N/A (not OA) | Narrative |

**Key findings**: Most existing reviews focus on single-modality scFMs. Our review addresses the gap by focusing on models that bridge text/language and biological data.

---

## 13. Amendments

| Date | Version | Change |
|------|---------|--------|
| 2026-01-28 | 1.0 | Initial draft |
| 2026-02-03 | 2.0 | Finalized criteria, added SpringerNature, created all query files, completed review of reviews |
| 2026-02-06 | 3.0 | Scope change: from "multi-modal single-cell FMs" to "generative FMs bridging text and biological data". Rewrote eligibility criteria (IC1-IC4, EC1-EC4), concept blocks, all query files. Updated search interfaces: S2 bulk search, EuropePMC for bioRxiv/medRxiv. |
