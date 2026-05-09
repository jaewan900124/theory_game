import openai

from .llm import LLM
from .utils import wrap_prompt


class GPT4(LLM):
    def __init__(self, **kwargs) -> None:
        self.version = kwargs["version"]
        self.cli = openai.Client(
            api_key=kwargs["api_key"],
            base_url=kwargs["base_url"],
            organization=kwargs.get("organization")
        )
        self.context = []

    def __str__(self) -> str:
        return self.version

    def reset(self):
        self.context = []

    def set_context(self, context, role: str = None):
        if self.version[:2] == "o1" and role == "system": return
        self.context = context if role is None else [wrap_prompt(context, role)]

    def invoke(self, message: str, **kwargs):
        wrapped_message = wrap_prompt(message)
        response = self.cli.chat.completions.create(
            model=self.version,
            messages=[*self.context, wrapped_message],
            temperature=0 if self.version[:2] != "o1" else 1
        )
        return response.choices[0].message.content