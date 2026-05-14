#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

GAME_NAMES="${GAME_NAMES:-tictactoe connect4 breakthrough first_sealed_auction liars_dice negotiation nim pig kuhn_poker prisoners_dilemma}"
NUM_MATCHES="${NUM_MATCHES:-100}"
NUM_WORKERS="${NUM_WORKERS:-1}"
THRESHOLD_MATCHES="${THRESHOLD_MATCHES:-100}"
SEED="${SEED:-0}"
EXP_ROOT="${EXP_ROOT:-experiments/gemma4_31b_high_reasoning_vs_high_distill_no_think_allgames_gpu01}"
PYTHONPATH="${PYTHONPATH:-${REPO_ROOT}}"
OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"

REASONING_MODEL_CONFIG="${REASONING_MODEL_CONFIG:-gamingbench/configs/model_configs/gemma4-31b-ollama-no-think-shared-reasoning.yaml}"
DISTILL_MODEL_CONFIG="${DISTILL_MODEL_CONFIG:-gamingbench/configs/model_configs/gemma4-31b-ollama-no-think-shared-distill.yaml}"
REASONING_AGENT_CONFIG="${REASONING_AGENT_CONFIG:-gamingbench/configs/agent_configs/theory_interaction_field_agent_high_engineering.yaml}"
DISTILL_AGENT_CONFIG="${DISTILL_AGENT_CONFIG:-gamingbench/configs/agent_configs/theory_interaction_field_agent_high_engineering_distill.yaml}"

read -r -a GAME_NAME_ARGS <<< "${GAME_NAMES}"

export PYTHONPATH
export OLLAMA_API_KEY

python -m gamingbench.main \
  --num-matches "${NUM_MATCHES}" \
  --exp-root "${EXP_ROOT}" \
  --seed "${SEED}" \
  --game-names "${GAME_NAME_ARGS[@]}" \
  --agent-configs \
    "${REASONING_AGENT_CONFIG}" \
    "${DISTILL_AGENT_CONFIG}" \
  --model-configs \
    "${REASONING_MODEL_CONFIG}" \
    "${DISTILL_MODEL_CONFIG}" \
  --exchange-first-player \
  --num-workers "${NUM_WORKERS}" \
  --threshold-matches "${THRESHOLD_MATCHES}"
