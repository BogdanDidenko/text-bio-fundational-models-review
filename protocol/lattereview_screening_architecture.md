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

The key design principle is:

- use `LatteReview` as an orchestration layer for a
  **criterion-by-criterion, sensitivity-first, human-supervised** workflow;
- do **not** use it as a wrapper around a one-shot binary classifier.

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
- `text_bio_relation`
- `final_decision`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

This reviewer should focus on:

- whether the record is even a candidate model paper;
- whether the abstract shows a real text+biology relation;
- whether the paper is actually in scope at all.

### 3.2 Architecture Reviewer

The architecture reviewer should answer:

- `architecture_type`
- `foundation_model_evidence`
- `paper_type`
- `final_decision`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

This reviewer should focus on:

- generative vs encoder-only;
- model paper vs wrapper/application;
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

- `final_decision`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`
- optionally `adjudication_note`

---

## 4. Recommended Decision Schema

The system should use a criterion-level JSON schema, not a simple score-only
schema.

Recommended fields:

- `paper_type`
- `bio_modality_present`
- `text_component_present`
- `text_bio_relation`
- `architecture_type`
- `foundation_model_evidence`
- `final_decision`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

Recommended value sets:

- `paper_type`: `primary_model_paper`, `review_editorial`,
  `benchmark_resource`, `application_wrapper`, `unclear`
- `bio_modality_present`: `yes`, `no`, `unclear`
- `text_component_present`: `yes`, `no`, `unclear`
- `text_bio_relation`: `explicit_natural_language_bridge`,
  `biological_token_generative_case`, `not_sufficient_for_scope`, `unclear`
- `architecture_type`: `generative`, `encoder_only`, `wrapper_or_pipeline`,
  `unclear`
- `foundation_model_evidence`: `yes`, `no`, `unclear`
- `final_decision`: `INCLUDE`, `EXCLUDE`, `UNCERTAIN`

This is more aligned with the literature than making `Tier A / B / C` the main
workflow language. If we keep the tier logic at all, it should only survive
inside the single field `text_bio_relation`.

---

## 5. Recommended Round Logic

### Round A filter

Run both first-pass reviewers on all candidate records that have title and
abstract text.

### Round B filter

Run the adjudicator only on records where:

- `scope_reviewer.final_decision != architecture_reviewer.final_decision`
  or
- either reviewer returns `UNCERTAIN`
  or
- either reviewer returns `unclear` on a core criterion

This keeps the workflow efficient without sacrificing conservative handling of
ambiguous records.

---

## 6. Python-Like Implementation Sketch

Below is the recommended orchestration shape. It is not a drop-in script, but
it matches the actual abstractions used by LatteReview.

```python
from lattereview.agents import ScoringReviewer
from lattereview.workflows.review_workflow import ReviewWorkflow


SCREENING_RESPONSE_FORMAT = {
    "paper_type": str,
    "bio_modality_present": str,
    "text_component_present": str,
    "text_bio_relation": str,
    "architecture_type": str,
    "foundation_model_evidence": str,
    "final_decision": str,
    "primary_exclusion_code": str,
    "uncertainty_reason": str,
    "decision_rationale": str,
}


scope_reviewer = ScoringReviewer(
    name="scope_reviewer",
    provider=provider,
    response_format=SCREENING_RESPONSE_FORMAT,
    scoring_task=(
        "Evaluate paper type, biological modality, text component, "
        "and the nature of the text-bio relationship. Then return a "
        "provisional final decision."
    ),
    scoring_set=[],
    reasoning="brief",
    model_args={
        "temperature": 0,
        "top_p": 1,
        "n": 1,
        "seed": 0,
    },
)


architecture_reviewer = ScoringReviewer(
    name="architecture_reviewer",
    provider=provider,
    response_format=SCREENING_RESPONSE_FORMAT,
    scoring_task=(
        "Evaluate whether the architecture is generative or encoder-only, "
        "whether the paper is a wrapper/application rather than a model paper, "
        "and whether there is evidence of a foundation-model contribution."
    ),
    scoring_set=[],
    reasoning="brief",
    model_args={
        "temperature": 0,
        "top_p": 1,
        "n": 1,
        "seed": 0,
    },
)


adjudicator = ScoringReviewer(
    name="adjudicator",
    provider=provider,
    response_format=SCREENING_RESPONSE_FORMAT,
    scoring_task=(
        "Resolve disagreements between the scope and architecture reviewers. "
        "Be conservative: if the abstract does not resolve a key criterion, "
        "return UNCERTAIN rather than EXCLUDE."
    ),
    scoring_set=[],
    reasoning="brief",
    model_args={
        "temperature": 0,
        "top_p": 1,
        "n": 1,
        "seed": 0,
    },
)


workflow = ReviewWorkflow(
    workflow_schema=[
        {
            "round": "A",
            "reviewers": [scope_reviewer, architecture_reviewer],
            "text_inputs": ["title", "abstract"],
        },
        {
            "round": "B",
            "reviewers": [adjudicator],
            "text_inputs": [
                "title",
                "abstract",
                "round-A_scope_reviewer_paper_type",
                "round-A_scope_reviewer_text_bio_relation",
                "round-A_scope_reviewer_final_decision",
                "round-A_scope_reviewer_decision_rationale",
                "round-A_architecture_reviewer_architecture_type",
                "round-A_architecture_reviewer_foundation_model_evidence",
                "round-A_architecture_reviewer_final_decision",
                "round-A_architecture_reviewer_decision_rationale",
            ],
            "filter": lambda row: (
                row["round-A_scope_reviewer_final_decision"] !=
                row["round-A_architecture_reviewer_final_decision"]
            ) or (
                row["round-A_scope_reviewer_final_decision"] == "UNCERTAIN"
            ) or (
                row["round-A_architecture_reviewer_final_decision"] == "UNCERTAIN"
            ),
        },
    ],
)
```

---

## 7. Reproducibility Mode

For this review, the default screening mode should be **reproducibility-first**.

Recommended inference settings:

- `temperature = 0`
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

This will not make the system universally reproducible across arbitrary
hardware/software changes, but it is the best documented current path for a
stable screening mode.

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

- pilot and validation runs may use a cheaper model;
- production deployment will likely use a stronger model;
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
