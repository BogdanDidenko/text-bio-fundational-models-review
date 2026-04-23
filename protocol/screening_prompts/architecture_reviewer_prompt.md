# Architecture Reviewer Prompt

## Purpose

This reviewer handles the architecture and foundation-model side of the same
title/abstract record.

Primary questions:

5. `generative_model_present`
6. `foundation_model_evidence`

It can also mark the record as `application_wrapper` when the abstract clearly
describes a downstream wrapper around an existing model.

## Canonical Runtime Files

The operative runtime artifacts for this reviewer are:

- [../screening_prompt_templates/architecture_reviewer_prompt.txt](../screening_prompt_templates/architecture_reviewer_prompt.txt)

## Structured Output

The reviewer returns exactly one JSON object with these keys:

- `paper_type`
- `generative_model_present`
- `foundation_model_evidence`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

Allowed high-level values:

- `paper_type`: `primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear`
- `generative_model_present`: `yes | no | unclear`
- `foundation_model_evidence`: `yes | no | unclear`

The operative template also constrains `primary_exclusion_code` and
`uncertainty_reason` to a smaller codebook for better reproducibility and
reportability.

## Why This Prompt Was Tightened

Compared with earlier prompt versions, the current template is stricter about:

- predictive/profile systems that are not truly generative;
- encoder-only systems that should not be treated as positive evidence;
- wrapper papers that borrow an existing model without presenting a new
  in-scope FM contribution;
- using `unclear` when architecture or FM evidence is underspecified.

This change was made to better align the prompt with:

- [../eligibility_criteria.md](../eligibility_criteria.md), especially `IC3`
  and `IC4`;
- the BMC-style criterion-by-criterion recommendation summarized in
  [../llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md](../llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md).
