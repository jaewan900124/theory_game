
import os
import json
import urllib.request
from pathlib import Path
from langchain.chat_models import ChatOpenAI, ChatAnyscale
from langchain_community.chat_models import ChatOpenAI, ChatAnyscale
from langchain_community.llms import DeepInfra
from langchain.schema import SystemMessage, HumanMessage, AIMessage


def write_to_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)


def _load_dotenv_if_needed(*keys):
    if all(os.environ.get(key) for key in keys):
        return
    for directory in [Path.cwd(), *Path.cwd().parents]:
        env_path = directory / ".env"
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key not in keys or os.environ.get(key):
                continue
            os.environ[key] = value.strip().strip("\"'")
        if all(os.environ.get(key) for key in keys):
            return


def _api_key_from_env(key):
    _load_dotenv_if_needed(key)
    value = os.environ[key]
    # API keys must be a single HTTP header token. This also fixes copied
    # multiline .env values or shell exports with accidental line wrapping.
    value = "".join(value.split())
    os.environ[key] = value
    return value


def chat_ollama(messages, model, temperature, max_tokens, n, timeout, stop, think=None, base_url=None):
    endpoint = (base_url or os.environ["OLLAMA_BASE_URL"]).rstrip("/")
    if endpoint.endswith("/v1"):
        endpoint = endpoint[:-3]
    endpoint = endpoint + "/api/chat"
    if think is None:
        think = os.environ.get("OLLAMA_THINK", "true").lower() not in {
            "0", "false", "no", "off"}

    responses = []
    total_completion_tokens = 0
    total_prompt_tokens = 0
    for _ in range(n):
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": think,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if stop is not None:
            payload["options"]["stop"] = [stop] if isinstance(stop, str) else stop

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        responses.append(body.get("message", {}).get("content", ""))
        total_completion_tokens += body.get("eval_count", 0)
        total_prompt_tokens += body.get("prompt_eval_count", 0)

    return {
        'generations': responses,
        'completion_tokens': total_completion_tokens,
        'prompt_tokens': total_prompt_tokens
    }


def chat_llm(messages, model, temperature, max_tokens, n, timeout, stop, return_tokens=False, chat_seed=0, think=None, base_url=None):
    if base_url or os.environ.get("OLLAMA_BASE_URL"):
        return chat_ollama(messages, model, temperature, max_tokens, n, timeout, stop, think=think, base_url=base_url)
    elif model.__contains__("gpt"):
        iterated_query = False
        chat = ChatOpenAI(model_name=model,
                          openai_api_key=_api_key_from_env("OPENAI_API_KEY"),
                          temperature=temperature,
                          max_tokens=max_tokens,
                          n=n,
                          request_timeout=timeout,
                          )
    elif 'Open-Orca/Mistral-7B-OpenOrca' == model:
        iterated_query = True
        chat = ChatAnyscale(temperature=temperature,
                            anyscale_api_key=_api_key_from_env("ANYSCALE_API_KEY"),
                            max_tokens=max_tokens,
                            n=1,
                            model_name=model,
                            request_timeout=timeout)
    else:
        # deepinfra
        iterated_query = True
        chat = ChatOpenAI(model_name=model,
                          openai_api_key=_api_key_from_env("DEEPINFRA_API_KEY"),
                          temperature=temperature,
                          max_tokens=max_tokens,
                          n=1,
                          request_timeout=timeout,
                          openai_api_base="https://api.deepinfra.com/v1/openai")

    longchain_msgs = []
    for msg in messages:
        if msg['role'] == 'system':
            longchain_msgs.append(SystemMessage(content=msg['content']))
        elif msg['role'] == 'user':
            longchain_msgs.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            longchain_msgs.append(AIMessage(content=msg['content']))
        else:
            raise NotImplementedError
    if n > 1 and iterated_query:
        response_list = []
        total_completion_tokens = 0
        total_prompt_tokens = 0
        for n in range(n):
            generations = chat.generate([longchain_msgs], stop=[
                stop] if stop is not None else None)
            responses = [
                chat_gen.message.content for chat_gen in generations.generations[0]]
            response_list.append(responses[0])
            token_usage = generations.llm_output.get('token_usage', {}) if generations.llm_output else {}
            completion_tokens = token_usage.get('completion_tokens', 0)
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            total_completion_tokens += completion_tokens
            total_prompt_tokens += prompt_tokens
        responses = response_list
        completion_tokens = total_completion_tokens
        prompt_tokens = total_prompt_tokens
    else:
        generations = chat.generate([longchain_msgs], stop=[
            stop] if stop is not None else None)
        responses = [
            chat_gen.message.content for chat_gen in generations.generations[0]]
        token_usage = generations.llm_output.get('token_usage', {}) if generations.llm_output else {}
        completion_tokens = token_usage.get('completion_tokens', 0)
        prompt_tokens = token_usage.get('prompt_tokens', 0)

    return {
        'generations': responses,
        'completion_tokens': completion_tokens,
        'prompt_tokens': prompt_tokens
    }
