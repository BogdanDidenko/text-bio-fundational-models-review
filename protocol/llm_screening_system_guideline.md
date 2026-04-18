# Guideline for Building the LLM-Assisted Screening System for This Review

## Purpose

This document gives a concrete recommendation for how to build the screening
system for this review of **text-bio foundational models**.

It is based on three methodological sources:

- [Trad et al. (2025) on LLM-assisted screening](https://doi.org/10.1186/s12874-025-02583-5), summarized locally in [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- [Holst et al. (2025) PRISMA-trAIce](https://doi.org/10.2196/80247), summarized locally in [jmir_prisma_trace_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)
- [Flemyng et al. (2025) Cochrane/Campbell/JBI/CEE position statement](https://doi.org/10.1002/14651858.ED000178), summarized locally in [cochrane_ai_position_statement_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/cochrane_ai_position_statement_2025_methodology.md)

The goal is not to invent a novel screening philosophy. The goal is to choose a
system design that is:

- methodologically defensible;
- conservative with respect to false exclusions;
- transparent enough to report properly;
- specific to the ambiguity structure of our review question.

---

## Executive Recommendation

The screening system for this review should be built as a:

- **criterion-by-criterion**
- **sensitivity-first**
- **human-supervised**
- **benchmark-validated**
- **fully logged**
title/abstract screening workflow.

It should **not** be built as:

- a one-shot `INCLUDE / EXCLUDE` classifier;
- an aggressive automatic exclusion engine;
- a full-text-first RAG pipeline;
- a loosely documented prompt hidden inside code.

### Why this is the recommended design

1. **BMC paper**: the strongest directly transferable design pattern is
   criterion-by-criterion screening with `yes / no / unsure`, where unsure cases
   are retained rather than excluded. This is the clearest empirical support for
   our pipeline architecture.
   Source:
   [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)

2. **PRISMA-trAIce**: the system must be designed so that prompts, versions,
   outputs, validation basis, and human-AI interaction can be reported and
   audited. This is the strongest support for version control, audit trail, and
   disagreement logging.
   Source:
   [jmir_prisma_trace_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)

3. **Cochrane position statement**: AI use in screening is acceptable only if
   it is justified, validated locally, and deployed under explicit human
   oversight. This is the strongest support for a benchmark gate and a formal
   safety case before live deployment.
   Source:
   [cochrane_ai_position_statement_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/cochrane_ai_position_statement_2025_methodology.md)

---

## 1. Primary Design Choice

### Recommendation

Build the system around **criterion-level questions**, not around a single
document-level label.

### Why

This is the most defensible choice for our task because our hard records are not
hard for the same reason. Failures arise from different dimensions:

- paper type;
- whether biological data are actually present;
- whether there is a real text component;
- whether the text-bio relation is substantive or superficial;
- whether the model is generative or encoder-only;
- whether the paper is foundational or a wrapper/application.

A one-shot label hides which dimension failed. A criterion-level design exposes
it.

### Source support

- BMC paper explicitly used questions identical to the human screening guide and
  required structured responses for each question.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- PRISMA-trAIce requires exact reporting of prompts, outputs, and how humans
  interacted with them, which is easier to satisfy with criterion-level output
  than with opaque free-form classification.
  Source:
  [jmir_prisma_trace_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)

---

## 2. Recommended Decision Schema

### Recommendation

The model should produce the following structured fields for each record:

1. `paper_type`
2. `bio_modality_present`
3. `text_component_present`
4. `text_bio_relation`
5. `architecture_type`
6. `foundation_model_evidence`
7. `final_decision`
8. `primary_exclusion_code`
9. `uncertainty_reason`
10. `decision_rationale`

### Recommended values

#### `paper_type`

- `primary_model_paper`
- `review_editorial`
- `benchmark_resource`
- `application_wrapper`
- `unclear`

#### `bio_modality_present`

- `yes`
- `no`
- `unclear`

#### `text_component_present`

- `yes`
- `no`
- `unclear`

#### `text_bio_relation`

- `explicit_natural_language_bridge`
- `biological_token_generative_case`
- `not_sufficient_for_scope`
- `unclear`

#### `architecture_type`

- `generative`
- `encoder_only`
- `wrapper_or_pipeline`
- `unclear`

#### `foundation_model_evidence`

- `yes`
- `no`
- `unclear`

#### `final_decision`

- `INCLUDE`
- `EXCLUDE`
- `UNCERTAIN`

### Why this schema is preferable

This schema is still specific to our domain, but it is closer to the best
practice supported by the literature than a tier-first design.

- It follows the BMC logic of screening by explicit criteria.
- It preserves `UNCERTAIN` as a real state.
- It avoids making `Tier A / B / C` the center of the whole system.
- It allows us to keep our special protocol exception for biological-token
  generative models without forcing the whole pipeline to speak in tiers.

### Source support

- BMC supports question-by-question screening and explicit `unsure`.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- Cochrane supports explicit justification and oversight for any
  judgment-bearing AI outputs.
  Source:
  [cochrane_ai_position_statement_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/cochrane_ai_position_statement_2025_methodology.md)

---

## 3. Role of `Tier A / Tier B / Tier C`

### Recommendation

Do **not** make `Tier A / Tier B / Tier C` the main public architecture of the
screening system.

If needed, keep them only as an **internal interpretation aid** for the single
field `text_bio_relation`.

### Why

The tier formulation was a useful internal attempt to sharpen IC2, but it is
not grounded as a standard in the literature.

- The articles do not present screening as a tier taxonomy.
- BMC-style question design is better supported than tier-first design.
- A tier-first system risks becoming idiosyncratic and harder to justify to
  outside reviewers.

### Source support

- BMC paper argues for criterion-level screening and `unsure`, not tier labels.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- PRISMA-trAIce supports transparent task-specific operationalization, but does
  not prescribe any tier taxonomy.
  Source:
  [jmir_prisma_trace_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)

---

## 4. Recommended Uncertainty Policy

### Recommendation

`UNCERTAIN` must be a deliberate screening state, not a failure state.

Any record should become `UNCERTAIN` if:

- architecture cannot be resolved from the abstract;
- the text-bio relation is unclear;
- the paper may be benchmark/resource/application rather than a candidate model
  paper;
- the abstract is too short or too vague to resolve a key criterion;
- the two reviewers disagree materially.

### Operational consequence

`UNCERTAIN` means:

- retain the record;
- route it to manual review or adjudication;
- log why it was uncertain.

### Why

For our task, many hard cases are not clean negatives. The conservative system
must distinguish "not in scope" from "not resolvable at title/abstract stage."

### Source support

- BMC: uncertain records are retained rather than excluded; this is the clearest
  empirical support for our policy.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- Cochrane: human oversight must be strongest where judgment risk is high.
  Source:
  [cochrane_ai_position_statement_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/cochrane_ai_position_statement_2025_methodology.md)

---

## 5. Recommended Reviewer Topology

### Recommendation

Use a **two-reviewer plus adjudicator** topology:

1. `Scope reviewer`
2. `Architecture reviewer`
3. `Adjudicator`

### Reviewer responsibilities

#### Scope reviewer

Responsible for:

- `paper_type`
- `bio_modality_present`
- `text_component_present`
- `text_bio_relation`

#### Architecture reviewer

Responsible for:

- `architecture_type`
- `foundation_model_evidence`
- whether the work looks like a wrapper/application rather than a model paper

#### Adjudicator

Responsible only for:

- disagreements;
- high-ambiguity cases;
- cases where the exclusion logic conflicts across criteria.

### Why

Our failure modes split naturally into:

- scope failures;
- architecture/FM failures.

This topology maps to that structure better than one general reviewer.

### Source support

- BMC supports criterion-level decomposition and explicit handling of uncertainty.
  The paper does not prescribe multi-agent topology, but this topology is a
  direct extension of its criterion-first logic.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- PRISMA-trAIce requires explicit reporting of human-AI interaction and
  discrepancy handling, which is easier to satisfy with clearly differentiated
  reviewer roles.
  Source:
  [jmir_prisma_trace_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)

---

## 6. Recommended Aggregation Rule

### Recommendation

Use a conservative aggregation rule:

- both reviewers support inclusion on compatible grounds -> `INCLUDE`
- both reviewers support exclusion on compatible grounds -> `EXCLUDE`
- disagreement or weak evidence -> `UNCERTAIN` or adjudication

### Why

The system should only exclude when the exclusion path is criterion-specific and
stable. Any cross-criterion conflict should preserve recall.

### Source support

- BMC supports conservative retention of uncertain cases.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- Cochrane supports conservative oversight when the cost of error is high.
  Source:
  [cochrane_ai_position_statement_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/cochrane_ai_position_statement_2025_methodology.md)

---

## 7. Recommended Benchmark Gate

### Recommendation

Do not deploy any prompt/model configuration on the live corpus before it passes
a curated benchmark set.

### Benchmark should contain

- must-include positives;
- clear negatives from different exclusion families;
- benchmark/resource papers;
- wrapper/application papers;
- encoder-only negatives;
- deliberately selected borderline papers.

### What the benchmark should score

Primary:

- false exclusion count;
- recall on must-include papers;
- behavior on borderline papers.

Secondary:

- agreement on clear negatives;
- manual workload reduction.

### Why

The literature supports validation before deployment, but it does not give us a
universal threshold. That means we must create our own local validation basis.

### Source support

- PRISMA-trAIce: validation basis and metrics must be explicit.
  Source:
  [jmir_prisma_trace_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)
- Cochrane: AI use must be justified in context, not assumed.
  Source:
  [cochrane_ai_position_statement_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/cochrane_ai_position_statement_2025_methodology.md)
- BMC: threshold choice changes the safety-efficiency trade-off materially.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)

---

## 8. Recommended Prompt Policy

### Recommendation

Treat the prompt as a controlled methodological artifact.

Each prompt version should have:

- full prompt text;
- `prompt_version`;
- `prompt_hash`;
- model/provider;
- key inference parameters;
- benchmark or validation basis;
- approval date;
- change note.

### Why

Our current problem is not just prompt quality. It is also prompt governance.

### Source support

- PRISMA-trAIce explicitly requires reporting prompt structure, settings, and
  iterative refinement.
  Source:
  [jmir_prisma_trace_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)

---

## 9. Recommended Logging Policy

### Recommendation

Log criterion-level outputs, not only final decisions.

Minimum recommended fields:

- record snapshot;
- model/provider/version;
- prompt version/hash;
- reviewer role;
- criterion answers;
- criterion rationales;
- final decision;
- primary exclusion code;
- uncertainty reason;
- raw output path;
- post-processing version;
- human review fields;
- adjudication fields;
- validation basis.

### Why

This is necessary for:

- prompt comparison;
- benchmark debugging;
- disagreement analysis;
- PRISMA-grade reporting;
- post hoc audit of exclusions.

### Source support

- BMC logged question-level outputs to support traceability.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)
- PRISMA-trAIce requires auditable reporting of inputs, outputs, and oversight.
  Source:
  [jmir_prisma_trace_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)

---

## 10. Recommended Governance And Safety Case

### Recommendation

Before live deployment, the repo should contain a short explicit justification
for AI use in this review.

It should state:

- why AI is being used;
- what benefit is expected;
- what the main risks are;
- what the benchmark evidence is;
- what the oversight policy is;
- what deployment rule is being used.

### Why

The most defensible system is not the most clever one. It is the one for which
we can explain why deployment is justified.

### Source support

- Cochrane statement is the clearest basis for this requirement.
  Source:
  [cochrane_ai_position_statement_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/cochrane_ai_position_statement_2025_methodology.md)
- PRISMA-trAIce supports protocol-level accountability and reporting of
  deviations.
  Source:
  [jmir_prisma_trace_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/jmir_prisma_trace_2025_methodology.md)

---

## 11. Recommended Position On Full-Text RAG

### Recommendation

Do **not** make full-text RAG part of the first stable version of this system.

### Why

Our main ambiguity still lives at title/abstract level:

- paper type;
- text-bio relation;
- architecture type;
- FM evidence.

Adding full-text RAG now would increase complexity before the first-stage logic
is stable.

### When full-text RAG becomes justified

Only after:

- title/abstract criteria are stable;
- the benchmark is in place;
- we can identify a recurring class of abstract-insufficient papers;
- we have a separate evaluation slice for those papers.

### Source support

- BMC supports full-text RAG only as a separate second phase, not as a
  substitute for good title/abstract design.
  Source:
  [bmc_streamlining_sr_llm_2025_methodology.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md)

---

## 12. Final Recommendation

For this review, the most defensible system is:

- **BMC-style criterion-by-criterion screening logic**
- under **PRISMA-trAIce-style reporting and auditability**
- with **Cochrane-style governance, validation, and human oversight**

This is more solid than a custom tier-first architecture because each core
design choice is directly motivated by the literature:

- criterion-level questions -> supported most clearly by BMC;
- prompt/version governance and audit trail -> supported most clearly by
  PRISMA-trAIce;
- benchmark gate, justification, and oversight -> supported most clearly by the
  Cochrane position statement.

Our own domain-specific interpretation is still needed, but it should enter only
at the level of criterion wording, not at the level of inventing an entirely
new screening philosophy.
