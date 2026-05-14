#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

GAME="${GAME:?GAME is required}"
ENGINEERING_PROFILE="${ENGINEERING_PROFILE:?ENGINEERING_PROFILE is required}"
PROFILE_TAG="${PROFILE_TAG:-${ENGINEERING_PROFILE}}"
ENGINEERING_PROFILE_MODE="${ENGINEERING_PROFILE_MODE:-reasoning}"
NUM_MATCHES="${NUM_MATCHES:-100}"
NUM_WORKERS="${NUM_WORKERS:-1}"
THRESHOLD_MATCHES="${THRESHOLD_MATCHES:-100}"
SEED="${SEED:-0}"
EXP_ROOT="${EXP_ROOT:?EXP_ROOT is required}"
PYTHONPATH="${PYTHONPATH:-${REPO_ROOT}}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11437}"
OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"

MODEL_CONFIG="${MODEL_CONFIG:-gamingbench/configs/model_configs/qwen3-14b-ollama-no-think.yaml}"
BASELINE_AGENT_CONFIG="gamingbench/configs/agent_configs/prompt_agent.yaml"

TMP_AGENT_CONFIG="$(mktemp /tmp/${PROFILE_TAG}_agent_XXXX.yaml)"
trap 'rm -f "${TMP_AGENT_CONFIG}"' EXIT

cat > "${TMP_AGENT_CONFIG}" <<EOF
agent_name: TheoryInteractionFieldAgent
num_generations: 1
majority_vote: False
engineering_profile: ${ENGINEERING_PROFILE}
engineering_profile_mode: ${ENGINEERING_PROFILE_MODE}
engineering_profile_strict: True
EOF

export PYTHONPATH
export OLLAMA_BASE_URL
export OLLAMA_API_KEY

python -m gamingbench.main \
  --num-matches "${NUM_MATCHES}" \
  --exp-root "${EXP_ROOT}" \
  --seed "${SEED}" \
  --game-names "${GAME}" \
  --agent-configs \
    "${TMP_AGENT_CONFIG}" \
    "${BASELINE_AGENT_CONFIG}" \
  --model-configs \
    "${MODEL_CONFIG}" \
    "${MODEL_CONFIG}" \
  --exchange-first-player \
  --num-workers "${NUM_WORKERS}" \
  --threshold-matches "${THRESHOLD_MATCHES}"
