#!/usr/bin/env python3
"""Build a compact prompt-regression set from replicate screening runs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from compare_screening_replicates import FINAL_DECISION, choose_id_column, dedupe_results, read_run


DEFAULT_OUTPUT = Path("protocol/screening_prompt_regression_cases.csv")


def clean_text(value: object) -> object:
    if not isinstance(value, str):
        return value
    return "\n".join(line.rstrip() for line in value.splitlines()).strip()


def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for column in out.select_dtypes(include=["object"]).columns:
        out[column] = out[column].map(clean_text)
    return out


def first_present(df: pd.DataFrame, names: list[str]) -> pd.Series:
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series([""] * len(df), index=df.index)


def make_case_frame(df: pd.DataFrame, id_column: str, group: str, limit: int | None = None) -> pd.DataFrame:
    out = pd.DataFrame(
        {
            id_column: df[id_column],
            "title": first_present(df, ["a_title", "b_title", "title"]),
            "abstract": first_present(df, ["a_abstract", "b_abstract", "abstract"]),
            "regression_group": group,
            "decision_run_a": first_present(df, [f"a_{FINAL_DECISION}", FINAL_DECISION]),
            "decision_run_b": first_present(df, [f"b_{FINAL_DECISION}"]),
            "scope_boundary_run_a": first_present(df, ["a_pilot_selected_boundary_case"]),
            "scope_boundary_run_b": first_present(df, ["b_pilot_selected_boundary_case"]),
            "rationale_run_a": first_present(df, ["a_pilot_decision_rationale", "a_pilot_selected_decision_rationale"]),
            "rationale_run_b": first_present(df, ["b_pilot_decision_rationale", "b_pilot_selected_decision_rationale"]),
        }
    )
    out = out.dropna(subset=["title", "abstract"], how="all")
    if limit is not None:
        out = out.head(limit)
    return out


def load_mismatches(compare_dir: Path, run_a: Path, run_b: Path) -> pd.DataFrame:
    mismatch_file = compare_dir / "decision_mismatches.csv"
    if mismatch_file.exists():
        return pd.read_csv(mismatch_file)

    left = dedupe_results(read_run(run_a))
    right = dedupe_results(read_run(run_b))
    id_column = choose_id_column(left, right)
    left = left.add_prefix("a_").rename(columns={f"a_{id_column}": id_column})
    right = right.add_prefix("b_").rename(columns={f"b_{id_column}": id_column})
    merged = left.merge(right, on=id_column, how="inner", validate="one_to_one")
    return merged[merged[f"a_{FINAL_DECISION}"].ne(merged[f"b_{FINAL_DECISION}"])].copy()


def add_benchmark_cases(path: Path | None, id_column: str) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if id_column not in df.columns:
        df[id_column] = "benchmark:" + df.index.astype(str)
    out = pd.DataFrame(
        {
            id_column: df[id_column],
            "title": first_present(df, ["title"]),
            "abstract": first_present(df, ["abstract"]),
            "regression_group": "benchmark_boundary_case",
            "decision_run_a": "",
            "decision_run_b": "",
            "scope_boundary_run_a": "",
            "scope_boundary_run_b": "",
            "rationale_run_a": "",
            "rationale_run_b": "",
        }
    )
    return clean_strings(out.dropna(subset=["title", "abstract"], how="all"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-a", required=True, type=Path)
    parser.add_argument("--run-b", required=True, type=Path)
    parser.add_argument("--compare-dir", type=Path, help="Directory containing decision_mismatches.csv")
    parser.add_argument("--benchmark-csv", type=Path, default=Path("runs/benchmark_boundary_subset_p1p2_input.csv"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--exclude-uncertain-sample", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    compare_dir = args.compare_dir or args.run_b
    mismatches = load_mismatches(compare_dir, args.run_a, args.run_b)
    run_a = dedupe_results(read_run(args.run_a))
    run_b = dedupe_results(read_run(args.run_b))
    id_column = choose_id_column(run_a, run_b)

    include_unstable = mismatches[
        mismatches[f"a_{FINAL_DECISION}"].eq("INCLUDE") | mismatches[f"b_{FINAL_DECISION}"].eq("INCLUDE")
    ].copy()
    exclude_uncertain = mismatches[
        ~mismatches[f"a_{FINAL_DECISION}"].eq("INCLUDE") & ~mismatches[f"b_{FINAL_DECISION}"].eq("INCLUDE")
    ].copy()

    stable_include_ids = set(run_a.loc[run_a[FINAL_DECISION].eq("INCLUDE"), id_column]) & set(
        run_b.loc[run_b[FINAL_DECISION].eq("INCLUDE"), id_column]
    )
    stable_include = run_a[run_a[id_column].isin(stable_include_ids)].copy()

    frames = [
        make_case_frame(include_unstable, id_column, "include_decision_unstable"),
        make_case_frame(stable_include, id_column, "stable_include"),
        make_case_frame(exclude_uncertain, id_column, "exclude_uncertain_unstable", args.exclude_uncertain_sample),
        add_benchmark_cases(args.benchmark_csv, id_column),
    ]
    regression = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True, sort=False)
    regression = regression.drop_duplicates(subset=[id_column, "title", "abstract", "regression_group"], keep="first")
    regression = regression.sort_values(["regression_group", "title"], na_position="last")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    clean_strings(regression).to_csv(args.output, index=False)
    print(f"Wrote {len(regression)} regression cases to {args.output}")
    print(regression["regression_group"].value_counts().to_string())


if __name__ == "__main__":
    main()
