# Scope Reviewer Prompt

## Purpose

This reviewer handles the first four title/abstract screening questions:

1. `paper_type`
2. `bio_modality_present`
3. `text_component_present`
4. `text_bio_bridge_present`

It is the first-pass scope gate for the current `LatteReview` workflow.

## Canonical Runtime Files

The operative runtime artifacts for this reviewer are:

- [../screening_prompt_templates/scope_reviewer_prompt.txt](../screening_prompt_templates/scope_reviewer_prompt.txt)
- [../screening_prompt_templates/scope_reviewer_backstory.txt](../screening_prompt_templates/scope_reviewer_backstory.txt)

The generic LatteReview system wrapper used around the reviewer metadata is
documented in:

- [../screening_prompt_templates/lattereview_system_prompt_template.txt](../screening_prompt_templates/lattereview_system_prompt_template.txt)

## Structured Output

The reviewer returns exactly one JSON object with these keys:

- `paper_type`
- `bio_modality_present`
- `text_component_present`
- `text_bio_bridge_present`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

Allowed high-level values:

- `paper_type`: `primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear`
- `bio_modality_present`: `yes | no | unclear`
- `text_component_present`: `yes | no | unclear`
- `text_bio_bridge_present`: `yes | no | unclear`

The operative template also constrains `primary_exclusion_code` and
`uncertainty_reason` to a smaller codebook for better reproducibility and
reportability.

## Why This Prompt Was Tightened

Compared with earlier prompt versions, the current template is stricter about:

- wrapper-style use of an external LLM;
- benchmark/resource papers that are not primary model papers;
- using `unclear` when a substantive text-bio bridge is not actually supported
  by the title/abstract.

This change was made to better align the prompt with:

- [../eligibility_criteria.md](../eligibility_criteria.md), especially `IC2`
  and `IC4`;
- the BMC-style criterion-by-criterion recommendation summarized in
  [../llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md](../llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md).
