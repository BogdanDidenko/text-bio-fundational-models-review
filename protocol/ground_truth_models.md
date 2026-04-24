# Ground Truth Models

Models that **must** be found by the search and correctly classified during
screening. This file serves two roles:

1. **Search validation anchor**: every must-include model should appear in at
   least one database export.
2. **Benchmark recall anchor** for the criterion-by-criterion LLM screening
   workflow, aligned with the benchmark schema in
   [`screening_benchmark_and_tiers.md`](screening_benchmark_and_tiers.md).

This file is **not** a complete definition of scope. The benchmark must also
contain must-exclude papers from multiple exclusion families and genuinely hard
borderline records (see `screening_benchmark_and_tiers.md §4` for full
composition).

---

## 1. Must-Include — Clear In-Scope Positives (Benchmark Group P1)

Papers with explicit text–biology bridge and natural language interaction.

| # | Model | Year | Modalities | Architecture | Key source |
|---|-------|------|-----------|--------------|------------|
| 3 | LangCell | 2024 | NL text + gene expression | CLIP-style alignment + generation | Text-to-cell, cell-to-text |
| 4 | ChatCell | 2024 | NL text + gene expression | LLM chat interface + generation | Conversational cell analysis |
| 5 | CellWhisperer | 2024 | NL text + gene expression | LLM + scRNA-seq encoder | Text generation from cells |
| 8 | EpiAgent | 2024 | NL text + epigenomics | LLM agent + bio tools | Agent-based epigenomics |
| 9 | GenePT | 2024 | NL gene descriptions + expression | GPT embeddings + bio data | NL-guided gene analysis |
| 10 | GeneGPT | 2023 | NL text + NCBI tools | LLM agent + gene databases | Tool-augmented LLM |
| 11 | PathOmCLIP | 2024 | NL text + pathology + omics | CLIP-style alignment | Cross-modal retrieval |
| 12 | Cell2Seq | 2026 | scRNA-seq tokens + NL text + metadata | 27B parameter LLM | DOI: 10.1101/2025.04.14.648850 |

### Expected criterion-level labels for Group P1

| Field | Expected value |
|-------|---------------|
| `expected_final_decision` | `INCLUDE` |
| `expected_paper_type` | `primary_model_paper` |
| `expected_bio_modality_present` | `yes` |
| `expected_text_component_present` | `yes` |
| `expected_text_bio_bridge_present` | `yes` |
| `expected_generative_model_present` | `yes` |
| `expected_foundation_model_evidence` | `yes` |
| `expected_primary_exclusion_code` | `none` |
| `expected_uncertainty_reason` | (blank) |

---

## 2. Must-Include — Protocol-Exception Positives (Benchmark Group P2)

Biological-token generative models. These papers use gene tokens in a GPT-style
decoder without a natural-language component. They are included under the
explicit protocol exception for biological-token generative models.

| # | Model | Year | Modalities | Architecture | Key source |
|---|-------|------|-----------|--------------|------------|
| 1 | scGPT | 2024 | Gene tokens + cell types | GPT-style autoregressive | Gene token decoder |
| 2 | tGPT | 2023 | Gene tokens + cell types | GPT-style autoregressive | Generative cell modeling |
| 6 | CellPLM | 2024 | Gene tokens + spatial | Transformer decoder | Pathway-level language model |
| 7 | Nicheformer | 2024 | Gene tokens + spatial niches | Transformer decoder | Niche-aware generation |
| 13 | X-Cell | 2026 | Perturbation + gene expression | Diffusion language model | DOI: 10.64898/2026.03.18.712807 |

### Expected criterion-level labels for Group P2

| Field | Expected value |
|-------|---------------|
| `expected_final_decision` | `INCLUDE` |
| `expected_paper_type` | `primary_model_paper` |
| `expected_bio_modality_present` | `yes` |
| `expected_text_component_present` | `yes` — gene-token generative language modeling per protocol exception |
| `expected_text_bio_bridge_present` | `yes` — gene tokens drive generative modeling |
| `expected_generative_model_present` | `yes` |
| `expected_foundation_model_evidence` | `yes` |
| `expected_primary_exclusion_code` | `none` |
| `expected_uncertainty_reason` | (blank) |

These papers are the canonical stress test for whether the screening system
preserves the biological-token protocol exception instead of collapsing it into
an EC2 exclusion for "no text component."

---

## 3. Related but Excluded — Encoder-Only Negatives (Benchmark Group N3)

Pure encoder-only architectures. These are excluded from the primary analysis
per `eligibility_criteria.md` EC3 and listed in the supplementary
"related but excluded" table.

| # | Model | Year | Architecture | Reason |
|---|-------|------|--------------|--------|
| 1 | scBERT | 2022 | BERT-style MLM | Encoder-only |
| 2 | Geneformer | 2023 | BERT-style MLM | Encoder-only |
| 3 | scFoundation | 2024 | Encoder-only | Encoder-only |
| 4 | UCE | 2024 | Encoder-only | Encoder-only |

### Expected criterion-level labels for Group N3

| Field | Expected value |
|-------|---------------|
| `expected_final_decision` | `EXCLUDE` |
| `expected_paper_type` | `primary_model_paper` |
| `expected_bio_modality_present` | `yes` |
| `expected_text_component_present` | `yes` — gene-token modeling present |
| `expected_text_bio_bridge_present` | `yes` |
| `expected_generative_model_present` | `no` — encoder-only MLM, no generation |
| `expected_foundation_model_evidence` | `yes` |
| `expected_primary_exclusion_code` | `EC3_not_generative` |
| `expected_uncertainty_reason` | (blank) |

These are the canonical stress test for whether the screening system correctly
rejects encoder-only architectures when `generative_model_present=no`.

---

## 4. Search Validation Status

### Search v3.1 (2026-02-15)
All 11 original must-find models found across combined 7 databases.

### Update search (2026-04-14)
- X-Cell: found in Semantic Scholar
- Cell2Seq: found in 4 databases (PubMed, S2, bioRxiv, GS). Paper title:
  "Scaling Large Language Models for Next-Generation Single-Cell Analysis"
  (DOI: 10.1101/2025.04.14.648850)

### Combined
All 13 must-find models are present in the combined corpus. All 4 encoder-only
negatives are also present and should be excluded by the screening system
through the `generative_model_present=no` path.

---

## 5. How This File Is Used By The Screening Benchmark

The manual benchmark in `screening_benchmark_and_tiers.md §4` uses these models
as two of its seven groups:

- Group P1 (clear positives) — maps to Section 1 of this file
- Group P2 (protocol-exception positives) — maps to Section 2 of this file
- Group N3 (encoder-only negatives) — maps to Section 3 of this file

The remaining groups (N1 review/editorial, N2 bio-only, N4 wrappers, N5
benchmark/resource, U1 borderline uncertain) must be populated from the actual
corpus with manual adjudication before the benchmark can be used as a
deployment gate.

---

## 6. Important Caveats

- These labels are derived from what each model paper describes in its
  abstract, not from outside knowledge. The screening reviewers are instructed
  to use only title/abstract evidence.
- For a real benchmark run, each model must be paired with its actual
  title/abstract text, not with its name in this table.
- The criterion labels above should be re-adjudicated if the eligibility
  criteria or the criterion schema change.
