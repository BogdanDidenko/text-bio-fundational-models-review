# Operative Prompt Templates

This folder contains the **canonical runtime prompt artifacts** for the
criterion-by-criterion screening workflow.

These files exist so that:

- the exact prompt stack can be versioned and reported in the paper;
- the screening runner does not hardcode operative prompt text;
- methodological prompt notes in `protocol/screening_prompts/` do not drift away
  from the prompts that are actually executed.

## Runtime-loaded files

The local screening runner loads these files directly:

- [scope_reviewer_prompt.txt](scope_reviewer_prompt.txt)
- [architecture_reviewer_prompt.txt](architecture_reviewer_prompt.txt)
- [adjudicator_prompt.txt](adjudicator_prompt.txt)

The templates use `{{...}}` placeholders for evidence-source wording. The
runner renders them with `--evidence-mode`:

- `title_abstract` (default): renders to the original title/abstract wording
  and sends only title, abstract, and metadata fields to reviewers.
- `full_text_sections`: renders to selected-full-text-section wording and sends
  title, abstract, and the complete `selected_full_text_sections` text. The
  structured `section_evidence` and `docling_markdown` fields remain in the
  input records for auditability but are not sent to reviewers.

The reviewer topology, criterion fields, allowed values, Python gate, and
adjudicator logic are shared across both modes. Only the evidence input profile
and prompt wording change.

## Design notes

In default `title_abstract` mode the rendered templates are intentionally:

- criterion-by-criterion rather than one-shot;
- sensitivity-first rather than aggressive auto-exclusion first;
- grounded in title/abstract evidence only;
- conservative about `unclear`;
- stricter about wrapper papers, benchmark/resource papers, and non-generative
  systems.
- explicit about recurring boundary cases that produced unstable replicate
  decisions: external-LLM wrappers, biological-token-only "language" models,
  thin abstracts, and predictive systems without stated generation.

Reviewer-role text is now embedded directly inside each reviewer prompt file
rather than stored in a separate `backstory` file. This keeps the operative
reviewer prompt easier to read and easier to report verbatim in the paper.

The current local screening runner also suppresses the extra LatteReview
system-wrapper layer so that these reviewer prompt files are the self-contained
operative prompt artifacts.

## Stability and audit fields

The runtime schema asks reviewers to emit short evidence fields for the text
component, text-bio bridge, and generative-model evidence, plus a `boundary_case`
label. These fields are not additional inclusion criteria. They make borderline
decisions auditable and make replicate disagreements easier to diagnose.

Prompt regression cases are tracked in
[`../screening_prompt_regression_cases.csv`](../screening_prompt_regression_cases.csv).
They are sampled from benchmark boundary records, stable INCLUDE records, and
cases whose INCLUDE/UNCERTAIN/EXCLUDE decisions changed across repeated
DeepSeek runs.
