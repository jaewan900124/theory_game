#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: $0 <seed> <port> <suffix>" >&2
  exit 2
fi

seed="$1"
port="$2"
suffix="$3"

cd "$(dirname "$0")/.."
export OLLAMA_THINK=false
export GAMEBENCH_SEA_BATTLE_MAX_ROUNDS="${GAMEBENCH_SEA_BATTLE_MAX_ROUNDS:-40}"

games=(
  sea_battle
  codenames
  two_rooms_and_a_boom
  are_you_the_traitor
  pit
  arctic_scavengers
)

for game in "${games[@]}"; do
  python scripts/run_pair_prompt_comparison.py \
    --run-id "base_vs_field_rationale_gemma4_31b_${game}_20260516_${suffix}" \
    --games "${game}" \
    --comparison base_vs_field_rationale \
    --left-agent base \
    --right-agent field_rationale \
    --num-matches 10 \
    --model-name gemma4:31b \
    --backend ollama \
    --base-url "http://127.0.0.1:${port}" \
    --temperature 1.0 \
    --max-tokens 2048 \
    --timeout 240 \
    --response-retries 3 \
    --match-timeout-seconds 1800 \
    --prompt-output-mode compact_field_analysis \
    --seed "${seed}" \
    --seating balanced
done

exec bash
