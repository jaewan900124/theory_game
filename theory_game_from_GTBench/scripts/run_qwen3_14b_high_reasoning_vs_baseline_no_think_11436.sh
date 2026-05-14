#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

NUM_MATCHES="${NUM_MATCHES:-10}"
NUM_WORKERS="${NUM_WORKERS:-1}"
THRESHOLD_MATCHES="${THRESHOLD_MATCHES:-10}"
SEED="${SEED:-0}"
EXP_ROOT="${EXP_ROOT:-experiments/qwen3_14b_high_reasoning_vs_baseline_allgames_10_no_think_11436}"
PYTHONPATH="${PYTHONPATH:-${REPO_ROOT}}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11436}"
OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"

MODEL_CONFIG="gamingbench/configs/model_configs/qwen3-14b-ollama-no-think.yaml"
THEORY_AGENT_CONFIG="gamingbench/configs/agent_configs/theory_interaction_field_agent_high_engineering.yaml"
BASELINE_AGENT_CONFIG="gamingbench/configs/agent_configs/prompt_agent.yaml"

GAMES=(
  tictactoe
  connect4
  breakthrough
  nim
  pig
  kuhn_poker
  negotiation
  prisoners_dilemma
  first_sealed_auction
  liars_dice
)

export PYTHONPATH
export OLLAMA_BASE_URL
export OLLAMA_API_KEY

python -m gamingbench.main \
  --num-matches "${NUM_MATCHES}" \
  --exp-root "${EXP_ROOT}" \
  --seed "${SEED}" \
  --game-names "${GAMES[@]}" \
  --agent-configs \
    "${THEORY_AGENT_CONFIG}" \
    "${BASELINE_AGENT_CONFIG}" \
  --model-configs \
    "${MODEL_CONFIG}" \
    "${MODEL_CONFIG}" \
  --exchange-first-player \
  --num-workers "${NUM_WORKERS}" \
  --threshold-matches "${THRESHOLD_MATCHES}"
