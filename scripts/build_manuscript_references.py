#!/usr/bin/env python3
"""Build the BibTeX file of the LaTeX manuscript (paper 1).

Two kinds of entries:
  * the 55 included records, with identifiers from the atlas
    (docs/input-representation-atlas/data/atlas.json) and the master record files;
  * works that the manuscript names but did not include (guidelines, tools, comparator
    models and the protein text models of the coverage check), listed in EXTERNAL below.

Metadata come from Crossref (DOI -> BibTeX) and the arXiv API. Raw responses are cached in
manuscript/latex/references_cache/, so the build is repeatable offline:

    python3 scripts/build_manuscript_references.py            # fetch what is missing, then build
    python3 scripts/build_manuscript_references.py --offline  # build from the cache only

Outputs: manuscript/latex/references.bib and manuscript/latex/references_audit.csv (one row per
entry with the source, the identifier and, for included records, the similarity between the
corpus title and the fetched title).
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript/latex"
CACHE = OUT / "references_cache"
ATLAS = ROOT / "docs/input-representation-atlas/data/atlas.json"
MASTER_FILES = [
    ROOT / "data/deduplicated_records.json",
    ROOT / "analysis/codex_screening_run_artifacts_20260706/inputs/dedup_update_2026-06-10/new_records_after_cross_dedup_crossref_checked.json",
    ROOT / "analysis/codex_screening_run_artifacts_20260706/inputs/dedup_update_2026-07-06/new_records_after_cross_dedup_crossref_checked.json",
    ROOT / "data/living_catalog_updates/update_2026-08-09/02_records/new_records_after_cross_dedup_crossref_checked.json",
]

# Citation keys of the included records (record id -> key). Keys name the system.
INCLUDED_KEYS = {
    "full_2026-07-06__rec_001218": "alter",
    "june_update_2026-06-10__rec_000194": "bioblip",
    "full_2026-07-06__rec_001519": "biogpt_genomics",
    "full_2026-07-06__rec_003214": "biomedgpt",
    "full_2026-07-06__rec_001074": "bioreason",
    "full_2026-07-06__rec_002049": "bioverse",
    "full_2026-07-06__rec_000090": "c2sscale",
    "full_2026-07-06__rec_001687": "calmflow",
    "full_2026-07-06__rec_001187": "precious3gpt",
    "full_2026-07-06__rec_001617": "cello1",
    "june_update_2026-06-10__rec_000248": "cell2text_thesis",
    "full_2026-07-06__rec_001838": "cell2text",
    "full_2026-07-06__rec_001126": "cellhermes",
    "full_2026-07-06__rec_002517": "chatcell",
    "full_2026-07-06__rec_000771": "chatnt",
    "full_2026-07-06__rec_000950": "chroma",
    "full_2026-07-06__rec_001277": "okrcell",
    "full_2026-07-06__rec_003629": "gemgen",
    "full_2026-07-06__rec_003008": "balanced_finetuning",
    "full_2026-07-06__rec_003043": "geneverse",
    "full_2026-07-06__rec_002243": "human_genome_book",
    "june_update_2026-06-10__rec_000133": "genna",
    "full_2026-07-06__rec_002304": "genolator",
    "full_2026-07-06__rec_003131": "gpgpt",
    "full_2026-07-06__rec_003206": "cell2sentence",
    "full_2026-07-06__rec_002105": "cellwhisperer_preprint",
    "full_2026-07-06__rec_000827": "cellwhisperer",
    "june_update_2026-06-10__rec_000152": "h2o",
    "full_2026-07-06__rec_001319": "instructcell",
    "full_2026-07-06__rec_003188": "leonine",
    "full_2026-07-06__rec_001381": "scmmgpt",
    "full_2026-07-06__rec_003434": "longevity_llm",
    "full_2026-07-06__rec_001352": "medpalmm",
    "full_2026-07-06__rec_003852": "mupad",
    "full_2026-07-06__rec_003323": "teampath",
    "update_2026-08-09__rec_000138": "ocellus",
    "june_update_2026-06-10__rec_000246": "omicslm",
    "full_2026-07-06__rec_001773": "omnidna",
    "june_update_2026-06-10__rec_000350": "omnigene4",
    "full_2026-07-06__rec_002327": "omnina_preprint",
    "full_2026-07-06__rec_003394": "omnina",
    "full_2026-07-06__rec_001830": "opticaldna",
    "full_2026-07-06__rec_000086": "procyon",
    "july_update_2026-07-06__rec_000050": "posttraining_bioreasoning",
    "june_update_2026-06-10__rec_000121": "rvqalpha",
    "full_2026-07-06__rec_001343": "scdiff",
    "june_update_2026-06-10__rec_000148": "scicoreomics",
    "update_2026-08-09__rec_000106": "scmir",
    "full_2026-07-06__rec_001889": "scmoba",
    "full_2026-07-06__rec_001200": "shusi",
    "full_2026-07-06__rec_000063": "tissuenarrator",
    "full_2026-07-06__rec_003517": "xcell",
    "update_2026-08-09__manual_recall_xunzi": "xunzi",
    "july_update_2026-07-06__rec_000060": "celltosg2sequence",
    "full_2026-07-06__rec_000060": "tissuecraftai",
}
# Two records share the number rec_000060 in different collection batches; they are told apart by title.
TITLE_KEYS = {
    "celltosg2sequence": "celltosg2sequence",
    "query-driven generative ai synthesizes": "tissuecraftai",
}

# Named but not included works: key -> (identifier, expected title words, role in the manuscript).
EXTERNAL = {
    "prisma_scr": ("doi:10.7326/M18-0850", "PRISMA Extension for Scoping Reviews", "reporting guideline"),
    "prisma_s": ("doi:10.1186/s13643-020-01542-z", "PRISMA-S", "search reporting guideline"),
    "press": ("doi:10.1016/j.jclinepi.2016.01.021", "PRESS Peer Review of Electronic Search Strategies", "search peer review guideline"),
    "docling": ("arxiv:2408.09869", "Docling Technical Report", "full-text conversion tool"),
    "lora": ("arxiv:2106.09685", "LoRA", "adaptation method"),
    "scgpt": ("doi:10.1038/s41592-024-02201-0", "scGPT", "comparator model"),
    "geneformer": ("doi:10.1038/s41586-023-06139-9", "Transfer learning enables predictions in network biology", "comparator model"),
    "esm2": ("doi:10.1126/science.ade2574", "Evolutionary-scale prediction of atomic-level protein structure", "comparator model"),
    "nicheformer": ("doi:10.1101/2024.04.15.589472", "Nicheformer", "comparator model"),
    "llama2": ("arxiv:2307.09288", "Llama 2", "comparator model"),
    "gpt4o": ("arxiv:2410.21276", "GPT-4o System Card", "comparator model"),
    "tahoe100m": ("doi:10.1101/2025.02.20.639398", "Tahoe-100M", "dataset of a missed comparison"),
    "llm4cell": ("arxiv:2510.07793", "LLM4Cell", "existing review"),
    "proteindt": ("arxiv:2302.04611", "text-guided protein design", "coverage check (not retrieved)"),
    "biot5": ("arxiv:2310.07276", "BioT5", "coverage check (not retrieved)"),
    "biot5plus": ("arxiv:2402.17810", "BioT5+", "coverage check (not retrieved)"),
    "naturelm": ("arxiv:2502.07527", "Nature Language Model", "coverage check (not retrieved)"),
    "evolla": ("doi:10.1101/2025.01.05.630192", "protein", "coverage check (not retrieved)"),
    "galactica": ("arxiv:2211.09085", "Galactica", "coverage check (not retrieved)"),
    "instructprotein": ("arxiv:2310.03269", "InstructProtein", "coverage check (not retrieved)"),
    "protllm": ("arxiv:2403.07920", "ProtLLM", "coverage check (not retrieved)"),
    "prot2text": ("arxiv:2307.14367", "Prot2Text", "coverage check (not retrieved)"),
    "prott3": ("arxiv:2405.12564", "ProtT3", "coverage check (not retrieved)"),
    "prollama": ("arxiv:2402.16445", "ProLLaMA", "coverage check (not retrieved)"),
    "txgemma": ("arxiv:2504.06196", "TxGemma", "coverage check (not retrieved)"),
}

ARXIV_NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def norm(text: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def similarity(a: str, b: str) -> float:
    return round(difflib.SequenceMatcher(None, norm(a), norm(b)).ratio(), 3)


def http_get(url: str, accept: str | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept} if accept else {})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception:  # retry transient failures, then re-raise
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(url)


def load_records(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    return data["records"] if isinstance(data, dict) and "records" in data else data


def included_records() -> list[dict]:
    atlas = json.loads(ATLAS.read_text())
    records: dict[str, dict] = {}
    for model in atlas["architectures"]:
        rec = records.setdefault(model["record_id"], {
            "record_id": model["record_id"], "title": model["paper_title"],
            "doi": model.get("doi") or "", "models": []})
        rec["models"].append(model["model_name"])
    master: dict[str, dict] = {}
    for path in MASTER_FILES:
        for row in load_records(path):
            master.setdefault(norm(row.get("title")), row)
    out = []
    for rec in records.values():
        key = INCLUDED_KEYS.get(rec["record_id"])
        if key is None:
            title = rec["title"].lower()
            key = next((v for k, v in TITLE_KEYS.items() if title.startswith(k)), None)
        if key is None:
            raise SystemExit(f"no citation key for {rec['record_id']}: {rec['title']}")
        row = master.get(norm(rec["title"]), {})
        doi = rec["doi"] or row.get("doi") or ""
        arxiv = row.get("arxiv_id") or ""
        url = row.get("url") or ""
        if not arxiv and "arxiv.org/abs/" in url:
            arxiv = url.rsplit("/abs/", 1)[1]
        if not doi:
            m = re.search(r"(10\.\d{4,9}/[^\s?#]+?)(?:\.abstract|\.full|v\d+)?(?:$|[?#])", url)
            if m and "arxiv" not in m.group(1).lower():
                doi = m.group(1)
        if doi.lower().startswith("10.48550/arxiv."):
            arxiv = arxiv or doi.split("arXiv.", 1)[-1]
            doi = ""
        arxiv = re.sub(r"v\d+$", "", arxiv)
        out.append({**rec, "key": key, "doi": doi, "arxiv": arxiv, "url": url, "master": row})
    if len(out) != 55 or len({r["key"] for r in out}) != 55:
        raise SystemExit(f"expected 55 records with unique keys, got {len(out)}")
    return out


def cached_json(name: str, url: str, offline: bool) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / name
    if not path.exists():
        if offline:
            raise SystemExit(f"missing cache file {path.name}")
        path.write_bytes(http_get(url))
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_doi(rec: dict, offline: bool) -> tuple[str, str]:
    """DOI for records whose metadata carry none: PMC articles through Europe PMC, others by an
    exact-title Crossref query (accepted only at title similarity >= 0.95)."""
    pmc = re.search(r"(PMC\d+)", rec["url"])
    if pmc:
        data = cached_json(f"europepmc_{pmc.group(1)}.json",
                           "https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&query=PMCID:" + pmc.group(1), offline)
        hits = data.get("resultList", {}).get("result", [])
        if hits and hits[0].get("doi"):
            return hits[0]["doi"], f"Europe PMC {pmc.group(1)}"
    if "ieeexplore" in rec["url"] or "openreview" in rec["url"]:
        q = urllib.parse.quote(rec["title"])
        data = cached_json(f"crossref_title_{rec['key']}.json",
                           f"https://api.crossref.org/works?rows=5&query.bibliographic={q}", offline)
        for item in data.get("message", {}).get("items", []):
            title = (item.get("title") or [""])[0]
            if similarity(title, rec["title"]) >= 0.95:
                return item["DOI"], "Crossref title query"
    return "", ""


def posted_content_label(doi: str, offline: bool) -> str:
    """Server name of a posted-content DOI (bioRxiv, medRxiv) from the Crossref work record."""
    data = cached_json("crossref_work_" + re.sub(r"[^A-Za-z0-9._-]", "_", doi) + ".json",
                       f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}", offline)
    msg = data.get("message", {})
    if msg.get("type") != "posted-content":
        return ""
    names = [i.get("name", "") for i in msg.get("institution", []) if i.get("name")]
    return names[0] if names else "Preprint server"


def fetch(identifier: str, offline: bool) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    kind, value = identifier.split(":", 1)
    path = CACHE / (re.sub(r"[^A-Za-z0-9._-]", "_", identifier) + (".bib" if kind == "doi" else ".xml"))
    if path.exists() or offline:
        return path
    if kind == "doi":
        url = f"https://api.crossref.org/works/{urllib.parse.quote(value, safe='/')}/transform/application/x-bibtex"
        path.write_bytes(http_get(url))
    else:
        url = f"https://export.arxiv.org/api/query?id_list={value}&max_results=1"
        path.write_bytes(http_get(url))
        time.sleep(3)  # arXiv API etiquette
    return path


def bib_escape(text: str) -> str:
    return re.sub(r"\s+", " ", text).replace("&", r"\&").replace("%", r"\%").replace("#", r"\#").strip()


def arxiv_entry(key: str, path: Path) -> tuple[str, str]:
    root = ET.fromstring(path.read_bytes())
    entry = root.find("a:entry", ARXIV_NS)
    if entry is None or entry.find("a:title", ARXIV_NS) is None:
        raise SystemExit(f"arXiv record missing for {key} ({path.name})")
    title = bib_escape(entry.findtext("a:title", "", ARXIV_NS))
    authors = " and ".join(bib_escape(a.findtext("a:name", "", ARXIV_NS)) for a in entry.findall("a:author", ARXIV_NS))
    year = entry.findtext("a:published", "", ARXIV_NS)[:4]
    arxiv_id = re.sub(r"v\d+$", "", entry.findtext("a:id", "", ARXIV_NS).rsplit("/abs/", 1)[-1])
    fields = {
        "author": authors, "title": "{" + title + "}", "year": year,
        "howpublished": f"arXiv:{arxiv_id}", "eprint": arxiv_id, "archiveprefix": "arXiv",
    }
    body = ",\n".join(f"  {k} = {{{v}}}" if not v.startswith("{") else f"  {k} = {v}" for k, v in fields.items())
    return f"@misc{{{key},\n{body}\n}}\n", title


def crossref_entry(key: str, path: Path, label: str = "") -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").strip()
    if not text.startswith("@"):
        raise SystemExit(f"Crossref BibTeX missing for {key} ({path.name})")
    text = re.sub(r"^@(\w+)\{[^,]*,", lambda m: f"@{m.group(1)}{{{key},", text, count=1)
    # Crossref titles can carry JATS/HTML markup (<i>, <sup>) and line breaks.
    text = re.sub(r"title=\{(.*?)\}, (?=\w+=)", lambda m: "title={" + re.sub(r"\s+([:;,.])", r"\1", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1)))).strip() + "}, ", text, count=1, flags=re.S)
    if label:  # posted content: Crossref gives no journal, so name the preprint server
        text = re.sub(r"^@\w+\{", "@misc{", text, count=1)
        text = re.sub(r"publisher=\{[^}]*\}", "publisher={" + label + "}", text, count=1)
        text = text.rstrip().rstrip("}").rstrip().rstrip(",") + ", howpublished={Preprint} }"
    text = re.sub(r",\s*month=\w+", "", text)  # months are not printed and some names are not .bst macros
    # the DOI is printed by the style (doi:...); the Crossref resolver URL would repeat it
    text = re.sub(r"\burl=\{http://dx\.doi\.org/[^}]*\},\s*", "", text, count=1)
    title = re.search(r"title=\{(.*?)\}, \w+=", text, re.S)
    return text + "\n", (title.group(1) if title else "")


def manual_entry(key: str, rec: dict) -> tuple[str, str]:
    row = rec["master"]
    authors = row.get("authors") or []
    authors = authors if isinstance(authors, list) else [a.strip() for a in str(authors).split(";")]
    if key == "cell2text_thesis":
        authors = ["Aris Markogiannakis"]  # full name from the thesis file name and the arXiv Cell2Text author list
    fields = {
        "author": " and ".join(bib_escape(a) for a in authors),
        "title": "{" + bib_escape(rec["title"]) + "}",
        "year": str(row.get("year") or ""),
        "howpublished": "Thesis, National Technical University of Athens" if "ntua" in rec["url"] else (row.get("venue") or ""),
        "url": rec["url"],
    }
    body = ",\n".join(f"  {k} = {v}" if v.startswith("{") else f"  {k} = {{{v}}}" for k, v in fields.items() if v)
    return f"@misc{{{key},\n{body}\n}}\n", rec["title"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    entries: list[str] = []
    audit: list[dict] = []
    for rec in included_records():
        how = ""
        if not rec["doi"] and not rec["arxiv"]:
            rec["doi"], how = resolve_doi(rec, args.offline)
        if rec["doi"]:
            ident = f"doi:{rec['doi']}" + (f" (via {how})" if how else "")
            entry, fetched = crossref_entry(rec["key"], fetch(f"doi:{rec['doi']}", args.offline),
                                            posted_content_label(rec["doi"], args.offline))
        elif rec["arxiv"]:
            ident = f"arxiv:{rec['arxiv']}"
            entry, fetched = arxiv_entry(rec["key"], fetch(ident, args.offline))
        else:
            ident = f"url:{rec['url']}"
            entry, fetched = manual_entry(rec["key"], rec)
        if rec["key"] == "okrcell":
            entry = entry.rstrip().rstrip("}").rstrip().rstrip(",") + ", note={Withdrawn preprint} }\n"
        entries.append(entry)
        audit.append({"key": rec["key"], "kind": "included", "record_id": rec["record_id"], "identifier": ident,
                      "corpus_title": rec["title"], "fetched_title": fetched,
                      "title_similarity": similarity(rec["title"], fetched)})
    for key, (ident, expect, role) in EXTERNAL.items():
        path = fetch(ident, args.offline)
        if ident.startswith("doi:"):
            entry, fetched = crossref_entry(key, path, posted_content_label(ident[4:], args.offline))
        else:
            entry, fetched = arxiv_entry(key, path)
        entries.append(entry)
        audit.append({"key": key, "kind": f"named: {role}", "record_id": "", "identifier": ident,
                      "corpus_title": expect, "fetched_title": fetched,
                      "title_similarity": 1.0 if norm(expect) in norm(fetched) else 0.0})
    (OUT / "references.bib").write_text("% Generated by scripts/build_manuscript_references.py; do not edit by hand.\n\n" + "\n".join(entries), encoding="utf-8")
    with (OUT / "references_audit.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(audit[0]))
        writer.writeheader()
        writer.writerows(audit)
    low = [a for a in audit if a["title_similarity"] < 0.9]
    print(json.dumps({"entries": len(entries), "included": sum(a["kind"] == "included" for a in audit),
                      "named": sum(a["kind"] != "included" for a in audit),
                      "title_checks_below_0.9": [(a["key"], a["title_similarity"]) for a in low]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
