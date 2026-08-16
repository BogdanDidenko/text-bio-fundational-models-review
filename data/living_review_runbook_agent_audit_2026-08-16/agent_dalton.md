I’ll inspect only the runbook and static files it explicitly references. I will not run any operational command from the procedure or touch repository state; the final response will present those commands as an unexecuted dry run.
The runbook defines the routine path as an 18-stage state machine and makes `current.json`, the method lock, and generated gate templates authoritative. I’m now extracting the published cursor, locked configuration, and protocol-defined reviewer payloads so the dry run does not invent details that the operator guide delegates elsewhere.
Static state shows the published cursor is `2026-08-09`, and the atlas currently points to the same corrected taxonomy snapshot named by `current.json`. The next routine interval is therefore `2026-08-10` through `2026-08-15` inclusive, but the runbook requires a real `doctor` result before accepting that plan; this dry run cannot establish doctor health.
The screening implementation reveals an important distinction the prose compresses: the scientific evidence fields are locked to `title + abstract` (plus complete selected sections at full text), while the serialized transport object also carries stable identifiers and bibliographic metadata. I’ll report that distinction explicitly, along with the resulting documentation ambiguity, instead of calling the larger JSON object “exactly title + abstract.”
A second protocol issue is emerging at the method boundary: abstract screening uses the hash-pinned legacy runner, but full-text screening calls a different runner. I’m checking whether that runner and its prompt/schema sources are actually covered by the executable method lock, because comparability depends on that rather than on the prose alone.
# Silent Dry Run

No operational command below was executed. This assessment used only read-only inspection of the runbook and referenced repository files.

## 1. Cursor And Interval

Authoritative state: [current.json](/Users/bogdan.didenko/lpnu/review/data/living_catalog/current.json).

- Published inclusive cursor: `search_end = 2026-08-09`.
- Next `date_from`: `2026-08-10`, exactly one calendar day later.
- Current date in `Europe/Kiev`: `2026-08-16`.
- Last fully elapsed local calendar day: `2026-08-15`.
- Next inclusive interval: **`2026-08-10` through `2026-08-15`**.
- Proposed run ID: **`update_2026-08-15`**.
- No directory for that run ID currently exists in the inspected static state.
- The current atlas points to the same taxonomy snapshot as `current.json`, with 55 records, 54 studies, 109 models, 468 configurations, and 586 routes.

The end date excludes the unfinished current day. The report must disclose that no automated retrospective lookback exists for records indexed late into a closed interval.

## 2. Unexecuted Initial Commands

```bash
cd /Users/bogdan.didenko/lpnu/review
git status --short --branch
git branch --show-current
git log -1 --format='%H %cI %s'
python3 --version
python3 scripts/run_living_review_pipeline.py doctor
python3 scripts/verify_living_review_method_lock.py --current-taxonomy-tree "$(jq -r .taxonomy_root data/living_catalog/current.json)/taxonomy_tree.json"

END=2026-08-15
RUN_ID="update_${END}"
RUN_ROOT="data/living_catalog_updates/${RUN_ID}"

python3 scripts/run_living_review_pipeline.py plan --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to "$END"
python3 scripts/run_living_review_pipeline.py preflight --date-to "$END" --through-stage report
python3 scripts/run_living_review_pipeline.py run --date-to "$END" --manage-server
```

Stop before `plan` unless `doctor` is healthy and method-lock verification passes. Accept the plan only if it reports `date_from=2026-08-10`, `date_to=2026-08-15`, the expected run root, the current corrected taxonomy root, and `ready: true` for every required preflight check.

After any interruption, nonzero exit, timeout, or ambiguous state:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
STAGE="FIRST_BLOCKING_STAGE_FROM_DOCTOR"
python3 scripts/run_living_review_pipeline.py run --run-id "$RUN_ID" --from-stage "$STAGE" --manage-server
```

`--force` is not routine recovery.

## 3. Ordered 18-Stage Procedure

| # | Stage | Required input and success condition | Denominator reconciliation | Failure/recovery |
|---:|---|---|---|---|
| 1 | `search` | Dated v3.3 config; complete PubMed, Scopus, OpenAlex, Semantic Scholar, arXiv, Europe PMC bioRxiv/medRxiv, SpringerNature, and signed Google Scholar exports. All pages/interfaces must terminate normally. | `raw hits = sum(completed source exports)`. A failed source is not zero. | Restore credentials/provider access or matching Scholar capture; resume `search`. |
| 2 | `deduplicate` | Eight completed exports; conservative DOI, PMID, preprint-ID, then title clustering with complete merge ledger. | `within-update unique = raw hits - duplicate members`; conflicting published DOIs stay separate. | Repair invalid export upstream or resume `deduplicate`; do not manually merge generated output. |
| 3 | `prepare-records` | Dedup clusters plus every published master artifact; Crossref audit and resolved cross-version conflicts. | `within-update unique = cumulative matches/exclusions + new records`. | Fill generated `manual_cross_dedup_resolutions.json`; resume this stage. |
| 4 | `enrich-abstracts` | New records; every missing/short abstract attempted through declared identifier/title routes. | `new records = screening input + below-threshold/no-usable-abstract exclusions`. | Retry same providers; rejected candidates remain logged. Bounded diagnostic output is not canonical. |
| 5 | `abstract-screening` | Frozen title/abstract runner, prompts, model, and schema; final structured decision per input. | Input count equals final `INCLUDE + EXCLUDE + UNCERTAIN`. | Retry incomplete batches with identical artifacts; never combine prompt/model versions. |
| 6 | `fulltext-candidates` | Final abstract decisions and stable-ID crosswalk. | Candidates equal abstract `INCLUDE + UNCERTAIN`, one row per unique candidate. | Correct only through upstream resolution paths. |
| 7 | `fulltext-download` | Candidate metadata and lawful OA/manual retrievals; one mutually exclusive disposition each. | Candidates equal PDF + HTML + preexisting reuse + terminal `not_retrieved*`; technical/XML dispositions must be zero before success. | Retry provider or declare authorized main article; supplements, login pages, and abstract pages are invalid. |
| 8 | `docling-screening` | Validated supported PDF/HTML subset; complete identity-corroborated no-VLM profile each. | Valid profiles equal retrieved supported payloads. `missing_documents` is an overlap, not another PRISMA branch. | Replace wrong/corrupt source and resume from download, otherwise rerun Docling. |
| 9 | `graph-sections` | Exact native Docling JSON/Markdown hashes; direct Graph extraction of both targets. | Profiles equal valid targeted-section pairs plus records requiring canonical overrides; after override, screening inputs equal profiles. | Provide exact heading selectors; no pasted excerpts, arbitrary windows, root sections, or whole document. |
| 10 | `fulltext-screening` | `title + abstract + complete selected_full_text_sections`; final result per record. | Section-screened count equals all final decisions. | Resolve section gate first or retry unchanged screening batches. |
| 11 | `eligibility-resolution` | Full-text decisions plus signed manual rows for every remaining uncertainty. | `accepted + excluded = resolved eligibility inputs`; unresolved must be zero. | Complete `manual_resolution.csv`; resume without `--force`. |
| 12 | `docling-vlm` | Newly accepted main-article PDFs only; fresh complete VLM profiles. | Complete VLM profile count equals newly accepted count. | HTML-only acceptance blocks; supply authorized PDF and resume from download. |
| 13 | `taxonomy-discovery` | Complete VLM profiles; open direct discovery without frozen family labels. | Every profile participates once; discovered models/routes may outnumber records. | Retry failed document shards unchanged. |
| 14 | `taxonomy-classification` | Fixed inventory, taxonomy v1, three direct runs, dense audit, separate adjudication. | All profiles succeed; route/evidence IDs reconcile; every dense-only candidate is dispositioned. | If Jaccard `<0.80`, family agreement `<0.90`, alpha `<0.80`, or alpha is unestimable, stop for whole-cohort rerun. |
| 15 | `crop-validation` | Accepted routes and all native figures; two selectors, adjudicator, cropper. | Exactly one validated crop or `no_suitable_figure` disposition per included model. | Retry failed model batches unchanged; retain selectors, source identity, and adjudication. |
| 16 | `snapshot` | Prior snapshot plus validated new cohort/routes/evidence/crops and corpus hashes. | Cumulative records equal prior snapshot plus accepted update under explicit duplicate/version linkage; route/evidence parity exact. | Repair earliest invalid upstream stage; never edit totals. |
| 17 | `atlas` | Snapshot, prior UI shell, and all actual figure-bearing corpus roots. | Atlas record/study/model/configuration/route counts equal snapshot; assets and iteration filter pass desktop/mobile QA. | Fix builder/UI, rebuild stage, rerun browser QA. |
| 18 | `report` | All machine-readable summaries and retrieval dispositions. | Recheck every identity above; all retrieval branches mutually exclusive. | Fix source artifact or report generator, not rendered counts. |

A genuine zero cohort is allowed only when the completed upstream source evidences it. The runner then writes explicit no-change markers rather than synthetic profiles, routes, crops, or snapshots.

## 4. Screening Payloads And Topology

**Abstract scientific evidence:** exactly `title + abstract`. The actual frozen transport object additionally contains:

```json
{"record_id":"rec_NNNNNN","title":"...","abstract":"...","doi":"...","year":"...","venue":"...","sources":[]}
```

**Full-text scientific evidence:** exactly `title + abstract + complete selected_full_text_sections`. The serialized object is:

```json
{"record_id":"...","candidate_id":"...","source_record_id":"...","source_corpus":"...","title":"...","abstract":"...","doi":"...","year":"...","venue":"...","sources":[],"selected_full_text_sections":"complete heading-bounded section text"}
```

It must not contain `selector_reason`, `section_evidence`, complete `docling_markdown`, chunks, or Graph provenance. Adjudicator payloads add `first_pass_outputs` containing the scope output, architecture output, and deterministic Python-gate result.

Topology for both passes:

1. Independent scope-reviewer invocation on `gpt-5.4-mini`.
2. Independent architecture-reviewer invocation on `gpt-5.4-mini`.
3. Deterministic Python gate.
4. Separate `gpt-5.4-mini` adjudicator only for conflicts or unresolved criteria.

Scope output covers paper type, biological modality, text component, bridge, exclusion code, uncertainty, rationale, and evidence snippet. Architecture output covers paper type, generative status, foundation-model evidence, exclusion code, uncertainty, rationale, and evidence snippet. Adjudication covers all criteria.

Abstract batches are 8, adjudicator batches 6, using the legacy runner with `max_workers=64`. Full-text batches are 8, adjudicator batches 6, `screening_workers=8`, three batch attempts, and a 1,800-second timeout.

## 5. Processing Modes And Reuse

- **No-VLM Docling:** PDF/HTML screening conversion; accurate tables and cell matching, page/picture images at scale `2.0`, heading hierarchy from bookmarks/numbering/style, no OCR, no formula enrichment, no truncation. HTML uses `SimplePipeline`.
- **VLM Docling:** fresh PDF-only conversion for accepted reports using `gpt-5.5`; retains native JSON, Markdown, source, figures, captions, and native picture descriptions. A no-VLM profile cannot be patched into this profile.
- **Graph sections:** `extraction-contract=direct`, `provenance=detailed`, model `openai/gpt-5.4-mini`, targets `data_source` and `input_representation`, complete heading-bounded reconstruction.
- **Taxonomy:** `incremental_frozen_taxonomy`; open direct discovery (`incremental_open_r1`), three fixed direct runs `r1/r2/r3` with prompt `v3-interface-boundary`, dense `coded/coverage` pass with `scoped` fill and `standard` deduplication, then separate adjudication. Taxonomy v1, temperature 0, no text truncation.
- **Crop:** `gpt-5.4-mini`; two blind selectors, one emphasizing route sufficiency and one specificity, followed by separate adjudication and normalized cropping.
- **Snapshot:** incremental atomic merge of prior snapshot and accepted update. A whole-cohort rerun must use the dedicated full-cohort freezer, never an empty prior snapshot.
- **Atlas:** staged build copied from the validated prior UI shell, rebuilt from the new snapshot and every actual figure-bearing corpus root, then local browser QA. Published atlas remains untouched until `publish`.

Successful retrievals and source checkpoints may be reused during the same run. Docling profiles or Graph workspaces may be reused only when source SHA, native Docling SHA, locked code/contract, model, schema, and stage match. A different publisher-file hash is a new profile. Preserved failed attempts cannot be mixed into a new attempt. Prior snapshot routes/crops and UI assets may be carried forward; new-cohort taxonomy outputs, VLM profiles, and crop dispositions cannot be borrowed from mismatched attempts.

## 6. Manual Gates

- Scholar: generated `00_search/google_scholar_provider_export.json`, validated against [google_scholar_provider_export_schema.md](/Users/bogdan.didenko/lpnu/review/protocol/google_scholar_provider_export_schema.md).
- Cross-dedup target: `02_records/manual_cross_dedup_resolutions.json`:

```json
{"update_cluster_id":"162","decision":"keep_new or exclude_as_duplicate","rationale":"Identifier/version evidence","resolver":"...","resolved_at":"ISO-8601"}
```

- Manual full text target: `05_fulltext/manual_fulltexts.json`:

```json
{"candidate_id":"update_2026-08-15__rec_NNNNNN","file":"/absolute/path/to/main_article.pdf","source_url":"https://source/article.pdf","retriever":"operator","retrieved_at":"ISO-8601"}
```

- Section override target: `08_section_input/manual_section_overrides.json`, schema version 2, exact canonical Markdown path/SHA and exact heading trails for both target types.
- Eligibility target: `10_eligibility/manual_resolution.csv` with `record_id,manual_decision,rationale,resolver,resolved_at`; decisions only `INCLUDE` or `EXCLUDE`.

After a declaration, resume the blocked stage without `--force`, then rerun `doctor`.

## 7. Archive, Publication, Deployment, Completion

```bash
ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"
python3 scripts/docling/build_input_taxonomy_artifact_manifest.py --artifact-root "$RUN_ROOT"
python3 scripts/archive_living_review_artifacts.py create --source-root "$RUN_ROOT" --archive-root "$ARCHIVE_ROOT" --receipt-dir data/living_catalog/archives --label "$RUN_ID" --storage-class independent_backup
RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT" --archive /path/to/copied/archive.tar.zst
python3 scripts/archive_living_review_artifacts.py restore --receipt "$RECEIPT" --destination /empty/path/restored_run

python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
git diff --check
python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor
```

After local publication, freeze all new review work. Rebuild the repository ledger, validate both storage views, and publish the exact atlas:

```bash
python3 scripts/docling/build_input_taxonomy_artifact_manifest.py --artifact-root "$RUN_ROOT"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID" --repository-checkout
git status --short
git diff --check
git add data/living_catalog/current.json
git add "data/living_catalog_updates/${RUN_ID}"
git add docs/input-representation-atlas
git add protocol/PRISMA_protocol.md protocol/prisma_search_screening_log_2026-07-07.md
git status --short
git diff --cached --check
git diff --cached --stat
git commit -m "Update living review through ${END}"
git push origin main
gh run list --workflow deploy-input-representation-atlas.yml --limit 5
GITHUB_RUN_ID="RUN_ID_FROM_GITHUB"
gh run watch "$GITHUB_RUN_ID" --exit-status
COMMIT="$(git rev-parse HEAD)"
python3 scripts/run_living_review_pipeline.py verify-live --expected-commit "$COMMIT" --check-assets
python3 scripts/run_living_review_pipeline.py doctor
```

The workflow independently runs `doctor --repository-checkout`, `release-manifest --commit "$GITHUB_SHA"`, deploys Pages, and retries `verify-live` five times.

After remote byte/hash verification and actual desktop/mobile UI QA:

```bash
python3 scripts/run_living_review_pipeline.py verify-live --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets --record-completion --workflow-run-id "$GITHUB_RUN_ID" --operator "OPERATOR" --screenshot /absolute/path/desktop.png --screenshot /absolute/path/mobile.png
git add "data/living_catalog/releases/${RUN_ID}/completion_record.json"
git diff --cached --check
git commit -m "Record verified release evidence for ${RUN_ID}"
git push origin HEAD
```

Deployment failure recovery uses the same commit/artifact:

```bash
gh run rerun "$GITHUB_RUN_ID"
gh run watch "$GITHUB_RUN_ID" --exit-status
python3 scripts/run_living_review_pipeline.py verify-live --expected-commit "$(gh run view "$GITHUB_RUN_ID" --json headSha -q .headSha)" --check-assets
python3 scripts/run_living_review_pipeline.py incident --run-id "$RUN_ID" --phase deployment --summary "Observed failure and chosen recovery" --operator "OPERATOR" --commit "$COMMIT" --workflow-run-id "$GITHUB_RUN_ID"
```

Withdrawal requires an auditable rollback commit restoring `current.json` and the atlas together from one last-known-good commit, followed by deployment and verification of that rollback SHA.

## 8. Remaining Reproducibility Blockers

1. **The required live checks remain unexecuted.** `doctor`, method-lock verification, preflight, credentials, dependencies, branch state, and repository cleanliness are unknown by design.
2. **No compliant independent backup currently exists.** Both committed receipts are explicitly `local_secondary`; [archives/README.md](/Users/bogdan.didenko/lpnu/review/data/living_catalog/archives/README.md) says future method-locked runs cannot be published until an `independent_backup` receipt exists. The actual independent mount/path is unspecified.
3. **The current published update has no completion record.** `data/living_catalog/releases/` is absent, so static repository evidence does not establish its GitHub workflow ID, remote byte comparison, screenshots, or completed release gate.
4. **Current-state provenance is split.** `current.json` and the atlas point to the August 16 full-cohort derived-correction snapshot, while the last run manifest’s `published_state` points to the older August 11 snapshot. No completion record binds the later transition.
5. **Full-text screening is outside the executable method lock.** The orchestrator calls `scripts/run_codex_screening_pipeline.py` and `protocol/screening_prompt_templates/*`, but neither appears in [living_review_method_lock_v1.json](/Users/bogdan.didenko/lpnu/review/protocol/living_review_method_lock_v1.json). Changes there can evade lock verification.
6. **Full-text prompts and schemas conflict.** The generic prompts request `evidence_for_*` and `boundary_case` fields and materially change the foundation-model exclusion policy, while the runner’s strict generated schemas do not permit those fields. This also differs from the hash-pinned abstract prompts, contradicting the runbook’s claim that selected-section screening uses hash-pinned legacy prompts.
7. **“Exact payload” is inconsistent across prose and implementation.** The lock says title/abstract evidence only, but model-facing JSON also carries DOI, year, venue, sources, and identifiers. Their permitted evidentiary role is not defined.
8. **Archive timing is ambiguous.** `publish` mutates `run_manifest.json` after the required independent archive is verified; the subsequent manifest rebuild changes the ledger. The runbook does not state whether a second independent archive/receipt is mandatory before commit and completion.
9. **Remote visual QA is required but has no documented operator command.** `verify-live` checks bytes, counts, commit, tree, and asset hashes, not browser interaction or screenshots. The source and capture procedure for completion-record desktop/mobile screenshots are unspecified.
10. **Post-restore validation is underspecified.** The runbook requires profile-contract validation and the relevant canonical-manifest check after restore but gives no exact commands.
11. **Known methodological limitations remain:** no late-indexing lookback and no general multi-operator filesystem lock.

Until items 2 through 9 are resolved or formally accepted through a versioned protocol correction, an unfamiliar agent cannot execute the next iteration with defensible end-to-end comparability.
