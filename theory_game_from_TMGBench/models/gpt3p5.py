import openai

from .llm import LLM
from .utils import wrap_prompt


class GPT3p5(LLM):
    def __init__(self, **kwargs) -> None:
        self.version = kwargs.get("version")
        self.cli = openai.Client(
            api_key=kwargs.get("api_key"),
            base_url=kwargs.get("base_url")
        )
        self.context = []

    def __str__(self) -> str:
        return self.version

    def reset(self):
        self.context = []

    def set_context(self, context, role: str = None):
        self.context = context if role is None else [wrap_prompt(context, role)]

    def invoke(self, message: str, **kwargs):
        wrapped_message = wrap_prompt(message)
        response = self.cli.chat.completions.create(
            model=self.version,
            messages=[*self.context, wrapped_message],
            temperature=0
        )
        return response.choices[0].message.content