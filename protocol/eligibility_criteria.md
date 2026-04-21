# Eligibility Criteria

## PICO Framework

| Element | Definition |
|---------|-----------|
| **Population** | Biological datasets — single-cell or bulk omics data (any species, any tissue, any modality) |
| **Intervention** | Foundation models that combine text modality (natural language or gene tokens) with biological data modality; must be generative (not encoder-only) |
| **Comparator** | Single-modality foundation models (scBERT, Geneformer), traditional integration methods (MultiVI, GLUE), or non-FM methods |
| **Outcome** | Cross-modal capabilities (text-to-cell, cell-to-text), downstream task performance (cell type annotation, perturbation prediction, gene function), generation quality |

---

## Inclusion Criteria

### IC1 — Biological data modality
The model works with at least one biological data modality:
- Gene expression (scRNA-seq, bulk RNA-seq)
- Chromatin accessibility (scATAC-seq, ATAC-seq)
- Surface proteins (CITE-seq, REAP-seq)
- Spatial data (spatial transcriptomics: Visium, MERFISH, Slide-seq)
- DNA methylation (scBS-seq, WGBS)
- Epigenomics
- Other omics (proteomics, metabolomics)

*Note*: Not limited to single-cell resolution. Models working with bulk data are also in scope.

### IC2 — Text modality with a substantive role (REQUIRED)
The model must incorporate a text/language component in a way that is
substantive to the model itself, not merely borrowed as an auxiliary feature.

In-scope patterns include:
- **Natural language**: cell type descriptions, gene annotations, prompts, text generation
- **Gene tokens**: gene identifiers processed as token sequences in a generative language-model style
- **Joint text-bio modeling**: explicit text-to-bio, bio-to-text, or aligned cross-modal modeling
- **Biological-token generative exception**: gene-token generative models explicitly treated as in scope by protocol decision

Not sufficient on their own:
- using embeddings, prompts, metadata descriptions, or outputs from an existing
  external LLM only as side information for a downstream bio task
- citing a pretrained language model as a feature extractor without a genuine
  text-bio modeling contribution
- generic tokenizer changes without evidence of a substantive text/language role

The key criterion is not the mere presence of a language artifact. The key
criterion is a **substantive text/language role in a model that also works with
biological data**.

### IC3 — Generative architecture
The model has clear generative capability:
- Decoder-only (GPT-style, autoregressive)
- Encoder-decoder (seq2seq, VAE with decoder)
- Diffusion-based language models
- CLIP-style only if paired with an explicit generative component

Not sufficient:
- pure contrastive alignment without generation
- predictive profile/score models that do not actually generate
- wrapper pipelines that call an existing generative model without contributing a
  new in-scope generative model architecture

**Excluded architectures**: Pure encoder-only models (BERT-style masked language
models without generation capability).

*Note*: Encoder-only models (scBERT, Geneformer, scFoundation) are excluded from the primary analysis but will be listed in a supplementary "related but excluded" table.

### IC4 — Foundation model characteristics
The model exhibits at least one FM characteristic as part of the candidate
model itself:
- Large-scale pretraining on substantial data (self-supervised, contrastive, or generative)
- Transferable representations applicable to unseen datasets/tasks
- Transformer, attention-based, or large neural network architecture designed for broad applicability

Not sufficient:
- a small supervised model trained only on a narrow labeled dataset
- a downstream application that merely uses an existing pretrained model as a
  frozen feature extractor
- simple concatenation or wrapper logic without evidence of broad transferable
  model behavior

### IC5 — Publication type
- Peer-reviewed journal articles
- Peer-reviewed conference papers (NeurIPS, ICML, ICLR, AAAI, RECOMB, ISMB, etc.)
- Preprints (bioRxiv, medRxiv, arXiv) — included due to rapid pace of field

### IC6 — Date range
Published or posted between **January 1, 2018** and **December 31, 2026** (search date).

### IC7 — Language
English only.

### IC8 — Access
Open Access only (full text must be freely accessible).

---

## Exclusion Criteria

### EC1 — No biological data modality
Studies that do not work with any biological data. Pure NLP/LLM studies without biology component.

### EC2 — No text/language component
Models that process only biological modalities without any text/language integration. This excludes:
- Bio-only multi-modal integration (e.g., MultiVI for RNA+ATAC without text)
- Expression-only foundation models without language component
- Traditional statistical integration (CCA, MNN, Seurat WNN)

This criterion also excludes cases where language artifacts are present only as
incidental or borrowed side features without a substantive text/language role
in the candidate model.

### EC3 — Encoder-only architecture
Pure encoder-only models without generative capability:
- Masked language models trained on gene expression (scBERT, Geneformer, scFoundation, UCE, GeneCompass)
- Metric learning models (SCimilarity)

These are listed in the supplementary "related but excluded" table.

### EC4 — No foundation model component
Studies that combine text and biology but lack FM characteristics:
- Simple concatenation or wrapper pipelines
- Supervised-only classifiers trained on small labeled datasets
- Rule-based text mining without learned representations
- applications that use an existing LLM or protein/gene LM only as an external
  feature extractor without presenting a new in-scope model

### EC5 — Non-computational
Purely experimental/wet-lab studies without a computational modeling contribution.

### EC6 — Non-scholarly sources
Editorials, news articles, blog posts, tutorials, software documentation.

### EC7 — Review articles
Systematic reviews, narrative reviews, meta-analyses, opinion pieces. Used in Step 0 but excluded from primary inclusion.

### EC8 — Duplicate publications
Earlier versions of the same model/paper (keep the most recent or peer-reviewed version).

---

## Screening Decision Tree

```
1. Does it work with biological data (omics, expression, genomics)?
   NO  -> EXCLUDE (EC1)
   YES -> continue

2. Does it have a substantive text/language component as part of the candidate model?
   NO  -> EXCLUDE (EC2), note in supplementary if multi-modal bio FM
   YES -> continue

3. Is there a substantive text-bio bridge rather than a wrapper around an existing model?
   NO  -> EXCLUDE (EC2/EC4)
   YES -> continue

4. Is the architecture generative (decoder, autoregressive, VAE, encoder-decoder)?
   NO (encoder-only)  -> EXCLUDE (EC3), note in supplementary "related but excluded"
   YES -> continue

5. Does it have FM characteristics (pretraining, transferable, large architecture)?
   NO  -> EXCLUDE (EC4)
   YES -> continue

6. Is it a primary research article/preprint (not a review)?
   NO  -> EXCLUDE (EC6/EC7)
   YES -> continue

7. Is it in English?
   NO  -> EXCLUDE (IC7)
   YES -> continue

8. Is it Open Access?
   NO  -> EXCLUDE (IC8)
   YES -> INCLUDE
```

---

## Resolved Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Date range | 2018-2026 | Captures precursors; first scFM ~2022, LLM+bio models from ~2023 |
| Preprints | Include | Many cutting-edge models are preprint-only |
| Open Access | OA only | Ensures full-text analysis; aligns with reproducibility |
| Conferences | Include | NeurIPS, ICML papers are key venues |
| Language | English only | Standard for computational biology reviews |
| Species | No restriction | Multi-species models are relevant |
| Single-cell vs bulk | Both in scope | Key criterion is text+bio combination, not resolution |
| Gene tokens as text | In scope | LLM on gene token sequences (scGPT, tGPT) counts as text modality |
| External LLM as side feature | Out of scope | Auxiliary LLM embeddings/prompts alone do not satisfy IC2/IC4 |
| Wrapper around existing FM | Out of scope | Application wrappers are not primary candidate model papers |
| Encoder-only FMs | Excluded from primary | scBERT, Geneformer -> supplementary table |
| Bio-only multi-modal | Excluded | MultiVI, totalVI lack text component |
| Pure VAE/diffusion without language | Excluded | No text modality = out of scope |
| CLIP-style models | Conditionally included | Must bridge text and bio and have a substantive generative component |
