#!/usr/bin/env python3
"""Count internal labels in the prose of paper 1, by category and section.

An internal label is a token that a reader cannot interpret without the project's files: record or
study identifiers, codes of criteria, axes, archetypes or cultures, protocol and release versions,
section symbols, file paths and file names, commit hashes, run names, snake_case values, the names of
the review's own tools and models, and draft placeholders.

Usage:
    python scripts/manuscript_label_census.py --md <manuscript.md> [--md <supplement.md>] \
        [--tex-frontmatter <main.tex>] --out <census.csv> [--allowed]

Sections are the level-2 headings of each Markdown file (plus "Front matter (main.tex)" when a LaTeX
file is given; only its \\abstract{...} and Key Points are read). With --allowed, the agreed
exceptions are not counted as violations (they are still reported in the census):
  * tool and model names in Methods and in the Supplementary Information;
  * the protocol archive identifier in Methods;
  * paths, file names, commit hashes, versions and URLs in "Data and code availability";
  * identifiers in dedicated identifier columns of supplementary tables (not part of the prose).
Generated blocks (between "<!-- generated: ... -->" and "<!-- end generated -->", written by
scripts/build_manuscript.py: tables, the data-file list, the search strings) and fenced code blocks
(verbatim query strings) are not prose. They are counted under "<section> [generated or verbatim]" and
never treated as violations.
Draft placeholders ([CITE ...], [TODO ...]) are counted separately and never treated as violations.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

CATEGORIES: list[tuple[str, re.Pattern[str]]] = [
    # tool names first, so that a model name in a code span is not counted as a file name
    ("review tool or model name", re.compile(r"\bgpt-5\.\d(?:-[a-z]+)?\b|\bCodex(?: CLI)?\b|\bDocling(?: Graph)?\b|\bLatteReview\b|\bSerpAPI\b|`scholarly`|\bscholarly Python\b")),
    ("record or study identifier", re.compile(r"\b(?:full|june_update|july_update|update)_2026-\d\d-\d\d__(?:rec_\d+|manual_recall_\w+)\b|\brec_\d{3,6}\b|\bW_[a-z0-9]+\b")),
    ("criterion code", re.compile(r"\b(?:EC|IC)[1-8]\b")),
    ("axis, archetype, family or motif code", re.compile(r"\b(?:A[1-5]|F[1-5]|M\d{2}|G[1-3])\b|\b(?:VERB|SOFT|COND|SYMB|XATT|ALIGN|UNRES|OTHER_TOK)\b")),
    ("culture code", re.compile(r"\((?:T|E|H|C|A)\)|\b(?:T|E|H|C|A)-only\b")),
    ("protocol, release or deviation number", re.compile(r"\bv\d+(?:\.\d+)+\b|\b(?:release|library) \d+\.\d+\.\d+\b|\b\d+\.\d+\.\d+\b|\b[a-z]+(?:-[a-z]+)+-v\d+(?:\.\d+)?\b|\bF\d{2,3}\b")),
    ("section symbol", re.compile(r"§\s?\d+(?:\.\d+)*(?:[–-]\d+(?:\.\d+)*)?")),
    ("file path or file name", re.compile(r"`[^`\s]*[/.][^`\s]*`|\b(?:analysis|data|scripts|protocol|manuscript|docs|config|tests)/[\w./*-]+|\b[\w-]+\.(?:md|csv|json|jsonl|py|png|pdf|txt|tex|bib|parquet|svg)\b")),
    ("commit hash", re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")),
    ("run name", re.compile(r"\b(?:v3\d_[a-z0-9_]+|heldout\d+|run_\d+|r\d_[a-z_]+|discovery_open_r\d|all50|rest30)\b")),
    ("snake_case value", re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")),
]
PLACEHOLDER = re.compile(r"\[(?:CITE|TODO)[^\]]*\]")

ALLOWED = {
    # category -> predicate(section) that allows it
    "review tool or model name": lambda s: s.startswith("Methods") or s.startswith("Supplementary"),
    "file path or file name": lambda s: s.startswith("Data and code availability"),
    "commit hash": lambda s: s.startswith("Data and code availability"),
    "protocol, release or deviation number": lambda s: s.startswith("Data and code availability") or s.startswith("Methods") or s.startswith("Supplementary"),
}


def strip_urls(text: str) -> str:
    return re.sub(r"<?https?://\S+>?", " ", text)


GENERATED = " [generated or verbatim]"


def sections_of_md(path: Path, prefix: str = "") -> list[tuple[str, str]]:
    out, name, buf, gen = [], prefix + "Title and draft note", [], []
    in_code = in_generated = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.fullmatch(r"<!-- generated:.*-->\s*", line) and "<!-- end generated" not in line:
            in_generated = True
            continue
        if re.fullmatch(r"<!-- end generated -->\s*", line):
            in_generated = False
            continue
        if not in_generated:
            # inline generated values (row counts, build commit) are kept; the comment markers are dropped
            line = re.sub(r"<!--.*?-->", "", line)
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or in_generated:
            gen.append(line)
            continue
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            out += [(name, "\n".join(buf))] + ([(name + GENERATED, "\n".join(gen))] if gen else [])
            name, buf, gen = prefix + re.sub(r"^\d+\.\s*", "", m.group(1)).strip(), [], []
        else:
            buf.append(line)
    out += [(name, "\n".join(buf))] + ([(name + GENERATED, "\n".join(gen))] if gen else [])
    if in_code or in_generated:
        raise SystemExit(f"{path}: unterminated code or generated block")
    return out


def sections_of_tex(path: Path) -> list[tuple[str, str]]:
    t = path.read_text(encoding="utf-8")
    out = []
    m = re.search(r"\\abstract\{(.*?)\}\n", t, re.S)
    if m:
        out.append(("Abstract (main.tex)", m.group(1)))
    m = re.search(r"\\section\*\{Key Points\}(.*?)\\end\{itemize\}", t, re.S)
    if m:
        out.append(("Key Points (main.tex)", m.group(1)))
    return out


def census(sections: list[tuple[str, str]], use_allowed: bool):
    counts = defaultdict(Counter)
    examples = defaultdict(list)
    violations = Counter()
    placeholders = Counter()
    status: dict = {}
    for sec, text in sections:
        text = strip_urls(text)
        placeholders[sec] += len(PLACEHOLDER.findall(text))
        text = PLACEHOLDER.sub(" ", text)
        taken: list[tuple[int, int]] = []
        for cat, rx in CATEGORIES:
            for m in rx.finditer(text):
                if any(a <= m.start() < b for a, b in taken):
                    continue  # one token, one category (first match wins)
                taken.append((m.start(), m.end()))
                counts[sec][cat] += 1
                examples[(sec, cat)].append(" ".join(m.group(0).split()))
                allowed = use_allowed and (sec.endswith(GENERATED) or ALLOWED.get(cat, lambda s: False)(sec))
                status[(sec, cat)] = "allowed" if allowed else "violation"
                if not allowed:
                    violations[sec] += 1
    census.status = status
    return counts, examples, violations, placeholders


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="append", type=Path, required=True)
    ap.add_argument("--tex-frontmatter", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--allowed", action="store_true")
    args = ap.parse_args()
    sections: list[tuple[str, str]] = []
    for i, p in enumerate(args.md):
        sections += sections_of_md(p, prefix="" if i == 0 else "Supplementary: ")
    if args.tex_frontmatter:
        sections += sections_of_tex(args.tex_frontmatter)
    counts, examples, violations, placeholders = census(sections, args.allowed)
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["section", "category", "count", "status", "examples"])
        for sec, _ in sections:
            for cat, _rx in CATEGORIES:
                n = counts[sec][cat]
                if n:
                    st = census.status.get((sec, cat), "") if args.allowed else ""
                    w.writerow([sec, cat, n, st, " | ".join(examples[(sec, cat)])])
    total = sum(sum(c.values()) for c in counts.values())
    by_cat = Counter()
    for c in counts.values():
        by_cat.update(c)
    print(f"labels: {total}; violations (after agreed exceptions): {sum(violations.values())}; placeholders: {sum(placeholders.values())}")
    for cat, n in by_cat.most_common():
        print(f"  {n:5d}  {cat}")
    bad = {s: n for s, n in violations.items() if n}
    if bad:
        print("violations by section:", bad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
