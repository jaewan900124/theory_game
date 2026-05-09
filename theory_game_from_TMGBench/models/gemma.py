from openai import OpenAI

from .llm import LLM
from .utils import wrap_prompt


class Gemma(LLM):
    def __init__(self, **kwargs):
        self.version = kwargs["version"]
        self.cli = OpenAI(
            api_key=kwargs["api_key"],
            base_url=kwargs["base_url"]
        )
        self.context = []

    def __str__(self) -> str:
        return self.version.split("/")[-1]

    def reset(self):
        self.context = []

    def set_context(self, context, role: str = None):
        self.context = context if role is None else [wrap_prompt(context, "system")]

    def invoke(self, message: str, **kwargs):
        wrapped_message = wrap_prompt(message)
        response = self.cli.chat.completions.create(
            model=self.version,
            messages=[*self.context, wrapped_message],
            temperature=0,
            max_tokens=1024,
            extra_body={"think": False, "options": {"num_ctx": 4096}},
        )
        return response.choices[0].message.content or ""
