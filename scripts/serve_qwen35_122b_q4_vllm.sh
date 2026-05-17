#!/usr/bin/env bash
set -euo pipefail

# This starts inference and will load the model onto the selected GPUs.
# Run only when you are ready to use the two A100s.
LOCAL_DIR="${LOCAL_DIR:-/home/user/.cache/huggingface/qwen35-122b-a10b-gptq-4bit}"
TOKENIZER_DIR="${TOKENIZER_DIR:-/home/user/.cache/huggingface/qwen35-122b-a10b-base-tokenizer}"
PORT="${PORT:-8000}"
GPU_IDS="${GPU_IDS:-0,1}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-32768}"
VLLM_BIN="${VLLM_BIN:-/home/user/miniconda3/envs/hf/bin/vllm}"
REASONING_PARSER="${REASONING_PARSER:-}"
DTYPE="${DTYPE:-float16}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-2}"
ENFORCE_EAGER="${ENFORCE_EAGER:-0}"

if [[ ! -d "${LOCAL_DIR}" ]]; then
  echo "Missing local model dir: ${LOCAL_DIR}"
  echo "Run scripts/download_qwen35_122b_q4.sh first."
  exit 1
fi

if [[ ! -f "${TOKENIZER_DIR}/tokenizer_config.json" ]]; then
  mkdir -p "${TOKENIZER_DIR}"
  cp "${LOCAL_DIR}/tokenizer_config.json" "${TOKENIZER_DIR}/"
  cp "${LOCAL_DIR}/tokenizer.json" "${TOKENIZER_DIR}/"
  cp "${LOCAL_DIR}/vocab.json" "${TOKENIZER_DIR}/"
  cp "${LOCAL_DIR}/merges.txt" "${TOKENIZER_DIR}/"
  cp "${LOCAL_DIR}/chat_template.jinja" "${TOKENIZER_DIR}/"
  sed -i 's/"tokenizer_class": "TokenizersBackend"/"tokenizer_class": "Qwen2TokenizerFast"/' \
    "${TOKENIZER_DIR}/tokenizer_config.json"
fi

export CUDA_VISIBLE_DEVICES="${GPU_IDS}"

args=(
  serve "${LOCAL_DIR}"
  --served-model-name qwen35-122b-a10b-q4 \
  --tokenizer "${TOKENIZER_DIR}" \
  --tensor-parallel-size "${TENSOR_PARALLEL_SIZE}" \
  --gpu-memory-utilization 0.92 \
  --max-model-len "${MAX_MODEL_LEN}" \
  --dtype "${DTYPE}" \
  --generation-config vllm \
  --trust-remote-code \
  --skip-mm-profiling \
  --port "${PORT}"
)

if [[ -n "${REASONING_PARSER}" ]]; then
  args+=(--reasoning-parser "${REASONING_PARSER}")
fi

if [[ "${ENFORCE_EAGER}" == "1" ]]; then
  args+=(--enforce-eager)
fi

exec "${VLLM_BIN}" "${args[@]}"
