from dataclasses import dataclass, field
import re
from typing import Any, Dict, List

from api.classes import Action, Agent, AvailableActions, Observation, Rules
from agents.action_parser import (
    action_feedback_message,
    parse_action_response_with_metadata,
)
from agents.backends import generate_completion
from prompts.gamebench_state_adapter import normalize_gamebench_state
from prompts.game_profiles import canonical_game_id
from prompts.high_distill import build_high_distill_prompt
from prompts.high_reasoning import build_high_reasoning_prompt


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()


@dataclass
class TheoryPromptAgent(Agent):
    agent_type_id: str = "theory_prompt"
    agent_mode: str = "high_reasoning"
    backend: str = "ollama"
    model_name: str = "qwen3:14b"
    system_message: str = "Choose the legal action that best advances your chance of winning."
    temperature: float = 0.2
    max_tokens: int = 2048
    timeout: int = 120
    response_retries: int = 3
    base_url: str = None
    api_key: str = None
    transparent_reasoning: bool = False
    prompt_output_mode: str = "compact"
    traces: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        backend_slug = _slug(self.backend)
        model_slug = _slug(self.model_name)
        mode_slug = _slug(self.agent_mode)
        self.agent_type_id = f"theory_{mode_slug}_{backend_slug}_{model_slug}"

    def print(self, *args, **kwargs):
        if self.transparent_reasoning:
            print(self.agent_type_id, *args, **kwargs)

    def _messages_for_state(self, state: Dict[str, Any]):
        if self.agent_mode == "high_reasoning":
            messages = build_high_reasoning_prompt(
                state, output_mode=self.prompt_output_mode
            )
        elif self.agent_mode == "high_distill":
            messages = build_high_distill_prompt(
                state, output_mode=self.prompt_output_mode
            )
        else:
            raise ValueError(f"Unsupported agent_mode: {self.agent_mode}")
        if self.system_message:
            messages[0]["content"] = self.system_message + "\n\n" + messages[0]["content"]
        return messages

    def take_action(
        self,
        rules: Rules,
        observation: Observation,
        available_actions: AvailableActions,
        show_state: bool,
    ) -> Action:
        if observation.image is not None:
            raise ValueError(
                f"{self.agent_type_id} supports text-only observations in v1."
            )

        state = normalize_gamebench_state(
            game_id=canonical_game_id(_slug(getattr(rules, "title", "game"))),
            rules=rules,
            observation=observation,
            available_actions=available_actions,
        )
        messages = self._messages_for_state(state)
        valid_predefined = state["predefined_actions"]
        valid_openended = state["openended_actions"]
        require_field_application = self.prompt_output_mode == "debug"

        last_error = None
        raw_response = ""
        for _ in range(self.response_retries):
            completion = generate_completion(
                self.backend,
                messages=messages,
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                base_url=self.base_url,
                api_key=self.api_key,
                json_mode=True,
            )
            raw_response = completion["content"]
            self.print("response:", raw_response)
            try:
                action, parse_metadata = parse_action_response_with_metadata(
                    raw_response,
                    valid_predefined,
                    valid_openended,
                    profile=state.get("profile"),
                    allow_fallback=False,
                    require_field_application=require_field_application,
                )
                self.traces.append(
                    {
                        "mode": self.agent_mode,
                        "prompt_output_mode": self.prompt_output_mode,
                        "backend": self.backend,
                        "model_name": self.model_name,
                        "observation": state["observation_text"],
                        "prompt_context": state.get("prompt_context"),
                        "messages": messages,
                        "raw_response": raw_response,
                        "parsed_response": parse_metadata.get("payload"),
                        "parse": parse_metadata,
                        "action": {
                            "action_id": action.action_id,
                            "openended_response": action.openended_response,
                        },
                    }
                )
                return action
            except ValueError as exc:
                last_error = str(exc)
                messages.append({"role": "assistant", "content": raw_response})
                messages.append(
                    {
                        "role": "user",
                        "content": action_feedback_message(
                            raw_response,
                            valid_predefined,
                            valid_openended,
                            require_field_application=require_field_application,
                        ),
                    }
                )

        fallback, fallback_parse_metadata = parse_action_response_with_metadata(
            '{"selected_action": "", "openended_response": null}',
            valid_predefined,
            valid_openended,
            profile=state.get("profile"),
            allow_fallback=True,
            require_field_application=False,
        )
        self.traces.append(
            {
                "mode": self.agent_mode,
                "prompt_output_mode": self.prompt_output_mode,
                "backend": self.backend,
                "model_name": self.model_name,
                "observation": state["observation_text"],
                "prompt_context": state.get("prompt_context"),
                "messages": messages,
                "raw_response": raw_response,
                "error": last_error,
                "parsed_response": fallback_parse_metadata.get("payload"),
                "parse": fallback_parse_metadata,
                "action": {
                    "action_id": fallback.action_id,
                    "openended_response": fallback.openended_response,
                },
            }
        )
        return fallback
