# PRISMA-S audit of the search (2026-10-14)

Scope: the five search rounds that feed the PRISMA flow (8,170 records identified). Every count below is read
from the committed export files by `scripts/build_prisma_search_audit.py`:
- `search_runs_by_database.csv`: one row per round and database, with the window, execution date, interface,
  date and access limits as executed, the API total, records fetched and retained, and the raw retrieval
  before post-retrieval validation;
- `search_strategies_as_executed.md`: the exact query string of every database in every round.

## 1. Records per database and round

| Round | Window | Executed | PubMed | Scopus | OpenAlex | Semantic Scholar | arXiv | bioRxiv/medRxiv (Europe PMC) | Springer Nature | Google Scholar | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 2018-01-01 to 2026-02-28 | 2026-02-15 | 631 | 1021 | not searched | 2192 | 187 | 669 | 272 | 562 | 5,534 |
| April | 2026-03-01 to 2026-04-14 | 2026-04-14 | 46 | 32 | not searched | 201 | 14 | 5 | 33 | 536 | 867 |
| June | 2026-04-15 to 2026-06-10 | 2026-06-10 | 68 | 39 | not searched | 215 | 21 | 33 | 27 | 530 | 933 |
| July | 2026-06-11 to 2026-07-06 | 2026-07-06 | 25 | 12 | not searched | 118 | 6 | 16 | 20 | 0 | 197 |
| August | 2026-07-07 to 2026-08-09 | 2026-08-10 | 27 | 16 | 100 | 183 | 14 | 20 | 27 | 252 | 639 |

The totals reproduce the PRISMA numbers: 5,534 + 867 + 933 + 197 + 639 = 8,170.

## 2. What is documented well

- **Exact queries.** Every export stores the query string as executed. Canonical forms are in
  `protocol/queries/`; round configs are in `scripts/search_config*.json` and the August run folder.
- **Windows and execution dates.** Each round has an explicit window and an execution date. The four
  top-up windows are contiguous: 2026-03-01 to 04-14, 04-15 to 06-10, 06-11 to 07-06, 07-07 to 08-09.
- **August round.** `data/living_catalog_updates/update_2026-08-09/00_search/search_boundary_audit.md`
  checks the counts and pagination of each source, labels the precision of each record's date, and
  documents deduplication.
- **Deduplication and pre-screening removals** are logged per round in
  `protocol/prisma_search_screening_log_2026-07-07.md`: within-round matching on DOI, arXiv ID and exact
  title; matching against the cumulative master; a Crossref audit for hidden duplicates; abstract
  enrichment; and removal of records without a usable abstract (225 in total).

## 3. Problems found

1. **Execution gap from 2026-02-16 to 2026-02-28; the declared windows are contiguous.**
   - *Executions.* The repository records six search executions: v3.0 on 2026-02-06 (`data/exports/`,
     superseded by v3.1 before screening, commit 2c471ff8), the v3.1 baseline on 2026-02-15
     (`data/exports_v31/`), and the four top-ups executed on 2026-04-14, 2026-06-10, 2026-07-06 and
     2026-08-10. No other execution covering February 2026 is recorded in any branch of the repository
     (the August folder also holds superseded diagnostic runs for its own window only).
   - *Windows as declared.* Baseline 2018-01-01 to 2026-02-28, then 2026-03-01 to 04-14, 04-15 to 06-10,
     06-11 to 07-06 and 07-07 to 08-09. The declared windows have no gap.
   - *Windows as executed.* The baseline ran on 2026-02-15, so its last 13 days were in the future at
     execution time, and the first top-up started at 2026-03-01. No date-bounded query (PubMed, Scopus,
     Semantic Scholar, arXiv, Europe PMC, Springer Nature) was executed after 2026-02-15 for records dated
     2026-02-16 to 2026-02-28. Two mechanisms reach the window in later rounds: Google Scholar's
     year-level (2026) queries in April, June and August, and date differences between databases (a record
     that one database dates in the window may be dated March by another).
   - *Coverage probe* (`scripts/probe_search_gap.py`, run 2026-10-14; output
     `gap_probe_2026-02-16_28.json`). The exact v3.1 query strings of the four sources that need no API
     key were re-run with the date range set to 2026-02-16 to 2026-02-28, and every hit was matched (DOI,
     arXiv ID, normalised title) against all records retrieved in the five rounds.

     | Source | Hits in window | Already retrieved |
     |---|---:|---:|
     | PubMed | 9 | 5 |
     | arXiv | 4 | 4 |
     | Europe PMC (bioRxiv/medRxiv) | 11 | 3 |
     | Semantic Scholar | 39 | 11 |

     The 63 hits are 51 unique records. 17 had already been retrieved: 11 through Google Scholar, 3 by the
     baseline itself (indexed by 2026-02-15), and 3 through Scopus in later rounds. 34 had never been
     retrieved. An indicative single-pass title/abstract triage of these 34 against
     `protocol/eligibility_criteria.md` (`gap_probe_indicative_triage.json`; 32 with abstracts; not the
     protocol's screening pipeline) excluded all 34: no substantive text component (EC2/IC2) 19, no
     biological data (EC1/IC1) 10, review articles (EC7) 5.
   - *Not probed.* Scopus and Springer Nature need API keys. OpenAlex was searched only in August, and
     Google Scholar is year-level.
   - *Consequence.* For four of the six date-bounded sources, no eligible record from the window appears to
     be missing. The windows must still be reported as executed. The manuscript currently states
     coverage from 2018-01-01 to 2026-08-09 without the execution dates.
2. **Seven sources, not eight, in rounds 1–4.** OpenAlex was added only in the August round. The abstract
   and the PRISMA box say "eight sources" for all five rounds.
3. **Dates are enforced differently by database.**
   - Exact date filters inside the query: PubMed (`[Date - Publication]`), arXiv (`submittedDate`),
     Europe PMC (`FIRST_PDATE`), Springer Nature (`datefrom`/`dateto`), OpenAlex
     (`from/to_publication_date`).
   - Year-level API filter, then an exact-date post-filter: Scopus (`PUBYEAR`) and Semantic Scholar
     (`year`). Records removed by the post-filter, by round:
     Baseline: Scopus 18, Semantic Scholar 1; April: Scopus 165, Semantic Scholar 226; June: Scopus 292, Semantic Scholar 462; July: Scopus 389, Semantic Scholar 766; August: Scopus 485, Semantic Scholar 914. In August, 291 records with
     a missing or year-only date were kept as recall candidates: 39 Semantic Scholar records without a
     date and the 252 Google Scholar records, which are year-only.
   - Year only: Google Scholar.
4. **Language, open-access and document-type limits were not applied the same way everywhere.**
   - PubMed: English[Language] and "free full text"[sb], which is a proxy, not an open-access filter.
   - Scopus: LANGUAGE(English) and OPENACCESS(1). The DOCTYPE limit in the query file is marked optional
     and was never applied.
   - OpenAlex: language:en and is_oa:true.
   - Semantic Scholar: no language or open-access limit. The openAccessPdf filter stated in
     `protocol/queries/semantic_scholar.txt` was not executed.
   - arXiv, Europe PMC and Google Scholar: no language or access limits. arXiv was limited to its
     categories; Europe PMC to preprints (SRC:PPR).

   English and open access were therefore enforced partly at search and partly at screening and full-text
   retrieval. The Methods must say this.
5. **Springer Nature is filtered after retrieval.** Its free API cannot restrict the search to title and
   abstract, so a broad query was followed by a mechanical three-block title/abstract validation. Raw to
   validated, by round: Baseline 17,130 to 272; April 1,185 to 33; June 1,129 to 27; July 510 to 20; August 691 to 27. The PRISMA flow counts
   the validated records. Both numbers must be reported. If the raw counts are treated as "identified",
   20,266 records would move to "marked ineligible by automation tools".
6. **Google Scholar was incomplete in three of five rounds.**
   - April and June: rate-limited after 5 of 7 queries; queries 6–7 were skipped.
   - July: rate-limited; 0 records.
   - August: a different interface (a provider export through SerpAPI) and a single combined query.
   - Baseline: completion status is unknown, because `data/exports_v31/search_summary_2026-02-15.json`
     was overwritten by a Springer Nature-only rerun. The per-database baseline counts are recoverable from
     the export files.
7. **Stale documentation.**
   - `protocol/search_strategy.md` still describes the v2 scope (multi-modal single-cell models) with
     different concept blocks.
   - The README says "7 databases, 4 rounds".
   - In rounds 2–4, the PubMed and Europe PMC metadata labels repeat the baseline window, although the
     query strings show the correct windows.
   - The arXiv query file asks for post-hoc validation of a stemming problem; no such validation was run.
8. **PRISMA-S items not stated in the manuscript:**
   - per-database interfaces, execution dates, limits and record counts (items 8, 9, 13, 15);
   - that no study registries, citation searching or contact with authors were used, apart from the one
     recall correction (XunZi) (items 3–7);
   - that no published search filters were used (item 10);
   - that there was no peer review of the search strategy, e.g. PRESS (item 14).

## 4. Proposed fixes

- Rewrite Methods §2.3 from this audit. Add Supplementary Table S0 (`search_runs_by_database.csv`) and
  Supplementary Text S1 (`search_strategies_as_executed.md`). Correct the "eight sources in five rounds"
  wording.
- Decide on the February window: either run a gap round for 2026-02-16 to 2026-02-28 across all sources
  and send the new records through deduplication and the protocol's screening (this also covers Scopus and
  Springer Nature, which the probe could not reach), or report the execution dates, the two partial
  mechanisms and the probe result as a limitation.
- Report Springer Nature raw and validated counts, Scopus and Semantic Scholar post-filter removals, and
  Google Scholar completion per round.
- Mark `protocol/search_strategy.md` superseded or regenerate it from the v3.1 queries; correct the README.

## 5. Applied on 2026-10-14

- Author decision on the February window: report it as a limitation (no gap round).
- Manuscript: abstract corrected (seven sources in rounds 1–4, OpenAlex added in round 5); Methods §2.3
  rewritten from this audit (sources and interfaces, rounds and execution dates, dates and limits as
  executed, Springer Nature raw and validated counts, Scopus and Semantic Scholar post-filter removals,
  Google Scholar completeness, PRISMA-S items 3–7, 10 and 14); Limitations gain the execution-gap bullet
  with the probe result; Table S0 and Text S1 added to the supplementary list.
- PRISMA flow (`scripts/build_prisma_flow.py`): the identification box reports records per database,
  read from `search_runs_by_database.csv`, with a balance check that they sum to 8,170.
- Still open: the README status line ("7 databases, 4 rounds") and `protocol/search_strategy.md` (v2
  scope); both are handled in the repository cleanup.
