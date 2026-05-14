#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

BASE_EXP_ROOT="${BASE_EXP_ROOT:-experiments/qwen3_14b_kuhn_groups_vs_baseline_onegame_no_think_distill_11437}"
NUM_MATCHES="${NUM_MATCHES:-100}"
NUM_WORKERS="${NUM_WORKERS:-1}"
THRESHOLD_MATCHES="${THRESHOLD_MATCHES:-100}"
SEED="${SEED:-0}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11437}"
OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"

for i in $(seq -w 1 10); do
  GROUP="kuhn_group_${i}"
  GROUP_TAG="g${i}"
  EXP_ROOT="${BASE_EXP_ROOT}/${GROUP_TAG}/kuhn_poker"

  if find "${EXP_ROOT}" -name '*.jsonl' -print -quit | grep -q .; then
    echo "[skip] ${GROUP} already has results under ${EXP_ROOT}"
    continue
  fi

  echo "[run] ${GROUP} -> ${EXP_ROOT}"
  GAME="kuhn_poker" \
  ENGINEERING_PROFILE="${GROUP}" \
  ENGINEERING_PROFILE_MODE="distill" \
  PROFILE_TAG="${GROUP_TAG}" \
  NUM_MATCHES="${NUM_MATCHES}" \
  NUM_WORKERS="${NUM_WORKERS}" \
  THRESHOLD_MATCHES="${THRESHOLD_MATCHES}" \
  SEED="${SEED}" \
  EXP_ROOT="${EXP_ROOT}" \
  OLLAMA_BASE_URL="${OLLAMA_BASE_URL}" \
  OLLAMA_API_KEY="${OLLAMA_API_KEY}" \
    bash scripts/run_qwen3_14b_custom_profile_vs_baseline_onegame_no_think.sh
done
