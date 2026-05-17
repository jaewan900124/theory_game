import json
import os
import urllib.request


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _env_int(name):
    value = os.environ.get(name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def generate_ollama(
    *,
    messages,
    model_name,
    temperature=0.2,
    max_tokens=512,
    timeout=120,
    base_url=None,
    json_mode=True,
):
    endpoint = (base_url or "http://127.0.0.1:11434").rstrip("/")
    if endpoint.endswith("/v1"):
        endpoint = endpoint[:-3]
    endpoint = endpoint + "/api/chat"
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
        "think": _env_bool("OLLAMA_THINK", False),
    }
    num_ctx = _env_int("OLLAMA_NUM_CTX")
    if num_ctx is not None:
        payload["options"]["num_ctx"] = num_ctx
    if json_mode:
        payload["format"] = "json"

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return {
        "content": body.get("message", {}).get("content", ""),
        "prompt_tokens": body.get("prompt_eval_count", 0),
        "completion_tokens": body.get("eval_count", 0),
        "raw": body,
    }
