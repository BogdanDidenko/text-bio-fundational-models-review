# Full-Text Screening Section Input Statistics

This file summarizes the exact Docling-derived sections used to build the full-text agent screening input.

## Inputs

- Screening input JSON: `data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_screening_input.json`
- Section audit CSV: `data/fulltext_screening_context_2026-07-09_compact_v2/fulltext_section_audit.csv`
- Screening run: `data/screening_codex_fulltext_2026-07-09`

## Record Counts

- Total records: **235**
- `include` records: **148**
- `uncertain` records: **87**

## Context Status

- `ok`: **225**
- `fallback_document_opening`: **10**

## Selected Section Count Per Record

- `1` selected sections: **18** records
- `2` selected sections: **13** records
- `3` selected sections: **20** records
- `4` selected sections: **31** records
- `5` selected sections: **36** records
- `6` selected sections: **47** records
- `7` selected sections: **53** records
- `8` selected sections: **17** records

## Section Type Counts

| Section type | Section instances | Records with type |
|---|---:|---:|
| `data_representation` | 603 | 210 |
| `discussion_conclusion` | 233 | 196 |
| `introduction` | 177 | 177 |
| `abstract` | 174 | 174 |
| `document_opening` | 10 | 10 |

## Top Exact Section Headings Used

| Section type | Heading | Occurrences | Records | Include | Uncertain |
|---|---|---:|---:|---:|---:|
| `introduction` | Introduction | 140 | 140 | 90 | 50 |
| `abstract` | Abstract | 139 | 139 | 90 | 49 |
| `discussion_conclusion` | Discussion | 132 | 129 | 87 | 45 |
| `data_representation` | Methods | 60 | 60 | 45 | 15 |
| `discussion_conclusion` | Conclusion | 53 | 53 | 30 | 23 |
| `abstract` | ABSTRACT | 34 | 34 | 23 | 11 |
| `introduction` | INTRODUCTION | 31 | 31 | 17 | 14 |
| `data_representation` | Datasets | 28 | 24 | 23 | 5 |
| `discussion_conclusion` | DISCUSSION | 16 | 16 | 9 | 7 |
| `discussion_conclusion` | Conclusions | 15 | 15 | 9 | 6 |
| `data_representation` | Model Architecture | 13 | 13 | 8 | 5 |
| `document_opening` | Docling opening text | 10 | 10 | 2 | 8 |
| `discussion_conclusion` | CONCLUSION | 10 | 10 | 5 | 5 |
| `data_representation` | Model architecture | 8 | 7 | 5 | 3 |
| `data_representation` | Architecture | 8 | 5 | 6 | 2 |
| `data_representation` | Materials and methods | 7 | 7 | 4 | 3 |
| `introduction` | Background | 6 | 6 | 2 | 4 |
| `data_representation` | Method | 6 | 6 | 4 | 2 |
| `data_representation` | METHODS | 6 | 6 | 2 | 4 |
| `data_representation` | Dataset | 6 | 6 | 5 | 1 |
| `data_representation` | Training Data | 5 | 5 | 3 | 2 |
| `data_representation` | Materials and Methods | 5 | 5 | 2 | 3 |
| `data_representation` | Online Methods | 4 | 4 | 3 | 1 |
| `data_representation` | Training data | 4 | 4 | 3 | 1 |
| `data_representation` | Influence of pre-training data size | 4 | 4 | 4 | 0 |
| `data_representation` | DATASETS | 4 | 4 | 3 | 1 |
| `discussion_conclusion` | Discussion and Conclusion | 4 | 4 | 2 | 2 |
| `data_representation` | Dataset Construction | 3 | 3 | 2 | 1 |
| `data_representation` | MODEL ARCHITECTURE | 3 | 3 | 3 | 0 |
| `data_representation` | Data collection and preprocessing | 3 | 3 | 0 | 3 |
| `data_representation` | Results under Noisy Mulit-modal Training Data | 3 | 3 | 0 | 3 |
| `data_representation` | Training Data Curation | 3 | 3 | 0 | 3 |
| `data_representation` | LLM-enriched Textual Corpus Curation | 3 | 3 | 0 | 3 |
| `data_representation` | Comparison Methods and Datasets | 3 | 3 | 0 | 3 |
| `data_representation` | Input representation | 2 | 2 | 1 | 1 |
| `data_representation` | Data Collection | 2 | 2 | 2 | 0 |
| `data_representation` | Analysis of species tag-prompting methods | 2 | 2 | 2 | 0 |
| `data_representation` | Downstream task datasets | 2 | 2 | 2 | 0 |
| `data_representation` | Pretraining data collection and preprocessing | 2 | 2 | 1 | 1 |
| `data_representation` | Datasets and Tasks | 2 | 2 | 2 | 0 |

## What Each Agent Role Received

All roles used the same full-text evidence fields. The adjudicator additionally received the first-pass reviewer outputs and Python gate result.

| Role | Prompt files | Prompts with `full_text_context` | Prompts with `section_evidence` | Prompts with `first_pass_outputs` |
|---|---:|---:|---:|---:|
| `scope_reviewer` | 235 | 235 | 235 | 0 |
| `architecture_reviewer` | 235 | 235 | 235 | 0 |
| `adjudicator` | 84 | 84 | 84 | 84 |

Agent prompts did not include raw PDFs. The evidence supplied for analysis was the selected text in `full_text_context` and the structured list in `section_evidence`, plus title/abstract metadata. `docling_markdown` was included as a traceability path, not as separately loaded context.

## Output Tables

- `section_input_by_record.csv`: one row per screened record, with the exact headings selected for that record.
- `section_instances.csv`: one row per selected section instance.
- `section_heading_counts.csv`: aggregate counts by exact heading and section type.
- `section_type_counts.csv`: aggregate counts by section type.
- `summary.json`: machine-readable version of this summary.
