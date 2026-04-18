# LLM Screening Methodology Notes

This folder collects reading notes on recent papers about LLM-assisted
screening for evidence synthesis.

Purpose:
- distill methodological lessons that are directly useful for our
  title/abstract screening task;
- turn generic "LLM for screening" claims into concrete design decisions
  for this review;
- document practical recommendations before we revise
  [screening_prompt.md](/Users/bogdan.didenko/e-hpc/text-bio-fundational-models-review/protocol/screening_prompt.md)
  and the screening pipeline.

Contents:
- `jmir_prisma_trace_2025_methodology.md`:
  reporting and transparency guidance for AI-assisted systematic reviews.
- `bmc_streamlining_sr_llm_2025_methodology.md`:
  practical pipeline design lessons for title/abstract and full-text
  screening with LLMs.
- `cochrane_ai_position_statement_2025_methodology.md`:
  governance and responsibility guidance for acceptable AI use in evidence
  synthesis.

Working interpretation for this repo:
- prioritize sensitivity over aggressive exclusion;
- preserve `UNCERTAIN` as a deliberate manual-review state;
- prefer question-level logging over a single opaque decision;
- treat prompt iteration and evaluation as protocol artifacts, not
  ad hoc experimentation.
