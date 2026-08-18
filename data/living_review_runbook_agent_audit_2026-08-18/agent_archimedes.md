No pipeline, network, build, LLM, Docling, or deployment command was executed. This is a read-only simulation based on the [canonical runbook](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/protocol/LIVING_REVIEW_RUNBOOK.md:34), runner, config, and stored state.

**Interval**
Stored [current.json](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/data/living_catalog/current.json) has `search_end=2026-08-09`. On 2026-08-18 in Europe/Kiev, the last fully elapsed day is 2026-08-17.

- Inclusive interval: `2026-08-10` through `2026-08-17`
- Run ID: `update_2026-08-17`
- Run root: `data/living_catalog_updates/update_2026-08-17`
- No manifest currently exists for that run ID.
- Stored atlas `meta.generated_from` matches `current.taxonomy_root`.
- Checkout is clean, on `main`, aligned with `origin/main`.

## Initial Trajectory

```bash
export REVIEW_REPO_ROOT="${REVIEW_REPO_ROOT:-/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review}"
export REVIEW_ARTIFACT_ROOT="${REVIEW_ARTIFACT_ROOT:-/Users/bogdan.didenko/lpnu/review}"
cd "$REVIEW_REPO_ROOT"
test "$(git rev-parse --show-toplevel)" = "$REVIEW_REPO_ROOT"
git status --short --branch
git branch --show-current
git log -1 --format='%H %cI %s'
python3 --version
python3 scripts/run_living_review_pipeline.py doctor
python3 scripts/verify_living_review_method_lock.py \
  --current-taxonomy-tree "$(jq -r .taxonomy_root data/living_catalog/current.json)/taxonomy_tree.json"

END=2026-08-17
RUN_ID=update_${END}

python3 scripts/run_living_review_pipeline.py plan --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to "$END"
python3 scripts/run_living_review_pipeline.py preflight \
  --date-to "$END" --through-stage report
python3 scripts/run_living_review_pipeline.py run \
  --date-to "$END" --manage-server
```

Proceed only if `doctor.healthy=true`, the method lock passes, the plan reports `2026-08-10..2026-08-17`, and every preflight check has `ready=true`. An existing manifest would instead require resume with its fixed dates.

After any nonzero/timeout/ambiguous result:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage STAGE --manage-server
```

`STAGE` must be the literal first blocker reported by `doctor`; never use `--force` for ordinary recovery.

## Scientific Stages

| Stage and resume literal | Prerequisite, output, gate, and recovery |
|---|---|
| `search` | Requires validated Scholar bundle plus credentials for all eight enabled providers: PubMed, Scopus, OpenAlex, Semantic Scholar, arXiv, bioRxiv/medRxiv, SpringerNature, Scholar. Produces `00_search/search_config.json` and `exports/search_summary_2026-08-17.json`. All pagination and provider states must be complete. On failure inspect `search_completion_gate.json`, restore access or rerun `scholar-capture`, then resume `search`; never record failure as zero. |
| `deduplicate` | Requires reconciled search totals. Produces `01_dedup/deduplicated_records.json`, statistics, merge evidence, and review queue. Raw hits must equal completed exports; identifier/title conflicts cannot be silently collapsed. Repair only invalid upstream evidence, then resume `search` or `deduplicate` as `doctor` directs. |
| `prepare-records` | Compares DOI, PMID, arXiv/bioRxiv IDs and normalized titles against every `current.master_record_files` entry. Produces the cumulative match audit and `02_records/new_records_after_cross_dedup_crossref_checked.json`. Conflict input is only `manual_cross_dedup_resolutions.json`, copied from its generated template; then resume `prepare-records`. |
| `enrich-abstracts` | Requires the new-record cohort. Produces `03_abstracts/abstract_screening_input.json` and unusable-abstract exclusions. Every missing abstract must be attempted; title-only fallback requires year/author corroboration. Retry the same stage/providers without promoting diagnostics. |
| `abstract-screening` | Requires frozen runner, prompts, schema, `gpt-5.4-mini`, and enriched input. Produces final structured results, summary, logs, and stable-ID crosswalk. Every row needs a final decision. Retry incomplete batches through `abstract-screening`; no prompt/model substitution or manufactured rows. |
| `fulltext-candidates` | Requires all abstract results. Raw candidates must equal `INCLUDE + UNCERTAIN`; output is `05_fulltext/fulltext_candidates.json`. Optional removal is supported only through `postscreen_dedup/duplicate_resolutions.json`; absence means none. Resume this stage after a lawful declaration. |
| `fulltext-download` | Each candidate must have exactly one validated PDF/HTML, terminal evidence-backed not-retrieved status, or blocking technical disposition. Outputs download manifest and `fulltext_retrieval_dispositions.json`. The only manual payload route is `manual_fulltexts.json` from its generated template. Resume `fulltext-download`; abstract pages, supplements, XML-only pages, and renamed files are invalid. |
| `docling-screening` | Only validated supported payloads enter locked no-VLM Docling. Produces one identity-corroborated profile per retrieved candidate, the canonical profile manifest, and retrieved-candidate subset. Wrong/corrupt source requires correction at `fulltext-download`; conversion failure resumes `docling-screening`. |
| `graph-sections` | Requires complete no-VLM profiles and the locked Graph contract. Produces Graph workspaces, provenance, metadata, and complete heading-bounded `data_source` and `input_representation` sections. Graph execution failures resume here. Missing valid pairs become a gate in the next stage. |
| `fulltext-screening` | Requires valid section pairs. Missing pairs may be supplied only in `08_section_input/manual_section_overrides.json` using exact canonical Markdown hash and heading trails from its template; then resume `fulltext-screening`. Produces final section-screening results using title, abstract, and selected sections only. |
| `eligibility-resolution` | Requires complete full-text decisions. Produces accepted, excluded, and unresolved ledgers. Every unresolved row must be resolved only through `10_eligibility/manual_resolution.csv` with decision, evidence rationale, resolver, and timestamp; then resume this stage. |
| `docling-vlm` | Only newly accepted records enter. Every accepted report must have an authorized main-article PDF; accepted HTML-only records block and require `manual_fulltexts.json`, followed by resume from `fulltext-download`. Produces fresh canonical VLM profiles containing native JSON, Markdown, figures, captions, and picture descriptions. |
| `taxonomy-discovery` | Requires all canonical VLM profiles. Open discovery sees full profiles without frozen labels and produces route inventory and study/model registry under `12_taxonomy`. Retry failed documents with unchanged model/schema. Zero accepted records produce an explicit no-new-record marker. |
| `taxonomy-classification` | Runs three direct classifications, dense coverage, adjudication, grounding, and F6. Requires Jaccard `>=0.80`, family agreement `>=0.90`, alpha `>=0.80`, complete route coverage, and an empty F6 action queue. Any agreement failure requires a reviewed whole-cohort bridge/rerun, not selected-record recoding. An F6 queue blocks snapshot; generated route files must not be edited. |
| `crop-validation` | Runs two selectors, adjudication, exact rendering, both F7 roles, adjusted-crop review, exhaustive replacement rounds, input-role review, and isolation audit. Only zero-unresolved `proposed_crossvalidated_crop_ledger.json` is promoted. Resume `crop-validation` for technical failure; unresolved cases remain blocking and no hand-edited crop is supported. |
| `snapshot` | Requires passing F6/F7 and exact route/evidence/crop parity. Produces cumulative `14_snapshot/snapshot_manifest.json` and crop ledger, preserving prior records plus the accepted update. Repair the earliest invalid stage; never edit totals. Zero accepted records produce `no_catalog_change.json`. |
| `atlas` | Builds staged `15_atlas` from the snapshot and all actual corpus roots. Produces `atlas.json`, build report, assets, browser QA, and desktop/mobile screenshots. Counts, review-iteration filter, assets, responsive views, and console checks must pass. Fix builder/UI code, resume `atlas`, and repeat QA. |
| `report` | Re-derives every PRISMA denominator and mutually exclusive retrieval branch. Produces `16_report/prisma_update_facts.json`, retrieval ledgers, and `update_report.md`. Fix source evidence or generator and resume `report`; never edit counts manually. |

Every successful stage becomes `complete` with SHA-256 inventory in `run_manifest.json`. Manual gates become `needs_manual_resolution`; failures become `failed`. Attempts remain under `logs/STAGE/attempt_NNN/`.

## Manual Inputs

The only supported scientific manual declarations are:

- `00_search/google_scholar_provider_export.json`, normally generated by the locked `scholar-capture`; another provider is not comparable under method v1.
- `02_records/manual_cross_dedup_resolutions.json`
- `05_fulltext/postscreen_dedup/duplicate_resolutions.json`, optional
- `05_fulltext/manual_fulltexts.json`
- `08_section_input/manual_section_overrides.json`
- `10_eligibility/manual_resolution.csv`

Each must follow its generated template/schema. Generated results, Markdown, route annotations, counts, crop ledgers, and cursor state are never manual-input surfaces. F6 and F7 expose no routine human declaration file.

## Preservation And Archive

Before recomputation, existing Docling profiles, Graph workspaces, taxonomy runs, adjudication, and crop outputs are moved to `preserved_stage_outputs/STAGE/attempt_NNN/` and recorded in `preservation_ledger.jsonl`. Successful downloads may be reused. Docling/Graph reuse requires matching source/profile hashes and the identical locked contract; evidence is never silently mixed across attempts.

After all 18 stages are hash-valid:

```bash
RUN_ROOT="data/living_catalog_updates/${RUN_ID}"
ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"

python3 scripts/docling/build_input_taxonomy_artifact_manifest.py \
  --artifact-root "$RUN_ROOT"
python3 scripts/archive_living_review_artifacts.py create \
  --source-root "$RUN_ROOT" --archive-root "$ARCHIVE_ROOT" \
  --receipt-dir data/living_catalog/archives --label "$RUN_ID" \
  --storage-class independent_backup
RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
```

The example `/Volumes/INDEPENDENT_BACKUP` mount is currently absent. Publication must stop until a genuine independent location is mounted and verified. Do not regenerate `artifact_manifest.csv` after publication.

## Publish And Completion

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
git diff --check
python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor
```

`publish` atomically updates the local atlas and `current.json`, advancing `search_end` to `2026-08-17`; it does not deploy Pages. Freeze subsequent review work.

Stage only the paths listed in the manual, verify the archive and both checkout modes, commit, fetch `origin/main`, require ancestry, and push `HEAD:main`. Then identify and watch the workflow for that exact commit and run:

```bash
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

For a zero-accepted cohort, the atlas must remain byte-identical and the Pages workflow must be manually dispatched for the new commit.

After remote bytes, assets, commit binding, desktop/mobile QA, and screenshots pass:

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
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
git push origin HEAD:main
```

The final healthy `doctor` should report the next cursor start as `2026-08-18`.

## Audit Result

**First exact command:**

```bash
export REVIEW_REPO_ROOT="${REVIEW_REPO_ROOT:-/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review}"
```

**Next routine run:** `2026-08-10..2026-08-17`, `update_2026-08-17`. After its completion, the following interval starts `2026-08-18`; its end and run ID cannot be determined until a future execution date.

**Material risks and ambiguities:**

- F6 gives versioned-correction commands only in the whole-cohort rerun context; it does not define how a corrected taxonomy is reintegrated into this routine run’s manifest and snapshot path.
- F7 says to retry failed model batches, but the runner exposes only whole-stage resume and no manual remediation declaration.
- A Scholar failure before `run` may leave files but no manifest, so `doctor --run-id` can select the prior published run rather than the failed pre-run capture.
- `scholar-validate` is called “read-only-capable,” but on an unpublished run it may create search config and validation files.
- The documented restore validator directly invokes `.venv-docling/bin/python`; that path is absent in the canonical checkout even though the resolver can find the environment under the artifact root.
- Local publication and Pages deployment are not transactional; there is no multi-operator lock or automated late-index lookback.
- The frozen screening prompts and strict schemas contain documented key mismatches. The parser resolves authority, but failures cannot be repaired without method versioning.

**Verdict: PASS WITH RISKS.** The manual gives a reproducible happy path, rigorous gates, and safe stopping behavior. It does not provide a fully executable routine recovery path for non-empty F6/F7 scientific action queues, and publication still depends on disciplined external coordination.
