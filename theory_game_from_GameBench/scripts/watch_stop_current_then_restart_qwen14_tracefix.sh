#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/nlpgpu7/jaewanpark/project/theory_game/theory_game_from_GameBench"
OLD_HD_SESSION="gb_qwen14_hd_selected_s0_20260514_135220"
OLD_HR_SESSION="gb_qwen14_hr_selected_s1_20260514_132700"
OLD_MERGE_SESSION="gb_qwen14_theory_merge_20260514_135220"
OLD_HD_MATCHES="$ROOT/theory_results/high_distill_qwen3_14b_no_think_selected_s0_20260514_135220/matches.jsonl"
OLD_HR_MATCHES="$ROOT/theory_results/high_reasoning_qwen3_14b_no_think_selected_s1_20260514_132700/matches.jsonl"

TS="${1:-$(date +%Y%m%d_%H%M%S)}"
NEW_HD_RUN="high_distill_qwen3_14b_no_think_tracefix_selected_s0_${TS}"
NEW_HR_RUN="high_reasoning_qwen3_14b_no_think_tracefix_selected_s1_${TS}"
NEW_HD_SESSION="gb_qwen14_hd_tracefix_s0_${TS}"
NEW_HR_SESSION="gb_qwen14_hr_tracefix_s1_${TS}"
NEW_MERGE_SESSION="gb_qwen14_tracefix_merge_${TS}"
COMBINED_DIR="combined_results/qwen3_14b_no_think_tracefix_selected_high_reasoning_high_distill_vs_random_${TS}"
ANALYSIS_DIR="combined_results/analysis_qwen3_14b_no_think_tracefix_selected_high_reasoning_high_distill_vs_random_${TS}"
GAMES="codenames santorini are_you_the_traitor air_land_sea two_rooms_and_a_boom"

count_game() {
  local matches_file="$1"
  local game="$2"
  if [[ ! -f "$matches_file" ]]; then
    echo 0
    return
  fi
  grep -c "\"game\": \"$game\"" "$matches_file" || true
}

stop_when_game_done() {
  local session="$1"
  local matches_file="$2"
  local game="$3"
  local target="$4"
  while tmux has-session -t "$session" 2>/dev/null; do
    local count
    count="$(count_game "$matches_file" "$game")"
    if [[ "$count" -ge "$target" ]]; then
      tmux kill-session -t "$session" 2>/dev/null || true
      break
    fi
    sleep 15
  done
}

tmux kill-session -t "$OLD_MERGE_SESSION" 2>/dev/null || true

stop_when_game_done "$OLD_HD_SESSION" "$OLD_HD_MATCHES" "santorini" 6 &
HD_WATCH_PID=$!
stop_when_game_done "$OLD_HR_SESSION" "$OLD_HR_MATCHES" "are_you_the_traitor" 6 &
HR_WATCH_PID=$!
wait "$HD_WATCH_PID" "$HR_WATCH_PID"

tmux new-session -d -s "$NEW_HD_SESSION" \
  "cd $ROOT && env OLLAMA_THINK=false OLLAMA_BASE_URL=http://127.0.0.1:11439 python scripts/run_theory_prompt_grid.py --run-id $NEW_HD_RUN --output-root theory_results --modes high_distill --match-plan paper_gpt4_random --games $GAMES --model-name qwen3:14b --backend ollama --base-url http://127.0.0.1:11439 --seating balanced --temperature 1.0 --max-tokens 1100 --timeout 240 --response-retries 3 --match-timeout-seconds 0"

tmux new-session -d -s "$NEW_HR_SESSION" \
  "cd $ROOT && env OLLAMA_THINK=false OLLAMA_BASE_URL=http://127.0.0.1:11441 python scripts/run_theory_prompt_grid.py --run-id $NEW_HR_RUN --output-root theory_results --modes high_reasoning --match-plan paper_gpt4_random --games $GAMES --model-name qwen3:14b --backend ollama --base-url http://127.0.0.1:11441 --seating balanced --temperature 1.0 --max-tokens 1100 --timeout 240 --response-retries 3 --match-timeout-seconds 0"

tmux new-session -d -s "$NEW_MERGE_SESSION" \
  "cd $ROOT && while tmux has-session -t $NEW_HD_SESSION 2>/dev/null || tmux has-session -t $NEW_HR_SESSION 2>/dev/null; do sleep 30; done; python scripts/merge_prompt_results.py --output-dir $COMBINED_DIR --include-run theory_results/$NEW_HR_RUN=codenames,santorini,are_you_the_traitor,air_land_sea,two_rooms_and_a_boom --include-run theory_results/$NEW_HD_RUN=codenames,santorini,are_you_the_traitor,air_land_sea,two_rooms_and_a_boom; python scripts/analyze_basic_results.py $COMBINED_DIR --output-dir $ANALYSIS_DIR"

echo "Started $NEW_HD_SESSION and $NEW_HR_SESSION"
echo "Merge watcher: $NEW_MERGE_SESSION"
echo "Combined output: $ROOT/$COMBINED_DIR"
