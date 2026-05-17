from dataclasses import dataclass, field
import re
from typing import Any, Dict, List

from api.classes import Action, Agent, AvailableActions, Observation, Rules
from agents.action_parser import (
    action_feedback_message,
    parse_action_response_with_metadata,
)
from agents.backends import generate_completion
from agents.trace_utils import action_trace_fields
from prompts.gamebench_state_adapter import normalize_gamebench_state
from prompts.game_profiles import canonical_game_id
from prompts.field_program import build_field_program_prompt
from prompts.field_rationale import build_field_rationale_prompt
from prompts.high_distill import build_high_distill_prompt
from prompts.high_reasoning import build_high_reasoning_prompt
from prompts.theory_fields import field_register_for_prompt, theory_mapping_for_game


BASE_SYSTEM_MESSAGE = (
    "You are an agent playing a game. Select the action that maximizes "
    "your probability of winning."
)
DEFAULT_THEORY_SYSTEM_MESSAGE = "Choose the legal action that best advances your chance of winning."


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
    include_action_id_reference: bool = False
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
        elif self.agent_mode == "field_rationale":
            messages = build_field_rationale_prompt(
                state,
                output_mode=self.prompt_output_mode,
                include_action_id_reference=self.include_action_id_reference,
            )
        elif self.agent_mode == "field_program":
            messages = build_field_program_prompt(
                state, output_mode=self.prompt_output_mode
            )
        elif self.agent_mode == "high_distill":
            messages = build_high_distill_prompt(
                state, output_mode=self.prompt_output_mode
            )
        else:
            raise ValueError(f"Unsupported agent_mode: {self.agent_mode}")
        if self.system_message:
            system_message = self.system_message
            if (
                self.agent_mode == "field_rationale"
                and system_message == DEFAULT_THEORY_SYSTEM_MESSAGE
            ):
                system_message = BASE_SYSTEM_MESSAGE
            if messages[0]["content"]:
                messages[0]["content"] = system_message + "\n\n" + messages[0]["content"]
            else:
                messages[0]["content"] = system_message
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
        field_schema = None
        if self.agent_mode == "field_rationale":
            mapping = theory_mapping_for_game(state.get("game_id"))
            valid_fields = field_register_for_prompt(
                mapping, state.get("prompt_context")
            )
            field_schema = {
                "valid_fields": valid_fields,
                "min_fields": 2,
                "max_fields": 6,
                "require_used_fields": True,
                "require_field_analysis": self.prompt_output_mode != "compact_basis",
                "max_analysis_words": 30,
            }

        last_error = None
        last_field_error = None
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
                    field_schema=field_schema,
                )
                trace = {
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
                trace.update(
                    action_trace_fields(
                        available_actions,
                        action.action_id,
                        game_id=state.get("game_id"),
                        observation_text=state["observation_text"],
                        action_instructions=state["action_instructions"],
                    )
                )
                self.traces.append(trace)
                return action
            except ValueError as exc:
                last_error = str(exc)
                last_field_error = (
                    last_error if field_schema and "field" in last_error else None
                )
                messages.append({"role": "assistant", "content": raw_response})
                messages.append(
                    {
                        "role": "user",
                        "content": action_feedback_message(
                            raw_response,
                            valid_predefined,
                            valid_openended,
                            require_field_application=require_field_application,
                            field_error=last_field_error,
                            valid_fields=(
                                field_schema.get("valid_fields")
                                if field_schema and last_field_error
                                else None
                            ),
                        ),
                    }
                )

        fallback_source = raw_response
        try:
            fallback, fallback_parse_metadata = parse_action_response_with_metadata(
                fallback_source,
                valid_predefined,
                valid_openended,
                profile=state.get("profile"),
                allow_fallback=True,
                require_field_application=False,
            )
        except ValueError:
            fallback_source = '{"selected_action": "", "openended_response": null}'
            fallback, fallback_parse_metadata = parse_action_response_with_metadata(
                fallback_source,
                valid_predefined,
                valid_openended,
                profile=state.get("profile"),
                allow_fallback=True,
                require_field_application=False,
            )
        trace = {
            "mode": self.agent_mode,
            "prompt_output_mode": self.prompt_output_mode,
            "backend": self.backend,
            "model_name": self.model_name,
            "observation": state["observation_text"],
            "prompt_context": state.get("prompt_context"),
            "messages": messages,
            "raw_response": raw_response,
            "fallback_source": fallback_source,
            "error": last_error,
            "field_validation_failed": bool(field_schema and last_field_error),
            "parsed_response": fallback_parse_metadata.get("payload"),
            "parse": fallback_parse_metadata,
            "fallback_used": True,
            "fallback_reason": (
                "action_parsed_after_field_validation_retries"
                if field_schema and last_field_error
                else "valid_action_after_retries"
            ),
            "action": {
                "action_id": fallback.action_id,
                "openended_response": fallback.openended_response,
            },
        }
        trace.update(
            action_trace_fields(
                available_actions,
                fallback.action_id,
                game_id=state.get("game_id"),
                observation_text=state["observation_text"],
                action_instructions=state["action_instructions"],
            )
        )
        self.traces.append(trace)
        return fallback
