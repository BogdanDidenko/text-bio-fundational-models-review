# PRISMA-S Search and Screening Log

**Review title**: Generative Foundation Models Bridging Text and Biological Data: A Scoping Review  
**Log date**: 2026-07-07  
**Protocol version**: v4.2  
**Review type**: Scoping review using PRISMA-ScR with PRISMA-S search reporting and PRISMA-trAIce-style LLM screening auditability.

This log records the current search, deduplication, and title/abstract
screening state. The full artifact bundle is:

`analysis/codex_screening_run_artifacts_20260706/`

## Information Sources

Seven sources were searched:

| Source | Interface | Role |
|---|---|---|
| PubMed / MEDLINE | NCBI Entrez E-utilities API | Biomedical database |
| Scopus | Elsevier Scopus API | Multidisciplinary database |
| Semantic Scholar | S2 Academic Graph bulk search API | AI/ML and citation graph database |
| arXiv | arXiv API | AI/ML preprint server |
| bioRxiv / medRxiv | EuropePMC REST API with `SRC:PPR` | Biology/medicine preprint search |
| SpringerNature | Meta API v2 + Open Access API | Publisher database |
| Google Scholar | `scholarly` Python library | Supplementary validation source |

## Concept Blocks

The search used three concept blocks combined as `A AND B AND C`.

| Block | Concept | Terms |
|---|---|---|
| A | Biological data | `single-cell`, `single cell`, `scRNA-seq`, `RNA-seq`, `RNA seq`, `gene expression`, `scATAC-seq`, `ATAC-seq`, `chromatin accessibility`, `CITE-seq`, `spatial transcriptomics`, `multi-omics`, `multi omics`, `multiomics`, `transcriptomics`, `genomics`, `proteomics`, `epigenomics`, `cell type`, `gene regulatory` |
| B | Text / language | `language model`, `LLM`, `large language model`, `natural language`, `GPT`, `CLIP`, `cross-modal`, `multimodal`, `multi-modal`, `tokenization`, `gene token`, `prompt`, `text generation`, `cell-to-text`, `text-to-cell`, `NLP` |
| C | FM + generativity | `foundation model`, `pretrained`, `pre-trained`, `self-supervised`, `transformer`, `generative`, `decoder`, `autoregressive`, `transfer learning`, `zero-shot`, `few-shot`, `masked modeling`, `attention mechanism`, `deep learning` |

## Exact Query Locations

Canonical full-window query files are in `protocol/queries/`.

For the June and July top-up searches, exact database-specific queries and
date filters are preserved in:

- `analysis/codex_screening_run_artifacts_20260706/search_configs/search_config_update_2026-06-10.json`
- `analysis/codex_screening_run_artifacts_20260706/search_configs/search_config_update_2026-07-06.json`

These configs preserve the exact PubMed, Scopus, Semantic Scholar, arXiv,
bioRxiv/medRxiv, SpringerNature, and Google Scholar strings used by the
reproducibility script.

## Database-Specific Query Forms for Update Searches

The June and July update searches reused the same concept structure. Only the
date bounds changed:

- June update: 2026-04-15 to 2026-06-10
- July update: 2026-06-11 to 2026-07-06

### PubMed

July exact query:

```text
(("single cell"[Title/Abstract] OR "single-cell"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR "RNA-seq"[Title/Abstract] OR "RNA seq"[Title/Abstract] OR "gene expression"[Title/Abstract] OR scATAC-seq[Title/Abstract] OR "ATAC-seq"[Title/Abstract] OR "chromatin accessibility"[Title/Abstract] OR CITE-seq[Title/Abstract] OR "spatial transcriptomics"[Title/Abstract] OR "multi-omics"[Title/Abstract] OR "multi omics"[Title/Abstract] OR multiomics[Title/Abstract] OR transcriptomics[Title/Abstract] OR genomics[Title/Abstract] OR proteomics[Title/Abstract] OR epigenomics[Title/Abstract] OR "cell type"[Title/Abstract] OR "gene regulatory"[Title/Abstract]) AND ("language model"[Title/Abstract] OR LLM[Title/Abstract] OR "large language model"[Title/Abstract] OR "natural language"[Title/Abstract] OR GPT[Title/Abstract] OR CLIP[Title/Abstract] OR "cross-modal"[Title/Abstract] OR multimodal[Title/Abstract] OR "multi-modal"[Title/Abstract] OR tokenization[Title/Abstract] OR "gene token"[Title/Abstract] OR prompt[Title/Abstract] OR "text generation"[Title/Abstract] OR "cell-to-text"[Title/Abstract] OR "text-to-cell"[Title/Abstract] OR NLP[Title/Abstract]) AND ("foundation model"[Title/Abstract] OR pretrained[Title/Abstract] OR "pre-trained"[Title/Abstract] OR "self-supervised"[Title/Abstract] OR transformer[Title/Abstract] OR generative[Title/Abstract] OR decoder[Title/Abstract] OR autoregressive[Title/Abstract] OR "transfer learning"[Title/Abstract] OR "zero-shot"[Title/Abstract] OR "few-shot"[Title/Abstract] OR "masked modeling"[Title/Abstract] OR "attention mechanism"[Title/Abstract] OR "deep learning"[Title/Abstract])) AND ("2026/06/11"[Date - Publication] : "2026/07/06"[Date - Publication]) AND "free full text"[sb] AND English[Language]
```

### Scopus

Scopus only supports year-level filtering in this workflow, so the API query
used `PUBYEAR > 2025` and the script post-filtered records to the update
window.

```text
TITLE-ABS-KEY(("single cell" OR "single-cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR "cell-to-text" OR "text-to-cell" OR NLP) AND ("foundation model" OR pretrain* OR "pre-train*" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")) AND PUBYEAR > 2025 AND OPENACCESS(1) AND LANGUAGE(English)
```

### Semantic Scholar

Semantic Scholar used `/paper/search/bulk`, `year=2026`, and post-filtering to
the update date window.

Main query:

```text
("single-cell" | "single cell" | "scRNA-seq" | "RNA-seq" | "RNA seq" | "gene expression" | transcriptomics | genomics | proteomics | epigenomics | "spatial transcriptomics" | "multi-omics" | "multi omics") + ("language model" | LLM | "large language model" | "natural language" | GPT | CLIP | multimodal | "multi-modal" | "cross-modal" | tokeniz* | prompt | NLP | "text generation") + ("foundation model" | pretrain* | "self-supervised" | transformer | generative | decoder | autoregressive | "transfer learning" | "zero-shot" | "deep learning")
```

Model-name query:

```text
(scGPT | tGPT | LangCell | ChatCell | CellWhisperer | GenePT | GeneGPT | CellPLM | Nicheformer | EpiAgent | PathOmCLIP)
```

### arXiv

arXiv used multiple focused subqueries and merged/deduplicated by arXiv ID.

Primary:

```text
(ti:"single cell" OR ti:scRNA OR ti:"gene expression" OR ti:transcriptomics OR ti:genomics OR abs:"single-cell" OR abs:"RNA-seq" OR abs:"RNA seq" OR abs:"spatial transcriptomics" OR abs:"multi-omics" OR abs:"multi omics") AND (ti:"language model" OR ti:GPT OR ti:LLM OR ti:CLIP OR ti:multimodal OR abs:"language model" OR abs:"large language model" OR abs:"natural language" OR abs:"cross-modal" OR abs:"multi-modal" OR abs:tokeniz OR abs:prompt) AND (abs:"foundation model" OR abs:pretrain OR abs:"self-supervised" OR abs:transformer OR abs:generative OR abs:decoder OR abs:autoregressive OR abs:"transfer learning")
```

Additional subqueries:

```text
abs:"foundation model" AND abs:"single cell" AND abs:"language model"
(ti:scGPT OR ti:tGPT OR ti:LangCell OR ti:ChatCell OR ti:GenePT OR ti:GeneGPT OR ti:CellPLM OR ti:Nicheformer OR ti:EpiAgent)
abs:"gene expression" AND abs:LLM AND (abs:generative OR abs:decoder OR abs:autoregressive)
```

### bioRxiv / medRxiv via EuropePMC

```text
("single-cell" OR "single cell" OR "scRNA-seq" OR "RNA-seq" OR "RNA seq" OR "gene expression" OR "scATAC-seq" OR "ATAC-seq" OR "chromatin accessibility" OR "CITE-seq" OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR transcriptomics OR genomics OR proteomics OR epigenomics) AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrain* OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "deep learning") AND (SRC:PPR) AND FIRST_PDATE:[2026-06-11 TO 2026-07-06]
```

### SpringerNature

SpringerNature free APIs do not support title/abstract-only searching, so
retrieval used the API query below and then post-retrieval title/abstract
validation against all three concept blocks.

```text
("single-cell" OR "single cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokenization OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrained OR "pre-trained" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")
```

### Google Scholar

Google Scholar was supplementary. The script used year `2026`; month-level
filtering is not available and was handled through metadata/date checks and
cross-deduplication.

```text
"foundation model" "gene expression" "language model" single-cell
GPT "single cell" "gene expression" generative
"natural language" "single-cell" "cell type" foundation model
multimodal LLM genomics transcriptomics "foundation model"
scGPT OR tGPT OR LangCell OR ChatCell OR CellWhisperer OR GenePT OR GeneGPT OR CellPLM OR Nicheformer OR EpiAgent
"multi omics" "language model" "foundation model" transformer
"RNA seq" LLM "foundation model" generative single-cell
```

## Search Windows and Database Counts

| Search window | Search date | PubMed | Scopus | Semantic Scholar | arXiv | bioRxiv/medRxiv | SpringerNature | Google Scholar | Raw total | Source |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| v3.1 baseline, 2018-01-01 to 2026-02-28 | 2026-02-15 | See v3.1 search log | See v3.1 search log | See v3.1 search log | See v3.1 search log | See v3.1 search log | See v3.1 search log | See v3.1 search log | 5,534 | `protocol/PRISMA_protocol.md` amendment v3.1 |
| Top-up, 2026-03-01 to 2026-04-14 | 2026-04-14 | 46 | 32 | 201 | 14 | 5 | 33 | 536 | 867 | `data/exports_update/search_summary_2026-04-14.json` |
| Top-up, 2026-04-15 to 2026-06-10 | 2026-06-10 | 68 | 39 | 215 | 21 | 33 | 27 | 530 | 933 | `analysis/.../inputs/exports_update_2026-06-10/search_summary_2026-06-10.json` |
| Top-up, 2026-06-11 to 2026-07-06 | 2026-07-06 | 25 | 12 | 118 | 6 | 16 | 20 | 0 | 197 | `analysis/.../inputs/exports_update_2026-07-06/search_summary_2026-07-06.json` |

**Cumulative raw records identified via database searching**: 7,531.

## Record Management and Deduplication

Deduplication used exact, conservative rules:

1. DOI / all DOI variants
2. PMID
3. arXiv ID
4. normalized title
5. Crossref audit for hidden duplicate DOI/title matches in update cohorts

| Stage | Raw records | Unique within search window | Already in previous master | Truly new after cross-corpus dedup / Crossref audit | Screening-ready after abstract check | Notes |
|---|---:|---:|---:|---:|---:|---|
| v3.1 baseline through 2026-02-28 | 5,534 | Not separately restated here | Not applicable | 3,371 | 3,371 | v3.1 screening-ready corpus |
| 2026-03-01 to 2026-04-14 top-up | 867 | 762 | 94 | 668 | Added into 4,027 master after abstract enrichment | 12 records excluded for missing abstract after enrichment in master corpus |
| 2026-04-15 to 2026-06-10 top-up | 933 | 785 | 338 | 445 | 431 | 2 hidden duplicates removed by Crossref audit; 14 no-abstract records not screened |
| 2026-06-11 to 2026-07-06 top-up | 197 | 155 | 21 | 134 | 119 | 0 hidden duplicates removed by Crossref audit; 15 no-abstract records not screened |

Current cumulative record-management state:

- Raw database records across all windows: 7,531
- Unique records after within-window deduplication, cross-corpus deduplication, and Crossref audit, before abstract availability exclusions: 4,618
- Records excluded before title/abstract screening because no abstract was available: 41
- Records entering title/abstract screening: 4,577

## Codex Title/Abstract Screening

The current Codex screening pipeline used:

- Model: `gpt-5.4-mini`
- Runner: `analysis/codex_screening_run_artifacts_20260706/pipeline_code/run_codex_screening_pipeline.py`
- Role prompts: `analysis/codex_screening_run_artifacts_20260706/prompt_templates/`
- First-pass roles: `scope_reviewer`, `architecture_reviewer`
- Gate: deterministic Python gate over structured criterion fields
- Escalation role: `adjudicator` for conflicts or unresolved criteria
- Final labels: `INCLUDE`, `EXCLUDE`, `UNCERTAIN`

The prompts require structured criterion fields, evidence snippets, and brief
evidence-grounded rationales. Hidden model chain-of-thought is not available
and is not included.

## Screening Runs and Decisions

| Run | Records screened | EXCLUDE | UNCERTAIN | INCLUDE | Adjudicated | Final results | Per-role logs |
|---|---:|---:|---:|---:|---:|---|---|
| Full rerun of pre-June master corpus | 4,027 | 3,805 | 88 | 134 | 1,338 | `analysis/codex_screening_run_artifacts_20260706/full_runs/codex_gpt54mini_all4027_20260706/final_screening_results.json` | `analysis/codex_screening_run_artifacts_20260706/full_runs/codex_gpt54mini_all4027_20260706/role_logs.tar.gz` |
| June update cohort | 431 | 409 | 7 | 15 | 158 | `analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update431_20260610/final_screening_results.json` | `analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update431_20260610/role_logs.tar.gz` |
| July update cohort | 119 | 113 | 0 | 6 | 40 | `analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update155_20260706/final_screening_results.json` | `analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update155_20260706/role_logs.tar.gz` |
| **Total** | **4,577** | **4,327** | **95** | **155** | **1,536** | See run-specific files | See run-specific archives |

Each `role_logs.tar.gz` archive contains:

- `role_logs/scope_reviewer/batch_*.prompt.txt`
- `role_logs/scope_reviewer/batch_*.response.txt`
- `role_logs/scope_reviewer/batch_*.parsed.json`
- `role_logs/scope_reviewer/batch_*.meta.json`
- the same file pattern for `architecture_reviewer`
- the same file pattern for `adjudicator`
- `batch_*.stdout.log` and `batch_*.stderr.log` for every Codex exec batch

Thus each screened record can be traced from final decision to structured role
output and then to the original prompt/response batch.

## Current PRISMA Funnel

This is the current title/abstract-stage funnel. Full-text eligibility is not
yet locked.

| PRISMA step | Count | Notes |
|---|---:|---|
| Records identified from databases | 7,531 | Sum of v3.1 baseline and three top-up windows |
| Records removed before screening | 2,954 | Deduplication, cross-corpus duplicate removal, Crossref hidden-duplicate removal, and no-abstract exclusions |
| Records screened by title/abstract | 4,577 | 4,027 full rerun + 431 June update + 119 July update |
| Records excluded at title/abstract | 4,327 | Codex final `EXCLUDE` |
| Records retained as provisional include | 155 | Codex final `INCLUDE`; requires full-text confirmation |
| Records retained as uncertain/manual queue | 95 | Codex final `UNCERTAIN`; requires manual/full-text eligibility decision |
| Candidate records for full-text/manual eligibility | 250 | `INCLUDE + UNCERTAIN` |
| Full-text articles assessed for final eligibility | Pending | Not yet finalized in this log |
| Studies included in final qualitative synthesis | Pending | Not yet finalized in this log |

## Current Limitations / Known Issues

- This log reports title/abstract screening, not final full-text eligibility.
- Abstract-only screening can misclassify biological-token generative models
  when abstracts do not explicitly state the text/gene-token bridge. These
  cases are retained through `UNCERTAIN` or manual audit where possible.
- Google Scholar is supplementary and may be rate-limited; June search stopped
  after query 5/7, and July returned 0 records in the automated run.
