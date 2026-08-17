# Forensic audit of the taxonomy and atlas agent traces

Date: 2026-08-14

## Scope

This audit compares:

- the original 52-record taxonomy run in
  `data/input_representation_taxonomy_2026-07-11/`;
- the 55-record full-cohort rerun in
  `data/living_catalog/taxonomy_rerun_preflight_2026-08-12/`;
- the original crop cross-validation in
  `data/input_representation_atlas_crop_crossvalidation_2026-07-12/`;
- the current crop pipeline and published atlas snapshot.

The machine-readable audit is
`analysis/taxonomy_agent_trace_audit_2026-08-14.json`. It is regenerated with:

```bash
python3 scripts/audit_taxonomy_agent_traces.py \
  --output analysis/taxonomy_agent_trace_audit_2026-08-14.json
```

The audit examines commands, prompts, response logs, run summaries, retries,
adjudication resolution, registries, source hashes, final routes, evidence
strength, crop decisions, and the generated methodological description. It does
not request or claim hidden chain-of-thought.

## Follow-up: F5 migration ledger, 2026-08-17

The missing cross-version transition ledger identified in F5 has now been
created under `analysis/input_taxonomy_migration_2026-08-17/`. It compares the
same 52 records at study, model, configuration, and route levels without an LLM.
All 52 study identifiers are stable. The shared cohort changes from 489 to 549
routes; the additional three records contribute 37 routes to the 586-route
current total. A conservative maximum-weight matcher accepts 279 one-to-one
primary route links and leaves all weaker or ambiguous relationships visible
rather than forcing them.

The separate analyst review of the 15 largest deltas shows that the drift mixes
task/model decomposition, route aggregation, entity normalization, and genuine
carrier/lifecycle recoding. Consequently, F5 is corrected as an audit-artifact
gap, but the substantive ProCyon, X-Cell, SciCore-Omics, scMOBA, TeamPath, and
Longevity-LLM cases remain part of the F6 evidence-sufficiency work. The old and
current route totals remain valid within-version outputs, not directly
comparable prevalence estimates.

## Follow-up: F6 semantic sufficiency, 2026-08-17

The semantic-sufficiency audit requested in F6 is complete under
`analysis/taxonomy_semantic_sufficiency_audit_2026-08-17/`. It selected the
union of dense-only and inferred final routes: 95 routes from 18 records. Two
independent `gpt-5.4-mini` roles reviewed all ten material fields against each
complete canonical Docling Markdown document without truncation; 66 routes with
field disagreement or a non-retain decision went to a separate full-document
adjudicator. Every returned supporting quote was verified against canonical
Markdown, and every request, schema, response, error, retry, command, hash, and
timing is retained.

The final dispositions retain 45 routes as-is, recommend field revision for 46,
and leave four ProCyon routes for manual full-text resolution. The dominant
problem is over-specific carrier subtype, model-visible-form, insertion, or
fusion-topology coding, rather than an untraceable paper or fabricated route.
The four unresolved routes use real benchmark labels (`GO Function`, `GtoP`,
`Drugbank Transporter`, and `Drugbank Target`) but do not establish the current
peptide-specific input interpretation. The audit closes the missing F6 test, but
does not silently mutate the canonical 586-route output: its 50-row action queue
must be resolved in a versioned correction release before that output can be
called semantically cross-validated.

## Follow-up: F7 exact-preview validation, 2026-08-17

The missing exact-preview and exact-model input-role checks are complete under
`analysis/atlas_exact_preview_validation_2026-08-17/`. The audit reconstructed
and hash-verified the exact rendered crops for all 98 currently cropped models;
the other 11 already had `no_suitable_figure`. Two blind `gpt-5.4-mini` visual
roles reviewed every crop, 19 conflicts were adjudicated, and every adjusted or
replacement crop was rendered and reviewed again.

Eighty-nine crops pass the strengthened gate. The OCellus-Agent crop was adjusted
and revalidated. Nine prior crops fail exact input-role validation. For six of
those cases, the audit searched every native source figure and attempted
replacement selection/cropping; no candidate survived both exact-preview and
adversarial input-role review. The proposed cross-validated ledger therefore has
89 crops and 20 explicit no-suitable-figure dispositions, with zero unresolved
models. It is stored separately from the canonical crop ledger. F7's validation
gap is closed, while promotion of the proposed ledger and atlas rebuild remain a
reviewed correction-release step rather than an audit side effect.

## Verdict

The LLM, Docling Graph, VLM, and crop-agent executions were real. There is no
evidence that model responses were fabricated, copied into empty placeholders,
or replaced by deterministic template output. The current run contains complete
per-role requests and responses, retained failed attempts, and successful repair
artifacts.

The run is nevertheless **not ready to be described as a fully validated
replacement of the original result**. Two blocking defects and four material
methodological gaps were found:

1. the current registry corrupts canonical-record and exact-duplicate flags;
2. the generated current Methods text falsely reuses several statements from the
   old run;
3. the current run applies the frozen taxonomy but does not re-synthesize it;
4. every shared source Markdown changed, while the effect of input regeneration
   is not separated from the effect of the new classification prompt;
5. the shared 52-record output changed substantially without a migration audit;
6. crop validation is materially weaker than the original cross-validation.

The first two are factual release blockers. The others do not invalidate the
execution, but they limit what can be claimed from it until explicitly resolved.

## Stage comparison

| Stage | Original run | Current run | Assessment |
|---|---:|---:|---|
| Canonical records | 52 | 55 | Current denominator is complete |
| Studies | 51 | 54 | Correct at the distinct `study_id` level |
| Open discovery | 52/52; 583 candidates | 55/55; 595 candidates | Actually executed |
| Taxonomy synthesis | 3 proposals + separate reconciliation | No new proposals; frozen v1 reused | Not equivalent to a full re-derivation |
| Direct classifications | 3 complete | 3 complete after logged repairs | Actually executed |
| Dense coverage | 2,208 candidates | 2,893 candidates | Actually executed |
| Adjudication | complete, including logged replay normalization | 55/55 selected after retained failures and repairs | Actually executed |
| Final routes | 489 | 586 | Large change requires migration analysis |
| Agreement gate | Jaccard 0.948; family 0.925; alpha 0.875 | 0.937; 0.925; 0.881 | Both pass within-run gates |
| Crop review | multi-stage adversarial and exact-preview validation | two selectors + adjudicator + cropper | Current crop QA is simplified |

## Findings

### F1. Blocking: prior-registry reuse is misclassified as duplication

`build_input_taxonomy_registry.py` treats any source hash found in the prior
registry as evidence of an exact duplicate, even when the prior row and current
row have the same `record_id`. It then marks that reused record as noncanonical.

Observed consequence:

- old registry: 52 records, 51 canonical records, 2 exact-duplicate rows;
- current registry: 55 records, only 17 canonical records, 38 rows marked as
  exact duplicates;
- current `registry_summary.json` contains 37 reported duplicate groups: one
  real cross-record group and 36 false self-duplicate groups that list the same
  record twice;
- `agreement_metrics.json` reports the OmniNA-linked sensitivity denominator as
  17 studies, although the independently computed value in the registry summary
  is 53.

The route rows retain their study identifiers, so this does not by itself alter
the 586 route annotations. It corrupts study-level reporting, duplicate special
cases, sensitivity analysis, and any downstream statistic that filters on
`canonical_record_for_study`.

Root cause:

- `scripts/docling/build_input_taxonomy_registry.py`, prior-hash handling around
  lines 95-123;
- `scripts/docling/analyze_input_taxonomy_runs.py`, sensitivity count around
  lines 516-526.

### F2. Blocking: current Methods text describes work that was not performed

The generated current file
`taxonomy/manuscript_methods.md` says that the corpus contained 52 records, that
discovery produced 583 candidates, that three taxonomy syntheses were reconciled
in this run, and that four old adjudication responses were replayed. The actual
current trace has 55 records, 595 discovery candidates, no new three-pass
taxonomy synthesis, and a different repair history.

This is the clearest instance of methodological imitation found in the audit:
the computational run is genuine, but its prose generator selects a hard-coded
old full-corpus paragraph whenever `--incremental` is absent. The current
55-record run was nonincremental, so old 52-record prose was silently inserted
and only the final count paragraph was updated.

Root cause: `scripts/docling/analyze_input_taxonomy_runs.py`, lines 653-679 and
712-714.

### F3. Major: the current run is confirmatory classification, not taxonomy re-synthesis

The original run contains `proposal_r1`, `proposal_r2`, `proposal_r3`, and an
adjudicated taxonomy. Current `commands.sh` runs only `--mode inventory` after
open discovery and then loads the existing taxonomy tree from the August
snapshot.

The old, input snapshot, and current snapshot taxonomy trees have the identical
SHA-256:

`b36c0261a93c6d0e19a2502ec416ba26bf71315cfc04bf3323b260c239693bf9`

This is a defensible living-review policy: the three new papers test coverage of
the frozen schema without moving category boundaries. It must be called
**full-cohort re-extraction and classification under frozen taxonomy v1**, not a
full rerun of the original taxonomy-development protocol. The new papers did not
participate in independent taxonomy synthesis.

### F4. Major: source documents and prompt changed together

All 52 shared records have different source-Markdown hashes between runs. None
has the same length:

- 51 became longer and 1 shorter;
- total increase: 352,400 characters;
- median change: +6,860.5 characters;
- range: -2,073 to +19,539 characters.

The current baseline was regenerated from recovered source documents through a
native VLM-enriched Docling conversion. The classification prompt also changed
from v1 to `v3-interface-boundary`. Because both factors changed together, route
differences cannot be attributed specifically to better document recovery,
VLM enrichment, or the new carrier-boundary instructions.

This is not truncation: current direct request prompts have median sizes of
146,682-157,082 characters and maxima above 282,000 characters, with
`max_tokens=None`. It is a comparability/design-confounding issue.

### F5. Major: large cross-version output drift is not reported

On the same 52 record identifiers:

- original final routes: 489;
- current final routes for those 52 records: 549;
- 27 records gained routes, 10 were unchanged, and 15 lost routes;
- 21/52 records have a different normalized set of model names;
- original/current totals changed from 111/109 models and 376/468
  configurations.

Largest route-count changes include:

| Record | Old | Current | Delta |
|---|---:|---:|---:|
| `rec_001617` | 4 | 26 | +22 |
| `rec_000090` | 34 | 15 | -19 |
| `rec_000086` | 20 | 38 | +18 |
| `rec_001352` | 14 | 29 | +15 |
| `rec_003517` | 14 | 29 | +15 |
| `rec_003394` | 8 | 21 | +13 |
| `rec_003323` | 21 | 10 | -11 |
| `rec_003434` | 18 | 9 | -9 |

Within-run agreement remains high, but repeated agents agreeing with one another
does not explain why a pipeline version changes the model/configuration inventory
and route counts this much. A cross-version transition ledger is missing.

### F6. Major: grounding validation is syntactic, not evidence-sufficiency validation

The final gate verifies that a quote matches canonical text/native items, points
to candidate provenance, cites Docling items, is not picture-only, and maps to a
valid family/subtype. It does not verify that the quoted span is sufficient to
support every asserted source, transformation, carrier, topology, and lifecycle
field.

Current final routes include:

- 92 routes supported only through dense-candidate references;
- 34 of those 92 with evidence quotes shorter than four words;
- 33 of those 92 carrying explicit uncertainty;
- 7 routes marked `inferred`.

Four ProCyon routes are accepted from quotes consisting only of `GO Function`,
`GtoP`, `Drugbank Transporter`, or `Drugbank Target`; their own uncertainty text
states that source object and topology were inferred from the surrounding list.
These are traceable, but the quote alone does not establish the complete route.

This is the main location where a structurally valid output can stand in for a
carefully established scientific assertion. At minimum, dense-only and inferred
routes need a semantic sufficiency audit using the full cited section.

### F7. Major: current crop validation is a real but weaker pipeline

The current crop run produced unique, nonempty outputs for 109 sufficiency
selectors, 109 specificity selectors, 109 adjudicators, and 98 croppers. One
invalid route reference was rejected and successfully retried. This is genuine
agent execution.

However, the original crop protocol additionally performed input-role integrity
review, scope adjudication, rendered exact-preview inspection, final scope
adjudication, and a final validation of changed panels. The current pipeline
validates figure indexes, route IDs, decision shape, and bounding boxes, then
relies on the same cropper output. Browser QA verifies layout and rendering, not
that each final crop visually demonstrates the claimed input route.

Therefore `98 validated source-figure crops` overstates the current evidence.
Until exact-preview and input-role checks are restored, the accurate phrase is
`98 agent-selected source-figure crops with structural validation`.

### F8. Major: `commands.sh` cannot reproduce the published endpoint

The script uses `set -euo pipefail`, but its initial direct and adjudication
passes contained failures. Successful completion required repair directories,
changed transport timeouts, and resolution selection that are absent from the
script. The file also omits crop selection, retry merge, snapshot freezing,
atlas construction, browser QA, and promotion into `docs/`.

It is an initial execution plan, not an end-to-end reproduction command. The
logs preserve what happened, but an operator cannot regenerate the final
snapshot by running this file alone.

### F9. Moderate: the acceptance gate checks within-run consistency only

The current acceptance gate correctly requires all direct runs, dense coverage,
adjudication, grounding, taxonomy validity, and agreement thresholds. It does
not assert:

- correct canonical and duplicate registry counts;
- the expected study-level sensitivity denominator;
- equivalence or explained change against the preceding release;
- semantic sufficiency of evidence spans;
- post-crop visual correctness;
- replayability of all repair and publication steps.

This explains how the run could report `acceptance_passed=true` despite the
registry and Methods defects.

### F10. Moderate: GitHub is an audit subset, not the complete execution archive

The local full-cohort artifact manifest hashes 7,486 files and about 7.02 GB.
All 72 current taxonomy `llm_calls.jsonl` files are tracked, but only 121 of
2,191 record-level Graph files and none of the regenerated baseline VLM corpus
are tracked in Git. This follows the existing artifact-size policy and is not
silent data loss: the local manifest records paths and hashes.

The limitation must remain explicit. A fresh GitHub clone can inspect prompts,
responses, summaries, final provenance, crop-agent outputs, and hashes, but it
cannot independently replay every document-level Graph/VLM step without the
external canonical archive.

## Evidence that execution was not fabricated

- Current direct traces contain 97, 70, and 94 request/response pairs across
  base runs and repairs; all responses are nonempty and every response hash is
  unique within each direct replicate trace set.
- Discovery contains 119 nonempty responses. Repeated response hashes are only
  small Graph merge payloads such as `{"merges":[]}`.
- Dense mode contains 2,831 matched request/response events. Its repeated
  payloads are expected empty scoped-fill or merge operations, especially
  `{"nodes":[]}`, rather than copied document annotations.
- Adjudication retains 99 requests and 95 completed responses. The four missing
  responses correspond to retained timeout/failure attempts; selected repair
  artifacts resolve all 55 records.
- Adjudication prompts contain complete canonical Markdown and anonymized A/B/C
  replicate results; median prompt length is 235,034 characters and the maximum
  is 429,786.
- The baseline VLM wrapper records 506 successful POST operations, matching the
  506 regenerated baseline images.
- Crop role response files are nonempty and unique by SHA-256; the rejected
  unknown-route response remains visible in the initial summary.

These properties are incompatible with a simple static-output or empty-run
emulation. They do not prove scientific correctness, which is why the semantic
and cross-version gaps above remain important.

## Required corrective work

### Before treating the 55-record snapshot as canonical

1. Fix prior-registry matching so the same `record_id` reuses its study ID
   without becoming a duplicate; add regression tests for same-record reuse,
   true cross-record exact duplicates, and OmniNA sensitivity linkage.
2. Regenerate the registry, special cases, agreement report, and Methods text.
   The LLM runs do not need to be repeated if route/study identifiers remain
   stable after the fix.
3. Replace hard-coded full-corpus Methods prose with values and protocol mode
   derived from run metadata. State explicitly that taxonomy v1 was frozen.
4. Use the completed F5 migration ledger when reporting cross-version change;
   do not compare the old and current route totals as direct prevalence drift.
5. Resolve the completed F6 audit's 46 field-revision rows and four manual
   full-text cases in one declared correction version, then rerun semantic
   sufficiency before promotion.
6. Review and promote the completed F7 audit's proposed crop ledger, then rebuild
   and visually verify the atlas so the nine rejected crops are no longer served.
7. Replace `commands.sh` with an end-to-end release driver or generated replay
   manifest that includes repairs, final selection, crops, snapshot, UI build,
   browser QA, manifest regeneration, and publication.
8. Extend the release gate with registry invariants, cross-version drift
   thresholds/review, semantic evidence sufficiency, and crop-preview approval.

## Release assessment

- **Agent execution authenticity:** pass.
- **All required taxonomy records processed:** pass after logged repairs.
- **Within-run computational agreement:** pass.
- **Verbatim/native-item provenance presence:** pass.
- **Registry correctness:** fail.
- **Methods accuracy:** fail.
- **Cross-version interpretability:** pass through the F5 migration ledger.
- **Evidence semantic sufficiency:** audit complete; canonical correction pending.
- **Crop semantic validation parity:** audit complete; canonical promotion pending.
- **End-to-end one-command reproducibility:** fail.

The present output is a substantial, traceable computation, not a simulated
result. Its main risk is different: structural checks and inherited prose make
the endpoint look more methodologically closed than the retained evidence
actually supports.
