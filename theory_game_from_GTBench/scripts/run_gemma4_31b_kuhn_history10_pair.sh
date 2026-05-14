#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

GAME="${GAME:-kuhn_poker_history10}"
NUM_MATCHES="${NUM_MATCHES:-100}"
NUM_WORKERS="${NUM_WORKERS:-1}"
THRESHOLD_MATCHES="${THRESHOLD_MATCHES:-100}"
SEED="${SEED:-0}"

REASONING_EXP_ROOT="${REASONING_EXP_ROOT:-experiments/gemma4_31b_high_reasoning_vs_baseline_onegame_no_think_history10/${GAME}}"
DISTILL_EXP_ROOT="${DISTILL_EXP_ROOT:-experiments/gemma4_31b_high_distill_vs_baseline_onegame_no_think_history10/${GAME}}"

echo "[pair] starting high reasoning on ${GAME} via 11436"
GAME="${GAME}" \
NUM_MATCHES="${NUM_MATCHES}" \
NUM_WORKERS="${NUM_WORKERS}" \
THRESHOLD_MATCHES="${THRESHOLD_MATCHES}" \
SEED="${SEED}" \
EXP_ROOT="${REASONING_EXP_ROOT}" \
OLLAMA_BASE_URL="http://127.0.0.1:11436" \
bash scripts/run_gemma4_31b_high_reasoning_vs_baseline_onegame_no_think.sh

echo "[pair] starting high distill on ${GAME} via 11437"
GAME="${GAME}" \
NUM_MATCHES="${NUM_MATCHES}" \
NUM_WORKERS="${NUM_WORKERS}" \
THRESHOLD_MATCHES="${THRESHOLD_MATCHES}" \
SEED="${SEED}" \
EXP_ROOT="${DISTILL_EXP_ROOT}" \
OLLAMA_BASE_URL="http://127.0.0.1:11437" \
bash scripts/run_gemma4_31b_high_distill_vs_baseline_onegame_no_think.sh
