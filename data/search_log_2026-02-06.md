# PRISMA-S Search Log

**Review Title**: Generative Foundation Models Bridging Text and Biological Data: A Scoping Review
**Search Date**: 2026-02-06
**Searcher**: Automated via API (Claude Code)
**Protocol Version**: v3.0

---

## Concept Blocks (A AND B AND C)

**Block A — Biological data**:
`"single-cell" | "single cell" | scRNA-seq | "RNA-seq" | "gene expression" | scATAC-seq | "ATAC-seq" | "chromatin accessibility" | CITE-seq | "spatial transcriptomics" | "multi-omics" | multiomics | transcriptomics | genomics | proteomics | epigenomics | "cell type" | "gene regulatory"`

**Block B — Text / language**:
`"language model" | LLM | "large language model" | "natural language" | GPT | CLIP | "cross-modal" | multimodal | "multi-modal" | tokenization | "gene token" | prompt | "text generation" | "cell-to-text" | "text-to-cell" | NLP`

**Block C — FM + generativity**:
`"foundation model" | pretrained | "pre-trained" | "self-supervised" | transformer | generative | decoder | autoregressive | "transfer learning" | "zero-shot" | "few-shot" | "masked modeling" | "attention mechanism" | "deep learning"`

**Date range**: 2018-01-01 to 2026-12-31

---

## 1. PubMed (MEDLINE via Entrez E-utilities)

**Interface**: NCBI Entrez E-utilities API (esearch + efetch)
**Search fields**: Title/Abstract `[Title/Abstract]`
**Date filter**: `"2018/01/01"[Date - Publication] : "2026/12/31"[Date - Publication]`
**Access filter**: `"free full text"[sb]`
**Language filter**: `English[Language]`

**Exact query**:
```
(("single cell"[Title/Abstract] OR "single-cell"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR "RNA-seq"[Title/Abstract] OR "gene expression"[Title/Abstract] OR scATAC-seq[Title/Abstract] OR "ATAC-seq"[Title/Abstract] OR "chromatin accessibility"[Title/Abstract] OR CITE-seq[Title/Abstract] OR "spatial transcriptomics"[Title/Abstract] OR "multi-omics"[Title/Abstract] OR multiomics[Title/Abstract] OR transcriptomics[Title/Abstract] OR genomics[Title/Abstract] OR proteomics[Title/Abstract] OR epigenomics[Title/Abstract] OR "cell type"[Title/Abstract] OR "gene regulatory"[Title/Abstract])
AND ("language model"[Title/Abstract] OR LLM[Title/Abstract] OR "large language model"[Title/Abstract] OR "natural language"[Title/Abstract] OR GPT[Title/Abstract] OR CLIP[Title/Abstract] OR "cross-modal"[Title/Abstract] OR multimodal[Title/Abstract] OR "multi-modal"[Title/Abstract] OR tokenization[Title/Abstract] OR "gene token"[Title/Abstract] OR prompt[Title/Abstract] OR "text generation"[Title/Abstract] OR "cell-to-text"[Title/Abstract] OR "text-to-cell"[Title/Abstract] OR NLP[Title/Abstract])
AND ("foundation model"[Title/Abstract] OR pretrained[Title/Abstract] OR "pre-trained"[Title/Abstract] OR "self-supervised"[Title/Abstract] OR transformer[Title/Abstract] OR generative[Title/Abstract] OR decoder[Title/Abstract] OR autoregressive[Title/Abstract] OR "transfer learning"[Title/Abstract] OR "zero-shot"[Title/Abstract] OR "few-shot"[Title/Abstract] OR "masked modeling"[Title/Abstract] OR "attention mechanism"[Title/Abstract] OR "deep learning"[Title/Abstract]))
AND ("2018/01/01"[Date - Publication] : "2026/12/31"[Date - Publication])
AND "free full text"[sb]
AND English[Language]
```

**Results**: 619
**Records retrieved**: 619
**Export file**: `data/exports/pubmed_2026-02-06.json`
**Notes**: `"open access"[filter]` does not work via Entrez API (returns 0); used `"free full text"[sb]` instead (619 results). Without OA filter: 787 results.

---

## 2. Scopus (Elsevier Scopus API)

**Interface**: Elsevier Scopus Search API v2
**Search fields**: TITLE-ABS-KEY (title, abstract, keywords)
**Date filter**: `PUBYEAR > 2017`
**Language filter**: `LANGUAGE(English)`
**Access filter**: none applied (OA status captured in metadata)

**Exact query**:
```
TITLE-ABS-KEY(
  ("single cell" OR "single-cell" OR scRNA-seq OR "RNA-seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory")
  AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR "cell-to-text" OR "text-to-cell" OR NLP)
  AND ("foundation model" OR pretrain* OR "pre-train*" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")
) AND PUBYEAR > 2017 AND LANGUAGE(English)
```

**Results**: 1,014
**Records retrieved**: 1,014
**Export file**: `data/exports/scopus_2026-02-06.json`
**Notes**: Scopus supports wildcards (`tokeniz*`, `pretrain*`). No OA filter applied at query level to maximize recall.

---

## 3. Semantic Scholar (Bulk Search API)

**Interface**: Semantic Scholar Academic Graph API — `/paper/search/bulk`
**Boolean syntax**: `+` (AND), `|` (OR), `-` (NOT)
**Year filter**: `year=2018-2026`
**Fields**: title, abstract, authors, year, venue, externalIds, citationCount, fieldsOfStudy, publicationTypes, openAccessPdf, publicationDate

**Exact query (main)**:
```
("single-cell" | "single cell" | "scRNA-seq" | "RNA-seq" | "gene expression" | transcriptomics | genomics | proteomics | epigenomics | "spatial transcriptomics" | "multi-omics") + ("language model" | LLM | "large language model" | "natural language" | GPT | CLIP | multimodal | "multi-modal" | "cross-modal" | tokeniz* | prompt | NLP | "text generation") + ("foundation model" | pretrain* | "self-supervised" | transformer | generative | decoder | autoregressive | "transfer learning" | "zero-shot" | "deep learning")
```

**Supplementary queries**:
1. Model names: `(scGPT | tGPT | LangCell | ChatCell | CellWhisperer | GenePT | GeneGPT | CellPLM | Nicheformer | EpiAgent | PathOmCLIP)`
2. Cell + language: `("cell" + "language model") | ("gene" + "GPT") | ("single-cell" + "LLM") | ("biological" + "language model")`

**Results**: 2,070 (main) + supplementary
**Records retrieved**: 2,069 unique
**Export file**: `data/exports/semantic_scholar_2026-02-06.json`
**Notes**: Used `/paper/search/bulk` endpoint (not `/paper/search`, which doesn't support Boolean). Pagination via continuation tokens. 1 record lost due to deduplication.

---

## 4. arXiv (arXiv API)

**Interface**: arXiv API (http://export.arxiv.org/api/query)
**Search fields**: `ti:` (title), `abs:` (abstract)
**Category filter**: `cat:cs.LG OR cat:cs.AI OR cat:cs.CL OR cat:q-bio.GN OR cat:q-bio.QM OR cat:stat.ML`

**Sub-queries executed**:

### 4a. Primary (broad)
```
(ti:"single cell" OR ti:scRNA OR ti:"gene expression" OR ti:transcriptomics OR ti:genomics OR abs:"single-cell" OR abs:"RNA-seq" OR abs:"spatial transcriptomics" OR abs:"multi-omics")
AND (ti:"language model" OR ti:GPT OR ti:LLM OR ti:CLIP OR ti:multimodal OR abs:"language model" OR abs:"large language model" OR abs:"natural language" OR abs:"cross-modal" OR abs:"multi-modal" OR abs:tokeniz OR abs:prompt)
AND (abs:"foundation model" OR abs:pretrain OR abs:"self-supervised" OR abs:transformer OR abs:generative OR abs:decoder OR abs:autoregressive OR abs:"transfer learning")
```
Results: 128

### 4b. Cell + language model
```
abs:"foundation model" AND abs:"single cell" AND abs:"language model"
```
Results: 11 (0 new after dedup)

### 4c. Model names
```
(ti:scGPT OR ti:tGPT OR ti:LangCell OR ti:ChatCell OR ti:GenePT OR ti:GeneGPT OR ti:CellPLM OR ti:Nicheformer OR ti:EpiAgent)
```
Results: 6 (5 new)

### 4d. Bio + LLM
```
abs:"gene expression" AND abs:LLM AND (abs:generative OR abs:decoder OR abs:autoregressive)
```
Results: 10 (7 new)

**Total unique results**: 140
**Records retrieved**: 140
**Export file**: `data/exports/arxiv_2026-02-06.json`
**Notes**: arXiv has known stemming bug (#303) for phrase matching; verified key terms return expected results. Category filter applied to all sub-queries.

---

## 5. bioRxiv / medRxiv (via EuropePMC REST API)

**Interface**: EuropePMC REST API (`https://www.ebi.ac.uk/europepmc/webservices/rest/search`)
**Source filter**: `SRC:PPR` (preprints only)
**Date filter**: `FIRST_PDATE:[2018-01-01 TO 2026-12-31]`
**Full Boolean**: supported

**Exact query**:
```
("single-cell" OR "single cell" OR "scRNA-seq" OR "RNA-seq" OR "gene expression" OR "scATAC-seq" OR "ATAC-seq" OR "chromatin accessibility" OR "CITE-seq" OR "spatial transcriptomics" OR "multi-omics" OR transcriptomics OR genomics OR proteomics OR epigenomics)
AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR NLP)
AND ("foundation model" OR pretrain* OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "deep learning")
AND (SRC:PPR)
AND FIRST_PDATE:[2018-01-01 TO 2026-12-31]
```

**Results**: 657
**Records retrieved**: 657
**Export file**: `data/exports/biorxiv_medrxiv_2026-02-06.json`
**Notes**: bioRxiv/medRxiv native API does NOT support content search (only date-range browsing). EuropePMC is used as the primary interface for preprint search with full Boolean support. `SRC:PPR` filter restricts to preprints.

---

## 6. SpringerNature (Meta API v2)

**Interface**: SpringerNature Meta API v2 (`https://api.springernature.com/meta/v2/json`)
**Search fields**: Full-text (title/abstract field restriction is premium-only)
**Date filter**: `datefrom:2018-01-01 dateto:2026-12-31`
**Boolean operators**: UPPERCASE required

**Exact query**:
```
("single-cell" OR "single cell" OR scRNA-seq OR "RNA-seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory")
AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokenization OR "gene token" OR prompt OR "text generation" OR NLP)
AND ("foundation model" OR pretrained OR "pre-trained" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")
datefrom:2018-01-01 dateto:2026-12-31
```

**Results**: 26,498 (Meta API full-text), 11,903 (Open Access API full-text)
**Records retrieved (raw)**: 17,737 unique (11,650 from Meta API + 6,087 new from OA API, deduplicated by DOI)
**Records after title/abstract validation**: 258
**Export files**:
- `data/exports/springernature_2026-02-06.json` — raw 17,737 records
- `data/exports/springernature_filtered_2026-02-06.json` — 258 validated records

**Post-retrieval title/abstract validation**:
SpringerNature Meta API searches full-text (body), not title/abstract. The `title:` field constraint is a premium-only feature unavailable on the free tier. To ensure comparability with other databases that natively search title/abstract (PubMed, Scopus), a post-retrieval validation step was applied: records were retained only if at least one term from **each** concept block (A AND B AND C) appeared in the record's title or abstract.

Validation patterns (case-insensitive regex, applied to title + abstract):
```
Block A: single.cell|scRNA|RNA-seq|gene expression|scATAC|ATAC-seq|chromatin accessibility|CITE-seq|spatial transcriptomics|multi-omics|multiomics|transcriptomics|genomics|proteomics|epigenomics|cell type|gene regulatory

Block B: language model|LLM|large language model|natural language|GPT|CLIP|cross-modal|multimodal|multi-modal|tokeniz|gene token|prompt|text generation|NLP

Block C: foundation model|pretrain|pre-train|self-supervised|transformer|generative|decoder|autoregressive|transfer learning|zero-shot|few-shot|masked modeling|attention mechanism|deep learning
```

Result: 17,737 → 258 records (98.5% removed as full-text-only matches).

**Additional notes**: Free API tier limits page size to `p=25` (p>=30 returns "premium feature" error). Meta API rate-limited after ~11,650 records; supplemented with Open Access API (separate key). Remaining ~8,761 unretreived records from positions >11,650 in Meta results; given 98.5% noise rate, estimated ~13 additional relevant records would be found there.

---

## 7. Google Scholar (Supplementary)

**Interface**: Google Scholar via `scholarly` Python library
**Date filter**: 2018–2026
**Role**: Supplementary source for validation and grey literature

**Queries executed**:
1. `"foundation model" "gene expression" "language model" single-cell`
2. `GPT "single cell" "gene expression" generative`
3. `"natural language" "single-cell" "cell type" foundation model`
4. `multimodal LLM genomics transcriptomics "foundation model"`
5. `scGPT OR tGPT OR LangCell OR ChatCell OR CellWhisperer OR GenePT OR GeneGPT OR CellPLM OR Nicheformer OR EpiAgent`

**Results**: 514 unique (across 5 queries, 200 cap per query)
**Records retrieved**: 514
**Export file**: `data/exports/google_scholar_2026-02-06.json`
**Notes**: GS has no official API; `scholarly` library used for automated retrieval. Max ~200 results per query (cap applied). Query 5 (model names) returned error "Cannot Fetch from Google Scholar" (likely rate limit). GS results are supplementary and require cross-referencing with primary database results. No formal Boolean support — simplified queries used.

---

## Summary Table

| Database | Interface | Search Fields | Results | Retrieved | File |
|---|---|---|---|---|---|
| PubMed | Entrez API | Title/Abstract | 619 | 619 | `pubmed_2026-02-06.json` |
| Scopus | Scopus API | Title/Abstract/Keywords | 1,014 | 1,014 | `scopus_2026-02-06.json` |
| Semantic Scholar | Bulk Search API | Title/Abstract | 2,070 | 2,069 | `semantic_scholar_2026-02-06.json` |
| arXiv | arXiv API | Title/Abstract | 140 | 140 | `arxiv_2026-02-06.json` |
| bioRxiv/medRxiv | EuropePMC API | Full text | 657 | 657 | `biorxiv_medrxiv_2026-02-06.json` |
| SpringerNature | Meta + OA API | Full text* | 26,498 | 258** | `springernature_filtered_2026-02-06.json` |
| Google Scholar | scholarly lib | Full text | ~514 | 514 | `google_scholar_2026-02-06.json` |
| **Total (before dedup)** | | | | **5,271** | |

\* SpringerNature searches full-text body; title/abstract restriction is premium-only.
\** Post-retrieval title/abstract validation applied (A AND B AND C in title/abstract). Raw: 17,737 retrieved of 26,498.

---

## Ground Truth Validation

Models that MUST be found in at least one database:
- [x] scGPT (58 hits across 5 databases)
- [x] tGPT (40 hits across 6 databases)
- [x] LangCell (4 hits: S2, arXiv, GS)
- [x] ChatCell (2 hits: arXiv, GS)
- [x] CellWhisperer (3 hits: bioRxiv, GS)
- [x] CellPLM (4 hits: S2, bioRxiv, GS)
- [x] Nicheformer (1 hit: GS only)
- [x] EpiAgent (1 hit: GS only)
- [x] GenePT (11 hits: PubMed, S2, bioRxiv, GS)
- [x] GeneGPT (13 hits: PubMed, Scopus, S2, arXiv)
- [x] PathOmCLIP (2 hits: S2, bioRxiv)

Models expected in "Related but excluded" (encoder-only):
- [x] scBERT (9 hits)
- [x] Geneformer (14 hits)
- [x] scFoundation (3 hits)
- [x] UCE (459 hits — inflated due to common abbreviation)

**Validation status**: PASSED (2026-02-06)

All 11 must-find models found across databases:

| Model | PubMed | Scopus | S2 | arXiv | bioRxiv | SN* | GS | Total |
|---|---|---|---|---|---|---|---|---|
| scGPT | 2 | 0 | 8 | 1 | 5 | 5 | 42 | 63 |
| tGPT | 5 | 6 | 16 | 1 | 2 | 1 | 10 | 41 |
| LangCell | 0 | 0 | 1 | 1 | 0 | 0 | 2 | 4 |
| ChatCell | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 2 |
| CellWhisperer | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 4 |
| CellPLM | 0 | 0 | 1 | 0 | 1 | 0 | 2 | 4 |
| Nicheformer | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| EpiAgent | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| GenePT | 1 | 0 | 1 | 0 | 1 | 1 | 8 | 12 |
| GeneGPT | 1 | 1 | 4 | 3 | 0 | 0 | 4 | 13 |
| PathOmCLIP | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 2 |

\* SN = SpringerNature (after title/abstract validation, 258 records)

All 4 encoder-only models also found (for supplementary table):
scBERT (9), Geneformer (14), scFoundation (3), UCE (459 — inflated due to "UCE" being a common abbreviation in other contexts)

**Note**: Nicheformer and EpiAgent found only in Google Scholar — critical that GS is included as supplementary source.

---

## Technical Notes

1. **PubMed OA filter**: `"open access"[filter]` returns 0 via Entrez API. Working alternative: `"free full text"[sb]` (619 results).
2. **Semantic Scholar**: Must use `/paper/search/bulk` endpoint for Boolean queries. `/paper/search` (relevance search) does NOT support Boolean.
3. **SpringerNature pagination**: Free tier limits page size to `p≤25`. `p=30+` returns "premium feature" error.
4. **SpringerNature field restriction**: `title:`, `keyword:`, `subject:`, `discipline:`, `year:` are all premium-only features. Only `datefrom:`/`dateto:` available for free tier.
5. **bioRxiv native API**: Does NOT support content search. EuropePMC with `SRC:PPR` filter is the recommended approach.
6. **arXiv stemming bug**: GitHub issue #303. Phrase matching may produce false negatives due to stemming. Mitigated by using multiple sub-queries.
