#!/usr/bin/env python3
"""Summarize decision agreement across repeated regression screening runs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from compare_screening_replicates import FINAL_DECISION, choose_id_column, dedupe_results, read_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", required=True, type=Path, help="Run directories or result files")
    parser.add_argument("--labels", nargs="+", help="Optional labels matching --runs")
    parser.add_argument("--regression-csv", type=Path, default=Path("protocol/screening_prompt_regression_cases.csv"))
    parser.add_argument("--output-dir", type=Path, help="Optional output directory for consensus CSVs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    labels = args.labels or [f"run_{i + 1}" for i in range(len(args.runs))]
    if len(labels) != len(args.runs):
        raise ValueError("--labels length must match --runs length")

    frames = [dedupe_results(read_run(path)) for path in args.runs]
    id_column = frames[0].columns[0]
    for frame in frames[1:]:
        id_column = choose_id_column(frames[0], frame)
        break
    cases = pd.read_csv(args.regression_csv)
    if id_column not in cases.columns:
        id_column = choose_id_column(cases, frames[0])

    out = cases[[id_column, "title", "regression_group"]].copy()
    for label, frame in zip(labels, frames):
        keep = frame[[id_column, FINAL_DECISION]].copy()
        keep = keep.rename(columns={FINAL_DECISION: label})
        out = out.merge(keep, on=id_column, how="left")

    decision_cols = labels
    out["decision_set"] = out[decision_cols].astype(str).agg("|".join, axis=1)
    out["stable"] = out[decision_cols].nunique(axis=1, dropna=False).eq(1)
    out["include_any"] = out[decision_cols].eq("INCLUDE").any(axis=1)
    out["include_all"] = out[decision_cols].eq("INCLUDE").all(axis=1)
    out["uncertain_any"] = out[decision_cols].eq("UNCERTAIN").any(axis=1)

    print(f"records={len(out)} runs={len(labels)}")
    print(f"stable={int(out['stable'].sum())}/{len(out)} = {out['stable'].mean():.3f}")
    print(f"unstable={int((~out['stable']).sum())}/{len(out)} = {(~out['stable']).mean():.3f}")
    print(f"include_all={int(out['include_all'].sum())}")
    print(f"include_any={int(out['include_any'].sum())}")
    print("\nDecision counts per run:")
    for label in labels:
        print(f"\n{label}")
        print(out[label].value_counts(dropna=False).to_string())
    print("\nStable by regression group:")
    print(out.groupby("regression_group")["stable"].agg(["sum", "count", "mean"]).to_string())
    print("\nUnstable cases:")
    unstable_cols = [id_column, "title", "regression_group", *decision_cols, "decision_set"]
    print(out.loc[~out["stable"], unstable_cols].to_csv(index=False))

    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        out.to_csv(args.output_dir / "repeat_consensus.csv", index=False)
        out.loc[out["stable"]].to_csv(args.output_dir / "stable_cases.csv", index=False)
        out.loc[~out["stable"]].to_csv(args.output_dir / "unstable_cases.csv", index=False)


if __name__ == "__main__":
    main()
