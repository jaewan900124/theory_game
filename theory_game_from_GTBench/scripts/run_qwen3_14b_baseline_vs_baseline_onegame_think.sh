#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

GAME="${GAME:-kuhn_poker}"
NUM_MATCHES="${NUM_MATCHES:-100}"
NUM_WORKERS="${NUM_WORKERS:-1}"
THRESHOLD_MATCHES="${THRESHOLD_MATCHES:-100}"
SEED="${SEED:-0}"
EXP_ROOT="${EXP_ROOT:-experiments/qwen3_14b_baseline_vs_baseline_onegame_think/${GAME}}"
PYTHONPATH="${PYTHONPATH:-${REPO_ROOT}}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11436}"
OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"

export PYTHONPATH
export OLLAMA_BASE_URL
export OLLAMA_API_KEY

python -m gamingbench.main \
  --num-matches "${NUM_MATCHES}" \
  --exp-root "${EXP_ROOT}" \
  --seed "${SEED}" \
  --game-names "${GAME}" \
  --agent-configs \
    gamingbench/configs/agent_configs/prompt_agent.yaml \
    gamingbench/configs/agent_configs/prompt_agent.yaml \
  --model-configs \
    gamingbench/configs/model_configs/qwen3-14b-ollama-think.yaml \
    gamingbench/configs/model_configs/qwen3-14b-ollama-think-baseline-b.yaml \
  --exchange-first-player \
  --num-workers "${NUM_WORKERS}" \
  --threshold-matches "${THRESHOLD_MATCHES}"
