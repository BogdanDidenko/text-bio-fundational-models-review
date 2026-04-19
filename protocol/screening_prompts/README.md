# Screening Prompts for Criterion-by-Criterion Title/Abstract Review

These files document the current `LatteReview` prompt stack for the
criterion-by-criterion title/abstract workflow.

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

The current structured response schema is:

- `paper_type`
- `bio_modality_present`
- `text_component_present`
- `text_bio_bridge_present`
- `generative_model_present`
- `foundation_model_evidence`
- `reviewer_recommendation`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`
