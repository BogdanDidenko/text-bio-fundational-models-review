# XunZi full-text retrieval audit

The title/abstract pipeline selected XunZi for full-text screening. Automatic
retrieval did not recover the primary report, but the author-supplied download
was located at `~/Downloads/Telegram Desktop/s41551-026-01769-6.pdf`, validated,
and copied into this immutable run as
`manual_files/update_2026-08-09__manual_recall_xunzi/manual_full_text.pdf`.

The primary PDF is 41 pages and 20,183,292 bytes. Its title and DOI match the
candidate, and its SHA-256 is
`d82a7b8ea12c3a0f72de2887f30c7b84161132f8beecdd3384b6ef9b1f2eeb79`.
`manual_fulltexts.json` records the manual source and validation, while
`fulltext_download_manifest.json` is the consolidated canonical retrieval
manifest used by downstream stages.

Two initially successful-looking payloads were rejected during payload audit:

1. `retrieval_invalid_supplement_misclassified_2026-08-11/` contains the
   publisher's 28-page Supplementary Information PDF, not the primary report.
2. `retrieval_invalid_pubmed_abstract_misclassified_2026-08-11/` contains a
   PubMed abstract landing page, not complete article HTML.

These invalid runs are retained as diagnostic evidence. Their emitted manifests
contain the original pre-rename paths and must not be treated as reusable
retrieval results.

The downloader was amended to reject Springer Nature `/esm/`/`MOESM`,
supplementary, reporting-summary, and source-data PDF links as primary reports.
It also rejects Nature paywall pages and PubMed abstract pages as complete HTML.
Targeted regression checks passed. The complete repository test module could not
be imported in either available Python environment because their optional
dependency sets are split (`litellm` missing from the system environment and
`pypdf` missing from `.venv-docling`).

With the validated primary PDF, the downstream pipeline resumed successfully:

- no-VLM Docling profile:
  `../06_docling_screening_manual_recall_xunzi_2026-08-11/`;
- Docling Graph targeted-section extraction:
  `../07_graph_sections_manual_recall_xunzi_2026-08-11/`;
- full-text screening input containing only title, abstract, and complete
  selected sections:
  `../08_section_input_manual_recall_xunzi_2026-08-11/`;
- repeated role-separated full-text screening:
  `../09_fulltext_screening_manual_recall_xunzi_2026-08-11/`;
- eligibility result (`INCLUDE`):
  `../10_eligibility_manual_recall_xunzi_2026-08-11/`;
- VLM-enriched canonical Docling profile:
  `../11_docling_vlm_manual_recall_xunzi_2026-08-11/`.

The supplementary PDF remains diagnostic evidence only and was not used as a
substitute for the primary report.
