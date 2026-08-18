**Resolved Run**

The published cursor is `2026-08-09` in [current.json](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/data/living_catalog/current.json:4). The local atlas `generated_from` matches the current taxonomy root, and no `update_2026-08-17/run_manifest.json` exists. Therefore:

- Mode: `Routine incremental update`
- Inclusive interval: `2026-08-10` through `2026-08-17`
- `END=2026-08-17`
- `RUN_ID=update_2026-08-17`
- `RUN_ROOT=data/living_catalog_updates/update_2026-08-17`
- Method: `living-review-v1-frozen-taxonomy-v1`
- Current method-lock SHA-256: `718bb59eded9858c7a150ee554d768103207787ab0ab0b62546332c778d945e4`
- Frozen taxonomy SHA-256: `b36c0261a93c6d0e19a2502ec416ba26bf71315cfc04bf3323b260c239693bf9`

No pipeline, network, Git-write, or mutation command was executed during this audit.

**Command Trajectory**

1. Bootstrap, from the canonical checkout only: `export REVIEW_REPO_ROOT=/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review`; `export REVIEW_ARTIFACT_ROOT=/Users/bogdan.didenko/lpnu/review`; `export TZ=Europe/Kiev`; `cd "$REVIEW_REPO_ROOT"`; `test "$(git rev-parse --show-toplevel)" = "$REVIEW_REPO_ROOT"`; `git status --short --branch`; `git branch --show-current`; `git log -1 --format='%H %cI %s'`; `python3 --version`; `python3 scripts/run_living_review_pipeline.py doctor`; `python3 scripts/verify_living_review_method_lock.py --current-taxonomy-tree "$(jq -r .taxonomy_root data/living_catalog/current.json)/taxonomy_tree.json"`. Stop if either verification is unhealthy.

2. Fix identity: `END=2026-08-17`; `DATE_FROM=2026-08-10`; `RUN_ID=update_${END}`; `RUN_ROOT=data/living_catalog_updates/${RUN_ID}`; `OPERATOR="Codex (computational operator)"`; `ARCHIVE_ROOT=/Volumes/INDEPENDENT_BACKUP/text-bio-living-review`.

3. Create and validate the run: `python3 scripts/run_living_review_pipeline.py plan --date-to "$END"`; confirm `date_from=2026-08-10`, `date_to=2026-08-17`, the current taxonomy/atlas linkage, and the new run root; then run `scholar-capture`, `scholar-validate`, and `preflight --date-to "$END" --through-stage report`. Capture must exhaust the v3.3 SerpAPI Google Scholar query and preserve all hashed raw pages.

4. Execute: `python3 scripts/run_living_review_pipeline.py run --date-to "$END" --manage-server`. This runs, in order: `search`, `deduplicate`, `prepare-records`, `enrich-abstracts`, `abstract-screening`, `fulltext-candidates`, `fulltext-download`, `docling-screening`, `graph-sections`, `fulltext-screening`, `eligibility-resolution`, `docling-vlm`, `taxonomy-discovery`, `taxonomy-classification`, `crop-validation`, `snapshot`, `atlas`, `report`.

5. On every interruption, timeout, non-zero exit, or ambiguous result: `python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"`. Populate only the generated declaration required by the first blocking stage, then run `python3 scripts/run_living_review_pipeline.py run --run-id "$RUN_ID" --from-stage STAGE --manage-server` and repeat `doctor`. Relevant manual targets are `02_records/manual_cross_dedup_resolutions.json`, optional `05_fulltext/postscreen_dedup/duplicate_resolutions.json`, `05_fulltext/manual_fulltexts.json`, `08_section_input/manual_section_overrides.json`, and `10_eligibility/manual_resolution.csv`. Never use `--force` for these resumes.

6. After all 18 stages are complete, create and verify the pre-publication archive:
```bash
python3 scripts/docling/build_input_taxonomy_artifact_manifest.py --artifact-root "$RUN_ROOT"
python3 scripts/archive_living_review_artifacts.py create \
  --source-root "$RUN_ROOT" --archive-root "$ARCHIVE_ROOT" \
  --receipt-dir data/living_catalog/archives --label "$RUN_ID" \
  --storage-class independent_backup
RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
```

7. Pre-publication and local promotion: run `doctor --run-id "$RUN_ID"`; `status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"`; `git diff --check`; then `publish --run-id "$RUN_ID"` and plain `doctor`. Freeze all new review work at this point.

8. Stage only the declared publication evidence: `git add data/living_catalog/current.json`; `git add "$RUN_ROOT"`; `git add "$RECEIPT"`; `git add docs/input-representation-atlas`; `git add protocol/PRISMA_protocol.md protocol/prisma_search_screening_log_2026-07-07.md`; inspect `git status --short`, `git diff --cached --check`, and `git diff --cached --stat`; verify the receipt again; run both normal and `--repository-checkout` doctor modes; then `git commit -m "Update living review through ${END}"`.

9. Deploy the exact commit:
```bash
COMMIT=$(git rev-parse HEAD)
git fetch origin main
git merge-base --is-ancestor origin/main "$COMMIT"
git push origin HEAD:main
if ! git diff-tree --no-commit-id --name-only -r "$COMMIT" | \
  rg -q '^docs/input-representation-atlas/'; then
  gh workflow run deploy-input-representation-atlas.yml --ref main
fi
GITHUB_RUN_ID=""
for attempt in 1 2 3 4 5 6; do
  GITHUB_RUN_ID="$(gh run list --workflow deploy-input-representation-atlas.yml \
    --branch main --limit 10 --json databaseId,headSha \
    --jq ".[] | select(.headSha == \"$COMMIT\") | .databaseId" | head -1)"
  test -n "$GITHUB_RUN_ID" && break
  sleep $((attempt * 5))
done
test -n "$GITHUB_RUN_ID"
gh run watch "$GITHUB_RUN_ID" --exit-status
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets
```

10. Run remote browser QA: set `RELEASE_ROOT=data/living_catalog/releases/${RUN_ID}` and `REMOTE_QA=${RELEASE_ROOT}/remote_browser_qa.json`; run `NODE_PATH="${NODE_PATH:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules}" node scripts/qa_input_representation_atlas.mjs https://bogdandidenko.github.io/text-bio-fundational-models-review/ "$REMOTE_QA"`; then run plain `doctor`. This writes `/tmp/atlas-graph-desktop.png` and `/tmp/atlas-graph-mobile.png`.

11. Record completion with `verify-live --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets --record-completion --workflow-run-id "$GITHUB_RUN_ID" --operator "$OPERATOR" --browser-qa-report "$REMOTE_QA" --screenshot /tmp/atlas-graph-desktop.png --screenshot /tmp/atlas-graph-mobile.png`. Inspect and commit `data/living_catalog/releases/$RUN_ID/completion_record.json`, verify ancestry, and push `HEAD:main` again.

**Stage Contracts**

| Stage | Accepted input | Success and downstream | Supported recovery |
|---|---|---|---|
| `search` | Dated config plus eight providers: PubMed, Scopus, OpenAlex, Semantic Scholar, arXiv, bioRxiv/medRxiv, SpringerNature, Google Scholar | All queries/pages complete and `search_summary_2026-08-17.json` reconciles; exports enter dedup | Restore access or matching Scholar capture; resume `search` |
| `deduplicate` | Eight completed exports | Counts reconcile; clusters/member ledger move to cumulative comparison | Correct invalid export; resume reported stage |
| `prepare-records` | Clusters, all `current.json` master files, Crossref audit | DOI/PMID/arXiv/title comparison complete and conflict queue resolved; new cohort moves on | Fill generated cross-dedup resolution file |
| `enrich-abstracts` | New records | Every missing/short abstract attempted and title fallback corroborated; screening input moves on | Retry unchanged provider routes |
| `abstract-screening` | Locked transport containing title/abstract and bibliographic identity | Every record has final structured scope/architecture/Python/adjudicated result | Retry incomplete frozen batches only |
| `fulltext-candidates` | Abstract `INCLUDE` + `UNCERTAIN`, stable-ID crosswalk, optional duplicate declaration | Raw and retrieval candidate counts reconcile | Correct identity/decision or declared duplicate file |
| `fulltext-download` | Candidate metadata and optional manual main articles | One validated PDF/HTML, terminal not-retrieved, or blocking disposition per candidate; supported payloads enter Docling | Retry providers or declare lawful main article |
| `docling-screening` | Validated PDF/full HTML subset | One identity-corroborated no-VLM canonical profile per retrieved candidate | Replace bad source or rerun Docling |
| `graph-sections` | No-VLM profiles and optional heading overrides | Both target sections are grounded and heading-bounded | Supply canonical heading override |
| `fulltext-screening` | Title, abstract, complete selected sections | Final structured result for every section-screened candidate | Retry frozen batches or resolve section gate |
| `eligibility-resolution` | Full-text decisions and manual CSV where needed | Zero unresolved; accepted records enter VLM, exclusions remain in ledger | Add declared evidence-based resolution |
| `docling-vlm` | Accepted records with authorized PDFs | Fresh complete VLM profiles, figures, captions, descriptions | Obtain valid PDF and resume from download |
| `taxonomy-discovery` | Complete canonical VLM profiles | Open route inventory and study/model registry complete | Retry failed unchanged batches |
| `taxonomy-classification` | Inventory, profiles, frozen taxonomy v1 | Three direct runs, dense audit, adjudication, thresholds and F6 pass; authoritative root moves on | One automatic F6 correction; otherwise whole-cohort rerun |
| `crop-validation` | Authoritative routes and every native source figure | One reviewed crop or explicit `no_suitable_figure` per model, zero unresolved | Retry technical batches; never promote unsupported crop |
| `snapshot` | Prior snapshot plus authoritative update routes/evidence/crops | Counts, IDs, evidence, corpus hashes reconcile | Repair earliest invalid upstream stage |
| `atlas` | New snapshot, prior atlas shell, all figure corpus roots | Build and desktop/mobile/browser/asset/console QA pass | Rebuild atlas and rerun QA |
| `report` | All machine-readable stage summaries | PRISMA denominators and retrieval branches reconcile | Repair source artifact or generator |

**F6 And F7**

F6 runs under `12_taxonomy/semantic_sufficiency/`. Any non-retain or field disagreement enters `semantic_sufficiency_action_queue.csv`. The runner automatically creates `semantic_correction_decisions/`, applies it into `semantic_correction_applied/`, reruns both complete-document reviewers, comparison, adjudication, and finalization under `semantic_sufficiency_revalidation/`, and writes `12_taxonomy/authoritative_taxonomy.json`. A second non-empty queue stops the routine run; the supported next command is `taxonomy-rerun-preflight`, not another patch.

F7 runs under `13_crops/exact_preview_validation/`. It reviews exact published bytes and coordinates, adjudicates, rerenders adjusted crops, searches every native figure for replacements, performs two replacement rounds and the adversarial input-role review, then finalizes. Persistent semantic failure becomes `crop_rejected_no_suitable_figure`: coordinates and supported route IDs are cleared, while the failure remains in `preterminal_status`. Only zero-unresolved `proposed_crossvalidated_crop_ledger.json` is copied to `13_crops/crop_ledger.json`.

**Preservation And Restore**

Each attempt is retained under `logs/STAGE/attempt_NNN/`. Before expensive recomputation, Docling profiles, Graph workspaces, taxonomy Graph runs, adjudications, and crop outputs move to `preserved_stage_outputs/<stage>/attempt_NNN/`; `preservation_ledger.jsonl` records original path, preserved path, counts, bytes, and time. Reuse requires matching source/profile hashes and the same locked contract.

The independent `.tar.zst` archive contains the complete run root: PDFs/HTML, native Docling JSON and Markdown, figures, VLM descriptions, all Graph files, prompts/responses/retries, direct and dense taxonomy runs, F6/F7/crop-agent evidence, snapshot, atlas, reports, and logs. Restore goes only to an empty directory with `archive_living_review_artifacts.py restore`; then verify the receipt, validate `11_docling_vlm/profiles/manifests/canonical_docling_profile_manifest.csv` with `validate_canonical_profile_manifest.py`, and run `doctor`. Immutable provenance paths remain unchanged and resolve through declared artifact roots. Recompute only absent or hash-invalid material.

**Remaining Risks And Gaps**

1. `END` is manually chosen; the runbook gives no executable “last fully elapsed day” calculation or assertion, and uses `Europe/Kiev` while the supplied environment says `Europe/Kyiv`.
2. Search APIs and indices are mutable, Google Scholar only claims provider-visible pagination, and no late-indexing lookback exists.
3. Model names such as `gpt-5.4-mini` and `gpt-5.5` are pinned strings, not immutable backend snapshots; service revisions can change decisions.
4. Python, Node, Playwright, ImageMagick, Codex, and most primary-environment dependency versions are checked for presence, not fully locked. Docling direct packages are pinned, but transitive wheels and hashes are not.
5. Access-dependent terminal `not_retrieved*` outcomes can differ across dates or institutions, with no automatic later retrieval retry.
6. The `deduplicate` success contract permits identifier/title conflicts to remain in a review queue but provides no declaration schema or explicit resolution command for that queue.
7. Manual files require unspecified editing/acquisition actions. The runbook does not provide executable commands for selecting headings, obtaining authorized PDFs, or producing eligibility judgments.
8. F6 says to run a grouped sibling-route adjudication “here” but does not give a generic executable command, case schema, or future-cohort invocation.
9. Selective post-correction F7 revalidation is described but lacks an exact command trajectory and target-manifest construction command.
10. Whole-cohort recovery text hard-codes 52 regenerated profiles, 55 records, and the 28/24 source split; those denominators become obsolete after this update.
11. Whole-cohort atlas commands retain unresolved `CORPUS_ROOT_1` and `CORPUS_ROOT_2` placeholders.
12. `/Volumes/INDEPENDENT_BACKUP/...`, operator identity, and storage independence cannot be derived or verified from repository state. Selecting the receipt via newest mtime is also concurrency-sensitive.
13. There is no general multi-operator filesystem lock; two operators can capture or archive the same interval concurrently.
14. `--force` and post-publication `reconcile --allow-mutated-stage` remain powerful escape hatches whose justification is prose-controlled rather than mechanically approved.
15. Local `publish` advances `current.json` before GitHub Pages succeeds. The freeze rule limits damage but is not a transaction or automatic remote rollback.
16. Manual resolution is not independent dual-human review, so resolver variation can affect future scientific comparability.

**Verdict: PASS WITH RISKS.** The routine path, interval, run identity, stage boundaries, evidence preservation, archive gate, and remote release verification are sufficiently defined to operate. Comparability is still exposed to mutable model/provider behavior, manual gates, late indexing, runtime drift, and non-transactional publication, while several exceptional recovery paths are not executable without operator invention.
