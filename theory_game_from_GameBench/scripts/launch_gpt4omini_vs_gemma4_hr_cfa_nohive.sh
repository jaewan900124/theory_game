#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/user/ktlim/theory_game/theory_game_from_GameBench"
ENV_FILE="/home/user/ktlim/theory_game/.env"
PY="/home/user/miniconda3/envs/theorygame/bin/python"
OUTPUT_ROOT="theory_results"
RUN_PREFIX="gpt4omini_base_vs_gemma4_31b_high_reasoning_cfa_nohive_20260515"
COMPARISON="base_vs_high_reasoning"
CURRENT_SESSIONS=(
  gb-basis-nohive-base-vs-hd-gpu1
  gb-basis-nohive-base-vs-hr-gpu0
  gb-basis-nohive-hr-vs-hd-gpu2
  gb-basis-nohive-qwen32-base-vs-hd-gpu3
  gb-basis-nohive-qwen32-base-vs-hr-gpu3
  gb-basis-nohive-qwen32-hr-vs-hd-gpu3
)

wait_for_current_runs() {
  while true; do
    local active=0
    for session in "${CURRENT_SESSIONS[@]}"; do
      if tmux has-session -t "$session" 2>/dev/null; then
        active=1
        break
      fi
    done
    if [[ "$active" == "0" ]]; then
      return
    fi
    sleep 60
  done
}

require_openai_key() {
  if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    return
  fi
  if [[ -f "$ROOT/credentials.json" ]]; then
    return
  fi
  echo "OPENAI_API_KEY is not set and $ROOT/credentials.json does not exist." >&2
  exit 1
}

launch_shard() {
  local shard="$1"
  local port="$2"
  shift 2
  local session="gb-gpt4omini-vs-gemma4-hr-cfa-s${shard}"
  local run_id="${RUN_PREFIX}_s${shard}"
  local games="$*"

  tmux new-session -d -s "$session" \
    "cd '$ROOT' && set -a && source '$ENV_FILE' && set +a && env OLLAMA_THINK=false OLLAMA_BASE_URL=http://127.0.0.1:${port} '$PY' scripts/run_pair_prompt_comparison.py --run-id '$run_id' --output-root '$OUTPUT_ROOT' --comparison '$COMPARISON' --left-agent base --right-agent high_reasoning --left-backend openai --left-model-name gpt-4o-mini --right-backend ollama --right-model-name gemma4:31b --right-base-url http://127.0.0.1:${port} --games ${games} --num-matches 5 --temperature 1.0 --max-tokens 2048 --timeout 300 --response-retries 3 --match-timeout-seconds 1800 --prompt-output-mode compact_field_analysis --seating balanced"
}

cd "$ROOT"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi
wait_for_current_runs
require_openai_key

launch_shard 0 11436 air_land_sea are_you_the_traitor
launch_shard 1 11437 arctic_scavengers codenames
launch_shard 2 11438 pit two_rooms_and_a_boom
launch_shard 3 11439 santorini sea_battle

tmux ls | grep 'gb-gpt4omini-vs-gemma4-hr-cfa' || true
