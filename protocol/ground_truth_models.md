# Ground Truth Models

Models that **must** be found by the search and correctly classified during screening.
Used for validation of search completeness and screening prompt accuracy.

## Must-Include (generative, text+bio, FM)

| # | Model | Year | Modalities | Architecture | Notes |
|---|-------|------|-----------|--------------|-------|
| 1 | scGPT | 2024 | Gene tokens + cell types | GPT-style autoregressive | Gene token decoder |
| 2 | tGPT | 2023 | Gene tokens + cell types | GPT-style autoregressive | Generative cell modeling |
| 3 | LangCell | 2024 | NL text + gene expression | CLIP-style alignment + generation | Text-to-cell, cell-to-text |
| 4 | ChatCell | 2024 | NL text + gene expression | LLM chat interface + generation | Conversational cell analysis |
| 5 | CellWhisperer | 2024 | NL text + gene expression | LLM + scRNA-seq encoder | Text generation from cells |
| 6 | CellPLM | 2024 | Gene tokens + spatial | Transformer decoder | Pathway-level language model |
| 7 | Nicheformer | 2024 | Gene tokens + spatial niches | Transformer decoder | Niche-aware generation |
| 8 | EpiAgent | 2024 | NL text + epigenomics | LLM agent + bio tools | Agent-based epigenomics |
| 9 | GenePT | 2024 | NL gene descriptions + expression | GPT embeddings + bio data | NL-guided gene analysis |
| 10 | GeneGPT | 2023 | NL text + NCBI tools | LLM agent + gene databases | Tool-augmented LLM |
| 11 | PathOmCLIP | 2024 | NL text + pathology + omics | CLIP-style alignment | Cross-modal retrieval |
| 12 | Cell2Seq | 2026 | scRNA-seq tokens + NL text + metadata | 27B parameter LLM | Paper: "Scaling LLMs for Next-Gen Single-Cell Analysis". DOI: 10.1101/2025.04.14.648850. Found in 4 DBs |
| 13 | X-Cell | 2026 | Perturbation + gene expression | Diffusion language model | CRISPRi Perturb-seq, cross-cell-type generalization |

## Related but Excluded (encoder-only, no generation)

| # | Model | Year | Reason for exclusion |
|---|-------|------|---------------------|
| 1 | scBERT | 2022 | Encoder-only (BERT-style MLM) |
| 2 | Geneformer | 2023 | Encoder-only (BERT-style MLM) |
| 3 | scFoundation | 2024 | Encoder-only |
| 4 | UCE | 2024 | Encoder-only |

## Validation Status

### Search v3.1 (2026-02-15)
All 11 original must-find models found across combined 7 databases.

### Update search (2026-04-14)
- X-Cell: found in Semantic Scholar
- Cell2Seq: found in 4 databases (PubMed, S2, bioRxiv, GS). Paper title: "Scaling Large Language Models for Next-Generation Single-Cell Analysis" (DOI: 10.1101/2025.04.14.648850)

## Usage

These models serve as ground truth for:
1. **Search validation**: every must-find model should appear in at least one database export
2. **Screening calibration**: screening prompt must classify all must-find models as INCLUDE
3. **Prompt few-shot examples**: some models used as worked examples in the screening prompt
