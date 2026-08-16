# Living Review Operator Runbook

**Purpose:** add one dated publication batch to the search, screening,
Docling, taxonomy, crop, and web-atlas corpus without changing the frozen
method or losing provenance.

**Methodological contract:**
`protocol/living_review_update_pipeline_2026-08-09.md`
**Configuration:** `config/living_review_pipeline.json`
**Runner:** `scripts/run_living_review_pipeline.py`
**Public atlas:**
<https://bogdandidenko.github.io/text-bio-fundational-models-review/>

This document is deliberately operational. It specifies what to inspect, what
may be changed, what constitutes success, and how to recover. It does not
replace the protocol or taxonomy codebook.

## 0. Agent execution contract

This is a state machine, not a list of loosely related scripts. An agent running
an update must follow these rules:

1. Start from `doctor`, `current.json`, and the selected `run_manifest.json`.
   Never infer the current stage from filenames or from the last terminal line.
2. Use `scripts/run_living_review_pipeline.py` for the normal path. A script
   mentioned inside the runner is an implementation detail, not an alternative
   entry point.
3. Execute stages in the declared order. Resume the first blocking stage shown
   by `doctor`; do not skip ahead because a downstream-looking file exists.
4. Treat a non-zero exit, timeout, partial JSON response, missing provider page,
   or incomplete shard as failure. Never create a plausible substitute output.
5. Keep every automatic response, retry, schema, prompt, command, and manual
   decision. Report decisions, not hidden chain-of-thought.
6. Do not change queries, prompts, models, schemas, Docling settings, Graph
   contracts, taxonomy definitions, route boundaries, or acceptance thresholds
   during a routine update.
7. Resolve human gates only through their generated declaration files. Never
   edit generated decisions, Markdown, Graph output, route annotations, counts,
   or the published cursor by hand.
8. Reconcile every transition denominator before continuing. `0` is a result
   only when the upstream source completed and the zero is evidenced.
9. Never delete or relocate source PDFs, native Docling profiles, Docling Graph
   workspaces, figures, or LLM logs until a complete archive has been verified
   in independent storage.
10. At every stop, state the last hash-valid stage, the blocking condition, the
    evidence path, and the exact next supported command.

### Supported run modes

Choose one mode before doing work; their outputs must not be mixed.

| Mode | When to use | Taxonomy behavior |
|---|---|---|
| Routine incremental update | New publication-date interval after the published cursor | Open discovery on new eligible records, then classification against unchanged taxonomy v1. |
| Resume | A previously created run is incomplete or failed | Same run ID, inputs, method lock, model, schema, and artifact namespace. |
| Supplemental recall | A missed record is discovered before publication | Register it at the cumulative-dedup boundary and invalidate all downstream stages. |
| Whole-cohort bridge/rerun | A method component changes or an agreement gate fails | Rebuild one complete cohort under one new declared version; never patch selected records into old results. |

`baseline_taxonomy_development`, `incremental_frozen_taxonomy`, and
`full_cohort_frozen_taxonomy` are distinct analysis modes. Inventory generation
is not taxonomy synthesis. A full-cohort rerun against taxonomy v1 must be
reported as frozen-taxonomy reclassification, even though discovery is rerun.

## 1. Safety model

The following files have distinct roles:

| Artifact | Authority |
|---|---|
| `data/living_catalog/current.json` | Published search cursor and cumulative input pointers. |
| `data/living_catalog_updates/update_YYYY-MM-DD/run_manifest.json` | State and hashes of one update run. |
| `data/living_catalog_updates/update_YYYY-MM-DD/00_search/search_config.json` | Exact dated search executed for that run. |
| `14_snapshot*/snapshot_manifest.json` | Cumulative taxonomy/crop snapshot used by the atlas. |
| `docs/input-representation-atlas/data/atlas.json` | Local deployable atlas payload. |
| Remote `data/atlas.json` | What GitHub Pages is actually serving. |

Never edit `current.json`, generated stage output, or a completed manifest to
make a failure disappear. Human intervention is allowed only through a declared
manual-input artifact or the explicit `reconcile` exception.

The cursor date is inclusive. A normal run uses:

`date_from = published search_end + 1 calendar day`

and an inclusive `date_to`. Use the last fully elapsed calendar day in
`Europe/Kiev` by default; searching an unfinished current day can permanently
under-count sources that index later that day. The present pipeline prevents
interval overlap but does not yet automate a retrospective late-indexing
lookback. Record that limitation in every update report.

## 2. Before creating a run

Work from the repository root. Do not clean or reset a dirty worktree: first
identify whether changes belong to another task.

```bash
cd /Users/bogdan.didenko/lpnu/review
git status --short --branch
git branch --show-current
git log -1 --format='%H %cI %s'
python3 --version
python3 scripts/run_living_review_pipeline.py doctor
python3 scripts/verify_living_review_method_lock.py \
  --current-taxonomy-tree "$(jq -r .taxonomy_root data/living_catalog/current.json)/taxonomy_tree.json"
```

Stop if `doctor` is not healthy. In particular, do not plan a new interval when:

- `current.json` is missing or malformed;
- local atlas `generated_from` differs from `taxonomy_root`;
- a completed run is unpublished;
- an unacknowledged stage hash has changed;
- a previous deployment is known to have failed.

Required local components are checked by `preflight`, including Python,
`requests`, Codex, Node/Playwright, ImageMagick, the isolated Docling Python,
baseline artifacts, and non-secret key names. API credentials live in
`api_keys.json`; never print or commit their values. Expected names are defined
by `scripts/api_keys.template.json`.

The configured model roles are not interchangeable:

| Operation | Model/configuration |
|---|---|
| Abstract and selected-section screening | Hash-pinned legacy runner and prompts; `gpt-5.4-mini`. |
| Graph route/section extraction | OpenAI-compatible wrapper; `openai/gpt-5.4-mini`. |
| VLM Docling profiles | Codex VLM role; currently `gpt-5.5`. |
| Crop selection/adjudication | Frozen crop pipeline; `gpt-5.4-mini`. |

Preflight or a hash check must fail rather than silently substitute a runner,
prompt, schema, model name, or taxonomy version.

### Comparability envelope and method lock

`protocol/living_review_method_lock_v1.json` is the executable definition of
"the same method." Every new run manifest records its `method_id` and lock
SHA-256. The runner refuses to execute if any locked file, configured model, or
the current frozen taxonomy tree differs.

Allowed run-to-run variation is limited to the inclusive search dates, records
returned by providers, lawful manual declarations, retry timing, and logged
worker concurrency. The following require a new method version and a bridge
analysis, not `--refresh` inside a routine update:

- a query term, search source, source-side validation rule, or date policy;
- inclusion/exclusion prompt, role topology, model identifier, or JSON schema;
- Docling dependency or conversion/VLM setting;
- Graph direct/dense contract, section boundary rule, or grounding rule;
- taxonomy family/subtype definition or source-to-model route boundary;
- replicate count, agreement metric/threshold, adjudication policy, or crop rule.

`--refresh` on the verifier is reserved for an explicitly reviewed method
version change. If the lock fails, restore the locked implementation or stop,
version the method, define a bridge cohort, and rerun that cohort end to end.
Do not relabel a changed lock as v1 merely to make preflight pass.

## 3. Plan and preflight

Set `END` to the last fully elapsed day. The examples below use `2026-08-11`.

```bash
END=2026-08-11
RUN_ID=update_${END}

python3 scripts/run_living_review_pipeline.py plan --date-to "$END"

# Build the dated config, exhaust the configured Scholar provider pages,
# preserve raw page hashes, and validate the signed bundle.
python3 scripts/run_living_review_pipeline.py scholar-capture \
  --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate \
  --date-to "$END"

python3 scripts/run_living_review_pipeline.py preflight \
  --date-to "$END" --through-stage report
```

Accept the plan only when:

1. `date_from` equals `current.search_end + 1 day`;
2. `date_to` equals the requested inclusive end;
3. `run_root` is `data/living_catalog_updates/$RUN_ID`;
4. `prior_state.taxonomy_root` matches the current atlas source snapshot;
5. preflight reports `ready: true` for every required check;
6. an existing directory with the same run ID is understood as a resume, not a
   fresh run.

An existing manifest fixes its original dates. Passing different dates with the
same run ID is rejected. There is no supported "abandon and overwrite" action;
retain failed attempts and choose a reviewed recovery path.

## 4. Run and observe

```bash
python3 scripts/run_living_review_pipeline.py run \
  --date-to "$END" --manage-server
```

`--manage-server` starts and stops the local OpenAI-compatible Codex wrapper
when a stage needs it. The configured endpoint is local port `8765`. A stopped
terminal or timeout does not imply that the stage completed.

After every non-zero exit, interruption, timeout, or ambiguous terminal state:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
```

Use the first blocking stage and its `validation_issues`; do not guess a later
restart point. Every stage writes append-only command attempts below
`logs/STAGE/attempt_NNN/`. Successful stage output and logs are inventoried by
SHA-256. Recalculation upstream invalidates all downstream stage statuses.

### Resume semantics

```bash
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage STAGE --manage-server
```

- A hash-valid completed stage is skipped.
- A failed or manual-gate stage is recomputed from its declared inputs.
- Successful full-text downloads may be reused across retrieval retries.
- LLM retries retain failed prompts/responses and require complete parsed rows.
- Before an expensive stage is recomputed, existing Docling profiles, Graph
  workspaces, taxonomy Graph runs, and adjudication outputs are moved to
  `preserved_stage_outputs/<stage>/attempt_NNN/`. The append-only
  `preservation_ledger.jsonl` records their original and preserved paths, file
  count, byte count, and timestamp. They remain recovery evidence and are not
  silently mixed into the new attempt; reuse requires matching source/profile
  hashes and the same locked stage contract.
- Never use `--force` as ordinary recovery. It explicitly invalidates the named
  stage and every downstream stage. Use it only after documenting why the
  current stage output is scientifically invalid and must be regenerated.

## 5. Stage contracts

| Stage | Primary evidence/output | Success condition | Recovery |
|---|---|---|---|
| `search` | Eight source exports, exact query config, raw/provider logs, search summary | Every enabled source and all pagination paths declare complete; a failed source is never recorded as zero hits. | Supply credentials or the matching Scholar provider export; resume `search`. Completed source checkpoints remain evidence. |
| `deduplicate` | Within-update clusters and merge log | Export counts reconcile with search summary; identifier/title conflicts remain in review queue. | Fix only an invalid upstream export, then rerun from `search` or `deduplicate` as reported. |
| `prepare-records` | Cumulative matches, Crossref audit, new-record cohort | DOI/PMID/arXiv/title comparison completed against every published master artifact; queue empty or manually resolved. | Complete generated cross-dedup resolution file and resume. |
| `enrich-abstracts` | Identifier/title retrieval logs and screening input | Every missing abstract attempted; accepted title fallback has year/author corroboration; no bounded diagnostic output becomes canonical. | Resume the stage; provider failures and rejected candidates remain logged. |
| `abstract-screening` | Scope, architecture, Python gate, adjudicator logs | Frozen runner/prompt hashes match; every input record has a final structured result. | Retry incomplete batches through the same stage/model/schema; never combine outputs from a changed prompt version. |
| `fulltext-candidates` | INCLUDE/UNCERTAIN manifest | Candidate IDs map one-to-one to abstract decisions and source records. | Correct upstream decisions only through their declared resolution path. |
| `fulltext-download` | Attempt ledger, payload manifest, and `fulltext_retrieval_dispositions.json` | Each candidate has one mutually exclusive validated PDF/HTML, terminal not-retrieved, or blocking technical disposition. | Retry providers or declare a lawful manual main article. Abstract pages and supplements are invalid. |
| `docling-screening` | Retrieved-candidate subset and complete no-VLM Docling profile manifest | Every candidate with a validated supported PDF/HTML has exactly one identity-corroborated profile; terminal not-retrieved records remain only in the PRISMA retrieval denominator. | Replace wrong/corrupt source payload and rerun from full-text download; otherwise rerun Docling stage. |
| `graph-sections` | Graph evidence and complete heading-bounded sections | Both data-source and input-representation targets are grounded; empty, duplicate, root-level, or near-whole-document sections are rejected. | Use canonical heading override through the generated template. |
| `fulltext-screening` | Same role topology over title, abstract, complete selected sections | Every candidate has final structured decision; no complete Docling markdown or selector reason is added to reviewer input. | Retry incomplete frozen batches or complete section overrides first. |
| `eligibility-resolution` | Accepted, excluded, unresolved ledgers | No unresolved record remains; every manual row has decision, evidence, resolver, and timestamp. | Inspect complete Docling evidence and add only a declared manual resolution. |
| `docling-vlm` | Fresh complete VLM-enriched profiles | Every newly accepted report has a validated PDF profile, figures, captions, and picture descriptions. HTML-only accepted reports block here. | Obtain an authorized main-article PDF and rerun from full-text download. |
| `taxonomy-discovery` | Open route candidates and study/model registry | Discovery sees full canonical profiles without frozen family labels in its extraction prompt. | Retry failed document batches with unchanged schema/model. |
| `taxonomy-classification` | Three direct runs, dense audit, adjudication, evidence ledger | All profiles succeed; every route is grounded; Jaccard >=0.80, family agreement >=0.90, alpha >=0.80; every dense-only route adjudicated. | A failed threshold requires a reviewed whole-cohort rerun under one prompt/schema version. Do not patch individual outputs. |
| `crop-validation` | Two selectors, adjudicator, crop coordinates/dispositions | Every included model has a validated source crop or explicit no-suitable-figure disposition. | Retry failed model batches; retain every selector response and source-figure identity. |
| `snapshot` | Cumulative registry/routes/evidence/crops and manifest | Counts and exact route/evidence IDs reconcile; source-corpus hashes are recorded. | Repair the earliest invalid upstream stage; never hand-edit snapshot totals. |
| `atlas` | Staged static UI and browser QA | Build report matches snapshot; desktop/mobile screenshots, review-iteration filter, assets, and console checks pass. | Fix builder/UI code, rebuild atlas stage, rerun browser QA. |
| `report` | PRISMA fact table, retrieval dispositions, update report | Every transition denominator is derived from artifacts and retrieval branches are mutually exclusive. | Fix source artifact or report generator; do not edit counts manually. |

### Boundary-by-boundary execution logic

The stage table defines acceptance. The following defines what crosses each
boundary and what the agent must check before advancing.

1. **Search to within-update deduplication.** `00_search/search_summary.json`
   must reconcile to the sum of all completed source exports. Preserve database,
   query name, raw rank, provider identifier, date status, and raw-page hash on
   every record. A provider failure stays a failure; it does not contribute zero.
2. **Within-update to cumulative deduplication.** Keep one update cluster with a
   complete member/merge ledger, then compare DOI, PMID, arXiv/bioRxiv identifier,
   and normalized title against every published master artifact. Cross-version
   conflicts remain visible. An exact file duplicate reuses its prior `study_id`;
   reuse of the same `record_id` is not itself a duplicate.
3. **Records to abstract screening.** Enrich missing abstracts through declared
   identifier and title routes. The screening payload is exactly `title +
   abstract`; title-only fallback is explicit and identity-corroborated. Scope
   reviewer and architecture reviewer are separate prompt roles of the same
   locked `gpt-5.4-mini`, followed by the Python gate and adjudicator.
4. **Abstract screening to retrieval.** Every `INCLUDE` and `UNCERTAIN` decision
   becomes one full-text candidate. The count must equal the corresponding final
   decision counts, after stable-ID uniqueness checks.
5. **Retrieval to Docling screening.** Every candidate receives exactly one
   disposition: validated main-article PDF/HTML, terminal evidence-backed
   not-retrieved, or blocking technical failure. Only validated supported payloads
   enter Docling. Supplements, abstract pages, XML-only payloads, and login pages
   do not masquerade as main articles.
6. **No-VLM Docling to Graph sections.** Build complete native profiles with the
   locked PDF settings. Graph direct extraction locates `data_source` and
   `input_representation` evidence. Recover the complete heading-bounded section,
   not an evidence quote, arbitrary character window, root document, or whole
   Markdown. Deduplicate identical selected sections.
7. **Selected sections to full-text screening.** Reviewer input is exactly
   `title + abstract + complete selected_full_text_sections`. It does not contain
   `selector_reason`, `section_evidence`, or complete `docling_markdown`. Use the
   same role topology and model as abstract screening in the configured
   full-document mode.
8. **Eligibility to canonical VLM profile.** Resolve every remaining UNCERTAIN
   through declared evidence. Only accepted records receive fresh, complete
   VLM-enriched profiles. Preserve source-document identity, native Docling JSON,
   Markdown, figures, captions, and VLM picture descriptions as one profile.
9. **Profiles to route taxonomy.** Open direct discovery sees each complete
   document without family labels. Three independent direct classifications use
   the fixed candidate inventory and taxonomy v1; dense scoped fill audits
   coverage; a separately prompted adjudicator dispositions conflicts and every
   dense candidate. The analysis mode must be
   `incremental_frozen_taxonomy` for a routine batch.
10. **Routes to crops, snapshot, and atlas.** Every accepted route must pass
    provenance and taxonomy consistency. Crop annotations reference accepted
    route IDs and native figures. Snapshot merge preserves prior routes and adds
    only the new cohort. The atlas is generated from the snapshot and exposes the
    review-iteration tag without changing existing filters or model details.

### Denominator ledger

Before `report`, verify these identities from machine-readable artifacts:

```text
raw hits = sum(completed source export counts)
within-update unique = raw hits - within-update duplicate members
new records = within-update unique - cumulative matches/exclusions
abstract-screened = records with a final title/abstract decision
full-text candidates = abstract INCLUDE + abstract UNCERTAIN
retrieval candidates = retrieved + terminal not-retrieved
section-screened = retrieved reports with a valid targeted-section pair
eligibility inputs = section-screened records
accepted + excluded = resolved eligibility inputs
taxonomy records = newly accepted records with complete VLM profiles
cumulative snapshot = prior snapshot + accepted update, under explicit duplicate/version linkage
```

These are different denominators. Route, configuration, model, study, and record
counts must never be substituted for one another. A paper may yield multiple
models, configurations, and routes; a model may belong to several carrier
families through separate source-to-model routes.

## 6. Manual gates

Generated templates are authoritative. Copy their structure into the target
manual file; do not rename candidate IDs, add unrequested records, or paste
evidence in place of a canonical selector.

### Search provider export

Target: `00_search/google_scholar_provider_export.json`
Contract: `protocol/google_scholar_provider_export_schema.md`.

The query signature, configured query names, raw page hashes, pagination end,
date boundary, and result count must match the generated bundle. Missing or
partial Scholar evidence blocks deduplication.

The normal interface is `scholar-capture`, followed by the read-only-capable
`scholar-validate` command shown in Section 3. The lower-level collector remains
available for diagnosis, but operators do not have to construct its arguments.

### Cumulative duplicate conflict

Template: `02_records/manual_cross_dedup_resolutions.template.json`
Target: `02_records/manual_cross_dedup_resolutions.json`.

Each generated `update_cluster_id` requires:

```json
{
  "update_cluster_id": "162",
  "decision": "keep_new or exclude_as_duplicate",
  "rationale": "Identifier/version evidence",
  "resolver": "Name or declared computational resolution",
  "resolved_at": "ISO-8601 timestamp"
}
```

### Manual full text

Template: `05_fulltext/manual_fulltexts.template.json`
Target: `05_fulltext/manual_fulltexts.json`.

```json
{
  "candidate_id": "update_YYYY-MM-DD__rec_NNNNNN",
  "file": "/absolute/path/to/main_article.pdf",
  "source_url": "https://source/article.pdf",
  "retriever": "operator",
  "retrieved_at": "ISO-8601 timestamp"
}
```

The pipeline revalidates file signature, size, title/DOI identity, and main
article status. A filename extension is not validation.

Inspect `05_fulltext/fulltext_retrieval_dispositions.json` before adding a
manual file. `manual_gate_required: true` means retry or supply a lawful main
article. `terminal_retrieval_evidence: true` with `not_retrieved*` is a valid
PRISMA disposition supported by the retained attempt ledger; it is not a claim
that the article does not exist. The exact status mapping is defined in
`protocol/fulltext_retrieval_disposition_schema.md`.

### Canonical section override

Template: `08_section_input/manual_section_overrides.template.json`
Target: `08_section_input/manual_section_overrides.json`.

Use the exact Markdown path/hash from the canonical no-VLM manifest and exact
Docling heading trails. Include one selector for `data_source` and one for
`input_representation`; the same section may satisfy both when justified.

```json
{
  "record_id": "...",
  "candidate_id": "...",
  "source_markdown": "/absolute/canonical/path.md",
  "source_markdown_sha256": "...",
  "sections": [
    {"target_section_types": ["data_source"], "heading_path": ["Methods", "Data"]},
    {"target_section_types": ["input_representation"], "heading_path": ["Methods", "Architecture"]}
  ],
  "rationale": "Why these complete sections answer both targets",
  "resolver": "...",
  "resolved_at": "ISO-8601 timestamp"
}
```

### Eligibility resolution

Target: `10_eligibility/manual_resolution.csv`.

Required columns:

`record_id,manual_decision,rationale,resolver,resolved_at`

`manual_decision` is `INCLUDE` or `EXCLUDE`. The rationale must cite the
specific full-document evidence that resolves the uncertainty. If Codex performs
the resolution, label it computational and do not describe it as human
validation.

After any manual edit, resume the blocked stage without `--force`, then run
`doctor` again. The manual artifact hash becomes part of the stage record.

## 7. Failure decisions

| Symptom | Action | Never do |
|---|---|---|
| API key missing, 401/403, pagination incomplete | Resolve source access and resume `search`. | Treat the source as zero records. |
| 429/timeout | Preserve checkpoint and retry the same stage. | Replace the export with an older unmatched file. |
| Existing run ID | Inspect its manifest and resume it. | Delete the directory and reuse the ID. |
| LLM partial/malformed batch | Resume same stage; retained attempts show split recovery. | Manually manufacture parsed rows or change models mid-run. |
| Wrong/supplement PDF | Add the correct main article via manual manifest. | Rename the wrong payload to `.pdf`. |
| Docling profile identity/completeness failure | Correct source or rerun Docling stage. | Patch canonical Markdown/JSON by hand. |
| Graph root/empty/whole-document section | Supply canonical heading selectors. | Paste arbitrary text or send whole Docling markdown to screening. |
| Taxonomy agreement below threshold | Stop and review prompt/schema version for a complete rerun. | Accept a convenient replicate or recode one paper manually. |
| Stage marked complete but hash changed | Inspect `doctor.validation_issues`; regenerate or use reviewed reconciliation only for a documented post-run correction. | Acknowledge unexplained mutation. |
| Local publish succeeds but Git/Pages fails | Do not start another interval. Retry deployment of the same commit or restore state+atlas together. | Revert only `current.json` or advance again. |
| `verify-live` differs | Treat deployment as incomplete; inspect workflow/cache/branch and redeploy same artifact. | Run the next update. |

### Whole-cohort taxonomy rerun

Do not improvise a partial rerun after a prompt/schema change or failed
acceptance threshold. Prepare the complete current cohort first:

```bash
RERUN=data/living_catalog/taxonomy_rerun_preflight_$(date +%F)
python3 scripts/run_living_review_pipeline.py taxonomy-rerun-preflight \
  --output-dir "$RERUN"
cat "$RERUN/readiness.json"
```

The command inventories every native Docling corpus, checks the expected
record denominator, and writes an executable `commands.sh`. On the recovered
current corpus it also prepares a 52-document VLM regeneration config from the
recovered source PDFs. The readiness ledger distinguishes the 28 exact
historical PDFs from 24 valid but version/hash-different PDFs; this difference
must remain visible in any rerun report. Taxonomy classification cannot begin
until all 55 records have complete native Docling JSON, Markdown, figure
manifests, and source-document hashes in one combined canonical manifest.

After a whole-cohort rerun passes taxonomy and crop acceptance, freeze it with
the dedicated full-cohort builder. Do not create a fake empty prior snapshot or
use the incremental merge command for this case:

```bash
python3 scripts/freeze_full_cohort_snapshot.py \
  --taxonomy-root "$RERUN/taxonomy" \
  --frozen-taxonomy-root "$(jq -r .taxonomy_root data/living_catalog/current.json)" \
  --crop-ledger "$RERUN/crops_final/crop_ledger.json" \
  --output-dir "$RERUN/snapshot_full" \
  --run-id "full-cohort-rerun-$(date +%F)" \
  --corpus-root "$RERUN/combined_vlm_profiles"
```

The command requires a passing `agreement_metrics.json`, exact route/evidence
parity, one crop disposition per model, valid crop coordinates and route
references, complete Docling profile artifacts, and the unchanged frozen
taxonomy tree. Explicitly reasoned `unresolved` dense candidates remain visible
and are not forced into accepted or excluded categories.

The atlas builder writes data and figure assets into an existing UI shell. Seed
the staged output from the last validated atlas, then rebuild with every actual
corpus root that contains a `figures/` directory. A combined manifest is not a
replacement for those asset roots:

```bash
cp -R docs/input-representation-atlas "$RERUN/atlas"
python3 scripts/build_input_representation_atlas.py \
  --taxonomy-root "$RERUN/snapshot_full" \
  --crop-ledger "$RERUN/snapshot_full/crop_ledger.json" \
  --output-dir "$RERUN/atlas" \
  --prior-atlas-root docs/input-representation-atlas \
  --corpus-root CORPUS_ROOT_1 \
  --corpus-root CORPUS_ROOT_2
```

Run `scripts/qa_input_representation_atlas.mjs` against a local HTTP server.
Its assertions must derive expected model, route, group, subtype, and batch
counts from the staged `atlas.json`; never hard-code counts from an older
snapshot.

## 8. Preserve Docling and Graph artifacts

Git is not the storage layer for the expensive corpus. `.gitignore` deliberately
excludes source PDFs, native Docling payloads, figures, and Graph workspaces.
`artifact_manifest.csv` is an integrity ledger, not a backup: it cannot restore
a missing file.

### What must be retained

Archive the complete run root, not a hand-selected list. At minimum it contains:

- validated source PDF/HTML payloads and their retrieval/identity evidence;
- no-VLM and VLM canonical profile manifests;
- native `*.docling.json`, complete Markdown, figure manifests, extracted images,
  captions, and VLM picture descriptions;
- every Graph `document.dclg`, `document.json`, `chunks.json`, `graph.html`,
  `metadata.json`, extraction summary, provenance row, schema, prompt, response,
  retry, and error;
- all direct replicates, dense coverage, adjudication, evidence ledgers, taxonomy
  outputs, crop decisions/assets, snapshot, atlas build evidence, and run logs.

The canonical Docling profile is the reusable document representation. A Graph
workspace is reusable only when the source-document SHA, canonical Docling JSON
SHA, locked Graph code/contract, model, schema, and extraction stage all match.
If one of those changes, create a new sibling run; never overwrite the old
workspace. A publisher version with a different source hash is a new profile,
even when its DOI/title represents the same study.

### Create and verify an immutable archive

Generate the ledger only after the run root is final. The archive command first
rehashes every declared file and rejects both missing files and unlisted extras.

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
```

The command streams a compressed `.tar.zst`, verifies every archived member
against the source ledger, and writes an immutable receipt under
`data/living_catalog/archives/`. Inspect and commit the receipt. A second folder
on the same internal disk may be labelled `local_secondary`, but it is not an
independent backup and does not satisfy the publication gate.

Verify the archived location again before deleting, migrating, or publishing:

```bash
RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
```

If an archive is copied to another disk or cloud-mounted path, verify that exact
copy without changing the receipt:

```bash
python3 scripts/archive_living_review_artifacts.py verify \
  --receipt "$RECEIPT" \
  --archive /path/to/copied/archive.tar.zst
```

Restore only into an empty directory, then point recovery tooling at the
restored root or restore to the original absolute location when old manifests
contain absolute paths:

```bash
python3 scripts/archive_living_review_artifacts.py restore \
  --receipt "$RECEIPT" \
  --destination /empty/path/restored_run
```

After restore, regenerate no scientific output. First run archive verification,
profile-contract validation, the relevant canonical manifest check, and
`doctor`. Recompute an expensive Docling/Graph stage only if the payload is
genuinely absent or fails its recorded hash/identity contract.

### Retention rule

Keep the live run root plus at least one independently stored verified archive.
Do not prune failed LLM attempts or intermediate Graph workspaces merely because
a final JSON exists; they establish how the final decision was reached. Local
payloads may be removed for space only after independent verification, receipt
commit, restore smoke test, and confirmation that no current manifest or corpus
root still points to the path.

## 9. Pre-publication review

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
git diff --check
```

Do not publish unless all 18 stages are complete and hash-valid, the report is
consistent with the snapshot, taxonomy gates passed, crop/atlas QA passed, and
all manual resolutions are retained. A method-locked run also requires an
`independent_backup` receipt matching the final run artifact manifest. `status` is the complete manifest;
`doctor` is the concise decision view.

```bash
python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor
```

`publish` atomically promotes the local atlas and advances local `current.json`.
It does **not** publish GitHub Pages. Therefore local promotion and remote
deployment are currently not a true two-phase transaction. Until the runner
implements pending/finalized publication, the operational rule is:

> After local `publish`, freeze new review work until the exact atlas has been
> committed, deployed, and verified remotely.

## 10. Git and GitHub Pages

Never use `git add .`. Review the diff and stage only intentional code/protocol,
the published state, the versioned run evidence permitted by `.gitignore`, and
the atlas:

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
```

Before committing, inspect staged paths for API keys, raw licensed full texts,
Docling binaries/images excluded by policy, caches, and unrelated work. The
repository `.gitignore` and
`data/input_representation_taxonomy_2026-07-11/github_artifact_policy.md`
define the current large-artifact precedent; the run manifest and artifact
hashes preserve excluded local evidence.

Build the run-level hash ledger from the complete local archive before staging.
The ledger and its summary must be committed even though the large payloads are
not. Then verify both storage modes explicitly:

```bash
python3 scripts/docling/build_input_taxonomy_artifact_manifest.py \
  --artifact-root "data/living_catalog_updates/${RUN_ID}"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID" \
  --repository-checkout
```

The first command validates the complete operator archive. The second doctor
mode models a clean Git checkout: it may waive a missing payload only when its
path, byte count, and SHA-256 agree in the stage inventory and committed
`artifact_manifest.csv`, and Git marks that path as ignored and untracked.
Changed tracked files, undeclared omissions, or a damaged ledger remain fatal.

```bash
git commit -m "Update living review through ${END}"
```

The Pages workflow is `.github/workflows/deploy-input-representation-atlas.yml`.
Push-triggered deployment currently accepts `main` and the legacy
`codex/fulltext-section-screening-audit` branch; `main` is the preferred
publication branch. The workflow runs `doctor --repository-checkout`, writes an ephemeral
commit-bound file/tree manifest, uploads the atlas, deploys Pages, then retries
full remote verification five times.

```bash
git push origin main
gh run list --workflow deploy-input-representation-atlas.yml --limit 5
gh run watch RUN_ID_FROM_GITHUB --exit-status
COMMIT=$(git rev-parse HEAD)
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets
python3 scripts/run_living_review_pipeline.py doctor
```

Remote verification uses cache-busting requests and requires matching source
snapshot and record/study/model/configuration/route counts, exact `atlas.json`
bytes, the expected Git commit, the complete atlas tree hash, and every remote
file hash. The contract is
`protocol/living_review_release_evidence_schema.md`.

Required UI checks:

- landing summary and five family counts load;
- review-iteration filter shows the exact records from the new iteration alone
  and clears correctly;
- at least one new model detail opens with routes, evidence, and crop/disposition;
- no missing figure assets or console errors;
- desktop and mobile screenshots are readable;
- remote `atlas.json` exactly matches local bytes.

## 11. Deployment failure and rollback

If commit, push, workflow, or remote verification fails after local `publish`:

1. Do not run `plan` for another interval.
2. Keep the failed run and local state unchanged while retrying deployment of
   the same commit/artifact.
3. Diagnose branch trigger, Pages environment, asset path, and remote hash.
4. If the update itself is invalid and must be withdrawn, restore
   `current.json` and `docs/input-representation-atlas/` together from the same
   last-known-good commit, deploy that commit, and verify it. Never restore only
   the cursor.
5. Record the incident and recovery commits in the run report.

If the update must be withdrawn, create a new auditable rollback commit. Replace
`LAST_GOOD_COMMIT` with the commit whose state and atlas were last verified
together; do not reset branch history:

```bash
git switch -c "codex/rollback-${RUN_ID}"
git restore --source LAST_GOOD_COMMIT -- data/living_catalog/current.json
git restore --source LAST_GOOD_COMMIT -- docs/input-representation-atlas
git diff --check
git add data/living_catalog/current.json docs/input-representation-atlas
git commit -m "Rollback invalid living review publication ${RUN_ID}"
git push origin HEAD
```

Deploy the rollback commit through the normal Pages workflow, run exact remote
verification against its SHA, and add `--recovery-commit` to the incident record.

Retry the exact failed workflow run, not a newly assembled artifact:

```bash
gh run rerun GITHUB_RUN_ID
gh run watch GITHUB_RUN_ID --exit-status
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$(gh run view GITHUB_RUN_ID --json headSha -q .headSha)" \
  --check-assets
```

Record the failure immediately:

```bash
python3 scripts/run_living_review_pipeline.py incident \
  --run-id "$RUN_ID" --phase deployment \
  --summary "Observed failure and chosen recovery" \
  --operator "OPERATOR" --commit "COMMIT" \
  --workflow-run-id "GITHUB_RUN_ID"
```

The runner has a local publication journal and rollback for a crash during
atlas/state promotion. It does not currently automate rollback across Git and
GitHub Pages.

## 12. Supplemental recall and reconciliation

Before publication, register a missed record through the first-class input
boundary rather than creating sibling stages:

```bash
python3 scripts/run_living_review_pipeline.py register-supplemental \
  --run-id "$RUN_ID" --record-file /absolute/path/record.json \
  --reason "Documented recall correction" \
  --source-url "https://publisher.example/article" \
  --resolver "OPERATOR"
```

The command invalidates `prepare-records` and everything downstream. The record
then passes cumulative deduplication, Crossref, both screening rounds, retrieval,
Docling, taxonomy, grounding, crop, snapshot, and atlas under the unchanged
contracts. See `protocol/supplemental_recall_record_schema.md`.

Use `reconcile` only for a correction discovered after publication, after the
complete downstream evidence chain and cumulative snapshot have already been
built and audited.

After building a single cumulative snapshot and atlas, inspect mutations with
`doctor`. Then use the explicit files and reason:

```bash
python3 scripts/run_living_review_pipeline.py reconcile \
  --run-id update_YYYY-MM-DD \
  --snapshot-root data/living_catalog_updates/update_YYYY-MM-DD/14_snapshot_CORRECTED \
  --atlas-root docs/input-representation-atlas \
  --supplemental-record-file path/to/supplemental_input_records.json \
  --reason "Documented recall correction and evidence" \
  --allow-mutated-stage STAGE
```

Each `--allow-mutated-stage` must correspond to a concrete `doctor` hash issue
whose cause is explained. `reconcile` cannot waive an incomplete stage. It
checks snapshot/atlas counts and source roots, writes an immutable reconciliation
ledger, adds supplemental records to future cumulative deduplication, and marks
the publication mode explicitly in PRISMA history.

## 13. Completion record

An update is complete only when all of the following are recorded:

- inclusive interval and search execution timestamp;
- run ID and run-manifest hash;
- method ID, method-lock hash, and independently verified archive receipt;
- exact source/query configuration and source completion states;
- search, dedup, screening, retrieval, eligibility, taxonomy, crop, and atlas counts;
- prompt/runner/schema/model and taxonomy identifiers;
- every manual/reconciliation decision and resolver;
- snapshot path/hash and local atlas hash;
- Git commit and Pages workflow run;
- successful remote byte comparison and browser QA;
- next cursor reported by final healthy `doctor`.

Create that record only after remote and visual QA succeed:

```bash
python3 scripts/run_living_review_pipeline.py verify-live \
  --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets \
  --record-completion --workflow-run-id "$GITHUB_RUN_ID" \
  --operator "OPERATOR" \
  --screenshot /absolute/path/desktop.png \
  --screenshot /absolute/path/mobile.png
```

The immutable result is
`data/living_catalog/releases/$RUN_ID/completion_record.json`.
Commit this record after inspecting it. The release-record path does not trigger
the atlas Pages workflow, so this provenance commit does not redeploy a different
payload:

```bash
git add "data/living_catalog/releases/${RUN_ID}/completion_record.json"
git diff --cached --check
git commit -m "Record verified release evidence for ${RUN_ID}"
git push origin HEAD
```

## 14. Known limitations

The following are explicit open engineering issues, not implied guarantees:

1. Local `publish` advances the cursor before remote Pages verification; the
   operational freeze above is required until two-phase publication exists.
2. Late indexing into already closed publication-date intervals is not yet
   covered by an automated retrospective lookback search.
3. Run creation has stale-state publication checks but no general multi-operator
   filesystem lock for concurrent execution.
4. Manual resolution is provenance-bearing but is not automatically independent
   dual-human review; do not describe it as such.
