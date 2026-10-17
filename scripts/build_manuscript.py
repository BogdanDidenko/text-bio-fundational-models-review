#!/usr/bin/env python3
"""Build the journal version of paper 1 (article and Supplementary Information) from its sources.

Sources, edited by hand:
  manuscript/review_manuscript_draft.md            the article (Markdown master)
  manuscript/supplementary_information.md          supplementary text, with placeholders for generated blocks
  manuscript/supplementary/deviations_source.csv   deviations from the protocol

Supplementary items are cited as [[S:key]]. Each item is declared once in the supplement source by a
heading "### [[S:key]] Title" under "## Supplementary Notes", "## Supplementary Tables" or
"## Supplementary Figures". Items are numbered per type in the order of their first citation: the
article first (in reading order, figure legends last), then the supplement. Every item must be cited,
and every citation must follow the word for its type ("Supplementary Table [[S:key]]").

Placeholders:
  {{build_commit}}                 commit of the sources (flagged if the sources have uncommitted changes)
  {{n:amendments}}, {{n:further_changes}}, {{n:after_results}}
                                   counts of the deviations table (article)
  {{zenodo:protocol}}, {{zenodo:materials}}
                                   DOI links of the Zenodo records (manuscript/zenodo_records.json)
  {{include:search_strategies}}    search strings as executed
  {{table:<name>}}                 a table generated from the analysis outputs
  {{figure:flow}}                  the full PRISMA 2020 flow
  {{rows:<name>}}                  number of rows of a data file
  {{datafiles}}                    list of data files with the column dictionary

Generated blocks are fenced by <!-- generated: ... --> and <!-- end generated --> comments, so that the
label census and the number check can tell typed text from generated text.

Outputs (do not edit):
  manuscript/build/manuscript.md and manuscript/build/supplementary_information.md (resolved Markdown)
  manuscript/build/supplementary_information.pdf
  manuscript/build/supplementary_numbering.csv
  manuscript/supplementary/data/*.csv and data_dictionary.csv (reader-facing data files)
  manuscript/supplementary/README.md (file index: the repository sources of every item)
  manuscript/latex/{frontmatter,keypoints,body,backmatter,biographies}.tex and manuscript/latex/main.pdf

Usage:
  python3 scripts/build_manuscript.py                      # everything
  python3 scripts/build_manuscript.py --no-supplement-pdf  # all but the PDF of the supplement

The article is built first (its bibliography numbers the references); the supplement is then built with
study labels (first author, year) and reference numbers taken from the article's bibliography.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_design_culture_synthesis import LINKED  # noqa: E402  reports of the same work

MS = ROOT / "manuscript"
MAIN_SRC = MS / "review_manuscript_draft.md"
SUPP_SRC = MS / "supplementary_information.md"
DEV_SRC = MS / "supplementary/deviations_source.csv"
BUILD = MS / "build"
DATA = MS / "supplementary/data"
INDEX = MS / "supplementary/README.md"
LATEX = MS / "latex"
SOURCE_FILES = [MAIN_SRC, SUPP_SRC, DEV_SRC, ROOT / "manuscript/zenodo_records.json", ROOT / "scripts/build_manuscript.py",
                ROOT / "scripts/build_manuscript_latex.py", LATEX / "main.tex"]

SRC = {
    "search_strategies": "analysis/prisma_search_audit_2026-10-14/search_strategies_as_executed.md",
    "search_runs": "analysis/prisma_search_audit_2026-10-14/search_runs_by_database.csv",
    "flow_md": "analysis/prisma_flow_2026-10-07/PRISMA_FLOW.md",
    "flow_facts": "analysis/prisma_flow_2026-10-07/prisma_facts.json",
    "flow_figure": "analysis/prisma_flow_2026-10-07/prisma_flow.png",
    "models": "analysis/review_synthesis_2026-10-07/charting_table_models.csv",
    "works": "analysis/design_culture_charting_2026-10-14/v11/work_level_table.csv",
    "roles": "analysis/design_culture_charting_2026-10-14/roles.json",
    "motifs": "analysis/motif_library_2026-10-14/motifs.json",
    "comparisons": "analysis/design_culture_charting_2026-10-14/v11/comparison_units_adjudicated.csv",
    "gene_budgets": "analysis/discovery_2026-10-14/gene_budget_table.csv",
    "token_budgets": "analysis/discovery_2026-10-14/token_budget_table.csv",
    "synthetic": "analysis/discovery_2026-10-14/synthetic_text_table.csv",
    "codebook": "analysis/design_taxonomy_2026-10-13/taxonomy_codebook.csv",
    "deviations": "manuscript/supplementary/deviations_source.csv",
}

# Repository sources of every supplementary item, for the file index (checked to exist).
ITEM_SOURCES = {
    "search_strings": ["analysis/prisma_search_audit_2026-10-14/search_strategies_as_executed.md", "scripts/search_config.json",
                       "scripts/search_config_update.json", "scripts/search_config_update_2026-06-10.json",
                       "scripts/search_config_update_2026-07-06.json",
                       "data/living_catalog_updates/update_2026-08-09/00_search/search_config.json"],
    "search": ["analysis/prisma_search_audit_2026-10-14/PRISMA_S_AUDIT.md",
               "analysis/prisma_search_audit_2026-10-14/gap_probe_2026-02-16_28.json",
               "analysis/prisma_search_audit_2026-10-14/gap_probe_indicative_triage.json", "scripts/probe_search_gap.py"],
    "decomposition": ["protocol/REPRESENTATION_LIBRARY_GUIDE.md", "protocol/OPERATION_PARAMETER_GLOSSARY.md",
                      "analysis/representation_block_library_2026-10-04/", "analysis/operation_decomposition_v32_2026-10-14/",
                      "analysis/operation_decomposition_v31_2026-10-12/", "scripts/operation_decomposition_v3.py",
                      "scripts/run_parameter_pass.py", "scripts/decomposition_consensus.py"],
    "motifs": ["analysis/motif_library_2026-10-14/MOTIF_LIBRARY.md", "analysis/design_taxonomy_2026-10-13/TAXONOMY_SPEC.md",
               "analysis/design_taxonomy_2026-10-13/axis_tests.json", "scripts/build_motif_library.py",
               "scripts/build_design_taxonomy.py"],
    "ai": ["protocol/llm_screening_system_guideline.md", "protocol/screening_prompt_templates/",
           "protocol/full_text_section_screening_2026-07-10.md", "protocol/data_extraction.md",
           "analysis/design_culture_charting_2026-10-14/v11/run_config.json",
           "analysis/design_culture_charting_2026-10-14/v11/agreement.json",
           "analysis/design_culture_charting_2026-10-14/v11/steward_adjudication.json",
           "scripts/run_design_culture_charting.py", "scripts/consolidate_design_culture_charting.py"],
    "coverage": ["analysis/prisma_search_audit_2026-10-14/protein_text_models_coverage_check.md",
                 "analysis/prisma_search_audit_2026-10-14/protein_text_models_coverage_check.json"],
    "deviations": ["manuscript/supplementary/deviations_source.csv", "protocol/PRISMA_protocol.md"],
    "search_runs": [SRC["search_runs"], "scripts/build_prisma_search_audit.py"],
    "exclusions": [SRC["flow_md"], SRC["flow_facts"]],
    "models": [SRC["models"]],
    "works": [SRC["works"], SRC["roles"], "scripts/build_design_culture_synthesis.py"],
    "motif_library": [SRC["motifs"], "analysis/motif_library_2026-10-14/MOTIF_LIBRARY.md"],
    "comparisons": [SRC["comparisons"], "analysis/design_culture_charting_2026-10-14/v11/review_comparisons.md"],
    "budgets": [SRC["gene_budgets"], SRC["token_budgets"]],
    "synthetic": [SRC["synthetic"], "analysis/discovery_2026-10-14/verify_synthetic_text.md"],
    "codebook": [SRC["codebook"], "analysis/design_taxonomy_2026-10-13/TAXONOMY_SPEC.md"],
    "flow": [SRC["flow_figure"], "analysis/prisma_flow_2026-10-07/prisma_flow.svg", SRC["flow_facts"]],
    "prompts": ["analysis/codex_screening_run_artifacts_20260706/prompt_templates/",
                "protocol/screening_prompt_templates/", "scripts/run_codex_screening_pipeline.py",
                "analysis/codex_screening_run_artifacts_20260706/full_runs/codex_gpt54mini_all4027_20260706/role_logs.tar.gz",
                "data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10/role_logs/",
                "data/living_catalog_updates/update_2026-08-09/04_abstract_screening/role_logs/",
                "data/living_catalog_updates/update_2026-08-09/09_fulltext_screening/role_logs/"],
    "ta_decisions": ["analysis/codex_screening_run_artifacts_20260706/full_runs/codex_gpt54mini_all4027_20260706/",
                     "analysis/codex_screening_run_artifacts_20260706/update_runs/",
                     "data/living_catalog_updates/update_2026-08-09/04_abstract_screening/",
                     "data/living_catalog_updates/update_2026-08-09/04_abstract_screening_manual_recall_xunzi_2026-08-11/"],
    "ft_decisions": ["data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10/",
                     "data/living_catalog_updates/update_2026-08-09/09_fulltext_screening/",
                     "data/living_catalog_updates/update_2026-08-09/10_eligibility/",
                     "data/living_catalog_updates/update_2026-08-09/09_fulltext_screening_manual_recall_xunzi_2026-08-11/",
                     "data/living_catalog_updates/update_2026-08-09/10_eligibility_manual_recall_xunzi_2026-08-11/"],
    "decomposition_steps": ["analysis/discovery_2026-10-14/steps.parquet", "analysis/operation_decomposition_v32_2026-10-14/",
                            "scripts/build_integrated_dataset.py"],
    "parameter_slots": ["analysis/discovery_2026-10-14/slots.parquet",
                        "analysis/operation_decomposition_v32_2026-10-14/parameter_pass/", "scripts/run_parameter_pass.py"],
    "charting_items": ["analysis/design_culture_charting_2026-10-14/v11/consensus_items.csv",
                       "analysis/design_culture_charting_2026-10-14/v11/run_1/",
                       "analysis/design_culture_charting_2026-10-14/v11/run_2/", "scripts/run_design_culture_charting.py"],
}

TYPES = {"Supplementary Notes": "Note", "Supplementary Tables": "Table", "Supplementary Figures": "Figure"}
REF = re.compile(r"\[\[S:([a-z_]+)\]\]")

# ------------------------------------------------------------------------------------- vocabularies
CULTURE = {"T": "token-native", "E": "encoder-mediated", "H": "hybrid", "C": "language-conditioned",
           "A": "alignment-only", "P": "image rendering"}
CULTURE_ORDER = "TEHCA"
DESIGN = {"controlled": "controlled ablation within one system",
          "same_backbone": "same backbone given the data as text", "between": "different systems"}
OPPONENT = {"prompted_general_llm": "prompted general LLM", "external_embedding": "external frozen embedding",
            "external_pretrained": "external pretrained model", "trained_baseline": "trained baseline",
            "trained_ablation": "trained ablation", "numeric_vectors": "representation compared without a model"}
TASK = {"categorical": "categorical", "text_generation": "text generation", "embedding_quality": "embedding quality",
        "generation_quantitative": "quantitative generation", "sequence_level": "sequence-level",
        "spatial_quantitative": "spatial", "generation_other": "other generation", "multi_task": "multi-task"}
T_ARM = {"names": "gene or feature names", "letters": "sequence letters", "knowledge_text": "knowledge text",
         "numbers": "numbers written as text", "names+letters": "names and sequence letters"}
SYNTH_CATEGORY = {"content": "training or evaluation content", "templates_only": "instruction templates only",
                  "unclear": "unclear"}
SYNTH_SOURCE = {"keyword pre-screen, confirmed in charting": "keyword pre-screen, confirmed by the targeted charting pass",
                "charting v1.1 (added)": "added by the targeted charting pass"}
DB = {"pubmed": "PubMed", "scopus": "Scopus", "openalex": "OpenAlex", "semantic_scholar": "Semantic Scholar",
      "arxiv": "arXiv", "biorxiv_medrxiv": "bioRxiv and medRxiv (Europe PMC preprints)",
      "springernature": "Springer Nature", "google_scholar": "Google Scholar"}
ARCHETYPE = {"TEXT": "text only (no biological input)", "VERB": "verbalised text in the token stream",
             "SYMB": "biological alphabet in the token stream", "SOFT": "encoded soft tokens",
             "XATT": "attention bridge", "COND": "generator conditioning", "ALIGN": "shared latent alignment",
             "TOOL": "retrieval or tool context", "UNRES": "interface not resolvable from the charting",
             "OTHER_TOK": "other token-stream input (embedded or perceptual carrier)"}
A1 = {"text_source": "text source (no biological input)"}
ROLE = {"B": "biological input", "T": "text input", "X": "joining biological and text inputs"}
OPERATION = {"LM": "learned module", "NOCAT": "computation outside the library", "serialize": "serialise",
             "tokenize": "tokenise", "normalize": "normalise", "lookup": "table lookup", "project": "learned projection",
             "log_transform": "log transform"}
DATE_STATUS = {"in_range_database_filter": "within the window (database filter)",
               "in_range": "within the window (exact-date check)",
               "unknown_missing": "without a publication date (kept)",
               "unknown_year_only": "with a publication year only (kept)"}


def words(code: str) -> str:
    return code.replace("_", " ") if code else code


def words_list(text: str, sep: str = ";") -> str:
    return "; ".join(words(p.strip()) for p in text.split(sep) if p.strip())


def yes(value) -> str:
    return {"True": "yes", "False": "no", True: "yes", False: "no"}[value]


def pct(value: str) -> str:
    return f"{round(100 * float(value))}%" if value not in ("", None) else "—"


def thousands(value: str) -> str:
    return f"{int(float(value)):,}" if value not in ("", None) else ""


def read_csv(rel: str) -> list[dict]:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def md_table(header: list[str], rows: list[list], widths: list[int], right: set[int] = frozenset()) -> str:
    def cell(value) -> str:
        # a zero-width space after underscores lets long identifiers (model names) wrap in narrow columns
        return re.sub(r"_(?=\w)", "_\u200b", str(value)).replace("|", "\\|").replace("\n", " ").strip()
    rule = "|" + "|".join(("-" * w + ":") if i in right else "-" * (w + 1) for i, w in enumerate(widths)) + "|"
    lines = ["| " + " | ".join(header) + " |", rule]
    lines += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def generated(name: str, sources: list[str], body: str) -> str:
    return f"<!-- generated: {name} from {', '.join(sources)} -->\n\n{body}\n\n<!-- end generated -->"


# --------------------------------------------------------------------------------------- data files
DATAFILES: list[dict] = []


def datafile(name: str, key: str, contents: str, columns: list[tuple[str, str]], rows: list[dict]) -> None:
    names = [c for c, _ in columns]
    for r in rows:
        if set(r) != set(names):
            raise SystemExit(f"{name}: row columns {sorted(set(r) ^ set(names))} do not match the dictionary")
    DATAFILES.append({"name": name, "key": key, "contents": contents, "columns": columns, "rows": rows})


def in_item_order(num: dict[str, str], items: dict[str, dict]) -> list[dict]:
    return sorted(DATAFILES, key=lambda f: ("NoteTableFigure".index(items[f["key"]]["type"]), int(num[f["key"]][1:])))


def write_datafiles(num: dict[str, str], items: dict[str, dict]) -> None:
    if DATA.exists():
        shutil.rmtree(DATA)
    DATA.mkdir(parents=True)
    dictionary = []
    for f in in_item_order(num, items):
        rows = [{c: REF.sub(lambda m: num[m[1]], v) if isinstance(v, str) else v for c, v in r.items()}
                for r in f["rows"]]
        with open(DATA / f["name"], "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=[c for c, _ in f["columns"]], lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        dictionary += [{"file": f["name"], "column": c, "description": d} for c, d in f["columns"]]
    with open(DATA / "data_dictionary.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "column", "description"], lineterminator="\n")
        w.writeheader()
        w.writerows(dictionary)


def datafiles_block(num: dict[str, str], items: dict[str, dict]) -> str:
    ordered = in_item_order(num, items)
    rows = [[f["name"], f"Supplementary {items[f['key']]['type']} {num[f['key']]}", f["contents"], len(f["rows"])]
            for f in ordered]
    files = md_table(["File", "Item", "Contents", "Rows"], rows, [20, 24, 56, 6], right={3})
    dic = md_table(["File", "Column", "Description"],
                   [[f["name"], c, d] for f in ordered for c, d in f["columns"]], [22, 26, 70])
    return ("The data files are comma-separated, UTF-8 encoded and use plain-language values. "
            "The coded originals from which they are built are kept in the project repository "
            "(see Data and code availability).\n\n" + files +
            "\n\n**Column dictionary** (also provided as data_dictionary.csv).\n\n" + dic)


# ---------------------------------------------------------------------------------- shared lookups
ROLES = json.loads((ROOT / SRC["roles"]).read_text(encoding="utf-8"))
MODELS = read_csv(SRC["models"])
PAPER = {}
for _m in MODELS:
    PAPER.setdefault(_m["record_id"], {"title": _m["paper_title"], "doi": _m["doi"], "year": _m["year"]})


def work_of(record: str) -> str:
    return LINKED.get(record, record)


WORK_RECORDS: dict[str, list[str]] = {}
for _r in ROLES:
    WORK_RECORDS.setdefault(work_of(_r), []).append(_r)


def proposed(work: str) -> str:
    names: list[str] = []
    for r in WORK_RECORDS[work]:
        for m in ROLES[r]:
            if m["role"] == "proposed" and m["model_name"] not in names:
                names.append(m["model_name"])
    return "; ".join(names)


def work_years(work: str) -> str:
    return "; ".join(sorted({PAPER[r]["year"] for r in WORK_RECORDS[work]}))


# Study labels (first author, year) and reference numbers, read from the article's bibliography after
# the LaTeX build, so that supplementary tables point to the article's reference list.
STUDY: dict[str, dict] = {}


def study_labels() -> dict[str, dict]:
    keys = dict(re.findall(r'"([a-z_0-9-]+__[a-z_0-9]+)": "([a-z0-9_]+)"',
                           (ROOT / "scripts/build_manuscript_references.py").read_text(encoding="utf-8")))
    numbers = {k: int(n) for k, n in re.findall(r"\\bibcite\{([^}]+)\}\{\{(\d+)\}", (LATEX / "main.aux").read_text())}
    bbl = (LATEX / "main.bbl").read_text(encoding="utf-8")
    labels = {}
    for entry in re.split(r"\\bibitem\{", bbl)[1:]:
        key, rest = entry.split("}", 1)
        text = " ".join(rest.replace("\\newblock", " ").split()).replace("~", " ")
        m = re.match(r"(.+?(?:et al\.|[A-Z]{1,4}\.))\s", text + " ")
        if not m:
            raise SystemExit(f"cannot read the authors of {key}: {text}")
        authors = [a.strip() for a in m[1].rstrip(".").split(",")]
        many = authors[-1] == "et al"
        surnames = [re.sub(r"\s+[A-Z]{1,4}$", "", a) for a in authors if a != "et al"]
        year = re.search(r"[.;]\s(20\d\d|19\d\d)\b", text[m.end() - 1:])
        if many or len(surnames) > 2:
            who = f"{surnames[0]} et al."
        else:
            who = " and ".join(surnames)
        labels[key] = f"{who} {year[1] if year else ''}".strip()
    out = {}
    for record, key in keys.items():
        if key not in numbers or key not in labels:
            raise SystemExit(f"included record {record} ({key}) is not cited in the article")
        out[record] = {"label": labels[key], "number": numbers[key]}
    return out


def study(records: list[str], numbered: bool = True) -> str:
    if not STUDY:
        return ""
    ordered = sorted(records, key=lambda r: STUDY[r]["number"])
    return "; ".join(STUDY[r]["label"] + (f" [{STUDY[r]['number']}]" if numbered else "") for r in ordered)


def study_number(records: list[str]) -> int:
    return min(STUDY[r]["number"] for r in records) if STUDY else 0


# ------------------------------------------------------------------------------- generated blocks
def include_search_strategies() -> str:
    text = (ROOT / SRC["search_strategies"]).read_text(encoding="utf-8")
    out, in_code = [], False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            out.append("```")
            continue
        if in_code:
            out.append(line)
            continue
        if line.startswith("# ") or line.startswith("Config:"):
            continue  # title of the generated file; repository paths (listed in the file index)
        m = re.match(r"## Round (\d+) (.+?)(?: \(v([\d.]+)\))?: (\S+) to (\S+)$", line)
        if m:
            version = f" (protocol version {m[3]})" if m[3] else ""
            out.append(f"#### Round {m[1]}, {m[2]}{version}: {m[4]} to {m[5]}")
            continue
        m = re.match(r"### (\w+) \(executed (\S+); retained (\d+)\)$", line)
        if m:
            out.append(f"##### {DB[m[1]]} (executed {m[2]}; {thousands(m[3])} records retained)")
            continue
        if line.startswith("Round notes:"):
            note = line[len("Round notes:"):].strip()
            for a, b in ((r"\bS2\b", "Semantic Scholar"), (r"\bGS\b", "Google Scholar"),
                         (r"retries due transient NCBI 500s", "retries after transient NCBI server errors (HTTP 500)"),
                         (r"\((\d{3})\)", r"(HTTP \1)")):
                note = re.sub(a, b, note)
            out.append("Notes logged with the round: " + note)
            continue
        if line.startswith("Date status by database:"):
            status = json.loads(re.search(r"`(\{.*\})`", line).group(1))
            parts, removed = [], 0
            for db, s in status.items():
                counts = ", ".join(f"{thousands(n)} {DATE_STATUS[k]}" for k, n in s["retained_status_counts"].items())
                parts.append(f"{DB[db]}: {counts}")
                removed += s["excluded_out_of_range"]
            out.append("Date status of the retained records. " + "; ".join(parts) +
                       f". Records removed as outside the window: {removed}.")
            continue
        out.append(line)
    return generated("include:search_strategies", [SRC["search_strategies"]], "\n".join(out).strip())


def table_search_runs() -> str:
    rows = read_csv(SRC["search_runs"])
    data, printed = [], []
    for r in rows:
        rnd = re.sub(r"\(v([\d.]+)\)", r"(protocol version \1)", r["round"])
        searched = r["searched"] == "yes"
        data.append({"round": rnd, "window_start": r["window_from"], "window_end": r["window_to"],
                     "source": DB[r["database"]], "searched": r["searched"], "executed_on": r["executed"],
                     "interface": r["interface"], "date_limit_as_executed": r["date_restriction_as_executed"],
                     "other_limits_as_executed": r["other_limits_as_executed"], "hits_reported": r["api_total"],
                     "records_fetched": r["fetched"], "records_before_validation": r["raw_before_validation"],
                     "count_in_run_log": r["summary_count"], "records_retained": r["retained"],
                     "export_file": r["export_file"]})
        printed.append([rnd, DB[r["database"]], r["executed"] if searched else "not searched",
                        r["date_restriction_as_executed"], r["other_limits_as_executed"],
                        thousands(r["api_total"]), thousands(r["retained"])])
    datafile("search_runs.csv", "search_runs", "Search runs by round and source, with limits and counts as executed", [
        ("round", "Search round: number, name and the protocol version under which it ran"),
        ("window_start", "First publication date of the round's search window (ISO date)"),
        ("window_end", "Last publication date of the round's search window (ISO date)"),
        ("source", "Bibliographic source"),
        ("searched", "Whether the source was searched in this round (yes or no)"),
        ("executed_on", "Date on which the search was executed (ISO date)"),
        ("interface", "Interface through which the source was queried"),
        ("date_limit_as_executed", "Date restriction as executed, in the syntax of the source"),
        ("other_limits_as_executed", "Other limits as executed (language, access, categories, validation)"),
        ("hits_reported", "Total number of results reported in the export metadata, where the interface reports one"),
        ("records_fetched", "Number of records fetched, as recorded in the export metadata"),
        ("records_before_validation", "Records in the raw export before filtering after retrieval (for Springer "
                                      "Nature, the check that a term of each concept block is in the title or abstract)"),
        ("count_in_run_log", "Count for the source in the search summary file of the round"),
        ("records_retained", "Records in the export file of the run, passed to deduplication"),
        ("export_file", "Repository path of the export file of the run"),
    ], data)
    return generated("table:search_runs", [SRC["search_runs"]], md_table(
        ["Round", "Source", "Executed", "Date limit as executed", "Other limits as executed", "Hits reported",
         "Retained"], printed, [16, 16, 10, 26, 26, 8, 8], right={5, 6}))


def table_exclusions() -> str:
    text = (ROOT / SRC["flow_md"]).read_text(encoding="utf-8")
    facts = json.loads((ROOT / SRC["flow_facts"]).read_text(encoding="utf-8"))
    sec = text.split("## Full-text exclusion reasons", 1)[1]
    rows = []
    for line in sec.split("\n"):
        m = re.match(r"\| (.+?) \| `([^`]+)` \| ([\d,]+) \|$", line)
        if m:
            n = int(m[3].replace(",", ""))
            if facts["exclusion_reasons"][m[2]] != n:
                raise SystemExit(f"exclusion count mismatch for {m[2]}")
            rows.append({"reason": m[1], "reports": n})
        elif rows and not line.startswith("|"):
            break
    if sum(r["reports"] for r in rows) != facts["excluded_fulltext"] or len(rows) != len(facts["exclusion_reasons"]):
        raise SystemExit("exclusion reasons do not add up to the full-text exclusions")
    datafile("fulltext_exclusions.csv", "exclusions", "Reports excluded at full text, by reason", [
        ("reason", "Main reason for exclusion at full text"),
        ("reports", "Number of reports excluded for this reason"),
    ], rows)
    printed = [[r["reason"], r["reports"]] for r in rows] + [["Total", facts["excluded_fulltext"]]]
    return generated("table:exclusions", [SRC["flow_md"], SRC["flow_facts"]],
                     md_table(["Reason", "Reports"], printed, [60, 8], right={1}))


def data_models() -> None:
    rows = [{"model": m["model_name"], "study": study([m["record_id"]], numbered=False), "record_id": m["record_id"],
             "paper_title": m["paper_title"], "doi": m["doi"],
             "year": m["year"], "year_basis": m["year_basis"], "routes": m["routes"],
             "configurations": m["configurations"], "input_carrier_families": m["input_families"],
             "primary_carrier_subtype": words(m["primary_subtype"]),
             "fusion_topologies": words_list(m["fusion_topologies"]), "text_roles": words_list(m["text_roles"]),
             "lifecycle_phases": words_list(m["lifecycle_phases"]), "biological_and_text_modalities": m["modalities"]}
            for m in MODELS]
    datafile("charted_models.csv", "models", "Charted models with their records, routes and input labels", [
        ("model", "Model name as charted"),
        ("study", "First author and year of the record, as in the article's reference list"),
        ("record_id", "Identifier of the included record in the review database"),
        ("paper_title", "Title of the record"),
        ("doi", "DOI of the record"),
        ("year", "Publication year"),
        ("year_basis", "Source of the publication year"),
        ("routes", "Number of charted input routes of the model"),
        ("configurations", "Number of charted configurations (training or use settings) of the model"),
        ("input_carrier_families", "Families of the carriers through which inputs reach the model"),
        ("primary_carrier_subtype", "Most frequent carrier subtype among the model's routes"),
        ("fusion_topologies", "How the inputs are fused with the language model, over all routes"),
        ("text_roles", "Roles of text on the model's routes"),
        ("lifecycle_phases", "Lifecycle phases covered by the routes (pretraining, fine-tuning, inference, evaluation)"),
        ("biological_and_text_modalities", "Modalities that enter the model"),
    ], rows)


def table_works() -> str:
    rows = read_csv(SRC["works"])
    data, printed = [], []
    for w in rows:
        if w["work"] not in WORK_RECORDS:
            raise SystemExit(f"work without records: {w['work']}")
        records = WORK_RECORDS[w["work"]]
        training = [label for col, label in (("llm_frozen", "frozen"), ("llm_lora_or_adapter", "LoRA or adapter"),
                                             ("llm_full_finetune", "full fine-tuning"),
                                             ("llm_trained_from_scratch", "trained from scratch")) if w[col] == "True"]
        data.append({
            "study": study(records, numbered=False), "proposed_models": proposed(w["work"]),
            "record_ids": "; ".join(records),
            "paper_titles": "; ".join(PAPER[r]["title"] for r in records),
            "dois": "; ".join(PAPER[r]["doi"] for r in records), "year": work_years(w["work"]),
            "design_culture": CULTURE[w["culture"]], "tests_dependence_on_biological_input": yes(w["dependence_test"]),
            "uses_llm_written_text": yes(w["llm_written_text"]), "language_model_frozen": yes(w["llm_frozen"]),
            "language_model_lora_or_adapter": yes(w["llm_lora_or_adapter"]),
            "language_model_full_fine_tuning": yes(w["llm_full_finetune"]),
            "language_model_trained_from_scratch": yes(w["llm_trained_from_scratch"]),
            "rationale_unchanged_architecture": yes(w["rationale_T_no_architecture_change_for_own"]),
            "rationale_language_model_knowledge": yes(w["rationale_T_leverage_llm_knowledge_for_own"]),
            "rationale_concedes_information_loss": yes(w["rationale_T_concedes_information_loss"]),
            "rationale_criticises_text_rendering": yes(w["rationale_E_criticises_text_fidelity"]),
            "cross_culture_comparison_units": w["cross_culture_units"],
            "opaque_step_share": w["opaque_step_share"], "unstated_parameter_slot_share": w["unstated_slot_share"],
            "parameter_slots": w["n_slots"]})
        printed.append((CULTURE_ORDER.index(w["culture"]), study_number(records), [
            study(records), proposed(w["work"]), CULTURE[w["culture"]], yes(w["dependence_test"]),
            yes(w["llm_written_text"]), ", ".join(training) or "none recorded", w["cross_culture_units"],
            pct(w["opaque_step_share"]), pct(w["unstated_slot_share"])]))
    datafile("included_works.csv", "works", "Included works with their design culture and charted variables", [
        ("study", "First author and year of each of the work's records, as in the article's reference list"),
        ("proposed_models", "Models proposed by the work, as charted"),
        ("record_ids", "Identifiers of the work's records in the review database (two for works with two reports)"),
        ("paper_titles", "Titles of the work's records"),
        ("dois", "DOIs of the work's records"),
        ("year", "Publication year of the work's records"),
        ("design_culture", "Design culture of the work: token-native, encoder-mediated, hybrid, language-conditioned "
                           "or alignment-only"),
        ("tests_dependence_on_biological_input", "Whether the work reports any test of whether outputs depend on the "
                                                 "biological input (removal, mismatch or shuffling, random input, a "
                                                 "no-biology baseline, content perturbation, order or value ablation)"),
        ("uses_llm_written_text", "Whether text written by an LLM was used for training or evaluation"),
        ("language_model_frozen", "Whether the language model is kept frozen in at least one setting"),
        ("language_model_lora_or_adapter", "Whether the language model is adapted by low-rank adaptation (LoRA) or "
                                           "adapters"),
        ("language_model_full_fine_tuning", "Whether the language model is fine-tuned in full"),
        ("language_model_trained_from_scratch", "Whether the language model is trained from scratch"),
        ("rationale_unchanged_architecture", "Token-native work justifies its own representation by needing no change "
                                             "to the language model's architecture"),
        ("rationale_language_model_knowledge", "Token-native work justifies its own representation by the language "
                                               "model's prior knowledge of named entities"),
        ("rationale_concedes_information_loss", "Token-native work concedes loss of quantitative or fine-grained "
                                                "information in its own representation"),
        ("rationale_criticises_text_rendering", "Encoder-mediated work criticises text rendering for losing "
                                                "magnitudes, low-abundance genes or structure"),
        ("cross_culture_comparison_units", "Number of the work's comparison units between arms of different cultures"),
        ("opaque_step_share", "Median share of the steps of the work's biological routes that are learned modules left "
                              "unexpanded (empty if no biological route was decomposed)"),
        ("unstated_parameter_slot_share", "Share of the parameter slots of the work's proposed and component models "
                                          "whose value is not stated in the paper (empty if there are no slots)"),
        ("parameter_slots", "Number of parameter slots of the work's proposed and component models"),
    ], data)
    body = md_table(["Study", "Proposed models", "Culture", "Dependence test", "LLM-written text",
                     "Language-model adaptation", "Cross-culture units", "Opaque steps", "Unstated slots"],
                    [p for _, _, p in sorted(printed, key=lambda t: (t[0], t[1]))],
                    [20, 22, 13, 11, 10, 15, 9, 8, 8], right={6, 7, 8})
    return generated("table:works", [SRC["works"], SRC["roles"], SRC["models"]], body)


def operations(template: list[str]) -> tuple[str, str]:
    roles = {t.split(":", 1)[0] for t in template}
    ops = [OPERATION.get(t.split(":", 1)[1], words(t.split(":", 1)[1])) for t in template]
    if len(roles) == 1:
        return " → ".join(ops), ROLE[roles.pop()]
    return " → ".join(f"{op} ({ROLE[t.split(':', 1)[0]]})" for op, t in zip(ops, template)), "mixed"


def table_motifs() -> str:
    lib = json.loads((ROOT / SRC["motifs"]).read_text(encoding="utf-8"))
    data, printed = [], []
    for m in lib["motifs"]:
        ops, role = operations(m["template"])
        ex = m["example"]
        steps = " | ".join(f"{OPERATION.get(s['token'].split(':', 1)[1], words(s['token'].split(':', 1)[1]))}: "
                           f"{s['chain_element']}" for s in ex["steps"])
        unstated = "; ".join(f"{words(k.replace('.', ' '))} {round(100 * v)}%"
                             for k, v in m["unstated_parameter_share"].items())
        data.append({"motif": m["name"], "family": m["category"], "operations": ops, "input_role": role,
                     "contiguous": yes(m["contiguous"]), "papers": m["papers"], "models": m["models"],
                     "pilot_papers": m["pilot_papers"], "description": m["description"],
                     "unstated_parameter_shares": unstated, "example_model": ex["model_name"],
                     "example_record_id": ex["record_id"], "example_route_id": ex["route_id"],
                     "example_steps": steps, "example_evidence": ex.get("evidence_quote", "")})
        printed.append([m["name"], m["category"], ops, role, "yes" if m["contiguous"] else "no", m["papers"],
                        m["models"], m["description"]])
    datafile("motif_library.csv", "motif_library", "Motif library: recurring operation sub-chains with an example each", [
        ("motif", "Name of the motif"),
        ("family", "Family of the motif: carrier formation, encoding or joining"),
        ("operations", "Library operations of the motif, in order"),
        ("input_role", "Role of the inputs of the operations: biological input, text input, or joining both"),
        ("contiguous", "Whether the operations must be adjacent (yes) or may have other operations between them (no)"),
        ("papers", "Number of papers with the motif"),
        ("models", "Number of models with the motif"),
        ("pilot_papers", "Number of the four author-curated pilot papers with the motif"),
        ("description", "What the motif does"),
        ("unstated_parameter_shares", "For each parameter of the motif's operations, the share of calls whose value "
                                      "the paper does not state"),
        ("example_model", "Model of the example"),
        ("example_record_id", "Record of the example in the review database"),
        ("example_route_id", "Charted route of the example"),
        ("example_steps", "Steps of the example: operation and the charted wording of the step"),
        ("example_evidence", "Verbatim quote from the paper supporting the example"),
    ], data)
    return generated("table:motifs", [SRC["motifs"]], md_table(
        ["Motif", "Family", "Operations", "Input", "Contiguous", "Papers", "Models", "Description"], printed,
        [18, 12, 22, 12, 8, 6, 6, 40], right={5, 6}))


def table_comparisons() -> str:
    rows = read_csv(SRC["comparisons"])
    data, printed = [], []
    for u in rows:
        work = work_of(u["work"])
        data.append({"unit": u["unit"], "study": study(WORK_RECORDS[work], numbered=False),
                     "proposed_models": proposed(work), "record_id": u["work"],
                     "task_family": TASK[u["task_family"]], "task": u["task"], "design": DESIGN[u["design"]],
                     "arm_a": CULTURE[u["armA"]], "arm_b": CULTURE[u["armB"]], "proposed_arm": CULTURE[u["proposed"]],
                     "opponent_arm": CULTURE[u["opponent_side"]], "opponent_obtained_as": OPPONENT[u["opponent"]],
                     "winner": CULTURE.get(u["winner"], u["winner"]), "proposed_arm_won": yes(u["proposed_wins"]),
                     "token_native_arm_content": T_ARM[u["t_arm_content"]], "values_reported": u["numbers"],
                     "adjudication_note": u["recode_note"], "charting_items": u["refs"]})
        printed.append([study(WORK_RECORDS[work]), TASK[u["task_family"]], u["task"], DESIGN[u["design"]],
                        CULTURE[u["proposed"]], f"{CULTURE[u['opponent_side']]} ({OPPONENT[u['opponent']]})",
                        CULTURE.get(u["winner"], u["winner"]), u["numbers"] or "—"])
    datafile("comparison_units.csv", "comparisons", "Cross-culture comparison units after adjudication", [
        ("unit", "Identifier of the comparison unit"),
        ("study", "First author and year of the work's records, as in the article's reference list"),
        ("proposed_models", "Models proposed by the work that reports the comparison"),
        ("record_id", "Record of the work in the review database"),
        ("task_family", "Family of the task compared"),
        ("task", "Task and arms, as adjudicated"),
        ("design", "Design of the comparison: controlled ablation within one system, same backbone given the data "
                   "as text, or different systems"),
        ("arm_a", "Culture of the first arm (image rendering: DNA drawn as an image)"),
        ("arm_b", "Culture of the second arm"),
        ("proposed_arm", "Culture of the arm proposed by the authors"),
        ("opponent_arm", "Culture of the opponent arm"),
        ("opponent_obtained_as", "How the opponent arm was obtained"),
        ("winner", "Culture of the winning arm, or mixed"),
        ("proposed_arm_won", "Whether the proposed arm won"),
        ("token_native_arm_content", "What the token-native arm writes into the token stream"),
        ("values_reported", "Values reported for the comparison, as quoted in the charting (empty if none in the text)"),
        ("adjudication_note", "Note on a change made at adjudication"),
        ("charting_items", "Charting items merged into the unit (run and item number)"),
    ], data)
    return generated("table:comparisons", [SRC["comparisons"]], md_table(
        ["Study", "Task family", "Task", "Design", "Proposed arm", "Opponent arm (obtained as)",
         "Winner", "Values reported"], printed, [19, 11, 24, 13, 10, 17, 10, 17]))


def table_budgets() -> str:
    genes = read_csv(SRC["gene_budgets"])
    tokens = read_csv(SRC["token_budgets"])
    gdata = [{"study": study([g["record_id"]], numbered=False), "model_and_context": g["context"],
              "record_id": g["record_id"], "route": g["route_kind"],
              "genes_kept": str(int(float(g["genes_kept"]))) if g["genes_kept"] else "not stated",
              "values_kept": g["values_kept"], "evidence": g["quote"]} for g in genes]
    tdata = [{"study": study([t["record_id"]], numbered=False), "model": t["model"], "record_id": t["record_id"],
              "unit": t["unit"], "number": t["tokens"], "evidence": t["quote"]} for t in tokens]
    datafile("gene_budgets.csv", "budgets", "Genes or features kept per cell or object, as stated in the papers", [
        ("study", "First author and year of the record, as in the article's reference list"),
        ("model_and_context", "Model and the setting in which the budget applies"),
        ("record_id", "Record in the review database"),
        ("route", "Kind of input route: text or embedding, and whose input it is"),
        ("genes_kept", "Number of genes or features kept per cell or object"),
        ("values_kept", "Whether measured values are kept, and how"),
        ("evidence", "Verbatim quote from the paper"),
    ], gdata)
    datafile("token_budgets.csv", "budgets", "Vectors, codes or text tokens per object passed to the language model", [
        ("study", "First author and year of the record, as in the article's reference list"),
        ("model", "Model and, where needed, the setting"),
        ("record_id", "Record in the review database"),
        ("unit", "What is counted, in the paper's terms"),
        ("number", "Number per cell, profile or object"),
        ("evidence", "Verbatim quote from the paper"),
    ], tdata)
    a = md_table(["Study", "Model and setting", "Route", "Genes kept", "Values kept", "Evidence"],
                 [[study([g["record_id"]]), g["model_and_context"], g["route"], g["genes_kept"], g["values_kept"],
                   g["evidence"]] for g in gdata], [15, 15, 13, 7, 12, 44], right={3})
    b = md_table(["Study", "Model", "What is counted", "Number", "Evidence"],
                 [[study([t["record_id"]]), t["model"], t["unit"], t["number"], t["evidence"]] for t in tdata],
                 [15, 13, 20, 7, 50], right={3})
    return generated("table:budgets", [SRC["gene_budgets"], SRC["token_budgets"]],
                     "**(a) Genes or features kept per cell or object.**\n\n" + a +
                     "\n\n**(b) Vectors, codes or text tokens per object.**\n\n" + b)


def table_synthetic() -> str:
    rows = read_csv(SRC["synthetic"])
    data, printed = [], []
    for s in rows:
        work = s["work"]
        if work not in WORK_RECORDS:
            raise SystemExit(f"unknown work in synthetic-text table: {work}")
        data.append({"study": study(WORK_RECORDS[work], numbered=False), "proposed_models": proposed(work),
                     "record_ids": "; ".join(WORK_RECORDS[work]),
                     "design_culture": CULTURE[s["culture"]], "year": s["year"],
                     "what_was_written": SYNTH_CATEGORY[s["category"]], "generators": s["generators"],
                     "human_check": yes(s["human_check"]), "reasoning_traces": yes(s["reasoning_traces"]),
                     "llm_text_in_evaluation": yes(s["llm_text_in_evaluation"]), "example": s["example_quote"],
                     "how_found": SYNTH_SOURCE[s["source"]]})
        printed.append((CULTURE_ORDER.index(s["culture"]), study_number(WORK_RECORDS[work]), [
            study(WORK_RECORDS[work]), CULTURE[s["culture"]], SYNTH_CATEGORY[s["category"]], s["generators"],
            yes(s["human_check"]), yes(s["reasoning_traces"]), yes(s["llm_text_in_evaluation"]), s["example_quote"]]))
    datafile("llm_written_text.csv", "synthetic", "Works that used text written by LLMs for training or evaluation", [
        ("study", "First author and year of the work's records, as in the article's reference list"),
        ("proposed_models", "Models proposed by the work"),
        ("record_ids", "Records of the work in the review database"),
        ("design_culture", "Design culture of the work"),
        ("year", "Publication year"),
        ("what_was_written", "What the LLM wrote: training or evaluation content, instruction templates only, or unclear"),
        ("generators", "LLMs that wrote the text, as named in the paper"),
        ("human_check", "Whether the paper reports a human check of the generated text"),
        ("reasoning_traces", "Whether the generated text includes reasoning traces"),
        ("llm_text_in_evaluation", "Whether LLM-written text is used in the evaluation"),
        ("example", "Verbatim quote from the paper"),
        ("how_found", "How the use was identified"),
    ], data)
    return generated("table:synthetic", [SRC["synthetic"]], md_table(
        ["Study", "Culture", "What was written", "Generators", "Human check", "Reasoning traces",
         "Used in evaluation", "Example"], [p for _, _, p in sorted(printed, key=lambda t: (t[0], t[1]))],
        [16, 11, 11, 12, 7, 10, 10, 36]))


def data_codebook() -> None:
    rows = read_csv(SRC["codebook"])
    data = [{"record_id": r["record_id"], "model_id": r["model_id"], "model": r["model_name"],
             "configuration_id": r["configuration_id"], "route_id": r["route_id"], "route_label": r["route_label"],
             "lifecycle_phase": words(r["lifecycle_phase"]), "source_modality": r["source_modality"],
             "carrier_family": words(r["carrier_family"]), "carrier_subtype": words(r["carrier_subtype"]),
             "fusion_topology": words(r["fusion_topology"]), "text_role": words(r["text_role"]),
             "operation_chain": " → ".join(OPERATION.get(op.strip(), words(op.strip()))
                                           for op in r["operation_chain"].split("|") if op.strip()),
             "carrier_formation": A1.get(r["A1_carrier_formation"], words(r["A1_carrier_formation"])),
             "carrier_formation_rule": r["A1_rule"], "interface": words(r["A2_interface"]),
             "interface_rule": r["A2_rule"], "value_transformation": words(r["A3_information"]),
             "value_transformation_rule": r["A3_rule"],
             "value_transformation_modifiers": r["A3_modifiers"].replace("+", ", "),
             "value_transformation_evidence_steps": r["A3_evidence_steps"], "text_role_axis": r["A4_text_role"],
             "transparency": words(r["A5_transparency"]), "opaque_step_share": r["opaque_step_share"],
             "stated_parameter_share": r["stated_parameter_share"], "archetype": ARCHETYPE[r["archetype"]]}
            for r in rows]
    datafile("route_codebook.csv", "codebook", "Route-level codebook of the design axes and archetypes", [
        ("record_id", "Record in the review database"),
        ("model_id", "Identifier of the charted model"),
        ("model", "Model name as charted"),
        ("configuration_id", "Identifier of the charted configuration"),
        ("route_id", "Identifier of the charted route"),
        ("route_label", "Label of the route, as charted"),
        ("lifecycle_phase", "Lifecycle phase of the route"),
        ("source_modality", "Modality of the route's source object"),
        ("carrier_family", "Family of the carrier that reaches the model"),
        ("carrier_subtype", "Subtype of the carrier"),
        ("fusion_topology", "How the carrier is fused with the language model"),
        ("text_role", "Role of text on the route"),
        ("operation_chain", "Consensus library operations of the route, in order"),
        ("carrier_formation", "Design axis 1, carrier formation: verbalised, symbolic, embedded, perceptual or text source"),
        ("carrier_formation_rule", "Rule that assigned the carrier formation"),
        ("interface", "Design axis 2, interface to the language model"),
        ("interface_rule", "Rule that assigned the interface"),
        ("value_transformation", "Design axis 3, transformation of measured values: verbatim, order only, discretised, "
                                 "learned compression, or not applicable"),
        ("value_transformation_rule", "Rule that assigned the value transformation"),
        ("value_transformation_modifiers", "Modifiers of the value transformation: subset, normalised"),
        ("value_transformation_evidence_steps", "Identifiers of the decomposed steps on which the value transformation rests"),
        ("text_role_axis", "Design axis 4, text role: instruction, payload, supervision, context or none"),
        ("transparency", "Design axis 5, transparency: transparent, partial, opaque or no computation"),
        ("opaque_step_share", "Share of the route's steps that are learned modules left unexpanded"),
        ("stated_parameter_share", "Share of the route's parameter slots whose value the paper states"),
        ("archetype", "Carrier × interface archetype of the route"),
    ], data)


def table_deviations() -> str:
    rows = read_csv(SRC["deviations"])
    cols = ["number", "kind", "date_or_stage", "area", "change", "made_after_results_were_seen",
            "dependent_results_and_labelling"]
    datafile("deviations.csv", "deviations", "Deviations from the protocol", [
        ("number", "Number of the deviation"),
        ("kind", "Protocol amendment (with the version it created) or further change not foreseen by the protocol"),
        ("date_or_stage", "Date of the amendment or the stage at which the change was made"),
        ("area", "Part of the review affected"),
        ("change", "What changed"),
        ("made_after_results_were_seen", "Whether the change was decided after results were known"),
        ("dependent_results_and_labelling", "Results that depend on the change, and how they are labelled"),
    ], [{c: r[c] for c in cols} for r in rows])
    return generated("table:deviations", [SRC["deviations"]], md_table(
        ["No.", "Kind", "Date or stage", "Area", "Change", "After results seen", "Dependent results and labelling"],
        [[r[c] for c in cols] for r in rows], [4, 14, 10, 10, 40, 7, 26], right={0}))


def figure_flow() -> str:
    return generated("figure:flow", [SRC["flow_figure"]], f"![]({SRC['flow_figure']}){{width=100%}}")


# ------------------------------------------------------------------------ screening prompts and decisions
SCREENING_RUNS = [  # key, stage, name, directory, role logs archived as role_logs.tar.gz, prefix of record ids
    ("ta_full", "title_abstract", "full re-screen of the cumulative records",
     "analysis/codex_screening_run_artifacts_20260706/full_runs/codex_gpt54mini_all4027_20260706", True, "full_2026-07-06__"),
    ("ta_june", "title_abstract", "June update",
     "analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update431_20260610", True, "june_update_2026-06-10__"),
    ("ta_july", "title_abstract", "July update",
     "analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update155_20260706", True, "july_update_2026-07-06__"),
    ("ta_august", "title_abstract", "August update",
     "data/living_catalog_updates/update_2026-08-09/04_abstract_screening", False, None),
    ("ta_recall", "title_abstract", "supplemental recall correction",
     "data/living_catalog_updates/update_2026-08-09/04_abstract_screening_manual_recall_xunzi_2026-08-11", False, None),
    ("ft_rounds", "full_text", "rounds 1–4",
     "data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10", False, ""),
    ("ft_august", "full_text", "August update",
     "data/living_catalog_updates/update_2026-08-09/09_fulltext_screening", False, ""),
    ("ft_recall", "full_text", "supplemental recall correction",
     "data/living_catalog_updates/update_2026-08-09/09_fulltext_screening_manual_recall_xunzi_2026-08-11", False, ""),
]
SCREEN_ROLES = [("scope_reviewer", "scope reviewer"), ("architecture_reviewer", "architecture reviewer"),
                ("adjudicator", "adjudicator")]
STAGE = {"title_abstract": "Title and abstract screening", "full_text": "Full-text screening"}
PROMPT_END = "Records JSON:\n"
FT_LEAD = "data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10/manual_resolution_2026-07-10.csv"
FT_AUG_ELIG = "data/living_catalog_updates/update_2026-08-09/10_eligibility"
FT_RECALL_ELIG = "data/living_catalog_updates/update_2026-08-09/10_eligibility_manual_recall_xunzi_2026-08-11"
DECISION = {"INCLUDE": "include", "EXCLUDE": "exclude", "UNCERTAIN": "uncertain"}
UNCERTAINTY = {"none": "", "generative_status_unclear": "generative status unclear", "mixed_signals": "mixed signals",
               "foundation_model_evidence_unclear": "foundation-model evidence unclear",
               "paper_type_unclear": "paper type unclear", "text_bio_bridge_unclear": "text–biology bridge unclear",
               "text_component_unclear": "text component unclear", "bio_modality_unclear": "biological modality unclear"}
PAPER_TYPE = {"primary_model_paper": "primary model paper", "review_editorial": "review or editorial",
              "benchmark_resource": "benchmark or resource", "application_wrapper": "application wrapper",
              "unclear": "unclear"}
DECIDED_BY = {"python_gate": "rule over the two first-pass reviewers", "adjudicator": "adjudicator"}


def run_dir(key: str) -> tuple:
    return next(r for r in SCREENING_RUNS if r[0] == key)


def run_label(key: str) -> str:
    _, stage, name, d, _, _ = run_dir(key)
    created = json.loads((ROOT / d / "run_metadata.json").read_text(encoding="utf-8"))["created"][:10]
    return f"{name} (run of {created})"


def static_prompts(key: str) -> dict[str, tuple[str, int]]:
    """The fixed part of every batch prompt of a run, per role, read from the run logs (up to 'Records JSON:')."""
    import tarfile
    _, _, _, d, archived, _ = run_dir(key)
    texts: dict[str, list[str]] = {}
    if archived:
        with tarfile.open(ROOT / d / "role_logs.tar.gz") as tf:
            for m in tf.getmembers():
                if m.name.endswith(".prompt.txt"):
                    texts.setdefault(m.name.split("/")[-2], []).append(tf.extractfile(m).read().decode("utf-8"))
    else:
        for p in sorted((ROOT / d / "role_logs").glob("*/*.prompt.txt")):
            texts.setdefault(p.parent.name, []).append(p.read_text(encoding="utf-8"))
    out = {}
    for role, ts in texts.items():
        statics = {t.split(PROMPT_END)[0] + PROMPT_END for t in ts if PROMPT_END in t}
        if len(statics) != 1 or any(PROMPT_END not in t for t in ts):
            raise SystemExit(f"{key}/{role}: batch prompts do not share one fixed part")
        out[role] = (statics.pop(), len(ts))
    return out


def screening_prompt_groups() -> list[dict]:
    """One entry per distinct fixed prompt text: stage, role, version (0 if the role has one text), runs, batches."""
    import hashlib
    groups: dict[tuple[str, str, str], list[str]] = {}
    batches: dict[tuple[str, str, str], int] = {}
    for key, stage, *_ in SCREENING_RUNS:
        for role, (text, n) in static_prompts(key).items():
            groups.setdefault((stage, role, text), []).append(run_label(key))
            batches[(stage, role, text)] = batches.get((stage, role, text), 0) + n
    out = []
    for stage in ("title_abstract", "full_text"):
        for role, role_name in SCREEN_ROLES:
            variants = [(t, runs) for (s, r, t), runs in groups.items() if s == stage and r == role]
            for i, (text, runs) in enumerate(variants, 1):
                out.append({"stage": stage, "role": role, "role_name": role_name,
                            "version": i if len(variants) > 1 else 0, "runs": runs,
                            "batches": batches[(stage, role, text)], "text": text,
                            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
    return out


def include_screening_prompts() -> str:
    out = []
    for g in screening_prompt_groups():
        head = f"#### {STAGE[g['stage']]}: {g['role_name']}" + (f", version {g['version']}" if g["version"] else "")
        out += [head, "", f"Used in: {'; '.join(g['runs'])}. Batches: {g['batches']:,}. "
                          f"SHA-256 of the text: {g['sha256']}.", "", "```", g["text"].rstrip("\n"), "```", ""]
    sources = sorted({run_dir(k)[3] + ("/role_logs.tar.gz" if run_dir(k)[4] else "/role_logs") for k, *_ in SCREENING_RUNS})
    return generated("include:screening_prompts", sources, "\n".join(out).strip())


def reason_words() -> dict[str, str]:
    text = (ROOT / SRC["flow_md"]).read_text(encoding="utf-8").split("## Full-text exclusion reasons", 1)[1]
    words_of = {m[2]: m[1] for m in re.finditer(r"\| (.+?) \| `([^`]+)` \| [\d,]+ \|", text)}
    words_of["EC4_no_foundation_model_evidence"] = words_of.get("EC4_no_foundation_model_evidence", "No foundation-model evidence")
    words_of["none"] = ""
    return words_of


def jsonl(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return {o["record_id"]: o for o in (json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip())}


def role_columns(prefix: str, o: dict | None, reasons: dict[str, str], fields: list[str]) -> dict[str, str]:
    o = o or {}
    out = {}
    for f in fields:
        v = o.get(f, "")
        if f == "paper_type":
            v = PAPER_TYPE.get(v, v)
        elif f == "primary_exclusion_code":
            v = reasons.get(v, v)
        elif f == "uncertainty_reason":
            v = UNCERTAINTY.get(v, v)
        out[f"{prefix}_{ROLE_FIELD[f]}"] = v
    return out


ROLE_FIELD = {"paper_type": "paper_type", "bio_modality_present": "biological_modality",
              "text_component_present": "text_component", "text_bio_bridge_present": "text_biology_bridge",
              "generative_model_present": "generative_model", "foundation_model_evidence": "foundation_model_evidence",
              "primary_exclusion_code": "exclusion_reason", "uncertainty_reason": "uncertainty",
              "decision_rationale": "rationale"}
SCOPE_FIELDS = ["paper_type", "bio_modality_present", "text_component_present", "text_bio_bridge_present",
                "primary_exclusion_code", "uncertainty_reason", "decision_rationale"]
ARCH_FIELDS = ["paper_type", "generative_model_present", "foundation_model_evidence", "primary_exclusion_code",
               "uncertainty_reason", "decision_rationale"]
ADJ_FIELDS = ["paper_type", "bio_modality_present", "text_component_present", "text_bio_bridge_present",
              "generative_model_present", "foundation_model_evidence", "primary_exclusion_code", "uncertainty_reason",
              "decision_rationale"]
ROLE_DICT = {
    "paper_type": "kind of paper: primary model paper, review or editorial, benchmark or resource, application wrapper, or unclear",
    "biological_modality": "whether a biological data modality is present (yes, no, unclear)",
    "text_component": "whether a natural-language text component is present (yes, no, unclear)",
    "text_biology_bridge": "whether a substantive bridge between text and biology is present (yes, no, unclear)",
    "generative_model": "whether the candidate model is generative (yes, no, unclear)",
    "foundation_model_evidence": "whether there is evidence of foundation-model characteristics (yes, no, unclear)",
    "exclusion_reason": "main exclusion reason returned by the role, if any",
    "uncertainty": "reason for uncertainty returned by the role, if any",
    "rationale": "brief evidence-grounded rationale returned by the role",
}


def screening_rows(key: str, reasons: dict[str, str]) -> list[dict]:
    _, stage, _, d, _, prefix = run_dir(key)
    base = ROOT / d
    rows = list(csv.DictReader(open(base / "final_screening_results.csv", encoding="utf-8", newline="")))
    scope, arch, adj = (jsonl(base / f"{r}.jsonl") for r, _ in SCREEN_ROLES)
    if key == "ta_august":
        cross = {c["legacy_record_id"]: c["stable_record_id"] for c in
                 json.loads((base / "record_id_crosswalk.json").read_text(encoding="utf-8"))["records"]}
    out = []
    for r in rows:
        rid = r["record_id"]
        if prefix is None and key == "ta_august":
            corpus_id = cross[rid]
        elif prefix is None:  # the supplemental recall record keeps the identifier of its full-text run
            corpus_id = "update_2026-08-09__manual_recall_xunzi"
        else:
            corpus_id = prefix + rid if prefix and not rid.startswith(prefix) else rid
        row = {"screening_run": run_label(key), "record_id": corpus_id, "record_id_in_run": rid, "title": r["title"],
               "doi": r["doi"], "automated_decision": DECISION[r["final_decision"]],
               "automated_exclusion_reason": reasons.get(r["final_code"], r["final_code"]),
               "automated_uncertainty": UNCERTAINTY.get(r["uncertainty_reason"], r["uncertainty_reason"]),
               "decided_by": DECIDED_BY.get(r["final_source"], r["final_source"]),
               "rationale": r["final_rationale"], "evidence": r["evidence_snippet"], "_code": r["final_code"]}
        row.update(role_columns("scope_reviewer", scope.get(rid), reasons, SCOPE_FIELDS))
        row.update(role_columns("architecture_reviewer", arch.get(rid), reasons, ARCH_FIELDS))
        row.update(role_columns("adjudicator", adj.get(rid), reasons, ADJ_FIELDS))
        out.append(row)
    return out


def screening_dictionary(first: list[tuple[str, str]]) -> list[tuple[str, str]]:
    cols = first + [
        ("automated_decision", "Decision of the automated screening: include, exclude or uncertain"),
        ("automated_exclusion_reason", "Exclusion reason of the automated decision, if any"),
        ("automated_uncertainty", "Reason for an uncertain automated decision, if any"),
        ("decided_by", "Who produced the automated decision: the fixed rule over the two first-pass reviewers, "
                       "or the adjudicator (called when the first-pass reviewers conflicted or were uncertain)"),
        ("rationale", "Rationale of the automated decision"),
        ("evidence", "Evidence snippet from the record that supports the decision"),
    ]
    for prefix, fields in (("scope_reviewer", SCOPE_FIELDS), ("architecture_reviewer", ARCH_FIELDS),
                           ("adjudicator", ADJ_FIELDS)):
        role = prefix.replace("_", " ")
        cols += [(f"{prefix}_{ROLE_FIELD[f]}", f"{role.capitalize()}: {ROLE_DICT[ROLE_FIELD[f]]}"
                  + (" (empty if the record was not adjudicated)" if prefix == "adjudicator" else ""))
                 for f in fields]
    return cols


def data_ta_decisions() -> None:
    reasons = reason_words()
    rows = []
    for key, stage, *_ in SCREENING_RUNS:
        if stage == "title_abstract":
            rows += screening_rows(key, reasons)
    facts = json.loads((ROOT / SRC["flow_facts"]).read_text(encoding="utf-8"))
    n_exc = sum(r["automated_decision"] == "exclude" for r in rows)
    if len(rows) != facts["screened"] + facts["other_screened"] or n_exc != facts["screen_excluded"]:
        raise SystemExit(f"title and abstract decisions do not match the flow: {len(rows)} screened, {n_exc} excluded")
    if len({r["record_id"] for r in rows}) != len(rows):
        raise SystemExit("a record appears twice among the title and abstract decisions")
    cols = screening_dictionary([
        ("screening_run", "Screening run (name and date of the run)"),
        ("record_id", "Identifier of the record in the review database"),
        ("record_id_in_run", "Identifier of the record within the screening run"),
        ("title", "Title of the record"),
        ("doi", "DOI of the record"),
    ])
    names = [c for c, _ in cols]
    datafile("title_abstract_screening_decisions.csv", "ta_decisions",
             "Title and abstract screening: decisions of the screening agents for every screened record", cols,
             [{c: r.get(c, "") for c in names} for r in rows])


def table_ft_decisions() -> str:
    reasons = reason_words()
    lead = {r["record_id"]: r for r in csv.DictReader(open(ROOT / FT_LEAD, encoding="utf-8", newline=""))}
    agent = {r["record_id"]: r for r in csv.DictReader(open(ROOT / FT_AUG_ELIG / "manual_resolution.csv",
                                                            encoding="utf-8", newline=""))}

    def elig(folder: str) -> dict[str, dict]:
        out = {}
        for name, decision in (("accepted_records.json", "INCLUDE"), ("excluded_records.json", "EXCLUDE")):
            for r in records_of(json.loads((ROOT / folder / name).read_text(encoding="utf-8"))):
                out[r["record_id"]] = {"decision": decision, "code": r.get("final_code", "none")}
        return out

    final_aug, final_recall = elig(FT_AUG_ELIG), elig(FT_RECALL_ELIG)
    rows = []
    for key, stage, *_ in SCREENING_RUNS:
        if stage != "full_text":
            continue
        for r in screening_rows(key, reasons):
            rid = r["record_id"]
            res = {"resolved_by": "", "resolution_decision": "", "resolution_reason": "", "resolution_basis": "",
                   "resolution_date": ""}
            if key == "ft_rounds":
                final, code = r["automated_decision"], r["_code"]
                if rid in lead:
                    m = lead[rid]
                    res = {"resolved_by": "review lead", "resolution_decision": DECISION[m["manual_decision"]],
                           "resolution_reason": reasons.get(m["manual_exclusion_code"], m["manual_exclusion_code"]),
                           "resolution_basis": m["manual_basis"], "resolution_date": m["manual_confirmation_date"]}
                    final, code = DECISION[m["manual_decision"]], m["manual_exclusion_code"]
            else:
                f = (final_aug if key == "ft_august" else final_recall)[rid]
                final, code = DECISION[f["decision"]], f["code"]
                if rid in agent:
                    m = agent[rid]
                    res = {"resolved_by": "LLM agent, not validated by a person",
                           "resolution_decision": DECISION[m["manual_decision"]], "resolution_reason": "",
                           "resolution_basis": m["rationale"], "resolution_date": m["resolved_at"][:10]}
            r.update(res)
            r["final_decision"] = final
            r["final_exclusion_reason"] = reasons.get(code, code) if final == "exclude" else ""
            r["study"] = study([rid], numbered=False) if rid in STUDY and final == "include" else ""
            rows.append(r)
    facts = json.loads((ROOT / SRC["flow_facts"]).read_text(encoding="utf-8"))
    n_exc = sum(r["final_decision"] == "exclude" for r in rows)
    n_inc = sum(r["final_decision"] == "include" for r in rows)
    if len(rows) != facts["assessed"] + facts["other_assessed"]:
        raise SystemExit(f"full-text decisions do not match the flow: {len(rows)} reports assessed")
    if n_exc != facts["excluded_fulltext"] or n_inc != facts["included_databases"] + facts["included_other"]:
        raise SystemExit(f"full-text decisions do not match the flow: {n_inc} included, {n_exc} excluded")
    if any(r["final_decision"] == "uncertain" for r in rows):
        raise SystemExit("a full-text decision is still uncertain")
    if STUDY and {r["record_id"] for r in rows if r["final_decision"] == "include"} != set(STUDY):
        raise SystemExit("the included reports differ from the included records of the bibliography")
    cols = screening_dictionary([
        ("screening_run", "Full-text screening run (name and date of the run)"),
        ("record_id", "Identifier of the record in the review database"),
        ("record_id_in_run", "Identifier of the record within the screening run"),
        ("title", "Title of the report"),
        ("doi", "DOI of the report"),
        ("study", "First author and year of an included report, as in the article's reference list"),
    ]) + [
        ("resolved_by", "Who resolved an uncertain automated decision: the review lead, from the cited full "
                        "sections (rounds 1–4), or an LLM agent reading the full document, whose decision was not "
                        "validated by a person (August round)"),
        ("resolution_decision", "Decision of the resolution"),
        ("resolution_reason", "Exclusion reason given by the resolution, if any"),
        ("resolution_basis", "Basis of the resolution, as recorded"),
        ("resolution_date", "Date of the resolution"),
        ("final_decision", "Final decision: include or exclude"),
        ("final_exclusion_reason", "Final exclusion reason, as counted in the flow diagram"),
    ]
    names = [c for c, _ in cols]
    datafile("fulltext_screening_decisions.csv", "ft_decisions",
             "Full-text screening: decisions of the screening agents, resolutions and final decisions for every "
             "assessed report", cols, [{c: r.get(c, "") for c in names} for r in rows])
    order = sorted(rows, key=lambda r: (r["final_decision"] != "include", r["final_exclusion_reason"],
                                        STUDY.get(r["record_id"], {}).get("number", 0), r["title"].lower()))
    printed = []
    for r in order:
        title = r["title"] + (f" [{STUDY[r['record_id']]['number']}]" if r["record_id"] in STUDY and r["final_decision"] == "include" else "")
        auto = r["automated_decision"] + (f": {r['automated_exclusion_reason'].lower()}" if r["automated_exclusion_reason"] else "")
        resolved = f"{r['resolution_decision']} ({r['resolved_by']})" if r["resolved_by"] else "—"
        printed.append([title, auto, resolved, r["final_decision"], r["final_exclusion_reason"] or "—"])
    return generated("table:ft_decisions", [run_dir(k)[3] for k, s, *_ in SCREENING_RUNS if s == "full_text"]
                     + [FT_LEAD, FT_AUG_ELIG, FT_RECALL_ELIG],
                     md_table(["Report", "Automated decision", "Resolution of an uncertain decision", "Final decision",
                               "Final reason for exclusion"], printed, [46, 18, 18, 8, 20]))


def records_of(value):
    return value["records"] if isinstance(value, dict) else value


STEP_CATEGORY = {"library_operation": "library operation", "learned_module": "learned module left unexpanded",
                 "source_provenance": "data provenance (no computation)", "identity": "identity (no change)",
                 "no_catalog_operation": "computation outside the library", "fusion_unspecified": "unspecified fusion",
                 "external_generator": "external text generator"}


def data_decomposition_steps() -> None:
    import pandas as pd
    s = pd.read_parquet(ROOT / "analysis/discovery_2026-10-14/steps.parquet")
    rows = [{"study": study([r.record_id], numbered=False), "record_id": r.record_id, "model": r.model_name,
             "route_id": r.route_id, "step": int(r.step_index), "steps_in_route": int(r.n_steps), "step_id": r.step_id,
             "charted_wording": r.chain_element, "category": STEP_CATEGORY.get(r.category, words(r.category)),
             "operations": "; ".join(OPERATION.get(o.strip(), words(o.strip())) for o in str(r.operations or "").split(",") if o.strip()),
             "runs_agreeing": f"{int(r.support)} of 3", "rule_and_rationale": r.rationale or "",
             "uncertainty": "" if pd.isna(r.uncertainty) else str(r.uncertainty), "evidence": r.evidence or ""}
            for r in s.itertuples()]
    datafile("decomposition_step_decisions.csv", "decomposition_steps",
             "Operation-level decomposition: decision for every step of the agent-decomposed routes", [
                 ("study", "First author and year of the record, as in the article's reference list"),
                 ("record_id", "Record in the review database"),
                 ("model", "Model name as charted"),
                 ("route_id", "Identifier of the charted route"),
                 ("step", "Position of the step in the route"),
                 ("steps_in_route", "Number of steps of the route"),
                 ("step_id", "Identifier of the step"),
                 ("charted_wording", "Element of the charted transformation chain that the step decomposes"),
                 ("category", "Decision category: library operation, learned module left unexpanded, data provenance "
                              "(no computation), identity (no change), computation outside the library, unspecified "
                              "fusion, or external text generator"),
                 ("operations", "Library operations named for the step"),
                 ("runs_agreeing", "Number of the three runs that returned the published decision"),
                 ("rule_and_rationale", "Rule of the decomposition protocol applied, with the agents' rationale"),
                 ("uncertainty", "Uncertainty recorded for the step, if any"),
                 ("evidence", "Verbatim quote from the paper"),
             ], rows)


def data_parameter_slots() -> None:
    import pandas as pd
    s = pd.read_parquet(ROOT / "analysis/discovery_2026-10-14/slots.parquet")
    status = {"stated": "stated", "unspecified": "not stated"}
    rows = [{"study": study([r.record_id], numbered=False), "record_id": r.record_id, "model": r.model_name,
             "route_id": r.route_id, "step_id": r.step_id, "operation": OPERATION.get(r.operation_id, words(r.operation_id)),
             "parameter": words(r.parameter), "status": status.get(r.status, words(r.status)),
             "value": "" if r.value is None or (isinstance(r.value, float) and pd.isna(r.value)) else str(r.value),
             "runs_agreeing": f"{int(r.support)} of 3",
             "evidence": "" if r.evidence is None or (isinstance(r.evidence, float) and pd.isna(r.evidence)) else str(r.evidence)}
            for r in s.itertuples()]
    datafile("parameter_slot_decisions.csv", "parameter_slots",
             "Parameter pass: whether the paper states each declared parameter of each operation call", [
                 ("study", "First author and year of the record, as in the article's reference list"),
                 ("record_id", "Record in the review database"),
                 ("model", "Model name as charted"),
                 ("route_id", "Identifier of the charted route"),
                 ("step_id", "Identifier of the step"),
                 ("operation", "Library operation of the call"),
                 ("parameter", "Declared parameter of the operation"),
                 ("status", "Whether the paper states the value for this data path: stated or not stated"),
                 ("value", "Stated value, as given in the paper"),
                 ("runs_agreeing", "Number of the three runs that returned the published status"),
                 ("evidence", "Verbatim quote from the paper"),
             ], rows)


CHARTING_FIELD = {"evaluation_formats": "evaluation format", "outputs": "output", "representation_rationale":
                  "stated rationale for or against an input representation", "biology_dependence_tests":
                  "test of whether outputs depend on the biological input", "connectors": "connector",
                  "llm_state": "language-model state", "encoder_state": "biological-encoder state",
                  "has_comparison": "reports a comparison between representations",
                  "has_synthetic_text": "uses text written by an LLM"}


def data_charting_items() -> None:
    rows = read_csv("analysis/design_culture_charting_2026-10-14/v11/consensus_items.csv")
    out = [{"study": study([r["record_id"]], numbered=False), "record_id": r["record_id"],
            "item": CHARTING_FIELD.get(r["field"], words(r["field"])), "category": words(r["category"]),
            "found_in_run_1": yes("True" if r["run1"] == "1" else "False"),
            "found_in_run_2": yes("True" if r["run2"] == "1" else "False")} for r in rows]
    datafile("targeted_charting_items.csv", "charting_items",
             "Targeted charting pass: for every record, which items each of the two runs returned", [
                 ("study", "First author and year of the record, as in the article's reference list"),
                 ("record_id", "Record in the review database"),
                 ("item", "Charting item"),
                 ("category", "Category of the item"),
                 ("found_in_run_1", "Whether the first run returned the category for the record (yes or no)"),
                 ("found_in_run_2", "Whether the second run returned the category for the record (yes or no)"),
             ], out)


GENERATORS = {"include:search_strategies": include_search_strategies, "table:search_runs": table_search_runs,
              "table:exclusions": table_exclusions, "table:works": table_works, "table:motifs": table_motifs,
              "table:comparisons": table_comparisons, "table:budgets": table_budgets,
              "table:synthetic": table_synthetic, "table:deviations": table_deviations, "figure:flow": figure_flow,
              "include:screening_prompts": include_screening_prompts, "table:ft_decisions": table_ft_decisions}
DATA_ONLY = [data_models, data_codebook, data_ta_decisions, data_decomposition_steps, data_parameter_slots,
             data_charting_items]


# ------------------------------------------------------------------------------ supplement parsing
def parse_supplement(text: str):
    preamble: list[str] = []
    sections: list[dict] = []
    sec = item = None
    for line in text.split("\n"):
        if line.startswith("## "):
            sec = {"name": line[3:].strip(), "lines": [], "items": []}
            sections.append(sec)
            item = None
        elif line.startswith("### ") and sec is not None:
            m = re.match(r"### \[\[S:([a-z_]+)\]\]\s+(.+)$", line)
            if not m or sec["name"] not in TYPES:
                raise SystemExit(f"supplementary heading without a key or outside a typed section: {line}")
            item = {"key": m[1], "title": m[2].strip(), "type": TYPES[sec["name"]], "lines": []}
            sec["items"].append(item)
        elif item is not None:
            item["lines"].append(line)
        elif sec is not None:
            sec["lines"].append(line)
        else:
            preamble.append(line)
    items = {}
    for s in sections:
        for it in s["items"]:
            if it["key"] in items:
                raise SystemExit(f"supplementary item declared twice: {it['key']}")
            items[it["key"]] = it
    return preamble, sections, items


def number_items(main_text: str, sections: list[dict], items: dict, blocks: dict[str, str]) -> dict[str, str]:
    order: list[str] = []

    def visit(text: str) -> None:
        for k in REF.findall(text):
            if k not in items:
                raise SystemExit(f"[[S:{k}]] is cited but not declared in the supplement")
            if k not in order:
                order.append(k)

    visit(main_text)
    for s in sections:
        for it in s["items"]:
            body = "\n".join(it["lines"])
            visit(PLACEHOLDER.sub(lambda m: blocks.get(m[1], ""), body))
    never = [k for k in items if k not in order]
    if never:
        raise SystemExit(f"supplementary items never cited: {never}")
    count = {"Note": 0, "Table": 0, "Figure": 0}
    num = {}
    for k in order:
        count[items[k]["type"]] += 1
        num[k] = f"S{count[items[k]['type']]}"
    return num


def check_types(text: str, items: dict, where: str) -> None:
    for m in REF.finditer(text):
        before = text[max(0, m.start() - 120):m.start()]
        kinds = re.findall(r"Supplementary\s+(Note|Table|Figure)s?\b", before)
        if not kinds or kinds[-1] != items[m[1]]["type"]:
            raise SystemExit(f"{where}: [[S:{m[1]}]] is a {items[m[1]]['type']} but is cited as "
                             f"{kinds[-1] if kinds else 'nothing'}: ...{before}")


PLACEHOLDER = re.compile(r"\{\{((?:include|table|figure):[a-z_]+)\}\}")


def resolve(text: str, num: dict[str, str], extra: dict[str, str]) -> str:
    text = REF.sub(lambda m: num[m[1]], text)
    for k, v in extra.items():
        text = text.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[^}]+\}\}", text)
    if left:
        raise SystemExit(f"unresolved placeholders: {sorted(set(left))}")
    return text


# ----------------------------------------------------------------------------------------- outputs
def git(*args: str) -> str:
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null")
    return subprocess.run(["git", *args], cwd=ROOT, env=env, capture_output=True, text=True, check=True).stdout.strip()


def deviation_counts() -> dict[str, str]:
    rows = read_csv(SRC["deviations"])
    kinds = [r["kind"].split(" (")[0] for r in rows]
    if set(kinds) - {"Protocol amendment", "Further change"}:
        raise SystemExit(f"unexpected kinds in the deviations table: {sorted(set(kinds))}")
    after = [r for r, k in zip(rows, kinds) if k == "Further change" and r["made_after_results_were_seen"].startswith("Yes")]
    return {"n:amendments": str(kinds.count("Protocol amendment")), "n:further_changes": str(kinds.count("Further change")),
            "n:after_results": str(len(after))}


def zenodo_links() -> dict[str, str]:
    recs = json.loads((ROOT / "manuscript/zenodo_records.json").read_text(encoding="utf-8"))
    return {f"zenodo:{k}": f"https://doi.org/{v['doi']}" for k, v in recs.items()}


def build_commit() -> str:
    head = git("rev-parse", "--short=8", "HEAD")
    dirty = git("status", "--porcelain", "--", *[str(p.relative_to(ROOT)) for p in SOURCE_FILES])
    return head + (", with uncommitted changes to the manuscript sources" if dirty else "")


def write_index(num: dict[str, str], items: dict) -> None:
    rows = []
    for k in sorted(items, key=lambda k: ("NoteTableFigure".index(items[k]["type"]), int(num[k][1:]))):
        sources = ITEM_SOURCES[k]
        for p in sources:
            if not (ROOT / p).exists():
                raise SystemExit(f"source of {k} does not exist: {p}")
        files = [f["name"] for f in DATAFILES if f["key"] == k]
        rows.append(f"| Supplementary {items[k]['type']} {num[k]} | {items[k]['title']} | "
                    f"{', '.join(f'`data/{f}`' for f in files) or '—'} | {'<br>'.join(f'`{p}`' for p in sources)} |")
    missing = set(items) - set(ITEM_SOURCES)
    if missing:
        raise SystemExit(f"no repository sources listed for: {sorted(missing)}")
    text = f"""# Supplementary material of paper 1: file index

Generated by `scripts/build_manuscript.py`; do not edit. Numbers follow the order in which the article
first cites each item, so they change if the article is reorganised; the keys in the sources
(`[[S:key]]`) do not.

| Item | Title | Data file | Repository sources |
|---|---|---|---|
""" + "\n".join(rows) + f"""

The data files in `data/` are reader-facing versions of the coded analysis outputs: identifiers are kept
in their own columns, coded values are written out in words, and `data/data_dictionary.csv` describes
every column. The coded originals stay in `analysis/` and are what the analysis scripts read.

Built files: `manuscript/build/manuscript.md` and `manuscript/build/supplementary_information.md`
(resolved Markdown), `manuscript/build/supplementary_information.pdf`, `manuscript/latex/main.pdf`.
Sources: `manuscript/review_manuscript_draft.md`, `manuscript/supplementary_information.md`,
`manuscript/supplementary/deviations_source.csv`.
"""
    INDEX.write_text(text, encoding="utf-8")


SUPP_HEADER = r"""\usepackage{fvextra}
\RecustomVerbatimEnvironment{verbatim}{Verbatim}{breaklines,breakanywhere,fontsize=\footnotesize}
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\footnotesize}
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.15}
\usepackage{xurl}
\usepackage{newunicodechar}
\makeatletter
\renewcommand\paragraph{\@startsection{paragraph}{4}{\z@}{3.25ex \@plus1ex \@minus.2ex}{0.6ex}{\normalfont\normalsize\bfseries}}
\makeatother
""" + "\\AtBeginDocument{\\newunicodechar{\u200b}{\\hspace{0pt}}}\n"  # zero-width space: break point


def supplement_pdf(md: Path, fallback: frozenset[str] = frozenset()) -> Path:
    """Typeset the supplement; characters missing from the text font are set in STIX Two Math."""
    header = BUILD / "supplement_header.tex"
    extra = ""
    if fallback:
        extra = "\\newfontfamily\\fallbackfont{STIX Two Math}\n" + "".join(
            f"\\AtBeginDocument{{\\newunicodechar{{{c}}}{{{{\\fallbackfont\\char\"{ord(c):04X}}}}}}}\n"
            for c in sorted(fallback))  # after unicode-math, which makes some of them math-only
    header.write_text(SUPP_HEADER + extra, encoding="utf-8")
    out = BUILD / "supplementary_information.pdf"
    cmd = ["pandoc", str(md), "-o", str(out), "--pdf-engine=xelatex", "--resource-path", str(ROOT),
           "-H", str(header), "--toc", "--toc-depth=3", "-V", "mainfont=Charter", "-V", "sansfont=Helvetica Neue",
           "-V", "monofont=Menlo", "-V", "fontsize=10pt", "-V", "geometry:margin=2cm", "-V", "colorlinks=true",
           "-V", "linkcolor=black", "-V", "urlcolor=blue"]
    r = subprocess.run(cmd, cwd=BUILD, capture_output=True, text=True, env=tex_env())
    if r.returncode:
        raise SystemExit("pandoc failed:\n" + r.stderr)
    missing = set(re.findall(r"Missing character: There is no (.) ", r.stderr))
    if missing and not fallback:
        return supplement_pdf(md, frozenset(missing))
    if missing:
        raise SystemExit(f"supplement: characters missing from the fonts: {sorted(missing)}")
    return out


def tex_env() -> dict:
    env = dict(os.environ, TEXMFVAR=str(BUILD / "texmf-var"))
    for p in ("/Library/TeX/texbin", "/usr/local/bin", "/opt/homebrew/bin"):
        if Path(p).exists() and p not in env.get("PATH", ""):
            env["PATH"] = env.get("PATH", "") + os.pathsep + p
    return env


def main_pdf() -> Path:
    r = subprocess.run([sys.executable, str(ROOT / "scripts/build_manuscript_latex.py")], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("LaTeX conversion failed:\n" + r.stdout + r.stderr)
    print(r.stdout.strip())
    env = tex_env()
    steps = [["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], ["bibtex", "main"],
             ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
             ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]]
    for cmd in steps:
        r = subprocess.run(cmd, cwd=LATEX, capture_output=True, text=True, env=env)
        if r.returncode:
            raise SystemExit(f"{' '.join(cmd)} failed:\n{r.stdout}")
    log = (LATEX / "main.log").read_text(encoding="utf-8", errors="replace")
    problems = re.findall(r"(LaTeX Warning: (?:Reference|Citation) .*? undefined.*)", log)
    if problems:
        raise SystemExit("undefined references or citations:\n" + "\n".join(sorted(set(problems))))
    return LATEX / "main.pdf"


def generate(used: set[str]) -> dict[str, str]:
    DATAFILES.clear()
    blocks = {name: GENERATORS[name]() for name in sorted(used)}
    for fn in DATA_ONLY:
        fn()
    return blocks


def assemble_supplement(preamble: list[str], sections: list[dict], blocks: dict[str, str], num: dict[str, str]) -> str:
    """Supplement with items in number order within each type; each top-level section starts a page."""
    title = next(l[2:].strip() for l in preamble if l.startswith("# "))
    rest = [l for l in preamble if not l.startswith("# ")]
    paras = "\n".join(rest).strip().split("\n\n")
    subtitle, intro = " ".join(paras[0].split()), "\n\n".join(paras[1:])
    out = ["---", f"title: \"{title}\"", f"subtitle: \"{subtitle}\"", "---", "", intro, ""]
    for i, s in enumerate(sections):
        if i:
            out += ["", "\\newpage", ""]
        out.append(f"## {s['name']}")
        out += s["lines"]
        for it in sorted(s["items"], key=lambda it: int(num[it["key"]][1:])):
            out.append(f"### Supplementary {it['type']} {num[it['key']]}. {it['title']}")
            out.append(PLACEHOLDER.sub(lambda m: blocks[m[1]], "\n".join(it["lines"])))
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-supplement-pdf", action="store_true", help="skip the PDF of the supplement")
    args = ap.parse_args()

    main_text = MAIN_SRC.read_text(encoding="utf-8")
    supp_text = SUPP_SRC.read_text(encoding="utf-8")
    preamble, sections, items = parse_supplement(supp_text)
    used = set(PLACEHOLDER.findall(supp_text))
    unknown = used - set(GENERATORS)
    if unknown or PLACEHOLDER.search(main_text):
        raise SystemExit(f"unknown placeholders: {sorted(unknown)}")
    if set(GENERATORS) - used:
        raise SystemExit(f"generators without a placeholder: {sorted(set(GENERATORS) - used)}")

    # pass 1: number the supplementary items and build the article
    blocks = generate(used)
    num = number_items(main_text, sections, items, blocks)
    check_types(main_text, items, "article")
    for s in sections:
        for it in s["items"]:
            check_types(PLACEHOLDER.sub(lambda m: blocks[m[1]], "\n".join(it["lines"])), items,
                        f"supplement ({it['key']})")
    commit = build_commit()
    BUILD.mkdir(parents=True, exist_ok=True)
    marked = {k: f"<!-- generated: {k} -->{v}<!-- end generated -->"
              for k, v in {"build_commit": commit, **deviation_counts(), **zenodo_links()}.items()}
    (BUILD / "manuscript.md").write_text(resolve(main_text, num, marked), encoding="utf-8")
    print(main_pdf().relative_to(ROOT))

    # pass 2: the supplement, with study labels and reference numbers from the article's bibliography
    STUDY.update(study_labels())
    blocks = generate(used)
    if number_items(main_text, sections, items, blocks) != num:
        raise SystemExit("supplementary numbering changed between passes")
    extra = {"build_commit": f"<!-- generated: build_commit -->{commit}<!-- end generated -->",
             **{k: f"<!-- generated: {k} -->{v}<!-- end generated -->" for k, v in zenodo_links().items()},
             "datafiles": generated("datafiles", ["the data files of this supplement"], datafiles_block(num, items))}
    extra.update({f"rows:{Path(f['name']).stem}": f"<!-- generated: rows of {f['name']} -->{len(f['rows'])}<!-- end generated -->"
                  for f in DATAFILES})
    (BUILD / "supplementary_information.md").write_text(
        resolve(assemble_supplement(preamble, sections, blocks, num), num, extra), encoding="utf-8")
    write_datafiles(num, items)
    write_index(num, items)
    with open(BUILD / "supplementary_numbering.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "type", "number", "title"])
        for k in sorted(items, key=lambda k: ("NoteTableFigure".index(items[k]["type"]), int(num[k][1:]))):
            w.writerow([k, items[k]["type"], num[k], items[k]["title"]])
    print({"items": {t: sum(1 for i in items.values() if i["type"] == t) for t in ("Note", "Table", "Figure")},
           "data_files": len(DATAFILES), "studies_labelled": len(STUDY), "build_commit": commit})
    if not args.no_supplement_pdf:
        print(supplement_pdf(BUILD / "supplementary_information.md").relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
