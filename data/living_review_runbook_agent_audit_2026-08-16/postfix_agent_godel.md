I’ll treat the runbook as the sole source of protocol truth, then inspect only the static repository files it explicitly names. I’ll distinguish inspection performed here from the operational commands listed for the hypothetical iteration; none of those workflow commands will be run.
The runbook defines a strict state machine with 18 named stages and makes the published cursor authoritative in `data/living_catalog/current.json`. It also documents a known prompt/schema mismatch that cannot be repaired inside a routine iteration, so I’m preserving that as a comparability constraint rather than normalizing it away.
Static state confirms the published cursor is `2026-08-09`, so the next interval begins `2026-08-10`. With the supplied clock date `2026-08-16` in `Europe/Kiev`, the default inclusive end is `2026-08-15`, the last calendar day that has fully elapsed; this remains provisional until the hypothetical `doctor` and `plan` outputs validate the state.
The configured routine path is more specific than the prose summary: no-VLM Docling feeds direct, detailed Graph section extraction; accepted PDFs then receive a fresh VLM conversion; taxonomy uses one open direct discovery, three fixed direct replicates, one scoped dense audit, blinded adjudication, and `incremental_frozen_taxonomy` analysis. Existing expensive outputs are preservation evidence only unless every recorded source/profile hash and locked contract matches.
The remaining review is reconciliation-focused: I’m checking that publication evidence can be carried from the immutable pre-publication archive through Git/Pages and the completion record. Two protocol gaps are already material: the runbook requires the archive receipt to be committed but its documented staging commands omit the receipt path, and it requires every generated update report to mention late indexing while the locked report generator contains no such text or declared manual input.
# Silent Dry Run

No workflow command below was executed. Inspection was read-only; no files or repository state were changed.

## 1. Cursor And Interval

The authoritative [current state](/Users/bogdan.didenko/lpnu/review/data/living_catalog/current.json:1) reports:

- Published cursor: `search_end = 2026-08-09`
- Next inclusive start: `2026-08-10`
- Current date: `2026-08-16` in `Europe/Kiev`
- Default inclusive end: `2026-08-15`, the last fully elapsed calendar day
- Run ID: `update_2026-08-15`
- Exact search interval: **`2026-08-10..2026-08-15`, inclusive**

The unfinished day `2026-08-16` must not be searched. The pipeline prevents overlap but has no retrospective late-indexing lookback.

Static inspection also found that the published atlas `generated_from` matches the current taxonomy root. Its published counts are 55 records, 54 studies, 109 models, 468 configurations, and 586 routes. Only `doctor` can establish current hash-valid health.

## 2. Ordered Procedure

1. Inspect worktree, branch, commit, Python, global `doctor`, and method lock.
2. Set `END=2026-08-15`; run `plan`.
3. Run `scholar-capture`, then read-only-capable `scholar-validate`.
4. Run preflight through `report`; require every check to report `ready: true`.
5. Execute the runner, which alone owns these 18 stages in order:
   `search → deduplicate → prepare-records → enrich-abstracts → abstract-screening → fulltext-candidates → fulltext-download → docling-screening → graph-sections → fulltext-screening → eligibility-resolution → docling-vlm → taxonomy-discovery → taxonomy-classification → crop-validation → snapshot → atlas → report`.
6. At any stop, run `doctor --run-id`; resolve only the first blocking stage and resume it without `--force`.
7. Resolve generated manual gates where necessary: Scholar export, cross-dedup, lawful full text, canonical section selectors, and eligibility.
8. After all 18 stages are complete and hash-valid, create `artifact_manifest.csv`, create and independently verify the immutable pre-publication archive, and validate any restore.
9. Run pre-publication `doctor`, `status`, and `git diff --check`.
10. Publish locally, which atomically promotes the staged atlas and advances `current.json`.
11. Freeze new review work; intentionally stage, commit, push, wait for Pages, verify exact remote bytes/assets/commit, and perform remote desktop/mobile browser QA.
12. Create and commit `completion_record.json`; only then is the iteration complete.

Steps 9 onward are conditionally blocked by two runbook inconsistencies identified in Section 7.

## 3. Stage Boundaries

| # | Stage | Required input and success/denominator | Failure or recovery |
|---:|---|---|---|
| 1 | `search` | Dated config and complete Scholar bundle; all eight sources and all pagination complete. `raw hits = Σ completed export counts`. | Restore credentials/provider access and resume `search`; never turn failure into zero. |
| 2 | `deduplicate` | Completed exports; merge ledger and review queue. `unique = raw hits − duplicate members`. | Repair invalid export or resolve identifier/title conflicts; resume reported stage. |
| 3 | `prepare-records` | Update clusters plus every published master artifact. `new = unique − cumulative matches/exclusions`. Queue must be empty or declared manually resolved. | Complete `manual_cross_dedup_resolutions.json`; resume `prepare-records`. |
| 4 | `enrich-abstracts` | New records; every missing/short abstract attempted. Usable cohort plus explicit below-threshold exclusions must partition the input. | Retry providers; retain rejected candidates. Bounded diagnostic output is not canonical. |
| 5 | `abstract-screening` | Title/abstract input; one final structured result per input. `abstract-screened = final decisions`. | Retry incomplete frozen batches with unchanged runner, prompts, model, and schema. |
| 6 | `fulltext-candidates` | Final abstract decisions. `candidates = INCLUDE + UNCERTAIN`, with unique stable IDs and one source mapping each. | Correct only through the upstream resolution path. |
| 7 | `fulltext-download` | Every candidate gets exactly one disposition. `candidates = retrieved + terminal not-retrieved`; technical/XML dispositions block. | Retry providers or declare a validated main article; supplements and abstract pages are invalid. |
| 8 | `docling-screening` | Validated supported PDF/HTML subset. Exactly one identity-corroborated no-VLM profile per retrieved supported payload. | Correct corrupt/wrong source from download or rerun Docling. |
| 9 | `graph-sections` | Complete no-VLM manifest. Every profile must yield grounded `data_source` and `input_representation` heading-bounded sections. | Use exact canonical heading overrides; never paste arbitrary text or whole Markdown. |
| 10 | `fulltext-screening` | Title, abstract, and selected sections. Input count must equal final structured decisions. | Apply valid section overrides first or retry unchanged screening batches. |
| 11 | `eligibility-resolution` | Full-text decisions. `eligibility inputs = accepted + excluded`; unresolved must be zero. | Add declared manual resolution with evidence, resolver, and timestamp. |
| 12 | `docling-vlm` | Newly accepted records with authorized PDFs. `accepted records = complete VLM profiles`. | HTML-only acceptance blocks; add PDF and rerun from `fulltext-download`. |
| 13 | `taxonomy-discovery` | Complete new VLM profiles. Every profile succeeds in open direct discovery and registry creation. | Retry failed document batches unchanged. Route counts are not record counts. |
| 14 | `taxonomy-classification` | Fixed inventory and taxonomy v1; 3 direct runs, dense audit, adjudication. Require route grounding, Jaccard ≥0.80, family agreement ≥0.90, alpha ≥0.80, and every dense candidate dispositioned. | Failed acceptance requires reviewed whole-cohort rerun; never patch selected outputs. |
| 15 | `crop-validation` | New accepted models/routes and native figures. Every new model gets one valid crop or `no_suitable_figure`. | Retry failed model batches; retain both selectors, adjudicator, and source identity. |
| 16 | `snapshot` | Prior snapshot plus validated update taxonomy/crops/profile roots. `cumulative = prior + accepted update` under duplicate/version linkage; route/evidence IDs must have parity. | Repair earliest invalid upstream stage; never edit totals. |
| 17 | `atlas` | Snapshot, prior UI shell, and every actual corpus root with figures. Atlas counts/assets must match snapshot and local desktop/mobile QA must pass. | Fix builder/UI, rebuild this stage, rerun browser QA. |
| 18 | `report` | All machine-readable stage summaries. Every denominator and mutually exclusive retrieval branch must reconcile. | Repair source artifact or generator; never edit generated counts manually. |

An evidenced zero-record or zero-accepted cohort is valid; downstream stages must write their declared zero/no-change markers.

## 4. Screening Payloads And Topology

Both passes use `gpt-5.4-mini` with batch size 8 and adjudicator batch size 6:

`scope reviewer invocation + architecture reviewer invocation → deterministic Python gate → separate adjudicator invocation only for conflicts/uncertainty`.

Abstract screening uses the hash-pinned legacy runner with concurrency 64. First-pass JSON records contain exactly:

```json
{"record_id":"...","title":"...","abstract":"...","doi":"...","year":"...","venue":"...","sources":[]}
```

Full-text screening uses `full_text_sections` mode and concurrency 8:

```json
{"record_id":"...","candidate_id":"...","source_record_id":"...","source_corpus":"...","title":"...","abstract":"...","doi":"...","year":"...","venue":"...","sources":[],"selected_full_text_sections":"..."}
```

The adjudicator receives the corresponding record plus `"first_pass_outputs": {...}`. Reviewers must not receive `selector_reason`, `section_evidence`, complete `docling_markdown`, or Graph provenance.

Strict response authority is `{"results":[...]}`, same record order, no undeclared properties:

- Scope row: `record_id`, `paper_type`, `bio_modality_present`, `text_component_present`, `text_bio_bridge_present`, `primary_exclusion_code`, `uncertainty_reason`, `decision_rationale`, `evidence_snippet`.
- Architecture row: `record_id`, `paper_type`, `generative_model_present`, `foundation_model_evidence`, `primary_exclusion_code`, `uncertainty_reason`, `decision_rationale`, `evidence_snippet`.
- Adjudicator row: `record_id` plus all six criteria and the four decision/evidence fields above.

The selected-section prompts still request legacy `evidence_for_*` and `boundary_case` properties, while the strict schema accepts `evidence_snippet` and rejects extras. This mismatch is frozen; it cannot be repaired in this routine run.

## 5. Processing And Reuse Modes

| Component | Required routine mode and reuse rule |
|---|---|
| Docling screening | No VLM; OCR off, accurate tables/cell matching, page/picture images at scale 2.0, formulas off, no truncation. PDF or genuine article HTML allowed. |
| Docling VLM | Fresh PDF conversion for newly accepted reports using `gpt-5.5`. Do not patch or relabel the no-VLM profile; HTML is insufficient. |
| Docling Graph | `direct`, detailed provenance, `openai/gpt-5.4-mini`; reconstruct complete heading-bounded target sections. |
| Taxonomy discovery | Open direct discovery, labels hidden, synthesis mode `inventory`; not taxonomy synthesis. |
| Taxonomy classification | `incremental_frozen_taxonomy`, taxonomy v1, prompt `v3-interface-boundary`, temperature 0, no truncation; direct `r1/r2/r3`, dense scoped fill with standard deduplication, separate adjudication. |
| Crop | Two blind selectors, separate adjudicator and cropper, `gpt-5.4-mini`, native figures. Existing model dispositions remain in the prior ledger and are not silently replaced. |
| Snapshot | Incremental merge of current snapshot plus only the accepted update. No fake empty prior snapshot and no full-cohort builder. |
| Atlas | Seed from the validated published UI, rebuild against the new snapshot and all real corpus roots, then local browser QA. A combined manifest cannot replace figure-bearing corpus roots. |

Successful downloads may be reused across retries. Canonical profiles or Graph workspaces may be reused only when source SHA, Docling JSON/profile SHA, code/contract, model, schema, and stage all match. Preserved outputs remain evidence and cannot be silently mixed. A source with a different publisher-file hash is a new profile.

## 6. Exact Commands Not Executed

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
RUN_ID=update_${END}
python3 scripts/run_living_review_pipeline.py plan --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to "$END"
python3 scripts/run_living_review_pipeline.py preflight --date-to "$END" --through-stage report
python3 scripts/run_living_review_pipeline.py run --date-to "$END" --manage-server

python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID"
STAGE=FIRST_BLOCKING_STAGE_REPORTED_BY_DOCTOR
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage "$STAGE" --manage-server
```

Manual declarations, only when generated gates require them:

```json
{"update_cluster_id":"...","decision":"keep_new","rationale":"...","resolver":"...","resolved_at":"ISO-8601"}
{"candidate_id":"...","file":"/absolute/path/main_article.pdf","source_url":"...","retriever":"operator","retrieved_at":"ISO-8601"}
{"record_id":"...","candidate_id":"...","source_markdown":"/absolute/path.md","source_markdown_sha256":"...","sections":[{"target_section_types":["data_source"],"heading_path":["Methods","Data"]},{"target_section_types":["input_representation"],"heading_path":["Methods","Architecture"]}],"rationale":"...","resolver":"...","resolved_at":"ISO-8601"}
```

Eligibility CSV header is exactly:

```text
record_id,manual_decision,rationale,resolver,resolved_at
```

Archive and restore commands:

```bash
RUN_ROOT="data/living_catalog_updates/${RUN_ID}"
ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"
python3 scripts/docling/build_input_taxonomy_artifact_manifest.py --artifact-root "$RUN_ROOT"
python3 scripts/archive_living_review_artifacts.py create \
  --source-root "$RUN_ROOT" --archive-root "$ARCHIVE_ROOT" \
  --receipt-dir data/living_catalog/archives --label "$RUN_ID" \
  --storage-class independent_backup
RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"

python3 scripts/archive_living_review_artifacts.py restore \
  --receipt "$RECEIPT" --destination /empty/path/restored_run
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
.venv-docling/bin/python scripts/docling/validate_canonical_profile_manifest.py \
  --manifest /empty/path/restored_run/11_docling_vlm/profiles/manifests/canonical_docling_profile_manifest.csv \
  --original-run-root "$RUN_ROOT" --restored-run-root /empty/path/restored_run \
  --expected-records EXPECTED_ACCEPTED_RECORDS
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
```

Pre-publication, publication, Git, deployment, and completion:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
git diff --check
python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor

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
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID" --repository-checkout
git commit -m "Update living review through ${END}"
git push origin main

gh run list --workflow deploy-input-representation-atlas.yml --limit 5
gh run watch GITHUB_RUN_ID --exit-status
COMMIT=$(git rev-parse HEAD)
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets

RELEASE_ROOT="data/living_catalog/releases/${RUN_ID}"
REMOTE_QA="${RELEASE_ROOT}/remote_browser_qa.json"
NODE_PATH="${NODE_PATH:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules}" \
  node scripts/qa_input_representation_atlas.mjs \
  https://bogdandidenko.github.io/text-bio-fundational-models-review/ "$REMOTE_QA"
python3 scripts/run_living_review_pipeline.py doctor

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

## 7. Remaining Reproducibility Blockers

1. Strict execution readiness is unknown because the required `doctor`, method verifier, plan, preflight, network capture, and hash checks were intentionally not run.
2. The runbook requires the independent-backup receipt to be inspected **and committed**, but its documented Git staging commands never stage `data/living_catalog/archives/${RUN_ID}__*.json`. No exact compliant receipt-commit command is specified.
3. The runbook requires every update report to disclose the absent late-indexing lookback, but the hash-locked report generator contains no such text and no declared manual report-input mechanism. Generated reports may not be edited.
4. The boundary section names `00_search/search_summary.json`, while the executable runner uses `00_search/exports/search_summary_${END}.json`.
5. `GITHUB_RUN_ID` is never assigned by the documented commands; `RUN_ID_FROM_GITHUB` and `GITHUB_RUN_ID` are used inconsistently, and selection from `gh run list` is not bound deterministically to `$COMMIT`.
6. `git push origin main` assumes an appropriate local `main` state, but branch-switch/update handling is not specified when the initial branch differs or contains unrelated work.
7. `ARCHIVE_ROOT`, `OPERATOR`, `EXPECTED_ACCEPTED_RECORDS`, and any manual resolver identity require authoritative runtime values. Credential validity, independent storage availability, lawful PDF access, GitHub authorization, and Pages access remain unverified.
8. The selected-section prompt/schema mismatch is frozen and can cause retries or failure; correcting it requires a new method lock and bridge analysis.
9. There is no multi-operator filesystem lock and no automated retrospective late-indexing search.
10. A code-level report-generator repair would mutate the hash-locked runner, conflicting with the routine recovery instruction unless a method-version/bridge path is declared.

Items 2 and 3 prevent strict end-to-end compliance without a documented protocol clarification or method-version change. Publication should stop rather than filling either gap by inference.
