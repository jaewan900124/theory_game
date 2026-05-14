#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/nlpgpu7/jaewanpark/project/theory_game/theory_game_from_GTBench"
PROMPT_FILE="$ROOT_DIR/.codex/auto_prompt.md"
OUTPUT_DIR="$ROOT_DIR/experiments/auto_theory_loop"
LOG_DIR="$OUTPUT_DIR/codex_logs"
STATUS_FILE="$OUTPUT_DIR/status.json"
LAST_MESSAGE_FILE="$LOG_DIR/last_message.txt"
MAX_LOOPS="${MAX_LOOPS:-5}"
USE_RESUME_AFTER_FIRST="${USE_RESUME_AFTER_FIRST:-1}"

mkdir -p "$LOG_DIR"

cd "$ROOT_DIR"

export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11437/v1}"
export OLLAMA_API_KEY="${OLLAMA_API_KEY:-ollama}"

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Missing prompt file: $PROMPT_FILE" >&2
  exit 2
fi

write_status() {
  local status="$1"
  local loop="$2"
  local reason="$3"
  python - "$STATUS_FILE" "$status" "$loop" "$reason" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
payload = {
    "status": sys.argv[2],
    "loop": int(sys.argv[3]),
    "reason": sys.argv[4],
    "updated_at": datetime.now(timezone.utc).isoformat(),
}
if path.exists():
    try:
        old = json.loads(path.read_text())
        old.update(payload)
        payload = old
    except Exception:
        pass
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
PY
}

fingerprint() {
  {
    git status --short || true
    if [[ -d "$OUTPUT_DIR" ]]; then
      find "$OUTPUT_DIR" -type f \
        ! -path "$LOG_DIR/*" \
        -print0 | sort -z | xargs -0 sha256sum 2>/dev/null || true
    fi
  } | sha256sum | awk '{print $1}'
}

checks_pass() {
  python -m py_compile scripts/*.py
}

is_complete() {
  python - "$STATUS_FILE" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit(1)
try:
    data = json.loads(path.read_text())
except Exception:
    raise SystemExit(1)
if data.get("status") in {"complete", "completed"}:
    raise SystemExit(0)
raise SystemExit(1)
PY
}

write_status "running" 0 "watcher started"

previous_fingerprint="$(fingerprint)"

for loop in $(seq 1 "$MAX_LOOPS"); do
  loop_log="$LOG_DIR/loop_${loop}.jsonl"
  echo "===== Codex auto loop $loop / $MAX_LOOPS ====="
  write_status "running" "$loop" "codex loop started"

  if [[ "$loop" -eq 1 || "$USE_RESUME_AFTER_FIRST" != "1" ]]; then
    codex -a never exec \
      -C "$ROOT_DIR" \
      -s workspace-write \
      --json \
      -o "$LAST_MESSAGE_FILE" \
      - < "$PROMPT_FILE" | tee "$loop_log"
  else
    codex -a never exec resume \
      --last \
      --json \
      -o "$LAST_MESSAGE_FILE" \
      - < "$PROMPT_FILE" | tee "$loop_log"
  fi

  current_fingerprint="$(fingerprint)"

  if is_complete; then
    if checks_pass; then
      write_status "complete" "$loop" "status complete and checks passed"
      echo "Completed after loop $loop."
      exit 0
    fi
    write_status "partial" "$loop" "status complete but checks failed"
    echo "Status says complete, but checks failed." >&2
    exit 1
  fi

  if [[ "$current_fingerprint" == "$previous_fingerprint" ]]; then
    if checks_pass; then
      write_status "stopped" "$loop" "no changes after loop and checks passed"
      echo "Stopped after loop $loop: no changes."
      exit 0
    fi
    write_status "blocked" "$loop" "no changes after loop and checks failed"
    echo "Stopped after loop $loop: no changes and checks failed." >&2
    exit 1
  fi

  previous_fingerprint="$current_fingerprint"
done

if checks_pass; then
  write_status "max_loop_reached" "$MAX_LOOPS" "max loop reached and checks passed"
  echo "Reached MAX_LOOPS=$MAX_LOOPS."
  exit 0
fi

write_status "blocked" "$MAX_LOOPS" "max loop reached and checks failed"
echo "Reached MAX_LOOPS=$MAX_LOOPS and checks failed." >&2
exit 1
