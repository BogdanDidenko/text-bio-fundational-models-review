#!/usr/bin/env python3
"""Probe the 2026-02-16..2026-02-28 window with the executed baseline queries of the keyless sources.

Why: the baseline (v3.1) search was executed on 2026-02-15 with a declared end date of 2026-02-28, and the
first update round started on 2026-03-01. The declared windows are contiguous, but no date-bounded query was
executed after 2026-02-15 for publications dated 2026-02-16..2026-02-28.

What: re-runs the exact v3.1 query strings of PubMed, arXiv, Europe PMC (bioRxiv/medRxiv) and Semantic
Scholar with only the date range changed, then matches each hit against every record retrieved in the five
search rounds that fed screening (DOI, arXiv ID, normalised title), and records which round and source
captured the matched ones. Scopus, SpringerNature, OpenAlex and Google Scholar need API keys and are not probed.

This is a coverage check, not a search round: hits are not screened or added to the corpus.
Output: analysis/prisma_search_audit_2026-10-14/gap_probe_2026-02-16_28.json
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/prisma_search_audit_2026-10-14/gap_probe_2026-02-16_28.json"
START, END = "2026-02-16", "2026-02-28"
ROUNDS = {"baseline_2026-02-15": "data/exports_v31",
          "april_2026-04-14": "data/exports_update",
          "june_2026-06-10": "analysis/codex_screening_run_artifacts_20260706/inputs/exports_update_2026-06-10",
          "july_2026-07-06": "analysis/codex_screening_run_artifacts_20260706/inputs/exports_update_2026-07-06",
          "august_2026-08-10": "data/living_catalog_updates/update_2026-08-09/00_search/exports"}
UA = {"User-Agent": "scoping-review-coverage-check/1.0"}
ARXIV_CATS = "cat:cs.LG OR cat:cs.AI OR cat:cs.CL OR cat:q-bio.GN OR cat:q-bio.QM OR cat:stat.ML"


def records(d):
    return d if isinstance(d, list) else (d.get("records") or d.get("results") or d.get("papers") or [])


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def clean_doi(x):
    return str(x or "").lower().replace("https://doi.org/", "").strip()


def corpus_index():
    """key -> list of (round, export file, date fields) for every record retrieved in a screening round."""
    idx = {}
    for rnd, folder in ROUNDS.items():
        for f in sorted((ROOT / folder).glob("*.json")):
            if "summary" in f.name or "raw" in f.name:
                continue
            for r in records(json.loads(f.read_text())):
                keys = set()
                if r.get("doi"):
                    keys.add(clean_doi(r["doi"]))
                for k in ("arxiv_id", "arxivId", "id"):
                    m = re.search(r"(\d{4}\.\d{4,5})", str(r.get(k) or ""))
                    if m:
                        keys.add(m.group(1))
                if r.get("title"):
                    keys.add(norm(r["title"]))
                date = {k: r.get(k) for k in ("date", "publication_date", "publicationDate", "year") if r.get(k)}
                for k in keys:
                    idx.setdefault(k, []).append({"round": rnd, "file": f.name, "date": date})
    return idx


def get(url, data=None, headers=None, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=120) as h:
                return h.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and i < tries - 1:
                time.sleep(int(e.headers.get("Retry-After") or 0) or 5 * (i + 1))
                continue
            raise


def pubmed(q):
    q = re.sub(r'"\d{4}/\d{2}/\d{2}"\[Date - Publication\]\s*:\s*"\d{4}/\d{2}/\d{2}"\[Date - Publication\]',
               f'"{START.replace("-", "/")}"[Date - Publication] : "{END.replace("-", "/")}"[Date - Publication]', q)
    es = json.loads(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", urllib.parse.urlencode(
        {"db": "pubmed", "term": q, "retmax": 1000, "retmode": "json"}).encode()))
    ids, out = es["esearchresult"]["idlist"], []
    if ids:
        xml = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(ids), "retmode": "xml"}).encode())
        for art in ET.fromstring(xml).iter("PubmedArticle"):
            t = art.find(".//ArticleTitle")
            out.append({"title": "".join(t.itertext()) if t is not None else "",
                        "doi": clean_doi(next((e.text for e in art.iter("ArticleId") if e.get("IdType") == "doi"), "")),
                        "pmid": art.findtext(".//PMID"),
                        "abstract": " ".join("".join(a.itertext()) for a in art.iter("AbstractText"))})
    return {"query": q, "api_count": int(es["esearchresult"]["count"]), "records": out}


def arxiv(queries):
    ns, out, seen = {"a": "http://www.w3.org/2005/Atom"}, [], set()
    for name, q in queries.items():
        full = f"({q}) AND ({ARXIV_CATS}) AND submittedDate:[{START.replace('-', '')}0000 TO {END.replace('-', '')}2359]"
        start = 0
        while True:
            root = ET.fromstring(get("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
                {"search_query": full, "start": start, "max_results": 200})))
            entries = root.findall("a:entry", ns)
            for e in entries:
                m = re.search(r"(\d{4}\.\d{4,5})", e.findtext("a:id", "", ns) or "")
                if m and m.group(1) not in seen:
                    seen.add(m.group(1))
                    out.append({"title": " ".join((e.findtext("a:title", "", ns) or "").split()), "arxiv_id": m.group(1),
                                "date": (e.findtext("a:published", "", ns) or "")[:10], "subquery": name,
                                "abstract": " ".join((e.findtext("a:summary", "", ns) or "").split())})
            if len(entries) < 200:
                break
            start += 200
            time.sleep(3)
        time.sleep(3)
    return {"queries": queries, "api_count": len(out), "records": out}


def europepmc(q):
    q = re.sub(r"FIRST_PDATE:\[[^\]]+\]", f"FIRST_PDATE:[{START} TO {END}]", q)
    out, cursor = [], "*"
    while True:
        d = json.loads(get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": q, "format": "json", "pageSize": 1000, "cursorMark": cursor, "resultType": "core"})))
        res = d.get("resultList", {}).get("result", [])
        for r in res:
            out.append({"title": r.get("title", ""), "doi": clean_doi(r.get("doi")), "date": r.get("firstPublicationDate"),
                        "abstract": re.sub("<[^>]+>", "", r.get("abstractText") or "")})
        nxt = d.get("nextCursorMark")
        if not res or not nxt or nxt == cursor:
            break
        cursor = nxt
    return {"query": q, "api_count": d.get("hitCount"), "records": out}


def semantic_scholar(q):
    out, token = [], None
    while True:
        params = {"query": q, "publicationDateOrYear": f"{START}:{END}",
                  "fields": "title,externalIds,publicationDate,abstract"}
        if token:
            params["token"] = token
        d = json.loads(get("https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(params)))
        for p in d.get("data", []):
            ext = p.get("externalIds") or {}
            out.append({"title": p.get("title") or "", "doi": clean_doi(ext.get("DOI")), "arxiv_id": ext.get("ArXiv") or "",
                        "date": p.get("publicationDate"), "abstract": p.get("abstract") or ""})
        token = d.get("token")
        if not token:
            break
        time.sleep(3)
    return {"query": q, "api_count": d.get("total"), "records": out}


def keys_of(r):
    return [k for k in (r.get("doi"), r.get("arxiv_id"), norm(r.get("title"))) if k]


def main():
    base = ROOT / "data/exports_v31"
    q = {s: json.loads((base / f).read_text()) for s, f in
         {"pubmed": "pubmed_2026-02-15.json", "arxiv": "arxiv_2026-02-15.json",
          "europepmc": "biorxiv_medrxiv_2026-02-15.json", "s2": "semantic_scholar_2026-02-15.json"}.items()}
    idx = corpus_index()
    res = {"window": [START, END], "rounds_matched": ROUNDS,
           "not_probed": ["Scopus (API key)", "SpringerNature (API key)", "OpenAlex (API key; August only)",
                          "Google Scholar (SerpAPI key; year-level 2026 queries ran in April, June and August)"],
           "sources": {"PubMed": pubmed(q["pubmed"]["query"]), "arXiv": arxiv(q["arxiv"]["queries"]),
                       "Europe PMC": europepmc(q["europepmc"]["query"]),
                       "Semantic Scholar": semantic_scholar(q["s2"]["query"])}}
    unique_missing = []
    for src, block in res["sources"].items():
        for r in block["records"]:
            hits = [h for k in keys_of(r) for h in idx.get(k, [])]
            r["in_corpus"] = bool(hits)
            r["captured_by"] = sorted({f'{h["round"]}:{h["file"].split("_20")[0]}' for h in hits})
            if hits:
                continue
            for u in unique_missing:
                if set(keys_of(u)) & set(keys_of(r)):
                    u["sources"].append(src)
                    u["abstract"] = u["abstract"] or r.get("abstract", "")
                    break
            else:
                unique_missing.append({**{k: r.get(k, "") for k in ("title", "doi", "arxiv_id", "date", "abstract")},
                                       "sources": [src]})
        block["hits"] = len(block["records"])
        block["in_corpus"] = sum(r["in_corpus"] for r in block["records"])
    res["unique_not_in_corpus"] = unique_missing
    route, unique_in = {}, []
    for src, block in res["sources"].items():
        for r in block["records"]:
            for c in r["captured_by"]:
                route[c] = route.get(c, 0) + 1
            if not r["in_corpus"]:
                continue
            for u in unique_in:
                if set(u["keys"]) & set(keys_of(r)):
                    u["keys"] = sorted(set(u["keys"]) | set(keys_of(r)))
                    u["sources"].append(src)
                    u["captured_by"] = sorted(set(u["captured_by"]) | set(r["captured_by"]))
                    break
            else:
                unique_in.append({"title": r["title"], "keys": keys_of(r), "sources": [src],
                                  "captured_by": r["captured_by"]})
    for u in unique_in:
        u["via_google_scholar"] = any("google_scholar" in c for c in u["captured_by"])
    res["unique_in_corpus"] = unique_in
    res["summary"] = {"per_source": {s: {"hits": b["hits"], "api_count": b["api_count"], "in_corpus": b["in_corpus"]}
                                     for s, b in res["sources"].items()},
                      "hits_total": sum(b["hits"] for b in res["sources"].values()),
                      "in_corpus_total": sum(b["in_corpus"] for b in res["sources"].values()),
                      "unique_in_corpus": len(unique_in),
                      "unique_in_corpus_via_google_scholar": sum(u["via_google_scholar"] for u in unique_in),
                      "unique_in_corpus_only_via_date_bounded_sources": sum(not u["via_google_scholar"] for u in unique_in),
                      "unique_not_in_corpus": len(unique_missing),
                      "unique_not_in_corpus_with_abstract": sum(bool(u["abstract"]) for u in unique_missing),
                      "capture_routes_of_in_corpus_hits": dict(sorted(route.items(), key=lambda x: -x[1]))}
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps(res["summary"], indent=1))


if __name__ == "__main__":
    main()
