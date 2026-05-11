#!/usr/bin/env bash
#SBATCH -J dsv4-full
#SBATCH -p common
#SBATCH --account=ehpc-aif-2026pg01-346
#SBATCH --qos=ehpc-aif-2026pg01-346
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=256G
#SBATCH --gres=gpu:4
#SBATCH --time=02:00:00
#SBATCH -o /valhalla/projects/ehpc-aif-2026pg01-346/slurm-logs/%x_%j.out
#SBATCH -e /valhalla/projects/ehpc-aif-2026pg01-346/slurm-logs/%x_%j.err

set -euo pipefail

PROJECT=/valhalla/projects/ehpc-aif-2026pg01-346
REPO=$PROJECT/review/text-bio-fundational-models-review
SIF=$PROJECT/containers/vllm-openai-deepseekv4-cu129.sif
OVERLAY=$PROJECT/containers/vllm-openai-deepseekv4-cu129-addons.img
MODEL=$PROJECT/models/deepseek-v4-flash-lfs
SERVED_MODEL=deepseek-v4-flash
INPUT_CSV="${INPUT_CSV:-$REPO/runs/all_abstracts_input_4027.csv}"
RUN_LABEL="${RUN_LABEL:-deepseek_v4_review_pipeline_all4027_current_watchdog_${SLURM_JOB_ID}}"
MAX_CONCURRENT="${MAX_CONCURRENT:-72}"
MAX_TOKENS="${MAX_TOKENS:-16000}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-1800}"
SEED="${SEED:-0}"
PIPELINE_SECONDS="${PIPELINE_SECONDS:-6600}"
MAX_CHAIN_JOBS="${MAX_CHAIN_JOBS:-16}"
AUTO_RESUBMIT="${AUTO_RESUBMIT:-1}"
PYTHON_BIN="${PYTHON_BIN:-$REPO/.review-venv/bin/python}"
RUN_ROOT=$REPO/runs/$RUN_LABEL
RUN_DIR=$RUN_ROOT/job_$SLURM_JOB_ID
RUN_TMP=/tmp/dsv4_full_${SLURM_JOB_ID}
PORT=8000

mkdir -p "$RUN_ROOT" "$RUN_DIR" "$RUN_TMP/triton" "$RUN_TMP/cache" "$PROJECT/slurm-logs"
chmod 700 "$RUN_TMP"

APPTAINER_BASE=(apptainer exec --nv --overlay "${OVERLAY}:ro" --bind "$PROJECT:$PROJECT" "$SIF")
COMMON_ENV="export TMPDIR='$RUN_TMP'; export TRITON_HOME='$RUN_TMP/triton_home'; export TRITON_CACHE_DIR='$RUN_TMP/triton'; export XDG_CACHE_HOME='$RUN_TMP/cache'; export VLLM_WORKER_MULTIPROC_METHOD=spawn; export PYTHONUNBUFFERED=1; export VLLM_MXFP4_USE_MARLIN=0; export TILELANG_CLEANUP_TEMP_FILES=1; export VLLM_DISABLE_COMPILE_CACHE=1; export VLLM_ENGINE_READY_TIMEOUT_S=3600; export VLLM_RPC_TIMEOUT=600000; export VLLM_LOG_STATS_INTERVAL=1;"

log() { echo "[$(date -u '+%F %T UTC')] $*"; }

cleanup() {
  log "cleanup"
  if [ -n "${SERVER_PID:-}" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -rf "$RUN_TMP" 2>/dev/null || true
}
trap cleanup EXIT

write_remaining_and_summary() {
  "$PYTHON_BIN" - <<'PY' "$INPUT_CSV" "$RUN_ROOT" "$RUN_DIR/remaining_input.csv"
import json
import sys
from pathlib import Path

import pandas as pd

input_csv = Path(sys.argv[1])
run_root = Path(sys.argv[2])
remaining_csv = Path(sys.argv[3])

source = pd.read_csv(input_csv)
if "cluster_id" not in source.columns:
    raise SystemExit("Input CSV must contain cluster_id")

parts = []
read_errors = {}
for path in sorted(run_root.glob("job_*/guideline_pilot_results.csv")):
    try:
        parts.append(pd.read_csv(path))
    except Exception as exc:
        read_errors[str(path)] = str(exc)
for path in sorted(run_root.glob("job_*/guideline_pilot_results_partial.csv")):
    if path.with_name("guideline_pilot_results.csv").exists():
        continue
    try:
        parts.append(pd.read_csv(path))
    except Exception as exc:
        read_errors[str(path)] = str(exc)

if parts:
    completed = pd.concat(parts, ignore_index=True, sort=False)
    if "completed_at" in completed.columns:
        completed = completed.sort_values("completed_at")
    completed = completed.drop_duplicates(subset=["cluster_id"], keep="last")
else:
    completed = pd.DataFrame(columns=["cluster_id"])

completed_ids = set(completed["cluster_id"].dropna()) if "cluster_id" in completed.columns else set()
remaining = source[~source["cluster_id"].isin(completed_ids)].copy()
remaining.to_csv(remaining_csv, index=False)

if not completed.empty:
    completed.to_csv(run_root / "guideline_pilot_results_all_completed_dedup.csv", index=False)
    try:
        completed.to_parquet(run_root / "guideline_pilot_results_all_completed_dedup.parquet", index=False)
    except Exception as exc:
        (run_root / "parquet_write.err").write_text(str(exc), encoding="utf-8")

summary = {
    "input_records": int(len(source)),
    "completed_records": int(len(completed)),
    "remaining_records": int(len(remaining)),
    "completed_unique_cluster_ids": int(len(completed_ids)),
}
if "pilot_final_decision" in completed.columns:
    summary["decision_counts"] = completed["pilot_final_decision"].value_counts(dropna=False).to_dict()
if read_errors:
    summary["read_errors"] = read_errors
(run_root / "watchdog_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
print(json.dumps(summary, sort_keys=True))
PY
}

cat >"$RUN_DIR/server_info.env" <<EOF
SLURM_JOB_ID=$SLURM_JOB_ID
NODE_NAME=$(hostname)
PORT=$PORT
BASE_URL=http://$(hostname):$PORT/v1
LOCAL_BASE_URL=http://127.0.0.1:$PORT/v1
MODEL_NAME=$MODEL
SERVED_MODEL_NAME=$SERVED_MODEL
SEED=$SEED
RUN_DIR=$RUN_DIR
RUN_ROOT=$RUN_ROOT
INPUT_CSV=$INPUT_CSV
MAX_CONCURRENT=$MAX_CONCURRENT
MAX_TOKENS=$MAX_TOKENS
REQUEST_TIMEOUT=$REQUEST_TIMEOUT
PIPELINE_SECONDS=$PIPELINE_SECONDS
AUTO_RESUBMIT=$AUTO_RESUBMIT
MAX_CHAIN_JOBS=$MAX_CHAIN_JOBS
EOF

log "preparing remaining input"
write_remaining_and_summary | tee "$RUN_DIR/pre_run_watchdog_summary.json"
REMAINING_COUNT=$("$PYTHON_BIN" - <<'PY' "$RUN_DIR/remaining_input.csv"
import sys
import pandas as pd
print(len(pd.read_csv(sys.argv[1])))
PY
)
log "remaining records: $REMAINING_COUNT"

if [ "$REMAINING_COUNT" -eq 0 ]; then
  log "run already complete"
  exit 0
fi

log "context"
hostname
nvidia-smi -L
nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader,nounits || true
echo "SLURM_JOB_GPUS=${SLURM_JOB_GPUS:-}"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-}"
echo "RUN_ROOT=$RUN_ROOT"
echo "RUN_DIR=$RUN_DIR"
echo "INPUT_CSV=$INPUT_CSV"
echo "MAX_CONCURRENT=$MAX_CONCURRENT"
echo "MAX_TOKENS=$MAX_TOKENS"

log "container checks"
"${APPTAINER_BASE[@]}" bash -lc "$COMMON_ENV python3 - <<'PY'
import importlib.util, torch
print('torch', torch.__version__, torch.cuda.is_available(), torch.version.cuda)
print('gpu_count', torch.cuda.device_count())
for m in ['vllm', 'deep_gemm', 'triton_kernels.matmul_ogs', 'triton_kernels.swiglu']:
    spec = importlib.util.find_spec(m)
    print(m, bool(spec), spec.origin if spec else '')
PY
command -v vllm"

log "starting DeepSeek V4 Flash vLLM server"
"${APPTAINER_BASE[@]}" bash -lc "$COMMON_ENV export CUDA_VISIBLE_DEVICES=0,1,2,3; exec vllm serve '$MODEL' \
  --trust-remote-code \
  --served-model-name '$SERVED_MODEL' \
  --seed '$SEED' \
  --kv-cache-dtype fp8 \
  --block-size 256 \
  --host 0.0.0.0 \
  --port '$PORT' \
  --data-parallel-size 4 \
  --enable-expert-parallel \
  --moe-backend triton_unfused \
  --tokenizer-mode deepseek_v4 \
  --reasoning-parser deepseek_v4 \
  --speculative-config '{\"method\":\"deepseek_mtp\",\"num_speculative_tokens\":1}' \
  --max-model-len 32768 \
  --max-num-batched-tokens 32768 \
  --max-num-seqs 4 \
  --enforce-eager \
  --no-disable-hybrid-kv-cache-manager \
  --disable-uvicorn-access-log" >"$RUN_DIR/server.log" 2>&1 &
SERVER_PID=$!

log "waiting for readiness"
READY=0
for i in $(seq 1 360); do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    log "server exited early"
    tail -240 "$RUN_DIR/server.log" || true
    exit 1
  fi
  if curl -fsS --max-time 5 "http://127.0.0.1:$PORT/v1/models" >"$RUN_DIR/models.json" 2>"$RUN_DIR/models.err"; then
    READY=1
    break
  fi
  if (( i % 12 == 0 )); then
    log "still loading after $((i*10))s"
    nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits || true
    tail -80 "$RUN_DIR/server.log" || true
  fi
  sleep 10
done

if [ "$READY" != 1 ]; then
  log "server did not become ready"
  tail -240 "$RUN_DIR/server.log" || true
  exit 1
fi

log "server ready"
cat "$RUN_DIR/models.json" || true

log "API check"
curl -fsS "http://127.0.0.1:$PORT/v1/chat/completions" \
  --max-time 180 \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Return exactly this JSON object: {\"ok\": true}"}],"max_tokens":256,"temperature":0,"response_format":{"type":"json_object"},"chat_template_kwargs":{"thinking":true,"reasoning_effort":"high"}}' \
  >"$RUN_DIR/api_check.json"

cd "$REPO"
log "starting pipeline for current remaining batch"
set +e
timeout --signal=TERM --kill-after=120s "$PIPELINE_SECONDS" \
  "$PYTHON_BIN" scripts/run_lattereview_guideline_pilot.py \
    --base-url "http://127.0.0.1:$PORT/v1" \
    --model "$SERVED_MODEL" \
    --input-csv "$RUN_DIR/remaining_input.csv" \
    --output-dir "$RUN_DIR" \
    --max-records 0 \
    --max-concurrent "$MAX_CONCURRENT" \
    --timeout "$REQUEST_TIMEOUT" \
    --max-tokens "$MAX_TOKENS" \
    --enable-thinking \
    --reasoning-effort high \
    --pipeline-mode streaming \
    >"$RUN_DIR/runner.log" 2>&1
PIPELINE_STATUS=$?
set -e
log "pipeline exited with status $PIPELINE_STATUS"

log "consolidating progress"
write_remaining_and_summary | tee "$RUN_DIR/post_run_watchdog_summary.json"
TOTAL_REMAINING=$("$PYTHON_BIN" - <<'PY' "$RUN_ROOT/watchdog_summary.json"
import json, sys
print(json.load(open(sys.argv[1]))["remaining_records"])
PY
)
CHAIN_JOBS=$(find "$RUN_ROOT" -maxdepth 1 -type d -name 'job_*' | wc -l)
log "remaining after consolidation: $TOTAL_REMAINING; chain jobs so far: $CHAIN_JOBS"

if [ "$TOTAL_REMAINING" -gt 0 ] && [ "$AUTO_RESUBMIT" = 1 ] && [ "$CHAIN_JOBS" -lt "$MAX_CHAIN_JOBS" ]; then
  log "submitting continuation job"
  SUBMIT_ARGS=(--dependency=afterany:"$SLURM_JOB_ID" --export=ALL,RUN_LABEL="$RUN_LABEL",INPUT_CSV="$INPUT_CSV",MAX_CONCURRENT="$MAX_CONCURRENT",MAX_TOKENS="$MAX_TOKENS",REQUEST_TIMEOUT="$REQUEST_TIMEOUT",SEED="$SEED",PIPELINE_SECONDS="$PIPELINE_SECONDS",MAX_CHAIN_JOBS="$MAX_CHAIN_JOBS",AUTO_RESUBMIT="$AUTO_RESUBMIT",PYTHON_BIN="$PYTHON_BIN")
  if [ -n "${TARGET_NODE:-}" ]; then
    SUBMIT_ARGS+=(--nodelist="$TARGET_NODE")
  fi
  sbatch "${SUBMIT_ARGS[@]}" "$REPO/scripts/submit_deepseek_v4_full_watchdog.sbatch" | tee "$RUN_DIR/continuation_job.txt"
else
  log "no continuation submitted"
fi

log "done"
