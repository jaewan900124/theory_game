#!/usr/bin/env bash
set -euo pipefail

LOCAL_DIR="${LOCAL_DIR:-/home/user/.cache/huggingface/qwen35-122b-a10b-gptq-4bit}"

if [[ ! -d "${LOCAL_DIR}" ]]; then
  echo "Missing local model dir: ${LOCAL_DIR}"
  exit 1
fi

echo "Model dir: ${LOCAL_DIR}"
du -sh "${LOCAL_DIR}"
find "${LOCAL_DIR}" -maxdepth 1 -type f | sed "s#${LOCAL_DIR}/##" | sort | head -80
