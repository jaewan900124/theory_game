from typing import Union

# common name -> class name
ref = {
    "GPT3.5": "GPT3p5",
    "GPT4": "GPT4",
    "Claude": "Claude",
    "Gemini": "Gemini",
    "Llama2": "Llama2",
    "Llama3": "Llama3",
    "Mistral": "Mistral",
    "DeepSeek": "DeepSeek",
    "Qwen": "Qwen",
    "Gemma": "Gemma",
    "Random": "Random"
}

def tocls(model: str):
    return ref[model]

def wrap_prompt(content: Union[str, list], role: str = "user"):
    if type(content) == str:
        return dict(content=content, role=role)
    else:
        wrapped_content = []
        for sth in content:
            wrapped_content.append(dict(content=sth[0], role="user"))
            wrapped_content.append(dict(content=sth[1], role="assistant"))
        return wrapped_content

def wrap_prompt_gemini(parts: Union[str, list], role: str = "user"):
    if type(parts) == str:
        return dict(parts=[parts], role=role)
    else:
        wrapped_content = []
        for sth in parts:
            wrapped_content.append(dict(parts=[sth[0]], role="user"))
            wrapped_content.append(dict(parts=[sth[1]], role="model"))
        return wrapped_content