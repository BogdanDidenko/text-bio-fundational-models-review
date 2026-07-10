# PRISMA 2020 Flow Diagram (to be populated after search execution)

## Identification

Records identified via database searching: ____
  - PubMed: ____
  - Scopus: ____
  - SpringerNature (Meta API): ____
  - SpringerNature (OA API): ____
  - arXiv: ____
  - bioRxiv: ____
  - medRxiv: ____
  - Google Scholar: ____
  - Semantic Scholar: ____

Records identified via other sources (citation chasing, hand search): ____

## Screening

Records after duplicates removed: ____
Records screened (title/abstract): ____
Records excluded at title/abstract: ____
  - EC1 Not single-cell: ____
  - EC2 Single-modality only: ____
  - EC3 No FM component: ____
  - EC4 Non-computational: ____
  - EC5 Non-scholarly: ____
  - EC6 Review article: ____
  - EC8 Not English: ____

## Eligibility

Full-text articles assessed: ____
Full-text articles excluded (with reasons): ____
  - EC2 Single-modality only: ____
  - EC3 No FM component: ____
  - EC9 Not Open Access: ____
  - EC7 Duplicate publication: ____
  - Other: ____

## Inclusion

Studies included in qualitative synthesis: ____
Studies noted in supplementary (single-modality FMs): ____

## Full-Text Evidence Screening Checkpoint (2026-07-10)

This checkpoint supplements the final PRISMA diagram. It distinguishes a
technical failure to construct the prespecified full-text evidence input from a
semantic eligibility exclusion.

| Checkpoint | Count |
|---|---:|
| Full-text records supplied to Docling Graph | 235 |
| Without valid `data_source` + `input_representation` evidence pair | 14 |
| Entering targeted full-text-section screening | 221 |
| Automated EXCLUDE | 165 |
| Automated INCLUDE candidates | 50 |
| Automated UNCERTAIN/manual-review candidates | 6 |
| Routed to adjudication | 67 |
| Manual resolution of automated UNCERTAIN candidates | 6 |
| Current INCLUDE after manual resolution | 52 |
| Current EXCLUDE after manual resolution | 169 |
| Remaining UNCERTAIN after manual resolution | 0 |

The 14 records without a valid evidence pair are not semantic PRISMA
exclusions. They remain in the audit as full-text evidence-preprocessing
limitations. See [full_text_section_screening_2026-07-10.md](full_text_section_screening_2026-07-10.md) for the complete method and logs.

The six automated-uncertain records were then inspected and confirmed by the
review lead using the relevant full Docling sections. This append-only manual
resolution added two INCLUDE and four EXCLUDE decisions without altering the
automated logs. The six-record rationale is in
[`manual_resolution_2026-07-10.md`](../data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10/manual_resolution_2026-07-10.md).
