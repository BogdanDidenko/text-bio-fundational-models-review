I’ll audit only the runbook and the static repository files it directly names. I’ll separate documented procedure from unresolved ambiguity and present all operational commands as an unexecuted dry-run transcript.
The runbook defines the update as a hash-tracked state machine with 18 named stages and forbids using downstream-looking files as progress evidence. I’m now tracing its boundary rules and every referenced declaration/template so the dry run can distinguish automatic retries from human-authorized recovery.
Static inspection confirms the published cursor is `2026-08-09`; with the runbook’s default Europe/Kiev policy, the next routine interval is `2026-08-10` through `2026-08-15`, inclusive. That interval is only provisional until the unexecuted `doctor`, method-lock verifier, plan, Scholar validation, and preflight commands all pass.
A material protocol gap has surfaced in the static runner: `fulltext-candidates` unconditionally reads `05_fulltext/postscreen_dedup/duplicate_resolutions.json`, but the runbook defines no generator, template, manual gate, or empty-file contract for a new run. I’ll keep the documented end-to-end procedure intact, but flag that stage as a reproducibility blocker instead of inventing an input.
# Silent Dry Run

No operational command below was executed. This evaluation uses only the [runbook](/Users/bogdan.didenko/lpnu/review/protocol/LIVING_REVIEW_RUNBOOK.md), [published state](/Users/bogdan.didenko/lpnu/review/data/living_catalog/current.json), and explicitly referenced static files.

**Cursor**
`current.json.search_end` is `2026-08-09`. The next inclusive interval is therefore **2026-08-10 through 2026-08-15**. The start is cursor + one calendar day; the end is the last fully elapsed calendar day in `Europe/Kiev` as of `2026-08-16`. Google Scholar remains year-bounded and late indexing in closed intervals has no automated lookback.

**Command Transcript**
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
RUN_ID="update_${END}"
RUN_ROOT="data/living_catalog_updates/${RUN_ID}"
python3 scripts/run_living_review_pipeline.py plan --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to "$END"
python3 scripts/run_living_review_pipeline.py preflight --date-to "$END" --through-stage report
python3 scripts/run_living_review_pipeline.py run --date-to "$END" --manage-server

# After any failure, timeout, interruption, or manual gate:
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage STAGE_FROM_DOCTOR --manage-server
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID"

# After all 18 stages are complete and hash-valid:
ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"
python3 scripts/docling/build_input_taxonomy_artifact_manifest.py --artifact-root "$RUN_ROOT"
python3 scripts/archive_living_review_artifacts.py create \
  --source-root "$RUN_ROOT" --archive-root "$ARCHIVE_ROOT" \
  --receipt-dir data/living_catalog/archives --label "$RUN_ID" \
  --storage-class independent_backup
RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"

python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
git diff --check
python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor

git status --short
git diff --check
git add data/living_catalog/current.json
git add "$RUN_ROOT"
git add "$RECEIPT"
git add docs/input-representation-atlas
git add protocol/PRISMA_protocol.md protocol/prisma_search_screening_log_2026-07-07.md
git status --short
git diff --cached --check
git diff --cached --stat
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID" --repository-checkout
git commit -m "Update living review through ${END}"
COMMIT="$(git rev-parse HEAD)"
git push origin main

gh run list --workflow deploy-input-representation-atlas.yml --limit 5
GITHUB_RUN_ID="SELECT_MATCHING_RUN_ID"
gh run watch "$GITHUB_RUN_ID" --exit-status
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets
RELEASE_ROOT="data/living_catalog/releases/${RUN_ID}"
REMOTE_QA="${RELEASE_ROOT}/remote_browser_qa.json"
NODE_PATH="${NODE_PATH:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules}" \
  node scripts/qa_input_representation_atlas.mjs \
  https://bogdandidenko.github.io/text-bio-fundational-models-review/ "$REMOTE_QA"
python3 scripts/run_living_review_pipeline.py doctor

OPERATOR="DECLARED OPERATOR"
python3 scripts/run_living_review_pipeline.py verify-live \
  --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets \
  --record-completion --workflow-run-id "$GITHUB_RUN_ID" \
  --operator "$OPERATOR" --browser-qa-report "$REMOTE_QA" \
  --screenshot /tmp/atlas-graph-desktop.png \
  --screenshot /tmp/atlas-graph-mobile.png
git add "data/living_catalog/releases/${RUN_ID}/completion_record.json"
git diff --cached --check
git commit -m "Record verified release evidence for ${RUN_ID}"
git push origin HEAD
```

Optional independent-copy verification and restore:

```bash
python3 scripts/archive_living_review_artifacts.py verify \
  --receipt "$RECEIPT" --archive /path/to/copied/archive.tar.zst
python3 scripts/archive_living_review_artifacts.py restore \
  --receipt "$RECEIPT" --destination /empty/path/restored_run
EXPECTED_ACCEPTED_RECORDS="$(jq '.records | length' "$RUN_ROOT/10_eligibility/accepted_records.json")"
.venv-docling/bin/python scripts/docling/validate_canonical_profile_manifest.py \
  --manifest /empty/path/restored_run/11_docling_vlm/profiles/manifests/canonical_docling_profile_manifest.csv \
  --original-run-root "$RUN_ROOT" --restored-run-root /empty/path/restored_run \
  --expected-records "$EXPECTED_ACCEPTED_RECORDS"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
```

**18 Stage Boundaries**

| # | Stage | Required input; success and denominator | Failure/recovery |
|---:|---|---|---|
| 1 | `search` | Dated v3.3 config, credentials, signed Scholar bundle; all eight sources and pagination complete; raw hits = sum completed exports | Fix access/provider failure and resume `search`; never record failure as zero |
| 2 | `deduplicate` | Eight exports; merge ledger complete; unique = raw hits − duplicate members | Correct invalid export or dedup evidence; resume reported stage |
| 3 | `prepare-records` | Update clusters plus every published master; DOI/PMID/arXiv/title and Crossref audit complete; new = unique − cumulative exclusions | Complete `manual_cross_dedup_resolutions.json`; resume |
| 4 | `enrich-abstracts` | New records; every missing/short abstract attempted; title fallback corroborated | Retry provider routes; screening input + unusable-abstract exclusions must reconcile to new records |
| 5 | `abstract-screening` | Title/abstract cohort; one final structured result per input | Same model/prompt/schema retries only |
| 6 | `fulltext-candidates` | Final abstract decisions; raw candidates = INCLUDE + UNCERTAIN with stable IDs | Correct only through declared resolution path; see critical gap below |
| 7 | `fulltext-download` | Candidate manifest; each candidate has exactly one retrieval disposition | Retry technical failures or declare lawful main PDF/HTML; terminal not-retrieved remains denominator evidence |
| 8 | `docling-screening` | Validated PDF/HTML subset; one complete identity-corroborated no-VLM profile per supported retrieval | Replace bad payload or rerun Docling; terminal non-retrieval gets no placeholder profile |
| 9 | `graph-sections` | Complete no-VLM manifest; both target sections grounded and heading-bounded | Provide canonical heading override; never paste arbitrary text |
| 10 | `fulltext-screening` | Title + abstract + complete selected sections; one final decision per valid/overridden pair | Retry frozen batches or resolve section gate first |
| 11 | `eligibility-resolution` | Full-text decisions; accepted + excluded = eligibility inputs; unresolved = 0 | Complete signed `manual_resolution.csv` |
| 12 | `docling-vlm` | Newly accepted records with PDFs; profiles = accepted records | Obtain authorized PDF for HTML-only acceptance; rerun from download |
| 13 | `taxonomy-discovery` | Complete VLM profiles; open direct discovery succeeds for every record | Retry unchanged document batches |
| 14 | `taxonomy-classification` | Three direct runs, dense audit, adjudication; Jaccard ≥0.80, family agreement ≥0.90, alpha ≥0.80 | Failure requires reviewed whole-cohort rerun, never per-record patching |
| 15 | `crop-validation` | Routes plus native figures; one validated crop or `no_suitable_figure` per included model | Retry failed model batches, retaining selector evidence |
| 16 | `snapshot` | Prior snapshot plus accepted update; exact route/evidence parity and hashes | Repair earliest invalid stage; never edit totals |
| 17 | `atlas` | Snapshot plus every actual figure-bearing corpus root; counts/assets/browser QA pass | Rebuild staged atlas and rerun QA |
| 18 | `report` | All stage summaries; every PRISMA transition and retrieval branch reconciles | Fix source artifact or generator, never report counts manually |

**Screening Payloads**
Abstract first-pass model record:

```json
{"record_id":"...","title":"...","abstract":"...","doi":"...","year":"...","venue":"...","sources":[]}
```

Full-text first-pass model record:

```json
{"record_id":"...","candidate_id":"...","source_record_id":"...","source_corpus":"...","title":"...","abstract":"...","doi":"","year":"","venue":"","sources":[],"selected_full_text_sections":"[data_source: ...]\n...\n\n[input_representation: ...]\n..."}
```

The full-text builder currently omits `doi/year/venue/sources`; the locked screening runner injects them as empty defaults. The adjudicator receives the corresponding record plus:

```json
{"first_pass_outputs":{"scope_reviewer":{...},"architecture_reviewer":{...},"python_gate":{...}}}
```

Both stages use `gpt-5.4-mini`: scope reviewer and architecture reviewer independently, deterministic Python gate, then a separate adjudicator only for conflict/uncertainty. Abstract screening uses the hash-pinned legacy runner, batches `8/6`, maximum 64 workers. Full-text uses `full_text_sections`, batches `8/6`, 8 workers, three attempts, and 1,800-second timeout. Strict result schemas reject extra properties; the known prompt/schema mismatch must not be repaired inside this routine run.

**Modes And Reuse**
- Docling screening: no VLM; PDF/HTML allowed; OCR/formulas off; accurate tables and cell matching on; page/picture images at scale 2; bookmarks/numbering/style headings. VLM mode is a fresh PDF-only profile using `gpt-5.5`, temperature 0, not a patch of the no-VLM profile.
- Graph section mode: direct extraction with `openai/gpt-5.4-mini`, detailed provenance, complete heading-boundary reconstruction, both targets required. Root containers covering ≥80% and any section covering ≥90% are rejected; duplicate selected sections are collapsed.
- Taxonomy mode: `incremental_frozen_taxonomy`; open direct discovery without family labels, three fixed direct classifications, dense scoped-fill/standard-dedup audit, blinded adjudication, taxonomy v1.
- Crop mode: two independent `gpt-5.4-mini` selectors, separate adjudicator, cropper; prior model dispositions are excluded from silent replacement.
- Snapshot mode: atomic incremental merge of prior snapshot plus accepted update. Whole-cohort work must use the dedicated full-cohort freezer.
- Atlas mode: copy the validated UI shell, rebuild from the staged snapshot and all actual corpus roots, then local desktop/mobile QA. Published atlas remains unchanged until `publish`.
- Downloads may be reused across retrieval retries. Docling profiles or Graph workspaces may be reused only when source/profile hashes and every locked contract/model/schema match. A different source hash is a new profile. Preserved attempts remain evidence and are not mixed automatically.

**Manual Gates**
- Scholar: `00_search/google_scholar_provider_export.json`, produced by `scholar-capture` and accepted only after signed query/page/pagination validation.
- Cross-dedup: `{"update_cluster_id":"...","decision":"keep_new|exclude_as_duplicate","rationale":"...","resolver":"...","resolved_at":"ISO-8601"}`.
- Full text: `{"candidate_id":"...","file":"/absolute/main_article.pdf","source_url":"...","retriever":"operator","retrieved_at":"ISO-8601"}`.
- Section override: canonical Markdown path and SHA, exact heading trails for `data_source` and `input_representation`, rationale, resolver, timestamp.
- Eligibility CSV: `record_id,manual_decision,rationale,resolver,resolved_at`, with decision `INCLUDE` or `EXCLUDE`.
- After any declaration, resume its blocked stage without `--force`, then run `doctor`.

**Unresolved Execution Blockers**
1. `fulltext-candidates` unconditionally reads `05_fulltext/postscreen_dedup/duplicate_resolutions.json`, but no generator, template, empty-file contract, or manual gate is documented for a new run. An unfamiliar operator cannot lawfully invent it.
2. The denominator ledger says candidates equal abstract INCLUDE + UNCERTAIN, while the runner can remove undocumented post-screening duplicates. The authoritative reconciliation formula is therefore unclear.
3. The documented full-text bibliographic payload conflicts with the locked builder, which omits four fields and causes empty values at model invocation.
4. The runbook names `00_search/search_summary.json`; the runner uses `00_search/exports/search_summary_2026-08-15.json`.
5. The selected-section prompts request legacy output keys that the strict schema rejects. The runbook acknowledges this but offers no routine-compatible correction.
6. Omitting `--date-to` makes the runner default to the unfinished current day, contrary to the runbook’s end-date policy.
7. The independent backup path, operator identity, matching workflow run ID, and authorization source for manual PDFs remain deployment-specific inputs.
8. Current `doctor`, method-lock, credential, provider, backup-mount, GitHub, and Pages health remain unestablished in this silent dry run.
9. Late-indexing lookback, concurrent-operator locking, and two-phase local/remote publication are explicitly absent. New review work must freeze after local publication until exact remote verification succeeds.
