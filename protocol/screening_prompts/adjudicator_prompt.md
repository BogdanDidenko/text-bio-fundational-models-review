# Adjudicator Prompt

## Purpose

This reviewer runs only on disagreement or unresolved-criterion cases after
round A.

It consumes:

- title
- abstract
- criterion outputs from `scope_reviewer`
- criterion outputs from `architecture_reviewer`

Its job is not to be liberal. Its job is to resolve disagreement conservatively
and preserve `unclear` when the abstract still does not justify a stronger
claim.

## Canonical Runtime Files

The operative runtime artifacts for this reviewer are:

- [../screening_prompt_templates/adjudicator_prompt.txt](../screening_prompt_templates/adjudicator_prompt.txt)

## Structured Output

The adjudicator returns exactly one JSON object with these keys:

- `paper_type`
- `bio_modality_present`
- `text_component_present`
- `text_bio_bridge_present`
- `generative_model_present`
- `foundation_model_evidence`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

Allowed high-level values:

- `paper_type`: `primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear`
- `bio_modality_present`: `yes | no | unclear`
- `text_component_present`: `yes | no | unclear`
- `text_bio_bridge_present`: `yes | no | unclear`
- `generative_model_present`: `yes | no | unclear`
- `foundation_model_evidence`: `yes | no | unclear`

The operative template also constrains `primary_exclusion_code` and
`uncertainty_reason` to a smaller codebook for better reproducibility and
reportability.

## Why This Prompt Was Tightened

Compared with earlier prompt versions, the current template is stricter about:

- resolving each criterion independently rather than “picking a winner” between
  reviewers;
- preserving conservative review/editorial, benchmark/resource, and
  application-wrapper exclusions;
- keeping a criterion as `unclear` when the conflict is not truly resolved by
  the title/abstract.

This change was made to better align the prompt with:

- the adjudication logic in
  [../lattereview_screening_architecture.md](../lattereview_screening_architecture.md);
- the sensitivity-first, criterion-by-criterion recommendation summarized in
  [../llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md](../llm_screening_methodology/bmc_streamlining_sr_llm_2025_methodology.md).
