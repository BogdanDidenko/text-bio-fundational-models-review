# Screening Benchmark And Tiered IC2 Operationalization

## Purpose

This note operationalizes the current review scope for title/abstract screening.
It does **not** replace `protocol/eligibility_criteria.md`.
Instead, it clarifies how to apply the existing criteria consistently in LLM-assisted screening and how to build a manual benchmark set.

Key principle:
- `ground_truth_models.md` is a **must-include recall anchor**, not a full definition of scope.
- The actual scope is defined by `protocol/eligibility_criteria.md`.
- The benchmark must therefore contain:
  - papers that definitely must be included,
  - papers that definitely must be excluded for different reasons,
  - papers that are genuinely borderline at title/abstract stage.

---

## Task Interpretation

The review is about:
- **foundation models**
- with **biological data modality**
- with a **text/language component**
- with **generative capability**
- in **primary research or preprints**

This means the screening task is **not**:
- "find all biology papers that mention LLMs"
- "find all omics foundation models"
- "find all biological sequence language models"
- "find all papers that evaluate or apply existing LLMs in biology"

The target is narrower:
- generative foundation models that bridge text and biological data,
- plus the explicit protocol exception that **biological-token generative decoder models** may be in scope, with gene-token models as the clearest existing examples.

---

## Operational Screening Order

For title/abstract screening, the most reliable order is:

1. `Paper type`
- Is this a primary model paper/preprint, or a review/benchmark/resource/application paper?

2. `Biological modality`
- Does the paper actually use biological data, not just biomedical text?

3. `Text/language component`
- Does it contain a true text/language bridge under the protocol?

4. `Architecture type`
- Is it generative, or is it encoder-only / representation-only?

5. `Foundation-model evidence`
- Is there real FM-style pretraining / transfer / broad reusable architecture?

6. `Administrative filters`
- English, date range, OA, duplicates.

This order is important because many false positives happen when the model sees "LLM" or "transformer" early and jumps to INCLUDE before confirming paper type or architecture.

---

## IC2 Tier System

The current IC2 is too broad for screening.
For operational use, it should be split into three tiers.

### Tier A — Explicit Text-Biology Bridge

Tier A is the clearest in-scope category.
These papers should usually be `INCLUDE` if IC1, IC3, IC4, and publication filters are also satisfied.

Typical signals:
- natural-language prompts or descriptions are inputs to the biological model
- the model generates natural-language outputs from biological data
- text-to-cell / cell-to-text tasks
- cross-modal retrieval between text and omics/cells
- CLIP-style alignment where one modality is natural language
- LLM agents grounded in biological data or biological tools as a core modeling contribution

Examples:
- LangCell
- ChatCell
- CellWhisperer
- GeneGPT
- EpiAgent
- PathOmCLIP

What counts:
- explicit natural language on at least one side of the bridge
- not just metadata strings incidentally attached to data

What does **not** count automatically:
- using an external LLM only to paraphrase labels or generate descriptions for a downstream classifier
- prompting ChatGPT to analyze biology without a genuine model bridge

### Tier B — Biological-Token Generative Exception

Tier B is the explicit protocol exception.
These papers are in scope even when there is little or no natural-language interaction.

Definition:
- biological entities from a real biological modality are treated as tokens or token-like units
- the model is clearly **generative**
- the architecture is GPT-like / decoder-only / autoregressive / other genuine generative sequence model
- the paper is positioned as a foundation model for broad downstream transfer

Examples:
- scGPT
- tGPT
- likely similar decoder-style biological-token FM papers

Interpretation:
- genes are the clearest current examples because the protocol explicitly names `scGPT` and `tGPT`
- but the underlying logic is broader than genes alone
- if another biological modality is discretized/tokenized and modeled with a genuine generative LM-style decoder, it can belong to Tier B under the same logic
- this does **not** mean that any tokenized biology paper is in scope

This tier should be treated as:
- `INCLUDE per protocol`
- but tracked separately in analysis as `biological-token generative`

Important boundary:
- Tier B is **not** "any biology sequence model"
- it is also **not** "any model that tokenizes biology"
- tokenization alone is insufficient; the model must still satisfy IC3 and IC4
- encoder-only token models remain out of scope
- wrappers that merely transform modality features into token-like inputs without a genuine generative FM contribution remain out of scope

### Tier C — Not Sufficient For IC2

Tier C covers papers that mention language-model ideas or tokenization, but do **not** satisfy the review's text/language criterion in an operational sense.

This tier should usually end in `EXCLUDE` or `UNCERTAIN`, depending on the abstract.

Typical cases:
- encoder-only gene-token models
- biological sequence LMs without a text-bio bridge relevant to this review question
- bio-only multimodal models
- wrappers that use LLM embeddings as side information
- prompt-based use of an external LLM without a new model bridge
- papers where "language model" is only a borrowed technique label

Examples:
- scBERT / Geneformer / scFoundation / UCE
- MultiVI / totalVI
- wrapper-style papers that embed labels or metadata with an LLM

Operational rule:
- Tier C does **not** satisfy IC2 by itself.

---

## How Tiering Maps To Decisions

### Clear INCLUDE

A paper should be `INCLUDE` when:
- IC1 is satisfied,
- IC2 is Tier A or Tier B,
- IC3 generative architecture is supported,
- IC4 FM characteristics are supported,
- paper type is primary research/preprint,
- and no administrative exclusion applies.

### Clear EXCLUDE

A paper should be `EXCLUDE` when:
- no biological data (`EC1`)
- no true text/language bridge and no Tier B exception (`EC2`)
- encoder-only / non-generative (`EC3`)
- no FM component / wrapper / narrow supervised model (`EC4`)
- review/editorial/tutorial (`EC6` or `EC7`)
- duplicate / non-English / non-OA as applicable

### UNCERTAIN

A paper should be `UNCERTAIN` when:
- the abstract suggests Tier A or Tier B but architecture is unclear
- the paper may be a wrapper around an external LLM rather than a new in-scope model
- the abstract uses vague words like "generator" or "LLM-based" without enough architectural detail
- paper type is unclear from abstract alone

Example:
- `scELMo` is a good borderline case because it mentions LLM generation of metadata descriptions and embeddings, but the abstract does not cleanly establish whether the core biological model is an in-scope generative FM or a wrapper pipeline.

---

## Exclusion Classes That Need Sharper Treatment

The current EC1-EC8 are useful, but title/abstract screening would benefit from one more operational distinction.

### Recommended addition: Benchmark / Evaluation / Resource papers

Current problem:
- papers like `GeneTuring` or `DART-Eval` are usually correctly excluded,
  but the existing EC set does not give them a natural home.
- they are not reviews in the classic sense,
  but they are also not candidate model papers for primary inclusion.

Recommended operational addition:
- `EC9: benchmark / evaluation / resource paper, not a candidate model paper`

If the protocol should remain unchanged formally, the screening layer can still use this as an **internal operational tag**, then map it back to a protocol-compatible exclusion family during reporting.

---

## Manual Benchmark Set Design

The benchmark should be small enough for careful manual review but broad enough to stress the decision boundaries.

Recommended size:
- `36-48` papers

### Split 1 — Clear Positives

#### P1. Tier A positives
- `10-12` papers
- explicit text-bio bridge

Examples to include:
- LangCell
- ChatCell
- CellWhisperer
- GeneGPT
- EpiAgent
- PathOmCLIP
- additional true positives discovered in the corpus

Goal:
- ensure the prompt does not become too conservative and miss real cross-modal text-bio model papers

#### P2. Tier B positives
- `6-8` papers
- gene-token generative decoder exception

Examples:
- scGPT
- tGPT
- CellPLM if confirmed in-scope under the protocol
- Nicheformer if confirmed in-scope under the protocol

Goal:
- ensure recall on the explicit protocol exception

### Split 2 — Clear Negatives

#### N1. Review / editorial / perspective
- `4-6` papers

Goal:
- verify early exclusion of non-primary literature

#### N2. Bio-only multimodal or omics-only papers
- `4-6` papers

Examples:
- MultiVI-style
- spatial + histology integration without language
- general multiomics fusion papers

Goal:
- enforce EC2 cleanly

#### N3. Encoder-only biology FMs
- `4-6` papers

Examples:
- scBERT
- Geneformer
- scFoundation
- UCE

Goal:
- enforce EC3 reliably

#### N4. Wrapper / application / narrow predictive pipelines
- `4-6` papers

Examples:
- papers using external LLM embeddings as auxiliary features
- disease prediction pipelines with no genuine FM contribution
- "apply ChatGPT to biology" papers

Goal:
- enforce EC4 and the Tier C boundary

#### N5. Benchmark / evaluation / resource papers
- `3-5` papers

Examples:
- GeneTuring
- DART-Eval
- similar benchmarking suites

Goal:
- prevent benchmark papers from being mistaken as primary model papers

### Split 3 — Borderline Cases

#### B1. Wrapper-like LLM metadata fusion
- `3-4` papers
- e.g. `scELMo`-type papers

#### B2. Ambiguous architecture
- `3-4` papers
- abstract says "transformer-based" or "foundation model" but does not say decoder/autoregressive/generative

#### B3. Ambiguous paper type
- `2-3` papers
- model/resource/application boundaries unclear

Goal:
- test whether `UNCERTAIN` is used appropriately instead of overconfident INCLUDE/EXCLUDE

---

## Benchmark Annotation Schema

Each benchmark paper should have manual labels for:

- `paper_id`
- `title`
- `year`
- `expected_decision`
- `expected_primary_code`
- `paper_type`
- `bio_modality_present`
- `ic2_tier`
- `generative_status`
- `fm_status`
- `why_borderline`
- `notes`

Recommended values:

- `paper_type`:
  - `primary_model`
  - `benchmark_resource`
  - `review`
  - `application_wrapper`
  - `other`

- `ic2_tier`:
  - `A`
  - `B`
  - `C`
  - `unclear`

- `generative_status`:
  - `generative`
  - `encoder_only`
  - `non_generative`
  - `unclear`

- `fm_status`:
  - `yes`
  - `no`
  - `unclear`

This is more informative than only storing `INCLUDE / EXCLUDE / UNCERTAIN`.

---

## LatteReview Pipeline Recommendations

The current pipeline is technically viable, but the reviewer schema should become more structured.

### Current weakness

A single scalar-like judgment tends to collapse several distinct questions:
- paper type
- modality
- text bridge
- architecture
- FM evidence

This makes reasoning brittle and harder to audit.

### Recommended review schema

For each reviewer, request structured output with:

- `paper_type`
- `bio_modality_present`
- `text_bridge_tier`
- `generative_evidence`
- `foundation_model_evidence`
- `primary_exclusion_code`
- `final_decision`
- `rationale`

### Recommended round structure

Round A:
- `Scope reviewer`
  - paper type, modality, text bridge
- `Architecture reviewer`
  - generative vs encoder-only vs wrapper, FM evidence

Round B:
- `Adjudicator`
  - only on disagreements or `UNCERTAIN`

This should reduce spurious confidence and make error analysis easier.

---

## Immediate Next Actions

1. Build a curated manual benchmark set of `36-48` papers using the split above.
2. Label each paper with the structured annotation schema.
3. Update the screening prompt to use Tier A/B/C explicitly.
4. Update LatteReview reviewer outputs from a single decision to structured fields.
5. Re-run a small benchmark-first pilot before scaling back to large-batch screening.

---

## Summary

The core clarification is:
- `Tier A` = explicit natural-language <-> biology bridge
- `Tier B` = biological-token generative decoder exception included per protocol
- `Tier C` = language-adjacent but not sufficient for IC2

The benchmark must reflect the full screening task, not only recall anchors.
That means the benchmark must intentionally contain:
- must-include positives,
- encoder-only negatives,
- bio-only negatives,
- benchmark/resource papers,
- wrapper/application papers,
- and real borderline cases.
