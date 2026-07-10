# PRISMA-S Protocol: Generative Foundation Models Bridging Text and Biological Data

**Version**: 4.4
**Date**: 2026-07-10
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
5. **Targeted full-text evidence screening**: For records with converted full text, use Docling Graph provenance to reconstruct complete `data_source` and `input_representation` sections. Screen the title, abstract, and those selected sections; do not render the whole document into the reviewer prompt. The executed 2026-07-10 method and audit trail are in [full_text_section_screening_2026-07-10.md](full_text_section_screening_2026-07-10.md).
6. **Conflict resolution**: Conflicts and unresolved criterion outputs between the role-separated scope and architecture passes escalate to an adjudicator round; unresolved cases remain in the manual review queue. These are different prompt roles executed by the same model, not independent human reviewers.
7. **Manual resolution layer**: A review lead inspects the relevant full Docling sections only for records still `UNCERTAIN` after adjudication. Each confirmed decision is appended as a stable record-level mapping that preserves the original automated decision, cited evidence section, rationale, and exclusion code where relevant; it does not overwrite prompts, raw responses, or automated outputs. The executed 2026-07-10 layer resolved 6 records to 2 INCLUDE and 4 EXCLUDE.

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
| 2026-06-10 | 4.1 | Top-up search 2026-04-15 → 2026-06-10 across all 7 DBs using the v3.1 query strategy with only date filters changed. Results: 933 raw records → 785 internally deduplicated → 447 new after cross-dedup against the 4,027-record master. CrossRef audit removed 2 hidden duplicates and enriched 126 screening-ready records with DOIs, leaving 431 records for Codex screening. |
| 2026-07-06 | 4.2 | Top-up search 2026-06-11 → 2026-07-06 across the same 7 DBs using `scripts/search_config_update_2026-07-06.json`. Results: 197 raw records → 155 internally deduplicated → 134 new after cross-dedup against the 4,027-record master. CrossRef audit found no hidden duplicates or DOI enrichments. Final screening-ready set contains 119 records; Google Scholar returned 0 because the automated `scholarly` run was fully rate-limited. |
| 2026-07-10 | 4.3 | Added the executed targeted full-text section screening method. Docling Graph processed 235 full-text records; 221 had valid dual-section evidence and entered the corrected second-stage screening payload. Final automated decisions: 50 INCLUDE, 165 EXCLUDE, 6 UNCERTAIN; 67 records were adjudicated. Full provenance, prompt, output, and decision audit is in `protocol/full_text_section_screening_2026-07-10.md`. |
| 2026-07-10 | 4.4 | Added an append-only human-confirmed manual-resolution layer for the six automated-UNCERTAIN full-text records. The review lead inspected the cited full Docling sections and confirmed 2 INCLUDE and 4 EXCLUDE decisions. The automated `50 / 165 / 6` output remains immutable; the current eligibility checkpoint for the 221 entered records is `52 INCLUDE / 169 EXCLUDE / 0 UNCERTAIN`. |
