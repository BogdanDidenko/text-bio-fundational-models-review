#!/usr/bin/env python3
"""Check that every number in the rewritten paper 1 equals a number of the previous version.

The old version is read from Git (default commit 4c4db9f0: the Markdown master plus the abstract and
Key Points of main.tex); the new version from the Markdown files given with --new. Numbers are
normalised before comparison: thousands separators are removed, "4.9 × 10⁻⁴" becomes 4.9e-4, dates
written as "9 August 2026" become 2026-08-09, and number words ("Seventeen", "Twenty-five") become
digits, "v3.0" is read as 3.0, and versions such as 1.3.0 are read as one token. Ranges are split into
their ends. In the new text, generated blocks (between "<!-- generated: ... -->" and
"<!-- end generated -->": tables and lists built from the analysis files by scripts/build_manuscript.py),
fenced code blocks (verbatim search strings) and the YAML header are skipped, because their numbers are
not typed but read from the data.

For every number of the new text the script finds the old sentences that contain the same number and
scores how similar the sentences are (share of shared content words). It reports
  * numbers of the new text that do not occur in the old text (they must be listed in --allow-new,
    with a reason, or the check fails);
  * numbers whose best old context is dissimilar (to be read by a person);
  * numbers of the old text that occur nowhere in the new text (moved out or dropped).
Exit status 1 if a new number is neither in the old text nor allowed.

Usage:
    python scripts/manuscript_number_check.py --new <md> [--new <md> ...] [--old-commit 4c4db9f0] \
        [--allow-new allow.csv] --out report.md
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                         "september", "october", "november", "december"], 1)}
UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
STOP = set("the a an of in and or to for by with from on at is are was were be as that this these those it its their "
           "than which who whose not no only all each per both two one".split())


def git_show(commit: str, path: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"], capture_output=True, text=True, check=True).stdout


def typed_text(text: str) -> str:
    """Drop generated blocks, fenced code and a YAML header: their numbers come from the data files."""
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"<!-- generated:.*?<!-- end generated -->", " ", text, flags=re.S)
    text = re.sub(r"^```.*?^```", " ", text, flags=re.S | re.M)
    return text


def clean(text: str) -> str:
    text = re.sub(r"<?https?://\S+>?", " ", text)            # URLs
    text = re.sub(r"\bv(\d)", r"\1", text)                    # v3.0 -> 3.0
    text = re.sub(r"\[(?:CITE|TODO)[^\]]*\]", " ", text)     # draft placeholders
    text = re.sub(r"`[^`]*`", " ", text)                       # code spans: paths, file names, identifiers
    text = re.sub(r"\b(?:10\.\d{4,9}/\S+)", " ", text)        # DOIs
    text = re.sub(r"\b[0-9a-f]{7,40}\b", lambda m: " " if re.search(r"[a-f]", m.group(0)) and re.search(r"\d", m.group(0)) else m.group(0), text)
    text = text.replace("\\,", "").replace("~", " ").replace("--", "–")
    return text


def sentences(text: str) -> list[str]:
    """Sentences within paragraphs, headings and list items (blocks are split first)."""
    out = []
    for block in re.split(r"\n\s*\n|\n(?=#)|\n(?=\s*[-*] )|\n(?=\s*\d+\. )|\n(?=\|)", text):
        block = re.sub(r"\s+", " ", block).strip()
        out += [s.strip() for s in re.split(r"(?<=[.;:!?])\s+(?=[A-Z0-9(•\-*])|\s+-\s+", block) if s.strip()]
    return out


def numbers_in(sentence: str) -> list[str]:
    s = sentence.translate(SUP)
    out: list[str] = []
    # dates
    for m in re.finditer(r"\b(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4})\b", s, re.I):
        out.append(f"{m.group(3)}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}")
    s = re.sub(r"\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b", " ", s, flags=re.I)
    for m in re.finditer(r"\b(\d{4})-(\d{2})-(\d{2})\b", s):
        out.append(m.group(0))
    s = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", s)
    s = re.sub(r"\b(\d{2})-(\d{2})\b(?= to )", r" \1 \2 ", s)
    # versions (1.3.0, 2.110.0) as single tokens
    for m in re.finditer(r"(?<![\w.])\d+\.\d+\.\d+(?![\w.]*\d)", s):
        out.append(m.group(0))
    s = re.sub(r"(?<![\w.])\d+\.\d+\.\d+(?![\w.]*\d)", " ", s)
    # scientific notation
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*[×x]\s*10\s*\^?\s*(-?\d+)", s):
        out.append(f"{float(m.group(1)):g}e{int(m.group(2))}")
    s = re.sub(r"(\d+(?:\.\d+)?)\s*[×x]\s*10\s*\^?\s*(-?\d+)", " ", s)
    # number words (compound first)
    low = s.lower()
    for m in re.finditer(r"\b(" + "|".join(TENS) + r")[- ](" + "|".join(k for k in UNITS if UNITS[k] < 10 and UNITS[k] > 0) + r")\b", low):
        out.append(str(TENS[m.group(1)] + UNITS[m.group(2)]))
    low2 = re.sub(r"\b(" + "|".join(TENS) + r")[- ](" + "|".join(k for k in UNITS if 0 < UNITS[k] < 10) + r")\b", " ", low)
    for m in re.finditer(r"\b(" + "|".join(list(UNITS) + list(TENS)) + r")\b", low2):
        out.append(str({**UNITS, **TENS}[m.group(1)]))
    # plain numbers
    for m in re.finditer(r"(?<![\w.])[-−]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\w.])[-−]?\d*\.\d+|(?<![\w.])\d+", s):
        tok = m.group(0).replace(",", "").replace("−", "-")
        if tok.startswith("."):
            tok = "0" + tok
        out.append(tok)
    return out


def corpus(texts: list[str]):
    occ = defaultdict(list)  # number -> list of sentences
    for t in texts:
        for sent in sentences(clean(t)):
            for n in numbers_in(sent):
                occ[n].append(sent)
    return occ


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z\-]+", s.lower()) if w not in STOP and len(w) > 2}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", action="append", type=Path, required=True)
    ap.add_argument("--old-commit", default="4c4db9f024c518a0b7ed7bc8e9a901c61b3adedb")
    ap.add_argument("--allow-new", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--min-similarity", type=float, default=0.12)
    args = ap.parse_args()
    old_md = git_show(args.old_commit, "manuscript/review_manuscript_draft.md")
    old_tex = git_show(args.old_commit, "manuscript/latex/main.tex")
    tex_parts = re.findall(r"\\abstract\{(.*?)\}\n", old_tex, re.S) + re.findall(r"\\section\*\{Key Points\}(.*?)\\end\{itemize\}", old_tex, re.S)
    tex_parts = [re.sub(r"\\item\s*", "\n- ", p).replace("--", "–") for p in tex_parts]
    old = corpus([old_md] + tex_parts)
    new = corpus([typed_text(p.read_text(encoding="utf-8")) for p in args.new])
    allowed = {}
    if args.allow_new and args.allow_new.exists():
        for r in csv.DictReader(open(args.allow_new, encoding="utf-8")):
            allowed[r["number"]] = r["reason"]
    missing, unallowed, dissimilar = [], [], []
    for n, sents in sorted(new.items(), key=lambda kv: kv[0]):
        if n not in old:
            (missing if n in allowed else unallowed).append((n, sents[0]))
            continue
        trivial = re.fullmatch(r"\d", n) is not None
        for s in sents:
            if len(words(s)) < 3:
                continue  # headings and table-like fragments: too short to compare
            best = max((len(words(s) & words(o)) / max(1, len(words(s) | words(o))) for o in old[n]), default=0.0)
            if best < args.min_similarity and not trivial:
                dissimilar.append((n, round(best, 2), s))
    dropped = sorted(n for n in old if n not in new)
    lines = ["# Number check: rewritten manuscript against the previous version", "",
             f"Old version: commit `{args.old_commit[:8]}` (Markdown master, abstract and Key Points of main.tex).",
             f"New version: {', '.join(f'`{p.relative_to(ROOT) if p.is_absolute() and ROOT in p.parents else p}`' for p in args.new)}.", "",
             f"- Distinct numbers in the new text: {len(new)}; in the old text: {len(old)}.",
             f"- New numbers not in the old text and not allowed: **{len(unallowed)}**.",
             f"- New numbers allowed as intentional additions: {len(missing)}.",
             f"- Occurrences with a dissimilar best old context (for reading): {len(dissimilar)}.",
             f"- Old numbers that no longer occur in the new text: {len(dropped)}.", ""]
    if unallowed:
        lines += ["## Not in the old text (check failed)", "", "| Number | New sentence |", "|---|---|"]
        lines += [f"| {n} | {s.replace('|', '/')} |" for n, s in unallowed] + [""]
    if missing:
        lines += ["## Intentional additions", "", "| Number | Reason | New sentence |", "|---|---|---|"]
        lines += [f"| {n} | {allowed[n]} | {s.replace('|', '/')} |" for n, s in missing] + [""]
    if dissimilar:
        lines += ["## Dissimilar contexts (read and confirm)", "", "| Number | Best similarity | New sentence |", "|---|---:|---|"]
        lines += [f"| {n} | {b} | {s.replace('|', '/')} |" for n, b, s in dissimilar] + [""]
    lines += ["## Old numbers absent from the new text", "", ", ".join(dropped) if dropped else "None.", ""]
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"new={len(new)} old={len(old)} unallowed={len(unallowed)} allowed_new={len(missing)} dissimilar={len(dissimilar)} dropped={len(dropped)}")
    return 1 if unallowed else 0


if __name__ == "__main__":
    sys.exit(main())
