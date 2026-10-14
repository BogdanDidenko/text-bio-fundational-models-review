#!/usr/bin/env python3
"""Figures 1, 3, 4 and 5 of the paper-1 manuscript (design cultures), from committed tables only.

Inputs (run scripts/build_design_culture_synthesis.py first):
- analysis/design_culture_charting_2026-10-14/v11/{comparison_units_with_opponent_class.csv,
  work_level_table.csv, design_culture_numbers.json, steward_adjudication.json}
- analysis/design_culture_charting_2026-10-14/roles.json
- analysis/discovery_2026-10-14/{gene_budget_table.csv, token_budget_table.csv, slots.parquet}
- analysis/motif_library_2026-10-14/{motifs.json, model_motif_composition.json}
- docs/input-representation-atlas/component-library/data/catalog.json (release 1.3.0)

Output: analysis/design_culture_charting_2026-10-14/v11/figures/figure{1,3,4,5}.{png,pdf} and one source-data
CSV per panel in the same folder.

  python3 scripts/build_design_culture_figures.py
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "analysis/design_culture_charting_2026-10-14/v11"
DI = ROOT / "analysis/discovery_2026-10-14"
ML = ROOT / "analysis/motif_library_2026-10-14"
CAT = ROOT / "docs/input-representation-atlas/component-library/data/catalog.json"
OUT = CH / "figures"
LINKED = {"full_2026-07-06__rec_000827": "W_cellwhisperer", "full_2026-07-06__rec_002105": "W_cellwhisperer",
          "full_2026-07-06__rec_002327": "W_omnina", "full_2026-07-06__rec_003394": "W_omnina",
          "june_update_2026-06-10__rec_000248": "W_cell2text", "full_2026-07-06__rec_001838": "W_cell2text"}

MM = 1 / 25.4
SIZES = (7, 6, 5.5)  # titles and axis labels; annotations and legends; ticks
COL = {"T": "#D55E00", "E": "#0072B2", "H": "#CC79A7", "C": "#009E73", "A": "#9A9A9A", "P": "#4D4D4D"}
TINT = {"T": "#F2C2A6", "E": "#A9CBE6"}
NAME = {"T": "Token-native", "E": "Encoder-mediated", "H": "Hybrid", "C": "Language-conditioned",
        "A": "Alignment-only", "P": "Image rendering"}
GREY = "#6E6E6E"


def work(record):
    return LINKED.get(record, record)


def style():
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": SIZES[0], "axes.titlesize": SIZES[0], "axes.labelsize": SIZES[0],
        "xtick.labelsize": SIZES[2], "ytick.labelsize": SIZES[2], "legend.fontsize": SIZES[1],
        "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "xtick.direction": "out", "ytick.direction": "out", "legend.frameon": False,
        "axes.titlelocation": "left", "axes.titleweight": "regular", "axes.titlepad": 4,
        "savefig.dpi": 300, "pdf.fonttype": 42, "ps.fonttype": 42, "hatch.linewidth": 0.5,
    })


def letter(fig, x_frac, ax, s):
    fig.text(x_frac, ax.get_position().y1 + 1.2 * MM / fig.get_size_inches()[1], s, fontsize=9,
             fontweight="bold", ha="left", va="bottom")


def overlaps(fig):
    """figure-style §9.1: visible text boxes that overlap each other or leave the figure."""
    r = fig.canvas.get_renderer()
    hidden = set()
    for ax in fig.axes:
        if not ax.axison:
            hidden.update(ax.get_xticklabels(which="both") + ax.get_yticklabels(which="both"))
            hidden.update([ax.xaxis.label, ax.yaxis.label])
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text)
             if t.get_text().strip() and t.get_visible() and t not in hidden]
    bad = [(a.get_text()[:28], b.get_text()[:28]) for i, (a, ba) in enumerate(texts) for b, bb in texts[i + 1:]
           if ba.overlaps(bb)]
    fb = fig.bbox
    outside = [t.get_text()[:28] for t, bt in texts
               if bt.x0 < fb.x0 - 1 or bt.x1 > fb.x1 + 1 or bt.y0 < fb.y0 - 1 or bt.y1 > fb.y1 + 1]
    return bad, outside


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    bad, outside = overlaps(fig)
    fig.savefig(OUT / f"{name}.png", dpi=300)
    fig.savefig(OUT / f"{name}.pdf")
    print(f"{name}: overlaps={bad} outside={outside}")
    plt.close(fig)


def load():
    d = {"units": pd.read_csv(CH / "comparison_units_with_opponent_class.csv"),
         "works": pd.read_csv(CH / "work_level_table.csv"),
         "numbers": json.loads((CH / "design_culture_numbers.json").read_text()),
         "gb": pd.read_csv(DI / "gene_budget_table.csv"),
         "tb": pd.read_csv(DI / "token_budget_table.csv"),
         "slots": pd.read_parquet(DI / "slots.parquet"),
         "roles": json.loads((ROOT / "analysis/design_culture_charting_2026-10-14/roles.json").read_text()),
         "motifs": json.loads((ML / "motifs.json").read_text())["motifs"],
         "mmc": json.loads((ML / "model_motif_composition.json").read_text()),
         "catalog": json.loads(CAT.read_text()),
         "culture": json.loads((CH / "steward_adjudication.json").read_text())["culture"]}
    return d


def colour_ticklabels(labels, keys):
    for t, k in zip(labels, keys):
        t.set_color(COL[k])


# ----------------------------------------------------------------------------------------- Figure 1
def box(ax, x, y, w, h, text, fc="white", ec="black", hatch=None, fs=SIZES[1], lw=0.7, r=0.8, text_bg=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}", fc=fc, ec=ec, lw=lw,
                                hatch=hatch))
    if text:
        kw = dict(bbox=dict(fc="white", ec="none", pad=0.6)) if text_bg else {}
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.1, **kw)


def arrow(ax, x0, y0, x1, y1, color="black", lw=0.8):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=6, lw=lw, color=color,
                                 shrinkA=0, shrinkB=0))


def fig1_schematic(ax, nums):
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 52)
    ax.axis("off")
    g, s = nums["gene_budget"], nums["soft_token_budget"]
    opq = nums["median_opaque_share_by_culture"]
    # the measurement
    genes = ["CD3E", "IL7R", "LTB", "CD2", "MALAT1", "GZMK", "CCR7", "NKG7"]
    vals = np.array([5.1, 4.4, 4.2, 3.6, 3.1, 2.2, 1.7, 0.9])
    x0, y0, bw, step = 7, 22, 2.4, 3.1
    for i, (gname, v) in enumerate(zip(genes, vals)):
        ax.add_patch(Rectangle((x0 + i * step, y0), bw, v * 2.9, fc="#BDBDBD", ec="none"))
        ax.text(x0 + i * step + bw / 2, y0 - 0.7, gname, rotation=90, ha="center", va="top", fontsize=SIZES[2],
                style="italic")
    ax.plot([x0 - 0.6, x0 + len(genes) * step], [y0, y0], color="black", lw=0.6)
    ax.text(x0 + len(genes) * step / 2, 13.2, "one cell, about 20,000\ngenes measured", ha="center", va="top",
            fontsize=SIZES[1], linespacing=1.1)
    # language model
    box(ax, 153, 6, 23, 40, "language\nmodel", fc="#F4F4F4", fs=SIZES[0], r=1.2)
    # translate lane
    yt = 40
    ax.text(43, 51.5, f"Translate: token-native ({nums['culture_n']['T']} works)", color=COL["T"], fontsize=SIZES[0],
            fontweight="bold", ha="left", va="top")
    arrow(ax, 33.5, 36.5, 42.5, yt, color=COL["T"])
    box(ax, 43, yt - 3.6, 27, 7.2, "rank, keep top K,\nwrite gene names", ec=COL["T"])
    arrow(ax, 70.5, yt, 74.5, yt, color=COL["T"])
    tx = 75
    for t in ["CD3E", "IL7R", "LTB", "CD2", "…"]:
        w = 2.4 + 1.5 * len(t)
        box(ax, tx, yt - 2.4, w, 4.8, t, fc=TINT["T"], ec=COL["T"], fs=SIZES[2], r=0.5)
        tx += w + 0.9
    arrow(ax, tx + 0.6, yt, 152.5, yt, color=COL["T"])
    ax.text(75, yt - 4.4,
            f"K = {g['text_K_median']:.0f} genes per cell (median; {g['text_K_min']:.0f}–{g['text_K_max']:.0f}; "
            f"{g['text_works_with_K']} works)\nvalues written as numbers in 2 of 51 works\n"
            f"median share of opaque learned steps per work: {opq['T']:.0f}",
            fontsize=SIZES[1], va="top", ha="left", linespacing=1.25)
    # encode lane
    yb = 12
    ax.text(43, 0.5, f"Encode: encoder-mediated ({nums['culture_n']['E']} works)", color=COL["E"],
            fontsize=SIZES[0], fontweight="bold", ha="left", va="bottom")
    arrow(ax, 33.5, 23.5, 42.5, yb, color=COL["E"])
    box(ax, 43, yb - 4, 22, 8, "biological\nencoder", ec=COL["E"], hatch="///", text_bg=True)
    arrow(ax, 65.5, yb, 69.5, yb, color=COL["E"])
    box(ax, 70, yb - 3, 14, 6, "projector", ec=COL["E"], hatch="///", text_bg=True)
    arrow(ax, 84.5, yb, 88, yb, color=COL["E"])
    for i in range(8):
        ax.add_patch(Rectangle((88.5 + i * 3.0, yb - 1.5), 2.4, 3, fc=TINT["E"], ec=COL["E"], lw=0.6))
    arrow(ax, 113, yb, 152.5, yb, color=COL["E"])
    ax.text(88.5, yb + 3.4,
            f"{s['min']}–{s['max']} vectors per object (median {s['median']:.0f}; {s['works']} works)\n"
            f"from {g['embedding_min']:,.0f}–{g['embedding_max']:,.0f} input features ({g['embedding_works']} works)\n"
            f"median share of opaque learned steps per work: {opq['E']:.2f}",
            fontsize=SIZES[1], va="bottom", ha="left", linespacing=1.25)
    ax.text(54, yb - 5.0, "hatched: learned module", fontsize=SIZES[2], color=GREY, ha="center", va="top")


def waffle_units(ax, units):
    rows = ["T", "E", "H", "P"]
    gx = {"released": 0.0, "trained_by_proposer": 9.4, "no_model": 15.6}
    heads = {"released": "released,\nunadapted opponent", "trained_by_proposer": "opponent built\nby the proposers",
             "no_model": "no\nmodel"}
    sq = 0.82
    for r, cult in enumerate(rows):
        y = -r * 1.3
        sub = units[units.proposed == cult]
        for gkey in gx:
            gg = sub[sub.opponent_class == gkey].sort_values(["proposed_wins", "unit"], ascending=[False, True])
            for i, (_, u) in enumerate(gg.iterrows()):
                x = gx[gkey] + i * 1.0
                if u.winner == "mixed":
                    ax.add_patch(Rectangle((x, y), sq, sq, fc="white", ec=GREY, hatch="//////", lw=0.6))
                else:
                    ax.add_patch(Rectangle((x, y), sq, sq, fc=COL[u.winner], ec="none"))
        ax.text(-0.6, y + sq / 2, f"{NAME[cult]} proposed ({len(sub)})", ha="right", va="center",
                fontsize=SIZES[1], color=COL[cult])
    for gkey, lab in heads.items():
        ax.text(gx[gkey], 1.15, lab, ha="left", va="bottom", fontsize=SIZES[2], color=GREY, linespacing=1.1)
    ly = -5.6
    ax.text(-0.6, ly + 0.3, "winner:", ha="right", va="center", fontsize=SIZES[2])
    items = [("T", "token-native"), ("E", "encoder-mediated"), ("H", "hybrid"), ("P", "image rendering"),
             (None, "mixed result")]
    pos = [(0, ly), (5.4, ly), (12.6, ly), (0, ly - 1.0), (7.0, ly - 1.0)]
    for (c, lab), (xx, yy) in zip(items, pos):
        if c:
            ax.add_patch(Rectangle((xx, yy), 0.6, 0.6, fc=COL[c], ec="none"))
        else:
            ax.add_patch(Rectangle((xx, yy), 0.6, 0.6, fc="white", ec=GREY, hatch="//////", lw=0.6))
        ax.text(xx + 0.85, yy + 0.3, lab, va="center", fontsize=SIZES[2])
    ax.set_xlim(-12.5, 18.0)
    ax.set_ylim(-6.9, 2.7)
    ax.set_aspect("equal")
    ax.set_anchor("NW")
    ax.axis("off")


def waffle_works(ax, works):
    rows = ["T", "E", "H", "C", "A"]
    sq = 0.82
    for r, cult in enumerate(rows):
        y = -r * 1.3
        sub = works[works.culture == cult].sort_values("dependence_test", ascending=False)
        for i, (_, w) in enumerate(sub.iterrows()):
            if w.dependence_test:
                ax.add_patch(Rectangle((i, y), sq, sq, fc=COL[cult], ec="none"))
            else:
                ax.add_patch(Rectangle((i + 0.06, y + 0.06), sq - 0.12, sq - 0.12, fc="white", ec=COL[cult], lw=0.6))
        ax.text(-0.6, y + sq / 2, NAME[cult], ha="right", va="center", fontsize=SIZES[1], color=COL[cult])
        ax.text(len(sub) + 0.3, y + sq / 2, f"{int(sub.dependence_test.sum())} of {len(sub)}", ha="left",
                va="center", fontsize=SIZES[1])
    ly = -7.2
    ax.add_patch(Rectangle((0, ly), 0.6, 0.6, fc="#4D4D4D", ec="none"))
    ax.text(0.85, ly + 0.3, "dependence tested", va="center", fontsize=SIZES[2])
    ax.add_patch(Rectangle((8.6, ly), 0.6, 0.6, fc="white", ec="#4D4D4D", lw=0.6))
    ax.text(9.45, ly + 0.3, "no test reported", va="center", fontsize=SIZES[2])
    ax.set_xlim(-10.0, 21.0)
    ax.set_ylim(-7.5, 1.2)
    ax.set_aspect("equal")
    ax.set_anchor("NW")
    ax.axis("off")


def figure1(d):
    fig = plt.figure(figsize=(180 * MM, 104 * MM))
    ax_a = fig.add_axes([0.035, 0.445, 0.955, 0.505])
    ax_b = fig.add_axes([0.035, 0.015, 0.50, 0.335])
    ax_c = fig.add_axes([0.575, 0.015, 0.415, 0.335])
    nums, c = d["numbers"], d["numbers"]["comparisons"]
    fig1_schematic(ax_a, nums)
    ax_a.set_title("The same measurement reaches a language model in two ways", loc="left")
    waffle_units(ax_b, d["units"])
    ax_b.set_title(f"The proposed representation won {c['proposed_wins_all']} of {c['units']} cross-culture "
                   f"comparisons", loc="left")
    waffle_works(ax_c, d["works"])
    ax_c.set_title(f"{nums['dependence_tests']['works']} of 51 works test whether outputs depend on the biology",
                   loc="left")
    fig.canvas.draw()
    for ax, L, x in [(ax_a, "a", 0.006), (ax_b, "b", 0.006), (ax_c, "c", 0.553)]:
        letter(fig, x, ax, L)
    d["units"].to_csv(OUT / "figure1b_units.csv", index=False)
    d["works"][["work", "culture", "dependence_test"]].to_csv(OUT / "figure1c_works.csv", index=False)
    save(fig, "figure1")


# ----------------------------------------------------------------------------------------- Figure 3
FAM = {"M01": "verbalisation", "M02": "verbalisation", "M04": "verbalisation", "M12": "verbalisation",
       "M05": "biological alphabet", "M07": "encoder", "M08": "encoder", "M09": "encoder", "M10": "encoder",
       "M11": "encoder", "M13": "encoder", "M14": "encoder", "M03": "shared", "M06": "shared", "M15": "shared"}
FAM_COL = {"verbalisation": COL["T"], "biological alphabet": TINT["T"], "encoder": COL["E"], "shared": "#BDBDBD"}


def figure3(d):
    fig = plt.figure(figsize=(180 * MM, 140 * MM))
    ax_a = fig.add_axes([0.155, 0.555, 0.30, 0.40])
    ax_b = fig.add_axes([0.715, 0.555, 0.265, 0.40])
    ax_c = fig.add_axes([0.215, 0.065, 0.27, 0.40])
    ax_d = fig.add_axes([0.715, 0.12, 0.265, 0.25])
    # a: operation reuse
    ops = pd.DataFrame([{"operation": b["label"], "papers": len(set(b.get("reuse_record_ids") or []))}
                        for b in d["catalog"]["blocks"]]).sort_values("papers")
    ax_a.barh(ops.operation, ops.papers, color="#9E9E9E", height=0.68)
    for y, v in enumerate(ops.papers):
        ax_a.text(v + 0.6, y, str(v), va="center", fontsize=SIZES[2])
    ax_a.set_xlabel("papers using the operation (of 54)")
    ax_a.set_xlim(0, 43)
    ax_a.set_ylim(-0.7, len(ops) - 0.3)
    ax_a.tick_params(axis="y", length=0)
    ax_a.set_title(f"{int((ops.papers >= 2).sum())} of {len(ops)} operations recur in two or more papers", loc="left")
    ops.to_csv(OUT / "figure3a_operation_reuse.csv", index=False)
    # b: unstated parameters
    s = d["slots"].copy()
    s["unstated"] = s.status == "unspecified"
    pp = s.groupby(["operation_id", "parameter"]).agg(n=("unstated", "size"), share=("unstated", "mean")).reset_index()
    pp = pp[pp.n >= 45].sort_values("share")
    ax_b.hlines(range(len(pp)), 0, pp.share, color="#BDBDBD", lw=0.8)
    ax_b.plot(pp.share, range(len(pp)), "o", color="#4D4D4D", ms=3.2)
    ax_b.set_yticks(range(len(pp)))
    ax_b.set_yticklabels([f"{o.replace('_', ' ')}: {p.replace('_', ' ')} ({n})"
                          for o, p, n in zip(pp.operation_id, pp.parameter, pp.n)])
    ax_b.tick_params(axis="y", length=0)
    ax_b.set_xlim(-0.03, 1.05)
    ax_b.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_b.set_xticklabels(["0", "25%", "50%", "75%", "100%"])
    ax_b.set_xlabel("calls with the parameter unstated")
    ax_b.set_ylim(-0.7, len(pp) - 0.3)
    ax_b.set_title("Key parameters often go unstated", loc="left")
    pp.to_csv(OUT / "figure3b_unstated_parameters.csv", index=False)
    # c: motif library
    mt = pd.DataFrame([{"motif": m["name"], "papers": m["papers"], "family": FAM[m["motif_id"]],
                        "motif_id": m["motif_id"]} for m in d["motifs"]]).sort_values("papers")
    ax_c.barh(mt.motif, mt.papers, color=[FAM_COL[f] for f in mt.family], height=0.68)
    for y, v in enumerate(mt.papers):
        ax_c.text(v + 0.3, y, str(v), va="center", fontsize=SIZES[2])
    ax_c.set_xlabel("papers with the motif (of 54)")
    ax_c.set_xticks([0, 5, 10, 15, 20])
    ax_c.set_xlim(0, 21)
    ax_c.set_ylim(-0.7, len(mt) - 0.3)
    ax_c.tick_params(axis="y", length=0)
    ax_c.set_title("Recurring sub-chains form verbalisation and encoder families", loc="left")
    for k, f in enumerate(["verbalisation", "biological alphabet", "encoder", "shared"]):
        yy = 3.6 - k * 1.05
        ax_c.add_patch(Rectangle((12.0, yy - 0.3), 0.8, 0.6, fc=FAM_COL[f], ec="none"))
        ax_c.text(13.1, yy, f, va="center", fontsize=SIZES[2])
    mt.to_csv(OUT / "figure3c_motifs.csv", index=False)
    # d: motif families by culture
    role_of = {(r, m["model_name"]): m["role"] for r, ms in d["roles"].items() for m in ms}
    wf = defaultdict(set)
    for k, mots in d["mmc"]["model_motifs"].items():
        r, mname = k.split("|", 1)
        if role_of.get((r, mname)) in ("proposed", "component"):
            wf[work(r)].update(FAM[m] for m in mots)
    rows, cols, cult = ["T", "E", "H", "C"], ["verbalisation", "biological alphabet", "encoder"], d["culture"]
    n = np.array([sum(1 for k in cult.values() if k == c) for c in rows])
    M = np.array([[sum(1 for w, k in cult.items() if k == c and f in wf.get(w, set())) for f in cols] for c in rows])
    S = M / n[:, None]
    ax_d.imshow(S, cmap="Greys", vmin=0, vmax=1.25, aspect="auto")
    for i in range(len(rows)):
        for j in range(len(cols)):
            ax_d.text(j, i, f"{M[i, j]}/{n[i]}", ha="center", va="center", fontsize=SIZES[1],
                      color="white" if S[i, j] > 0.62 else "black")
    ax_d.set_xticks(range(len(cols)))
    ax_d.set_xticklabels(["verbalisation", "biological\nalphabet", "encoder"])
    ax_d.set_yticks(range(len(rows)))
    ax_d.set_yticklabels([NAME[c] for c in rows])
    colour_ticklabels(ax_d.get_yticklabels(), rows)
    ax_d.tick_params(length=0)
    for sp in ax_d.spines.values():
        sp.set_visible(False)
    ax_d.set_title("Motif families track the cultures", loc="left")
    pd.DataFrame(M, index=rows, columns=cols).assign(n=n).to_csv(OUT / "figure3d_motif_families_by_culture.csv")
    fig.canvas.draw()
    for ax, L, x in [(ax_a, "a", 0.006), (ax_b, "b", 0.515), (ax_c, "c", 0.006), (ax_d, "d", 0.515)]:
        letter(fig, x, ax, L)
    save(fig, "figure3")


# ----------------------------------------------------------------------------------------- Figure 4
def short(s):
    s = str(s)
    for cut in [" (", ":"]:
        if cut in s:
            s = s.split(cut)[0]
    return s.strip()


def place_labels(values, heights):
    """Spread label centres (log10 units) so that neighbouring labels of the given heights do not overlap."""
    out = np.log10(np.asarray(values, dtype=float)).copy()
    h = np.asarray(heights, dtype=float)
    for _ in range(500):
        moved = False
        for i in range(1, len(out)):
            need = (h[i] + h[i - 1]) / 2
            if out[i] - out[i - 1] < need - 1e-9:
                push = (need - (out[i] - out[i - 1])) / 2
                out[i] += push
                out[i - 1] -= push
                moved = True
        if not moved:
            break
    return out


def figure4(d):
    cult = d["culture"]
    gb, tb = d["gb"].copy(), d["tb"].copy()
    gb["work"], tb["work"] = gb.record_id.map(work), tb.record_id.map(work)
    k = gb[gb.route_kind == "text: proposed model input"].dropna(subset=["genes_kept"])
    k = k.loc[k.groupby("record_id").genes_kept.idxmax()]
    feats = gb[gb.route_kind == "embedding: proposed model input"]
    feats = feats.loc[feats.groupby("record_id").genes_kept.idxmax()]
    vec = tb[~tb.unit.str.contains("text tokens")]
    pts = pd.concat([
        pd.DataFrame({"category": 0, "work": k.work, "label": k.context.map(short), "value": k.genes_kept}),
        pd.DataFrame({"category": 1, "work": vec.work, "label": vec.model.map(short), "value": vec.tokens}),
        pd.DataFrame({"category": 2, "work": feats.work, "label": feats.context.map(short), "value": feats.genes_kept}),
    ]).reset_index(drop=True)
    pts["culture"] = pts.work.map(cult)
    pts.loc[pts.label.str.startswith("RVQ-Alpha"), "label"] = "RVQ-Alpha (codes)"
    pts.to_csv(OUT / "figure4a_budgets.csv", index=False)
    w = d["works"]
    fig = plt.figure(figsize=(180 * MM, 104 * MM))
    ax_a = fig.add_axes([0.068, 0.115, 0.47, 0.80])
    ax_b = fig.add_axes([0.665, 0.625, 0.325, 0.29])
    ax_c = fig.add_axes([0.665, 0.115, 0.325, 0.29])
    line = 0.155  # one 5.5-pt text line in decades of the y axis at this panel height
    XPOS = [0, 1.3, 2.55]
    for cat in [0, 1, 2]:
        sub = pts[pts.category == cat]
        groups = sub.groupby("value")
        vals = sorted(groups.groups)
        texts = []
        for v in vals:
            names = list(groups.get_group(v).sort_values("label").label)
            if cat == 2:
                texts.append(",\n".join(names))
            else:
                texts.append(", ".join(names) if len(names) <= 2 else ", ".join(names[:2]) + ",\n" + ", ".join(names[2:]))
        ys = place_labels(vals, [line * (t.count("\n") + 1) for t in texts])
        for v, ly, text in zip(vals, ys, texts):
            g = groups.get_group(v).sort_values("label")
            for j, (_, r) in enumerate(g.iterrows()):
                ax_a.plot(XPOS[cat] - 0.12 + j * 0.085, v, "o", ms=3.6, color=COL[r.culture], mec="white", mew=0.4,
                          zorder=3)
            xr = XPOS[cat] - 0.12 + (len(g) - 1) * 0.085
            ax_a.plot([xr + 0.06, XPOS[cat] + 0.27], [v, 10 ** ly], color="#C8C8C8", lw=0.4, zorder=1)
            ax_a.text(XPOS[cat] + 0.29, 10 ** ly, text, fontsize=SIZES[2], va="center", ha="left", linespacing=1.0)
    ax_a.set_yscale("log")
    ax_a.set_ylim(0.6, 45000)
    ax_a.set_yticks([1, 10, 100, 1000, 10000])
    ax_a.set_yticklabels(["1", "10", "100", "1k", "10k"])
    ax_a.minorticks_off()
    ax_a.set_xlim(-0.3, 3.45)
    ax_a.set_xticks(XPOS)
    ax_a.set_xticklabels(["genes written as names\n(K, text routes)", "vectors or codes given\nto the language model",
                          "features entering\nthe encoder"])
    ax_a.tick_params(axis="x", length=0)
    ax_a.set_ylabel("count per cell or biological object")
    ax_a.set_title("Text keeps about 100 genes; encoders emit tens of vectors", loc="left")
    for j, c in enumerate(["T", "H", "E", "C", "A"]):
        yy = 10 ** (4.5 - j * 0.2)
        ax_a.plot(-0.12, yy, "o", ms=3.6, color=COL[c], mec="white", mew=0.4)
        ax_a.text(-0.05, yy, NAME[c], fontsize=SIZES[2], va="center")
    rng = np.random.default_rng(3)
    order = ["T", "E", "H", "C"]
    labels = {"T": "Token-native", "E": "Encoder-\nmediated", "H": "Hybrid", "C": "Language-\nconditioned"}
    for ax, col, title, yl in [
        (ax_b, "opaque_step_share", "Learned modules hide encoder steps",
         "opaque learned steps\n(share of route steps)"),
        (ax_c, "unstated_slot_share", "Reporting gaps do not differ by culture",
         "unstated parameters\n(share of slots)"),
    ]:
        ticks = []
        for i, c in enumerate(order):
            v = w.loc[w.culture == c, col].dropna().values
            ax.plot(i + rng.uniform(-0.17, 0.17, len(v)), v, "o", ms=2.6, color=COL[c], alpha=0.85, mec="none")
            ax.plot([i - 0.28, i + 0.28], [np.median(v)] * 2, color="black", lw=1.2)
            ticks.append(f"{labels[c]}\nn = {len(v)}")
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(ticks, linespacing=1.05)
        colour_ticklabels(ax.get_xticklabels(), order)
        ax.tick_params(axis="x", length=0, pad=2)
        ax.set_xlim(-0.5, 3.5)
        ax.set_ylim(-0.04, 1.04)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(["0", "0.5", "1"])
        ax.set_ylabel(yl, fontsize=SIZES[1])
        ax.set_title(title, loc="left")
    w[["work", "culture", "opaque_step_share", "unstated_slot_share", "n_slots"]].to_csv(OUT / "figure4bc_shares.csv",
                                                                                       index=False)
    fig.canvas.draw()
    for ax, L, x in [(ax_a, "a", 0.006), (ax_b, "b", 0.575), (ax_c, "c", 0.575)]:
        letter(fig, x, ax, L)
    save(fig, "figure4")


# ----------------------------------------------------------------------------------------- Figure 5
OPP = [("prompted_general_llm", "prompted general LLM", "#D9D9D9", "/////"),
       ("external_embedding", "released encoder, frozen", "#D9D9D9", None),
       ("external_pretrained", "released model as published", "#F0F0F0", None),
       ("trained_baseline", "baseline trained by the proposers", "#8C8C8C", None),
       ("trained_ablation", "ablation by the proposers", "#4D4D4D", None),
       ("numeric_vectors", "no model", "white", None)]
TASK = {"categorical": "categorical", "text_generation": "text generation", "embedding_quality": "embedding quality",
        "generation_quantitative": "quantitative generation", "sequence_level": "sequence-level",
        "spatial_quantitative": "spatial", "generation_other": "other generation", "multi_task": "multi-task"}


def figure5(d):
    w, u = d["works"], d["units"]
    fig = plt.figure(figsize=(180 * MM, 128 * MM))
    ax_a = fig.add_axes([0.215, 0.635, 0.25, 0.31])
    ax_b = fig.add_axes([0.665, 0.66, 0.325, 0.285])
    ax_c = fig.add_axes([0.155, 0.235, 0.31, 0.27])
    ax_d = fig.add_axes([0.665, 0.07, 0.325, 0.43])
    # a: rationales
    rat = [("T", "rationale_T_no_architecture_change_for_own", "architecture left unchanged"),
           ("T", "rationale_T_leverage_llm_knowledge_for_own", "uses the LLM's prior knowledge"),
           ("T", "rationale_T_concedes_information_loss", "concedes loss of quantitative detail"),
           ("E", "rationale_E_criticises_text_fidelity", "criticises text for losing values")]
    for i, (c, col, _) in enumerate(rat):
        n = int((w.culture == c).sum())
        k_ = int(w.loc[w.culture == c, col].sum())
        y = len(rat) - 1 - i
        ax_a.barh(y, k_ / n, color=COL[c], height=0.62)
        ax_a.text(k_ / n + 0.02, y, f"{k_} of {n}", va="center", fontsize=SIZES[1])
    ax_a.set_yticks(range(len(rat)))
    ax_a.set_yticklabels([r[2] for r in rat][::-1])
    colour_ticklabels(ax_a.get_yticklabels(), [r[0] for r in rat][::-1])
    ax_a.tick_params(axis="y", length=0)
    ax_a.set_xlim(0, 0.8)
    ax_a.set_xticks([0, 0.25, 0.5, 0.75])
    ax_a.set_xticklabels(["0", "25%", "50%", "75%"])
    ax_a.set_xlabel("works in the culture stating it")
    ax_a.set_title("Both cultures name the same trade-off", loc="left")
    # b: supervision and adaptation
    rows = ["T", "E", "H", "C"]
    cols = [("llm_written_text", "LLM-written\ntext"), ("llm_frozen", "LLM\nfrozen"),
            ("llm_lora_or_adapter", "LoRA or\nadapter"), ("llm_full_finetune", "full\nfine-tuning"),
            ("llm_trained_from_scratch", "trained\nfrom scratch")]
    M = np.array([[int(w.loc[w.culture == c, k].sum()) for k, _ in cols] for c in rows])
    nn = np.array([int((w.culture == c).sum()) for c in rows])
    S = M / nn[:, None]
    ax_b.imshow(S, cmap="Greys", vmin=0, vmax=1.25, aspect="auto")
    for i in range(len(rows)):
        for j in range(len(cols)):
            ax_b.text(j, i, f"{M[i, j]}/{nn[i]}", ha="center", va="center", fontsize=SIZES[1],
                      color="white" if S[i, j] > 0.62 else "black")
    ax_b.set_xticks(range(len(cols)))
    ax_b.set_xticklabels([c[1] for c in cols])
    ax_b.set_yticks(range(len(rows)))
    ax_b.set_yticklabels([NAME[c] for c in rows])
    colour_ticklabels(ax_b.get_yticklabels(), rows)
    ax_b.tick_params(length=0)
    for sp in ax_b.spines.values():
        sp.set_visible(False)
    ax_b.set_title("Supervision and adaptation differ little", loc="left")
    pd.DataFrame(M, index=rows, columns=[c[0] for c in cols]).assign(n=nn).to_csv(OUT / "figure5b_practices.csv")
    # c: opponents by proposed representation
    prow = ["T", "E", "H", "P"]
    left = np.zeros(len(prow))
    for key, lab, fc, hatch in OPP:
        vals = np.array([int(((u.proposed == c) & (u.opponent == key)).sum()) for c in prow])
        ax_c.barh(np.arange(len(prow))[::-1], vals, left=left, color=fc, edgecolor="#4D4D4D", lw=0.5, hatch=hatch,
                  height=0.62, label=lab)
        left += vals
    ax_c.set_yticks(np.arange(len(prow))[::-1])
    ax_c.set_yticklabels([f"{NAME[c]} ({int((u.proposed == c).sum())})" for c in prow])
    colour_ticklabels(ax_c.get_yticklabels(), prow)
    ax_c.tick_params(axis="y", length=0)
    ax_c.set_xlim(0, 14)
    ax_c.set_xlabel("cross-culture comparisons, by proposed representation")
    ax_c.legend(loc="upper left", bbox_to_anchor=(-0.02, -0.30), ncol=2, fontsize=SIZES[2], handlelength=1.3,
                handleheight=0.9, columnspacing=1.2, borderaxespad=0)
    ax_c.set_title("Opponents are mostly released, unadapted models", loc="left")
    # d: outcome by task family
    fams = u.task_family.value_counts().index.tolist()
    marker = {"between": "s", "controlled": "o", "same_backbone": "D"}
    for i, f in enumerate(fams):
        sub = u[u.task_family == f].sort_values(["proposed_wins", "proposed"], ascending=[False, True])
        y = len(fams) - 1 - i
        for j, (_, r) in enumerate(sub.iterrows()):
            ax_d.plot(j * 0.55, y, marker[r.design], ms=3.8, mfc=COL[r.proposed] if r.proposed_wins else "white",
                      mec=COL[r.proposed], mew=0.8)
    ax_d.set_yticks(range(len(fams))[::-1])
    ax_d.set_yticklabels([f"{TASK.get(f, f)} ({int((u.task_family == f).sum())})" for f in fams])
    ax_d.tick_params(axis="y", length=0)
    ax_d.set_xticks([])
    ax_d.spines["bottom"].set_visible(False)
    ax_d.set_xlim(-0.4, 6.0)
    ax_d.set_ylim(-0.6, len(fams) - 0.4)
    ax_d.set_title("Proposers won most units in every task family", loc="left")
    hd = [Line2D([0], [0], marker="s", ls="", mfc="#4D4D4D", mec="#4D4D4D", ms=3.6),
          Line2D([0], [0], marker="o", ls="", mfc="#4D4D4D", mec="#4D4D4D", ms=3.6),
          Line2D([0], [0], marker="D", ls="", mfc="#4D4D4D", mec="#4D4D4D", ms=3.4),
          Line2D([0], [0], marker="s", ls="", mfc="white", mec="#4D4D4D", ms=3.6, mew=0.8)]
    ax_d.legend(hd, ["between systems", "controlled ablation", "same backbone", "open: proposer did not win"],
                loc="lower right", fontsize=SIZES[2], handletextpad=0.4, borderaxespad=0.2, labelspacing=0.5)
    u[["unit", "work", "proposed", "design", "winner", "task_family", "opponent", "opponent_class",
       "proposed_wins"]].to_csv(OUT / "figure5cd_units.csv", index=False)
    fig.canvas.draw()
    for ax, L, x in [(ax_a, "a", 0.006), (ax_b, "b", 0.505), (ax_c, "c", 0.006), (ax_d, "d", 0.505)]:
        letter(fig, x, ax, L)
    save(fig, "figure5")


def main():
    style()
    OUT.mkdir(parents=True, exist_ok=True)
    d = load()
    figure1(d)
    figure3(d)
    figure4(d)
    figure5(d)


if __name__ == "__main__":
    main()
