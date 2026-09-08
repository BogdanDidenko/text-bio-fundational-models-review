# P030 candidate-order correction

Date: 2026-09-08. Record: `full_2026-07-06__rec_001617`.
Route: `route_8db6326aa3e2`, OpenAI o1 / CellPuzzles batch-level prompt.

The author authorized correction of the candidate-order description in the card
and repository analysis record. This log records that bounded amendment.
The remaining P030 audit judgments are still held; no full human validation or
new category decision is inferred from the correction request.

## Before and after

| Item | Description |
|---|---|
| Original article-derived step | `shuffle the candidate cell types` |
| Reviewed description | Alphabetically sort candidate cell types in the published QA builder; historical o1 request ordering remains unverified |
| Source discrepancy retained | The article reports shuffling, while the published implementation sorts the visible candidate list |

The model-visible biological content, carrier family, subtype, lifecycle,
input status and route identity are unchanged by this amendment.

## Evidence

The [canonical article text](../../data/docling_include_vlm_52_2026-07-10_nolimits/markdown/full_2026_07_06_rec_001617.md)
reports shuffled candidate labels at line 61. Section 4.2.1, line 99, links o1
distillation to the standardized prompt in Table 1.

The archived author file [sources/match_qa.py](sources/match_qa.py) is from
commit `fe43d11295b3d9c18fbf37047e9abc4680e2ccc0`:

- Lines 41-48 randomly select cell types and corresponding cells.
- Lines 56-64 build numbered gene lists and an alphabetically sorted candidate list.
- Line 66 keeps the answer in cell order.

The decisive [published statement at line 64](https://github.com/ncbi-nlp/cell-o1/blob/fe43d11295b3d9c18fbf37047e9abc4680e2ccc0/data/match_qa.py#L64)
is `sorted(chosen_types)`. Random cell selection and candidate display order are
distinct operations. No historical o1 API request was replayed or independently
authenticated in this review. The correction therefore retains an explicit limit
on historical attribution.

## Preservation of original logs

The original agent prompts, replies, decisions and frozen inventories remain
unchanged. Relevant retained provenance includes:

- [Full-cohort adjudication for this paper](../../data/living_catalog/taxonomy_rerun_preflight_2026-08-12/taxonomy/adjudication/shard_02/records/full_2026-07-06__rec_001617_76b0056d59c3/adjudicated_routes.json).
- [Frozen 55-record route inventory](../../data/living_catalog/taxonomy_rerun_preflight_2026-08-12/snapshot_full_55_semantic_correction_2026-08-17/route_annotations.jsonl).
- [Dated reviewed-view amendment](../../data/input_representation_audit_amendments/2026-09-08_p030_candidate_order.json).

`transformation_chain_verbatim` retains the original reported claim.
`reviewed_transformation_chain` contains the annotated description displayed by
the current card. The new text is not represented as a verbatim article quote.
The card retains the earlier statement in its expandable review history, with
separate links to the article, code and this correction log.

## Audit boundary

The complete original candidate remains subject to the recorded paper/code
discrepancy. The preceding source review recommended `partial` for support of
that entire assertion. Correcting the displayed description does not upgrade
the historical assertion to fully supported. The v16 audit workbook and its
original candidate/quote remain unchanged in this bounded update. The taxonomy,
PRISMA counts, P023 uncertainty and all other routes are preserved.

## Verify

```sh
python3 analysis/input_taxonomy_p030_candidate_order_2026-09-08/verify.py
python3 scripts/apply_atlas_review_amendments.py --check
```

The verifier checks the source hashes and code ordering without executing author
code. `verification.json` identifies the checked snapshot and preserved inputs.
