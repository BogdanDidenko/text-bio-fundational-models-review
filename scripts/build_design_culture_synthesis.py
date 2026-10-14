#!/usr/bin/env python3
"""Numbers for the design-culture analysis (paper 1), computed from committed tables only.

Inputs:
- analysis/design_culture_charting_2026-10-14/v11/{steward_adjudication.json, consensus_items.csv,
  comparison_units_adjudicated.csv, agreement.json}
- analysis/discovery_2026-10-14/{synthetic_text_table.csv, gene_budget_table.csv, token_budget_table.csv,
  routes.parquet}

Output: analysis/design_culture_charting_2026-10-14/v11/design_culture_numbers.json
"""
import json
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest, fisher_exact

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "analysis/design_culture_charting_2026-10-14/v11"
DI = ROOT / "analysis/discovery_2026-10-14"
LINKED = {"full_2026-07-06__rec_000827": "W_cellwhisperer", "full_2026-07-06__rec_002105": "W_cellwhisperer",
          "full_2026-07-06__rec_002327": "W_omnina", "full_2026-07-06__rec_003394": "W_omnina",
          "june_update_2026-06-10__rec_000248": "W_cell2text", "full_2026-07-06__rec_001838": "W_cell2text"}
DEP = ["remove_biological_input", "mismatched_or_shuffled_input", "random_or_noise_input",
       "text_only_or_llm_only_baseline", "perturb_content_of_input", "order_or_value_ablation"]


def work(record):
    return LINKED.get(record, record)


def per_culture(works, culture):
    out = {}
    for c in ["T", "E", "H", "C", "A"]:
        members = [w for w, k in culture.items() if k == c]
        out[c] = {"n": len(members), "count": sum(w in works for w in members)}
    return out


def main():
    adj = json.loads((CH / "steward_adjudication.json").read_text())
    culture = adj["culture"]
    n_by = pd.Series(culture).value_counts().to_dict()
    ci = pd.read_csv(CH / "consensus_items.csv")
    ci["work"] = ci.record_id.map(work)
    ci["both"] = (ci.run1 == 1) & (ci.run2 == 1)

    # biology-dependence tests (both runs + adjudicated single-run additions)
    dep = ci[(ci.field == "biology_dependence_tests") & ci.category.isin(DEP) & ci.both]
    dep_works = set(dep.work) | set(adj["dependence_tests"]["added_single_run"])
    dep_works -= set(adj["dependence_tests"]["excluded_single_run"])

    # LLM and encoder states, vocabulary (both runs)
    def states(field):
        d = ci[(ci.field == field) & ci.both]
        return {cat: per_culture(set(g.work), culture) for cat, g in d.groupby("category")}

    syn = pd.read_csv(DI / "synthetic_text_table.csv")
    rat = {k: per_culture(set(v), culture) for k, v in adj["rationale_adjudicated"].items() if isinstance(v, list)}

    cu = pd.read_csv(CH / "comparison_units_adjudicated.csv")
    between = cu[cu.design == "between"]
    comp = {
        "units": len(cu), "works": int(cu.work.nunique()),
        "proposed_wins_all": int(cu.proposed_wins.sum()),
        "between_units": len(between), "between_proposed_wins": int(between.proposed_wins.sum()),
        "between_binomial_p": binomtest(int(between.proposed_wins.sum()), len(between), 0.5).pvalue,
        "controlled_units": int((cu.design == "controlled").sum()),
        "controlled_proposed_wins": int(cu[cu.design == "controlled"].proposed_wins.sum()),
        "winners_between": between.winner.value_counts().to_dict(),
        "winner_by_design": pd.crosstab(cu.design, cu.winner).to_dict(orient="index"),
        "opponent_by_proposed": pd.crosstab(cu.proposed, cu.opponent).to_dict(orient="index"),
        "winner_by_t_arm_content": pd.crosstab(cu.t_arm_content.fillna("-"), cu.winner).to_dict(orient="index"),
    }

    # robustness of the comparison result (stress test, 2026-10-14)
    released = {"prompted_general_llm", "external_embedding", "external_pretrained"}
    self_built = {"trained_baseline", "trained_ablation"}
    cu["opponent_class"] = cu.opponent.map(lambda o: "released" if o in released else
                                           ("trained_by_proposer" if o in self_built else "no_model"))
    by_work = cu.groupby("work").proposed_wins.all()
    by_work_between = between.groupby("work").proposed_wins.all()

    def fisher(a, n1, b, n2):
        return fisher_exact([[a, n1 - a], [b, n2 - b]])[1]

    def opp_share(proposed, kinds):
        d = cu[cu.proposed == proposed]
        return int(d.opponent.isin(kinds).sum()), len(d)

    e_pr, e_n = opp_share("E", {"prompted_general_llm"})
    t_pr, t_n = opp_share("T", {"prompted_general_llm"})
    e_ex, _ = opp_share("E", {"external_embedding", "external_pretrained"})
    t_ex, _ = opp_share("T", {"external_embedding", "external_pretrained"})
    comp["robustness"] = {
        "by_opponent_class": {k: {"units": len(g), "proposed_wins": int(g.proposed_wins.sum()),
                                  "non_wins": sorted(g[~g.proposed_wins].unit)}
                              for k, g in cu.groupby("opponent_class")},
        "work_level_all_units": {"works": len(by_work), "proposer_won_all": int(by_work.sum()),
                                 "sign_test_p": binomtest(int(by_work.sum()), len(by_work), 0.5).pvalue},
        "work_level_between": {"works": len(by_work_between), "proposer_won_all": int(by_work_between.sum()),
                               "sign_test_p": binomtest(int(by_work_between.sum()), len(by_work_between), 0.5).pvalue},
        "opponent_prompted_llm_E_vs_T": {"E": [e_pr, e_n], "T": [t_pr, t_n], "fisher_p": fisher(e_pr, e_n, t_pr, t_n)},
        "opponent_released_encoder_T_vs_E": {"T": [t_ex, t_n], "E": [e_ex, e_n], "fisher_p": fisher(t_ex, t_n, e_ex, e_n)},
        "by_task_family": {k: {"units": len(g), "proposed_wins": int(g.proposed_wins.sum()),
                               "proposed": g.proposed.value_counts().to_dict(), "winner": g.winner.value_counts().to_dict()}
                           for k, g in cu.groupby("task_family")},
    }
    comp_works = set(cu.work)
    a = len(comp_works & dep_works)
    b = len(dep_works - comp_works)
    n_other = len(set(culture) - comp_works)
    comp["robustness"]["dependence_by_comparison_status"] = {
        "with_cross_culture_units": [a, len(comp_works)], "without": [b, n_other],
        "fisher_p": fisher(a, len(comp_works), b, n_other)}

    gb = pd.read_csv(DI / "gene_budget_table.csv")
    text_prop = gb[gb.route_kind == "text: proposed model input"].groupby("record_id").genes_kept.max().dropna()
    emb_prop = gb[gb.route_kind == "embedding: proposed model input"].groupby("record_id").genes_kept.max()
    tb = pd.read_csv(DI / "token_budget_table.csv")
    soft = tb[~tb.unit.str.contains("text tokens")]

    routes = pd.read_parquet(DI / "routes.parquet")
    routes["work"] = routes.record_id.map(work)
    routes["culture"] = routes.work.map(culture)
    bio = routes[routes.source_modality_normalized.fillna("").str.lower() != "text"]
    opaque = bio.groupby(["culture", "work"]).opaque_step_share.median().groupby("culture").median().round(2).to_dict()

    # exploratory culture contrasts (two-sided Fisher exact tests, unadjusted)
    def cnt(ws, c):
        members = [w for w, k in culture.items() if k == c]
        return sum(w in ws for w in members), len(members)

    def vs_rest(ws, c):
        a, n1 = cnt(ws, c)
        b = sum(w in ws for w, k in culture.items() if k != c)
        n2 = sum(1 for k in culture.values() if k != c)
        return {"group": [a, n1], "rest": [b, n2], "fisher_p": fisher(a, n1, b, n2)}

    def t_vs_e(ws):
        a, n1 = cnt(ws, "T")
        b, n2 = cnt(ws, "E")
        return {"T": [a, n1], "E": [b, n2], "fisher_p": fisher(a, n1, b, n2)}

    syn_works = set(syn.work)
    frozen = set(ci[(ci.field == "llm_state") & ci.both & (ci.category == "frozen")].work)
    contrasts = {
        "dependence_T_vs_E": t_vs_e(dep_works), "dependence_E_vs_rest": vs_rest(dep_works, "E"),
        "synthetic_T_vs_E": t_vs_e(syn_works), "synthetic_C_vs_rest": vs_rest(syn_works, "C"),
        "frozen_llm_T_vs_E": t_vs_e(frozen),
        "note": "exploratory, two-sided, unadjusted",
    }

    def by_culture(series_index_records, values):
        cult = [culture.get(work(r)) for r in series_index_records]
        return {c: sorted(v for v, k in zip(values, cult) if k == c) for c in ["T", "E", "H", "C", "A"]}

    budget_by_culture = {
        "text_K_proposed": by_culture(text_prop.index, text_prop.tolist()),
        "embedding_input_features": by_culture(emb_prop.index, emb_prop.tolist()),
        "vectors_per_object": by_culture(soft.record_id.tolist(), soft.tokens.tolist()),
    }

    # per-work table (source data for the figures)
    slots = pd.read_parquet(DI / "slots.parquet")
    roles = json.loads((ROOT / "analysis/design_culture_charting_2026-10-14/roles.json").read_text())
    role_of = {(r, m["model_name"]): m["role"] for r, ms in roles.items() for m in ms}
    slots["role"] = [role_of.get((r, m)) for r, m in zip(slots.record_id, slots.model_name)]
    sl = slots[slots.role.isin(["proposed", "component"])].copy()
    sl["work"] = sl.record_id.map(work)
    sl["unstated"] = sl.status == "unspecified"
    llm = {cat: set(g.work) for cat, g in ci[(ci.field == "llm_state") & ci.both].groupby("category")}
    wt = pd.DataFrame({"work": sorted(culture)})
    wt["culture"] = wt.work.map(culture)
    wt["dependence_test"] = wt.work.isin(dep_works)
    wt["llm_written_text"] = wt.work.isin(syn_works)
    for cat in ["frozen", "lora_or_adapter", "full_finetune", "trained_from_scratch"]:
        wt[f"llm_{cat}"] = wt.work.isin(llm.get(cat, set()))
    for k, v in adj["rationale_adjudicated"].items():
        if isinstance(v, list):
            wt[f"rationale_{k}"] = wt.work.isin(set(v))
    wt["cross_culture_units"] = wt.work.map(cu.groupby("work").size()).fillna(0).astype(int)
    wt["opaque_step_share"] = wt.work.map(bio.groupby("work").opaque_step_share.median())
    wt["unstated_slot_share"] = wt.work.map(sl.groupby("work").unstated.mean())
    wt["n_slots"] = wt.work.map(sl.groupby("work").size()).fillna(0).astype(int)
    wt.to_csv(CH / "work_level_table.csv", index=False)
    cu.to_csv(CH / "comparison_units_with_opponent_class.csv", index=False)

    numbers = {
        "works": len(culture), "culture_n": n_by,
        "dependence_tests": {"works": len(dep_works), "by_culture": per_culture(dep_works, culture)},
        "synthetic_text": {"works": int(syn.work.nunique()), "by_culture": per_culture(set(syn.work), culture),
                           "category": syn.category.value_counts().to_dict(),
                           "reasoning_traces": int(syn.reasoning_traces.sum()), "human_check": int(syn.human_check.sum()),
                           "llm_text_in_evaluation": int(syn.llm_text_in_evaluation.sum())},
        "llm_state": states("llm_state"), "encoder_state": states("encoder_state"),
        "rationale": rat, "comparisons": comp,
        "gene_budget": {"text_works_with_K": len(text_prop), "text_K_median": float(text_prop.median()),
                        "text_K_min": float(text_prop.min()), "text_K_max": float(text_prop.max()),
                        "embedding_works": len(emb_prop), "embedding_min": float(emb_prop.min()),
                        "embedding_max": float(emb_prop.max()), "embedding_median": float(emb_prop.median())},
        "soft_token_budget": {"works": int(soft.record_id.nunique()), "min": int(soft.tokens.min()),
                              "max": int(soft.tokens.max()), "median": float(soft.tokens.median())},
        "median_opaque_share_by_culture": opaque,
        "budget_by_culture": budget_by_culture,
        "culture_contrasts_fisher": contrasts,
        "agreement": {k: v["mean_jaccard"] for k, v in json.loads((CH / "agreement.json").read_text())["fields"].items()},
    }
    (CH / "design_culture_numbers.json").write_text(json.dumps(numbers, indent=1, default=str))
    print(json.dumps({k: numbers[k] for k in ["culture_n", "dependence_tests", "gene_budget", "soft_token_budget",
                                               "median_opaque_share_by_culture"]}, default=str))
    print(json.dumps({k: v for k, v in comp.items() if k in ["units", "works", "proposed_wins_all", "between_units",
                                                             "between_proposed_wins", "between_binomial_p",
                                                             "controlled_units", "controlled_proposed_wins"]}))


if __name__ == "__main__":
    main()
