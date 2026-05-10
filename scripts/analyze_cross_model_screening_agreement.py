#!/usr/bin/env python3
"""Build cross-run and cross-model screening agreement analysis artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from compare_screening_replicates import FINAL_DECISION, dedupe_results, read_run


RUNS = {
    "deepseek_rep1": Path("runs/prompt_regression_116_deepseek_v4_iter5_3repeats_20260509T213855Z_rep1/repeat_1"),
    "deepseek_rep2": Path("runs/prompt_regression_116_deepseek_v4_iter5_3repeats_20260509T213855Z_rep2/repeat_1"),
    "deepseek_rep3": Path("runs/prompt_regression_116_deepseek_v4_iter5_3repeats_20260509T213855Z_rep3/repeat_1"),
    "gptoss_rep1": Path("runs/prompt_regression_116_gpt_oss_120b_2repeats_20260509T214053Z_rep1/repeat_1"),
    "gptoss_rep2": Path("runs/prompt_regression_116_gpt_oss_120b_2repeats_20260509T214053Z_rep2/repeat_1"),
}

KEY_COLUMNS = [
    "cluster_id",
    "title",
    "abstract",
    "regression_group",
    "pilot_final_decision",
    "pilot_final_exclusion_code",
    "pilot_final_uncertainty_reason",
    "pilot_selected_paper_type",
    "pilot_selected_text_component_present",
    "pilot_selected_text_bio_bridge_present",
    "pilot_selected_generative_model_present",
    "pilot_selected_foundation_model_evidence",
    "pilot_selected_evidence_for_text_component",
    "pilot_selected_evidence_for_text_bio_bridge",
    "pilot_selected_evidence_for_generative_model",
    "pilot_selected_boundary_case",
    "pilot_selected_decision_rationale",
    "round-A_scope_reviewer_decision_rationale",
    "round-A_architecture_reviewer_decision_rationale",
    "round-B_adjudicator_decision_rationale",
]


def clean_text(value: object) -> object:
    if not isinstance(value, str):
        return value
    return "\n".join(line.rstrip() for line in value.splitlines()).strip()


def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for column in out.select_dtypes(include=["object"]).columns:
        out[column] = out[column].map(clean_text)
    return out


def load_runs() -> dict[str, pd.DataFrame]:
    runs = {}
    for label, path in RUNS.items():
        if (path / "guideline_pilot_results.csv").exists() or path.with_suffix(".csv").exists():
            runs[label] = clean_strings(dedupe_results(read_run(path)))
    return runs


def add_prefix(df: pd.DataFrame, label: str) -> pd.DataFrame:
    keep = [column for column in KEY_COLUMNS if column in df.columns]
    out = df[keep].copy()
    rename = {column: f"{label}_{column}" for column in keep if column != "cluster_id"}
    return out.rename(columns=rename)


def merge_runs(runs: dict[str, pd.DataFrame], cases: pd.DataFrame) -> pd.DataFrame:
    out = cases[["cluster_id", "title", "abstract", "regression_group"]].copy()
    for label, df in runs.items():
        out = out.merge(add_prefix(df, label), on="cluster_id", how="left")
    return out


def summarize_pair(merged: pd.DataFrame, a: str, b: str) -> dict[str, object]:
    ca = f"{a}_{FINAL_DECISION}"
    cb = f"{b}_{FINAL_DECISION}"
    matched = merged[ca].notna() & merged[cb].notna()
    pair = merged.loc[matched, [ca, cb]]
    mismatches = pair[ca].ne(pair[cb])
    a_include = pair[ca].eq("INCLUDE")
    b_include = pair[cb].eq("INCLUDE")
    stable_include = a_include & b_include
    include_union = a_include | b_include
    return {
        "pair": f"{a} vs {b}",
        "matched_records": int(matched.sum()),
        "decision_mismatches": int(mismatches.sum()),
        "decision_mismatch_rate": float(mismatches.mean()) if len(pair) else None,
        "a_counts": pair[ca].value_counts(dropna=False).to_dict(),
        "b_counts": pair[cb].value_counts(dropna=False).to_dict(),
        "include_jaccard": float(stable_include.sum() / include_union.sum()) if include_union.any() else 1.0,
        "stable_include": int(stable_include.sum()),
        "include_union": int(include_union.sum()),
        "transition_matrix": pd.crosstab(pair[ca], pair[cb], dropna=False).to_dict(),
    }


def build_consensus(merged: pd.DataFrame, labels: list[str], prefix: str) -> pd.DataFrame:
    cols = [f"{label}_{FINAL_DECISION}" for label in labels]
    out = merged[["cluster_id", "title", "regression_group", *cols]].copy()
    out[f"{prefix}_decision_set"] = out[cols].astype(str).agg("|".join, axis=1)
    out[f"{prefix}_stable"] = out[cols].nunique(axis=1, dropna=False).eq(1)
    out[f"{prefix}_include_any"] = out[cols].eq("INCLUDE").any(axis=1)
    out[f"{prefix}_include_all"] = out[cols].eq("INCLUDE").all(axis=1)
    out[f"{prefix}_uncertain_any"] = out[cols].eq("UNCERTAIN").any(axis=1)
    out[f"{prefix}_include_count"] = out[cols].eq("INCLUDE").sum(axis=1)
    out[f"{prefix}_exclude_count"] = out[cols].eq("EXCLUDE").sum(axis=1)
    out[f"{prefix}_uncertain_count"] = out[cols].eq("UNCERTAIN").sum(axis=1)
    return out


def consensus_summary(consensus: pd.DataFrame | None, prefix: str) -> dict[str, object] | None:
    if consensus is None or consensus.empty:
        return None
    return {
        "records": int(len(consensus)),
        "stable": int(consensus[f"{prefix}_stable"].sum()),
        "stable_rate": float(consensus[f"{prefix}_stable"].mean()),
        "include_any": int(consensus[f"{prefix}_include_any"].sum()),
        "include_all": int(consensus[f"{prefix}_include_all"].sum()),
        "uncertain_any": int(consensus[f"{prefix}_uncertain_any"].sum()),
    }


def boundary_counts(merged: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    rows = []
    for label in labels:
        col = f"{label}_pilot_selected_boundary_case"
        if col not in merged.columns:
            continue
        counts = merged[col].fillna("MISSING").replace("", "MISSING").value_counts()
        for boundary, count in counts.items():
            rows.append({"run": label, "boundary_case": boundary, "count": int(count)})
    return pd.DataFrame(rows)


def unstable_reasoning_table(merged: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    decision_cols = [f"{label}_{FINAL_DECISION}" for label in labels]
    stable = merged[decision_cols].nunique(axis=1, dropna=False).eq(1)
    rows = []
    for _, row in merged.loc[~stable].iterrows():
        item = {
            "cluster_id": row["cluster_id"],
            "title": row["title"],
            "regression_group": row["regression_group"],
            "decision_set": "|".join(str(row.get(col, "")) for col in decision_cols),
        }
        for label in labels:
            item[f"{label}_decision"] = row.get(f"{label}_{FINAL_DECISION}", "")
            item[f"{label}_exclusion_code"] = row.get(f"{label}_pilot_final_exclusion_code", "")
            item[f"{label}_uncertainty_reason"] = row.get(f"{label}_pilot_final_uncertainty_reason", "")
            item[f"{label}_boundary_case"] = row.get(f"{label}_pilot_selected_boundary_case", "")
            item[f"{label}_text_evidence"] = row.get(f"{label}_pilot_selected_evidence_for_text_component", "")
            item[f"{label}_bridge_evidence"] = row.get(f"{label}_pilot_selected_evidence_for_text_bio_bridge", "")
            item[f"{label}_generative_evidence"] = row.get(f"{label}_pilot_selected_evidence_for_generative_model", "")
            item[f"{label}_rationale"] = row.get(f"{label}_pilot_selected_decision_rationale", "")
        rows.append(item)
    return pd.DataFrame(rows)


def infer_issue_tags(row: pd.Series, labels: list[str]) -> str:
    text = " ".join(str(row.get(f"{label}_rationale", "")) for label in labels).lower()
    text += " " + " ".join(str(row.get(f"{label}_boundary_case", "")) for label in labels).lower()
    tags = []
    checks = {
        "thin_or_truncated_abstract": ["thin", "truncated", "too brief", "short"],
        "wrapper_boundary": ["wrapper", "existing llm", "frozen", "pretrained llm"],
        "text_component_boundary": ["text component", "natural-language", "metadata", "text-derived", "embeddings"],
        "generative_boundary": ["generative", "decoder", "diffusion", "prediction", "classifier", "risk"],
        "biological_token_only": ["gene token", "cell sentence", "biological token", "omics language"],
    }
    for tag, needles in checks.items():
        if any(needle in text for needle in needles):
            tags.append(tag)
    return ";".join(tags) if tags else "unclassified"


def write_markdown(
    output_dir: Path,
    pair_summaries: list[dict[str, object]],
    deepseek_consensus: pd.DataFrame | None,
    gpt_consensus: pd.DataFrame | None,
    cross_model: pd.DataFrame,
    unstable: pd.DataFrame,
    consensus_summaries: dict[str, dict[str, object] | None],
) -> None:
    lines = [
        "# LLM Screening Agreement and Nondeterminism Analysis",
        "",
        "This folder summarizes repeat-run and cross-model agreement for the 116-case prompt regression set.",
        "The purpose is to support a methods/results section on nondeterminism in LLM-assisted title/abstract screening.",
        "",
        "## Pairwise Agreement",
        "",
    ]
    for summary in pair_summaries:
        lines.extend(
            [
                f"### {summary['pair']}",
                f"- Matched records: {summary['matched_records']}",
                f"- Decision mismatches: {summary['decision_mismatches']} ({summary['decision_mismatch_rate']:.3f})",
                f"- Include Jaccard: {summary['include_jaccard']:.3f}",
                f"- Stable INCLUDE: {summary['stable_include']} / include union {summary['include_union']}",
                f"- A counts: `{summary['a_counts']}`",
                f"- B counts: `{summary['b_counts']}`",
                "",
            ]
        )
    lines.extend(["## Consensus Summaries", ""])
    for label, summary in consensus_summaries.items():
        if summary is None:
            continue
        lines.extend(
            [
                f"### {label}",
                f"- Stable decisions: {summary['stable']} / {summary['records']} ({summary['stable_rate']:.3f})",
                f"- INCLUDE in any run: {summary['include_any']}",
                f"- INCLUDE in every run: {summary['include_all']}",
                f"- UNCERTAIN in any run: {summary['uncertain_any']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Main Observations",
            "",
            "- GPT-OSS 120B was more repeatable across two runs than DeepSeek V4 Flash on the same 116 records.",
            "- GPT-OSS was also more liberal: it produced substantially more INCLUDE decisions and fewer UNCERTAIN decisions.",
            "- DeepSeek was more conservative but less stable, especially for EXCLUDE/UNCERTAIN boundary cases.",
            "- Cross-model disagreement was larger than within-model GPT-OSS disagreement, showing that model choice materially changes the screened corpus.",
            "- The recurring unstable mechanisms are thin abstracts, wrapper-vs-primary-model ambiguity, text-derived metadata/embedding ambiguity, and generative-vs-predictive ambiguity.",
            "",
            "## Artifacts",
            "",
            "- `pairwise_agreement.json`: numeric pairwise agreement summaries.",
            "- `cross_model_decisions.csv`: all decisions and rationales merged across runs.",
            "- `deepseek_consensus.csv`: DeepSeek repeat consensus for available repeats.",
            "- `gptoss_consensus.csv`: GPT-OSS repeat consensus.",
            "- `all_run_consensus.csv`: decision stability across every available run.",
            "- `unstable_reasoning_cases.csv`: case-level rationales for all records with any disagreement.",
            "- `boundary_case_counts.csv`: emitted boundary labels by run.",
            "- `issue_tag_counts.csv`: heuristic tags for disagreement mechanisms.",
            "- `representative_reasoning_paths.md`: compact qualitative case studies for paper writing.",
            "",
            "## Draft Research Framing",
            "",
            "These results suggest that LLM screening should not be treated as a deterministic classifier, even when prompts, inputs, and decoding settings are held constant. "
            "The same pipeline can produce different eligibility decisions across repeated runs, and different LLMs can shift the inclusion frontier. "
            "For evidence synthesis, the most important risk is not just random label noise, but unstable boundary interpretation: wrapper papers, biological-token-only language models, text-conditioned generative models, and truncated abstracts are especially sensitive to model and run variation. "
            "A defensible automated screening workflow should therefore report repeat-run agreement, include-set stability, model-dependence, and the treatment of UNCERTAIN records.",
            "",
        ]
    )
    output_dir.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/cross_agent_screening_agreement"))
    parser.add_argument("--regression-csv", type=Path, default=Path("protocol/screening_prompt_regression_cases.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    cases = clean_strings(pd.read_csv(args.regression_csv))
    runs = load_runs()
    labels = list(runs)
    merged = merge_runs(runs, cases)
    merged.to_csv(output_dir / "cross_model_decisions.csv", index=False)

    pair_order = [
        ("deepseek_rep1", "deepseek_rep2"),
        ("deepseek_rep1", "deepseek_rep3"),
        ("deepseek_rep2", "deepseek_rep3"),
        ("gptoss_rep1", "gptoss_rep2"),
        ("deepseek_rep1", "gptoss_rep1"),
        ("deepseek_rep2", "gptoss_rep2"),
        ("deepseek_rep3", "gptoss_rep1"),
    ]
    pair_summaries = [summarize_pair(merged, a, b) for a, b in pair_order if a in runs and b in runs]
    (output_dir / "pairwise_agreement.json").write_text(json.dumps(pair_summaries, indent=2), encoding="utf-8")

    deepseek_labels = [label for label in labels if label.startswith("deepseek")]
    gpt_labels = [label for label in labels if label.startswith("gptoss")]
    deepseek_consensus = build_consensus(merged, deepseek_labels, "deepseek") if len(deepseek_labels) >= 2 else None
    gpt_consensus = build_consensus(merged, gpt_labels, "gptoss") if len(gpt_labels) >= 2 else None
    if deepseek_consensus is not None:
        deepseek_consensus.to_csv(output_dir / "deepseek_consensus.csv", index=False)
    if gpt_consensus is not None:
        gpt_consensus.to_csv(output_dir / "gptoss_consensus.csv", index=False)
    all_consensus = build_consensus(merged, labels, "all_runs") if len(labels) >= 2 else None
    if all_consensus is not None:
        all_consensus.to_csv(output_dir / "all_run_consensus.csv", index=False)

    boundaries = boundary_counts(merged, labels)
    boundaries.to_csv(output_dir / "boundary_case_counts.csv", index=False)

    unstable = unstable_reasoning_table(merged, labels)
    if not unstable.empty:
        unstable["issue_tags"] = unstable.apply(lambda row: infer_issue_tags(row, labels), axis=1)
    unstable.to_csv(output_dir / "unstable_reasoning_cases.csv", index=False)

    tag_counts = Counter()
    for tags in unstable.get("issue_tags", []):
        for tag in str(tags).split(";"):
            if tag:
                tag_counts[tag] += 1
    pd.DataFrame([{"issue_tag": tag, "count": count} for tag, count in tag_counts.most_common()]).to_csv(
        output_dir / "issue_tag_counts.csv",
        index=False,
    )

    write_markdown(
        output_dir,
        pair_summaries,
        deepseek_consensus,
        gpt_consensus,
        merged,
        unstable,
        {
            "DeepSeek repeats": consensus_summary(deepseek_consensus, "deepseek"),
            "GPT-OSS repeats": consensus_summary(gpt_consensus, "gptoss"),
            "All available runs": consensus_summary(all_consensus, "all_runs"),
        },
    )
    print(f"Wrote cross-agent agreement analysis to {output_dir}")
    for summary in pair_summaries:
        print(
            f"{summary['pair']}: mismatches={summary['decision_mismatches']}/"
            f"{summary['matched_records']} include_jaccard={summary['include_jaccard']:.3f}"
        )


if __name__ == "__main__":
    main()
