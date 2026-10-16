#!/usr/bin/env python3
"""Map every block of the previous manuscript version to its place in the journal version.

A block is a paragraph, a list item or a table. Each block of the old Markdown master (default: the
archived v0.5.1, manuscript/archive/review_manuscript_draft_v0.5.1.md) is compared with every block of
the resolved journal version (manuscript/build/manuscript.md and supplementary_information.md; generated
tables and verbatim search strings are compared too, because some old text became a generated table).

For each old block the script reports the new block that covers most of its content words (coverage =
share of the old block's content words found in the new block) and the new section that covers most
(union of the section's blocks). The status is

  kept or moved       best block covers at least 0.6 of the old block;
  reworded or split   best section covers at least 0.5;
  condensed           best section covers 0.3-0.5;
  not carried over    below 0.3 (listed for reading; the reason is given in the move-list notes).

Usage:
    python scripts/manuscript_move_list.py --out-csv manuscript/journal_rewrite/move_list.csv
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = set("the a an of in and or to for by with from on at is are was were be as that this these those it its their "
           "than which who whose not no only all each per both one two we our they them into also but has have had "
           "can could would should may more most less such other than then there here".split())


def content_words(text: str) -> set[str]:
    text = re.sub(r"<!--.*?-->", " ", text)
    text = re.sub(r"\[\[S:[a-z_]+\]\]|`[^`]*`|https?://\S+", " ", text)
    return {w for w in re.findall(r"[a-z][a-z0-9\-]+|\d[\d.,]*", text.lower()) if w not in STOP and len(w) > 1}


def blocks(path: Path, label: str) -> list[dict]:
    out, h2, h3 = [], "", ""
    lines = path.read_text(encoding="utf-8").split("\n")
    if lines and lines[0] == "---":  # YAML header
        end = lines.index("---", 1)
        lines = lines[end + 1:]
    buf: list[str] = []

    def flush():
        text = " ".join(" ".join(buf).split())
        if text and not text.startswith("<!--") and text not in ("\\newpage",):
            out.append({"file": label, "section": " > ".join(x for x in (h2, h3) if x), "text": text})
        buf.clear()

    in_code = False
    for line in lines:
        if line.startswith("```"):
            in_code = not in_code
            buf.append(line)
            if not in_code:
                flush()
            continue
        if in_code:
            buf.append(line)
            continue
        if re.match(r"^#{1,6} ", line):
            flush()
            level = len(line) - len(line.lstrip("#"))
            title = re.sub(r"^\d+(\.\d+)*\.?\s*", "", line.lstrip("#").strip())
            if level <= 2:
                h2, h3 = title, ""
            elif level == 3:
                h3 = title
            continue
        if not line.strip():
            flush()
            continue
        if re.match(r"^(\s{0,1})([-*]|\d+\.)\s", line) and buf and not buf[0].startswith("|"):
            flush()  # a new top-level list item starts a block
        if line.startswith("|") and buf and not buf[0].startswith("|"):
            flush()
        buf.append(line.strip())
    flush()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", type=Path, default=ROOT / "manuscript/archive/review_manuscript_draft_v0.5.1.md")
    ap.add_argument("--new", type=Path, action="append",
                    default=None, help="resolved Markdown files of the journal version")
    ap.add_argument("--out-csv", type=Path, required=True)
    args = ap.parse_args()
    new_files = args.new or [ROOT / "manuscript/build/manuscript.md", ROOT / "manuscript/build/supplementary_information.md"]
    old = blocks(args.old, "previous version")
    new = []
    for p in new_files:
        new += blocks(p, "article" if p.name == "manuscript.md" else "Supplementary Information")
    for b in old + new:
        b["words"] = content_words(b["text"])
    sections: dict[tuple[str, str], set[str]] = {}
    for b in new:
        sections.setdefault((b["file"], b["section"]), set()).update(b["words"])
    rows = []
    for i, b in enumerate(old, 1):
        w = b["words"]
        if not w:
            continue
        best = max(new, key=lambda n: len(w & n["words"]) / len(w))
        cov_block = len(w & best["words"]) / len(w)
        sec_key, sec_words = max(sections.items(), key=lambda kv: len(w & kv[1]) / len(w))
        cov_sec = len(w & sec_words) / len(w)
        if cov_block >= 0.6:
            status = "kept or moved"
        elif cov_sec >= 0.5:
            status = "reworded or split"
        elif cov_sec >= 0.3:
            status = "condensed"
        else:
            status = "not carried over"
        rows.append({"old_block": i, "old_section": b["section"], "old_text": b["text"],
                     "new_file": best["file"] if cov_block >= cov_sec * 0.6 else sec_key[0],
                     "new_section": best["section"] if cov_block >= cov_sec * 0.6 else sec_key[1],
                     "best_block_coverage": round(cov_block, 2), "best_section": f"{sec_key[0]}: {sec_key[1]}",
                     "best_section_coverage": round(cov_sec, 2), "status": status, "new_text": best["text"]})
    with open(args.out_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(len(rows), dict(Counter(r["status"] for r in rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
