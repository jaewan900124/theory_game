#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/user/ktlim/theory_game/theory_game_from_GameBench"
PY="/home/user/miniconda3/envs/theorygame/bin/python"
OUTPUT_ROOT="$ROOT/theory_results/gemma4_31b_field_rationale_vs_qwen_checked_2each_v4_20260517"
OLLAMA_MODEL_DIR="/home/user/.ollama/models"
GEMMA_MODEL="gemma4:31b"
CHECKER_MODEL="hf.co/Qwen/Qwen3-Next-80B-A3B-Instruct-GGUF:Q4_K_M"

GAMES_SHARD_0=(
  air_land_sea
  arctic_scavengers
  are_you_the_traitor
  codenames
)

GAMES_SHARD_1=(
  pit
  santorini
  sea_battle
  two_rooms_and_a_boom
)

mkdir -p "$OUTPUT_ROOT"

launch_server() {
  local gpu="$1"
  local port="$2"
  local model="$3"
  local session="$4"

  tmux kill-session -t "$session" 2>/dev/null || true
  tmux new-session -d -s "$session" \
    "CUDA_VISIBLE_DEVICES=$gpu OLLAMA_HOST=127.0.0.1:$port OLLAMA_MODELS=$OLLAMA_MODEL_DIR ollama serve"

  tmux new-window -t "$session" -n warmup \
    "sleep 8; OLLAMA_HOST=127.0.0.1:$port ollama show '$model' >/dev/null && printf 'ready %s %s\n' '$port' '$model'; bash"
}

wait_for_model() {
  local port="$1"
  local model="$2"
  local label="$3"
  local attempts=120

  printf 'waiting for %s on port %s (%s)\n' "$label" "$port" "$model"
  for ((i = 1; i <= attempts; i++)); do
    if OLLAMA_HOST=127.0.0.1:"$port" ollama show "$model" >/dev/null 2>&1; then
      printf 'ready %s on port %s\n' "$label" "$port"
      return 0
    fi
    sleep 5
  done

  printf 'ERROR: timed out waiting for %s on port %s (%s)\n' "$label" "$port" "$model" >&2
  return 1
}

launch_run() {
  local shard="$1"
  local draft_port="$2"
  local checker_port="$3"
  local session="$4"
  shift 4
  local games=("$@")
  local run_id="gemma4_31b_fr_vs_fr_qwen_checker_shard${shard}_2each_v4_20260517"

  tmux kill-session -t "$session" 2>/dev/null || true
  tmux new-session -d -s "$session" \
    "cd '$ROOT' && env OLLAMA_THINK=false OLLAMA_BASE_URL=http://127.0.0.1:$draft_port '$PY' scripts/run_pair_prompt_comparison.py --run-id '$run_id' --output-root '$OUTPUT_ROOT' --comparison field_rationale_vs_field_rationale_checked --left-agent field_rationale --right-agent field_rationale_checked --left-backend ollama --right-backend ollama --left-model-name '$GEMMA_MODEL' --right-model-name '$GEMMA_MODEL' --left-base-url http://127.0.0.1:$draft_port --right-base-url http://127.0.0.1:$draft_port --right-checker-backend ollama --right-checker-model-name '$CHECKER_MODEL' --right-checker-base-url http://127.0.0.1:$checker_port --games ${games[*]} --num-matches 2 --temperature 1.0 --max-tokens 2048 --timeout 300 --response-retries 3 --checker-temperature 0.2 --checker-max-tokens 1024 --checker-timeout 300 --match-timeout-seconds 1800 --prompt-output-mode compact_field_analysis --include-action-id-reference --seating balanced"
}

launch_server 0 11440 "$GEMMA_MODEL" fr-checker-gemma-g0
launch_server 1 11441 "$GEMMA_MODEL" fr-checker-gemma-g1
launch_server 2 11442 "$CHECKER_MODEL" fr-checker-qwen-g2
launch_server 3 11443 "$CHECKER_MODEL" fr-checker-qwen-g3

wait_for_model 11440 "$GEMMA_MODEL" "gemma shard0"
wait_for_model 11441 "$GEMMA_MODEL" "gemma shard1"
wait_for_model 11442 "$CHECKER_MODEL" "qwen checker shard0"
wait_for_model 11443 "$CHECKER_MODEL" "qwen checker shard1"

launch_run 0 11440 11442 gb-fr-vs-fr-qwen-checker-shard0 "${GAMES_SHARD_0[@]}"
launch_run 1 11441 11443 gb-fr-vs-fr-qwen-checker-shard1 "${GAMES_SHARD_1[@]}"

echo "output_root=$OUTPUT_ROOT"
tmux ls | rg 'fr-checker|gb-fr-vs-fr-qwen-checker'
