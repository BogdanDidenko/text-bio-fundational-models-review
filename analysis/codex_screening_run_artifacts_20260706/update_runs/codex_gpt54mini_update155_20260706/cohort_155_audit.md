# July 2026 Update Cohort Audit

Created: `2026-07-06T20:26:56`

This file reconciles the 155 unique records from `data/dedup_update_2026-07-06/deduplicated_records.json` with the title/abstract screening run.

## Summary

- Update-unique records: **155**
- New title/abstract records screened now: **119**
- Already present in master/full rerun: **21**
- Not screened because abstract is empty: **15**
- New screened decisions: **{'EXCLUDE': 113, 'INCLUDE': 6}**

## INCLUDE from new screened records

- `rec_000046` / cluster `66`: HoloCell: A Generative Foundation Model for Holistic Cellular Modeling
  - DOI: `10.64898/2026.06.07.730684`; source: `python_gate`
  - Rationale: All first-pass criteria were positive without unresolved uncertainty.
- `rec_000050` / cluster `70`: How Post-Training Shapes Biological Reasoning Models
  - DOI: ``; source: `python_gate`
  - Rationale: All first-pass criteria were positive without unresolved uncertainty.
- `rec_000060` / cluster `81`: CellTosg2Sequence: A Unified Text-Omics-Signaling-Graph Large Language Model for Single-Cell Analysis
  - DOI: `10.64898/2026.06.16.732397`; source: `python_gate`
  - Rationale: All first-pass criteria were positive without unresolved uncertainty.
- `rec_000073` / cluster `96`: Generating antimicrobial peptides via genomic transfer learning
  - DOI: `10.64898/2026.06.16.732639`; source: `python_gate`
  - Rationale: All first-pass criteria were positive without unresolved uncertainty.
- `rec_000074` / cluster `98`: CellOS: Learning a World Model of Cellular State through Joint Embedding Prediction
  - DOI: `10.64898/2026.06.18.733163`; source: `python_gate`
  - Rationale: All first-pass criteria were positive without unresolved uncertainty.
- `rec_000085` / cluster `111`: DNA Language Models: An Assessment of Pre-Training for Fine-Tuning Tasks
  - DOI: ``; source: `adjudicator`
  - Rationale: This is a primary study of DNA language models and pretraining for genomics fine-tuning tasks. The abstract explicitly references foundation models, LLMs, and BPE tokenization applied to genomic sequences.

## No-Abstract Records

- cluster `25`: Artificial intelligence in clinical oncology: Multimodal integration and translational development
  - DOI: `10.1016/j.canlet.2026.218493`
- cluster `28`: Sequence determinant and functional relevance of 8-oxoguanine RNA modification unveiled from foundation-model-based predictor
  - DOI: `10.1016/j.omtn.2026.102951`
- cluster `29`: Prediction of Lung Cancer Metastasis Risk Based on GCAVE-GAN Data Augmentation and Multimodal Feature Fusion
  - DOI: `10.3233/ATDE260373`
- cluster `30`: Redefining Pathobiology with Spatial Multi-Omics at the Intersection of Biology, Computation, and Histopathological Assessment
  - DOI: `10.1016/j.ajpath.2026.01.007`
- cluster `32`: Comprehensive RNA-binding protein analyses and deep learning uncover genetic constraints and disease associations in protein-RNA interfaces
  - DOI: `10.1016/j.cels.2026.101588`
- cluster `33`: Linear Attention and SSM Fusion for Long Sequence Modeling: An Innovative Framework Breaking the Complexity Bottleneck of Transformers
  - DOI: `10.3233/ATDE260340`
- cluster `45`: Artificial Intelligence in single-cell and spatial transcriptomics data analyses.
  - DOI: `10.1016/bs.pmbts.2026.01.011`
- cluster `54`: CD-Former: A Cross-modal Dual-interaction Transformer with Whole-Slide Image Pyramids and Genomics for Survival Prediction
  - DOI: `10.1109/tcsvt.2026.3672108`
- cluster `64`: Enhanced Multimodal Transformer for Treatment-Resistant Depression Prediction Using Synthetic fMRI, Genomic, and Clinical Data
  - DOI: `10.4236/oalib.1114447`
- cluster `65`: Mechanism-Aware Prediction of Tissue-Specific Drug Activity via Multi-Modal Biological Graphs
  - DOI: ``
- cluster `73`: Advances in Massive Parallel Sequencing: From Genomics to Spatial Transcriptomics.
  - DOI: `10.1007/978-3-032-18966-0_3`
- cluster `87`: A Visually Interpretable Histopathology-Based Immune Model Predicts T-effector Biology and Response to Immune checkpoint inhibition in Clear Cell Renal Cell Carcinoma Clinical Trial and Contemporary Real-World Datasets
  - DOI: `10.64898/2026.06.21.733614`
- cluster `120`: Artificial Intelligence in the prediction of 3D chromatin structure and gene regulation.
  - DOI: `10.1016/bs.pmbts.2026.01.018`
- cluster `127`: Multi-Modal Deep Learning-Based Model to Predict Burkitt Lymphoma Recurrence.
  - DOI: ``
- cluster `135`: Artificial intelligence in multi-omics analysis of small-molecule drug discovery.
  - DOI: `10.1016/bs.pmbts.2026.01.026`

## Already in Master

- cluster `7` -> master cluster `2790`, full record `rec_002619`: A transformer-based language model reveals developmental constraint and network complexity during zebrafish embryogenesis.
  - match: `Exact title match`; prior full-rerun decision: `EXCLUDE` / `EC4_no_foundation_model_evidence`
- cluster `16` -> master cluster `2574`, full record `rec_002410`: seqLens: Optimizing Language Models for Genomic Predictions.
  - match: `Exact title match`; prior full-rerun decision: `INCLUDE` / `none`
- cluster `19` -> master cluster `2151`, full record `rec_002011`: Unlocking precision diagnostics: A multimodal framework integrating metabolomics with advanced machine learning techniques.
  - match: `Exact title match`; prior full-rerun decision: `EXCLUDE` / `EC2_no_text_component`
- cluster `24` -> master cluster `2271`, full record `rec_002126`: Interpretable deep generative ensemble learning for single-cell omics with Hydra.
  - match: `Exact title match`; prior full-rerun decision: `EXCLUDE` / `EC2_no_text_component`
- cluster `26` -> master cluster `3806`, full record `rec_003612`: Leveraging Artificial Intelligence and Large Language Models for Cancer Immunotherapy
  - match: `Exact title match`; prior full-rerun decision: `EXCLUDE` / `review_editorial`
- cluster `27` -> master cluster `3764`, full record `rec_003571`: CLOP-DiT: Structured-metadata-conditioned single-cell latent generation via contrastive language-omics pretraining and Diffusion Transformers
  - match: `Exact title match`; prior full-rerun decision: `EXCLUDE` / `EC4_no_foundation_model_evidence`
- cluster `37` -> master cluster `659`, full record `rec_000651`: OsteoFGRNet: Osteopontin-Driven Expression Profiling for Early Fetal Growth Restriction Analysis
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `EC2_no_text_component`
- cluster `42` -> master cluster `1346`, full record `rec_001233`: GenoME: a MoE-based generative model for individualized, multimodal prediction and perturbation of genomic profiles
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `EC2_no_text_component`
- cluster `47` -> master cluster `647`, full record `rec_000643`: Harnessing deep learning for the discovery of latent patterns in multi-omics medical data
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `review_editorial`
- cluster `52` -> master cluster `3638`, full record `rec_003448`: AI for Scientific Discovery in Omics Data-Driven Precision Medicine.
  - match: `PMID match`; prior full-rerun decision: `UNCERTAIN` / `none`
- cluster `63` -> master cluster `3655`, full record `rec_003464`: A Systematic Literature Review of Generative AI Approaches for Synthetic Clinical Data Generation: Balancing Realism and Privacy
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `review_editorial`
- cluster `91` -> master cluster `3686`, full record `rec_003493`: Artificial Intelligence Approaches in Toxicology
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `review_editorial`
- cluster `97` -> master cluster `1266`, full record `rec_001155`: πDIA-CLIP: efficient identification of highly heterogeneous proteomics data via a generalized zero-shot framework
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `EC2_no_text_component`
- cluster `100` -> master cluster `2060`, full record `rec_001928`: Attention-Enhanced Hierarchical Transformer for Multimodal Integration of Mammograms and Clinical Data
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `EC2_no_text_component`
- cluster `106` -> master cluster `3708`, full record `rec_003515`: Whole-Slide Images as Predictive Biomarkers for Drug Response Using Transcriptomically Transferred Labels
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `EC2_no_text_component`
- cluster `112` -> master cluster `3718`, full record `rec_003525`: Artificial Intelligence Augmented Diagnostics In Clinical Microbiology: A Multimodal Evaluation Of Diagnostic Accuracy, Workflow Efficiency, And Antimicrobial Resistance Prediction.
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `application_wrapper`
- cluster `116` -> master cluster `3724`, full record `rec_003531`: MMBCSurv: Multimodal Breast Cancer Survival Prediction Integrating Histopathology Images and Multi-Omics Data via Dynamic Fusion
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `EC2_no_text_component`
- cluster `126` -> master cluster `3744`, full record `rec_003551`: A genomic approach to understanding common diseases in human populations
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `review_editorial`
- cluster `138` -> master cluster `632`, full record `rec_000630`: Artificial intelligence in bone biology: Transforming basic research into advanced therapeutics
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `review_editorial`
- cluster `141` -> master cluster `2715`, full record `rec_002545`: Sparse Autoencoders Reveal Interpretable Features in Single-Cell Foundation Models
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `EC2_no_text_component`
- cluster `147` -> master cluster `1493`, full record `rec_001374`: Artificial intelligence in nephrology: predicting CKD progression and personalizing treatment
  - match: `DOI match`; prior full-rerun decision: `EXCLUDE` / `review_editorial`
