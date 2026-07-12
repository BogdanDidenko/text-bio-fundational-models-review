# Atlas crop cross-validation

The July 11 one-pass crop ledger is retained only as a baseline. The canonical ledger was rebuilt through blind crop review, exact-preview inspection, adversarial input-role checking, and scope-aware adjudication.

## Decision rule

A displayed crop must visibly support at least one grounded route for the exact model. A route-specific input object or representation is sufficient even when the model box is not shown. Shared architecture figures may represent variants that use the same input mechanism, and training/fine-tuning inputs are allowed when the route lifecycle matches. Target-model outputs sent to graders, evaluator prompts, unrelated downstream consumers, performance-only plots, and mismatched routes are excluded.

## Result

- Models accounted for: 111
- Cross-validated displayed crops: 79
- Explicit no-suitable-figure cases: 32
- Two initial blind model decisions per model: 111 + 111
- Initial strong-model adjudications: 37
- Input-role integrity checks: 89
- Input-role scope adjudications: 47
- Post-role exact-preview checks: 81
- Final scope adjudications: 37
- Final changed panels checked and passed: 6

Prompts, schemas, model identifiers, image paths, responses, stdout events, stderr, timestamps, retries, and decisions are retained under `subagents/`. Hidden chain-of-thought is neither stored nor claimed.

## Reproduction commands

Run from the repository root:

```bash
python3 scripts/prepare_atlas_crop_crossvalidation.py
python3 scripts/run_atlas_crop_crossvalidation.py validate-both --batch-size 5 --max-workers 12
python3 scripts/prepare_atlas_crop_adjudication.py
python3 scripts/run_atlas_crop_adjudication.py
python3 scripts/run_atlas_replacement_crops.py --decision-role adjudicator
python3 scripts/build_atlas_crop_crossvalidation_ledger.py
python3 scripts/run_atlas_final_crop_validation.py
python3 scripts/run_atlas_input_role_integrity_validation.py
python3 scripts/run_atlas_input_role_adjudication.py
python3 scripts/run_atlas_replacement_crops.py --decision-role input_role_adjudicator
python3 scripts/build_atlas_post_role_ledger.py
python3 scripts/run_atlas_final_crop_validation.py \
  --manifest post_role_preview_manifest.json \
  --output-role post_role_preview_validator
python3 scripts/run_atlas_input_role_integrity_validation.py \
  --manifest post_role_preview_manifest.json \
  --output-role post_role_input_integrity_validator
python3 scripts/run_atlas_input_role_adjudication.py \
  --review-role post_role_input_integrity_validator \
  --preview-manifest post_role_preview_manifest.json \
  --preview-review-role post_role_preview_validator \
  --output-role post_role_scope_adjudicator \
  --candidate-folder post_role_scope_candidates
python3 scripts/run_atlas_replacement_crops.py \
  --decision-role post_role_scope_adjudicator
python3 scripts/finalize_atlas_post_role_scope.py
python3 scripts/run_atlas_final_crop_validation.py \
  --manifest canonical_changed_preview_manifest.json \
  --output-role canonical_changed_preview_validator
python3 scripts/freeze_atlas_crop_crossvalidation.py
python3 scripts/build_input_representation_atlas.py
```

Intermediate ledgers and panels are intentionally retained. The site builder
uses only `final_crossvalidated_crop_ledger.json`.
