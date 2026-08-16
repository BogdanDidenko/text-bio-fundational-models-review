I’ll inspect the runbook first, then only the static repository files it explicitly cites. I’ll distinguish documented commands from ambiguities and will not execute any operational command from the procedure.
The runbook defines the routine path as a hash-validated state machine with 18 named stages, and it makes `doctor` authoritative for recovery. I’m continuing through the boundary contracts, manual declarations, backup, publication, and completion sections before checking only the referenced protocol/config/scripts and current cursor.
The published state says `search_end` is `2026-08-09`; with today being `2026-08-16` in `Europe/Kiev`, the default proposed inclusive interval is `2026-08-10` through `2026-08-15`. That interval remains only a proposal until the documented `doctor`, method-lock check, plan, Scholar bundle, and preflight succeed.
Static inspection confirms the orchestrator’s 18-stage order exactly matches the runbook. The screening implementation also exposes a documented v1 contract mismatch at full text: prompts request legacy keys that the strict parser rejects; that is a method-version issue, not something a routine operator may repair.
No operational command below was executed. This is based only on permitted static inspection of the runbook and referenced repository files.

**1. Cursor And Interval**

Authoritative cursor: `data/living_catalog/current.json.search_end = 2026-08-09`.

Next routine inclusive interval:

```text
date_from: 2026-08-10
date_to:   2026-08-15
run_id:    update_2026-08-15
```

`date_from` is the published cursor plus one calendar day. Because the current date is `2026-08-16` in `Europe/Kiev`, `2026-08-15` is the last fully elapsed calendar day. The current day must not be searched. The run report must disclose that no automated retrospective late-indexing lookback exists.

The proposed run directory is currently absent, but only `doctor` and `plan` may establish whether a fresh run is permitted.

**2. Initial Procedure**

These are the exact initial commands I would execute:

```bash
cd /Users/bogdan.didenko/lpnu/review
git status --short --branch
git branch --show-current
git log -1 --format='%H %cI %s'
python3 --version

python3 scripts/run_living_review_pipeline.py doctor

python3 scripts/verify_living_review_method_lock.py \
  --current-taxonomy-tree "$(jq -r .taxonomy_root data/living_catalog/current.json)/taxonomy_tree.json"

END=2026-08-15
RUN_ID=update_2026-08-15

python3 scripts/run_living_review_pipeline.py plan --date-to "$END"

python3 scripts/run_living_review_pipeline.py scholar-capture \
  --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate \
  --date-to "$END"

python3 scripts/run_living_review_pipeline.py preflight \
  --date-to "$END" --through-stage report
```

Proceed only if:

- initial `doctor` is healthy;
- method lock `living-review-v1-frozen-taxonomy-v1` verifies without refresh;
- plan returns `2026-08-10..2026-08-15` and `data/living_catalog_updates/update_2026-08-15`;
- planned prior taxonomy equals the atlas `generated_from`;
- Scholar capture is complete, signed, and validated;
- every required preflight check has `ok: true` and overall `ready: true`;
- the worktree/branch state is understood.

The current static atlas does point to the same taxonomy root as `current.json`, but this does not replace `doctor`.

**3. Eighteen Stages And Boundaries**

Execute the complete state machine with:

```bash
python3 scripts/run_living_review_pipeline.py run \
  --date-to "$END" --manage-server
```

| # | Stage and required input | Success and denominator reconciliation | Failure/recovery |
|---:|---|---|---|
| 1 | `search`: dated config, credentials, validated Scholar bundle | All eight sources and pagination paths complete; raw hits equal sum of completed exports | Resolve access/provider failure; rerun from `search`; never count a failed source as zero |
| 2 | `deduplicate`: eight exports and search summary | `within-update unique = raw hits - duplicate members`; complete cluster/merge ledger | Repair invalid export or unresolved identifier/title conflict; resume stage reported by `doctor` |
| 3 | `prepare-records`: update clusters plus every published master artifact | `new records = within-update unique - cumulative matches/exclusions`; Crossref audit complete | Fill generated cross-dedup declaration; resume `prepare-records` |
| 4 | `enrich-abstracts`: genuinely new records | Every missing/short abstract attempted; kept screening input plus unusable-abstract exclusions equals input | Retry same provider routes; rejected candidates remain logged |
| 5 | `abstract-screening`: title/abstract cohort | One final structured result per input; decision counts sum to screened records | Retry incomplete frozen batches only; no prompt/model/schema substitution |
| 6 | `fulltext-candidates`: final abstract decisions | Candidate IDs are unique and `candidates = INCLUDE + UNCERTAIN` | Correct only through upstream declared resolution path |
| 7 | `fulltext-download`: candidate manifest | Every candidate has exactly one validated PDF/HTML, terminal not-retrieved disposition, or blocking technical disposition | Retry providers or supply declared main article; technical/XML disposition blocks |
| 8 | `docling-screening`: validated supported PDF/HTML subset | Exactly one identity-corroborated no-VLM profile per retrieved supported candidate; terminal non-retrieval remains only in PRISMA | Correct wrong payload from retrieval or rerun Docling |
| 9 | `graph-sections`: complete no-VLM profiles | Each profile has grounded, complete heading-bounded `data_source` and `input_representation` sections | Fill canonical heading override; no pasted evidence or whole-document substitute |
| 10 | `fulltext-screening`: title, abstract, selected sections | Final structured decision for every valid section input | Retry frozen batches or resolve section gate first |
| 11 | `eligibility-resolution`: full-text decisions | No unresolved rows; `accepted + excluded = resolved eligibility inputs` | Fill `manual_resolution.csv`; resume this stage |
| 12 | `docling-vlm`: newly accepted reports with PDFs | Fresh complete VLM profile for every accepted report; `taxonomy records = accepted records with profiles` | HTML-only acceptance requires an authorized PDF and rerun from `fulltext-download` |
| 13 | `taxonomy-discovery`: complete VLM profiles | Every profile processed in open direct discovery; complete route inventory and study/model registry | Retry failed shards unchanged |
| 14 | `taxonomy-classification`: inventory, taxonomy v1, profiles | All profiles succeed; route/evidence parity; Jaccard ≥0.80, family agreement ≥0.90, alpha ≥0.80; every dense candidate adjudicated | Stop; failed threshold requires reviewed whole-cohort rerun, never record-level patching |
| 15 | `crop-validation`: accepted routes and native figures | New models receive a validated crop or explicit `no_suitable_figure`; cumulative ledger retains prior dispositions | Retry failed model batches with identical model/schema; preserve all selector evidence |
| 16 | `snapshot`: prior snapshot plus validated update | Exact route/evidence IDs and counts; `cumulative = prior + accepted update` with duplicate/version linkage | Repair earliest invalid upstream stage; never edit totals |
| 17 | `atlas`: snapshot, prior UI shell, all actual corpus roots | Build counts match snapshot; assets, iteration filter, desktop/mobile and console QA pass | Fix builder/UI, rebuild atlas stage, repeat browser QA |
| 18 | `report`: all stage summaries | All PRISMA identities reconcile; retrieval branches are mutually exclusive | Fix source artifact or generator, never report counts manually |

A zero cohort is valid only after the corresponding upstream stage completed and produced machine-readable evidence. Later stages then create their documented no-change markers.

On any non-zero exit, timeout, interruption, or ambiguous result:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID"

STAGE=FIRST_BLOCKING_STAGE_REPORTED_BY_DOCTOR
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage "$STAGE" --manage-server
```

Do not use `--force` for normal recovery.

**4. Screening Payloads And Topology**

Abstract first-pass model-visible record:

```json
{
  "record_id": "rec_NNNNNN",
  "title": "...",
  "abstract": "...",
  "doi": "...",
  "year": "...",
  "venue": "...",
  "sources": []
}
```

Full-text first-pass model-visible record:

```json
{
  "record_id": "...",
  "candidate_id": "...",
  "source_record_id": "...",
  "source_corpus": "...",
  "title": "...",
  "abstract": "...",
  "doi": "...",
  "year": "...",
  "venue": "...",
  "sources": [],
  "selected_full_text_sections": "complete heading-bounded sections"
}
```

The adjudicator receives the corresponding record plus:

```json
{
  "first_pass_outputs": {
    "scope_reviewer": {},
    "architecture_reviewer": {},
    "python_gate": {}
  }
}
```

Neither `selector_reason`, Graph `section_evidence`, nor complete `docling_markdown` may enter full-text screening.

Topology for both passes:

1. Separate scope-reviewer invocation.
2. Separate architecture-reviewer invocation.
3. Deterministic Python gate.
4. Separate adjudicator only for conflicts or unresolved criteria.

All reviewer/adjudicator invocations use `gpt-5.4-mini`. Abstract screening uses the hash-pinned legacy runner, batch size 8, adjudicator batch size 6, and configured legacy concurrency 64. Full-text screening uses batch size 8, adjudicator batch size 6, 8 workers, 3 attempts, and 1,800-second timeout.

Strict output schemas require:

- Scope: `record_id`, `paper_type`, `bio_modality_present`, `text_component_present`, `text_bio_bridge_present`, `primary_exclusion_code`, `uncertainty_reason`, `decision_rationale`, `evidence_snippet`.
- Architecture: `record_id`, `paper_type`, `generative_model_present`, `foundation_model_evidence`, `primary_exclusion_code`, `uncertainty_reason`, `decision_rationale`, `evidence_snippet`.
- Adjudicator: `record_id`, all six criteria, `primary_exclusion_code`, `uncertainty_reason`, `decision_rationale`, `evidence_snippet`.

Undeclared properties are rejected.

**5. Processing And Reuse Modes**

- **No-VLM Docling:** validated PDF or genuine article HTML; OCR off; accurate table structure and cell matching on; page/picture images on at scale 2.0; formula enrichment off; heading hierarchy from bookmarks, numbering, and style; no text truncation.
- **VLM Docling:** fresh PDF-only conversion for newly accepted reports, model `gpt-5.5`; native JSON, Markdown, source document, figures, captions, and descriptions form one canonical profile. The no-VLM profile cannot be patched into a VLM profile.
- **Docling Graph sections:** `openai/gpt-5.4-mini`, direct extraction, detailed provenance, complete heading-bounded sections for both targets. Root, empty, duplicate, arbitrary-window, and near-whole-document selections are invalid.
- **Taxonomy:** `incremental_frozen_taxonomy`; open direct discovery without family labels, fixed inventory, three direct classifications, dense scoped-fill/standard-dedup audit, separate adjudication, taxonomy v1, temperature 0, no truncation.
- **Crop:** `gpt-5.4-mini`; two blind selectors, separate adjudicator, cropper over native figures. Existing dispositions are retained rather than silently replaced.
- **Snapshot:** incremental merge of immutable prior snapshot and accepted update. A whole-cohort rerun must use the dedicated full-cohort freezer, never a fake empty prior snapshot.
- **Atlas:** copy the last validated UI shell into staging, rebuild from the new snapshot and every real corpus root containing figures, then run local HTTP/browser QA. Published atlas remains unchanged until `publish`.

Reuse rules:

- Hash-valid completed stages are skipped on resume.
- Successful downloads may be reused across retrieval retries.
- A Docling profile is reusable only under matching source/profile hashes and the same lock.
- A Graph workspace additionally requires matching source SHA, Docling JSON SHA, Graph code/contract, model, schema, and stage.
- Changed publisher-source hash means a new profile.
- Preserved failed/recomputed outputs remain evidence but may not be silently mixed into a new attempt.

**6. Archive, Publication, And Verification Commands**

After all 18 stages are complete:

```bash
RUN_ROOT="data/living_catalog_updates/${RUN_ID}"
ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"

python3 scripts/docling/build_input_taxonomy_artifact_manifest.py \
  --artifact-root "$RUN_ROOT"

python3 scripts/archive_living_review_artifacts.py create \
  --source-root "$RUN_ROOT" \
  --archive-root "$ARCHIVE_ROOT" \
  --receipt-dir data/living_catalog/archives \
  --label "$RUN_ID" \
  --storage-class independent_backup

RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"

python3 scripts/archive_living_review_artifacts.py verify \
  --receipt "$RECEIPT" \
  --archive /path/to/copied/archive.tar.zst

python3 scripts/archive_living_review_artifacts.py restore \
  --receipt "$RECEIPT" \
  --destination /empty/path/restored_run

.venv-docling/bin/python scripts/docling/validate_canonical_profile_manifest.py \
  --manifest /empty/path/restored_run/11_docling_vlm/profiles/manifests/canonical_docling_profile_manifest.csv \
  --original-run-root "$RUN_ROOT" \
  --restored-run-root /empty/path/restored_run \
  --expected-records EXPECTED_ACCEPTED_RECORDS

python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
```

Pre-publication and local promotion:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" \
  > "/tmp/${RUN_ID}_status.json"
git diff --check

python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor
```

Then review/stage exactly the permitted publication paths, verify both checkout modes, commit, and deploy:

```bash
git status --short
git diff --check
git add data/living_catalog/current.json
git add "data/living_catalog_updates/${RUN_ID}"
git add docs/input-representation-atlas
git add protocol/PRISMA_protocol.md protocol/prisma_search_screening_log_2026-07-07.md
git status --short
git diff --cached --check
git diff --cached --stat

python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID" \
  --repository-checkout

git commit -m "Update living review through ${END}"
git push origin main

gh run list --workflow deploy-input-representation-atlas.yml --limit 5
gh run watch RUN_ID_FROM_GITHUB --exit-status

COMMIT=$(git rev-parse HEAD)
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets

RELEASE_ROOT="data/living_catalog/releases/${RUN_ID}"
REMOTE_QA="${RELEASE_ROOT}/remote_browser_qa.json"
NODE_PATH="${NODE_PATH:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules}" \
  node scripts/qa_input_representation_atlas.mjs \
  https://bogdandidenko.github.io/text-bio-fundational-models-review/ \
  "$REMOTE_QA"

python3 scripts/run_living_review_pipeline.py doctor
```

The QA script generates `/tmp/atlas-graph-desktop.png` and `/tmp/atlas-graph-mobile.png`. After exact remote verification and visual QA:

```bash
python3 scripts/run_living_review_pipeline.py verify-live \
  --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets \
  --record-completion --workflow-run-id "$GITHUB_RUN_ID" \
  --operator "OPERATOR" --browser-qa-report "$REMOTE_QA" \
  --screenshot /tmp/atlas-graph-desktop.png \
  --screenshot /tmp/atlas-graph-mobile.png

git add "data/living_catalog/releases/${RUN_ID}/completion_record.json"
git diff --cached --check
git commit -m "Record verified release evidence for ${RUN_ID}"
git push origin HEAD
```

After local `publish`, no new review work may begin until the same atlas commit has deployed and passed remote verification. Deployment failure requires retrying the same commit/artifact or an auditable paired state-and-atlas rollback.

**7. Remaining Execution Blockers And Ambiguities**

1. The locked legacy abstract runner synthesizes positional IDs such as `rec_000001`, but `fulltext-candidates` unconditionally requires `04_abstract_screening/record_id_crosswalk.json`. No inspected locked script generates that crosswalk. This would block the routine path after abstract screening: [runner](/Users/bogdan.didenko/lpnu/review/scripts/run_living_review_pipeline.py:1569), [legacy runner](/Users/bogdan.didenko/lpnu/review/analysis/codex_screening_run_artifacts_20260706/pipeline_code/run_codex_screening_pipeline.py:160), [consumer](/Users/bogdan.didenko/lpnu/review/scripts/build_living_review_cohorts.py:145).
2. Full-text prompts demand `evidence_for_*` and `boundary_case`, while the strict schema rejects those properties and instead requires `evidence_snippet`. The runbook correctly identifies this as a method-version issue; an unfamiliar operator cannot lawfully repair it in a routine run.
3. The abstract prompts similarly say to return an exact key set that omits `evidence_snippet`, while appended batch instructions and the strict schema require it. This conflict is not separately acknowledged by the runbook.
4. `/Volumes/INDEPENDENT_BACKUP/...`, `/path/to/copied/archive.tar.zst`, restore destination, and `EXPECTED_ACCEPTED_RECORDS` are unresolved placeholders. Publication cannot pass until a real independent storage destination and restore denominator are declared.
5. `OPERATOR`, `RUN_ID_FROM_GITHUB`, and `GITHUB_RUN_ID` require external values. The runbook does not provide an exact command assigning the selected workflow run ID.
6. The runbook says to inspect and commit the archive receipt, but its explicit staging block omits `data/living_catalog/archives/...`; the exact receipt-staging command is undocumented.
7. `main` is preferred, but no branch-switch/rebase procedure is defined when initial inspection shows another branch. Blindly running `git push origin main` could push a different local branch state.
8. Runtime health, credentials, source access, method-lock validity, independent-storage availability, and dependency checks remain unknown because the required doctor/verifier/preflight commands were deliberately not executed.
9. Automated late-index lookback, a general multi-operator filesystem lock, and a true local/remote two-phase publication transaction do not exist. These documented limitations must remain explicit in the completion report.
