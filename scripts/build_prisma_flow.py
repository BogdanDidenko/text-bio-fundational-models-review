"""Build the cumulative PRISMA 2020 flow (55 included records) from the frozen run artifacts.

Inputs are the committed baseline fact table, the 2026-08-09 update facts, the supplemental
XunZi recall stage, the full-text decisions (with manual resolutions) and the current atlas.
Every number in the output is recomputed or read from those files; nothing is typed in.
"""

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_FACTS = ROOT / "analysis/living_review_baseline_prisma_facts_2026-08-09.json"
UPDATE = ROOT / "data/living_catalog_updates/update_2026-08-09"
BASE_FT = ROOT / "data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10"
ATLAS = ROOT / "docs/input-representation-atlas/data/atlas.json"
OUT = ROOT / "analysis/prisma_flow_2026-10-07"

REASON_LABELS = {
    "EC2_no_text_component": "No natural-language text component",
    "EC2_no_substantive_text_bio_bridge": "No substantive text-biology bridge",
    "application_wrapper": "Application wrapper around an existing model",
    "EC3_not_generative": "Not a generative model",
    "review_editorial": "Review or editorial",
    "EC1_no_bio_modality": "No biological data modality",
    "benchmark_resource": "Benchmark or resource without a new model",
    "EC4_no_foundation_model_evidence": "No foundation-model evidence",
}


def load(path):
    return json.loads(Path(path).read_text())


def records(value):
    return value["records"] if isinstance(value, dict) else value


def facts():
    base = load(BASE_FACTS)["prisma"]
    upd = load(UPDATE / "16_report/prisma_update_facts.json")
    cand = load(UPDATE / "05_fulltext/fulltext_candidates.json")["metadata"]
    xunzi_ta = load(UPDATE / "04_abstract_screening_manual_recall_xunzi_2026-08-11/summary.json")
    xunzi_ft = load(UPDATE / "09_fulltext_screening_manual_recall_xunzi_2026-08-11/summary.json")
    xunzi_acc = records(load(UPDATE / "10_eligibility_manual_recall_xunzi_2026-08-11/accepted_records.json"))
    upd_acc = records(load(UPDATE / "10_eligibility/accepted_records.json"))
    atlas = load(ATLAS)["meta"]

    # Full-text exclusion reasons: baseline automatic decisions overridden by manual resolution, plus update.
    manual = {r["record_id"]: r for r in csv.DictReader(open(BASE_FT / "manual_resolution_2026-07-10.csv"))}
    reasons, base_inc = Counter(), 0
    for r in records(load(BASE_FT / "final_screening_results.json")):
        decision, code = r["final_decision"], r.get("final_code")
        if r["record_id"] in manual:
            decision, code = manual[r["record_id"]]["manual_decision"], manual[r["record_id"]]["manual_exclusion_code"]
        reasons[code] += decision == "EXCLUDE"
        base_inc += decision == "INCLUDE"
    reasons += Counter(r["final_code"] for r in records(load(UPDATE / "10_eligibility/excluded_records.json")))
    reasons = Counter({k: v for k, v in reasons.items() if v})

    upd_dups = upd["within_update_duplicates_removed"] + upd["already_in_cumulative_master"] + upd["crossref_hidden_duplicates"]
    f = {
        "search_window": {"from": "2018-01-01", "to": upd["date_to"]},
        "rounds": [r["label"] for r in load(BASE_FACTS)["search_rounds"]] + ["August top-up (2026-07-07 to 2026-08-09)"],
        "identified_databases": base["records_identified"] + upd["raw_hits"],
        "identified_other_methods": len(xunzi_acc),
        "duplicates_removed": base["duplicates_removed"] + upd_dups,
        "removed_no_usable_abstract": base["records_without_usable_abstracts"] + upd["records_without_usable_abstract"],
        "screened": base["title_abstract_screened"] + upd["abstracts_screened"],
        "screen_excluded": base["title_abstract_excluded"] + upd["abstract_decisions"]["EXCLUDE"],
        "postscreen_duplicates": cand["postscreen_duplicates_removed"],
        "sought": base["fulltext_candidates"] + cand["candidate_count"],
        "not_retrieved": base["reports_not_retrieved"] + upd["reports_not_retrieved"],
        "no_valid_section_pair": base["reports_without_valid_targeted_section_pair"] + upd["unresolved_section_failures"],
        "assessed": base["complete_section_screened"] + upd["section_screening_input"],
        "excluded_fulltext": sum(reasons.values()),
        "exclusion_reasons": dict(reasons.most_common()),
        "included_databases": base["accepted_records"] + len(upd_acc),
        "other_screened": xunzi_ta["total_records"],
        "other_assessed": xunzi_ft["total_records"],
        "included_other": len(xunzi_acc),
        "included_records": atlas["record_count"],
        "included_studies": atlas["study_count"],
        "models": atlas["model_count"], "configurations": atlas["configuration_count"], "routes": atlas["route_count"],
    }
    # Internal consistency: each stage must balance exactly.
    checks = {
        "identified - duplicates - no abstract = screened":
            f["identified_databases"] - f["duplicates_removed"] - f["removed_no_usable_abstract"] == f["screened"],
        "screened - excluded - postscreen duplicates = sought":
            f["screened"] - f["screen_excluded"] - f["postscreen_duplicates"] == f["sought"],
        "sought - not retrieved - no section pair = assessed":
            f["sought"] - f["not_retrieved"] - f["no_valid_section_pair"] == f["assessed"],
        "assessed - excluded = included (databases)": f["assessed"] - f["excluded_fulltext"] == f["included_databases"],
        "baseline includes after manual resolution = baseline accepted": base_inc == base["accepted_records"],
        "databases + other methods = atlas records": f["included_databases"] + f["included_other"] == f["included_records"],
    }
    if not all(checks.values()):
        raise SystemExit(f"PRISMA flow does not balance: {checks}")
    f["balance_checks"] = checks
    return f


def draw(f, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(8.2, 9.6))
    ax.set_xlim(0, 100), ax.set_ylim(0, 112), ax.axis("off")
    ink, band = "#202124", "#e8eef6"

    def box(x, y, w, h, text, fill="white", bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.8", fc=fill, ec=ink, lw=0.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7.2, color=ink,
                fontweight="bold" if bold else "normal", linespacing=1.35)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=ink, mutation_scale=8))

    for y, h, label in [(86, 22, "Identification"), (50, 34, "Screening"), (2, 46, "Included / eligibility")]:
        ax.add_patch(FancyBboxPatch((0.5, y), 5.5, h, boxstyle="round,pad=0.2", fc=band, ec="none"))
        ax.text(3.25, y + h / 2, label, rotation=90, ha="center", va="center", fontsize=7.5, fontweight="bold", color=ink)

    L, R, W, WR = 9, 57, 42, 42
    box(L, 92, W, 14, f"Records identified from 8 databases\n(5 search rounds, {f['search_window']['from']} to {f['search_window']['to']})\nn = {f['identified_databases']:,}")
    box(R, 92, WR, 14, f"Records removed before screening:\nduplicates n = {f['duplicates_removed']:,}\nno usable abstract n = {f['removed_no_usable_abstract']:,}")
    arrow(L + W, 99, R, 99)
    box(L, 72, W, 10, f"Records screened (title/abstract)\nn = {f['screened']:,}")
    arrow(L + W / 2, 92, L + W / 2, 82)
    box(R, 72, WR, 10, f"Records excluded n = {f['screen_excluded']:,}\npost-screen duplicate n = {f['postscreen_duplicates']}")
    arrow(L + W, 77, R, 77)
    box(L, 55, W, 10, f"Reports sought for retrieval\nn = {f['sought']}")
    arrow(L + W / 2, 72, L + W / 2, 65)
    box(R, 55, WR, 10, f"Reports not retrieved n = {f['not_retrieved']}\nno valid targeted section pair n = {f['no_valid_section_pair']}")
    arrow(L + W, 60, R, 60)
    box(L, 36, W, 10, f"Reports assessed for eligibility\n(complete targeted full-text sections)\nn = {f['assessed']}")
    arrow(L + W / 2, 55, L + W / 2, 46)
    reasons = "\n".join(f"{REASON_LABELS.get(k, k)}: {v}" for k, v in f["exclusion_reasons"].items())
    box(R, 24, WR, 28, f"Reports excluded n = {f['excluded_fulltext']}\n\n{reasons}")
    arrow(L + W, 41, R, 41)
    box(R, 5, WR, 12, f"Records identified by\nsupplemental recall correction\n(screened and assessed with the\nfrozen pipelines) n = {f['included_other']}", fill="#f8f9fa")
    box(L, 5, W, 12, f"Records included in review n = {f['included_records']}\n({f['included_databases']} via databases + {f['included_other']} via recall correction)\n"
                     f"{f['included_studies']} studies · {f['models']} models · {f['routes']} input routes", bold=True)
    arrow(L + W / 2, 36, L + W / 2, 17)
    arrow(R, 11, L + W, 11)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def markdown(f):
    rows = [("Records identified from databases", f["identified_databases"]),
            ("Records identified by supplemental recall correction", f["identified_other_methods"]),
            ("Duplicates removed", f["duplicates_removed"]),
            ("Removed: no usable abstract", f["removed_no_usable_abstract"]),
            ("Records screened (title/abstract)", f["screened"]),
            ("Records excluded at title/abstract", f["screen_excluded"]),
            ("Post-screen duplicate removed", f["postscreen_duplicates"]),
            ("Reports sought for retrieval", f["sought"]),
            ("Reports not retrieved", f["not_retrieved"]),
            ("Reports without a valid targeted section pair", f["no_valid_section_pair"]),
            ("Reports assessed for eligibility", f["assessed"]),
            ("Reports excluded at full text", f["excluded_fulltext"]),
            ("Records included via databases", f["included_databases"]),
            ("Records included via recall correction", f["included_other"]),
            ("Records included (total)", f["included_records"]),
            ("Studies included", f["included_studies"])]
    out = ["# PRISMA 2020 flow: cumulative corpus through 2026-08-09 (55 records)", "",
           "Generated by `scripts/build_prisma_flow.py` from the frozen run artifacts. No search refresh",
           "was performed for the manuscript (author decision, 2026-10-07).", "",
           "| Stage | n |", "|---|---:|"] + [f"| {a} | {b:,} |" for a, b in rows]
    out += ["", "## Full-text exclusion reasons", "", "| Reason | Code | n |", "|---|---|---:|"]
    out += [f"| {REASON_LABELS.get(k, k)} | `{k}` | {v} |" for k, v in f["exclusion_reasons"].items()]
    out += ["", "## Notes", "",
            "- Databases: PubMed, Scopus, Semantic Scholar, arXiv, bioRxiv/medRxiv, Springer Nature and Google Scholar"
            " in all rounds; OpenAlex was added in the August top-up. Google Scholar returned 0 records in the July"
            " round (rate-limited).",
            "- Duplicates include within-round, cross-round (cumulative master) and Crossref-audited hidden duplicates.",
            "- XunZi (10.1038/s41551-026-01769-6) was recovered after the pre-screen lexical validator was amended to"
            " recognise 'AI biologist'; it then passed the frozen abstract and full-text section screening.",
            "- The withdrawn OKR-Cell preprint (full_2026-07-06__rec_001277) is counted among the 55 records pending an"
            " author decision.",
            f"- Corpus after the 2026-08-17 semantic correction: {f['models']} models, {f['configurations']} task/input"
            f" configurations, {f['routes']} grounded input routes (atlas.json).", "",
            "## Balance checks", ""] + [f"- [{'x' if ok else ' '}] {name}" for name, ok in f["balance_checks"].items()]
    return "\n".join(out) + "\n"


def main():
    f = facts()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "prisma_facts.json").write_text(json.dumps(f, indent=2, sort_keys=True) + "\n")
    (OUT / "PRISMA_FLOW.md").write_text(markdown(f))
    draw(f, OUT / "prisma_flow.png")
    print(json.dumps({k: f[k] for k in ("identified_databases", "screened", "sought", "assessed", "excluded_fulltext",
                                         "included_records", "included_studies")}, indent=1))


if __name__ == "__main__":
    main()
