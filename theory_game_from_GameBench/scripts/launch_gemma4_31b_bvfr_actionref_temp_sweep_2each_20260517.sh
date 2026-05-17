#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/user/ktlim/theory_game/theory_game_from_GameBench"
PY="/home/user/miniconda3/envs/theorygame/bin/python"
OUTPUT_ROOT="$ROOT/theory_results/gemma4_31b_base_vs_field_rationale_nohive_actionref_temp_sweep_2each_20260517"
MODEL="gemma4:31b"
GAMES=(
  air_land_sea
  arctic_scavengers
  are_you_the_traitor
  codenames
  pit
  santorini
  sea_battle
  two_rooms_and_a_boom
)

mkdir -p "$OUTPUT_ROOT"

launch_server() {
  local gpu="$1"
  local port="$2"
  local session="$3"

  tmux kill-session -t "$session" 2>/dev/null || true
  tmux new-session -d -s "$session" \
    "CUDA_VISIBLE_DEVICES=$gpu OLLAMA_HOST=127.0.0.1:$port OLLAMA_MODELS=/home/user/.ollama/models ollama serve"
}

launch_run() {
  local temp="$1"
  local port="$2"
  local session="$3"
  local temp_id="${temp//./p}"
  local run_id="gemma4_31b_base_vs_field_rationale_nohive_t${temp_id}_actionref_2each_20260517"

  tmux kill-session -t "$session" 2>/dev/null || true
  tmux new-session -d -s "$session" \
    "cd '$ROOT' && env OLLAMA_THINK=false OLLAMA_BASE_URL=http://127.0.0.1:$port '$PY' scripts/run_pair_prompt_comparison.py --run-id '$run_id' --output-root '$OUTPUT_ROOT' --comparison base_vs_field_rationale --left-agent base --right-agent field_rationale --left-backend ollama --right-backend ollama --left-model-name '$MODEL' --right-model-name '$MODEL' --left-base-url http://127.0.0.1:$port --right-base-url http://127.0.0.1:$port --games ${GAMES[*]} --num-matches 2 --temperature '$temp' --max-tokens 2048 --timeout 300 --response-retries 3 --match-timeout-seconds 1800 --prompt-output-mode compact_field_analysis --include-action-id-reference --seating balanced"
}

launch_server 0 11440 ollama-gemma4-temp-sweep-g0
launch_server 1 11441 ollama-gemma4-temp-sweep-g1
launch_server 2 11442 ollama-gemma4-temp-sweep-g2
launch_server 3 11443 ollama-gemma4-temp-sweep-g3

sleep 5

launch_run 0 11440 gb-gemma4-31b-bvfr-actionref-t0-2each-20260517
launch_run 0.3 11441 gb-gemma4-31b-bvfr-actionref-t03-2each-20260517
launch_run 0.7 11442 gb-gemma4-31b-bvfr-actionref-t07-2each-20260517
launch_run 1 11443 gb-gemma4-31b-bvfr-actionref-t1-2each-20260517

echo "output_root=$OUTPUT_ROOT"
tmux ls | rg 'ollama-gemma4-temp-sweep|gb-gemma4-31b-bvfr-actionref'
