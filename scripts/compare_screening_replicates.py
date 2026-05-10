#!/usr/bin/env python3
"""Compare two completed guideline-screening runs for decision stability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


FINAL_DECISION = "pilot_final_decision"
ID_CANDIDATES = ("cluster_id", "doi", "title")


def read_run(path: Path) -> pd.DataFrame:
    if path.is_file():
        return read_table(path)

    preferred = (
        "guideline_pilot_results_all_completed_dedup.csv",
        "guideline_pilot_results_all_completed_dedup.parquet",
        "guideline_pilot_results.csv",
        "guideline_pilot_results_partial.csv",
    )
    for name in preferred:
        candidate = path / name
        if candidate.exists():
            return read_table(candidate)

    parts = []
    for pattern in ("job_*/guideline_pilot_results.csv", "job_*/guideline_pilot_results_partial.csv"):
        parts.extend(read_table(p) for p in sorted(path.glob(pattern)))
    if not parts:
        raise FileNotFoundError(f"No guideline pilot result files found under {path}")

    df = pd.concat(parts, ignore_index=True, sort=False)
    return dedupe_results(df)


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        try:
            return pd.read_parquet(path)
        except ImportError:
            csv_fallback = path.with_suffix(".csv")
            if csv_fallback.exists():
                return pd.read_csv(csv_fallback)
            raise
    if path.suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported input file type: {path}")


def choose_id_column(left: pd.DataFrame, right: pd.DataFrame) -> str:
    for column in ID_CANDIDATES:
        if column in left.columns and column in right.columns:
            return column
    raise ValueError(f"No shared identifier column found. Tried: {', '.join(ID_CANDIDATES)}")


def dedupe_results(df: pd.DataFrame) -> pd.DataFrame:
    id_column = next((column for column in ID_CANDIDATES if column in df.columns), None)
    if id_column is None:
        return df
    if "completed_at" in df.columns:
        df = df.sort_values("completed_at")
    return df.drop_duplicates(subset=[id_column], keep="last")


def add_prefixed_columns(df: pd.DataFrame, prefix: str, id_column: str) -> pd.DataFrame:
    keep = [id_column]
    useful_prefixes = (
        "pilot_",
        "round-A_scope_reviewer_",
        "round-A_architecture_reviewer_",
        "round-B_adjudicator_",
    )
    useful_names = {"title", "abstract", "doi", "year", "source"}
    for column in df.columns:
        if column == id_column:
            continue
        if column in useful_names or column.startswith(useful_prefixes):
            keep.append(column)
    out = df.loc[:, list(dict.fromkeys(keep))].copy()
    rename = {column: f"{prefix}_{column}" for column in out.columns if column != id_column}
    return out.rename(columns=rename)


def include_stats(merged: pd.DataFrame) -> dict[str, float | int]:
    a_include = merged[f"a_{FINAL_DECISION}"].eq("INCLUDE")
    b_include = merged[f"b_{FINAL_DECISION}"].eq("INCLUDE")
    stable = a_include & b_include
    union = a_include | b_include
    return {
        "run_a_include": int(a_include.sum()),
        "run_b_include": int(b_include.sum()),
        "stable_include": int(stable.sum()),
        "run_a_include_changed": int((a_include & ~b_include).sum()),
        "run_b_include_new": int((b_include & ~a_include).sum()),
        "include_union": int(union.sum()),
        "include_jaccard": float(stable.sum() / union.sum()) if union.any() else 1.0,
        "include_union_disagreement_rate": float((union & ~stable).sum() / union.sum()) if union.any() else 0.0,
    }


def write_outputs(merged: pd.DataFrame, output_dir: Path, summary: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    mismatches = merged[merged[f"a_{FINAL_DECISION}"].ne(merged[f"b_{FINAL_DECISION}"])].copy()
    mismatches.to_csv(output_dir / "decision_mismatches.csv", index=False)

    include_unstable = mismatches[
        mismatches[f"a_{FINAL_DECISION}"].eq("INCLUDE") | mismatches[f"b_{FINAL_DECISION}"].eq("INCLUDE")
    ].copy()
    include_unstable.to_csv(output_dir / "include_unstable_cases_with_agent_outputs.csv", index=False)

    with (output_dir / "comparison_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)


def print_summary(summary: dict[str, object], transitions: pd.DataFrame) -> None:
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("\nTransition matrix:")
    print(transitions.to_string())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-a", required=True, type=Path, help="First run directory or result file")
    parser.add_argument("--run-b", required=True, type=Path, help="Second run directory or result file")
    parser.add_argument("--output-dir", type=Path, help="Optional directory for mismatch CSVs and JSON summary")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    left = dedupe_results(read_run(args.run_a))
    right = dedupe_results(read_run(args.run_b))
    id_column = choose_id_column(left, right)
    if FINAL_DECISION not in left.columns or FINAL_DECISION not in right.columns:
        raise ValueError(f"Both runs must contain {FINAL_DECISION}")

    merged = add_prefixed_columns(left, "a", id_column).merge(
        add_prefixed_columns(right, "b", id_column),
        on=id_column,
        how="inner",
        validate="one_to_one",
    )
    transitions = pd.crosstab(merged[f"a_{FINAL_DECISION}"], merged[f"b_{FINAL_DECISION}"], dropna=False)
    mismatches = merged[f"a_{FINAL_DECISION}"].ne(merged[f"b_{FINAL_DECISION}"])
    summary: dict[str, object] = {
        "id_column": id_column,
        "run_a_records": int(len(left)),
        "run_b_records": int(len(right)),
        "matched_records": int(len(merged)),
        "decision_mismatches": int(mismatches.sum()),
        "decision_mismatch_rate": float(mismatches.mean()) if len(merged) else 0.0,
        "run_a_counts": left[FINAL_DECISION].value_counts(dropna=False).to_dict(),
        "run_b_counts": right[FINAL_DECISION].value_counts(dropna=False).to_dict(),
        "include_stats": include_stats(merged),
    }
    print_summary(summary, transitions)
    if args.output_dir:
        write_outputs(merged, args.output_dir, summary)


if __name__ == "__main__":
    main()
