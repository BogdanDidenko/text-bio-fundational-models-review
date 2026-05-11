#!/usr/bin/env bash
#SBATCH -J dsv4-reg116
#SBATCH -p common
#SBATCH --account=ehpc-aif-2026pg01-346
#SBATCH --qos=ehpc-aif-2026pg01-346
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=600G
#SBATCH --gres=gpu:4
#SBATCH --nodelist=dgx1
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
INPUT_CSV="${INPUT_CSV:-$REPO/protocol/screening_prompt_regression_cases.csv}"
RUN_LABEL="${RUN_LABEL:-prompt_regression_116_deepseek_v4_repeats_${SLURM_JOB_ID}}"
REPEATS="${REPEATS:-3}"
MAX_CONCURRENT="${MAX_CONCURRENT:-12}"
MAX_TOKENS="${MAX_TOKENS:-4000}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-900}"
SEED="${SEED:-0}"
PYTHON_BIN="${PYTHON_BIN:-$REPO/.review-venv/bin/python}"
RUN_ROOT=$REPO/runs/$RUN_LABEL
RUN_TMP=/tmp/dsv4_reg116_${SLURM_JOB_ID}
PORT=8000

mkdir -p "$RUN_ROOT" "$RUN_TMP/triton" "$RUN_TMP/cache" "$PROJECT/slurm-logs"
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

cat >"$RUN_ROOT/server_info.env" <<EOF
SLURM_JOB_ID=$SLURM_JOB_ID
NODE_NAME=$(hostname)
PORT=$PORT
BASE_URL=http://$(hostname):$PORT/v1
LOCAL_BASE_URL=http://127.0.0.1:$PORT/v1
MODEL_NAME=$MODEL
SERVED_MODEL_NAME=$SERVED_MODEL
SEED=$SEED
RUN_ROOT=$RUN_ROOT
INPUT_CSV=$INPUT_CSV
REPEATS=$REPEATS
MAX_CONCURRENT=$MAX_CONCURRENT
MAX_TOKENS=$MAX_TOKENS
REQUEST_TIMEOUT=$REQUEST_TIMEOUT
EOF

log "context"
hostname
nvidia-smi -L
nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader,nounits || true
echo "SLURM_JOB_GPUS=${SLURM_JOB_GPUS:-}"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-}"
echo "INPUT_CSV=$INPUT_CSV"
echo "RUN_ROOT=$RUN_ROOT"
echo "REPEATS=$REPEATS"
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
  --disable-uvicorn-access-log" >"$RUN_ROOT/server.log" 2>&1 &
SERVER_PID=$!

log "waiting for readiness"
READY=0
for i in $(seq 1 360); do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    log "server exited early"
    tail -240 "$RUN_ROOT/server.log" || true
    exit 1
  fi
  if curl -fsS --max-time 5 "http://127.0.0.1:$PORT/v1/models" >"$RUN_ROOT/models.json" 2>"$RUN_ROOT/models.err"; then
    READY=1
    break
  fi
  if (( i % 12 == 0 )); then
    log "still loading after $((i*10))s"
    nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits || true
    tail -80 "$RUN_ROOT/server.log" || true
  fi
  sleep 10
done

if [ "$READY" != 1 ]; then
  log "server did not become ready"
  tail -240 "$RUN_ROOT/server.log" || true
  exit 1
fi

log "server ready"
cat "$RUN_ROOT/models.json" || true

log "API check"
curl -fsS "http://127.0.0.1:$PORT/v1/chat/completions" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Return exactly this JSON object: {\"ok\": true}"}],"max_tokens":256,"temperature":0,"response_format":{"type":"json_object"},"chat_template_kwargs":{"thinking":true,"reasoning_effort":"high"}}' \
  >"$RUN_ROOT/api_check.json"

cd "$REPO"
for repeat in $(seq 1 "$REPEATS"); do
  RUN_DIR="$RUN_ROOT/repeat_${repeat}"
  mkdir -p "$RUN_DIR"
  log "starting repeat $repeat/$REPEATS"
  PYTHONPATH=. "$PYTHON_BIN" scripts/run_lattereview_guideline_pilot.py \
    --base-url "http://127.0.0.1:$PORT/v1" \
    --model "$SERVED_MODEL" \
    --input-csv "$INPUT_CSV" \
    --output-dir "$RUN_DIR" \
    --max-records 0 \
    --max-concurrent "$MAX_CONCURRENT" \
    --timeout "$REQUEST_TIMEOUT" \
    --max-tokens "$MAX_TOKENS" \
    --enable-thinking \
    --reasoning-effort high \
    --pipeline-mode streaming \
    >"$RUN_DIR/runner.log" 2>&1
  log "repeat $repeat complete"
  "$PYTHON_BIN" scripts/analyze_prompt_regression_run.py \
    --run "$RUN_DIR" \
    --regression-csv "$INPUT_CSV" \
    >"$RUN_DIR/regression_analysis.txt" 2>&1 || true
  cat "$RUN_DIR/regression_analysis.txt" || true
done

log "all repeats complete"
