# Screening Prompts for Criterion-by-Criterion Title/Abstract Review

These files document the current `LatteReview` prompt stack for the
criterion-by-criterion title/abstract workflow.

They are **not** the canonical runtime source of truth for operative prompt
text.

The canonical prompt templates intended for loading by the screening runner are
stored in:

- [../screening_prompt_templates/README.md](../screening_prompt_templates/README.md)

Current stage prompts:

- [scope_reviewer_prompt.md](scope_reviewer_prompt.md)
- [architecture_reviewer_prompt.md](architecture_reviewer_prompt.md)
- [adjudicator_prompt.md](adjudicator_prompt.md)

These prompts are aligned to:

- [eligibility_criteria.md](../eligibility_criteria.md)
- [llm_screening_system_guideline.md](../llm_screening_system_guideline.md)
- [lattereview_screening_architecture.md](../lattereview_screening_architecture.md)

The prompt stack is intentionally:

- criterion-by-criterion rather than one-shot;
- sensitivity-first rather than aggressive-auto-exclusion-first;
- structured-output-first rather than rationale-first.

The current structured response schema is reviewer-specific:

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
  - the union of criterion fields needed to resolve round-A conflicts

The final `INCLUDE / EXCLUDE / UNCERTAIN` label is derived later by Python gate
logic and rule-based aggregation, not treated as the primary reviewer output.
