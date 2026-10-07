# Corpus-wide operation decomposition (51 remaining included papers)

Extends the reviewed four-paper operation-constructor pilot (ChatNT, InstructCell, X-Cell,
MUPAD) to every other paper in the 55-record included set. No search refresh is part of
this step: the corpus is the current included set in `docs/input-representation-atlas/data/atlas.json`.

## Agents

Native `codex exec` (console CLI, not an API client), with the same invocation as
`scripts/run_taxonomy_semantic_correction.py`: read-only sandbox in an empty temporary
workspace, `--ephemeral`, shell and other tools disabled, prompt on stdin, strict
`--output-schema`. Default model `gpt-5.4-mini` for both roles, the repo's standard Codex
model for text roles (screening, graph route/section extraction, taxonomy correction; see
`protocol/LIVING_REVIEW_RUNBOOK.md`). `--model` / `--review-model` override it.

Per paper:
1. **Extractor** gets the shared protocol (`protocol/REPRESENTATION_LIBRARY_GUIDE.md`), the
   pinned operation catalog, one reviewed pilot trajectory as a worked example, the atlas
   models for the record as a coverage checklist, and the complete full-text packet.
2. **Mechanical validation** (`scripts/operation_decomposition.py`): verbatim quote match in
   the cited section, known sections, catalog operation IDs and ports, every declared
   parameter present (`unspecified` when not established), every step operand consumed and
   result produced, no mixed boundary/library steps, Pydantic contracts, lossless source
   restoration. Errors are returned to the extractor (up to 2 repairs).
3. **Independent reviewer** in a fresh context audits each step against its quotes and
   flags blocking/minor findings plus coverage gaps.
4. **Revision**: blocking findings return to the extractor, then validation and a second
   review. Remaining blocking findings are kept and the record is marked
   `accepted_with_open_findings`.

## Packets

`build_packet()` reproduces the pilot's section scheme exactly (verified on all 89 pilot
evidence items: section hash, quote offset and heading path). Sources are the canonical
Docling VLM Markdown already in the repo (52 records from
`data/docling_include_vlm_52_2026-07-10_nolimits/markdown`, 3 from the 2026-08-09 update).
Packets are complete; nothing is truncated.

## Run

```bash
export PYTHONPATH=$PWD
python3 scripts/run_operation_decomposition.py --dry-run          # packets + prompts only
python3 scripts/run_operation_decomposition.py --limit 2          # smoke test, 2 papers
python3 scripts/run_operation_decomposition.py --max-workers 4    # all 51; resumable
python3 scripts/run_operation_decomposition.py --retry-failed     # re-run failed records only
python3 scripts/build_operation_corpus.py                         # collect accepted records
# steward: bump operation_catalog.json release to 1.1.0, then
python3 scripts/build_representation_library.py --freeze
python3 -m pytest tests/test_operation_decomposition.py tests/test_representation_library.py
```

Every attempt keeps `prompt.txt`, `output_schema.json`, `response.json`, `stdout.jsonl`,
`stderr.log` and `meta.json` under `records/<record_id>/attempts/`. `corpus_status.json`
summarizes statuses, call counts, unexpanded boundaries, open findings and operation
proposals for the library steward.

## Acceptance

Only `accepted` records enter `corpus_assemblies.json` by default
(`--include-open-findings` adds the rest). The release build refuses to overwrite a frozen
release, so publishing requires a new catalog release. Agent output is a reviewed
candidate reconstruction: source entailment of each graph remains the authors' scientific
review responsibility, as for the pilot. The withdrawn OKR-Cell preprint
(`full_2026-07-06__rec_001277`) is decomposed like the others and labelled
`(WITHDRAWN source)`, but it is published only with `build_operation_corpus.py --include-withdrawn`
(it is currently the page's supplemental binning example); keeping it in the review is an open author decision.
