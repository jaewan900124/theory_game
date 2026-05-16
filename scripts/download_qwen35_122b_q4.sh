#!/usr/bin/env bash
set -euo pipefail

# Download only. This does not start an inference server or load the model on GPU.
MODEL_ID="${MODEL_ID:-btbtyler09/Qwen3.5-122B-A10B-GPTQ-4bit}"
LOCAL_DIR="${LOCAL_DIR:-/home/user/.cache/huggingface/qwen35-122b-a10b-gptq-4bit}"
PYTHON_BIN="${PYTHON_BIN:-/home/user/miniconda3/envs/hf/bin/python}"

export HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-0}"
export HF_HUB_DISABLE_XET="${HF_HUB_DISABLE_XET:-1}"
export MODEL_ID
export LOCAL_DIR

"${PYTHON_BIN}" - <<'PY'
import os
from huggingface_hub import snapshot_download

model_id = os.environ["MODEL_ID"]
local_dir = os.environ["LOCAL_DIR"]

print(f"Downloading {model_id}")
print(f"Local dir: {local_dir}")

snapshot_download(
    repo_id=model_id,
    local_dir=local_dir,
)

print("Download complete.")
PY
