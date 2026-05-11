#!/usr/bin/env python3
"""Summarize a prompt-regression screening run against its case groups."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from compare_screening_replicates import FINAL_DECISION, read_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--regression-csv", type=Path, default=Path("protocol/screening_prompt_regression_cases.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run = read_run(args.run)
    cases = pd.read_csv(args.regression_csv)
    id_col = "cluster_id" if "cluster_id" in run.columns and "cluster_id" in cases.columns else "title"
    merged = cases.merge(run, on=id_col, how="left", suffixes=("_case", ""))

    print(f"records={len(merged)} completed={merged[FINAL_DECISION].notna().sum()}")
    print("\nDecision counts:")
    print(merged[FINAL_DECISION].value_counts(dropna=False).to_string())

    print("\nDecision counts by regression group:")
    grouped = pd.crosstab(merged["regression_group"], merged[FINAL_DECISION].fillna("MISSING"), dropna=False)
    print(grouped.to_string())

    if "decision_run_a" in merged.columns and "decision_run_b" in merged.columns:
        include_unstable = merged["regression_group"].eq("include_decision_unstable")
        stable_include = merged["regression_group"].eq("stable_include")
        benchmark = merged["regression_group"].eq("benchmark_boundary_case")
        print("\nHigh-signal group rates:")
        for label, mask in (
            ("stable_include_included", stable_include),
            ("unstable_include_included", include_unstable),
            ("benchmark_boundary_included", benchmark),
        ):
            denom = int(mask.sum())
            rate = float(merged.loc[mask, FINAL_DECISION].eq("INCLUDE").mean()) if denom else 0.0
            print(f"{label}: {int(merged.loc[mask, FINAL_DECISION].eq('INCLUDE').sum())}/{denom} = {rate:.3f}")

    boundary_col = "pilot_selected_boundary_case"
    if boundary_col in merged.columns:
        print("\nBoundary labels:")
        print(merged[boundary_col].fillna("MISSING").value_counts().head(20).to_string())


if __name__ == "__main__":
    main()
