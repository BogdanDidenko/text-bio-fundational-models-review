# Canonical Full-Text-Section Screening Run

This directory is the final valid second-stage screening artifact for the
2026-07-10 targeted full-text evidence pass. It supersedes discarded
exploratory runs that rendered whole-document markdown or duplicated the
selected section text in prompts.

## Input contract

Each first-pass model call received the record title, abstract, and complete
`selected_full_text_sections`, plus stable technical IDs for output mapping.
The full `docling_markdown` and structured `section_evidence` fields were kept
in the source input for audit but were not rendered into the first-pass prompt.
The adjudicator additionally received the structured first-pass outputs.

## Final result

| Metric | Count |
|---|---:|
| Input records | 221 |
| Scope outputs | 221 |
| Architecture outputs | 221 |
| Adjudicated records | 67 |
| INCLUDE | 50 |
| EXCLUDE | 165 |
| UNCERTAIN | 6 |

All retained `batch_*.meta.json` records have `status: ok`. Logs preserve the
exact prompt, raw final response, schema-validated response, and runtime
metadata for each call. They preserve short rationales and evidence snippets,
not hidden chain-of-thought.

## Human-confirmed resolution layer

The six automated `UNCERTAIN` records were subsequently inspected against the
relevant full Docling sections and confirmed by the review lead. The original
automated artifacts above are immutable. The append-only manual layer is:

- `manual_resolution_2026-07-10.md` -- evidence-grounded decision rationale;
- `manual_resolution_2026-07-10.csv` -- machine-readable six-record mapping.

The manual layer resolves two records to `INCLUDE` and four to `EXCLUDE`, giving
the current eligibility checkpoint of 52 INCLUDE, 169 EXCLUDE, and 0 UNCERTAIN
among the 221 records. It is not a replacement for later data extraction or
model-level duplicate handling.

See `protocol/full_text_section_screening_2026-07-10.md` for the complete
method, section-quality controls, and PRISMA checkpoint.
