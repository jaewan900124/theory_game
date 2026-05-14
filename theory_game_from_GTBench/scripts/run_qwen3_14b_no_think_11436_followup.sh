#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

bash scripts/run_qwen3_14b_high_distill_vs_baseline_no_think_11436.sh
bash scripts/run_qwen3_14b_high_reasoning_vs_baseline_no_think_11436.sh
