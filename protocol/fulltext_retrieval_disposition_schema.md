# Full-Text Retrieval Disposition Contract

Each full-text candidate receives exactly one row in
`05_fulltext/fulltext_retrieval_dispositions.json` immediately after download
consolidation. The rows partition the candidate denominator; they are not a
manual exclusion list.

## Dispositions

| Downloader status | Disposition | Terminal evidence | Blocks the pipeline |
|---|---|---:|---:|
| `pdf_downloaded` | `pdf_retrieved` | yes | no |
| `html_full_text_downloaded`, `non_pdf_full_text_downloaded` | `html_full_text_retrieved` | yes | no |
| `skipped_existing` | `preexisting_retrieval_reused` | yes | no |
| `access_restricted` | `not_retrieved_access_restricted` | yes | no |
| `no_full_text_found` | `not_retrieved` | yes | no |
| `retrieval_incomplete` | `technical_retrieval_failure` | no | yes |
| `xml_full_text_downloaded` | `xml_full_text_retrieved_unsupported` | no | yes |

`access_restricted` and `no_full_text_found` are accepted only after the
downloader's complete attempt policy has run. A timeout, provider error, or
transport failure is `retrieval_incomplete` and cannot be converted into a
negative retrieval disposition.

Every row retains attempt counts, access/technical failure counts, retrieved
file hashes, and the attempt-ledger directory. The later report-stage artifact
adds the overlap with Docling input availability; that overlap is not a second
PRISMA branch.

The complete full-text candidate set remains the retrieval denominator. Only
records with a validated supported PDF or full-article HTML enter
`06_docling_screening/retrieved_fulltext_candidates.json` and subsequent section
screening. Terminal `not_retrieved*` rows therefore remain visible without
creating impossible placeholder Docling profiles or blocking eligibility logic.
