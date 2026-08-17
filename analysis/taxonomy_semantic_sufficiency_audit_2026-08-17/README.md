# F6 semantic sufficiency audit

This audit tests whether complete canonical Docling Markdown semantically supports every material field of the dense-only or inferred routes. It does not alter the canonical taxonomy output.

- Records audited: **18**
- Routes audited: **95**
- Routes sent to adjudication: **66**
- Retain as-is: **45**
- Change or manual review recommended: **50**
- Model for all roles: `gpt-5.4-mini`
- Evidence input: complete canonical Docling Markdown, without truncation
- Validation: every returned supporting quote was matched against the canonical Markdown
- Interpretation: repeated computational review with LLM adjudication, not human ground truth

## Final sufficiency

- `insufficient`: 4
- `partial`: 46
- `sufficient`: 45

## Recommended actions

- `manual_full_text_review`: 4
- `retain_as_is`: 45
- `revise_fields`: 46

Detailed route-level decisions are in `semantic_sufficiency_dispositions.jsonl`; exact prompts, schemas, responses, stdout, stderr, retries, commands, hashes, and timings are retained under `runs/`.
Routes requiring a change or manual review are flattened into `semantic_sufficiency_action_queue.csv` for correction work.
Aggregate field and record-level patterns are documented in `semantic_sufficiency_failure_modes.md`.
