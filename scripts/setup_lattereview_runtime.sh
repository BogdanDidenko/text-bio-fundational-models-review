#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${1:-$ROOT/external/LatteReview}"

echo "Repo root: $ROOT"
echo "LatteReview target: $TARGET_DIR"

mkdir -p "$(dirname "$TARGET_DIR")"

if [[ -d "$TARGET_DIR/.git" ]]; then
  echo "LatteReview clone already exists at $TARGET_DIR"
else
  git clone https://github.com/PouriaRouzrokh/LatteReview.git "$TARGET_DIR"
fi

python3 -m pip install -r "$ROOT/scripts/requirements_lattereview_pilot.txt"

echo
echo "LatteReview runtime setup complete."
echo "Clone path: $TARGET_DIR"
echo
echo "Next step:"
echo "  python3 $ROOT/scripts/run_lattereview_guideline_pilot.py --model <served-model-name> --input-csv <input.csv> --output-dir <out-dir>"
