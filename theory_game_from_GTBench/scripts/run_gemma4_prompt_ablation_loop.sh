#!/usr/bin/env bash
set -euo pipefail

export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11437/v1}"
export OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"

python scripts/run_gemma4_prompt_ablation_loop.py "$@"
