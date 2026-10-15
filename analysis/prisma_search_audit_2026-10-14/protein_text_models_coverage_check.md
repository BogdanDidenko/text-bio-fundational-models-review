# Coverage check: protein and biomolecular text–generative models (2026-10-15)

Question: were these models excluded at screening (no text component, not generative), or never retrieved?

Method: every record retrieved in all search executions (v3.0, v3.1 baseline, April, June, July, August exports, deduplication files and screening inputs; 2,324 JSON files) was scanned for each model name or title. None was found, so none reached screening. Each paper's title and abstract (arXiv API or Europe PMC) was then tested against the three concept blocks of the executed v3.1 PubMed query (A biological data, B text/language, C foundation model/generativity; phrase match, hyphen/space variants).

| Model | Source id | Date | Block A (biological data) | Block B (text) | Block C (FM/generative) | arXiv categories in search filter |
|---|---|---|---|---|---|---|
| ProteinDT | 2302.04611v4 | 2023-02-09 | no match | multi-modal | decoder, zero-shot | yes |
| BioT5 | 2310.07276v3 | 2023-10-11 | no match | natural language, cross-modal | no match | yes |
| BioT5+ | 2402.17810v2 | 2024-02-27 | no match | tokenization | pre-trained | yes |
| NatureLM | 2502.07527 | 2025-02-11 | no match | language model, natural language | foundation model, pre-trained | yes |
| Evolla | 10.1101/2025.01.05.630192 | 2025-01-06 | no match | language model, natural language | generative, zero-shot | n/a (bioRxiv) |
| Galactica | 2211.09085v1 | 2022-11-16 | no match | language model, large language model, GPT | no match | yes |
| InstructProtein | 2310.03269v1 | 2023-10-05 | no match | LLM, natural language, prompt, text generation | no match | yes |
| ProtLLM | 2403.07920v1 | 2024-02-28 | no match | language model, LLM, large language model, natural language, cross-modal | zero-shot | yes |
| Prot2Text | 2307.14367v3 | 2023-07-25 | no match | multimodal, multi-modal | decoder | yes |
| ProtT3 | 2405.12564v1 | 2024-05-21 | no match | cross-modal, text generation | no match | yes |
| ProLLaMA | 2402.16445v3 | 2024-02-26 | no match | language model, LLM, large language model, natural language, NLP | no match | no |
| TxGemma | 2504.06196v1 | 2025-04-08 | no match | natural language | no match | yes |

Not checked: Pinal (title lookup failed; Semantic Scholar rate limit).

Positive controls (included works with protein or sequence inputs), Block A terms in the exported title+abstract and retrieving sources. ChatNT takes nucleotide sequences only (its protein tasks are posed on coding sequences). By the charting table (`charting_table_models.csv`, modality labels), 13 included records carry protein inputs; in three (Chroma, PROCYON, BioMedGPT) proteins, with small molecules in BioMedGPT, are the only biological input:

- Chroma: retrieved by scopus; Block A terms: none in title/abstract (export had no abstract in 1 record(s); Scopus also matches author keywords and index terms).
- PROCYON: retrieved by biorxiv_medrxiv, google_scholar, pubmed, semantic_scholar; Block A terms: RNA seq, RNA-seq.
- BioMedGPT: retrieved by google_scholar; Block A terms: single cell, single-cell.
- ChatNT: retrieved by biorxiv_medrxiv, google_scholar, scopus, semantic_scholar, springernature; Block A terms: genomics, proteomics, transcriptomics.

## Why the query has no protein-sequence terms

- The review question admits any "biological data modalities", but protocol objective 1 lists them as
  "(omics, expression, genomics)", and Block A (`protocol/PRISMA_protocol.md`, concept table) has only
  omics-measurement and single-cell terms. The only protein terms are "proteomics" and CITE-seq; eligibility
  IC1 mentions proteins only as surface proteins (CITE-seq, REAP-seq) and proteomics.
- The v3.0 amendment (2026-02-06) changed the scope from "multi-modal single-cell FMs" to "generative FMs
  bridging text and biological data" and rewrote the concept blocks, but Block A kept the single-cell and
  omics-measurement vocabulary. No protocol file records a decision to exclude protein sequences or
  structures.
- Block A has no molecule-level terms for nucleic acids either ("DNA", "nucleotide", "genome"); nucleotide
  sequence models were retrieved when their abstracts used "genomics" or another omics term (e.g. ChatNT).
- The search validation set (13 must-find models) contains only single-cell and gene-level models, so the
  missing protein family could not show up as a recall failure.

## Size of the gap (API hit counts, 2026-10-15)

Window 2018-01-01 to 2026-08-09; the v3.1 Block B (text) and Block C (FM/generative) unchanged; the new
biological block replaces Block A, and records that the original Block A already matches are removed
(NOT Block A). Protein block: protein, proteins, "protein sequence(s)", "amino acid", peptide(s),
antibody/antibodies, enzyme(s), "protein structure", "protein language model", "protein design".
Nucleotide block: DNA, RNA, nucleotide(s), genome(s), genomic, "DNA sequence", "RNA sequence",
"regulatory sequence". PubMed keeps its limits ("free full text"[sb], English[Language]).

| Source | Original query (control) | New records, protein block | New records, nucleotide block |
|---|---:|---:|---:|
| PubMed | 939 | 1,140 | 508 |
| Europe PMC preprints (SRC:PPR) | not counted | 1,130 | 633 |

Protein and nucleotide sets can overlap. Scopus, Semantic Scholar, Springer Nature, OpenAlex and Google
Scholar were not counted.
