# Generative Foundation Models Bridging Text and Biological Data: A Scoping Review

Supplementary materials and reproducible search scripts for the scoping review.

## Overview

This repository contains the complete search methodology, PRISMA-S protocol, and reproducible search scripts for a scoping review that identifies **generative foundation models combining text modality (natural language or gene tokens) with biological data modalities** (single-cell transcriptomics, genomics, proteomics, epigenomics, spatial transcriptomics, etc.).

### Review Question

> What generative foundation models exist that combine text modality with biological data modalities, and how do they bridge language and biology?

### Scope

- **Date range**: January 2018 -- February 2026
- **Databases**: 7 (PubMed, Scopus, Semantic Scholar, arXiv, bioRxiv/medRxiv, SpringerNature, Google Scholar)
- **Access**: Open access publications only
- **Language**: English

## Repository Structure

```
.
├── README.md                    # This file
├── LICENSE                      # MIT License
├── scripts/                     # Reproducible search scripts
│   ├── reproduce_search.py      # Main script — queries all 7 databases
│   ├── search_config.json       # Exact Boolean queries and filters
│   ├── api_keys.template.json   # Template for API keys
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Script usage instructions
├── protocol/                    # PRISMA-S protocol and methodology
│   ├── PRISMA_protocol.md       # Full PRISMA-S protocol (v3.0)
│   ├── eligibility_criteria.md  # Inclusion/exclusion criteria
│   ├── search_strategy.md       # Search strategy description
│   ├── screening_process.md     # Screening methodology
│   ├── data_extraction.md       # Data extraction form
│   ├── prisma_flow_template.md  # PRISMA flow diagram template
│   └── queries/                 # Database-specific query files
│       ├── pubmed.txt
│       ├── scopus.txt
│       ├── semantic_scholar.txt
│       ├── arxiv.txt
│       ├── biorxiv_medrxiv.txt
│       ├── springernature.txt
│       └── google_scholar.txt
└── data/
    ├── search_log_2026-02-06.md # Detailed search execution log
    └── exports/                 # Original search results (JSON)
        ├── pubmed_2026-02-06.json
        ├── scopus_2026-02-06.json
        ├── semantic_scholar_2026-02-06.json
        ├── arxiv_2026-02-06.json
        ├── biorxiv_medrxiv_2026-02-06.json
        ├── springernature_filtered_2026-02-06.json
        └── google_scholar_2026-02-06.json
```

## Search Strategy

The search uses three concept blocks combined with AND logic:

| Block | Concept | Example Terms |
|---|---|---|
| **A** | Biological data | single-cell, scRNA-seq, gene expression, transcriptomics, genomics, proteomics, spatial transcriptomics, multi-omics |
| **B** | Text / language | language model, LLM, GPT, CLIP, multimodal, cross-modal, NLP, tokenization |
| **C** | FM + generativity | foundation model, pretrained, self-supervised, transformer, generative, decoder, autoregressive, transfer learning |

### Databases and Results

| # | Database | Interface | Records |
|---|---|---|---|
| 1 | PubMed | NCBI Entrez API | ~620 |
| 2 | Scopus | Elsevier API | ~1,010 |
| 3 | Semantic Scholar | S2 Bulk Search API | ~2,150 |
| 4 | arXiv | arXiv API | ~185 |
| 5 | bioRxiv/medRxiv | EuropePMC API | ~670 |
| 6 | SpringerNature | Meta + OA APIs | ~250 (validated) |
| 7 | Google Scholar | scholarly library | ~514 |
| | **Total (before dedup)** | | **~5,400** |

## Reproducing the Search

See [scripts/README.md](scripts/README.md) for detailed instructions.

Quick start:
```bash
cd scripts
pip install -r requirements.txt
cp api_keys.template.json api_keys.json  # Fill in your API keys
python reproduce_search.py --keys api_keys.json \
  --gs-fallback ../data/exports/google_scholar_2026-02-06.json
```

## Ground Truth Validation

11 known models are used to validate search completeness:

| Model | Found |
|---|---|
| scGPT, tGPT, LangCell, ChatCell, CellWhisperer, CellPLM, Nicheformer, EpiAgent, GenePT, GeneGPT, PathOmCLIP | 11/11 |

## Citation

If you use this search methodology or data, please cite:

> Didenko B. Generative Foundation Models Bridging Text and Biological Data: A Scoping Review. 2026.

## License

MIT License. See [LICENSE](LICENSE).
