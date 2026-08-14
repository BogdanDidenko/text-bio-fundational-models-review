# Living Review Update Postmortem

**Evaluated update:** 2026-07-07 through 2026-08-09
**Audit date:** 2026-08-12
**Outcome:** 3 eligible records added; cumulative catalog now contains 55
records, 54 studies, 117 models, 400 task/input configurations, and 519
grounded routes.

## Direct assessment

The update was scientifically recoverable and highly auditable, but it was not
operationally easy. The repository contained the necessary components, yet the
operator repeatedly needed project memory to decide which artifact was
canonical and what command came next. The methodological documentation was
stronger than the runbook: it explained why evidence was valid, but did not
consistently turn each stop into one concrete recovery action.

The main run completed all 18 declared stages, but final publication did not go
through its own `publish` transition. XunZi was recovered later through a valid
supplemental recall path and merged into a 55-record snapshot and UI. The public
atlas was therefore newer than the missing `data/living_catalog/current.json`.
Before reconciliation, `plan` incorrectly proposed searching again from
2026-07-07. This was the highest-risk defect because a successful-looking UI
and a stale control cursor could silently duplicate an entire update interval.

## What actually required intervention

| Boundary | Observed friction | Consequence | Resolution now required |
|---|---|---|---|
| State -> search | Scopus/Springer credentials and Google Scholar provider evidence were initially unavailable; search ran six attempts. | Partial sources could be mistaken for zero-result sources. | Preflight plus a hard search completion gate; `doctor` must be the first command. |
| Search -> dedup | OpenAlex and a single-query Scholar capture were added during the run; exact search provenance had to be reconstructed. | Query versions and denominators could diverge. | Signed query/config artifacts and immutable raw exports remain mandatory. |
| Dedup -> screening | Crossref audit was a distinct hidden-duplicate pass. | A record could appear new despite DOI/title equivalence. | Preserve within-window, cumulative, and Crossref decisions as separate ledgers. |
| Abstracts -> LLM screening | A configurable runner was first used and invalidated because comparability required the hash-pinned legacy runner. | Results from different prompt implementations could have been mixed. | Runner and prompt hashes are frozen and tested. |
| Search validation -> recall | XunZi's abstract used `AI biologist`, which the title/abstract lexical validator did not recognize as biological scope. | A clearly relevant model was absent from the normal 285-record cohort. | Preserve lexical rejects and perform a recall audit; supplemental recovery must remain explicit. |
| Screening -> full text | 12 INCLUDE/UNCERTAIN candidates required five retrieval attempts and PDF/HTML identity checks. | Landing pages, supplements, or abstract pages could masquerade as full text. | Payload signature, main-article identity, HTML body threshold, and manual manifest gates remain blocking. |
| Full text -> Docling | Both PDF and HTML payloads had to produce canonical profiles. | File extension alone was insufficient evidence of a usable article. | Manifest-bound identity and profile completeness checks are mandatory. |
| Docling -> selected sections | Graph evidence had to be converted back to complete heading-bounded sections. Several section artifacts were regenerated after their first inventory. | Root headings, duplicate markdown, empty sections, or nearly whole papers could enter screening. | Hash-bound canonical headings, duplicate removal, coverage rejection, and an explicit override gate. |
| Sections -> final screening | Complete-batch LLM calls failed and were retried in logged splits. | A partial response could look like a completed role output. | Per-batch completeness checks and append-only retry logs. |
| Eligibility -> taxonomy | Two normal records and one supplemental record followed separate physical directories. | The scientific result was correct, but orchestration no longer represented one cohort. | Supplemental recall is now a named reconciliation operation rather than an informal merge. |
| Taxonomy replicates -> acceptance | A one-record XunZi sensitivity run had Jaccard 0.75 even though cumulative 55-record agreement passed all frozen thresholds. | The wrong denominator could block a valid cumulative update or encourage taxonomy changes. | Apply prespecified agreement gates to the declared cumulative cohort and retain record-level sensitivity metrics. |
| Taxonomy -> crops/UI | Snapshot merge, atlas rebuild, collection-batch filter, browser QA, commit, and Pages deployment were separate actions. | Local and remote catalogs could differ despite a completed analysis. | `publish`, Git deployment, `verify-live`, and final `doctor` are distinct mandatory steps. |

## Retry evidence

The run directories record six search attempts, five full-text retrieval
attempts, four abstract-enrichment attempts, three full-text-screening attempts,
three crop-validation attempts, and two attempts for deduplication,
record preparation, candidate creation, eligibility, Docling VLM, and taxonomy
classification. This is evidence that resume semantics worked, but also that
the nominal one-command path was not yet the practical path.

## Documentation verdict

GitHub had sufficient material to reconstruct the science: exact database
queries, PRISMA facts, role prompts, model identifiers, Docling contracts,
taxonomy codebook, provenance ledgers, and UI artifacts were present. It did
not have one current operational page that linked state, gates, publication,
deployment, and remote verification. The root README also still described
title/abstract screening as in progress after the 55-record atlas existed.

`protocol/LIVING_REVIEW_RUNBOOK.md` is now the canonical operational page.
`protocol/living_review_update_pipeline_2026-08-09.md` remains the detailed
methodological contract; neither should duplicate the other.

## Remaining automation priorities

1. Monitor the new automatic Springer 2/3-block recall stratum and report its
   yield separately; this replaces ad hoc expansion by one regex term at a time.
2. Make provider acquisition failures actionable before a run directory is
   created, including credential names and Scholar export readiness.
3. Convert every manual gate note into a generated template plus exact resume
   command in `doctor` output.
4. Keep supplemental records inside a first-class cohort manifest so future
   updates do not need reconciliation.
5. Add CI that runs `doctor`-equivalent consistency checks against committed
   state, snapshot, atlas, PRISMA history, and deployment inputs.

The pipeline is now resumable and its current cursor is repaired, but "no
problems at any stage" should mean that failures become explicit states with a
single recovery path, not that external databases, publishers, or LLM calls
are assumed never to fail.
