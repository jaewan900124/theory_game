#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

while pgrep -f 'run_qwen3_14b_high_reasoning_alt6_vs_baseline_onegame_no_think_11437.sh' >/dev/null; do
  sleep 30
done

GAME=kuhn_poker NUM_MATCHES=100 THRESHOLD_MATCHES=100 bash scripts/run_qwen3_14b_kuhn_groups_vs_baseline_no_think_11437.sh
