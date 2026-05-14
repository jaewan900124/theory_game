from agents.backends.ollama_backend import generate_ollama
from agents.backends.openai_backend import generate_openai


def generate_completion(
    backend: str,
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
    backend_name = (backend or "").strip().lower()
    if backend_name == "ollama":
        return generate_ollama(
            messages=messages,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            base_url=base_url,
            json_mode=json_mode,
        )
    if backend_name == "openai":
        return generate_openai(
            messages=messages,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            api_key=api_key,
            json_mode=json_mode,
        )
    raise ValueError(f"Unsupported backend: {backend}")
