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
and preserve `UNCERTAIN` when the abstract still does not justify a stronger
claim.

## Structured Output

The adjudicator returns exactly one JSON object with these keys:

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

Allowed values:

- `paper_type`: `primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear`
- `bio_modality_present`: `yes | no | unclear`
- `text_component_present`: `yes | no | unclear`
- `text_bio_bridge_present`: `yes | no | unclear`
- `generative_model_present`: `yes | no | unclear`
- `foundation_model_evidence`: `yes | no | unclear`
- `reviewer_recommendation`: `INCLUDE | EXCLUDE | UNCERTAIN`

## Prompt Assembly

### Generic prompt

```text
Review the title/abstract record below for systematic-review screening of text-bio foundational models.

Return exactly one JSON object with these keys:
- paper_type
- bio_modality_present
- text_component_present
- text_bio_bridge_present
- generative_model_present
- foundation_model_evidence
- reviewer_recommendation
- primary_exclusion_code
- uncertainty_reason
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- bio_modality_present: yes | no | unclear
- text_component_present: yes | no | unclear
- text_bio_bridge_present: yes | no | unclear
- generative_model_present: yes | no | unclear
- foundation_model_evidence: yes | no | unclear
- reviewer_recommendation: INCLUDE | EXCLUDE | UNCERTAIN

Global decision policy:
- Use a sensitivity-first title/abstract screening strategy.
- If a key criterion cannot be resolved from the abstract, use UNCERTAIN rather than forcing EXCLUDE.
- Review/editorial, benchmark/resource, and application/wrapper papers are not primary in-scope model papers.
- Encoder-only biological token models are out of scope.
- Biological-token generative models may be in scope if the architecture is clearly generative and FM-like.
- If a paper only uses embeddings, metadata descriptions, prompts, or outputs from an existing LLM as auxiliary features for downstream bio tasks, classify it as application_wrapper unless the abstract clearly presents a new joint text-bio generative foundation model.
- Benchmark/resource papers evaluating LLMs or DNA/protein language models are not in-scope primary model papers.
- Return a short rationale, not a long essay.
```

### Reviewer-specific task

```text
Resolve disagreements between the criterion-level outputs of the scope and architecture reviewers using the abstract and their structured outputs.
```

### Reviewer-specific rules

```text
Use the most conservative interpretation consistent with the abstract. Preserve clear review/benchmark/application exclusions. If the abstract only supports wrapper-style LLM use, set paper_type=application_wrapper and text_bio_bridge_present=no. If any decisive criterion remains unresolved, return reviewer_recommendation=UNCERTAIN.
```

### Shared context

```text
Key boundaries for this review:
- Strong include-style patterns: explicit text-to-bio or bio-to-text bridge, text-guided omics generation/alignment, or biological-token generative FM.
- Strong exclude-style patterns: review/editorial papers, benchmark/resource papers, application wrappers around an existing LLM, encoder-only models, and bio-only multimodal systems with no real text bridge.
- Predictive profile/score outputs are not generative by default; do not mark generative_model_present=yes unless the abstract clearly describes decoder/autoregressive/seq2seq/diffusion/generative behavior.
- If the abstract is very short, snippet-like, or insufficient to resolve architecture or scope, prefer UNCERTAIN.
```
