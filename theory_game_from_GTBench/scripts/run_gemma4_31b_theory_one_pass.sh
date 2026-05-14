#!/usr/bin/env bash
set -euo pipefail

cd /home/nlpgpu7/jaewanpark/project/theory_game/theory_game_from_GTBench

set -a
source /home/nlpgpu7/jaewanpark/project/.env
set +a

export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11436/v1}"
export OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"
export PYTHONPATH=.

python gamingbench/main.py \
  --num-matches 1 \
  --exp-root experiments/gemma4_31b_theory_one_pass \
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
    gamingbench/configs/model_configs/gemma4-31b-ollama.yaml
