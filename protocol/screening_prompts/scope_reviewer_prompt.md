# Scope Reviewer Prompt

## Purpose

This reviewer handles the first four title/abstract screening questions:

1. `paper_type`
2. `bio_modality_present`
3. `text_component_present`
4. `text_bio_bridge_present`

It is the first-pass scope gate for the current `LatteReview` workflow.

## Structured Output

The reviewer returns exactly one JSON object with these keys:

- `paper_type`
- `bio_modality_present`
- `text_component_present`
- `text_bio_bridge_present`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

Allowed values:

- `paper_type`: `primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear`
- `bio_modality_present`: `yes | no | unclear`
- `text_component_present`: `yes | no | unclear`
- `text_bio_bridge_present`: `yes | no | unclear`

## Prompt Assembly

### Generic prompt

```text
Review the title/abstract record below for systematic-review screening of text-bio foundational models.

Return exactly one JSON object with these keys:
- paper_type
- bio_modality_present
- text_component_present
- text_bio_bridge_present
- primary_exclusion_code
- uncertainty_reason
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- bio_modality_present: yes | no | unclear
- text_component_present: yes | no | unclear
- text_bio_bridge_present: yes | no | unclear

Global decision policy:
- Use a sensitivity-first title/abstract screening strategy.
- If a key criterion cannot be resolved from the abstract, use UNCERTAIN rather than forcing EXCLUDE.
- Review/editorial, benchmark/resource, and application/wrapper papers are not primary in-scope model papers.
- Encoder-only biological token models are out of scope.
- Biological-token generative models may be in scope if the architecture is clearly generative and FM-like.
- If a paper only uses embeddings, metadata descriptions, prompts, or outputs from an existing LLM as auxiliary features for downstream bio tasks, classify it as application_wrapper unless the abstract clearly presents a new joint text-bio generative foundation model.
- Benchmark/resource papers evaluating LLMs or DNA/protein language models are not in-scope primary model papers.
- Return a short rationale, not a long essay.
- Do not invent a final include/exclude label. Answer only the criterion fields requested for this reviewer.
```

### Reviewer-specific task

```text
Answer criterion questions 1-4 for title/abstract screening:
(1) paper_type, (2) bio_modality_present, (3) text_component_present,
(4) text_bio_bridge_present.
```

### Reviewer-specific rules

```text
Focus on scope and publication type. Treat review/editorial, benchmark/resource, and application_wrapper papers as out of scope. Mark text_bio_bridge_present=no when the abstract only describes using an existing LLM or language embeddings as side information for downstream bio tasks rather than a genuine joint text-bio model. If the bridge cannot be established from the abstract, use unclear. Do not answer generative_model_present or foundation_model_evidence.
```

### Shared context

```text
Key boundaries for this review:
- Strong include-style patterns: explicit text-to-bio or bio-to-text bridge, text-guided omics generation/alignment, or biological-token generative FM.
- Strong exclude-style patterns: review/editorial papers, benchmark/resource papers, application wrappers around an existing LLM, encoder-only models, and bio-only multimodal systems with no real text bridge.
- Predictive profile/score outputs are not generative by default; do not mark generative_model_present=yes unless the abstract clearly describes decoder/autoregressive/seq2seq/diffusion/generative behavior.
- If the abstract is very short, snippet-like, or insufficient to resolve architecture or scope, prefer UNCERTAIN.
```
