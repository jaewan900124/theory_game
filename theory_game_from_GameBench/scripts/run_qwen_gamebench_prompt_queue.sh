#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

QUEUE_ID="${1:-$(date +%Y%m%d_%H%M%S)}"
GPU0_BASE_URL="${GPU0_BASE_URL:-http://127.0.0.1:11439}"
GPU1_BASE_URL="${GPU1_BASE_URL:-http://127.0.0.1:11441}"
GPU0_HOST="${GPU0_BASE_URL#http://}"
GPU1_HOST="${GPU1_BASE_URL#http://}"
EXISTING_QWEN8_HR_S0="${EXISTING_QWEN8_HR_S0:-}"
EXISTING_QWEN8_HR_S1="${EXISTING_QWEN8_HR_S1:-gb_hr_qwen8_s1_20260514_113740}"
SKIP_ARCTIC="${SKIP_ARCTIC:-0}"

MODEL8="${MODEL8:-qwen3:8b}"
MODEL14="${MODEL14:-qwen3:14b}"
OUTPUT_ROOT_THEORY="${OUTPUT_ROOT_THEORY:-theory_results}"
OUTPUT_ROOT_BASIC="${OUTPUT_ROOT_BASIC:-basic_results}"
COMBINED_ROOT="${COMBINED_ROOT:-combined_results}"

# Paper-style GameBench evaluation should let each game terminate by its own
# rule-defined end condition. Set these env vars only for debugging stuck runs.
MAIN_TIMEOUT="${MAIN_TIMEOUT:-0}"
ARCTIC_TIMEOUT="${ARCTIC_TIMEOUT:-0}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-240}"
MAX_TOKENS="${MAX_TOKENS:-1100}"
TEMP="${TEMP:-1.0}"
RETRIES="${RETRIES:-3}"

GAMES_A_MAIN=(air_land_sea codenames hive pit)
GAMES_A_ARCTIC=(arctic_scavengers)
GAMES_B=(are_you_the_traitor santorini sea_battle two_rooms_and_a_boom)

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

wait_session() {
  local session="$1"
  while tmux has-session -t "$session" 2>/dev/null; do
    sleep 30
  done
}

wait_sessions() {
  local session
  for session in "$@"; do
    wait_session "$session"
  done
}

start_job() {
  local session="$1"
  shift
  log "start ${session}: $*"
  tmux new-session -d -s "$session" -c "$ROOT" "$*"
}

theory_cmd() {
  local run_id="$1"
  local mode="$2"
  local model="$3"
  local base_url="$4"
  local match_timeout="$5"
  shift 5
  printf 'env OLLAMA_THINK=false OLLAMA_BASE_URL=%s python scripts/run_theory_prompt_grid.py --run-id %s --output-root %s --modes %s --match-plan paper_gpt4_random --games %s --model-name %s --backend ollama --base-url %s --seating random --temperature %s --max-tokens %s --timeout %s --response-retries %s --match-timeout-seconds %s' \
    "$base_url" "$run_id" "$OUTPUT_ROOT_THEORY" "$mode" "$*" "$model" "$base_url" "$TEMP" "$MAX_TOKENS" "$REQUEST_TIMEOUT" "$RETRIES" "$match_timeout"
}

basic_cmd() {
  local run_id="$1"
  local model="$2"
  local base_url="$3"
  local match_timeout="$4"
  shift 4
  printf 'env OLLAMA_THINK=false OLLAMA_BASE_URL=%s python scripts/run_basic_prompt_grid.py --run-id %s --output-root %s --match-plan paper_gpt4_random --games %s --model-name %s --backend ollama --base-url %s --seating random --temperature %s --max-tokens %s --timeout %s --response-retries %s --match-timeout-seconds %s' \
    "$base_url" "$run_id" "$OUTPUT_ROOT_BASIC" "$*" "$model" "$base_url" "$TEMP" "$MAX_TOKENS" "$REQUEST_TIMEOUT" "$RETRIES" "$match_timeout"
}

run_gpu0_theory_split() {
  local prefix="$1"
  local mode="$2"
  local model="$3"
  local session_main="${prefix}_s0_main_${QUEUE_ID}"
  local session_arctic="${prefix}_s0_arctic_${QUEUE_ID}"
  local run_main="${mode}_${model//:/_}_random_s0_main_${QUEUE_ID}"
  local run_arctic="${mode}_${model//:/_}_random_s0_arctic_${QUEUE_ID}"

  start_job "$session_main" "$(theory_cmd "$run_main" "$mode" "$model" "$GPU0_BASE_URL" "$MAIN_TIMEOUT" "${GAMES_A_MAIN[@]}")"
  wait_session "$session_main"
  if [[ "$SKIP_ARCTIC" == "1" ]]; then
    log "skip arctic_scavengers for ${prefix} ${mode}"
    return
  fi
  start_job "$session_arctic" "$(theory_cmd "$run_arctic" "$mode" "$model" "$GPU0_BASE_URL" "$ARCTIC_TIMEOUT" "${GAMES_A_ARCTIC[@]}")"
  wait_session "$session_arctic"
}

run_gpu1_theory_b() {
  local prefix="$1"
  local mode="$2"
  local model="$3"
  local session="${prefix}_s1_${QUEUE_ID}"
  local run_id="${mode}_${model//:/_}_random_s1_${QUEUE_ID}"

  start_job "$session" "$(theory_cmd "$run_id" "$mode" "$model" "$GPU1_BASE_URL" "$MAIN_TIMEOUT" "${GAMES_B[@]}")"
}

run_gpu0_basic_split() {
  local prefix="$1"
  local model="$2"
  local session_main="${prefix}_s0_main_${QUEUE_ID}"
  local session_arctic="${prefix}_s0_arctic_${QUEUE_ID}"
  local run_main="base_prompt_${model//:/_}_random_s0_main_${QUEUE_ID}"
  local run_arctic="base_prompt_${model//:/_}_random_s0_arctic_${QUEUE_ID}"

  start_job "$session_main" "$(basic_cmd "$run_main" "$model" "$GPU0_BASE_URL" "$MAIN_TIMEOUT" "${GAMES_A_MAIN[@]}")"
  wait_session "$session_main"
  if [[ "$SKIP_ARCTIC" == "1" ]]; then
    log "skip arctic_scavengers for ${prefix}"
    return
  fi
  start_job "$session_arctic" "$(basic_cmd "$run_arctic" "$model" "$GPU0_BASE_URL" "$ARCTIC_TIMEOUT" "${GAMES_A_ARCTIC[@]}")"
  wait_session "$session_arctic"
}

run_gpu1_basic_b() {
  local prefix="$1"
  local model="$2"
  local session="${prefix}_s1_${QUEUE_ID}"
  local run_id="base_prompt_${model//:/_}_random_s1_${QUEUE_ID}"

  start_job "$session" "$(basic_cmd "$run_id" "$model" "$GPU1_BASE_URL" "$MAIN_TIMEOUT" "${GAMES_B[@]}")"
}

stop_model_if_loaded() {
  local host="$1"
  local model="$2"
  log "ollama stop ${model} on ${host}"
  OLLAMA_HOST="$host" ollama stop "$model" || true
}

merge_and_analyze_8b() {
  local out="${COMBINED_ROOT}/qwen3_8b_high_reasoning_high_distill_vs_random_${QUEUE_ID}"
  local analysis="${COMBINED_ROOT}/analysis_qwen3_8b_high_reasoning_high_distill_vs_random_${QUEUE_ID}"
  local merge_args=(
    --output-dir "$out" \
    --include-run "${OUTPUT_ROOT_THEORY}/high_reasoning_qwen3_8b_random_s0_main_${QUEUE_ID}=air_land_sea,codenames,hive,pit" \
    --include-run "${OUTPUT_ROOT_THEORY}/high_reasoning_qwen3_8b_random_s1_20260514_113740=are_you_the_traitor,santorini,sea_battle,two_rooms_and_a_boom" \
    --include-run "${OUTPUT_ROOT_THEORY}/high_distill_qwen3_8b_random_s0_main_${QUEUE_ID}=air_land_sea,codenames,hive,pit" \
    --include-run "${OUTPUT_ROOT_THEORY}/high_distill_qwen3_8b_random_s1_${QUEUE_ID}=are_you_the_traitor,santorini,sea_battle,two_rooms_and_a_boom"
  )
  if [[ "$SKIP_ARCTIC" != "1" ]]; then
    merge_args+=(
      --include-run "${OUTPUT_ROOT_THEORY}/high_reasoning_qwen3_8b_random_s0_arctic_${QUEUE_ID}=arctic_scavengers"
      --include-run "${OUTPUT_ROOT_THEORY}/high_distill_qwen3_8b_random_s0_arctic_${QUEUE_ID}=arctic_scavengers"
    )
  fi
  python scripts/merge_prompt_results.py "${merge_args[@]}"
  python scripts/analyze_basic_results.py "$out" --output-dir "$analysis"
}

merge_and_analyze_14b() {
  local out="${COMBINED_ROOT}/qwen3_14b_base_high_reasoning_high_distill_vs_random_${QUEUE_ID}"
  local analysis="${COMBINED_ROOT}/analysis_qwen3_14b_base_high_reasoning_high_distill_vs_random_${QUEUE_ID}"
  local merge_args=(
    --output-dir "$out" \
    --include-run "${OUTPUT_ROOT_BASIC}/base_prompt_qwen3_14b_random_s0_main_${QUEUE_ID}=air_land_sea,codenames,hive,pit" \
    --include-run "${OUTPUT_ROOT_BASIC}/base_prompt_qwen3_14b_random_s1_${QUEUE_ID}=are_you_the_traitor,santorini,sea_battle,two_rooms_and_a_boom" \
    --include-run "${OUTPUT_ROOT_THEORY}/high_reasoning_qwen3_14b_random_s0_main_${QUEUE_ID}=air_land_sea,codenames,hive,pit" \
    --include-run "${OUTPUT_ROOT_THEORY}/high_reasoning_qwen3_14b_random_s1_${QUEUE_ID}=are_you_the_traitor,santorini,sea_battle,two_rooms_and_a_boom" \
    --include-run "${OUTPUT_ROOT_THEORY}/high_distill_qwen3_14b_random_s0_main_${QUEUE_ID}=air_land_sea,codenames,hive,pit" \
    --include-run "${OUTPUT_ROOT_THEORY}/high_distill_qwen3_14b_random_s1_${QUEUE_ID}=are_you_the_traitor,santorini,sea_battle,two_rooms_and_a_boom"
  )
  if [[ "$SKIP_ARCTIC" != "1" ]]; then
    merge_args+=(
      --include-run "${OUTPUT_ROOT_BASIC}/base_prompt_qwen3_14b_random_s0_arctic_${QUEUE_ID}=arctic_scavengers"
      --include-run "${OUTPUT_ROOT_THEORY}/high_reasoning_qwen3_14b_random_s0_arctic_${QUEUE_ID}=arctic_scavengers"
      --include-run "${OUTPUT_ROOT_THEORY}/high_distill_qwen3_14b_random_s0_arctic_${QUEUE_ID}=arctic_scavengers"
    )
  fi
  python scripts/merge_prompt_results.py "${merge_args[@]}"
  python scripts/analyze_basic_results.py "$out" --output-dir "$analysis"
}

log "queue id: ${QUEUE_ID}"
log "GPU0 ${GPU0_BASE_URL}, GPU1 ${GPU1_BASE_URL}, skip_arctic=${SKIP_ARCTIC}, arctic timeout ${ARCTIC_TIMEOUT}s"

log "run qwen3:8b high_reasoning set A"
PID_HR8_S0=
if [[ -n "$EXISTING_QWEN8_HR_S0" ]] && tmux has-session -t "$EXISTING_QWEN8_HR_S0" 2>/dev/null; then
  log "wait existing qwen3:8b high_reasoning set A: ${EXISTING_QWEN8_HR_S0}"
  wait_session "$EXISTING_QWEN8_HR_S0" &
  PID_HR8_S0=$!
elif [[ -n "$EXISTING_QWEN8_HR_S0" ]]; then
  log "existing set A session is not running; assuming output already exists: ${EXISTING_QWEN8_HR_S0}"
else
  run_gpu0_theory_split gb_hr_qwen8_retry high_reasoning "$MODEL8" &
  PID_HR8_S0=$!
fi
if tmux has-session -t "$EXISTING_QWEN8_HR_S1" 2>/dev/null; then
  log "wait existing qwen3:8b high_reasoning set B: ${EXISTING_QWEN8_HR_S1}"
  wait_session "$EXISTING_QWEN8_HR_S1" &
  PID_HR8_S1=$!
else
  log "existing set B session is not running: ${EXISTING_QWEN8_HR_S1}"
  PID_HR8_S1=
fi
if [[ -n "${PID_HR8_S0}" ]]; then
  wait "$PID_HR8_S0"
fi
if [[ -n "${PID_HR8_S1}" ]]; then
  wait "$PID_HR8_S1"
fi

log "run qwen3:8b high_distill"
run_gpu1_theory_b gb_hd_qwen8 high_distill "$MODEL8"
run_gpu0_theory_split gb_hd_qwen8 high_distill "$MODEL8" &
PID_HD8_S0=$!
wait "$PID_HD8_S0"
wait_sessions "gb_hd_qwen8_s1_${QUEUE_ID}"

log "merge qwen3:8b high_reasoning/high_distill"
merge_and_analyze_8b

log "free qwen3:8b runners before qwen3:14b"
stop_model_if_loaded "$GPU0_HOST" "$MODEL8"
stop_model_if_loaded "$GPU1_HOST" "$MODEL8"
stop_model_if_loaded "127.0.0.1:11436" "$MODEL8"
stop_model_if_loaded "127.0.0.1:11440" "$MODEL8"
stop_model_if_loaded "127.0.0.1:11437" "$MODEL8"
sleep 10
nvidia-smi || true

log "run qwen3:14b base_prompt"
run_gpu1_basic_b gb_base_qwen14 "$MODEL14"
run_gpu0_basic_split gb_base_qwen14 "$MODEL14" &
PID_BASE14_S0=$!
wait "$PID_BASE14_S0"
wait_sessions "gb_base_qwen14_s1_${QUEUE_ID}"

log "run qwen3:14b high_reasoning"
run_gpu1_theory_b gb_hr_qwen14 high_reasoning "$MODEL14"
run_gpu0_theory_split gb_hr_qwen14 high_reasoning "$MODEL14" &
PID_HR14_S0=$!
wait "$PID_HR14_S0"
wait_sessions "gb_hr_qwen14_s1_${QUEUE_ID}"

log "run qwen3:14b high_distill"
run_gpu1_theory_b gb_hd_qwen14 high_distill "$MODEL14"
run_gpu0_theory_split gb_hd_qwen14 high_distill "$MODEL14" &
PID_HD14_S0=$!
wait "$PID_HD14_S0"
wait_sessions "gb_hd_qwen14_s1_${QUEUE_ID}"

log "merge qwen3:14b base/high_reasoning/high_distill"
merge_and_analyze_14b

log "done"
