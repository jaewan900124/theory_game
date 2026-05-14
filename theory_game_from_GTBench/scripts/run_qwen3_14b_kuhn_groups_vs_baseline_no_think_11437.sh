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
BASE_EXP_ROOT="${BASE_EXP_ROOT:-experiments/qwen3_14b_kuhn_groups_vs_baseline_onegame_no_think_11437}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11437}"

GROUP_IDS=(01 02 03 04 05 06 07 08 09 10)

for group_id in "${GROUP_IDS[@]}"; do
  profile="kuhn_group_${group_id}"
  profile_tag="g${group_id}"
  exp_root="${BASE_EXP_ROOT}/${profile_tag}/${GAME}"
  result_glob="${exp_root}/${GAME}"/*.jsonl
  if compgen -G "${result_glob}" > /dev/null; then
    echo "Skipping ${profile_tag}: existing result detected under ${exp_root}"
    continue
  fi
  echo "Running ${profile_tag} with profile ${profile}"
  GAME="${GAME}" \
  ENGINEERING_PROFILE="${profile}" \
  PROFILE_TAG="${profile_tag}" \
  NUM_MATCHES="${NUM_MATCHES}" \
  NUM_WORKERS="${NUM_WORKERS}" \
  THRESHOLD_MATCHES="${THRESHOLD_MATCHES}" \
  SEED="${SEED}" \
  EXP_ROOT="${exp_root}" \
  OLLAMA_BASE_URL="${OLLAMA_BASE_URL}" \
  bash scripts/run_qwen3_14b_custom_profile_vs_baseline_onegame_no_think.sh
done
