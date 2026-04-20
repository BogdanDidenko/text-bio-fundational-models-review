# Architecture Reviewer Prompt

## Purpose

This reviewer handles the architecture and foundation-model side of the same
title/abstract record.

Primary questions:

5. `generative_model_present`
6. `foundation_model_evidence`

It can also mark the record as `application_wrapper` when the abstract clearly
describes a downstream wrapper around an existing model.

## Structured Output

The reviewer returns exactly one JSON object with these keys:

- `paper_type`
- `generative_model_present`
- `foundation_model_evidence`
- `primary_exclusion_code`
- `uncertainty_reason`
- `decision_rationale`

Allowed values:

- `paper_type`: `primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear`
- `generative_model_present`: `yes | no | unclear`
- `foundation_model_evidence`: `yes | no | unclear`

## Prompt Assembly

### Generic prompt

```text
Review the title/abstract record below for systematic-review screening of text-bio foundational models.

Return exactly one JSON object with these keys:
- paper_type
- generative_model_present
- foundation_model_evidence
- primary_exclusion_code
- uncertainty_reason
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- generative_model_present: yes | no | unclear
- foundation_model_evidence: yes | no | unclear

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
Answer criterion questions 5-6 for title/abstract screening:
(5) generative_model_present, (6) foundation_model_evidence.
Use paper_type=application_wrapper if the abstract makes clear that the work is only a wrapper around an existing model.
```

### Reviewer-specific rules

```text
Focus on architecture and FM evidence. Predictive models, profile prediction systems, and downstream classifiers are not generative unless the abstract explicitly says decoder/autoregressive/seq2seq/diffusion/generative. Encoder-only and unclear architectures are not positive evidence for inclusion. If the paper may simply wrap an existing LLM or the architecture is underspecified, use unclear rather than forcing yes. Do not answer bio_modality_present, text_component_present, or text_bio_bridge_present.
```

### Shared context

```text
Key boundaries for this review:
- Strong include-style patterns: explicit text-to-bio or bio-to-text bridge, text-guided omics generation/alignment, or biological-token generative FM.
- Strong exclude-style patterns: review/editorial papers, benchmark/resource papers, application wrappers around an existing LLM, encoder-only models, and bio-only multimodal systems with no real text bridge.
- Predictive profile/score outputs are not generative by default; do not mark generative_model_present=yes unless the abstract clearly describes decoder/autoregressive/seq2seq/diffusion/generative behavior.
- If the abstract is very short, snippet-like, or insufficient to resolve architecture or scope, prefer UNCERTAIN.
```
