#!/usr/bin/env bash
set -euo pipefail

export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11437/v1}"
export OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"

python -m gamingbench.main \
  --num-matches "${NUM_MATCHES:-1}" \
  --seed "${SEED:-0}" \
  --exp-root "${EXP_ROOT:-experiments/gemma4_31b_theory_vs_baseline}" \
  --game-names \
    tictactoe \
    connect4 \
    breakthrough \
    first_sealed_auction \
    liars_dice \
    negotiation \
    nim \
    pig \
    kuhn_poker \
    prisoners_dilemma \
  --agent-configs \
    gamingbench/configs/agent_configs/theory_agent.yaml \
    gamingbench/configs/agent_configs/prompt_agent.yaml \
  --model-configs \
    gamingbench/configs/model_configs/gemma4-31b-ollama.yaml \
    gamingbench/configs/model_configs/gemma4-31b-ollama.yaml \
  --num-workers 1
