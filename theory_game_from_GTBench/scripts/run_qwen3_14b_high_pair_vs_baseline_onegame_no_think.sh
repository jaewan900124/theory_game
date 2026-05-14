#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

GAME="${GAME:-nim}"
NUM_MATCHES="${NUM_MATCHES:-100}"
NUM_WORKERS="${NUM_WORKERS:-1}"
THRESHOLD_MATCHES="${THRESHOLD_MATCHES:-100}"
SEED="${SEED:-0}"
BASE_EXP_ROOT="${BASE_EXP_ROOT:-experiments/qwen3_14b_high_pair_vs_baseline_onegame_no_think}"

export GAME
export NUM_MATCHES
export NUM_WORKERS
export THRESHOLD_MATCHES
export SEED

EXP_ROOT="${BASE_EXP_ROOT}/high_reasoning/${GAME}" \
  bash scripts/run_qwen3_14b_high_reasoning_vs_baseline_onegame_no_think.sh

EXP_ROOT="${BASE_EXP_ROOT}/high_distill/${GAME}" \
  bash scripts/run_qwen3_14b_high_distill_vs_baseline_onegame_no_think.sh
