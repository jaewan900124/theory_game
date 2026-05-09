import random

import openai

from .llm import LLM
from .utils import wrap_prompt


class Random(LLM):
    def __init__(self, **kwargs) -> None:
        pass

    def __str__(self) -> str:
        return "random-single_choice"

    def reset(self):
        pass

    def set_context(self, context, role: str = None):
        pass

    def invoke(self, message: str, **kwargs):
        answer = random.choice([
            '[("A1", "B1")]', '[("A1", "B2")]', '[("A2", "B1")]', '[("A2", "B2")]'
        ])
        return f"""```python\nanswer = {answer}\n```"""