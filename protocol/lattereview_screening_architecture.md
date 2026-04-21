# LatteReview Screening Architecture For This Review

## Purpose

This document describes how `LatteReview` should be used for our
LLM-assisted title/abstract screening workflow for **text-bio foundational
models**.

The architecture below is not a generic LatteReview example. It is a concrete
recommendation for this review, grounded in:

- the actual structure of the local `LatteReview` codebase
- the literature-backed guideline in
  [llm_screening_system_guideline.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/llm_screening_system_guideline.md)
- the methodological reviews in
  `protocol/llm_screening_methodology/`

The key design principles are:

- use `LatteReview` as an orchestration layer for a
  **criterion-by-criterion, sensitivity-first, human-supervised** workflow;
- do **not** use it as a wrapper around a one-shot binary classifier.
- keep screening orchestration local and treat the cluster primarily as a
  remote OpenAI-compatible `vLLM` serving backend.

---

## 1. What LatteReview Already Gives Us

From the local codebase, the relevant abstractions are:

- `ScoringReviewer`
- `BasicReviewer`
- `ReviewWorkflow`
- provider abstractions (`OpenAIProvider`, `LiteLLMProvider`, etc.)

Operationally:

- each reviewer is configured with a provider, a prompt, a response schema, and
  model arguments;
- `ReviewWorkflow` executes one or more rounds;
- each round can use one or multiple reviewers;
- each reviewer writes outputs back into dataframe columns like
  `round-A_<reviewer>_<field>`;
- later rounds can consume previous round outputs as part of their
  `text_inputs`.

This means LatteReview is already a good fit for our target design:

- round A: independent first-pass reviewers;
- round B: adjudicator over disagreements / uncertain cases;
- structured outputs per reviewer;
- dataframe-native logging of intermediate results.

---

## 2. Recommended Workflow Topology

### Round A

Two independent reviewers:

1. `scope_reviewer`
2. `architecture_reviewer`

### Round B

One adjudicator:

3. `adjudicator`

### Why this topology

This is the cleanest mapping between our review problem and the workflow model
implemented by LatteReview.

Our difficult records tend to fail for one of two reasons:

- **scope failure**:
  - review / benchmark / application paper
  - no real biology
  - no real text component
  - no real text-bio relationship

- **architecture/FM failure**:
  - encoder-only rather than generative
  - wrapper rather than model
  - insufficient FM evidence

This split is exactly why one all-purpose reviewer is suboptimal for our task.

---

## 3. Recommended Reviewer Responsibilities

### 3.1 Scope Reviewer

The scope reviewer should answer:

- `paper_type`
- `bio_modality_present`
- `text_component_present`
- `text_bio_bridge_present`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

This reviewer should focus on:

- whether the record is even a candidate model paper;
- whether the abstract shows a real text+biology relation;
- whether the paper is actually in scope at all.

### 3.2 Architecture Reviewer

The architecture reviewer should answer:

- `paper_type` when the abstract clearly describes a wrapper/application paper
- `generative_model_present`
- `foundation_model_evidence`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

This reviewer should focus on:

- generative vs encoder-only;
- model paper vs wrapper/application when that is explicit in the abstract;
- whether FM-style pretraining / transfer evidence is present.

### 3.3 Adjudicator

The adjudicator should consume:

- title + abstract
- scope reviewer structured outputs
- architecture reviewer structured outputs

The adjudicator should run only when:

- reviewers disagree on final decision;
- either reviewer returns `UNCERTAIN`;
- reviewer outputs are internally inconsistent.

The adjudicator should produce:

- resolved criterion fields
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`
- optionally `adjudication_note`

---

## 4. Recommended Decision Schema

The system should use a criterion-level JSON schema, not a simple score-only
schema.

The current workflow uses reviewer-specific schemas.

### Scope reviewer fields

- `paper_type`
- `bio_modality_present`
- `text_component_present`
- `text_bio_bridge_present`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

### Architecture reviewer fields

- `paper_type`
- `generative_model_present`
- `foundation_model_evidence`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

Recommended value sets:

- `paper_type`: `primary_model_paper`, `review_editorial`,
  `benchmark_resource`, `application_wrapper`, `unclear`
- `bio_modality_present`: `yes`, `no`, `unclear`
- `text_component_present`: `yes`, `no`, `unclear`
- `text_bio_bridge_present`: `yes`, `no`, `unclear`
- `generative_model_present`: `yes`, `no`, `unclear`
- `foundation_model_evidence`: `yes`, `no`, `unclear`

The adjudicator uses the union of these fields when round B is triggered.

This is more aligned with the literature than making `Tier A / B / C` the
main workflow language. If we keep the tier logic at all, it should only
survive inside the interpretation of whether a substantive
`text_bio_bridge_present` signal exists.

The reviewer-level output should stop at criterion answers. A provisional gate
state such as `INCLUDE`, `EXCLUDE`, or `UNCERTAIN` should be computed in Python
from those answers rather than requested directly from the LLM.

---

## 5. Recommended Round Logic

### Round A filter

Run both first-pass reviewers on all candidate records that have title and
abstract text.

### Round B filter

Run the adjudicator only on records where:

- either reviewer returns `unclear` on a core criterion
- or criterion-derived gate logic produces `UNCERTAIN`
- or there is a criterion-level conflict between reviewers on an overlapping field

This keeps the workflow efficient without sacrificing conservative handling of
ambiguous records.

---

## 6. Python-Like Implementation Sketch

Below is the recommended orchestration shape. It is not a drop-in script, but
it matches the actual abstractions used by LatteReview.

```python
from lattereview.agents import ScoringReviewer
from lattereview.workflows.review_workflow import ReviewWorkflow


SCOPE_RESPONSE_FORMAT = {
    "paper_type": str,
    "bio_modality_present": str,
    "text_component_present": str,
    "text_bio_bridge_present": str,
    "primary_exclusion_code": str,
    "uncertainty_reason": str,
    "decision_rationale": str,
}


scope_reviewer = ScoringReviewer(
    name="scope_reviewer",
    provider=provider,
    response_format=SCREENING_RESPONSE_FORMAT,
    scoring_task=(
        "Answer criterion questions 1-4 for title/abstract screening: "
        "(1) paper_type, (2) bio_modality_present, "
        "(3) text_component_present, (4) text_bio_bridge_present."
    ),
    scoring_set=[],
    reasoning="brief",
    model_args={
        "temperature": 0.7,
        "top_p": 1,
        "n": 1,
        "seed": 0,
    },
)


ARCHITECTURE_RESPONSE_FORMAT = {
    "paper_type": str,
    "generative_model_present": str,
    "foundation_model_evidence": str,
    "primary_exclusion_code": str,
    "uncertainty_reason": str,
    "decision_rationale": str,
}


architecture_reviewer = ScoringReviewer(
    name="architecture_reviewer",
    provider=provider,
    response_format=ARCHITECTURE_RESPONSE_FORMAT,
    scoring_task=(
        "Answer criterion questions 5-6 for title/abstract screening: "
        "(5) generative_model_present, (6) foundation_model_evidence. "
        "Use paper_type=application_wrapper if the abstract makes clear "
        "that the work is only a wrapper around an existing model."
    ),
    scoring_set=[],
    reasoning="brief",
    model_args={
        "temperature": 0.7,
        "top_p": 1,
        "n": 1,
        "seed": 0,
    },
)


ADJUDICATOR_RESPONSE_FORMAT = {
    "paper_type": str,
    "bio_modality_present": str,
    "text_component_present": str,
    "text_bio_bridge_present": str,
    "generative_model_present": str,
    "foundation_model_evidence": str,
    "primary_exclusion_code": str,
    "uncertainty_reason": str,
    "decision_rationale": str,
}


adjudicator = ScoringReviewer(
    name="adjudicator",
    provider=provider,
    response_format=ADJUDICATOR_RESPONSE_FORMAT,
    scoring_task=(
        "Resolve disagreements between the criterion-level outputs of the "
        "scope and architecture reviewers using the abstract and their "
        "structured outputs."
    ),
    scoring_set=[],
    reasoning="brief",
    model_args={
        "temperature": 0.7,
        "top_p": 1,
        "n": 1,
        "seed": 0,
    },
)


round_a_workflow = ReviewWorkflow(
    workflow_schema=[
        {
            "round": "A",
            "reviewers": [scope_reviewer, architecture_reviewer],
            "text_inputs": ["title", "abstract"],
        },
    ],
)

round_a_results = round_a_workflow(df)
round_a_results["scope_gate"] = round_a_results.apply(scope_gate_decision, axis=1)
round_a_results["architecture_gate"] = round_a_results.apply(architecture_gate_decision, axis=1)
round_a_results["needs_adjudication"] = round_a_results.apply(needs_adjudication, axis=1)

adjudication_df = round_a_results[round_a_results["needs_adjudication"]]

round_b_workflow = ReviewWorkflow(
    workflow_schema=[
        {
            "round": "B",
            "reviewers": [adjudicator],
            "text_inputs": [
                "title",
                "abstract",
                "round-A_scope_reviewer_paper_type",
                "round-A_scope_reviewer_bio_modality_present",
                "round-A_scope_reviewer_text_component_present",
                "round-A_scope_reviewer_text_bio_bridge_present",
                "round-A_scope_reviewer_primary_exclusion_code",
                "round-A_scope_reviewer_uncertainty_reason",
                "round-A_architecture_reviewer_paper_type",
                "round-A_architecture_reviewer_generative_model_present",
                "round-A_architecture_reviewer_foundation_model_evidence",
                "round-A_architecture_reviewer_primary_exclusion_code",
                "round-A_architecture_reviewer_uncertainty_reason",
            ],
        },
    ],
)
```

In the current pilot, the final record-level decision is then produced by a
Python aggregation layer over the criterion fields rather than by asking the
LLM for the final label as a first-class field.

---

## 7. Reproducibility Mode

For this review, the default screening mode should be a
**controlled-stochastic reproducibility profile**.

Recommended inference settings:

- `temperature = 0.7`
- `top_p = 1`
- `n = 1`
- fixed `seed = 0`

For `vLLM`, the best currently documented official mechanism is
`VLLM_BATCH_INVARIANT=1`, which aims to make outputs deterministic and invariant
to batch size / request order on supported hardware.

Recommended runtime policy for the reproducible screening profile:

- fixed model revision
- fixed tokenizer revision
- fixed vLLM version
- fixed hardware class
- `VLLM_BATCH_INVARIANT=1`
- same prompt version / hash across reruns
- no silent model or provider swap

This profile is more stochastic than a greedy `temperature=0` setup, so it
should not be described as guaranteed universal determinism. Instead, it should
be treated as a reproducibility target that must be verified empirically on the
serving stack we actually use.

### Practical implication for our current stack

An empirical probe on **April 18, 2026** using one candidate serving profile:

- `Qwen/Qwen3.5-35B-A3B-FP8`
- `vLLM 0.19.1rc1.dev235+g1b19bd758`
- `temperature=0.7`
- `top_p=1`
- `seed=0`
- `VLLM_BATCH_INVARIANT=1`
- the same 10 records presented in three different orders

showed that outputs were **not byte-identical across runs**. The final decision
was stable for most records, but at least one benchmark/resource paper showed
differences in structured criterion fields beyond free-text rationale.

Therefore, for our review we should document the following rule:

- fixed seed plus `temperature=0.7` is acceptable as a controlled screening
  profile;
- however, it must **not** be described as guaranteed deterministic on the
  current serving stack;
- any claim of determinism must be supported by a passing benchmark probe on
  the exact serving profile used in production: model, vLLM version, hardware,
  and server configuration.

### Current runtime recommendation

The screening workflow should now be described as:

- local `LatteReview` orchestration;
- remote `vLLM` serving on the GPU cluster;
- SSH tunneling from a local OpenAI-compatible endpoint to the remote server;
- determinism checks performed against that exact end-to-end serving profile.

This reduces dependence on fragile remote development sessions while keeping
the model-serving stack fixed.

In the current project state, a repeated 10-record local-orchestration run
against the same remote serving profile produced an exact match across the two
runs on all shared result columns. This does not prove universal determinism,
but it is the strongest current operational evidence that the architecture is
stable under the validated serving profile.

---

## 8. Model Policy

### Development vs production

For development and pilot calibration, we may use a cheaper or smaller model.

For production screening, the model will likely be different.

This should be stated explicitly in the repo because:

- screening architecture should be stable even if the serving model changes;
- model choice is a deployment variable, not the core methodological design;
- production may require a stronger model or a different infrastructure profile.

### Recommended wording

The architecture should be documented as **model-agnostic**, with the note that:

- pilot and validation runs may use any model that satisfies the validation target;
- production deployment may use a different model entirely;
- the hard requirement is reproducible behavior under the validated serving profile, not loyalty to a specific checkpoint.
- every model change requires revalidation on the benchmark set.

---

## 9. What The Reviewed Papers Suggest About Model Choice

### Do the papers recommend using different LLMs for different reviewers?

No. The reviewed papers do **not** say that different reviewers must use
different LLM families.

### What the papers do support

#### BMC paper

The BMC paper uses a single GPT-4-based workflow and does not argue that
reviewer diversity must come from different model families.

What it supports is:

- explicit criterion questions;
- explicit handling of `unsure`;
- structured logging;
- conservative retention of ambiguous cases.

#### PRISMA-trAIce

PRISMA-trAIce is not a model-selection paper. It requires transparent reporting
of:

- model identity;
- prompt identity;
- settings;
- validation basis;
- human-AI interaction.

It does not recommend one model, or multiple different models, as a universal
best practice.

#### Cochrane position statement

The Cochrane-style governance statement does not recommend model diversity as a
rule either. It requires that:

- the tool be justified for the task;
- the validation basis be explicit;
- oversight be defined;
- deployment risk be acceptable.

### Practical recommendation for our pipeline

For our first stable pipeline, it is acceptable to use the **same base model**
for:

- `scope_reviewer`
- `architecture_reviewer`
- `adjudicator`

as long as:

- prompts are role-specific;
- outputs are structured;
- the configuration is benchmark-validated.

This is more directly supported by the literature than inventing
cross-model diversity as a requirement.

If later we want to test heterogeneous models, that should be treated as a
benchmarkable engineering experiment, not as something the papers require.

---

## 10. Final Recommendation

The recommended LatteReview architecture for this review is:

- two role-specialized first-pass reviewers;
- one adjudicator;
- criterion-level JSON outputs;
- conservative `UNCERTAIN` retention;
- reproducibility-first runtime settings;
- explicit model/version governance;
- benchmark-gated deployment.

This design is:

- consistent with the actual LatteReview orchestration model;
- aligned with the strongest screening recommendation from the BMC paper;
- reportable under PRISMA-trAIce-style logic;
- governable under the Cochrane/RAISE-style position.
