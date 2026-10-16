#!/usr/bin/env python3
"""Generate the LaTeX body of paper 1 from the Markdown master.

Input:  manuscript/build/manuscript.md, the resolved Markdown master written by
        scripts/build_manuscript.py (supplementary numbers filled in, build commit inserted)
Output: manuscript/latex/frontmatter.tex (abstract, keywords), keypoints.tex, body.tex,
        backmatter.tex (statements and biographical notes) and the figure files in
        manuscript/latex/figures/

The title page (authors, affiliations, correspondence) stays in manuscript/latex/main.tex; every
other part of the article comes from the Markdown master.

Conventions applied here:
  * each included work, guideline, tool or comparator named in the text is cited at its first
    mention (CITATIONS below; keys from manuscript/latex/references.bib), and all 55 included
    records are cited together where the inclusion count is reported (section 3.1);
  * [CITE ...] placeholders of the draft stay visible (red) for the author to resolve;
  * [TODO ...] placeholders are typeset with \todo (red);
  * the lists of the subsections "A neutral comparison protocol" and "A reporting card for input
    representations" are typeset as Box 1;
  * figure legends come from the "Figure legends" list.

Run through scripts/build_manuscript.py, which writes the resolved master first; on its own:
    python3 scripts/build_manuscript_latex.py
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "manuscript/build/manuscript.md"
OUT = ROOT / "manuscript/latex"
BIB = OUT / "references.bib"

FIGURES = {
    1: ["analysis/design_culture_charting_2026-10-14/v11/figures/figure1.pdf"],
    2: ["analysis/prisma_flow_2026-10-07/prisma_flow.png", "analysis/review_synthesis_2026-10-07/corpus_landscape.png"],
    3: ["analysis/design_culture_charting_2026-10-14/v11/figures/figure3.pdf"],
    4: ["analysis/design_culture_charting_2026-10-14/v11/figures/figure4.pdf"],
    5: ["analysis/design_culture_charting_2026-10-14/v11/figures/figure5.pdf"],
}
FIG2_DRAFT_NOTE = (
    r" \draftnote{Draft: the compact flow (a) and the works-per-culture breakdown are still to be made; the "
    r"panels shown are the full flow (left) and the current corpus panels (right).}"
)
FRONT = ("Abstract", "Keywords", "Key Points")
BACK_FIRST = "Supplementary data"
LEGENDS = "Figure legends"
TABLE_CAPTIONS = [
    "Design cultures of the 51 independent works.",
    "Stated rationales for and against input representations, by culture (works; adjudicated from verbatim quotes).",
    "Works reporting a test of whether outputs depend on the biological input, by culture.",
]
BOX_TITLE = "A neutral comparison protocol and a reporting card for input representations"  # the class prints "Box 1"

# Name as written in the manuscript -> citation keys. Cited once, at the first mention in the body.
CITATIONS = [
    ("PRISMA-ScR", ["prisma_scr"]), ("PRISMA-S", ["prisma_s"]), ("PRISMA-trAIce", ["prisma_trace"]), ("PRESS", ["press"]),
    ("Docling", ["docling"]), ("LoRA", ["lora"]), ("LLM4Cell", ["llm4cell"]),
    ("scGPT", ["scgpt"]), ("Geneformer", ["geneformer"]), ("ESM-2", ["esm2"]), ("Nicheformer", ["nicheformer"]),
    ("Llama-2-Chat", ["llama2"]), ("GPT-4o", ["gpt4o"]), ("Tahoe-100M", ["tahoe100m"]),
    ("ProteinDT", ["proteindt"]), ("BioT5+", ["biot5plus"]), ("BioT5", ["biot5"]), ("NatureLM", ["naturelm"]),
    ("Evolla", ["evolla"]), ("Galactica", ["galactica"]), ("InstructProtein", ["instructprotein"]),
    ("ProtLLM", ["protllm"]), ("Prot2Text", ["prot2text"]), ("ProtT3", ["prott3"]), ("ProLLaMA", ["prollama"]),
    ("TxGemma", ["txgemma"]),
    ("XunZi", ["xunzi"]), ("BioMedGPT", ["biomedgpt"]), ("Chroma", ["chroma"]), ("PROCYON", ["procyon"]),
    ("ChatNT", ["chatnt"]), ("InstructCell", ["instructcell"]), ("X-Cell", ["xcell"]), ("MUPAD", ["mupad"]),
    ("OKR-Cell", ["okrcell"]), ("Cell2Text", ["cell2text", "cell2text_thesis"]),
    ("CellWhisperer", ["cellwhisperer_preprint", "cellwhisperer"]), ("OmniNA", ["omnina_preprint", "omnina"]),
    ("Cell2Sentence", ["cell2sentence"]), ("CellHermes", ["cellhermes"]), ("ChatCell", ["chatcell"]),
    ("TeamPath", ["teampath"]), ("CellTosg2Sequence", ["celltosg2sequence"]), ("C2S-Scale", ["c2sscale"]),
    ("OCellus", ["ocellus"]), ("BIOVERSE", ["bioverse"]), ("OmicsLM", ["omicslm"]), ("Genolator", ["genolator"]),
    ("RVQ-Alpha", ["rvqalpha"]), ("scMMGPT", ["scmmgpt"]), ("SciCore-Omics", ["scicoreomics"]),
    ("Bio-BLIP", ["bioblip"]), ("scMIR", ["scmir"]), ("scMOBA", ["scmoba"]), ("BIOREASON", ["bioreason"]),
    ("OpticalDNA", ["opticaldna"]), ("OmniGene-4", ["omnigene4"]), ("TISSUENARRATOR", ["tissuenarrator"]),
    ("Geneverse", ["geneverse"]),
]
INCLUSION_SENTENCE = "giving 55 records from 54 studies"  # all included records are cited here
INCLUDED_KEYS_FROM = ROOT / "scripts/build_manuscript_references.py"

SUP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-"}
MATH = {"×": r"$\times$", "≈": r"$\approx$", "≤": r"$\leq$", "≥": r"$\geq$", "κ": r"$\kappa$", "α": r"$\alpha$", "§": r"\S{}"}


class Citer:
    def __init__(self, known: set[str]):
        self.done: set[str] = set()
        self.known = known
        self.patterns = [(name, keys, re.compile(r"(?<![\w\-/.])" + re.escape(name) + r"(?![\w\-+])('s|')?"))
                         for name, keys in CITATIONS]
        missing = {k for _, keys in CITATIONS for k in keys} - known
        if missing:
            raise SystemExit(f"citation keys missing from references.bib: {sorted(missing)}")

    def mark(self, text: str) -> str:
        """Insert a citation marker after the first mention of each name (outside code spans)."""
        parts = re.split(r"(`[^`]*`)", text)
        for i in range(0, len(parts), 2):
            seg = parts[i]
            hits = []
            for name, keys, pat in self.patterns:
                if name in self.done:
                    continue
                m = pat.search(seg)
                if m:
                    hits.append((m.end(), name, keys))
            taken: set[int] = set()
            for end, name, keys in sorted(hits, key=lambda h: -h[0]):
                if end in taken:  # e.g. BioT5 inside BioT5+ cannot match, but keep positions unique
                    continue
                taken.add(end)
                seg = seg[:end] + "⟦CITE:" + ",".join(keys) + "⟧" + seg[end:]
                self.done.add(name)
            parts[i] = seg
        return "".join(parts)


def code(text: str) -> str:
    if re.search(r"[/._-]", text) and " " not in text and len(text) > 24:
        return r"\nolinkurl{" + text + "}"  # paths: may break at separators
    return r"\mbox{\texttt{" + esc(text) + "}}"  # model names and short identifiers: never broken


def esc(text: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")):
        text = text.replace(a, b)
    return text


def plain(text: str) -> str:
    parts = re.split(r"(⟦CITE:[^⟧]+⟧)", text)
    return "".join(r"~\cite{" + p[6:-1] + "}" if p.startswith("⟦CITE:") else plain_text(p) for p in parts)


def plain_text(text: str) -> str:
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])", r"\\emph{\1}", text)
    text = re.sub(r'"(.+?)"', r"``\1''", text)
    text = re.sub(r"([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", lambda m: "$^{" + "".join(SUP[c] for c in m.group(1)) + "}$", text)
    for a, b in MATH.items():
        text = text.replace(a, b)
    text = re.sub(r"\b(e\.g\.|i\.e\.|vs\.) ", r"\1\\ ", text)
    return text


def inl(text: str) -> str:
    # [CITE ...] and [TODO ...] placeholders of the draft are kept visible
    out, last = [], 0
    for m in re.finditer(r"\[(CITE|TODO)[^\]]*\]", text):
        out.append(inl_core(text[last:m.start()]))
        inner = m.group(0)[1:-1]
        if m.group(1) == "TODO":
            out.append(r"\todo{" + inl_core(inner[len("TODO:"):].strip() if inner.startswith("TODO:") else inner) + "}")
        else:
            out.append(r"\citeplaceholder{" + inl_core(inner) + "}")
        last = m.end()
    out.append(inl_core(text[last:]))
    return "".join(out)


def inl_core(text: str) -> str:
    parts = re.split(r"(`[^`]*`)", text)
    return "".join(code(p[1:-1]) if p.startswith("`") and p.endswith("`") and len(p) > 1 else plain(p) for p in parts)


# ---------------------------------------------------------------- block parsing
MARKER = re.compile(r"^(\s*)(-|\d+\.)\s+(.*)$")


def blocks_of(lines: list[str]) -> list[tuple[str, object]]:
    out: list[tuple[str, object]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("### "):
            out.append(("subsection", line[4:].strip()))
            i += 1
        elif line.startswith("## "):
            out.append(("section", line[3:].strip()))
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(("table", rows))
        elif MARKER.match(line) and not line.startswith(" "):
            block = []
            while i < len(lines):
                cur = lines[i]
                if not cur.strip():
                    nxt = next((l for l in lines[i + 1:] if l.strip()), "")
                    if nxt.startswith(" ") or (MARKER.match(nxt) and not nxt.startswith(" ") and not nxt.startswith("#")):
                        block.append(cur)
                        i += 1
                        continue
                    break
                if not (cur.startswith(" ") or MARKER.match(cur)):
                    break
                block.append(cur)
                i += 1
            out.append(("list", block))
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|")) and not (MARKER.match(lines[i]) and not lines[i].startswith(" ")):
                para.append(lines[i].strip())
                i += 1
            out.append(("para", " ".join(para)))
    return out


def parse_list(lines: list[str]) -> list[dict]:
    root: list[dict] = []
    stack: list[dict] = []
    pending_break = False
    for line in lines:
        if not line.strip():
            pending_break = True
            continue
        m = MARKER.match(line)
        # As in CommonMark, an ordered marker other than 1 cannot interrupt the text of an item
        # ("... 691 to\n  27. The flow counts ..." is a continuation line, not a new list).
        if m and m.group(2) not in ("-", "1.") and not pending_break and stack \
                and len(m.group(1)) > stack[-1]["indent"] and stack[-1]["blocks"][-1][0] == "text":
            m = None
        if m:
            indent, mark, text = len(m.group(1)), m.group(2), m.group(3)
            item = {"indent": indent, "content_indent": indent + len(mark) + 1,
                    "kind": "ul" if mark == "-" else "ol", "blocks": [["text", [text]]]}
            while stack and stack[-1]["indent"] >= indent:
                stack.pop()
            if stack:
                parent = stack[-1]
                if parent["blocks"][-1][0] != "list":
                    parent["blocks"].append(["list", []])
                parent["blocks"][-1][1].append(item)
            else:
                root.append(item)
            stack.append(item)
        else:
            indent = len(line) - len(line.lstrip())
            while stack and stack[-1]["indent"] >= indent:
                stack.pop()
            if not stack:
                raise SystemExit(f"continuation line outside a list: {line!r}")
            item = stack[-1]
            if item["blocks"][-1][0] == "text" and not pending_break:
                item["blocks"][-1][1].append(line.strip())
            else:
                item["blocks"].append(["text", [line.strip()]])
        pending_break = False
    return root


def render_items(items: list[dict], citer: Citer) -> str:
    out = []
    for kind, group in group_by_kind(items):
        env = "itemize" if kind == "ul" else "enumerate"
        body = []
        for item in group:
            chunks = []
            for btype, content in item["blocks"]:
                if btype == "text":
                    chunks.append(inl(citer.mark(" ".join(content))))
                else:
                    chunks.append(render_items(content, citer))
            body.append(r"\item " + "\n".join(c if c.startswith("\\begin") else c for c in join_chunks(chunks)))
        out.append(f"\\begin{{{env}}}\n" + "\n".join(body) + f"\n\\end{{{env}}}")
    return "\n".join(out)


def join_chunks(chunks: list[str]) -> list[str]:
    out = []
    for c in chunks:
        if out and not c.startswith("\\begin") and not out[-1].startswith("\\begin"):
            out.append(r"\par " + c)
        else:
            out.append(c)
    return out


def group_by_kind(items: list[dict]):
    group: list[dict] = []
    for item in items:
        if group and item["kind"] != group[-1]["kind"]:
            yield group[-1]["kind"], group
            group = []
        group.append(item)
    if group:
        yield group[-1]["kind"], group


def table_rows(rows: list[str]) -> list[list[str]]:
    out = []
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        out.append(cells)
    return out


def render_table(rows: list[list[str]], citer: Citer, caption: str, label: str, wide: bool) -> str:
    ncol = len(rows[0])
    if wide:
        spec = {3: r"@{}>{\raggedright\arraybackslash}p{0.2\textwidth}>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X@{}"}.get(ncol, "@{}" + "X" * ncol + "@{}")
        if label == "tab:cultures":
            spec = r"@{}>{\raggedright\arraybackslash}p{0.18\textwidth}>{\raggedright\arraybackslash}X r@{}"
        width, env = r"\textwidth", "table*"
    else:
        spec = r"@{}>{\raggedright\arraybackslash}X r@{}"
        width, env = r"\columnwidth", "table"
    head = " & ".join(r"\textbf{" + inl(c) + "}" for c in rows[0]) + r" \\"
    body = "\n".join(" & ".join(inl(citer.mark(c)) for c in r) + r" \\" for r in rows[1:])
    return (f"\\begin{{{env}}}[!t]\n\\caption{{{caption}}}\\label{{{label}}}\n"
            f"\\begin{{tabularx}}{{{width}}}{{{spec}}}\n\\toprule\n{head}\n\\midrule\n{body}\n\\botrule\n"
            f"\\end{{tabularx}}\n\\end{{{env}}}")


def figure_legends(lines: list[str]) -> tuple[dict[int, str], list[str]]:
    """Figure legends (bold-titled items) and the supplementary items of the Figures and tables list."""
    items = parse_list(lines)
    legends: dict[int, str] = {}
    supplementary: list[str] = []
    for item in items:
        text = " ".join(" ".join(c) for t, c in item["blocks"] if t == "text")
        m = re.match(r"\*\*Figure (\d)\. (.+?)\.?\*\*\s*(.*)$", text)
        if m:
            legends[int(m.group(1))] = r"\textbf{" + inl_core(m.group(2)) + ".} " + inl_core(m.group(3))
        elif re.match(r"(Supplementary Figure|Table S|Text S)", text):
            supplementary.append(text)
    return legends, supplementary


def render_figure(n: int, caption: str) -> str:
    files = [Path(p).name for p in FIGURES[n]]
    if len(files) == 1:
        body = f"\\includegraphics[width=\\textwidth]{{{files[0]}}}"
    else:
        body = (f"\\begin{{minipage}}[c]{{0.34\\textwidth}}\\includegraphics[width=\\linewidth]{{{files[0]}}}\\end{{minipage}}\\hfill\n"
                f"\\begin{{minipage}}[c]{{0.63\\textwidth}}\\includegraphics[width=\\linewidth]{{{files[1]}}}\\end{{minipage}}")
    return f"\\begin{{figure*}}[!t]\n\\centering\n{body}\n\\caption{{{caption}}}\\label{{fig:{n}}}\n\\end{{figure*}}"


def section_text(lines: list[str], heads: dict[str, int], name: str) -> list[str]:
    i = heads[name] + 1
    out = []
    while i < len(lines) and not lines[i].startswith("## "):
        out.append(lines[i])
        i += 1
    return out


def write_front_matter(lines: list[str], heads: dict[str, int]) -> None:
    gen = "% Generated by scripts/build_manuscript_latex.py from the Markdown master; do not edit."
    abstract = " ".join(l.strip() for l in section_text(lines, heads, "Abstract") if l.strip())
    keywords = " ".join(l.strip() for l in section_text(lines, heads, "Keywords") if l.strip())
    kw = ", ".join(k.strip() for k in keywords.split(";") if k.strip())
    (OUT / "frontmatter.tex").write_text(f"{gen}\n\\abstract{{{inl(abstract)}}}\n\n\\keywords{{{esc(kw)}}}\n", encoding="utf-8")
    items = parse_list([l for l in section_text(lines, heads, "Key Points")])
    dummy = Citer.__new__(Citer)
    dummy.done, dummy.patterns = set(), []
    (OUT / "keypoints.tex").write_text(f"{gen}\n\\section*{{Key Points}}\n" + render_items(items, dummy) + "\n", encoding="utf-8")


def write_back_matter(lines: list[str], citer: "Citer") -> None:
    out = ["% Generated by scripts/build_manuscript_latex.py from the Markdown master; do not edit."]
    bios: list[str] = []
    name = ""
    for btype, content in blocks_of(lines):
        if btype == "section":
            name = content
            if name != "Biographical notes":
                out.append(f"\n\\section*{{{inl_core(name)}}}")
        elif name == "Biographical notes" and btype == "list":
            for item in parse_list(content):
                text = " ".join(" ".join(c) for t, c in item["blocks"] if t == "text")
                person, _, rest = text.partition(" [")
                rest = "[" + rest if rest else ""
                bios.append(f"\\begin{{biography}}{{}}{{\\author{{{inl(person)}}} {inl(rest)}}}\n\\end{{biography}}")
        elif btype == "para":
            out.append(inl(content))
        elif btype == "list":
            out.append(render_items(parse_list(content), citer))
    (OUT / "backmatter.tex").write_text("\n\n".join(out) + "\n", encoding="utf-8")
    (OUT / "biographies.tex").write_text("\n\n".join(bios) + "\n", encoding="utf-8")


def main() -> int:
    md = MD.read_text(encoding="utf-8")
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)  # markers of generated values (see build_manuscript.py)
    lines = md.split("\n")
    heads = {l[3:].strip(): i for i, l in enumerate(lines) if l.startswith("## ")}
    start, back_at, figs_at = heads["Introduction"], heads[BACK_FIRST], heads[LEGENDS]
    body_lines, back_lines, fig_lines = lines[start:back_at], lines[back_at:figs_at], lines[figs_at + 1:]
    write_front_matter(lines, heads)
    known = set(re.findall(r"^@\w+\{([^,\s]+),", BIB.read_text(encoding="utf-8"), re.M))
    included = re.findall(r'"[a-z_0-9-]+__[a-z_0-9]+": "([a-z0-9_]+)"', INCLUDED_KEYS_FROM.read_text())
    if len(set(included)) != 55:
        raise SystemExit(f"expected 55 included keys, found {len(set(included))}")
    citer = Citer(known)
    legends, supplementary = figure_legends(fig_lines)
    legends[2] = legends[2] + FIG2_DRAFT_NOTE

    out: list[str] = ["% Generated by scripts/build_manuscript_latex.py from manuscript/review_manuscript_draft.md; do not edit.", ""]
    inclusion_cited = False
    pending_figs: list[int] = []
    placed: set[int] = set()
    tables = 0
    section = subsection = ""
    box_parts: list[str] = []
    for btype, content in blocks_of(body_lines):
        if btype == "section":
            section = re.sub(r"^\d+\.\s*", "", content)
            out.append(f"\n\\section{{{inl_core(section)}}}")
        elif btype == "subsection":
            subsection = re.sub(r"^\d+\.\d+\s*", "", content)
            out.append(f"\n\\subsection{{{inl_core(subsection)}}}")
        elif btype == "para":
            text = content.replace(" (arXiv:2510.07793)", "")
            if INCLUSION_SENTENCE in text:
                text = text.replace(INCLUSION_SENTENCE, INCLUSION_SENTENCE + "⟦CITE:" + ",".join(dict.fromkeys(included)) + "⟧", 1)
                inclusion_cited = True
            if subsection.startswith("A neutral comparison protocol") and text.endswith("except the representation:"):
                text = text[:-1] + " (Box 1)."
            if subsection.startswith("A reporting card") and text.startswith("Reporting completeness"):
                text = text.rstrip(".") + " (Box 1)."
            if subsection.startswith("A reporting card") and text.startswith("The operation library"):
                box_parts.append(inl(citer.mark(text)))
                continue
            out.append(inl(citer.mark(text)))
        elif btype == "list":
            rendered = render_items(parse_list(content), citer)
            if subsection.startswith("A neutral comparison protocol"):
                box_parts.append(r"\textbf{Neutral comparison protocol} (everything fixed except the representation)" + "\n" + rendered)
                continue
            out.append(rendered)
        elif btype == "table":
            rows = table_rows(content)
            if subsection.startswith("A reporting card"):
                head = " & ".join(r"\textbf{" + inl(c) + "}" for c in rows[0]) + r" \\"
                body = "\n".join(" & ".join(inl(citer.mark(c)) for c in r) + r" \\" for r in rows[1:])
                box_parts.append(r"\textbf{Reporting card.} Items to report for each input representation:" + "\n\n"
                                 r"\noindent\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{0.3\linewidth}>{\raggedright\arraybackslash}X@{}}" "\n"
                                 r"\toprule" "\n" + head + "\n" r"\midrule" "\n" + body + "\n" r"\botrule" "\n" r"\end{tabularx}")
                continue
            label = ["tab:cultures", "tab:rationales", "tab:dependence"][tables]
            out.append(render_table(rows, citer, TABLE_CAPTIONS[tables], label, wide=tables < 2))
            tables += 1
        # figures: place each after the block where it is first called out
        text_for_figs = content if isinstance(content, str) else " ".join(content if isinstance(content, list) else [])
        called = {int(x) for x in re.findall(r"Figures? (\d)", text_for_figs)}
        called |= {int(x) for x in re.findall(r"Figures \d[a-z\u2013-]* and (\d)", text_for_figs)}
        for n in sorted(called - placed):
            pending_figs.append(n)
            placed.add(n)
        if btype not in ("section", "subsection"):
            while pending_figs:
                n = pending_figs.pop(0)
                out.append(render_figure(n, legends[n]))
    # Box 1 at the end of section 4.4 (inserted before "Relation to existing reviews")
    box = f"\\begin{{boxtext}}[{BOX_TITLE}]\n" + "\n\n".join(box_parts) + "\n\\end{boxtext}"
    idx = next(i for i, l in enumerate(out) if l.startswith("\n\\subsection{Relation to existing reviews"))
    out.insert(idx, box)
    if pending_figs or set(FIGURES) - placed:
        raise SystemExit(f"figures not placed: {sorted(set(FIGURES) - placed)}")
    if not inclusion_cited:
        raise SystemExit(f"inclusion sentence not found in the body: {INCLUSION_SENTENCE!r}")
    not_cited = [n for n, _ in CITATIONS if n not in citer.done]
    if not_cited:
        raise SystemExit(f"names never found in the body: {not_cited}")
    (OUT / "body.tex").write_text("\n\n".join(out) + "\n", encoding="utf-8")

    write_back_matter(back_lines, citer)

    figdir = OUT / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    for paths in FIGURES.values():
        for p in paths:
            shutil.copy2(ROOT / p, figdir / Path(p).name)
    print({"tables": tables, "figures": sorted(placed), "cited_names": len(citer.done),
           "included_records_cited": len(set(included))})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
