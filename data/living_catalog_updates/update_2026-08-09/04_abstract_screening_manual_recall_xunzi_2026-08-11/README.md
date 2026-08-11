# XunZi manual recall abstract screening

This supplemental run preserves a search-boundary correction without rewriting
the original 285-record screening cohort. The record was present in the raw
Springer Nature export but was excluded before deduplication by the historical
three-block title/abstract validator.

## Reproduction

```bash
python3 analysis/codex_screening_run_artifacts_20260706/pipeline_code/run_codex_screening_pipeline.py \
  --input data/living_catalog_updates/update_2026-08-09/04_abstract_screening_manual_recall_xunzi_2026-08-11/input.json \
  --output-dir data/living_catalog_updates/update_2026-08-09/04_abstract_screening_manual_recall_xunzi_2026-08-11 \
  --model gpt-5.4-mini \
  --batch-size 8 \
  --adjudicator-batch-size 6 \
  --max-workers 64
```

The runner and prompt hashes match the canonical 285-record abstract run:

- runner: `f970db5faad1b718bd2142f4c832088deed60cc5798704ed0ff02bd8ad1ec533`
- scope prompt: `4dbe7ab8d863d4cf07df1858852653005ee72087ea706c53f240ec144d76931a`
- architecture prompt: `f5296132ab4780b441eee56023b2f05459b76f3115cfe49a4f09d4cc896d4346`
- adjudicator prompt: `9509161e046f0fec3d4149f5bb2b68d8302f06ab947dce6edc34f46d6ba2a8b0`
- input: `e3c70c4d434ad85d5d4154a0ce98e0137b556ee3e3a18c9a714bb97e83b84143`
- final result: `67443f07879f5157a107b6390cc17962a035c94594939ae3bdbc3747aba4531f`

## Result

- Scope reviewer: all scope criteria `yes`.
- Architecture reviewer: foundation-model evidence `yes`; generative status
  `unclear` because the abstract describes generated hypotheses but not the
  architecture.
- Python gate: `ADJUDICATE`.
- Adjudicator: all criteria `yes`.
- Final abstract decision: `INCLUDE`.

Prompts, schemas, raw command outputs, parsed responses, evidence snippets, and
brief decision rationales are retained under `role_logs/`. Hidden chain-of-thought
was not requested or stored.

The downstream full-text retrieval audit is in
`../05_fulltext_manual_recall_xunzi_2026-08-11/`.
