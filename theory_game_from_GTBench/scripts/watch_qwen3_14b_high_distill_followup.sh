#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

NO_THINK_SESSION="${NO_THINK_SESSION:-qwen14_high_distill_no_think}"
THINK_SESSION="${THINK_SESSION:-qwen14_high_distill_think}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11437}"

echo "[watch] waiting for ${NO_THINK_SESSION} to finish"
while tmux has-session -t "${NO_THINK_SESSION}" 2>/dev/null; do
  sleep 30
done

echo "[watch] ${NO_THINK_SESSION} finished, checking ${OLLAMA_BASE_URL}"
if ! curl --max-time 5 -s "${OLLAMA_BASE_URL}/api/tags" >/dev/null; then
  echo "[watch] server check failed, not starting think run"
  exit 1
fi

if tmux has-session -t "${THINK_SESSION}" 2>/dev/null; then
  echo "[watch] ${THINK_SESSION} already exists, not starting duplicate run"
  exit 0
fi

echo "[watch] server healthy, starting ${THINK_SESSION}"
tmux new-session -d -s "${THINK_SESSION}" "cd ${REPO_ROOT} && bash scripts/run_qwen3_14b_high_distill_vs_baseline_think.sh"
echo "[watch] started ${THINK_SESSION}"
