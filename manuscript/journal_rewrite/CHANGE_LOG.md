# Change log: from the scoping-review report (v0.5.1) to the journal review (v0.6)

The previous version is archived as `manuscript/archive/review_manuscript_draft_v0.5.1.md` (identical to
the Markdown master at commit 4c4db9f0); its PDF is in the Git history. The results did not change: no
analysis was re-run, and the number check compares every typed number with the previous version
(`number_check_report.md`).

## Structure

- The article now follows Introduction, Methods, Results, Discussion and Conclusions, then the
  statements. Section numbers are no longer typed; the template numbers the sections.
- Methods appear once, in PRISMA order: protocol, registration and reporting; eligibility criteria;
  information sources and search; selection of sources of evidence; data charting and data items;
  critical appraisal; synthesis; use of AI tools. Procedural text that the previous version gave in
  Results (search rounds, decomposition stability, run agreement, the earlier analysis that was
  withdrawn) was moved to Methods or to the Supplementary Information.
- The Results open with one paragraph on the selection of sources of evidence, with the flow figure,
  and then report the included works and one section per review question.
- Limitations are a subsection of the Discussion, grouped as automation and human checks, search and
  selection, scope, and analysis.
- The abstract, keywords and Key Points are kept in the Markdown master; `main.tex` keeps only the
  title page. The long structured abstract of the Markdown draft was replaced by the short abstract that
  the typeset v0.5.1 already used.
- The neutral comparison protocol and the reporting card stay in Box 1.

## Supplementary Information (new)

- `manuscript/supplementary_information.md` is a new source with supplementary notes (search strings
  as executed; search details; decomposition rules, runs and stability; motifs, design axes and
  archetypes; use of AI tools by PRISMA-trAIce item; coverage of protein and nucleotide models),
  supplementary tables (deviations from the protocol; search runs; full-text exclusions; charted
  models; included works; motif library; gene and token budgets; LLM-written text; cross-culture
  comparison units; route codebook) and the full flow figure.
- Items are cited by key (`[[S:key]]`) and numbered by type in the order of first citation. The table
  of deviations is a new curated source (`manuscript/supplementary/deviations_source.csv`): every
  protocol amendment and every further change that the protocol did not foresee, with its date or
  stage, whether it was decided after results were seen, and the results that depend on it.
- Each supplementary table has a reader-facing data file in `manuscript/supplementary/data/`, with
  values in words and identifiers in their own columns, and a column dictionary. The coded originals in
  `analysis/` are unchanged. `manuscript/supplementary/README.md` lists the repository sources of every
  item.
- Supplementary tables give each work as first author and year with its reference number in the
  article.

## Wording

- Internal labels were replaced by words: record identifiers, criterion codes, axis, archetype and
  culture codes, section symbols, run names, file paths and protocol section references. Paths and
  commit hashes appear only in the data availability statement. Review tools and model names, with
  versions, appear only in Methods and the Supplementary Information. Counts are in `LABEL_CENSUS.md`.
- Model names are set in roman, not in code font. Docling and Docling Graph versions and the commit
  date of the first protocol version were added (see the allowed new numbers in
  `number_check_allowed_new.csv`).
- The counts of protocol amendments, further changes and changes made after results were seen are
  generated from the deviations table.
- Plain-language edits: the record recovered after the correction of the automated keyword check
  (formerly "pre-screen lexical validator"); "agent papers" written as papers decomposed by the LLM
  agent; OpenAlex limits described in words.

## References

- PRISMA-trAIce (Holst et al., JMIR AI 2025) was added.
- The citation of all 55 included records at the inclusion sentence of the Results is checked by the
  converter; it had been lost when the sentence was reworded and is restored. Every entry of the
  bibliography is cited.

## Build and checks (new or changed scripts)

- `scripts/build_manuscript.py` builds everything: it numbers the supplementary items, generates the
  tables, data files and file index, resolves the Markdown master, typesets the article (via
  `scripts/build_manuscript_latex.py`, pdfLaTeX and BibTeX) and then the supplement (pandoc and
  XeLaTeX), with study labels and reference numbers read from the article's bibliography.
- `scripts/build_manuscript_latex.py` now reads the resolved master, writes the front matter, Key Points,
  back matter and biographies as well as the body, strips the markers of generated values, keeps short
  identifiers unbroken and fails if the inclusion citation is missing.
- `scripts/manuscript_label_census.py`, `scripts/manuscript_number_check.py`,
  `scripts/manuscript_move_list.py` and `scripts/manuscript_rewrite_audit.py` are the checks of this
  rewrite; the audit script writes the reports of this folder and fails on a census violation or an
  unexplained new number.

## Version 0.6.1: added supplementary items and one correction

These changes came after the rewrite and are not presentation changes.

- Correction. Versions 0.5.1 and 0.6 stated that the review lead resolved the full-text records left
  uncertain by automated screening. This holds for rounds 1–4. In the August round, the one uncertain
  record (scMIR, included) was resolved by an LLM agent reading the full document, and no person
  validated that decision (`data/living_catalog_updates/update_2026-08-09/10_eligibility/manual_resolution.csv`).
  Methods (selection of sources of evidence; use of AI tools), the summary of deviations, Limitations
  and the supplementary note on AI use now say so, and the deviations table has a new further change.
- New supplementary note: the prompts of the screening roles, reproduced verbatim from the run logs
  (the fixed part before the records of each batch), grouped by identical text, with the runs that used
  each text, the number of batches and the SHA-256 of the text.
- New supplementary tables: the decisions for every record at title and abstract screening (data file
  only) and at full-text screening (printed and data file, with the resolutions and who made them), and
  data-file tables with the decomposition decision for every step, the parameter-pass decision for every
  slot, and the items of each targeted charting run. The build checks the screening tables against the
  counts of the flow diagram.
- The supplementary items are renumbered by first citation, so the supplementary numbers of version 0.6
  no longer apply. Data and code availability now states that the run logs, which embed the paper texts,
  are not part of the Zenodo snapshot.
- The label census and number check were rerun on this version; `COMPLIANCE.md` gives the new lengths.

## Open items (not done in this rewrite)

- Literature placeholders ([CITE]) in the Introduction, the selection paragraph of Methods (companion
  methods paper) and Relation to existing reviews.
- Zenodo deposits: identifier and date of the protocol record, and the DOI of the repository snapshot,
  for Methods and Data and code availability.
- Figure 2: the compact flow (panel a) and the works-per-culture breakdown are still to be drawn; the
  legend marks them as to do.
- A second human coder for the cross-culture comparison units and the culture assignment, with a recall
  audit of comparisons (stated as planned in Methods and Limitations).
- Decision on the withdrawn OKR-Cell preprint, which is still counted among the 55 records.
- Confirmation by the review lead of the August full-text inclusion that an LLM agent resolved (scMIR).
- Author statements: use of language models in drafting, funding, conflicts of interest, contributions,
  acknowledgements, biographies, co-authors and affiliations on the title page.
- At submission: the journal's own template options and cover letter; the supplement may need to be
  delivered as a single PDF plus the data files.
