import os

import openai

import api.util as util


def _resolve_api_key(api_key=None):
    if api_key:
        return api_key
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        return env_key
    return util.load_json("credentials.json")["openai_api_key"]


def generate_openai(
    *,
    messages,
    model_name,
    temperature=0.2,
    max_tokens=512,
    timeout=120,
    base_url=None,
    api_key=None,
    json_mode=True,
):
    client_kwargs = {"api_key": _resolve_api_key(api_key)}
    if base_url:
        client_kwargs["base_url"] = base_url.rstrip("/") + "/"
    client = openai.Client(**client_kwargs)
    kwargs = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": timeout,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**kwargs)
    choice = response.choices[0].message.content
    usage = response.usage
    return {
        "content": choice or "",
        "prompt_tokens": getattr(usage, "prompt_tokens", 0),
        "completion_tokens": getattr(usage, "completion_tokens", 0),
        "raw": response,
    }
