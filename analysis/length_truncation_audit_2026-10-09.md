# Length-based truncation and filtering audit (2026-10-09)

Author rule: no document, section, prompt, response or field may be truncated, shortened, skipped or
filtered because of its size, and no length thresholds or length ratios may decide inclusion,
unless the author explicitly authorises the exact limit.

## Operation decomposition (2026-10-07/08 run)

- **Model inputs were complete.** All 563 Codex calls with usage records read at least their whole
  prompt (input tokens cover the prompt length in every call); no compaction, truncation or
  context-length events occur in any event stream. Keyword hits for "truncated"/"context window"
  are paper text quoted by the agents.
- **Fixed cut points in the decomposition code** (none affected the papers the agents read):
  closest-span repair hint searched only the first 200 characters of a quote; validation messages
  showed quotes cut to 120 characters; `meta.json` kept only the last 4,000 characters of stderr;
  the steward queue listed only the 40 most frequent boundary labels; publication-year matching
  compared titles cut to 70 characters; DOM-QA diagnostics showed the first 3 messages. All now
  use the full value. `--limit` (number of records) and `year[:4]` (date parsing) are not size cuts.

## Upstream stages that decided inclusion (not yet remediated)

1. **Abstracts cut to ~1,500 characters in the canonical 2026-07-10 full-text screening.**
   `build_docling_graph_pipeline_input.py` copies abstracts from
   `data/screening_codex_fulltext_2026-07-09/input_records.json`, built by the superseded compact
   context builder with `max_section_chars = 1600` (`trim()` appends `[truncated]`). 73 of the 221
   screened records had cut abstracts: 17 included, 53 excluded (42 as EC2 no text component),
   3 uncertain. Where the full abstract was found in the master records (39), the median loss was
   18% of the abstract (maximum 49%). Selected sections themselves were complete
   (`no_section_truncation: true`).
2. **Length-ratio rules in section selection.** `FULL_DOCUMENT_RATIO = 0.90` rejects a reconstructed
   section that covers at least 90% of the paper's Markdown; `ROOT_CONTAINER_RATIO = 0.80` demotes a
   root heading covering at least 80%. 11 sections were rejected in the 2026-07-10 run. Five of the
   14 reports counted in the PRISMA flow as "no valid targeted section pair" lost a section to these
   rules and were never screened at full text: `full_2026-07-06__rec_000246`, `__rec_002960`,
   `__rec_001447` (GeneChat), `__rec_002400`, `__rec_001487`.
3. **Minimum abstract lengths.** `enrich_abstracts.py` treats abstracts of 10 characters or fewer as
   missing (`MIN_ABSTRACT_LEN = 10`); living-review cohorts use `--minimum-chars 50`. Records below
   these lengths were sent to abstract enrichment and, if still short, removed before screening. In
   the 2026-08-09 update no record was removed this way (shortest screened abstract: 53 characters).
   The baseline set of 225 records without a usable abstract has not yet been re-checked against
   this rule.
4. Superseded or auxiliary runs with `[truncated]` markers (not used for inclusion or charting):
   the 2026-07-09 compact screening, atlas figure-crop subagent prompts (2026-07-11/12) and four
   taxonomy semantic-sufficiency audit prompts (2026-08-17).

## Remediation options (author decision)

- Re-screen the 73 records with complete abstracts and the 5 ratio-dropped reports with complete
  sections, using the frozen prompts. The frozen model `gpt-5.4-mini` is no longer served through
  Codex, so a re-screen needs a model deviation or another provider.
- Remove the ratio rules and length thresholds from the pipeline code for future updates, or keep
  them as explicitly authorised and documented limits.
- Report the issue in the PRISMA flow and limitations either way.
