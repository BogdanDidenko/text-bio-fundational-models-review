# Operative Prompt Templates

This folder contains the **canonical runtime prompt artifacts** for the
criterion-by-criterion title/abstract screening workflow.

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

## Reporting file

This file documents the generic system-prompt wrapper produced by LatteReview's
`BasicReviewer`:

- [lattereview_system_prompt_template.txt](lattereview_system_prompt_template.txt)

It is included for transparency and reporting. The current runner does not load
this file directly because the system prompt is constructed internally by
LatteReview from reviewer metadata and the response schema.

## Design notes

The current templates are intentionally:

- criterion-by-criterion rather than one-shot;
- sensitivity-first rather than aggressive auto-exclusion first;
- grounded in title/abstract evidence only;
- conservative about `unclear`;
- stricter about wrapper papers, benchmark/resource papers, and non-generative
  systems.

Reviewer-role text is now embedded directly inside each reviewer prompt file
rather than stored in a separate `backstory` file. This keeps the operative
reviewer prompt easier to read and easier to report verbatim in the paper.
