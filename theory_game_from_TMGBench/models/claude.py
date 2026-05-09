import anthropic

from .llm import LLM
from .utils import wrap_prompt


class Claude(LLM):
    def __init__(self, **kwargs):
        self.version = kwargs["version"]
        self.cli = anthropic.Anthropic(
            api_key=kwargs["api_key"],
            base_url=kwargs["base_url"],
        )
        self.context = []
        self.system_message = ""

    def __str__(self) -> str:
        return self.version

    def reset(self):
        self.context = []
        self.system_message = ""

    def set_context(self, context, role: str = None):
        if type(context) == str:
            self.context = []
            self.system_message = context
        else:
            if context[0]["role"] == "system":
                self.system_message = context[0]["content"]
                self.context = context[1:]
            else:
                self.context = context

    def invoke(self, message: str):
        wrapped_message = wrap_prompt(message)

        response = self.cli.messages.create(
            model=self.version,
            max_tokens=4096,
            system=self.system_message,
            messages=[*self.context, wrapped_message],
            temperature=0
        )
        return response.content[0].text