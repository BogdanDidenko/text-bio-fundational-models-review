# F6 semantic-sufficiency failure modes

The audit primarily identifies over-specific field coding, not automatically false input routes. `revise_fields` means the paper establishes a route but does not establish every current source, transformation, carrier, topology, lifecycle, text-role, or input-status assertion. `manual_full_text_review` remains unresolved computationally.

## Records requiring action

| Record | Retain | Revise fields | Manual review |
|---|---:|---:|---:|
| `full_2026-07-06__rec_000086` — PROCYON: A multimodal foundation model for protein phenotypes. | 12 | 12 | 4 |
| `full_2026-07-06__rec_003517` — X-Cell: Scaling Causal Perturbation Prediction Across Diverse Cellular Contexts via Diffusion Language Models | 3 | 13 | 0 |
| `july_update_2026-07-06__rec_000060` — CellTosg2Sequence: A Unified Text-Omics-Signaling-Graph Large Language Model for Single-Cell Analysis | 2 | 3 | 0 |
| `june_update_2026-06-10__rec_000246` — OmicsLM: A Multimodal Large Language Model for Multi-Sample Omics Reasoning | 1 | 3 | 0 |
| `full_2026-07-06__rec_001343` — A General Single-Cell Analysis Framework via Conditional Diffusion Generative Models | 0 | 2 | 0 |
| `full_2026-07-06__rec_001381` — Language-Enhanced Representation Learning for Single-Cell Transcriptomics | 2 | 2 | 0 |
| `full_2026-07-06__rec_002327` — OmniNA: A foundation model for nucleotide sequences | 0 | 2 | 0 |
| `full_2026-07-06__rec_003629` — Phenotype-Guided In Silico Molecular Generation Using Large Language Models | 0 | 2 | 0 |
| `full_2026-07-06__rec_000950` — Illuminating protein space with a programmable generative model | 0 | 1 | 0 |
| `full_2026-07-06__rec_001074` — BIOREASON: Incentivizing Multimodal Biological Reasoning within a DNA-LLM Model | 0 | 1 | 0 |
| `full_2026-07-06__rec_001187` — Precious3GPT: Multimodal Multi-Species Multi-Omics Multi-Tissue Transformer for Aging Research and Drug Discovery | 2 | 1 | 0 |
| `full_2026-07-06__rec_003043` — Geneverse: A collection of Open-source Multimodal Large Language Models for Genomic and Proteomic Research | 0 | 1 | 0 |
| `june_update_2026-06-10__rec_000350` — OmniGene-4: a unified bio-language MoE model with router-level interpretability | 4 | 1 | 0 |
| `update_2026-08-09__manual_recall_xunzi` — XunZi, an AI biologist, reveals disease-modifying targets | 0 | 1 | 0 |
| `update_2026-08-09__rec_000138` — OCellus: A Language-Model Framework for Single-Cell, Spatial, and Perturbation Biology with Natural-Language Reasoning | 0 | 1 | 0 |

## Unsupported or incomplete fields

Counts below are field verdicts, so one route may contribute several rows.

| Field | Verdict | Routes |
|---|---|---:|
| `carrier_family_and_subtype` | `partially_supported` | 24 |
| `fusion_topology` | `unsupported` | 21 |
| `carrier_family_and_subtype` | `unsupported` | 17 |
| `model_visible_form` | `unsupported` | 14 |
| `insertion_or_fusion` | `unsupported` | 14 |
| `fusion_topology` | `unclear` | 9 |
| `text_role` | `unsupported` | 8 |
| `input_status` | `unsupported` | 7 |
| `fusion_topology` | `partially_supported` | 5 |
| `insertion_or_fusion` | `partially_supported` | 5 |
| `lifecycle_phase` | `unsupported` | 5 |
| `source_object` | `unsupported` | 4 |
| `input_status` | `unclear` | 4 |
| `model_visible_form` | `partially_supported` | 4 |
| `text_role` | `partially_supported` | 1 |
| `source_object` | `partially_supported` | 1 |

## Manual full-text queue

- `route_18a49a03ed5f` (ProCyon, GO Function): The benchmark label is real, but the peptide-specific coding is not established by the document.
- `route_67d60756e8b4` (ProCyon, Drugbank Target): The label exists in the paper, but the evaluation-time peptide coding is not supported.
- `route_7d3bbc8ca354` (ProCyon, Drugbank Transporter): The label exists in the paper, but the evaluation-time peptide coding is not supported.
- `route_ba110b719918` (ProCyon, GtoP): The label exists in the paper, but the evaluation-time peptide coding is not supported.

The complete field explanations, verified supporting quotes, unsupported assertions, blind reviewer outputs, and adjudication are retained in the route-level disposition ledger and `runs/` tree.
