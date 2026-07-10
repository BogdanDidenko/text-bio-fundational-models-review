# Human-Confirmed Resolution of Automated UNCERTAIN Records

## Purpose and status

This is a separate, append-only manual-resolution layer for the six records
with `final_decision=UNCERTAIN` in the canonical automated full-text-section
screening run. It does not edit or replace the model outputs, prompts, raw
responses, schemas, or deterministic gate results. The review lead inspected
the cited full Docling markdown evidence and confirmed the decisions below on
2026-07-10.

The automated run remains reproducible as `50 INCLUDE`, `165 EXCLUDE`, and
`6 UNCERTAIN`. Applying only the six confirmed manual resolutions gives the
current full-text eligibility checkpoint of `52 INCLUDE`, `169 EXCLUDE`, and
`0 UNCERTAIN` among the 221 records that entered targeted full-text-section
screening.

## Resolution table

| Record | Title | Automated result | Confirmed manual result | Reason and Docling evidence |
|---|---|---|---|---|
| `full_2026-07-06__rec_001735` | Learning from Gene Names, Expression Values and Images: Contrastive Masked Text-Image Pretraining for Spatial Transcriptomics Representation Learning | `UNCERTAIN` | `EXCLUDE (EC3_not_generative)` | `Method > Overall Pipeline of CoMTIP`, `Masked Feature Modeling`, and `Objective Functions` describe contrastive image--gene-sentence alignment plus reconstruction of masked image features. The paper does not describe generation of text or biological data by the candidate model. Pure contrastive/masked representation learning does not meet IC3. |
| `full_2026-07-06__rec_001218` | Any-to-Any Learning in Computational Pathology via Triplet Multimodal Pretraining | `UNCERTAIN` | `INCLUDE` | `3.1 Problem Formulation` defines serialized WSI, gene-expression, and diagnostic-report inputs `(H,G,T)`. `4.1 Datasets and Tasks` explicitly evaluates `h. -> t.` report generation, and the Results report BLEU, METEOR, and ROUGE-L. This establishes a central text-bio bridge and generated text output in a tri-modal pretrained model. The automated `data_source` selection was a non-informative `7 Conclusion` section, but the full Docling source resolves the case. |
| `full_2026-07-06__rec_003258` | Foundation model for biomedical graphs: Integrating knowledge graphs and protein structures to large language models | `UNCERTAIN` | `EXCLUDE (EC4_no_foundation_model_evidence)` | The full source repeatedly states future intent: `2.4 Graph Encoder` says "I plan to train" and `2.5 Foundation Model for Biomedical Graphs` says alignment "will be implemented". `4 Conclusion` identifies the document as a proposal. The preliminary experiment evaluates only medical LLMs, not the proposed multimodal graph model. |
| `full_2026-07-06__rec_000129` | Genos: a human-centric genomic foundation model | `UNCERTAIN` | `EXCLUDE (EC2_no_text_component)` | `Method > Data collection and preprocessing` describes one-hot nucleotide inputs only. The only natural-language evidence occurs in the downstream `Text-genome model fusion case`, which follows an external Bioreason architecture, fine-tunes Qwen/021 text models, and freezes the Genos DNA model. That downstream fusion does not make the primary Genos candidate a substantive text-bio model. |
| `june_update_2026-06-10__rec_000152` | H2O: A Foundation Model Bridging Histopathology to Spatial Multi-Omics Profiling | `UNCERTAIN` | `INCLUDE` | `Methods > Model Training` integrates a ViT with fine-tuned scGPT gene-token representations and aligns the modalities. `Methods > Training objective > Concatenation and decoder` explicitly uses a 3-layer MLP decoder to decode the fused representation to the high-variable-gene space and the paper evaluates expression generation. Gene-token generative models are in scope under IC2. This decisive decoder section was outside the two Graph-selected input sections used by the automated run. |
| `full_2026-07-06__rec_001833` | Generation of Multimodal Longitudinal Synthetic Data By Artificial Intelligence to Improve Personalized Medicine in Hematology | `UNCERTAIN` | `EXCLUDE (application_wrapper)` | The poster abstract describes a pipeline assembled from conditional GAN, Tabular-VAE, Tabular-GPT, a fine-tuned LLM, Stable Diffusion, and CLIP. It does not present one new text-bio foundation-model architecture or an explicit natural-language conditioning bridge. It is therefore a wrapper pipeline rather than an in-scope primary candidate model. |

## Evidence sources and reproducibility

The stable automatic record IDs above link this layer to:

- `final_screening_results.json` for the original automated decision;
- `scope_reviewer.jsonl`, `architecture_reviewer.jsonl`, and `adjudicator.jsonl`
  for the role outputs that led to `UNCERTAIN`;
- the corresponding public Docling Graph `screening_evidence_summary.json` for
  Graph provenance and initial selected-section headings; and
- the local Docling markdown path recorded in each final record for the
  additional full-document section inspection.

The raw Docling markdown is intentionally not duplicated here. The public
Graph summaries and the explicit headings/claims above make the manual
resolution inspectable without changing the original execution logs.

## Scope of the manual layer

This is an eligibility-resolution checkpoint, not a new model run. It changes
only the six previously unresolved records. It does not claim that all 52
current INCLUDE records have completed downstream data extraction, duplicate
linking, or manuscript-level synthesis.
