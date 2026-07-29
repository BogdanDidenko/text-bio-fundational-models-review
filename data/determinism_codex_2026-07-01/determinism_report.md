# Codex Screening Determinism Check

Created: 2026-07-01T04:05:48

Input: `data/determinism_codex_2026-07-01/input_random20_seed20260701.json`

Protocol: same `scripts/run_codex_screening_pipeline.py` used for the 2026-06-10 package; model `gpt-5.4-mini`; batch size 8; adjudicator batch size 6; max workers 1.

## Run summaries

| Run | Decision counts | Adjudication queue | Adjudicated |
|---|---:|---:|---:|
| run_1 | `{'EXCLUDE': 18, 'UNCERTAIN': 2}` | 11 | 11 |
| run_2 | `{'EXCLUDE': 19, 'UNCERTAIN': 1}` | 8 | 8 |
| run_3 | `{'EXCLUDE': 18, 'UNCERTAIN': 2}` | 11 | 11 |

## Agreement

- Stable `final_decision`: 18/20 (90.0%)
- Stable full tuple (`final_decision`, `final_code`, `uncertainty_reason`, `final_source`): 5/20 (25.0%)
- Unstable final decision record IDs: rec_000004, rec_000017
- Any compared-field instability record IDs: rec_000001, rec_000003, rec_000004, rec_000006, rec_000007, rec_000008, rec_000010, rec_000011, rec_000012, rec_000013, rec_000014, rec_000016, rec_000017, rec_000018, rec_000020

## Record-level final decisions

| Record | Cluster | Title short | Run 1 | Run 2 | Run 3 | Stable decision | Stable full tuple |
|---|---:|---|---|---|---|---:|---:|
| rec_000001 | 4086 | Prompt-based bioinformatic pipeline generation for a multi-step metaviral workflow | EXCLUDE / application_wrapper / adjudicator | EXCLUDE / application_wrapper / python_gate | EXCLUDE / application_wrapper / adjudicator | True | False |
| rec_000002 | 1175 | Multimodal random subspace for breast cancer molecular subtypes prediction by integrati... | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / python_gate | True | True |
| rec_000003 | 2680 | Generative pretraining from large-scale transcriptomes: Implications for single-cell de... | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_substantive_text_bio_bridge / python_gate | EXCLUDE / EC2_no_text_component / python_gate | True | False |
| rec_000004 | 4057 | DestinyNet: A deep-learning framework for cell-fate analysis from lineage-tracing singl... | EXCLUDE / EC2_no_text_component / adjudicator | EXCLUDE / EC2_no_text_component / adjudicator | UNCERTAIN / none / adjudicator | False | False |
| rec_000005 | 3759 | TRAILBLAZER: generative multicellular perturbation model of biology | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / python_gate | True | True |
| rec_000006 | 34 | STAG-LLM: Predicting TCR-pHLA binding with protein language models and computationally ... | EXCLUDE / EC3_not_generative / adjudicator | EXCLUDE / EC2_no_substantive_text_bio_bridge / python_gate | EXCLUDE / EC2_no_text_component / adjudicator | True | False |
| rec_000007 | 613 | Translating cancer genomics into precision medicine with artificial intelligence: appli... | EXCLUDE / review_editorial / python_gate | EXCLUDE / review_editorial / python_gate | EXCLUDE / review_editorial / adjudicator | True | False |
| rec_000008 | 487 | Integrative Multiscale Biochemical Mapping of the Brain via Deep-Learning-Enhanced High... | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / adjudicator | True | False |
| rec_000009 | 2520 | scMGCL: accurate and efficient integration representation of single-cell multi-omics data | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / python_gate | True | True |
| rec_000010 | 305 | A multi-modal transformer for cell type-agnostic regulatory predictions. | EXCLUDE / EC2_no_text_component / adjudicator | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / python_gate | True | False |
| rec_000011 | 3285 | Large language models in genomics—a perspective on personalized medicine | EXCLUDE / review_editorial / adjudicator | EXCLUDE / review_editorial / adjudicator | EXCLUDE / review_editorial / python_gate | True | False |
| rec_000012 | 1056 | Novel research and future prospects of artificial intelligence in cancer diagnosis and ... | EXCLUDE / review_editorial / adjudicator | EXCLUDE / review_editorial / adjudicator | EXCLUDE / review_editorial / python_gate | True | False |
| rec_000013 | 3388 | Biomedical data and AI | UNCERTAIN / none / adjudicator | UNCERTAIN / none / adjudicator | UNCERTAIN / none / adjudicator | True | False |
| rec_000014 | 188 | CART-GPT: A T Cell-Informed AI Linguistic Framework for Interpreting Neurotoxicity and ... | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / EC2_no_text_component / adjudicator | EXCLUDE / EC2_no_text_component / python_gate | True | False |
| rec_000015 | 2464 | CellOntologyMapper: Consensus mapping of cell type annotation | EXCLUDE / application_wrapper / python_gate | EXCLUDE / application_wrapper / python_gate | EXCLUDE / application_wrapper / python_gate | True | True |
| rec_000016 | 4209 | Chromatin unwinding state for in situ identification and lineage tracing of circulating... | EXCLUDE / EC2_no_text_component / adjudicator | EXCLUDE / EC2_no_text_component / python_gate | EXCLUDE / review_editorial / adjudicator | True | False |
| rec_000017 | 1775 | Evaluating the Effectiveness of Parameter-Efficient Fine-Tuning in Genomic Classificati... | UNCERTAIN / none / adjudicator | EXCLUDE / application_wrapper / adjudicator | EXCLUDE / EC3_not_generative / adjudicator | False | False |
| rec_000018 | 1193 | IMG-33. Unveiling glioblastoma heterogeneity with deep learning derived MRI subtyping: ... | EXCLUDE / EC2_no_text_component / adjudicator | EXCLUDE / EC2_no_text_component / adjudicator | EXCLUDE / EC2_no_text_component / adjudicator | True | False |
| rec_000019 | 2380 | Automated machine learning with interpretation: A systematic review of methodologies an... | EXCLUDE / review_editorial / adjudicator | EXCLUDE / review_editorial / adjudicator | EXCLUDE / review_editorial / adjudicator | True | True |
| rec_000020 | 1072 | Protein Structure Prediction: Challenges, Advances, and the Shift of Research Paradigms | EXCLUDE / review_editorial / python_gate | EXCLUDE / review_editorial / python_gate | EXCLUDE / review_editorial / adjudicator | True | False |

Detailed CSV: `data/determinism_codex_2026-07-01/determinism_record_diff.csv`
