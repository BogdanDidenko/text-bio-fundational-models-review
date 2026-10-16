# Rules applied in the journal rewrite of paper 1

The rewrite changed the presentation of the review, not its results: no analysis was re-run, no
inclusion decision or count was changed, and every number of the typed text either occurs in the
previous version or is listed, with its reason, in `number_check_allowed_new.csv`. The files of this
folder record what was done (see `README.md`).

## Sources of the rules

1. The instructions for authors of the target journal (an OUP journal) for review articles: article
   types and lengths, title page, short abstract, keywords, Key Points, author biographies, statements
   (data availability, use of large language models, funding, conflicts of interest, contributions),
   supplementary material and reference style. The manuscript does not name the journal.
2. Five systematic and scoping reviews published in the target journal in 2025–2026, read in full for
   structure and reporting conventions:
   - a scoping review of approaches to evaluating workflow management systems for bioinformatics users;
   - a systematic review of multi-omics time-series analysis in microbiome research;
   - a systematic review of molecular representation learning foundation models;
   - a systematic literature review of deep representation learning for temporal inference in cancer
     omics;
   - a systematic review of computational prediction of RNA modification site–disease associations.
3. Reporting guidelines: PRISMA-ScR (structure of Methods and Results), PRISMA-S (search) and
   PRISMA-trAIce (steps assisted by AI).
4. The rewrite brief: presentation only; Methods once, in PRISMA order; one selection paragraph to open
   the Results; procedural detail in the Supplementary Information; no internal labels in the prose;
   traceability kept outside the prose.

## Rules and how they were applied

| Rule | Source | How it was applied | Where |
|---|---|---|---|
| Article type and length: review article; the guide length is checked, not forced | Instructions for authors; the five reviews | Main-text length measured by the audit script; nothing was cut to reach a length | `COMPLIANCE.md` |
| Short, unstructured abstract; methods in one or two sentences | Instructions; all five reviews have unstructured abstracts | The long structured Markdown abstract was replaced by the short abstract of the typeset draft, now kept in the Markdown master | Abstract |
| Up to six keywords; up to five Key Points, shown at the end | Instructions | Keywords and Key Points kept in the Markdown master and typeset from it | Keywords; Key Points |
| Title page with affiliations and corresponding author; author biographies of about 30 words | Instructions | Title page kept in `main.tex`; biographies are placeholders for the authors | `manuscript/latex/main.tex`; Biographical notes |
| Order Introduction, Methods, Results, Discussion, Conclusions | The scoping review read; PRISMA-ScR | Sections renamed and reordered; section numbers come from the template | Article |
| Methods once, in PRISMA order, in the past tense, with who did what and with which threshold | PRISMA-ScR items 5–14; brief | Methods rewritten as: protocol, registration and reporting; eligibility; information sources and search; selection; data charting and items; critical appraisal; synthesis; use of AI tools | Methods |
| Protocol and registration stated once, with the archive identifier and date | PRISMA-ScR item 5; brief | One paragraph: not registered; first version under version control with its commit date; retrospective deposit (identifier to be added) | Methods: Protocol, registration and reporting |
| Changes from the protocol in one paragraph, with a table | The scoping review read ("Changes from the protocol"); brief | One paragraph with generated counts; every amendment and further change, with its date or stage, whether it was decided after results were seen and what depends on it, in a table | Methods; Supplementary Table S1 |
| Results open with the selection of sources of evidence, then findings by review question | PRISMA-ScR item 14; all five reviews | One selection paragraph with the flow figure; then the included works and four sections that follow the four review questions | Results |
| Use of AI: one Methods paragraph, details by PRISMA-trAIce item in the supplement | PRISMA-trAIce; instructions (statement on large language models); brief | Tools and model versions named once in Methods; tasks, prompts, runs, agreement and human checks in a supplementary note; drafting use to be stated by the authors | Methods: Use of AI tools; Supplementary Note S5; Use of large language models |
| Search strings, per-source counts, stability and calibration figures, per-study tables and earlier analyses in the supplement, cited from the text | Brief; the five reviews keep per-study tables in supplements | Moved to Supplementary Notes S1–S6, Tables S1–S10 and Figure S1 | Supplementary Information |
| Supplementary items numbered by type in the order of first citation | Brief; instructions | Items are cited by key in the sources and numbered by the build; a citation must name the right type | `scripts/build_manuscript.py`; `manuscript/build/supplementary_numbering.csv` |
| Weaknesses reported in the Discussion | The five reviews; PRISMA-ScR item 20 | Limitations subsection with four themes (automation and human checks, search and selection, scope, analysis) | Discussion: Limitations |
| No internal labels in the prose: record identifiers, criterion, axis, archetype and culture codes, section symbols, file paths, run names | Brief | Labels replaced by words; definitions given once; label census before and after | `LABEL_CENSUS.md` |
| Paths and commit hashes only in the data availability statement | Brief | Paths moved to the data availability statement and to the supplementary file index | Data and code availability; `manuscript/supplementary/README.md` |
| Review tools and model names only in Methods and the supplement | Brief | Tool and model names (with versions) appear only in Methods and Supplementary Notes S3 and S5 | Methods; Supplementary Information |
| Included studies cited as references | Brief; instructions (numbered references) | All 55 included records are cited where the inclusion is reported, and each named work at its first mention; supplementary tables give first author, year and reference number | Results; Supplementary Tables S5–S9 |
| Abbreviations defined at first use, none in the title, those used fewer than three times written out | Instructions; brief | Checked over the article; LLM, AI, API and LoRA are defined and used at least three times | Article |
| Tables in words; captions define what remains | Brief | Culture, design, opponent, task and archetype codes written out; each supplementary table has a legend | Tables 1–3; Supplementary Tables |
| Data files in plain language with a column dictionary; coded originals kept | Brief | Reader-facing data files for the supplementary tables and `data_dictionary.csv`, generated from the coded analysis outputs, which stay unchanged | `manuscript/supplementary/data/` |
| Edit sources, not outputs; type no number by hand | Brief | All text is edited in the Markdown sources; tables, counts of deviations, row counts and the build commit are generated; number check against the previous version | `scripts/build_manuscript.py`; `number_check_report.md` |
| Traceability outside the prose | Brief | Previous version archived; move list of every block; label census; number check; file index | This folder; `manuscript/archive/` |
