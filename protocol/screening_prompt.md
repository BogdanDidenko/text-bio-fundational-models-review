# LLM Screening Prompt Stack — Title/Abstract Phase

## Current Status

The repository no longer treats title/abstract screening as a one-shot
`INCLUDE / EXCLUDE / UNCERTAIN` prompt hidden inside one script.

The current direction is a **criterion-by-criterion LatteReview workflow**
aligned to:

- [`eligibility_criteria.md`](eligibility_criteria.md)
- [`llm_screening_system_guideline.md`](llm_screening_system_guideline.md)
- [`lattereview_screening_architecture.md`](lattereview_screening_architecture.md)

This is the prompt stack currently being piloted on the screening corpus.

---

## Current Prompt Topology

Stage prompts:

- [`scope_reviewer`](screening_prompts/scope_reviewer_prompt.md)
- [`architecture_reviewer`](screening_prompts/architecture_reviewer_prompt.md)
- [`adjudicator`](screening_prompts/adjudicator_prompt.md)

The workflow is:

1. round A `scope_reviewer`
2. round A `architecture_reviewer`
3. Python gate logic computes provisional retain/exclude/uncertain states from criterion answers
4. round B `adjudicator` only for unresolved or criterion-conflict cases
5. rule-based aggregation from selected criterion fields to final decision

This is intentionally closer to the BMC paper than to the older one-shot
prompting approach.

---

## Current Structured Output Schema

The current screening stack uses reviewer-specific criterion fields rather than
a reviewer-level final label.

Current reviewer outputs:

- `scope_reviewer`
  - `paper_type`
  - `bio_modality_present`
  - `text_component_present`
  - `text_bio_bridge_present`
  - `primary_exclusion_code`
  - `uncertainty_reason`
  - `decision_rationale`
- `architecture_reviewer`
  - `paper_type`
  - `generative_model_present`
  - `foundation_model_evidence`
  - `primary_exclusion_code`
  - `uncertainty_reason`
  - `decision_rationale`
- `adjudicator`
  - union of the above criterion fields when round B is triggered

Allowed high-level values:

- `paper_type`: `primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear`
- criterion fields: `yes | no | unclear`

The important design choice is that the final screening decision is no longer
trusted as a pure one-shot model judgment. Instead, the workflow first elicits
criterion-level answers, derives reviewer gate states outside the LLM, and then
aggregates them conservatively.

---

## Current Aggregation Policy

The current pilot aggregation logic is conservative:

- the scope reviewer and architecture reviewer do **not** emit the final
  decision as a primary field;
- Python gate logic converts their criterion answers into provisional gate
  states such as `INCLUDE / EXCLUDE / UNCERTAIN`;
- adjudication is triggered by unresolved criteria or criterion-level conflict,
  not by disagreement between two opaque reviewer labels;
- `review_editorial`, `benchmark_resource`, and `application_wrapper` are
  direct exclusion classes;
- `no` on `bio_modality_present` excludes for lack of biological modality;
- `no` on `text_component_present` excludes for lack of text component;
- `no` on `text_bio_bridge_present` excludes for lack of substantive text-bio bridge;
- `no` on `generative_model_present` excludes for non-generative architecture;
- `no` on `foundation_model_evidence` excludes for insufficient FM evidence;
- any unresolved decisive criterion can escalate to `UNCERTAIN`.

This is the main difference from the deprecated `v0.1` design: criterion fields
are primary, and the final label is a derived downstream artifact.

## Current Execution Pattern

The preferred development and pilot mode is now:

1. run a remote OpenAI-compatible `vLLM` server on the GPU cluster;
2. expose it locally through an SSH tunnel;
3. execute the `LatteReview` workflow locally against that endpoint;
4. keep all prompt iteration, gate logic, and result analysis local.

This pattern is operationally important because the screening method is now
decoupled from the GPU runtime environment. The cluster provides the inference
backend; the screening logic remains local and versioned.

---

## Why the Prompt Stack Changed

The old `v0.1` prompt was too close to a one-shot classifier. In testing, that
made it too easy for:

- wrapper-style LLM applications to slip through;
- benchmark/resource papers to look falsely in scope;
- weakly specified transformer papers to be treated as generative;
- ambiguous abstracts to be forced into premature binary decisions.

The current criterion-by-criterion stack was introduced to fix those exact
failure modes and to align the repo with the literature-backed recommendation:

- BMC for screening behavior;
- PRISMA-trAIce for auditability;
- Cochrane for validation and human oversight.

---

## Deprecated Prompt

The earlier one-shot prompt design described here as `v0.1` should now be
treated as historical background rather than the current operational design.
