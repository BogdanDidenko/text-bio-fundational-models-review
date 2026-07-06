# PRISMA-S Protocol: Generative Foundation Models Bridging Text and Biological Data

**Version**: 4.2
**Date**: 2026-07-07
**Type**: Scoping review (PRISMA-ScR) with PRISMA-S compliant search methodology and PRISMA-trAIce-style LLM screening

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
| 7 | Google Scholar | `scholarly` Python library | Supplementary |

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
2. **Deduplication**: Conservative exact matching only — DOI → PMID → arXiv ID → normalized title (no fuzzy matching). See [scripts/deduplicate.py](../scripts/deduplicate.py).
3. **Abstract enrichment + exclusion**: Records without abstracts are enriched via S2/CrossRef/PubMed APIs; records still lacking an abstract are excluded.
4. **Title/Abstract screening**: Apply eligibility criteria decision tree (see [eligibility_criteria.md](eligibility_criteria.md)) using a criterion-by-criterion LatteReview workflow (see [llm_screening_system_guideline.md](llm_screening_system_guideline.md), [lattereview_screening_architecture.md](lattereview_screening_architecture.md)).
5. **Full-text screening**: For records passing title/abstract screen, verify all inclusion criteria on full text.
6. **Conflict resolution**: Disagreements between scope and architecture reviewers escalate to an adjudicator round; unresolved cases go to manual review queue.

### 7.2 Exclusion Codes

The protocol uses 8 high-level exclusion codes (EC1–EC8). The runtime LLM
screening codebook in `protocol/screening_prompt_templates/` further refines
these into specific values such as `EC2_no_text_component`,
`EC2_no_substantive_text_bio_bridge`, `EC3_not_generative`, and
`EC4_no_foundation_model_evidence`.

| Code | Reason |
|------|--------|
| EC1 | No biological data modality |
| EC2 | No text/language component (or no substantive text-bio bridge) |
| EC3 | Encoder-only architecture (note in supplementary) |
| EC4 | No foundation model component |
| EC5 | Non-computational |
| EC6 | Non-scholarly source |
| EC7 | Review article |
| EC8 | Duplicate publication |

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

## 9. PRISMA-S Search and Screening Log

The current PRISMA-S search, deduplication, and Codex title/abstract screening
log is maintained in
[prisma_search_screening_log_2026-07-07.md](prisma_search_screening_log_2026-07-07.md).

Current cumulative status:

| Stage | Count | Notes |
|---|---:|---|
| Raw database records identified | 7,531 | v3.1 baseline plus 2026-04-14, 2026-06-10, and 2026-07-06 top-up searches |
| Unique records before no-abstract exclusions | 4,618 | After within-window deduplication, cross-corpus deduplication, and Crossref hidden-duplicate audit |
| No-abstract records excluded before title/abstract screening | 41 | 12 in the pre-June master corpus, 14 in the June top-up, 15 in the July top-up |
| Records screened by Codex title/abstract pipeline | 4,577 | 4,027 full rerun + 431 June update + 119 July update |
| Title/abstract EXCLUDE | 4,327 | Codex final `EXCLUDE` |
| Title/abstract UNCERTAIN | 95 | Manual/full-text eligibility queue |
| Title/abstract provisional INCLUDE | 155 | Requires full-text confirmation |

Exact query strings and database-specific update configs are preserved in:

- [queries/](queries/)
- `analysis/codex_screening_run_artifacts_20260706/search_configs/search_config_update_2026-06-10.json`
- `analysis/codex_screening_run_artifacts_20260706/search_configs/search_config_update_2026-07-06.json`

Codex screening artifacts and per-record role logs are preserved in:

- `analysis/codex_screening_run_artifacts_20260706/full_runs/codex_gpt54mini_all4027_20260706/`
- `analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update431_20260610/`
- `analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update155_20260706/`

---

## 10. PRISMA Flow Diagram

See [prisma_flow_template.md](prisma_flow_template.md) for the current
title/abstract-stage PRISMA flow. Full-text eligibility and final qualitative
synthesis counts remain pending.

---

## 11. Validation

### Ground Truth Models (from existing reviews + known models)

Must-include (13): scGPT, tGPT, LangCell, ChatCell, CellWhisperer, CellPLM,
Nicheformer, EpiAgent, GenePT, GeneGPT, PathOmCLIP, Cell2Seq, X-Cell.

Related but excluded (4, encoder-only, for supplementary table):
scBERT, Geneformer, scFoundation, UCE.

All 13 must-find models were captured by the combined v3.1 + 2026-04-14 update
search. See [ground_truth_models.md](ground_truth_models.md) for per-model
metadata and per-group expected criterion-level labels used as the recall
anchor for the LLM screening benchmark.

See [data/existing_reviews_compilation.md](../data/existing_reviews_compilation.md) for the original ground truth compilation from existing reviews.

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
| 2026-02-15 | 3.1 | Added space variants `RNA seq` and `multi omics` to all 7 queries; rerun search. 5,534 → 3,371 records for screening. |
| 2026-04-14 | 3.2 | Top-up search 2026-03-01 → 2026-04-14 across all 7 DBs; 668 truly new records after cross-dedup; added Cell2Seq and X-Cell to ground truth (13 must-find total); short-abstract enrichment via CrossRef title search. 4,027 records for screening. |
| 2026-04-25 | 4.0 | Adopted criterion-by-criterion LatteReview screening workflow (BMC + PRISMA-trAIce + Cochrane). Three reviewer roles: scope, architecture, adjudicator. Final decision derived in Python gate logic, not emitted by the LLM. Deprecated v0.1 one-shot screening script. Aligned exclusion codebook (EC1–EC8 high-level → runtime codebook with refined codes). |
| 2026-06-10 | 4.1 | Top-up search 2026-04-15 → 2026-06-10 across all 7 DBs; 933 raw records, 785 update-unique after within-window deduplication, 445 truly new after cross-corpus deduplication and Crossref audit, 431 screening-ready records. Codex `gpt-5.4-mini` screened 431 records: 409 EXCLUDE, 7 UNCERTAIN, 15 INCLUDE. |
| 2026-07-07 | 4.2 | Added PRISMA-S search/screening log covering all current windows and Codex audit artifacts. July top-up search 2026-06-11 → 2026-07-06 found 197 raw records, 155 update-unique records, 134 truly new after cross-corpus deduplication/Crossref audit, and 119 screening-ready records. Codex `gpt-5.4-mini` screened 119 records: 113 EXCLUDE, 0 UNCERTAIN, 6 INCLUDE. Full pre-June 4,027-record corpus was rerun with the same Codex pipeline: 3,805 EXCLUDE, 88 UNCERTAIN, 134 INCLUDE. |
