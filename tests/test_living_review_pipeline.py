from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/docling"))

from build_living_review_cohorts import (
    accepted_records,
    abstract_input,
    apply_section_overrides,
    best_document,
    consolidate_downloads,
    classify_pdf_text_role,
    fulltext_candidates,
    normalized_download_status,
)
from build_input_representation_atlas import collection_metadata
from build_search_update_config import build_config
from build_docling_graph_pipeline_input import (
    choose_sections_for_input,
    screening_only_record,
    validate_graph_summary_set,
)
from prepare_incremental_records import (
    MasterIndex,
    apply_cross_dedup_resolutions,
    assign_ids,
    crossref_acceptance,
    main as prepare_incremental_main,
)
from run_codex_screening_pipeline import (
    archive_failed_batch_attempt,
    build_role_prompt,
    codex_batch_with_retries,
    safe_record,
)
from run_living_review_pipeline import (
    ManualGate,
    Pipeline,
    atlas_tree_manifest,
    date_precision_rollup,
    rel,
    retrieved_candidate_subset,
    retrieval_disposition_table,
)
from merge_supplemental_recall_records import merge_records, validate_declaration
from prepare_full_cohort_taxonomy_rerun import rerun_commands
from run_incremental_atlas_crop_pipeline import (
    contact_sheet_font,
    load_figures_by_record,
    validate_selection,
)
from run_atlas_exact_preview_validation import terminalize_unresolved_dispositions
from enrich_abstracts import fetch_abstract_openalex_doi, main as enrich_abstracts_main
from metadata_match import accept_title_candidate
from download_full_texts import (
    access_restriction_attempts,
    fulltext_links_from_html,
    is_supplementary_url,
    looks_like_full_text_html,
    looks_like_pdf,
    record_title_candidate_attempt,
    reusable_existing_result,
    source_urls,
    technical_attempt_failures,
)
from merge_living_catalog_snapshot import corpus_inventory, validate_grounded_evidence
from docling_graph_grounding import derive_full_section
from build_canonical_vlm_profile_manifest import document_identity
from analyze_input_taxonomy_runs import corpus_description, load_fixed_run
from build_input_taxonomy_registry import assemble_registry
from archive_living_review_artifacts import create_archive, restore_archive, verify_archive
from verify_living_review_method_lock import verify_method_lock
from classify_fixed_input_taxonomy_candidates import prompt_for_record
from profile_artifact_contract import validate_profile_artifacts
from validate_canonical_profile_manifest import (
    rebase_row as rebase_canonical_profile_row,
    validate_row as validate_canonical_profile_row,
)
from reproduce_search import (
    classify_interval_date,
    search_springernature,
    filter_interval_records,
    main as reproduce_search_main,
    retry_request,
    search_openalex,
    search_scopus,
    search_semantic_scholar,
    SemanticScholarRateLimitError,
    load_google_scholar_provider_export,
    query_signature,
)
from deduplicate import DeduplicationEngine, validate_search_contract
from capture_google_scholar_serpapi import normalize_result, scrub_secret


class SearchConfigTests(unittest.TestCase):
    def test_expensive_stage_output_is_preserved_before_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pipeline = Pipeline.__new__(Pipeline)
            pipeline.run_root = root
            graph = root / "07_graph_sections"
            payload = graph / "shard_00" / "record" / "document.dclg"
            payload.parent.mkdir(parents=True)
            payload.write_text("expensive graph", encoding="utf-8")

            preserved = pipeline.preserve_expensive_generated_path(
                "graph-sections", graph
            )

            self.assertFalse(graph.exists())
            self.assertIsNotNone(preserved)
            self.assertEqual(
                (preserved / "shard_00/record/document.dclg").read_text(
                    encoding="utf-8"
                ),
                "expensive graph",
            )
            ledger = root / "preserved_stage_outputs/preservation_ledger.jsonl"
            rows = [json.loads(line) for line in ledger.read_text().splitlines()]
            self.assertEqual(rows[0]["stage"], "graph-sections")
            self.assertEqual(rows[0]["file_count"], 1)

    def test_springer_two_block_near_miss_enters_explicit_recall_stratum(self) -> None:
        config = {
            "databases": {
                "springernature": {
                    "query": "query",
                    "date_filter": "datefrom:2026-08-10 dateto:2026-08-12",
                    "minimum_validation_blocks": 2,
                    "validation_patterns": {
                        "block_a": "biology",
                        "block_b": "language model",
                        "block_c": "generative",
                    },
                }
            }
        }
        records = [
            {"doi": "10.1/a", "title": "Biology language model", "abstract": "generative"},
            {"doi": "10.1/b", "title": "Language model", "abstract": "generative"},
            {"doi": "10.1/c", "title": "Biology only", "abstract": ""},
        ]
        with patch("reproduce_search._sn_paginated_search", return_value=(records, {"complete": True})):
            result, _ = search_springernature(config, {"springernature_Meta_API": "key"})
        self.assertEqual(result["validation_stratum_counts"]["primary_3_of_3"], 1)
        self.assertEqual(result["validation_stratum_counts"]["recall_2_of_3"], 1)
        self.assertEqual(result["validation_stratum_counts"]["rejected_0_or_1_of_3"], 1)
        self.assertEqual(result["records"][1]["search_validation_stratum"], "recall_2_of_3")

    def test_atlas_review_iteration_is_derived_from_canonical_record_id(self) -> None:
        self.assertEqual(
            collection_metadata("update_2026-08-09__manual_recall_xunzi"),
            {"batch_id": "update_2026-08-09", "date": "2026-08-09"},
        )
        with self.assertRaises(ValueError):
            collection_metadata("record_without_collection_date")

    def test_contact_sheet_font_resolves_to_a_real_file(self) -> None:
        self.assertTrue(contact_sheet_font().is_file())

    def test_taxonomy_v3_clarifies_visual_and_dense_interface_boundaries(self) -> None:
        prompt = prompt_for_record(
            {"candidate_id": "rec_1", "title": "Example", "doi": ""},
            "Complete paper",
            [],
            {"families": []},
            {"type": "object"},
            "v3-interface-boundary",
        )
        self.assertIn("image fed to image encoder -> Q-Former\" (visual)", prompt)
        self.assertIn("dedicated modality encoder -> embedding aligned to an LLM", prompt)
        self.assertIn("not make the route text-native", prompt)

    def test_downloader_uses_canonical_record_url(self) -> None:
        session = Mock()
        session.get.return_value.status_code = 404
        session.get.return_value.ok = False
        session.get.return_value.content = b""
        session.get.return_value.headers = {}
        session.get.return_value.url = "https://example.org/direct.pdf"
        urls = source_urls({"title": "", "url": "https://example.org/direct.pdf"}, session, "reviewer@example.org", [])
        self.assertEqual(urls, [("record_url", "https://example.org/direct.pdf")])

    def test_landing_parser_recovers_signed_pdf_without_pdf_suffix(self) -> None:
        payload = (
            b'<a class="wt-download-pdf" title="Download PDF" href="https://media.example/file?_s=token">Download</a>'
            b'<embed type="application/pdf" src="https://media.example/file?_s=token#view=FitV">'
        )
        self.assertEqual(
            fulltext_links_from_html(payload, "https://example.org/landing"),
            [("landing_pdf_link", "https://media.example/file?_s=token")],
        )

    def test_landing_parser_rejects_supplementary_nature_pdf(self) -> None:
        payload = (
            b'<a title="Download PDF" '
            b'href="https://media.springernature.com/original/springer-static/esm/'
            b'art%3A10.1038%2Fexample/MediaObjects/example_MOESM1_ESM.pdf">Supplement</a>'
            b'<a title="Download PDF" href="/content/pdf/10.1038/example.pdf">Article PDF</a>'
        )
        self.assertTrue(
            is_supplementary_url(
                "https://media.springernature.com/original/springer-static/esm/"
                "art%3A10.1038%2Fexample/MediaObjects/example_MOESM1_ESM.pdf"
            )
        )
        self.assertEqual(
            fulltext_links_from_html(payload, "https://www.nature.com/articles/example"),
            [("landing_pdf_link", "https://www.nature.com/content/pdf/10.1038/example.pdf")],
        )

    def test_paywalled_landing_page_is_not_full_text_html(self) -> None:
        payload = (
            b'<html><body><h2 id="access-options">Access options</h2>'
            b'<a data-test="buy-or-subscribe">Buy or subscribe</a>'
            + b'<p>metadata and references</p>' * 500
            + b'</body></html>'
        )
        self.assertFalse(looks_like_full_text_html(payload))

    def test_pubmed_abstract_page_is_not_full_text_html(self) -> None:
        payload = (
            b'<html><head><meta name="ncbi_app" content="pubmed">'
            b'<meta name="citation_abstract_html_url" content="https://pubmed.ncbi.nlm.nih.gov/1/">'
            b'</head><body><div class="abstract-content">Abstract</div>'
            + b'<p>metadata, navigation and references</p>' * 500
            + b'</body></html>'
        )
        self.assertFalse(looks_like_full_text_html(payload))

    def test_downloader_reuses_hash_valid_existing_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b"%PDF-1.4\n" + b"x" * 6000
            pdf = root / "paper.pdf"
            pdf.write_bytes(payload)
            (root / "download_result.json").write_text(
                json.dumps(
                    {
                        "candidate_id": "candidate_1",
                        "status": "pdf_downloaded",
                        "files": [
                            {
                                "file": str(pdf),
                                "filename": "paper.pdf",
                                "content_type": "application/pdf",
                                "bytes": len(payload),
                                "sha256": hashlib.sha256(payload).hexdigest(),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = reusable_existing_result(root, "candidate_1")
            self.assertIsNotNone(result)
            self.assertTrue(result["reused_existing"])
            self.assertEqual(result["status"], "pdf_downloaded")

    def test_openalex_doi_abstract_is_reconstructed(self) -> None:
        response = Mock()
        response.json.return_value = {
            "abstract_inverted_index": {"Biological": [0], "abstract": [1]}
        }
        with patch("enrich_abstracts.retry_get", return_value=response) as get:
            abstract = fetch_abstract_openalex_doi("10.1000/example", "key")
        self.assertEqual(abstract, "Biological abstract")
        self.assertEqual(get.call_args.kwargs["params"], {"api_key": "key"})

    def test_serpapi_secret_is_scrubbed_from_raw_response(self) -> None:
        secret = "private-key"
        payload = {
            "api_key": secret,
            "search_metadata": {
                "json_endpoint": f"https://example.test/?api_key={secret}"
            },
        }
        scrubbed = scrub_secret(payload, secret)
        self.assertEqual(scrubbed["api_key"], "[REDACTED]")
        self.assertNotIn(secret, json.dumps(scrubbed))

    def test_serpapi_scholar_result_is_normalized_with_provenance(self) -> None:
        record = normalize_result(
            {
                "title": "A model",
                "link": "https://example.test/paper",
                "result_id": "abc",
                "snippet": "An abstract-like snippet.",
                "publication_info": {
                    "summary": "A Lovelace, B Turing - Journal, 2026",
                    "authors": [{"name": "A Lovelace"}, {"name": "B Turing"}],
                },
            },
            "gs_q1",
            "raw/gs_q1/page_000.json",
            "digest",
        )
        self.assertEqual(record["year"], "2026")
        self.assertEqual(record["authors"], ["A Lovelace", "B Turing"])
        self.assertEqual(record["query_ids"], ["gs_q1"])
        self.assertEqual(record["raw_response_sha256"], "digest")

    def test_openalex_missing_key_is_explicitly_incomplete(self) -> None:
        result, raw = search_openalex(
            {
                "databases": {
                    "openalex": {
                        "queries": {"main": "biology AND language"},
                        "date_from": "2026-07-07",
                        "date_to": "2026-08-09",
                    }
                }
            },
            {},
        )
        self.assertFalse(result["execution"]["complete"])
        self.assertEqual(result["execution"]["reason"], "OpenAlex API key missing")
        self.assertEqual(raw["records"], [])

    def test_openalex_unions_queries_and_preserves_membership(self) -> None:
        work = {
            "id": "https://openalex.org/W1",
            "doi": "https://doi.org/10.1000/example",
            "ids": {"pmid": "https://pubmed.ncbi.nlm.nih.gov/123/"},
            "display_name": "A model",
            "abstract_inverted_index": {"Biology": [0], "model": [1]},
            "authorships": [{"author": {"display_name": "A. Author"}}],
            "publication_year": 2026,
            "publication_date": "2026-07-20",
            "open_access": {"is_oa": True},
            "primary_location": {
                "landing_page_url": "https://example.org/work",
                "source": {"display_name": "Journal"},
            },
        }
        payload = {"meta": {"count": 1, "next_cursor": None}, "results": [work]}
        config = {
            "databases": {
                "openalex": {
                    "queries": {"main": "biology", "models": "ModelName"},
                    "date_from": "2026-07-07",
                    "date_to": "2026-08-09",
                }
            }
        }
        with patch("reproduce_search._openalex_request", side_effect=[payload, payload]):
            result, raw = search_openalex(config, {"openalex": "secret"})

        self.assertTrue(result["execution"]["complete"])
        self.assertEqual(result["records_fetched"], 1)
        self.assertEqual(result["records"][0]["abstract"], "Biology model")
        self.assertEqual(result["records"][0]["doi"], "10.1000/example")
        self.assertEqual(result["records"][0]["pmid"], "123")
        self.assertEqual(result["records"][0]["query_ids"], ["main", "models"])
        self.assertEqual(len(raw["records"]), 1)

    def test_missing_scopus_key_is_an_explicit_incomplete_source(self) -> None:
        result = search_scopus(
            {"databases": {"scopus": {"query": "TITLE-ABS(test)"}}},
            {},
        )
        self.assertEqual(result["records"], [])
        self.assertFalse(result["execution"]["complete"])
        self.assertEqual(result["execution"]["reason"], "Scopus API key missing")

    def test_scopus_key_is_sent_only_in_header(self) -> None:
        response = Mock()
        response.json.return_value = {
            "search-results": {
                "opensearch:totalResults": "0",
                "entry": [],
            }
        }
        with patch("reproduce_search.retry_request", return_value=response) as request:
            search_scopus(
                {"databases": {"scopus": {"query": "TITLE-ABS(test)"}}},
                {"scopus": "secret-key"},
            )

        _, kwargs = request.call_args
        self.assertNotIn("apiKey", kwargs["params"])
        self.assertEqual(kwargs["headers"]["X-ELS-APIKey"], "secret-key")

    def test_update_snapshot_requires_hashable_native_profile_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifests/canonical_docling_profile_manifest.csv"
            manifest.parent.mkdir()
            artifacts = {
                "docling_json": root / "documents/paper.docling.json",
                "markdown": root / "markdown/paper.md",
                "figures_manifest": root / "figures/paper/figures_manifest.json",
                "source_document": root / "source/paper.pdf",
            }
            for path in artifacts.values():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("artifact", encoding="utf-8")
            manifest.write_text(
                "candidate_id,profile_status,docling_json,markdown,figures_manifest,source_document\n"
                + "r1,complete,"
                + ",".join(str(path) for path in artifacts.values())
                + "\n",
                encoding="utf-8",
            )
            inventory = corpus_inventory(root, require_complete_profile_artifacts=True)
            self.assertEqual(inventory["status"], "complete")
            self.assertEqual(len(inventory["profile_artifacts"]), 4)
            artifacts["markdown"].unlink()
            with self.assertRaisesRegex(RuntimeError, "inventory is incomplete"):
                corpus_inventory(root, require_complete_profile_artifacts=True)

    def test_update_snapshot_resolves_migrated_relative_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            corpus = workspace / "corpus"
            manifest = corpus / "manifests/canonical_docling_profile_manifest.csv"
            manifest.parent.mkdir(parents=True)
            relative_paths = {
                "docling_json": Path("data/profiles/documents/paper.docling.json"),
                "markdown": Path("data/profiles/markdown/paper.md"),
                "figures_manifest": Path("data/profiles/figures/paper/figures_manifest.json"),
                "source_document": Path("data/source/paper.pdf"),
            }
            for relative in relative_paths.values():
                path = workspace / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("artifact", encoding="utf-8")
            manifest.write_text(
                "candidate_id,profile_status,docling_json,markdown,figures_manifest,source_document\n"
                + "r1,complete,"
                + ",".join(str(path) for path in relative_paths.values())
                + "\n",
                encoding="utf-8",
            )

            inventory = corpus_inventory(
                corpus,
                require_complete_profile_artifacts=True,
                artifact_roots=[workspace],
            )

            self.assertEqual(inventory["status"], "complete")
            self.assertEqual(len(inventory["profile_artifacts"]), 4)

    def test_prisma_date_and_retrieval_counts_are_explicit_partitions(self) -> None:
        date_audit = date_precision_rollup(
            {
                "total_before_dedup": 3,
                "date_status_by_database": {
                    "pubmed": {
                        "retained_status_counts": {"in_range": 2},
                        "excluded_out_of_range": 4,
                    },
                    "arxiv": {
                        "retained_status_counts": {"unknown_year_only": 1},
                        "excluded_out_of_range": 0,
                    },
                },
            }
        )
        self.assertEqual(date_audit["confirmed_by_source_date_filter"], 2)
        self.assertEqual(date_audit["uncertain_date_recall_candidates"], 1)
        self.assertEqual(date_audit["excluded_confirmed_out_of_range_before_export"], 4)

        retrieval = retrieval_disposition_table(
            [{"candidate_id": "r1"}, {"candidate_id": "r2"}, {"candidate_id": "r3"}],
            {
                "results": [
                    {"candidate_id": "r1", "status": "pdf_downloaded"},
                    {"candidate_id": "r2", "status": "non_pdf_full_text_downloaded"},
                    {"candidate_id": "r3", "status": "no_full_text_found"},
                ]
            },
            [{"candidate_id": "r3"}],
        )
        self.assertEqual(
            retrieval["disposition_counts"],
            {"pdf_retrieved": 1, "html_full_text_retrieved": 1, "not_retrieved": 1},
        )
        self.assertTrue(all(row["terminal_retrieval_evidence"] for row in retrieval["rows"]))
        self.assertFalse(any(row["manual_gate_required"] for row in retrieval["rows"]))
        self.assertEqual(retrieval["docling_missing_by_retrieval_disposition"], {"not_retrieved": 1})

    def test_only_candidates_with_supported_payloads_enter_docling_screening(self) -> None:
        candidates = [
            {"candidate_id": "a", "title": "Retrieved"},
            {"candidate_id": "b", "title": "Not retrieved"},
        ]
        subset = retrieved_candidate_subset(
            candidates,
            [{"candidate_id": "a", "path": "paper.pdf", "kind": "pdf"}],
        )
        self.assertEqual(subset, [candidates[0]])
        with self.assertRaises(RuntimeError):
            retrieved_candidate_subset(candidates, [{"candidate_id": "unknown"}])

    def test_snapshot_requires_one_verified_evidence_row_per_route(self) -> None:
        route = {"route_id": "route_1", "record_id": "r1", "final_grounding_valid": True}
        evidence = {
            "route_id": "route_1",
            "record_id": "r1",
            "final_grounding_valid": True,
            "quote": "verified evidence",
            "pages": [1],
            "doc_item_refs": [],
            "quote_verified_in_canonical_markdown": True,
            "quote_verified_in_native_items": None,
        }
        validate_grounded_evidence([route], [evidence])
        with self.assertRaisesRegex(RuntimeError, "mismatch"):
            validate_grounded_evidence([route], [])
        evidence["quote_verified_in_canonical_markdown"] = False
        with self.assertRaisesRegex(RuntimeError, "not verified"):
            validate_grounded_evidence([route], [evidence])

    def test_root_container_section_is_not_a_targeted_screening_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "paper.md"
            markdown.write_text(
                "# Title\n" + ("x" * 880) + "\n## Methods\n" + ("y" * 80)
                + "\n## Results\n" + ("z" * 80) + "\n",
                encoding="utf-8",
            )
            root = {
                "section_type": "data_source",
                "heading_path": ["Title"],
                "derived_full_section": {"status": "ok", "text": "x" * 880, "heading_path": ["Title"]},
            }
            summary = {
                "source_markdown": str(markdown),
                "section_grounding": {
                    "data_source_chunks": [root],
                    "input_representation_chunks": [{**root, "section_type": "input_representation"}],
                },
            }
            selected, audit = choose_sections_for_input(summary)
            self.assertEqual(selected, [])
            self.assertEqual(set(audit["missing_targets"]), {"data_source", "input_representation"})

    def test_graph_section_builder_prefers_one_section_grounded_for_both_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "paper.md"
            markdown.write_text("# Paper\n## Methods\nEvidence.\n## Results\nOther.\n", encoding="utf-8")

            def section(section_type: str, heading: str, start: int, text: str) -> dict[str, object]:
                return {
                    "section_type": section_type,
                    "heading_path": ["Paper", heading],
                    "derived_full_section": {
                        "status": "ok",
                        "text": text,
                        "heading_path": ["Paper", heading],
                        "line_start": start,
                        "line_end": start + 1,
                        "source_markdown": str(markdown),
                        "contains_evidence_quote": True,
                    },
                }

            shared_data = section("data_source", "Methods", 2, "shared evidence")
            shared_input = section("input_representation", "Methods", 2, "shared evidence")
            separate = section("data_source", "Results", 4, "separate evidence")
            summary = {
                "source_markdown": str(markdown),
                "section_grounding": {
                    "data_source_chunks": [separate, shared_data],
                    "input_representation_chunks": [shared_input],
                },
            }
            selected, audit = choose_sections_for_input(summary)
            self.assertEqual(audit["missing_targets"], [])
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0]["heading_path"], ["Paper", "Methods"])
            self.assertEqual(
                set(selected[0]["target_section_types"]),
                {"data_source", "input_representation"},
            )

    def test_graph_section_builder_rejects_reference_container(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "paper.md"
            markdown.write_text("# Paper\n## Results\nEvidence.\n## References\nCitation.\n", encoding="utf-8")

            def section(section_type: str, heading: str, start: int, text: str) -> dict[str, object]:
                return {
                    "section_type": section_type,
                    "heading_path": ["Paper", heading],
                    "derived_full_section": {
                        "status": "ok",
                        "text": text,
                        "heading_path": ["Paper", heading],
                        "line_start": start,
                        "line_end": start + 1,
                        "source_markdown": str(markdown),
                        "contains_evidence_quote": True,
                    },
                }

            summary = {
                "source_markdown": str(markdown),
                "section_grounding": {
                    "data_source_chunks": [section("data_source", "Results", 2, "valid")],
                    "input_representation_chunks": [
                        section("input_representation", "References", 4, "repeated quote"),
                        section("input_representation", "Results", 2, "valid"),
                    ],
                },
            }
            selected, _audit = choose_sections_for_input(summary)
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0]["heading_path"], ["Paper", "Results"])

    def test_graph_section_builder_rejects_stale_or_unbound_summaries(self) -> None:
        profiles = {"r1": {"candidate_id": "r1", "docling_json": "documents/r1.json", "markdown": "markdown/r1.md"}}
        summary = {
            "candidate_id": "stale",
            "source_docling_json": "documents/stale.json",
            "source_markdown": "markdown/stale.md",
        }
        with self.assertRaisesRegex(RuntimeError, "does not match"):
            validate_graph_summary_set([(Path("stale.json"), summary)], profiles)

    def test_graph_section_builder_binds_exact_source_hashes(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            directory_path = Path(directory)
            docling = directory_path / "paper.docling.json"
            markdown = directory_path / "paper.md"
            docling.write_text('{"schema_name":"DoclingDocument"}\n', encoding="utf-8")
            markdown.write_text("# Paper\n\nEvidence.\n", encoding="utf-8")
            docling_hash = hashlib.sha256(docling.read_bytes()).hexdigest()
            markdown_hash = hashlib.sha256(markdown.read_bytes()).hexdigest()
            profiles = {
                "r1": {
                    "candidate_id": "r1",
                    "docling_json": str(docling),
                    "docling_json_sha256": docling_hash,
                    "markdown": str(markdown),
                    "markdown_sha256": markdown_hash,
                }
            }
            summary = {
                "candidate_id": "r1",
                "source_docling_json": str(docling),
                "source_docling_sha256": docling_hash,
                "source_markdown": str(markdown),
                "source_markdown_sha256": markdown_hash,
            }
            validate_graph_summary_set([(Path("summary.json"), summary)], profiles)
            markdown.write_text("# Paper\n\nChanged evidence.\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "source hash mismatch"):
                validate_graph_summary_set([(Path("summary.json"), summary)], profiles)

    def test_docling_profile_identity_requires_title_or_doi_evidence(self) -> None:
        title_match = document_identity(
            "A Generative Foundation Model for Single Cell Biology",
            "",
            "# A Generative Foundation Model for Single Cell Biology\n\n## Abstract\nEvidence.",
        )
        self.assertEqual(title_match["status"], "verified")
        doi_match = document_identity(
            "Expected Title",
            "10.1234/example.5",
            "# Publisher export\n\nhttps://doi.org/10.1234/example.5\n",
        )
        self.assertTrue(doi_match["doi_match"])
        mismatch = document_identity(
            "Expected Biological Model Paper",
            "10.1234/missing",
            "# A Completely Different Article\n\nUnrelated contents.\n",
        )
        self.assertEqual(mismatch["status"], "unverified")

    def test_taxonomy_profile_contract_detects_post_manifest_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docling = root / "paper.json"
            markdown = root / "paper.md"
            docling.write_text("{}\n", encoding="utf-8")
            markdown.write_text("# Verified paper\n", encoding="utf-8")
            row = {
                "candidate_id": "r1",
                "profile_status": "complete",
                "document_identity_status": "verified",
                "docling_json": str(docling),
                "docling_json_sha256": hashlib.sha256(docling.read_bytes()).hexdigest(),
                "markdown": str(markdown),
                "markdown_sha256": hashlib.sha256(markdown.read_bytes()).hexdigest(),
            }
            validate_profile_artifacts(row)
            docling.write_text('{"changed":true}\n', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "hash mismatch"):
                validate_profile_artifacts(row)

    def test_heading_reconstruction_uses_the_complete_ancestor_trail(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            markdown = Path(directory) / "paper.md"
            markdown.write_text(
                "# Methods\n## Data\nmethods data\n# Supplement\n## Data\nsupplement data\n",
                encoding="utf-8",
            )
            result = derive_full_section(
                row={"markdown": str(markdown.relative_to(ROOT))},
                heading_path=["Supplement", "Data"],
                chunk_text="supplement data",
                evidence_quote="supplement data",
            )
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["text"], "supplement data")
            self.assertEqual(result["matched_by"], "exact_heading_path+evidence_quote")

    def test_title_abstract_fallback_requires_independent_metadata_corroboration(self) -> None:
        record = {"title": "A Biological Foundation Model", "year": "2026", "authors": "Ada Lovelace"}
        accepted, status, evidence = accept_title_candidate(
            record,
            {"title": "A Biological Foundation Model", "year": 2026, "authors": ["Ada Lovelace"]},
        )
        self.assertTrue(accepted)
        self.assertEqual(status, "accepted_title_match")
        self.assertTrue(evidence["exact_normalized_title"])

        accepted, status, _ = accept_title_candidate(
            record,
            {"title": "A Biological Foundation Model", "year": 2021, "authors": ["Ada Lovelace"]},
        )
        self.assertFalse(accepted)
        self.assertEqual(status, "year_conflict")

        accepted, status, _ = accept_title_candidate(
            {"title": "A Biological Foundation Model"},
            {"title": "A Biological Foundation Model", "year": None, "authors": []},
        )
        self.assertFalse(accepted)
        self.assertEqual(status, "insufficient_independent_corroboration")

    def test_title_fulltext_fallback_logs_rejected_candidate(self) -> None:
        attempts = []
        candidate = {
            "record": {"title": "A Biological Foundation Model", "year": "2026", "authors": "Ada Lovelace"},
            "title": "A Biological Foundation Model",
            "year": 2021,
            "authors": ["Ada Lovelace"],
            "doi": "10.1000/wrong-year",
        }
        self.assertFalse(record_title_candidate_attempt(attempts, "openalex_title_match", candidate))
        self.assertEqual(attempts[0]["title_match_status"], "year_conflict")
        self.assertEqual(attempts[0]["candidate_identifier"], "10.1000/wrong-year")

    def test_all_database_date_filters_are_updated(self) -> None:
        template = json.loads(
            (ROOT / "scripts/search_config_living_v3_3.json").read_text(
                encoding="utf-8"
            )
        )
        config = build_config(template, date(2026, 7, 7), date(2026, 8, 9))
        self.assertEqual(config["metadata"]["date_from"], "2026-07-07")
        self.assertEqual(config["metadata"]["date_to"], "2026-08-09")
        self.assertIn(
            '"2026/07/07"[Date - Publication] : "2026/08/09"[Date - Publication]',
            config["databases"]["pubmed"]["query"],
        )
        self.assertEqual(
            config["databases"]["arxiv"]["date_filter"],
            "submittedDate:[20260707 TO 20260809]",
        )
        self.assertIn(
            "FIRST_PDATE:[2026-07-07 TO 2026-08-09]",
            config["databases"]["biorxiv_medrxiv"]["query"],
        )
        self.assertEqual(
            config["databases"]["springernature"]["date_filter"],
            "datefrom:2026-07-07 dateto:2026-08-09",
        )
        self.assertEqual(config["databases"]["openalex"]["date_from"], "2026-07-07")
        self.assertEqual(config["databases"]["openalex"]["date_to"], "2026-08-09")
        self.assertEqual(
            config["databases"]["openalex"]["query_scopes"],
            {"main": "title_and_abstract", "model_names": "title"},
        )
        self.assertEqual(
            config["metadata"]["google_scholar_acquisition"],
            "provider_export_required",
        )

    def test_living_template_uses_supported_scopus_wildcard_syntax(self) -> None:
        template = json.loads(
            (ROOT / "scripts/search_config_living_v3_3.json").read_text(
                encoding="utf-8"
            )
        )
        query = template["databases"]["scopus"]["query"]
        self.assertNotIn('"pre-train*"', query)
        self.assertIn("pre-train*", query)

    def test_living_template_uses_one_google_scholar_query(self) -> None:
        template = json.loads(
            (ROOT / "scripts/search_config_living_v3_3.json").read_text(
                encoding="utf-8"
            )
        )
        scholar = template["databases"]["google_scholar"]
        self.assertEqual(len(scholar["queries"]), 1)
        self.assertNotIn("max_per_query", scholar)
        self.assertIn(" OR ", scholar["queries"][0])

    def test_interval_filter_exposes_uncertain_dates(self) -> None:
        self.assertEqual(
            classify_interval_date("2026-07-18", "2026-07-07", "2026-08-09"),
            "in_range",
        )
        self.assertEqual(
            classify_interval_date("2026", "2026-07-07", "2026-08-09"),
            "unknown_year_only",
        )
        kept, excluded, audit = filter_interval_records(
            [
                {"title": "exact", "date": "2026-07-18"},
                {"title": "coarse", "date": "2026"},
                {"title": "old", "date": "2026-06-01"},
                {"title": "missing", "date": ""},
            ],
            "2026-07-07",
            "2026-08-09",
        )
        self.assertEqual([row["title"] for row in kept], ["exact", "coarse", "missing"])
        self.assertEqual([row["title"] for row in excluded], ["old"])
        self.assertEqual(audit["counts"]["unknown_year_only"], 1)
        self.assertEqual(audit["counts"]["unknown_missing"], 1)

    def test_search_summary_fails_closed_on_partial_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            keys = root / "keys.json"
            output = root / "output"
            config.write_text(
                json.dumps(
                    {
                        "metadata": {
                            "review_title": "test",
                            "date_from": "2026-07-07",
                            "date_to": "2026-08-09",
                        },
                        "databases": {
                            "pubmed": {"enabled": True, "query": "test"},
                        },
                    }
                ),
                encoding="utf-8",
            )
            keys.write_text("{}", encoding="utf-8")
            result = {
                "database": "PubMed",
                "records_fetched": 1,
                "records": [{"title": "partial"}],
                "execution": {
                    "status": "incomplete",
                    "complete": False,
                    "reason": "test partial pagination",
                },
            }
            argv = [
                "reproduce_search.py",
                "--config",
                str(config),
                "--keys",
                str(keys),
                "--output-dir",
                str(output),
                "--file-date",
                "2026-08-09",
            ]
            with patch("reproduce_search.search_pubmed", return_value=result):
                with patch.object(sys, "argv", argv):
                    self.assertEqual(reproduce_search_main(), 2)
            summary = json.loads(
                (output / "search_summary_2026-08-09.json").read_text()
            )
            self.assertFalse(summary["complete"])
            self.assertEqual(summary["incomplete_databases"], ["pubmed"])

    def test_rate_limit_exhaustion_raises_explicit_error(self) -> None:
        response = Mock(status_code=429)
        with patch("reproduce_search.requests.get", return_value=response):
            with patch("reproduce_search.time.sleep"):
                with self.assertRaisesRegex(RuntimeError, "HTTP 429 rate limit"):
                    retry_request("https://example.invalid", max_retries=2, delay=0)

    def test_semantic_scholar_is_paced_resumable_and_preserves_query_membership(self) -> None:
        class Response:
            status_code = 200
            headers = {}

            def __init__(self, payload):
                self.payload = payload
                self.content = json.dumps(payload).encode("utf-8")

            def raise_for_status(self):
                return None

            def json(self):
                return self.payload

        config = {
            "metadata": {"date_from": "2026-07-07", "date_to": "2026-08-09"},
            "databases": {
                "semantic_scholar": {
                    "fields": "paperId,title,publicationDate",
                    "year_range": "2026-2026",
                    "date_from_post_filter": "2026-07-07",
                    "date_post_filter": "2026-08-09",
                    "queries": {"first": "first query", "second": "second query"},
                }
            },
        }
        paper = {"paperId": "p1", "title": "Paper", "publicationDate": "2026-07-20"}
        responses = [
            Response({"data": [paper], "token": "next"}),
            Response({"data": [], "token": None}),
            Response({"data": [paper], "token": None}),
        ]
        with tempfile.TemporaryDirectory() as directory:
            with patch("reproduce_search.requests.get", side_effect=responses):
                with patch("reproduce_search.time.sleep"):
                    result = search_semantic_scholar(
                        config, {"S2_API_KEY": "test-key"}, Path(directory)
                    )
            self.assertTrue(result["execution"]["complete"])
            self.assertEqual(result["records"][0]["found_by_queries"], ["first", "second"])
            checkpoint = json.loads((Path(directory) / "checkpoint.json").read_text())
            self.assertEqual(len(checkpoint["queries"]["first"]["pages"]), 2)
            self.assertEqual(len(checkpoint["queries"]["second"]["pages"]), 1)

    def test_semantic_scholar_rate_limit_writes_non_secret_checkpoint(self) -> None:
        class Response:
            status_code = 429
            headers = {"Retry-After": "0"}
            content = b"rate limited"

        config = {
            "metadata": {"date_from": "2026-07-07", "date_to": "2026-08-09"},
            "databases": {
                "semantic_scholar": {
                    "fields": "paperId,title",
                    "year_range": "2026-2026",
                    "date_from_post_filter": "2026-07-07",
                    "date_post_filter": "2026-08-09",
                    "queries": {"first": "first query"},
                }
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            with patch("reproduce_search.requests.get", return_value=Response()):
                with patch("reproduce_search.time.sleep"):
                    with self.assertRaises(SemanticScholarRateLimitError):
                        search_semantic_scholar(
                            config, {"S2_API_KEY": "test-key"}, Path(directory)
                        )
            checkpoint_text = (Path(directory) / "checkpoint.json").read_text()
            checkpoint = json.loads(checkpoint_text)
            self.assertEqual(len(checkpoint["request_events"]), 5)
            self.assertNotIn("test-key", checkpoint_text)

    def test_bounded_missing_abstract_fetch_cannot_exclude_unattempted_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            output = root / "output.json"
            excluded = root / "excluded.json"
            log_path = root / "log.json"
            source.write_text(
                json.dumps(
                    {
                        "metadata": {},
                        "records": [
                            {"cluster_id": "a", "title": "A", "abstract": ""},
                            {"cluster_id": "b", "title": "B", "abstract": ""},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            argv = [
                "enrich_abstracts.py",
                "--input",
                str(source),
                "--output",
                str(output),
                "--excluded-output",
                str(excluded),
                "--log-output",
                str(log_path),
                "--limit",
                "1",
            ]
            with patch("enrich_abstracts.fetch_abstract_s2_title", return_value=None):
                with patch("enrich_abstracts.time.sleep"):
                    with patch.object(sys, "argv", argv):
                        self.assertEqual(enrich_abstracts_main(), 2)
            self.assertFalse(output.exists())
            self.assertFalse(excluded.exists())
            log = json.loads(log_path.read_text())
            self.assertEqual(log["status"], "incomplete_fetch_limit")
            self.assertEqual(log["unattempted_missing_abstracts"], 1)

    def test_provider_mediated_google_scholar_export_requires_complete_bundle(self) -> None:
        config = {
            "metadata": {"date_from": "2026-07-07", "date_to": "2026-08-09"},
            "databases": {"google_scholar": {"queries": ["one", "two"], "year_range": [2026, 2026]}},
        }
        acquisition = {"provider": "test", "pagination_policy": "all visible pages"}
        bundle = {
            "queries": ["one", "two"],
            "year_range": [2026, 2026],
            "date_from": "2026-07-07",
            "date_to": "2026-08-09",
            "acquisition": acquisition,
        }
        payload = {
            "query_bundle": bundle,
            "query_signature": query_signature(
                bundle["queries"], bundle["year_range"], bundle["date_from"], bundle["date_to"], acquisition
            ),
            "raw_response_manifest": [],
            "query_execution": [
                {"query_id": "gs_q1", "execution_complete": True, "retrieval_complete": True},
                {"query_id": "gs_q2", "execution_complete": True, "retrieval_complete": True},
            ],
            "records": [{"title": "Paper", "query_ids": ["gs_q1", "gs_q2"]}],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "google.json"
            raw = Path(directory) / "raw/q1.json"
            raw.parent.mkdir()
            raw.write_text('{"organic_results": []}\n', encoding="utf-8")
            payload["raw_response_manifest"] = [
                {
                    "artifact": "raw/q1.json",
                    "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
                }
            ]
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = load_google_scholar_provider_export(config, path)
        self.assertTrue(result["execution"]["complete"])
        self.assertEqual(result["records"][0]["query_ids"], ["gs_q1", "gs_q2"])


class CrossDedupTests(unittest.TestCase):
    @staticmethod
    def dedup_record(title: str, doi: str, source: str) -> dict:
        from deduplicate import normalize_doi, normalize_title

        return {
            "source_db": source,
            "title_original": title,
            "title_normalized": normalize_title(title),
            "doi_original": doi,
            "doi_normalized": normalize_doi(doi),
            "pmid": "",
            "arxiv_id_original": "",
            "arxiv_id_normalized": "",
            "s2_id": "",
            "abstract": "",
            "authors": [],
            "year": "2026",
            "venue": "",
            "date": "2026-07-20",
            "url": "",
            "search_date_status": "in_range",
            "query_id": "q1",
        }

    def test_conflicting_published_dois_are_not_title_merged(self) -> None:
        engine = DeduplicationEngine()
        engine.add_record(self.dedup_record("Shared title", "10.1000/a", "pubmed"))
        engine.add_record(self.dedup_record("Shared title", "10.1000/b", "scopus"))
        self.assertEqual(len(engine.get_deduplicated_records()), 2)
        self.assertEqual(len(engine.review_queue), 1)
        self.assertEqual(engine.review_queue[0]["automatic_action"], "kept_separate")

    def test_preprint_and_published_doi_can_title_merge(self) -> None:
        engine = DeduplicationEngine()
        engine.add_record(self.dedup_record("Versioned paper", "10.1101/123", "biorxiv_medrxiv"))
        engine.add_record(self.dedup_record("Versioned paper", "10.1000/final", "pubmed"))
        rows = engine.get_deduplicated_records()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["doi"], "10.1000/final")
        self.assertEqual(rows[0]["preprint_doi"], "10.1101/123")

    def test_dedup_boundary_rejects_incomplete_search_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = root / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "complete": False,
                        "incomplete_databases": ["semantic_scholar"],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "semantic_scholar"):
                validate_search_contract(summary, root, {})

    def test_match_order_and_global_update_ids(self) -> None:
        master = [
            {"record_id": "old-doi", "title": "Known", "doi": "10.1/known"},
            {"record_id": "old-title", "title": "Same normalized: title!", "doi": ""},
        ]
        index = MasterIndex(master)
        matched, reason = index.match(
            {"title": "Changed title", "doi": "https://doi.org/10.1/KNOWN"}
        )
        self.assertEqual(matched["record_id"], "old-doi")
        self.assertTrue(reason.startswith("DOI match"))
        matched, reason = index.match({"title": "Same normalized title", "doi": ""})
        self.assertEqual(matched["record_id"], "old-title")
        self.assertEqual(reason, "Exact title match")
        assigned = assign_ids([{"title": "New"}], "update_2026-08-09")
        self.assertEqual(assigned[0]["record_id"], "update_2026-08-09__rec_000001")
        self.assertEqual(assigned[0]["source_record_id"], "rec_000001")

    def test_cumulative_title_match_does_not_hide_conflicting_doi(self) -> None:
        index = MasterIndex(
            [{"record_id": "old", "title": "Same paper title", "doi": "10.1000/a"}]
        )
        matched, reason = index.match(
            {"title": "Same paper title", "doi": "10.1000/b"}
        )
        self.assertIsNone(matched)
        self.assertEqual(reason, "")
        self.assertEqual(len(index.review_queue), 1)

    def test_crossref_acceptance_requires_corroboration(self) -> None:
        record = {
            "title": "A study",
            "year": "2026",
            "authors": "Ada Lovelace; Grace Hopper",
        }
        accepted, status, evidence = crossref_acceptance(
            record,
            {
                "score": 1.0,
                "doi": "10.1000/x",
                "year": 2026,
                "authors": ["Ada Lovelace"],
            },
            0.88,
        )
        self.assertTrue(accepted)
        self.assertEqual(status, "accepted_title_match")
        self.assertEqual(evidence["author_overlap"], ["lovelace"])
        accepted, status, _ = crossref_acceptance(
            record,
            {
                "score": 1.0,
                "doi": "10.1000/y",
                "year": 2022,
                "authors": ["Ada Lovelace"],
            },
            0.88,
        )
        self.assertFalse(accepted)
        self.assertEqual(status, "crossref_year_conflict")

    def test_crossref_detects_hidden_duplicate_within_update(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            update = root / "update.json"
            master = root / "master.json"
            output = root / "output"
            update.write_text(
                json.dumps(
                    {
                        "records": [
                            {"cluster_id": "a", "title": "Version A", "year": "2026", "authors": "Ada Lovelace"},
                            {"cluster_id": "b", "title": "Version B", "year": "2026", "authors": "Ada Lovelace"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            master.write_text('{"records": []}', encoding="utf-8")
            argv = [
                "prepare_incremental_records.py",
                "--update-records",
                str(update),
                "--master-records",
                str(master),
                "--output-dir",
                str(output),
                "--run-id",
                "update_test",
                "--sleep",
                "0",
            ]
            match = {
                "score": 0.99,
                "title": "Canonical paper",
                "doi": "10.1234/shared",
                "type": "journal-article",
                "publisher": "Publisher",
                "year": 2026,
                "authors": ["Ada Lovelace"],
            }
            with patch("prepare_incremental_records.crossref_lookup", return_value=match):
                with patch.object(sys, "argv", argv):
                    self.assertEqual(prepare_incremental_main(), 0)
            stats = json.loads((output / "crossref_checked_stats.json").read_text())
            records = json.loads(
                (output / "new_records_after_cross_dedup_crossref_checked.json").read_text()
            )["records"]
            self.assertEqual(stats["hidden_within_update_duplicates_removed_by_crossref"], 1)
            self.assertEqual(len(records), 1)


class CohortTests(unittest.TestCase):
    def test_supplementary_pdf_is_identified_for_docling_ranking(self) -> None:
        self.assertEqual(
            classify_pdf_text_role(
                "Unify learns cellular evolution with universal multimodal embeddings Supplementary Note 1"
            ),
            "supplementary",
        )
        self.assertEqual(
            classify_pdf_text_role("Unify learns cellular evolution with universal multimodal embeddings Abstract"),
            "main_or_unknown",
        )

    def test_fulltext_candidates_apply_crosswalk_and_postscreen_dedup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decisions = root / "decisions.json"
            screening_input = root / "input.json"
            crosswalk = root / "crosswalk.json"
            canonical_input = root / "canonical.json"
            resolutions = root / "resolutions.json"
            output = root / "fulltext.json"
            decisions.write_text(
                json.dumps(
                    {
                        "records": [
                            {"record_id": "rec_1", "final_decision": "INCLUDE"},
                            {"record_id": "rec_2", "final_decision": "INCLUDE"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            screening_input.write_text(
                json.dumps(
                    {
                        "records": [
                            {"record_id": "rec_1", "title": "Canonical"},
                            {"record_id": "rec_2", "title": "Duplicate"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            crosswalk.write_text(
                json.dumps(
                    {
                        "records": [
                            {"legacy_record_id": "rec_1", "stable_record_id": "stable_1"},
                            {"legacy_record_id": "rec_2", "stable_record_id": "stable_2"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            canonical_input.write_text(
                json.dumps(
                    {
                        "records": [
                            {"record_id": "stable_1", "title": "Canonical", "url": "https://example.org/paper.pdf"},
                            {"record_id": "stable_2", "title": "Duplicate", "url": "https://example.org/duplicate.pdf"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            resolutions.write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "duplicate_screening_record_id": "rec_2",
                                "canonical_screening_record_id": "rec_1",
                                "resolution": "duplicate_of",
                                "rationale": "Exact DOI and title match",
                                "resolver": "test",
                                "resolved_at": "2026-08-16T12:00:00+00:00",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            fulltext_candidates(
                argparse.Namespace(
                    screening_results=decisions,
                    screening_input=screening_input,
                    record_id_crosswalk=crosswalk,
                    canonical_input=canonical_input,
                    duplicate_resolutions=resolutions,
                    output=output,
                )
            )
            artifact = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(artifact["metadata"]["raw_screening_candidates"], 2)
            self.assertEqual(artifact["metadata"]["candidate_count"], 1)
            self.assertEqual(artifact["records"][0]["record_id"], "stable_1")
            self.assertEqual(artifact["records"][0]["screening_record_id"], "rec_1")
            self.assertEqual(artifact["records"][0]["url"], "https://example.org/paper.pdf")
            self.assertEqual(len(artifact["removed_duplicates"]), 1)

    def test_retrieval_payload_and_failure_states_are_not_conflated(self) -> None:
        self.assertFalse(looks_like_pdf(b"<html>access denied</html>", "application/pdf"))
        self.assertTrue(looks_like_pdf(b"%PDF-1.7\n", "text/html"))
        failures = technical_attempt_failures(
            [
                {"status_code": 404},
                {"status_code": 403},
                {"status_code": 429},
                {"error": "timeout"},
            ]
        )
        self.assertEqual(len(failures), 2)
        self.assertEqual(
            len(access_restriction_attempts([{"status_code": 403}, {"status_code": 429}])),
            1,
        )
        self.assertEqual(
            normalized_download_status(
                {
                    "status": "non_pdf_full_text_downloaded",
                    "files": [{"filename": "article.xml"}],
                }
            ),
            "xml_full_text_downloaded",
        )

    def test_taxonomy_analysis_rejects_duplicate_success_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for shard in ("shard_00", "shard_01"):
                output = root / shard / "records" / "r1"
                output.mkdir(parents=True)
                (output / "fixed_candidate_classification.json").write_text(
                    json.dumps({"status": "ok", "record_id": "r1"}), encoding="utf-8"
                )
            with self.assertRaisesRegex(RuntimeError, "Duplicate successful fixed"):
                load_fixed_run(root)

    def test_accepted_records_restore_metadata_without_expanding_screening_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decisions = root / "decisions.json"
            screening_input = root / "input.json"
            source_records = root / "candidates.json"
            profiles = root / "profiles.csv"
            decisions.write_text(
                json.dumps({"records": [{"record_id": "r1", "candidate_id": "r1", "final_decision": "INCLUDE"}]}),
                encoding="utf-8",
            )
            screening_input.write_text(
                json.dumps({"records": [{"record_id": "r1", "candidate_id": "r1", "title": "Paper", "abstract": "A", "selected_full_text_sections": "Methods"}]}),
                encoding="utf-8",
            )
            source_records.write_text(
                json.dumps({"records": [{"record_id": "r1", "candidate_id": "r1", "title": "Paper", "abstract": "A", "doi": "10.1/example", "year": "2026", "venue": "Journal", "sources": ["database"]}]}),
                encoding="utf-8",
            )
            profiles.write_text(
                "candidate_id,profile_status,source_document,source_document_kind\n"
                "r1,complete,paper.pdf,pdf\n",
                encoding="utf-8",
            )
            output = root / "accepted.json"
            accepted_records(
                argparse.Namespace(
                    screening_results=decisions,
                    screening_input=screening_input,
                    source_records=source_records,
                    profile_manifest=profiles,
                    manual_resolution=None,
                    output=output,
                    excluded_output=root / "excluded.json",
                    unresolved_output=root / "unresolved.json",
                )
            )
            row = json.loads(output.read_text(encoding="utf-8"))["records"][0]
            self.assertEqual(row["doi"], "10.1/example")
            self.assertEqual(row["year"], "2026")
            self.assertEqual(row["venue"], "Journal")
            self.assertEqual(row["selected_full_text_sections"], "Methods")

    def test_manual_eligibility_resolutions_are_owned_by_uncertain_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decisions = root / "decisions.json"
            screening_input = root / "input.json"
            profiles = root / "profiles.csv"
            manual = root / "manual.csv"
            decisions.write_text(
                json.dumps({"records": [{"record_id": "r1", "candidate_id": "r1", "final_decision": "INCLUDE"}]}),
                encoding="utf-8",
            )
            screening_input.write_text(
                json.dumps({"records": [{"record_id": "r1", "candidate_id": "r1"}]}),
                encoding="utf-8",
            )
            profiles.write_text(
                "candidate_id,profile_status,source_document,source_document_kind\n"
                "r1,complete,paper.pdf,pdf\n",
                encoding="utf-8",
            )
            manual.write_text(
                "record_id,manual_decision,rationale,resolver,resolved_at\n"
                "r1,EXCLUDE,override,reviewer,2026-08-10\n",
                encoding="utf-8",
            )
            args = argparse.Namespace(
                screening_results=decisions,
                screening_input=screening_input,
                profile_manifest=profiles,
                manual_resolution=manual,
                output=root / "accepted.json",
                excluded_output=root / "excluded.json",
                unresolved_output=root / "unresolved.json",
            )
            with self.assertRaisesRegex(RuntimeError, "non-UNCERTAIN"):
                accepted_records(args)

    def test_cross_dedup_manual_resolutions_require_exact_queue_membership(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manual.json"
            review_queue = [{"update": {"cluster_id": "cluster_1"}, "master_candidates": []}]
            path.write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "update_cluster_id": "orphan",
                                "decision": "keep_new",
                                "rationale": "not in queue",
                                "resolver": "reviewer",
                                "resolved_at": "2026-08-10",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "not in the review queue"):
                apply_cross_dedup_resolutions([], [], review_queue, path)

    def test_abstract_threshold_is_auditable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "records.json"
            output = root / "screening.json"
            excluded = root / "excluded.json"
            source.write_text(
                json.dumps(
                    {
                        "records": [
                            {"record_id": "a", "abstract": "x" * 50},
                            {"record_id": "b", "abstract": "x" * 49},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            args = argparse.Namespace(
                input=source,
                output=output,
                excluded_output=excluded,
                minimum_chars=50,
            )
            self.assertEqual(abstract_input(args), 0)
            self.assertEqual(len(json.loads(output.read_text())["records"]), 1)
            excluded_rows = json.loads(excluded.read_text())["records"]
            self.assertEqual(excluded_rows[0]["exclusion_code"], "EC_NO_USABLE_ABSTRACT")
            self.assertEqual(excluded_rows[0]["abstract_chars"], 49)

    def test_docling_document_selection_rejects_xml_only_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            xml = root / "article.xml"
            html = root / "article.html"
            xml.write_text("<?xml version='1.0'?><article/>", encoding="utf-8")
            selected, kind, unsupported = best_document({"files": [{"file": str(xml)}]})
            self.assertIsNone(selected)
            self.assertEqual(kind, "")
            self.assertEqual(len(unsupported), 1)
            html.write_text(
                "<!doctype html><html><body>" + ("paper content " * 300) + "</body></html>",
                encoding="utf-8",
            )
            selected, kind, unsupported = best_document(
                {"files": [{"file": str(xml)}, {"file": str(html)}]}
            )
            self.assertEqual(selected, html.resolve())
            self.assertEqual(kind, "html")
            self.assertEqual(len(unsupported), 1)

    def test_manual_section_override_is_exact_screening_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            automatic = root / "automatic.json"
            source = root / "source.json"
            metadata = root / "metadata.json"
            profile_manifest = root / "profiles.csv"
            markdown = root / "paper.md"
            overrides = root / "overrides.json"
            output = root / "merged.json"
            audit = root / "audit.json"
            automatic.write_text("[]", encoding="utf-8")
            source.write_text(
                json.dumps({"records": [{"record_id": "r1", "candidate_id": "r1", "source_record_id": "r1", "title": "T", "abstract": "A", "docling_markdown": "must not leak"}]}),
                encoding="utf-8",
            )
            markdown.write_text(
                "# Methods\n## Data\nCanonical data section\n## Input\nCanonical input section\n",
                encoding="utf-8",
            )
            profile_manifest.write_text(
                "candidate_id,source_record_id,profile_status,markdown\n"
                f"r1,r1,complete,{markdown}\n",
                encoding="utf-8",
            )
            metadata.write_text(
                json.dumps({"excluded_records": [{"record_id": "r1", "candidate_id": "r1"}]}),
                encoding="utf-8",
            )
            overrides.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "records": [{
                            "record_id": "r1", "candidate_id": "r1",
                            "source_markdown": str(markdown),
                            "source_markdown_sha256": hashlib.sha256(markdown.read_bytes()).hexdigest(),
                            "sections": [
                                {"target_section_types": ["data_source"], "heading_path": ["Methods", "Data"]},
                                {"target_section_types": ["input_representation"], "heading_path": ["Methods", "Input"]},
                            ],
                            "rationale": "manual boundary", "resolver": "review lead", "resolved_at": "2026-08-09",
                        }],
                    }
                ),
                encoding="utf-8",
            )
            args = argparse.Namespace(
                input=automatic,
                source_records=source,
                run_metadata=metadata,
                profile_manifest=profile_manifest,
                overrides=overrides,
                output=output,
                audit_output=audit,
            )
            self.assertEqual(apply_section_overrides(args), 0)
            row = json.loads(output.read_text())[0]
            self.assertEqual(
                set(row),
                {"record_id", "candidate_id", "source_record_id", "source_corpus", "title", "abstract", "selected_full_text_sections"},
            )
            self.assertNotIn("docling_markdown", row)
            self.assertIn("Canonical data section", row["selected_full_text_sections"])
            self.assertNotIn("must not leak", row["selected_full_text_sections"])
            self.assertEqual(json.loads(audit.read_text())["records"][0]["validation_status"], "validated_canonical_section_selectors")
            invalid = json.loads(overrides.read_text())
            invalid["records"][0]["selected_full_text_sections"] = "untrusted pasted text"
            overrides.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "must not supply"):
                apply_section_overrides(args)

    def test_manual_fulltext_ingest_validates_and_copies_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            automatic = root / "automatic.json"
            declaration = root / "manual.json"
            source_pdf = root / "downloaded.pdf"
            output = root / "run" / "fulltext_download_manifest.json"
            source_pdf.write_bytes(b"%PDF-1.7\n" + b"0" * 6000)
            automatic.write_text(
                json.dumps({"results": [{"candidate_id": "r1", "record_id": "r1", "status": "no_full_text_found", "files": []}]}),
                encoding="utf-8",
            )
            declaration.write_text(
                json.dumps({"records": [{"candidate_id": "r1", "file": str(source_pdf), "retriever": "review lead"}]}),
                encoding="utf-8",
            )
            args = argparse.Namespace(
                manifest=[automatic], manual_manifest=declaration, output=output
            )
            self.assertEqual(consolidate_downloads(args), 0)
            payload = json.loads(output.read_text())
            self.assertEqual(payload["manual_full_texts_ingested"], 1)
            self.assertEqual(payload["results"][0]["status"], "pdf_downloaded")
            copied = Path(payload["results"][0]["files"][0]["file"])
            self.assertTrue(copied.is_file())
            self.assertNotEqual(copied, source_pdf)


class ScreeningPayloadTests(unittest.TestCase):
    def test_fulltext_prompt_contains_only_selected_sections(self) -> None:
        source = {
            "record_id": "r1",
            "title": "Paper",
            "abstract": "Abstract evidence",
            "selected_full_text_sections": "Complete selected section",
            "section_evidence": [{"text": "must not enter prompt"}],
            "docling_markdown": "whole paper must not enter prompt",
        }
        record = safe_record(source, 1)
        prompt = build_role_prompt("scope_reviewer", [record], evidence_mode="full_text_sections")
        self.assertIn("Complete selected section", prompt)
        self.assertNotIn("whole paper must not enter prompt", prompt)
        self.assertNotIn("must not enter prompt", prompt)

    def test_title_abstract_mode_preserves_original_evidence_surface(self) -> None:
        record = safe_record(
            {
                "record_id": "r1",
                "title": "Paper",
                "abstract": "Abstract evidence",
                "selected_full_text_sections": "must not enter abstract screening",
            },
            1,
        )
        prompt = build_role_prompt("scope_reviewer", [record], evidence_mode="title_abstract")
        self.assertIn("Abstract evidence", prompt)
        self.assertNotIn("must not enter abstract screening", prompt)

    def test_graph_screening_projection_is_minimal(self) -> None:
        projected = screening_only_record(
            {
                "record_id": "r1",
                "candidate_id": "c1",
                "source_record_id": "s1",
                "source_corpus": "update",
                "title": "Paper",
                "abstract": "Abstract",
                "selected_full_text_sections": "Sections",
                "section_evidence": [{"heading": "Methods"}],
                "docling_markdown": "Whole document",
            }
        )
        self.assertEqual(
            set(projected),
            {"record_id", "candidate_id", "source_record_id", "source_corpus", "title", "abstract", "selected_full_text_sections"},
        )


class BaselineRegistryTests(unittest.TestCase):
    def test_frozen_baseline_registry_remains_52_records(self) -> None:
        path = ROOT / "data/input_representation_taxonomy_2026-07-11/study_model_registry.csv"
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 52)
        self.assertEqual(len({row["study_id"] for row in rows}), 51)

    @staticmethod
    def source_row(record_id: str, source_hash: str = "hash-a") -> dict[str, str]:
        return {
            "candidate_id": record_id,
            "source_record_id": record_id,
            "source_document_sha256": source_hash,
            "title": record_id,
            "doi": "",
            "docling_json": f"{record_id}.json",
            "markdown": f"{record_id}.md",
        }

    @staticmethod
    def prior_row(
        record_id: str,
        *,
        canonical: bool,
        source_hash: str = "hash-a",
    ) -> dict[str, str]:
        return {
            "record_id": record_id,
            "study_id": "study-preserved",
            "source_document_sha256": source_hash,
            "canonical_record_for_study": str(canonical),
        }

    def test_same_record_prior_reuse_is_not_a_duplicate(self) -> None:
        registry, groups = assemble_registry(
            [self.source_row("record-a")],
            [self.prior_row("record-a", canonical=True)],
        )
        self.assertEqual(groups, [])
        self.assertTrue(registry[0]["canonical_record_for_study"])
        self.assertFalse(registry[0]["exact_duplicate"])
        self.assertEqual(registry[0]["study_id"], "study-preserved")

    def test_new_cross_record_exact_duplicate_inherits_prior_canonical(self) -> None:
        registry, groups = assemble_registry(
            [self.source_row("record-new")],
            [self.prior_row("record-old", canonical=True)],
        )
        self.assertFalse(registry[0]["canonical_record_for_study"])
        self.assertTrue(registry[0]["exact_duplicate"])
        self.assertEqual(groups[0]["record_ids"], ["record-new", "record-old"])
        self.assertEqual(groups[0]["canonical_record_id"], "record-old")

    def test_full_cohort_duplicate_group_does_not_repeat_prior_ids(self) -> None:
        registry, groups = assemble_registry(
            [self.source_row("record-a"), self.source_row("record-b")],
            [
                self.prior_row("record-a", canonical=True),
                self.prior_row("record-b", canonical=False),
            ],
        )
        self.assertEqual(groups[0]["record_ids"], ["record-a", "record-b"])
        by_id = {row["record_id"]: row for row in registry}
        self.assertTrue(by_id["record-a"]["canonical_record_for_study"])
        self.assertFalse(by_id["record-b"]["canonical_record_for_study"])

    def test_full_cohort_methods_are_derived_from_current_run(self) -> None:
        lines = corpus_description(
            protocol_mode="full_cohort_frozen_taxonomy",
            expected=55,
            cohort_label="full living catalog",
            inventory_candidate_count=644,
            taxonomy_version="v1",
            taxonomy_synthesis_runs=0,
            registry_rows=[self.prior_row("record-a", canonical=True)],
        )
        text = " ".join(lines)
        self.assertIn("55 accepted screening records", text)
        self.assertIn("644 candidates", text)
        self.assertIn("did not re-synthesize", text)
        self.assertNotIn("52 accepted", text)
        self.assertNotIn("583", text)
        self.assertNotIn("Three independent", text)


class MethodLockTests(unittest.TestCase):
    def test_repository_method_lock_passes(self) -> None:
        current = json.loads((ROOT / "data/living_catalog/current.json").read_text())
        result = verify_method_lock(
            ROOT / "protocol/living_review_method_lock_v1.json",
            ROOT / "config/living_review_pipeline.json",
            current_taxonomy_tree=ROOT / current["taxonomy_root"] / "taxonomy_tree.json",
        )
        self.assertTrue(result["ok"], result["issues"])

    def test_configured_model_drift_fails_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = json.loads((ROOT / "config/living_review_pipeline.json").read_text())
            config["models"]["graph"] = "openai/different-model"
            config_path = Path(directory) / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            result = verify_method_lock(
                ROOT / "protocol/living_review_method_lock_v1.json",
                config_path,
            )
        self.assertFalse(result["ok"])
        self.assertTrue(
            any("models.graph" in issue for issue in result["issues"]),
            result["issues"],
        )


class CanonicalProfileManifestTests(unittest.TestCase):
    def test_restore_validator_checks_all_profile_payload_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "original_run"
            original.mkdir()
            source = original / "paper.pdf"
            docling_json = original / "paper.docling.json"
            markdown = original / "paper.md"
            figures = original / "figures_manifest.json"
            source.write_bytes(b"%PDF-1.4\nrestored article")
            docling_json.write_text('{"schema_name":"DoclingDocument"}\n', encoding="utf-8")
            markdown.write_text("# Restored article\n", encoding="utf-8")
            figures.write_text('[{"index":1}]\n', encoding="utf-8")

            def digest(path: Path) -> str:
                return hashlib.sha256(path.read_bytes()).hexdigest()

            row = {
                "candidate_id": "rec_restore",
                "profile_status": "complete",
                "document_identity_status": "verified",
                "source_document": str(source),
                "source_document_sha256": digest(source),
                "docling_json": str(docling_json),
                "docling_json_sha256": digest(docling_json),
                "markdown": str(markdown),
                "markdown_sha256": digest(markdown),
                "figures_manifest": str(figures),
                "figures_manifest_sha256": digest(figures),
                "figure_count": "1",
            }
            self.assertEqual(
                validate_canonical_profile_row(row)["candidate_id"], "rec_restore"
            )
            restored = root / "restored_run"
            shutil.copytree(original, restored)
            rebased = rebase_canonical_profile_row(row, original, restored)
            shutil.rmtree(original)
            self.assertEqual(
                validate_canonical_profile_row(rebased)["candidate_id"], "rec_restore"
            )
            (restored / "figures_manifest.json").write_text("[]\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Hash mismatch"):
                validate_canonical_profile_row(rebased)


class ArtifactArchiveTests(unittest.TestCase):
    @staticmethod
    def write_manifest(root: Path) -> None:
        payload = root / "profiles/record/document.dclg"
        payload.parent.mkdir(parents=True)
        payload.write_bytes(b"expensive graph payload")
        digest = hashlib.sha256(payload.read_bytes()).hexdigest()
        manifest = root / "artifact_manifest.csv"
        manifest.write_text(
            "relative_path,category,size_bytes,mtime_utc,sha256\n"
            f"profiles/record/document.dclg,test,{payload.stat().st_size},2026-01-01T00:00:00+00:00,{digest}\n",
            encoding="utf-8",
        )
        summary = {
            "artifact_root": str(root),
            "file_count": 1,
            "total_size_bytes": payload.stat().st_size,
            "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        }
        (root / "artifact_manifest_summary.json").write_text(
            json.dumps(summary), encoding="utf-8"
        )

    def test_create_verify_and_restore_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "run"
            source.mkdir()
            self.write_manifest(source)
            args = argparse.Namespace(
                source_root=source,
                archive_root=root / "archives",
                receipt_dir=root / "receipts",
                label="test-run",
                storage_class="local_secondary",
                compression_level=1,
            )
            created = create_archive(args)
            self.assertTrue(created["ok"], created["issues"])
            receipt = next((root / "receipts").glob("*.json"))
            verified = verify_archive(receipt, None, update_receipt=False)
            self.assertTrue(verified["ok"], verified["issues"])
            restored = restore_archive(
                argparse.Namespace(
                    receipt=receipt,
                    archive=None,
                    destination=root / "restored",
                )
            )
            self.assertTrue(restored["ok"])
            self.assertEqual(
                (root / "restored/profiles/record/document.dclg").read_bytes(),
                b"expensive graph payload",
            )

    def test_stale_manifest_blocks_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "run"
            source.mkdir()
            self.write_manifest(source)
            (source / "unlisted.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                create_archive(
                    argparse.Namespace(
                        source_root=source,
                        archive_root=root / "archives",
                        receipt_dir=root / "receipts",
                        label="test-run",
                        storage_class="local_secondary",
                        compression_level=1,
                    )
                )


class CropValidationTests(unittest.TestCase):
    def test_crop_figure_lookup_uses_profile_record_binding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            figures = root / "figures/c1/figures_manifest.json"
            figures.parent.mkdir(parents=True)
            figures.write_text(json.dumps([{"candidate_id": "c1", "figure_index": 1}]), encoding="utf-8")
            manifest = root / "manifests/canonical_docling_profile_manifest.csv"
            manifest.parent.mkdir()
            manifest.write_text(
                "candidate_id,source_record_id,profile_status,figures_manifest\n"
                f"c1,r1,complete,{figures}\n",
                encoding="utf-8",
            )
            by_record = load_figures_by_record(root)
            self.assertEqual(by_record["r1"][0]["figure_index"], 1)
            self.assertEqual(by_record["c1"][0]["figure_index"], 1)

    def test_selected_figure_must_reference_grounded_route(self) -> None:
        valid_figures = {1, 2}
        valid_routes = {"route_1"}
        validate_selection(
            {
                "decision": "select_figure",
                "figure_index": 2,
                "route_ids_supported": ["route_1"],
            },
            valid_figures,
            valid_routes,
        )
        with self.assertRaises(RuntimeError):
            validate_selection(
                {
                    "decision": "select_figure",
                    "figure_index": 2,
                    "route_ids_supported": ["route_missing"],
                },
                valid_figures,
                valid_routes,
            )


class OrchestratorTests(unittest.TestCase):
    @staticmethod
    def pipeline_args_and_config(root: Path) -> tuple[argparse.Namespace, dict]:
        config = {
            "baseline_search_end": "2026-07-06",
            "master_record_files": [],
            "baseline_taxonomy_root": str(root / "taxonomy"),
            "baseline_docling_corpus_roots": [],
            "baseline_crop_ledger": str(root / "crops.json"),
            "living_state": str(root / "current.json"),
            "updates_root": str(root / "updates"),
            "atlas_output": str(root / "atlas"),
        }
        args = argparse.Namespace(
            config=root / "config.json",
            run_id="update_test",
            date_from="2026-07-07",
            date_to="2026-08-09",
            force=False,
            manage_server=False,
            from_stage=None,
            through_stage=None,
        )
        return args, config

    def test_upstream_rerun_invalidates_all_downstream_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            self.assertEqual(pipeline.current["prisma_update_history"], [])
            pipeline.manifest["stages"] = {
                "search": {"status": "complete"},
                "deduplicate": {"status": "complete"},
                "abstract-screening": {"status": "complete"},
                "atlas": {"status": "complete"},
            }
            pipeline.invalidate_from(
                "deduplicate", include_stage=False, reason="test upstream change"
            )
            self.assertEqual(set(pipeline.manifest["stages"]), {"search", "deduplicate"})
            invalidated = pipeline.manifest["invalidation_history"][-1]["invalidated"]
            self.assertEqual(
                {row["stage"] for row in invalidated},
                {"abstract-screening", "atlas"},
            )

    def test_abstract_screening_uses_hash_pinned_legacy_runner(self) -> None:
        pipeline = Pipeline.__new__(Pipeline)
        pipeline.config = json.loads(
            (ROOT / "config/living_review_pipeline.json").read_text(encoding="utf-8")
        )
        command = pipeline.screening_command(
            Path("input.json"), Path("output"), "title_abstract"
        )
        self.assertIn(
            "analysis/codex_screening_run_artifacts_20260706/pipeline_code/run_codex_screening_pipeline.py",
            command[1],
        )
        self.assertEqual(command[command.index("--model") + 1], "gpt-5.4-mini")
        self.assertNotIn("--evidence-mode", command)
        self.assertNotIn("--codex-timeout", command)

    def test_legacy_abstract_screening_crosswalk_preserves_stable_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            pipeline.paths.abstract_input.parent.mkdir(parents=True)
            pipeline.paths.abstract_input.write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "record_id": "update_2026-08-09__stable_1",
                                "candidate_id": "candidate_1",
                                "title": "Stable title",
                                "abstract": "Stable abstract",
                                "doi": "10.1/stable",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            pipeline.paths.abstract_screening.mkdir(parents=True)
            (pipeline.paths.abstract_screening / "input_records.json").write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "record_id": "rec_000001",
                                "title": "Stable title",
                                "abstract": "Stable abstract",
                                "doi": "10.1/stable",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            crosswalk = json.loads(
                pipeline.write_abstract_screening_crosswalk().read_text()
            )
            self.assertEqual(
                crosswalk["records"],
                [
                    {
                        "legacy_record_id": "rec_000001",
                        "stable_record_id": "update_2026-08-09__stable_1",
                        "candidate_id": "candidate_1",
                        "input_position": 1,
                    }
                ],
            )

    def test_postscreen_duplicate_resolution_is_optional_and_fingerprinted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            pipeline.manifest["method_lock"] = {"method_id": "test-method"}
            with patch.object(pipeline, "run_command") as run:
                pipeline.stage_fulltext_candidates()
            command = run.call_args.args[2]
            self.assertNotIn("--duplicate-resolutions", command)

            declaration = (
                pipeline.paths.fulltext / "postscreen_dedup/duplicate_resolutions.json"
            )
            declaration.parent.mkdir(parents=True)
            declaration.write_text('{"records":[]}\n', encoding="utf-8")
            with patch.object(pipeline, "run_command") as run:
                pipeline.stage_fulltext_candidates()
            command = run.call_args.args[2]
            self.assertEqual(
                command[command.index("--duplicate-resolutions") + 1], str(declaration)
            )
            fingerprints = pipeline.human_input_fingerprints("fulltext-candidates")
            self.assertTrue(fingerprints[0]["present"])
            self.assertIn("sha256", fingerprints[0])

    def test_new_routine_plan_requires_explicit_end_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            args.command = "plan"
            args.run_id = None
            args.date_to = None
            with self.assertRaisesRegex(ValueError, "explicit --date-to"):
                Pipeline(args, config)
            args.run_id = "update_not_started"
            with self.assertRaisesRegex(ValueError, "explicit --date-to"):
                Pipeline(args, config)

    def test_fulltext_screening_logs_three_bounded_batch_attempts(self) -> None:
        pipeline = Pipeline.__new__(Pipeline)
        pipeline.config = json.loads(
            (ROOT / "config/living_review_pipeline.json").read_text(encoding="utf-8")
        )
        command = pipeline.screening_command(
            Path("input.json"), Path("output"), "full_text_sections"
        )
        self.assertEqual(command[command.index("--model") + 1], "gpt-5.4-mini")
        self.assertEqual(command[command.index("--batch-attempts") + 1], "3")
        self.assertEqual(
            command[command.index("--evidence-mode") + 1], "full_text_sections"
        )

    def test_failed_screening_attempt_is_archived_before_retry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outdir = Path(directory)
            role_dir = outdir / "role_logs" / "scope_reviewer"
            role_dir.mkdir(parents=True)
            for suffix in ("prompt.txt", "response.txt", "meta.json"):
                (role_dir / f"batch_0001.{suffix}").write_text(suffix, encoding="utf-8")
            archived = archive_failed_batch_attempt(outdir, "scope_reviewer", 1, 1)
            self.assertEqual(len(archived), 3)
            self.assertTrue((role_dir / "batch_0001.attempt_01.prompt.txt").exists())
            self.assertFalse((role_dir / "batch_0001.prompt.txt").exists())

    def test_incomplete_batch_recovers_by_logged_complete_split(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outdir = Path(directory)
            batch = [{"record_id": f"r{i}"} for i in range(4)]

            def fake_batch(**kwargs: object) -> dict[str, object]:
                rows = kwargs["batch"]
                if len(rows) > 2:  # type: ignore[arg-type]
                    raise ValueError("incomplete batch")
                role_dir = Path(kwargs["outdir"]) / "role_logs" / str(kwargs["role"])
                role_dir.mkdir(parents=True, exist_ok=True)
                parsed = [{"record_id": row["record_id"]} for row in rows]  # type: ignore[index]
                (role_dir / "batch_0001.parsed.json").write_text(
                    json.dumps(parsed), encoding="utf-8"
                )
                (role_dir / "batch_0001.response.txt").write_text("raw", encoding="utf-8")
                (role_dir / "batch_0001.meta.json").write_text('{"status":"ok"}', encoding="utf-8")
                return {"status": "ok", "batch_index": 1}

            with patch("run_codex_screening_pipeline.codex_batch", side_effect=fake_batch):
                meta = codex_batch_with_retries(
                    max_attempts=1,
                    role="adjudicator",
                    batch_index=1,
                    batch=batch,
                    outdir=outdir,
                    schema=Path("schema.json"),
                    model="gpt-5.4-mini",
                    evidence_mode="full_text_sections",
                )
            self.assertEqual(meta["status"], "ok_recovered_by_split")
            parsed = json.loads(
                (outdir / "role_logs/adjudicator/batch_0001.parsed.json").read_text()
            )
            self.assertEqual([row["record_id"] for row in parsed], ["r0", "r1", "r2", "r3"])
            self.assertTrue(
                (outdir / "role_logs/adjudicator/recovery_batch_0001_part_01.response.txt").exists()
            )

    def test_stage_inventory_detects_mutated_log_or_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            artifact = pipeline.paths.search / "result.json"
            artifact.parent.mkdir(parents=True)
            artifact.write_text('{"ok": true}\n', encoding="utf-8")
            log = pipeline.log_dir("search") / "probe.log"
            log.parent.mkdir(parents=True)
            log.write_text("stable\n", encoding="utf-8")
            pipeline.mark("search", "complete", [artifact])
            self.assertTrue(pipeline.stage_is_complete("search"))
            log.write_text("changed\n", encoding="utf-8")
            self.assertFalse(pipeline.stage_is_complete("search"))

    def test_new_manual_fulltext_file_invalidates_completed_download_stage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            manifest = pipeline.paths.download_manifest
            manifest.parent.mkdir(parents=True)
            manifest.write_text('{"results": []}\n', encoding="utf-8")
            pipeline.mark("fulltext-download", "complete", [manifest])
            self.assertTrue(pipeline.stage_is_complete("fulltext-download"))
            manual = pipeline.paths.fulltext / "manual_fulltexts.json"
            manual.write_text('{"records": []}\n', encoding="utf-8")
            self.assertFalse(pipeline.stage_is_complete("fulltext-download"))

    def test_supplemental_recall_is_a_hashed_prepare_records_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            artifact = pipeline.paths.records / "result.json"
            artifact.parent.mkdir(parents=True)
            artifact.write_text('{"records": []}\n', encoding="utf-8")
            pipeline.mark("prepare-records", "complete", [artifact])
            declaration = pipeline.paths.records / "supplemental_recall_records.json"
            declaration.write_text(
                '{"schema_version":1,"declarations":[]}\n', encoding="utf-8"
            )
            self.assertFalse(pipeline.stage_is_complete("prepare-records"))

    def test_absent_new_optional_input_preserves_legacy_stage_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            artifact = pipeline.paths.records / "result.json"
            artifact.parent.mkdir(parents=True)
            artifact.write_text('{"records": []}\n', encoding="utf-8")
            pipeline.mark("prepare-records", "complete", [artifact])
            fingerprints = pipeline.manifest["stages"]["prepare-records"][
                "human_input_fingerprints"
            ]
            pipeline.manifest["stages"]["prepare-records"]["human_input_fingerprints"] = [
                row
                for row in fingerprints
                if not row["path"].endswith("supplemental_recall_records.json")
            ]
            self.assertTrue(pipeline.stage_is_complete("prepare-records"))

    def test_release_tree_excludes_its_self_describing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "index.html").write_text("atlas", encoding="utf-8")
            (root / "data/atlas.json").write_text("{}", encoding="utf-8")
            (root / "data/deployment.json").write_text("changing", encoding="utf-8")
            first = atlas_tree_manifest(root)
            (root / "data/deployment.json").write_text("changed again", encoding="utf-8")
            second = atlas_tree_manifest(root)
            self.assertEqual(first["manifest_sha256"], second["manifest_sha256"])
            self.assertEqual(first["file_count"], 2)

    def test_release_manifest_and_remote_verifier_check_commit_tree_and_assets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            state = {
                "schema_version": 1,
                "search_end": "2026-07-06",
                "master_record_files": [],
                "taxonomy_root": str(root / "taxonomy"),
                "docling_corpus_roots": [],
                "crop_ledger": str(root / "crops.json"),
                "atlas_output": str(root / "atlas"),
                "last_run_id": "update_test",
            }
            Path(config["living_state"]).write_text(json.dumps(state), encoding="utf-8")
            atlas = Path(config["atlas_output"])
            (atlas / "data").mkdir(parents=True)
            (atlas / "index.html").write_text("atlas", encoding="utf-8")
            (atlas / "data/atlas.json").write_text(
                json.dumps(
                    {
                        "meta": {
                            "generated_from": str(root / "taxonomy"),
                            "record_count": 1,
                            "study_count": 1,
                            "model_count": 1,
                            "configuration_count": 1,
                            "route_count": 1,
                        }
                    }
                ),
                encoding="utf-8",
            )
            (atlas / "data/browser_qa.json").write_text(
                '{"status":"ok","scope":"local"}\n', encoding="utf-8"
            )
            pipeline = Pipeline(args, config)
            pipeline.manifest.setdefault("stages", {})["search"] = {
                "status": "complete",
                "finished": "2026-08-09T12:00:00+00:00",
            }
            pipeline.save_manifest()
            pipeline.args.commit = "commit-sha"
            with patch("builtins.print"):
                self.assertEqual(pipeline.release_manifest(), 0)

            class Response:
                def __init__(self, content: bytes):
                    self.content = content

                def raise_for_status(self) -> None:
                    return None

            def fake_get(url: str, **_: object) -> Response:
                requested = url.split("https://atlas.test/", 1)[1].split("?", 1)[0]
                return Response((atlas / requested).read_bytes())

            pipeline.args.url = "https://atlas.test"
            pipeline.args.expected_commit = "commit-sha"
            pipeline.args.check_assets = True
            pipeline.args.record_completion = False
            with patch("requests.get", side_effect=fake_get), patch("builtins.print"):
                self.assertEqual(pipeline.verify_live(), 0)

            search_config = pipeline.run_root / "00_search/search_config.json"
            search_config.parent.mkdir(parents=True)
            search_config.write_text('{"databases":{}}\n', encoding="utf-8")
            prisma_facts = pipeline.run_root / "16_report/prisma_update_facts.json"
            prisma_facts.parent.mkdir(parents=True)
            prisma_facts.write_text('{"raw_hits":7,"accepted_records":1}\n', encoding="utf-8")
            method_lock_path = root / "method_lock.json"
            method_lock_path.write_text('{"method_id":"test-method"}\n', encoding="utf-8")
            remote_qa = root / "remote_browser_qa.json"
            remote_qa.write_text('{"status":"ok","scope":"remote"}\n', encoding="utf-8")
            archive_receipt = root / "receipt.json"
            archive_receipt.write_text(
                '{"storage_class":"independent_backup"}\n', encoding="utf-8"
            )
            screenshots = [root / "desktop.png", root / "mobile.png"]
            for screenshot in screenshots:
                screenshot.write_bytes(b"screenshot")
            config["release_records_root"] = str(root / "releases")
            pipeline.config = config
            pipeline.args.record_completion = True
            pipeline.args.workflow_run_id = "workflow-1"
            pipeline.args.operator = "tester"
            pipeline.args.browser_qa_report = str(remote_qa)
            pipeline.args.screenshot = [str(path) for path in screenshots]
            method_status = {
                "ok": True,
                "issues": [],
                "method_id": "test-method",
                "lock_path": str(method_lock_path),
                "lock_sha256": hashlib.sha256(method_lock_path.read_bytes()).hexdigest(),
                "frozen_taxonomy_sha256": "f" * 64,
            }
            archive_status = {
                "ok": True,
                "receipt": str(archive_receipt),
                "storage_class": "independent_backup",
                "source_manifest_sha256": "a" * 64,
                "issues": [],
            }
            with (
                patch("requests.get", side_effect=fake_get),
                patch("builtins.print"),
                patch.object(pipeline, "method_lock_status", return_value=method_status),
                patch.object(pipeline, "artifact_archive_status", return_value=archive_status),
            ):
                self.assertEqual(pipeline.verify_live(), 0)
            completion = json.loads(
                (root / "releases/update_test/completion_record.json").read_text()
            )
            self.assertEqual(completion["schema_version"], 2)
            self.assertEqual(completion["method"]["method_id"], "test-method")
            self.assertEqual(
                completion["artifact_archive"]["receipt"], str(archive_receipt)
            )
            self.assertEqual(
                completion["artifact_archive"]["receipt_artifact"]["path"],
                str(archive_receipt.resolve()),
            )
            self.assertEqual(completion["prisma_counts"]["raw_hits"], 7)
            self.assertEqual(completion["catalog_counts"]["route_count"], 1)
            self.assertEqual(
                completion["search_interval"]["search_completed_at"],
                "2026-08-09T12:00:00+00:00",
            )
            self.assertEqual(
                completion["remote_browser_qa"]["path"], str(remote_qa.resolve())
            )

    def test_zero_eligible_taxonomy_classification_writes_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            pipeline.paths.accepted_records.parent.mkdir(parents=True)
            pipeline.paths.accepted_records.write_text('{"records": []}\n', encoding="utf-8")
            outputs = pipeline.stage_taxonomy_classification()
            self.assertEqual(len(outputs), 1)
            self.assertTrue(outputs[0].is_file())
            self.assertEqual(json.loads(outputs[0].read_text())["records"], 0)

    def test_stage_reruns_preserve_prior_command_logs_by_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            artifact = pipeline.paths.search / "result.json"

            def callback(label: str):
                def run() -> list[Path]:
                    pipeline.run_command(
                        "search", "probe", [sys.executable, "-c", f"print('{label}')"]
                    )
                    artifact.parent.mkdir(parents=True, exist_ok=True)
                    artifact.write_text(json.dumps({"label": label}), encoding="utf-8")
                    return [artifact]

                return run

            pipeline.execute_stage("search", callback("first"))
            pipeline.args.force = True
            pipeline.execute_stage("search", callback("second"))
            first_log = pipeline.log_dir("search") / "attempt_001/probe/stdout.log"
            second_log = pipeline.log_dir("search") / "attempt_002/probe/stdout.log"
            self.assertEqual(first_log.read_text().strip(), "first")
            self.assertEqual(second_log.read_text().strip(), "second")

    def test_partial_search_is_checkpointed_as_manual_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            template = root / "search_template.json"
            keys = root / "keys.json"
            template.write_text(
                json.dumps({"databases": {"pubmed": {"enabled": True}, "scopus": {"enabled": True}}}),
                encoding="utf-8",
            )
            keys.write_text("{}\n", encoding="utf-8")
            config.update({"search_config_template": str(template), "api_keys_file": str(keys)})
            pipeline = Pipeline(args, config)

            def fake_run(stage: str, name: str, command: list[str], *unused, **kwargs) -> None:
                if name == "build-config":
                    pipeline.paths.search_config.parent.mkdir(parents=True, exist_ok=True)
                    pipeline.paths.search_config.write_text(template.read_text(), encoding="utf-8")
                    return
                pipeline.paths.search_exports.mkdir(parents=True, exist_ok=True)
                summary = pipeline.paths.search_exports / "search_summary_2026-08-09.json"
                summary.write_text(
                    json.dumps(
                        {
                            "results_per_database": {"pubmed": 4, "scopus": 0},
                            "database_status": {
                                "pubmed": {"complete": True},
                                "scopus": {"complete": False, "reason": "missing API key"},
                            },
                            "complete": False,
                            "incomplete_databases": ["scopus"],
                        }
                    ),
                    encoding="utf-8",
                )
                raise RuntimeError("partial search")

            with patch.object(pipeline, "run_command", side_effect=fake_run):
                with self.assertRaises(ManualGate):
                    pipeline.stage_search()
            gate = json.loads(
                (pipeline.paths.search / "search_completion_gate.json").read_text()
            )
            self.assertEqual(gate["incomplete_databases"], ["scopus"])
            self.assertEqual(gate["database_status"]["scopus"]["reason"], "missing API key")

    def test_publish_requires_the_entire_hash_valid_stage_closure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            pipeline.manifest["stages"] = {"report": {"status": "complete"}}
            with self.assertRaisesRegex(RuntimeError, "stage closure"):
                pipeline.publish()

    def test_doctor_reports_missing_state_and_atlas_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            atlas_data = Path(config["atlas_output"]) / "data/atlas.json"
            atlas_data.parent.mkdir(parents=True)
            atlas_data.write_text(
                json.dumps(
                    {
                        "meta": {
                            "generated_from": "new_snapshot",
                            "record_count": 55,
                            "model_count": 117,
                            "route_count": 519,
                        }
                    }
                ),
                encoding="utf-8",
            )
            pipeline = Pipeline(args, config)
            with patch("builtins.print") as output:
                self.assertEqual(pipeline.doctor(), 2)
            payload = json.loads(output.call_args.args[0])
            self.assertEqual(
                {issue["code"] for issue in payload["issues"]},
                {"MISSING_LIVING_STATE", "ATLAS_STATE_DIVERGENCE"},
            )

    def test_repository_checkout_waives_only_matching_external_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            artifact = pipeline.paths.search / "ignored.pdf"
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"external payload")
            pipeline.mark("search", "complete", [artifact])
            expected = pipeline.manifest["stages"]["search"]["artifacts"][0]
            artifact.unlink()

            strict = pipeline.stage_validation_issues("search")
            self.assertIn(f"missing declared artifact: {expected['path']}", strict)
            with patch.object(
                pipeline,
                "repository_external_artifacts",
                return_value={expected["path"]: expected},
            ):
                omissions: list[str] = []
                self.assertEqual(
                    pipeline.stage_validation_issues(
                        "search",
                        repository_checkout=True,
                        repository_omissions=omissions,
                    ),
                    [],
                )
            self.assertEqual(set(omissions), {expected["path"]})

            wrong = {**expected, "sha256": "0" * 64}
            with patch.object(
                pipeline,
                "repository_external_artifacts",
                return_value={expected["path"]: wrong},
            ):
                issues = pipeline.stage_validation_issues("search", repository_checkout=True)
            self.assertIn(f"missing declared artifact: {expected['path']}", issues)

    def test_live_verifier_retries_an_individual_asset_connection_reset(self) -> None:
        import requests

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            args.url = "https://example.test/catalog"
            args.expected_commit = "commit-under-test"
            args.check_assets = True
            args.record_completion = False
            atlas_root = Path(config["atlas_output"])
            atlas_json = atlas_root / "data/atlas.json"
            atlas_json.parent.mkdir(parents=True)
            atlas_json.write_text(
                json.dumps(
                    {
                        "meta": {
                            "generated_from": "snapshot",
                            "record_count": 1,
                            "study_count": 1,
                            "model_count": 1,
                            "configuration_count": 1,
                            "route_count": 1,
                        }
                    }
                ),
                encoding="utf-8",
            )
            asset = atlas_root / "assets/figure.png"
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b"figure")
            tree = atlas_tree_manifest(atlas_root)
            deployment = json.dumps(
                {"commit": args.expected_commit, "atlas_tree": tree}
            ).encode()
            payloads = {
                "data/atlas.json": atlas_json.read_bytes(),
                "data/deployment.json": deployment,
                "assets/figure.png": asset.read_bytes(),
            }
            attempts: dict[str, int] = {}

            def response_for(url: str, **unused: object) -> Mock:
                path = url.split("/catalog/", 1)[1].split("?", 1)[0]
                attempts[path] = attempts.get(path, 0) + 1
                if path == "assets/figure.png" and attempts[path] == 1:
                    raise requests.ConnectionError("transient reset")
                response = Mock()
                response.content = payloads[path]
                response.raise_for_status.return_value = None
                return response

            pipeline = Pipeline(args, config)
            with patch("requests.get", side_effect=response_for), patch(
                "run_living_review_pipeline.time.sleep"
            ), patch("builtins.print"):
                self.assertEqual(pipeline.verify_live(), 0)
            self.assertEqual(attempts["assets/figure.png"], 2)

    def test_reconcile_adopts_valid_supplemental_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            args.snapshot_root = str(root / "snapshot")
            args.atlas_root = str(root / "atlas")
            args.reason = "Documented recall correction"
            supplement = root / "supplement.json"
            supplement.write_text('{"records": [{"record_id": "r3"}]}', encoding="utf-8")
            args.supplemental_record_file = [str(supplement)]
            pipeline = Pipeline(args, config)

            main_records = pipeline.paths.records / "new_records_after_cross_dedup_crossref_checked.json"
            main_records.parent.mkdir(parents=True)
            main_records.write_text('{"records": [{"record_id": "r1"}]}', encoding="utf-8")
            primary_facts = pipeline.paths.report / "prisma_update_facts.json"
            primary_facts.parent.mkdir(parents=True)
            primary_facts.write_text('{"accepted_records": 2}', encoding="utf-8")
            corpus = root / "corpus"
            corpus.mkdir()
            snapshot = Path(args.snapshot_root)
            snapshot.mkdir()
            (snapshot / "crop_ledger.json").write_text("[]", encoding="utf-8")
            counts = {"records": 55, "studies": 54, "models": 117, "configurations": 400, "routes": 519}
            (snapshot / "snapshot_manifest.json").write_text(
                json.dumps({**counts, "corpus_roots": [str(corpus)]}), encoding="utf-8"
            )
            atlas_data = Path(args.atlas_root) / "data/atlas.json"
            atlas_data.parent.mkdir(parents=True)
            atlas_data.write_text(
                json.dumps(
                    {
                        "meta": {
                            "generated_from": rel(snapshot),
                            "record_count": 55,
                            "study_count": 54,
                            "model_count": 117,
                            "configuration_count": 400,
                            "route_count": 519,
                        }
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(pipeline, "stage_is_complete", return_value=True), patch("builtins.print"):
                self.assertEqual(pipeline.reconcile(), 0)
            state = json.loads(Path(config["living_state"]).read_text())
            self.assertEqual(state["search_end"], "2026-08-09")
            self.assertEqual(state["taxonomy_root"], rel(snapshot))
            self.assertIn(rel(supplement), state["master_record_files"])
            self.assertEqual(pipeline.manifest["publication_mode"], "supplemental_recall_reconciliation")

    def test_pipeline_recovers_interrupted_atlas_publication_before_loading_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            state_path = Path(config["living_state"])
            prior_state = {
                "schema_version": 1,
                "search_end": "2026-07-06",
                "master_record_files": [],
                "taxonomy_root": config["baseline_taxonomy_root"],
                "docling_corpus_roots": [],
                "crop_ledger": config["baseline_crop_ledger"],
                "atlas_output": config["atlas_output"],
            }
            state_path.write_text(json.dumps({**prior_state, "search_end": "2026-08-09"}), encoding="utf-8")
            target = Path(config["atlas_output"])
            backup = target.with_name(target.name + ".previous")
            target.mkdir()
            backup.mkdir()
            (target / "index.html").write_text("new", encoding="utf-8")
            (backup / "index.html").write_text("old", encoding="utf-8")
            journal = Path(config["updates_root"]) / ".publish_journal.json"
            journal.parent.mkdir()
            journal.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "state_path": str(state_path),
                        "state_existed": True,
                        "prior_state": prior_state,
                        "atlas": {
                            "target": str(target), "backup": str(backup),
                            "temporary": str(target.with_name(target.name + ".next")),
                            "target_existed": True,
                        },
                    }
                ),
                encoding="utf-8",
            )
            Pipeline(args, config)
            self.assertEqual((target / "index.html").read_text(), "old")
            self.assertEqual(json.loads(state_path.read_text())["search_end"], "2026-07-06")
            self.assertFalse(journal.exists())

    def test_downstream_fulltext_files_do_not_invalidate_candidate_stage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            candidate = pipeline.paths.fulltext_candidates
            candidate.parent.mkdir(parents=True)
            candidate.write_text('{"records": []}\n', encoding="utf-8")
            pipeline.mark("fulltext-candidates", "complete", [candidate])
            pipeline.paths.download_manifest.write_text(
                '{"results": []}\n', encoding="utf-8"
            )
            self.assertTrue(pipeline.stage_is_complete("fulltext-candidates"))

    def test_taxonomy_replicates_receive_distinct_log_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            r1 = pipeline.sharded_commands(["command"], root / "r1", 2, "fixed-r1")
            dense = pipeline.sharded_commands(["command"], root / "dense", 2, "dense")
            self.assertEqual([name for name, _ in r1], ["fixed-r1-00", "fixed-r1-01"])
            self.assertEqual([name for name, _ in dense], ["dense-00", "dense-01"])

    def test_artifact_root_resolves_migrated_docling_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact_root = root / "artifact-store"
            corpus = artifact_root / "data/corpus"
            corpus.mkdir(parents=True)
            args, config = self.pipeline_args_and_config(root)
            config["artifact_roots"] = [str(artifact_root)]
            pipeline = Pipeline(args, config)

            self.assertEqual(
                pipeline.resolve_artifact("data/corpus").resolve(), corpus.resolve()
            )
            self.assertEqual(
                pipeline.resolve_artifact("/old/machine/review/data/corpus").resolve(),
                corpus.resolve(),
            )
            self.assertEqual(
                pipeline.artifact_root_arguments(),
                ["--artifact-root", str(artifact_root.resolve())],
            )

    def test_taxonomy_classification_runs_f6_semantic_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            config.update(
                {
                    "graph_workers": 1,
                    "codex_timeout_seconds": 30,
                    "taxonomy_adjudication_timeout_seconds": 30,
                    "openai_compatible_endpoint": "http://127.0.0.1:8765/v1",
                    "models": {
                        "graph": "openai/gpt-5.4-mini",
                        "crop": "gpt-5.4-mini",
                    },
                }
            )
            pipeline = Pipeline(args, config)
            baseline_taxonomy = Path(config["baseline_taxonomy_root"])
            baseline_taxonomy.mkdir(parents=True)
            (baseline_taxonomy / "taxonomy_tree.json").write_text("{}\n", encoding="utf-8")
            (baseline_taxonomy / "taxonomy_codebook.md").write_text("# v1\n", encoding="utf-8")
            pipeline.paths.accepted_records.parent.mkdir(parents=True)
            pipeline.paths.accepted_records.write_text(
                '{"records":[{"record_id":"r1"}]}\n', encoding="utf-8"
            )
            command_names = []

            def fake_run(stage: str, name: str, command: list[str], *args, **kwargs) -> None:
                command_names.append(name)
                if name == "analyze":
                    pipeline.paths.taxonomy.mkdir(parents=True, exist_ok=True)
                    (pipeline.paths.taxonomy / "route_annotations.jsonl").write_text(
                        '{"route_id":"route_1"}\n', encoding="utf-8"
                    )
                    (pipeline.paths.taxonomy / "evidence_ledger.jsonl").write_text(
                        '{"route_id":"route_1"}\n', encoding="utf-8"
                    )
                    (pipeline.paths.taxonomy / "agreement_metrics.json").write_text(
                        '{}\n', encoding="utf-8"
                    )
                    (pipeline.paths.taxonomy / "study_model_registry.csv").write_text(
                        "record_id,model_id\nr1,m1\n", encoding="utf-8"
                    )
                if name == "f6-finalize":
                    output = pipeline.paths.taxonomy / "semantic_sufficiency"
                    output.mkdir(parents=True, exist_ok=True)
                    (output / "semantic_sufficiency_action_queue.csv").write_text(
                        "record_id,route_id,recommended_action\n", encoding="utf-8"
                    )
                    (output / "semantic_sufficiency_report.json").write_text(
                        '{"status":"complete"}\n', encoding="utf-8"
                    )

            with (
                patch.object(pipeline, "docling_python", return_value=sys.executable),
                patch.object(pipeline, "run_parallel"),
                patch.object(pipeline, "run_command", side_effect=fake_run),
                patch.object(
                    pipeline, "codex_server", return_value=contextlib.nullcontext()
                ),
            ):
                outputs = pipeline.stage_taxonomy_classification()

            self.assertIn("f6-semantic_reviewer", command_names)
            self.assertIn("f6-adversarial_reviewer", command_names)
            self.assertIn("f6-adjudicate", command_names)
            self.assertIn("f6-finalize", command_names)
            self.assertIn(
                pipeline.paths.taxonomy
                / "semantic_sufficiency/semantic_sufficiency_gate.json",
                outputs,
            )
            marker = json.loads(
                (pipeline.paths.taxonomy / "authoritative_taxonomy.json").read_text()
            )
            self.assertEqual(marker["mode"], "original_classification_f6_pass")
            self.assertEqual(
                pipeline.authoritative_taxonomy_root().resolve(),
                pipeline.paths.taxonomy.resolve(),
            )

    def test_taxonomy_classification_corrects_and_revalidates_nonretain_f6_routes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            config.update(
                {
                    "graph_workers": 1,
                    "codex_timeout_seconds": 30,
                    "taxonomy_adjudication_timeout_seconds": 30,
                    "openai_compatible_endpoint": "http://127.0.0.1:8765/v1",
                    "models": {
                        "graph": "openai/gpt-5.4-mini",
                        "crop": "gpt-5.4-mini",
                    },
                }
            )
            baseline_taxonomy = Path(config["baseline_taxonomy_root"])
            baseline_taxonomy.mkdir(parents=True)
            (baseline_taxonomy / "taxonomy_tree.json").write_text("{}\n", encoding="utf-8")
            (baseline_taxonomy / "taxonomy_codebook.md").write_text("# v1\n", encoding="utf-8")
            pipeline = Pipeline(args, config)
            pipeline.paths.accepted_records.parent.mkdir(parents=True)
            pipeline.paths.accepted_records.write_text(
                '{"records":[{"record_id":"r1"}]}\n', encoding="utf-8"
            )
            command_names: list[str] = []

            def write_taxonomy(target: Path, route_payload: str) -> None:
                target.mkdir(parents=True, exist_ok=True)
                (target / "route_annotations.jsonl").write_text(
                    route_payload + "\n", encoding="utf-8"
                )
                (target / "evidence_ledger.jsonl").write_text(
                    '{"route_id":"route_1"}\n', encoding="utf-8"
                )
                (target / "study_model_registry.csv").write_text(
                    "record_id,model_id\nr1,m1\n", encoding="utf-8"
                )
                (target / "taxonomy_tree.json").write_text("{}\n", encoding="utf-8")
                (target / "taxonomy_codebook.md").write_text("# v1\n", encoding="utf-8")
                (target / "agreement_metrics.json").write_text("{}\n", encoding="utf-8")

            def fake_run(stage: str, name: str, command: list[str], *args, **kwargs) -> None:
                command_names.append(name)
                if name == "analyze":
                    write_taxonomy(
                        pipeline.paths.taxonomy,
                        '{"route_id":"route_1","carrier_family":"unclear"}',
                    )
                elif name == "f6-finalize":
                    output = pipeline.paths.taxonomy / "semantic_sufficiency"
                    output.mkdir(parents=True, exist_ok=True)
                    (output / "semantic_sufficiency_action_queue.csv").write_text(
                        "record_id,route_id,recommended_action\nr1,route_1,revise_fields\n",
                        encoding="utf-8",
                    )
                    (output / "semantic_sufficiency_report.json").write_text(
                        '{"status":"complete_with_actions"}\n', encoding="utf-8"
                    )
                elif name == "f6-apply-correction":
                    write_taxonomy(
                        pipeline.paths.taxonomy / "semantic_correction_applied",
                        '{"route_id":"route_1","carrier_family":"text_native_token_stream"}',
                    )
                elif name == "f6-revalidate-finalize":
                    output = pipeline.paths.taxonomy / "semantic_sufficiency_revalidation"
                    output.mkdir(parents=True, exist_ok=True)
                    (output / "semantic_sufficiency_action_queue.csv").write_text(
                        "record_id,route_id,recommended_action\n", encoding="utf-8"
                    )
                    (output / "semantic_sufficiency_report.json").write_text(
                        '{"status":"complete"}\n', encoding="utf-8"
                    )

            with (
                patch.object(pipeline, "docling_python", return_value=sys.executable),
                patch.object(pipeline, "run_parallel"),
                patch.object(pipeline, "run_command", side_effect=fake_run),
                patch.object(
                    pipeline, "codex_server", return_value=contextlib.nullcontext()
                ),
            ):
                pipeline.stage_taxonomy_classification()

            self.assertIn("f6-correct", command_names)
            self.assertIn("f6-apply-correction", command_names)
            self.assertIn("f6-revalidate-finalize", command_names)
            marker = json.loads(
                (pipeline.paths.taxonomy / "authoritative_taxonomy.json").read_text()
            )
            self.assertEqual(marker["mode"], "versioned_f6_semantic_correction")
            self.assertEqual(
                pipeline.authoritative_taxonomy_root().resolve(),
                (pipeline.paths.taxonomy / "semantic_correction_applied").resolve(),
            )

    def test_f7_terminalizes_exhaustive_failure_without_promoting_a_crop(self) -> None:
        dispositions = [
            {
                "model_id": "m1",
                "model_name": "Model 1",
                "status": "unresolved_replacement_required",
                "final_crop_box": {"x": 0.1, "y": 0.1, "width": 0.5, "height": 0.5},
                "route_ids_supported": ["route_1"],
            },
            {
                "model_id": "m2",
                "model_name": "Model 2",
                "status": "validated_current_crop",
                "final_crop_box": {"x": 0, "y": 0, "width": 1, "height": 1},
                "route_ids_supported": ["route_2"],
            },
        ]
        resolved, prior = terminalize_unresolved_dispositions(dispositions)
        self.assertEqual(prior[0]["status"], "unresolved_replacement_required")
        self.assertEqual(resolved[0]["status"], "crop_rejected_no_suitable_figure")
        self.assertEqual(resolved[0]["preterminal_status"], "unresolved_replacement_required")
        self.assertIsNone(resolved[0]["final_crop_box"])
        self.assertEqual(resolved[0]["route_ids_supported"], [])
        self.assertEqual(resolved[1], dispositions[1])

    def test_failed_scholar_validation_persists_run_manifest_before_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            self.assertFalse(pipeline.manifest_path.exists())
            with patch.object(
                pipeline, "ensure_search_config", side_effect=RuntimeError("probe failure")
            ):
                with self.assertRaisesRegex(RuntimeError, "probe failure"):
                    pipeline.scholar_validate()
            self.assertTrue(pipeline.manifest_path.is_file())
            persisted = json.loads(pipeline.manifest_path.read_text())
            self.assertEqual(persisted["run_id"], "update_test")

    def test_crop_validation_promotes_only_f7_validated_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            config.update(
                {
                    "crop_workers": 1,
                    "codex_timeout_seconds": 30,
                    "models": {"crop": "gpt-5.4-mini"},
                }
            )
            pipeline = Pipeline(args, config)
            pipeline.paths.accepted_records.parent.mkdir(parents=True)
            pipeline.paths.accepted_records.write_text(
                '{"records":[{"record_id":"r1"}]}\n', encoding="utf-8"
            )
            command_names = []

            def fake_run(stage: str, name: str, command: list[str], *args, **kwargs) -> None:
                command_names.append(name)
                if name == "two-selectors-adjudicator-cropper":
                    pipeline.paths.crops.mkdir(parents=True, exist_ok=True)
                    write_json = lambda path, value: path.write_text(
                        json.dumps(value) + "\n", encoding="utf-8"
                    )
                    write_json(
                        pipeline.paths.crops / "crop_ledger.json",
                        [{"model_id": "m1", "status": "no_suitable_figure"}],
                    )
                    write_json(pipeline.paths.crops / "run_summary.json", {"errors": []})
                if name == "f7-finalize":
                    output = pipeline.paths.crops / "exact_preview_validation"
                    output.mkdir(parents=True, exist_ok=True)
                    (output / "exact_preview_validation_report.json").write_text(
                        '{"status":"complete","unresolved_models":0}\n', encoding="utf-8"
                    )
                    (output / "tool_isolation_audit.json").write_text(
                        '{"status":"pass","tool_events":0}\n', encoding="utf-8"
                    )
                    (output / "proposed_crossvalidated_crop_ledger.json").write_text(
                        '[{"model_id":"m1","status":"no_suitable_figure",'
                        '"exact_preview_validation":{"status":"not_applicable_no_crop"}}]\n',
                        encoding="utf-8",
                    )

            with patch.object(pipeline, "run_command", side_effect=fake_run):
                outputs = pipeline.stage_crop_validation()

            promoted = json.loads(
                (pipeline.paths.crops / "crop_ledger.json").read_text(encoding="utf-8")
            )
            self.assertIn("f7-exact_preview_validator", command_names)
            self.assertIn("f7-input_role_validator", command_names)
            self.assertIn("f7-replacement-finalize", command_names)
            self.assertEqual(
                promoted[0]["exact_preview_validation"]["status"],
                "not_applicable_no_crop",
            )
            self.assertIn(pipeline.paths.crops / "crop_ledger.json", outputs)

    def test_accepted_html_stops_before_canonical_vlm_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args, config = self.pipeline_args_and_config(root)
            pipeline = Pipeline(args, config)
            pipeline.paths.accepted_records.parent.mkdir(parents=True)
            pipeline.paths.accepted_records.write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "record_id": "r1",
                                "candidate_id": "r1",
                                "title": "HTML-only accepted report",
                                "source_document": "article.html",
                                "source_document_kind": "html",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ManualGate):
                pipeline.stage_docling_vlm()
            self.assertTrue(
                (pipeline.paths.docling_vlm / "accepted_without_pdf.json").is_file()
            )


class SupplementalRecallTests(unittest.TestCase):
    def test_declared_record_enters_before_cumulative_dedup(self) -> None:
        declarations = validate_declaration(
            {
                "schema_version": 1,
                "declarations": [
                    {
                        "record": {
                            "title": "New AI biologist",
                            "doi": "10.1000/new",
                            "url": "https://example.test/new",
                        },
                        "reason": "Recall correction",
                        "source_url": "https://example.test/new",
                        "resolver": "operator",
                        "declared_at": "2026-08-12T00:00:00+00:00",
                    }
                ],
            }
        )
        merged, audit = merge_records(
            [{"cluster_id": "1", "title": "Existing", "doi": "10.1000/old"}],
            declarations,
        )
        self.assertEqual(len(merged), 2)
        self.assertEqual(audit[0]["disposition"], "added_before_cumulative_deduplication")
        self.assertEqual(merged[1]["supplemental_recall"]["resolver"], "operator")

    def test_existing_within_update_record_is_not_duplicated(self) -> None:
        declaration = {
            "record": {"title": "Existing", "doi": "10.1000/old"},
            "reason": "Recall correction",
            "source_url": "https://example.test/old",
            "resolver": "operator",
            "declared_at": "2026-08-12T00:00:00+00:00",
        }
        merged, audit = merge_records(
            [{"cluster_id": "1", "title": "Existing", "doi": "10.1000/old"}],
            [declaration],
        )
        self.assertEqual(len(merged), 1)
        self.assertEqual(audit[0]["disposition"], "already_present_in_within_update_cohort")


class FullCohortTaxonomyRerunTests(unittest.TestCase):
    def test_generated_commands_cover_complete_repeated_annotation_topology(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            commands = rerun_commands(
                root / "canonical.csv",
                root / "rerun",
                root / "frozen_taxonomy",
                {
                    "docling_python": ".venv-docling/bin/python",
                    "models": {"graph": "openai/gpt-5.4-mini"},
                    "openai_compatible_endpoint": "http://127.0.0.1:8765/v1",
                    "openai_compatible_port": 8765,
                    "graph_workers": 4,
                    "taxonomy_adjudication_timeout_seconds": 3600,
                },
                55,
            )
        script = "\n".join(commands)
        self.assertIn("mkdir -p", script)
        self.assertIn("/health", script)
        self.assertIn("full_cohort_open_r1", script)
        for replicate in ("r1", "r2", "r3"):
            self.assertIn(f"--replicate-id {replicate}", script)
        self.assertIn("--extraction-contract dense", script)
        self.assertIn("adjudicate_input_taxonomy.py", script)
        self.assertIn("--expected-records 55", script)


if __name__ == "__main__":
    unittest.main()
