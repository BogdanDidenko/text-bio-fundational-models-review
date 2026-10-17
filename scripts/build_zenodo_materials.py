#!/usr/bin/env python3
"""Build the Zenodo deposit of the review materials that belong to the current manuscript version.

The deposit holds what a reader needs to audit the review:

  supplementary_information_<version>.pdf   Supplementary Information of the manuscript
  supplementary_data.zip                    its data files, column dictionary and file index
  screening.zip                             screening prompts (verbatim, from the run logs), the output of every
                                            agent role for every record at title/abstract and full text, the
                                            resolutions and eligibility decisions, search strategies and flow counts
  extraction.zip                            outputs of the agents that extracted information from the included
                                            papers (input-route charting, operation-level decomposition, parameter
                                            pass, targeted charting), with run configurations, schemas, rules and code
  operation_library_<release>.zip           the operation library release used in the manuscript, the motif
                                            library and the design-pattern codebook
  README.md, MANIFEST.csv                   description of the deposit; every file with size, SHA-256, source and
                                            transformation

Left out: paper texts and sections, figures and crops from papers, the titles and abstracts sent to the agents,
and the raw LLM call logs, which embed paper text. LLM call logs are reduced to the request metadata, with the
SHA-256 of each prompt, and the responses. Files are read from the working tree, which must match HEAD for every
included path; the commit is recorded in the README.

Usage:
  python3 scripts/build_zenodo_materials.py --out <dir> [--protocol-doi DOI] [--materials-doi DOI]
"""
import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_manuscript as bm  # noqa: E402

GH = "https://github.com/BogdanDidenko/text-bio-fundational-models-review"
SITE = "https://bogdandidenko.github.io/text-bio-fundational-models-review/"
LIBRARY_SITE = SITE + "component-library/"
TAX = "data/living_catalog/taxonomy_rerun_preflight_2026-08-12"
DEC = "analysis/operation_decomposition_v32_2026-10-14"
DEC_RUNS = "analysis/operation_decomposition_2026-10-07"
CHART = "analysis/design_culture_charting_2026-10-14"
LIBR = "analysis/representation_block_library_2026-10-04"
RELEASE = "1.3.0"

SCREEN_FOLDER = {  # run key of build_manuscript.SCREENING_RUNS -> folder in the deposit (date appended)
    "ta_full": "title_abstract/1_full_rescreen", "ta_june": "title_abstract/2_june_update",
    "ta_july": "title_abstract/3_july_update", "ta_august": "title_abstract/4_august_update",
    "ta_recall": "title_abstract/5_recall_correction", "ft_rounds": "full_text/1_rounds_1-4",
    "ft_august": "full_text/2_august_update", "ft_recall": "full_text/3_recall_correction",
}
RUN_FILES = ["final_screening_results.csv", "scope_reviewer.jsonl", "architecture_reviewer.jsonl", "adjudicator.jsonl",
             "python_gate_outputs.json", "run_metadata.json", "summary.json", "artifact_summary.json", "README.md",
             "record_id_crosswalk.json", "reproducibility_manifest.json", "include_records.md",
             "manual_resolution_2026-07-10.csv", "manual_resolution_2026-07-10.md"]
RUN_PATTERNS = [r"schemas/[^/]+\.json", r"cohort_[^/]+_audit\.(json|md)"]
PAPER_TEXT_KEYS = {"abstract", "selected_full_text_sections", "text"}
TOP = "(top level)"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def tracked(prefix: str) -> list[str]:
    return [p for p in git("ls-files", "--", prefix).split("\n") if p]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Deposit:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, container: str, dest: str, data: bytes, source: str, transformation: str) -> None:
        if any(i["container"] == container and i["path"] == dest for i in self.items):
            raise SystemExit(f"duplicate path in {container}: {dest}")
        self.items.append({"container": container, "path": dest, "data": data, "source": source,
                           "transformation": transformation})

    def copy(self, container: str, dest: str, src: str, transformation: str = "copied") -> None:
        path = ROOT / src
        if not path.is_file():
            raise SystemExit(f"missing source file: {src}")
        self.add(container, dest, path.read_bytes(), src, transformation)

    def copy_tree(self, container: str, dest: str, prefix: str, skip=lambda rel: False) -> int:
        files = tracked(prefix)
        if not files:
            raise SystemExit(f"no tracked files under {prefix}")
        n = 0
        for src in files:
            rel = src[len(prefix):].lstrip("/")
            if skip(rel):
                continue
            self.copy(container, f"{dest}/{rel}", src)
            n += 1
        return n


def strip_paper_text(obj):
    """Replace paper text (abstracts, sections) by a marker with its length and SHA-256."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in PAPER_TEXT_KEYS and isinstance(v, str) and v:
                out[k] = f"[omitted: {len(v)} characters of paper text; sha256 {sha256(v.encode('utf-8'))}]"
            else:
                out[k] = strip_paper_text(v)
        return out
    if isinstance(obj, list):
        return [strip_paper_text(v) for v in obj]
    return obj


def responses_only(src: str) -> bytes:
    """An LLM call log reduced to request metadata (prompt and schema replaced by their SHA-256) and responses."""
    out = []
    for line in (ROOT / src).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("event") == "request":
            prompt = e.get("prompt")
            text = prompt if isinstance(prompt, str) else json.dumps(prompt, ensure_ascii=False, sort_keys=True)
            r = {k: v for k, v in e.items() if k not in ("prompt", "schema_json")}
            r.setdefault("prompt_sha256", sha256(text.encode("utf-8")))
            r["prompt_characters"] = len(text)
            if "schema_json" in e:
                schema = e["schema_json"] if isinstance(e["schema_json"], str) else json.dumps(e["schema_json"], sort_keys=True)
                r["schema_sha256"] = sha256(schema.encode("utf-8"))
            out.append(r)
        else:
            out.append(e)
    return ("\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n").encode("utf-8")


def run_date(key: str) -> str:
    m = re.search(r"run of (\d{4}-\d{2}-\d{2})", bm.run_label(key))
    if not m:
        raise SystemExit(f"no run date for {key}")
    return m.group(1)


def manuscript_version() -> str:
    m = re.search(r"manuscript (v[0-9.]+)", (ROOT / "manuscript/latex/main.tex").read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("manuscript version not found in manuscript/latex/main.tex")
    return m.group(1)


# ---------------------------------------------------------------- sections


def screening(dep: Deposit) -> dict:
    z = "screening.zip"
    facts = {"runs": []}
    index = io.StringIO()
    w = csv.writer(index, lineterminator="\n")
    w.writerow(["file", "stage", "role", "version", "used_in_runs", "batches", "sha256"])
    for g in bm.screening_prompt_groups():
        name = f"{g['stage']}__{g['role']}" + (f"__version_{g['version']}" if g["version"] else "") + ".txt"
        dep.add(z, f"screening/prompts/{name}", g["text"].encode("utf-8"),
                "role logs of the runs listed in prompts_index.csv",
                "fixed part of the batch prompt as sent (text up to 'Records JSON:'), extracted from the run logs")
        w.writerow([name, g["stage"], g["role"], g["version"] or "", "; ".join(g["runs"]), g["batches"], g["sha256"]])
    dep.add(z, "screening/prompts/prompts_index.csv", index.getvalue().encode("utf-8"),
            "scripts/build_manuscript.py (screening_prompt_groups)", "generated")
    facts["prompts"] = len(bm.screening_prompt_groups())
    dep.copy_tree(z, "screening/prompts/templates/protocol", "protocol/screening_prompt_templates")
    dep.copy_tree(z, "screening/prompts/templates/title_abstract_runs_2026-07-06",
                  "analysis/codex_screening_run_artifacts_20260706/prompt_templates")
    dep.copy(z, "screening/code/run_codex_screening_pipeline.py", "scripts/run_codex_screening_pipeline.py")
    dep.copy(z, "screening/code/as_archived_with_the_runs_of_2026-07-06/run_codex_screening_pipeline.py",
             "analysis/codex_screening_run_artifacts_20260706/pipeline_code/run_codex_screening_pipeline.py")
    for doc in ("eligibility_criteria.md", "screening_process.md", "llm_screening_system_guideline.md",
                "full_text_section_screening_2026-07-10.md"):
        dep.copy(z, f"screening/protocol/{doc}", f"protocol/{doc}")

    for key, stage, name, d, _archived, _prefix in bm.SCREENING_RUNS:
        folder = f"screening/{SCREEN_FOLDER[key]}_{run_date(key)}"
        kept = []
        for src in tracked(d):
            rel = src[len(d) + 1:]
            if rel in RUN_FILES or any(re.fullmatch(p, rel) for p in RUN_PATTERNS):
                dep.copy(z, f"{folder}/{rel}", src)
                kept.append(rel)
        if "final_screening_results.csv" not in kept or "scope_reviewer.jsonl" not in kept:
            raise SystemExit(f"{key}: decision files missing")
        with open(ROOT / d / "final_screening_results.csv", encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        decisions = {}
        for r in rows:
            decisions[r["final_decision"].lower()] = decisions.get(r["final_decision"].lower(), 0) + 1
        facts["runs"].append({"key": key, "stage": stage, "label": bm.run_label(key), "folder": folder,
                              "records": len(rows), "decisions": decisions})

    for folder_key, src_dir in (("ft_august", bm.FT_AUG_ELIG), ("ft_recall", bm.FT_RECALL_ELIG)):
        folder = f"screening/{SCREEN_FOLDER[folder_key]}_{run_date(folder_key)}/eligibility"
        for src in tracked(src_dir):
            rel = src[len(src_dir) + 1:]
            if rel.endswith(".json"):
                obj = json.loads((ROOT / src).read_text(encoding="utf-8"))
                dep.add(z, f"{folder}/{rel}", (json.dumps(strip_paper_text(obj), ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
                        src, "abstracts and full-text sections replaced by markers with length and SHA-256")
            else:
                dep.copy(z, f"{folder}/{rel}", src)

    for src in ("analysis/prisma_search_audit_2026-10-14/search_strategies_as_executed.md",
                "analysis/prisma_search_audit_2026-10-14/search_runs_by_database.csv",
                "analysis/prisma_search_audit_2026-10-14/PRISMA_S_AUDIT.md",
                "analysis/prisma_search_audit_2026-10-14/protein_text_models_coverage_check.md",
                "analysis/prisma_search_audit_2026-10-14/protein_text_models_coverage_check.json",
                "analysis/prisma_flow_2026-10-07/PRISMA_FLOW.md", "analysis/prisma_flow_2026-10-07/prisma_facts.json",
                "analysis/prisma_flow_2026-10-07/prisma_flow.svg", "analysis/prisma_flow_2026-10-07/prisma_flow.png"):
        dep.copy(z, f"screening/search_and_flow/{Path(src).name}", src)
    for src in tracked("scripts"):
        if re.fullmatch(r"scripts/search_config[^/]*\.json", src):
            dep.copy(z, f"screening/search_and_flow/search_configs/{Path(src).name}", src)
    dep.copy(z, "screening/search_and_flow/reproduce_search.py", "scripts/reproduce_search.py")
    return facts


def extraction(dep: Deposit) -> dict:
    z = "extraction.zip"
    facts = {}
    # Input-route charting (atlas): final snapshot, corrections, runs, adjudication, amendments, code.
    facts["route_snapshot_files"] = dep.copy_tree(z, "extraction/route_charting/final_snapshot",
                                                  f"{TAX}/snapshot_full_55_semantic_correction_2026-08-17")
    dep.copy(z, "extraction/route_charting/README_rerun_2026-08-12.md", f"{TAX}/README.md")
    dep.copy(z, "extraction/route_charting/commands.sh", f"{TAX}/commands.sh")
    for rel in ("DERIVED_METADATA_CORRECTION_2026-08-16.md",
                "taxonomy_derived_correction_2026-08-16/special_cases_report.md",
                "taxonomy_semantic_correction_2026-08-17/semantic_correction_report.json",
                "taxonomy_semantic_correction_2026-08-17/route_transition_ledger.csv",
                "taxonomy_semantic_correction_2026-08-17/route_transition_ledger.jsonl"):
        dep.copy(z, f"extraction/route_charting/corrections/{rel}", f"{TAX}/{rel}")
    n_logs = 0
    for prefix, dest in ((f"{TAX}/taxonomy/runs", "extraction/route_charting/runs"),
                         (f"{TAX}/taxonomy/adjudication", "extraction/route_charting/adjudication")):
        for src in tracked(prefix):
            rel = src[len(prefix) + 1:]
            if rel.endswith("llm_calls.jsonl"):
                dep.add(z, f"{dest}/{rel[:-len('llm_calls.jsonl')]}responses.jsonl", responses_only(src), src,
                        "LLM call log reduced to request metadata and responses; prompts (which embed the paper) "
                        "and schemas replaced by their SHA-256")
                n_logs += 1
            elif rel.endswith(".json") or rel.endswith("events.jsonl"):
                dep.copy(z, f"{dest}/{rel}", src)
            elif rel.endswith(".txt") or rel.endswith(".log"):
                continue  # prompts with paper text and raw logs
            else:
                raise SystemExit(f"unexpected file type in route-charting runs: {src}")
    facts["route_call_logs"] = n_logs
    dep.copy(z, "extraction/route_charting/adjudication/adjudication_resolution_manifest.csv",
             f"{TAX}/taxonomy/adjudication_resolution_manifest.csv")
    dep.copy_tree(z, "extraction/route_charting/amendments", "data/input_representation_audit_amendments")
    for src in ("scripts/docling/run_docling_graph_input_taxonomy.py", "scripts/docling/classify_fixed_input_taxonomy_candidates.py",
                "scripts/docling/adjudicate_input_taxonomy.py", "scripts/docling/synthesize_input_representation_taxonomy.py",
                "scripts/docling/build_input_taxonomy_registry.py", "scripts/docling/analyze_input_taxonomy_runs.py",
                "scripts/docling/codex_openai_compat_server.py", "scripts/run_taxonomy_semantic_correction.py"):
        dep.copy(z, f"extraction/route_charting/code/{Path(src).name}", src)
    dep.copy(z, "extraction/route_charting/protocol/input_representation_taxonomy_2026-07-11.md",
             "protocol/input_representation_taxonomy_2026-07-11.md")

    # Operation-level decomposition: consensus per record, the three runs per record, stability, rules, code.
    facts["decomposition_records"] = len({p.split("/")[3] for p in tracked(f"{DEC}/records")})
    dep.copy_tree(z, "extraction/decomposition/consensus/records", f"{DEC}/records")
    for name in ("run_summary.json", "STEWARD_QUEUE.md", "README.md"):  # corpus_assemblies.json = union of records
        dep.copy(z, f"extraction/decomposition/consensus/{name}", f"{DEC}/{name}")
    for run in ("v32_all", "v32_h4"):
        dep.copy_tree(z, f"extraction/decomposition/runs/{run}", f"{DEC_RUNS}/stabilization/{run}")
    for src in tracked(f"{DEC_RUNS}/stabilization"):
        rel = src[len(DEC_RUNS) + len("/stabilization/"):]
        if "/" not in rel and rel != ".gitignore":
            dep.copy(z, f"extraction/decomposition/stability/{rel}", src)
    for name in ("README.md", "run_config.json", "worked_examples.json"):
        dep.copy(z, f"extraction/decomposition/runs/{name}", f"{DEC_RUNS}/{name}")
    for src in ("protocol/REPRESENTATION_LIBRARY_GUIDE.md", "protocol/OPERATION_PARAMETER_GLOSSARY.md",
                "protocol/REPRESENTATION_LIBRARY_STEWARD_PROMPT.md"):
        dep.copy(z, f"extraction/decomposition/rules/{Path(src).name}", src)
    for src in ("scripts/operation_decomposition_v3.py", "scripts/operation_decomposition.py"):
        dep.copy(z, f"extraction/decomposition/code/{Path(src).name}", src)

    # Parameter pass.
    dep.copy_tree(z, "extraction/parameter_pass", f"{DEC}/parameter_pass")
    dep.copy(z, "extraction/parameter_pass/code/run_parameter_pass.py", "scripts/run_parameter_pass.py")

    # Targeted charting pass (design cultures): the two runs, consensus, adjudication, tables; figure images left out.
    dep.copy_tree(z, "extraction/targeted_charting", f"{CHART}/v11",
                  skip=lambda rel: rel.startswith("figures/") and not rel.endswith(".csv"))
    for name in ("roles.json", "records.json"):
        dep.copy(z, f"extraction/targeted_charting/{name}", f"{CHART}/{name}")
    dep.copy(z, "extraction/targeted_charting/code/run_design_culture_charting.py", "scripts/run_design_culture_charting.py")
    facts["charting_records"] = len({p.split("/")[5] for p in tracked(f"{CHART}/v11/run_1/records")})
    return facts


def library(dep: Deposit) -> str:
    z = f"operation_library_{RELEASE}.zip"
    root = f"operation_library_{RELEASE}"
    dep.copy_tree(z, f"{root}/release", f"{LIBR}/releases/{RELEASE}")
    for name in ("operation_catalog.json", f"DECISION_MEMO_{RELEASE}.md", "OPERATION_REBUILD_DECISIONS.md", "README.md"):
        dep.copy(z, f"{root}/{name}", f"{LIBR}/{name}")
    dep.copy_tree(z, f"{root}/motif_library", "analysis/motif_library_2026-10-14")
    dep.copy_tree(z, f"{root}/design_patterns", "analysis/design_taxonomy_2026-10-13")
    return z


def supplementary(dep: Deposit, version: str) -> str:
    dep.copy(TOP, f"supplementary_information_{version}.pdf", "manuscript/build/supplementary_information.pdf")
    dep.copy_tree("supplementary_data.zip", "supplementary_data/data", "manuscript/supplementary/data")
    dep.copy("supplementary_data.zip", "supplementary_data/FILE_INDEX.md", "manuscript/supplementary/README.md")
    return f"supplementary_information_{version}.pdf"


# ---------------------------------------------------------------- README, manifest, zips


def readme(dep: Deposit, version: str, commit: str, sfacts: dict, efacts: dict, libzip: str, pdf: str,
           protocol_doi: str, materials_doi: str) -> str:
    sizes = {}
    for i in dep.items:
        c = i["container"]
        sizes.setdefault(c, [0, 0])
        sizes[c][0] += 1
        sizes[c][1] += len(i["data"])
    run_lines = []
    for r in sfacts["runs"]:
        dec = ", ".join(f"{n} {k}" for k, n in sorted(r["decisions"].items()))
        run_lines.append(f"| `{r['folder'].split('/', 1)[1]}` | {r['label']} | {r['records']} | {dec} |")
    proto = f"https://doi.org/{protocol_doi}" if protocol_doi else "[protocol record DOI]"
    own = f"https://doi.org/{materials_doi}" if materials_doi else "[DOI of this record]"
    zips = sorted(c for c in sizes if c != TOP)
    files_table = "\n".join(f"| `{c}` | {sizes[c][0]} | {sizes[c][1] / 1e6:.1f} MB |" for c in zips)
    return f"""# Review materials: Translate or encode? Two design cultures for coupling language and omics data in generative foundation models (manuscript {version})

This record holds the materials of a scoping review of generative foundation models that couple a text
modality with omics data: the screening prompts and the decisions of the screening agents for every record,
the outputs of the agents that extracted information from the included papers, the operation library used
in the analysis, and the Supplementary Information with its data files. It accompanies manuscript {version}
(not peer reviewed). The protocol and its amendments are deposited separately ({proto}).

- Repository: {GH} (files of this record taken at commit `{commit}`)
- Interactive operation library: {LIBRARY_SITE}
- Input-representation atlas: {SITE}
- This record: {own}

## Contents

| File | Files inside | Uncompressed |
|---|---:|---:|
| `{pdf}` | 1 | {sizes[TOP][1] / 1e6:.1f} MB |
{files_table}

`MANIFEST.csv` lists every file with its size, SHA-256, the repository path it comes from and what was done
to it.

### `supplementary_data.zip`

The data files of the Supplementary Information with their column dictionary (`data/data_dictionary.csv`)
and the file index of the supplementary items (`FILE_INDEX.md`), which gives the repository source of each
item. They include the title/abstract decision for every screened record and the full-text decision for
every assessed report, with the answers and rationales of each agent role.

### `screening.zip`

- `prompts/`: the fixed part of the batch prompt of each screening role, as sent ({sfacts['prompts']} distinct
  texts), extracted from the run logs; `prompts_index.csv` gives for each text the runs that used it, the
  number of batches and its SHA-256. Each prompt continued, after the line `Records JSON:`, with the records
  of the batch. The prompt templates and the pipeline code that rendered them are in `prompts/templates/`
  and `code/`.
- One folder per screening run, with the final decisions (`final_screening_results.csv`), the output of each
  role for each record (`scope_reviewer.jsonl`, `architecture_reviewer.jsonl`, `adjudicator.jsonl`), the
  rule-based gate over the two first-pass reviewers (`python_gate_outputs.json`), run metadata, output
  schemas where they were recorded, and the resolutions of uncertain full-text records:

| Folder | Run | Records | Automated decisions |
|---|---|---:|---|
{chr(10).join(run_lines)}

  Uncertain full-text records were resolved by the review lead in rounds 1–4
  (`full_text/1_rounds_1-4_*/manual_resolution_2026-07-10.csv`) and by an LLM agent reading the full
  document in the August round (`full_text/2_august_update_*/eligibility/manual_resolution.csv`); the latter
  decision was not validated by a person. In the eligibility files, abstracts and full-text sections are
  replaced by markers with their length and SHA-256.
- `search_and_flow/`: search strategies as executed, search runs by database, the search configurations and
  the script that reruns them, the PRISMA-S audit, the coverage check for protein and nucleotide models, and
  the PRISMA flow counts and diagram.
- `protocol/`: the eligibility criteria and screening procedure documents used by the agents.

### `extraction.zip`

- `route_charting/`: input routes of every charted model. `final_snapshot/` holds the routes after
  adjudication and the dated corrections (`route_annotations`, `evidence_ledger` with the verbatim evidence,
  `taxonomy_tree.json`, agreement metrics); `runs/` and `adjudication/` hold the responses of the discovery,
  the three direct classification runs, dense coverage and the blinded adjudication ({efacts['route_call_logs']}
  call logs), with run configurations and schemas; `corrections/` documents the dated corrections;
  `amendments/` the author-led amendments; `code/` and `protocol/` the scripts and rules.
- `decomposition/`: operation-level decomposition of the agent-decomposed papers
  ({efacts['decomposition_records']} records): `consensus/` the majority decision per step with evidence and
  the assembled operation graphs; `runs/` the output of each of the three runs per record, including the
  held-out stability runs; `stability/` the record sets, gate and stability report; `rules/` and `code/` the
  decomposition rules and the scripts that built the prompts.
- `parameter_pass/`: the three runs per record, the consensus and the code.
- `targeted_charting/`: the two runs per record ({efacts['charting_records']} records), the items found by
  each run, the adjudication of the variables used for culture-level claims, the work-level tables, the
  cross-culture comparison units, the source data of the figure panels and the code.

### `{libzip}`

The operation library release used in the manuscript (catalog of operations, assemblies, evidence, schemas,
validation), with the release decision memo, the motif library and the design-pattern codebook. The same
release is browsable at {LIBRARY_SITE}.

## What is not included, and why

The texts of the reviewed papers (converted full texts, sections passed to the agents), figures and crops
from the papers, the titles and abstracts sent to the agents, and the raw LLM call logs are left out, because
they reproduce third-party text. The call logs of route charting are reduced to the request metadata and the
responses; each request keeps the SHA-256 of its prompt, which identifies the prompt in the repository logs.
The prompts of the extraction steps are built by the scripts in each `code/` folder from the rules, the
operation catalog and the paper text.

## Licence

The content created for this review is released under the Creative Commons Attribution 4.0 International
licence (CC BY 4.0); the code files are under the MIT licence of the repository. Verbatim quotations,
titles and figure captions from the reviewed papers remain under the copyright of their owners and are not
covered by these licences.

## Citation

Please cite the manuscript and this record ({own}).
"""


def write_out(dep: Deposit, out: Path, readme_text: str, commit_time: tuple) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    for old in out.iterdir():
        if old.is_file():
            old.unlink()
    containers = sorted({i["container"] for i in dep.items if i["container"] != TOP})
    for c in containers:
        with zipfile.ZipFile(out / c, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for i in sorted((i for i in dep.items if i["container"] == c), key=lambda i: i["path"]):
                info = zipfile.ZipInfo(i["path"], date_time=commit_time)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                zf.writestr(info, i["data"])
    for i in dep.items:
        if i["container"] == TOP:
            (out / i["path"]).write_bytes(i["data"])
    (out / "README.md").write_text(readme_text, encoding="utf-8")
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["container", "path", "bytes", "sha256", "source", "transformation"])
    for i in sorted(dep.items, key=lambda i: (i["container"], i["path"])):
        w.writerow([i["container"], i["path"], len(i["data"]), sha256(i["data"]), i["source"], i["transformation"]])
    (out / "MANIFEST.csv").write_text(buf.getvalue(), encoding="utf-8")
    return sorted(out.iterdir())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--protocol-doi", default="")
    ap.add_argument("--materials-doi", default="")
    args = ap.parse_args()
    commit = git("rev-parse", "HEAD").strip()
    dep = Deposit()
    version = manuscript_version()
    pdf = supplementary(dep, version)
    sfacts = screening(dep)
    efacts = extraction(dep)
    libzip = library(dep)
    dirty = git("status", "--porcelain", "--", *sorted({i["source"] for i in dep.items if (ROOT / i["source"]).is_file()}))
    if dirty.strip():
        raise SystemExit("included files differ from HEAD:\n" + dirty)
    ts = git("show", "-s", "--format=%cd", "--date=format:%Y %m %d %H %M %S", "HEAD").split()
    files = write_out(dep, args.out, readme(dep, version, commit, sfacts, efacts, libzip, pdf,
                                            args.protocol_doi, args.materials_doi), tuple(int(x) for x in ts))
    info = {"commit": commit, "version": version, "files": [f.name for f in files], "items": len(dep.items),
            "bytes": sum(len(i["data"]) for i in dep.items)}
    (args.out / "build_info.json").write_text(json.dumps(info, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
