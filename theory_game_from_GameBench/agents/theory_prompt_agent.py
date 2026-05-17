from dataclasses import dataclass, field
import json
import re
from typing import Any, Dict, List

from api.classes import Action, Agent, AvailableActions, Observation, Rules
from agents.action_parser import (
    action_feedback_message,
    _load_json_like,
    parse_action_response_with_metadata,
)
from agents.backends import generate_completion
from agents.trace_utils import action_trace_fields, format_action_id_reference
from prompts.gamebench_state_adapter import normalize_gamebench_state
from prompts.game_profiles import canonical_game_id
from prompts.field_program import build_field_program_prompt
from prompts.field_rationale import build_field_rationale_prompt
from prompts.high_distill import build_high_distill_prompt
from prompts.high_reasoning import build_high_reasoning_prompt
from prompts.theory_fields import (
    field_register_for_prompt,
    required_fields_for_prompt,
    theory_mapping_for_game,
)


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
    enable_field_checker: bool = False
    checker_backend: str = "ollama"
    checker_model_name: str = None
    checker_base_url: str = None
    checker_api_key: str = None
    checker_temperature: float = 0.2
    checker_max_tokens: int = 1024
    checker_timeout: int = 240
    traces: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        backend_slug = _slug(self.backend)
        model_slug = _slug(self.model_name)
        mode_slug = _slug(self.agent_mode)
        self.agent_type_id = f"theory_{mode_slug}_{backend_slug}_{model_slug}"
        if self.enable_field_checker:
            checker_backend_slug = _slug(self.checker_backend)
            checker_model_slug = _slug(self.checker_model_name or "checker")
            self.agent_type_id += f"_checked_by_{checker_backend_slug}_{checker_model_slug}"

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

    def _field_value_repair_messages_for_state(
        self,
        state: Dict[str, Any],
        draft_payload: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        mapping = theory_mapping_for_game(state.get("game_id"))
        valid_fields = field_register_for_prompt(
            mapping, state.get("prompt_context")
        )
        required_fields = []
        if self.prompt_output_mode == "required_field_analysis":
            required_fields = required_fields_for_prompt(
                state.get("game_id"), state.get("prompt_context")
            )
        field_selection_rule = (
            "- used_fields must exactly equal # Required Field Set, in the same order.\n"
            "- Do not add optional fields or remove required fields."
            if required_fields
            else "- Keep 2 to 6 fields."
        )
        field_count_rule = (
            f"- Return exactly {len(required_fields)} fields."
            if required_fields
            else "- Keep 2 to 6 fields."
        )
        prompt = f"""You are a field-selection and field-value repair agent for a game-playing field-rationale agent.

Your job is to check and, if needed, repair only the draft used_fields and field_analysis.

Rules:
- Use only the current observation, rules summary, action instructions, and available action details.
- Do not choose or change the action.
- Do not invent new game state.
- Select fields only from # Field Register.
- Check field selection first: fields should be the smallest sufficient set that materially affects the current action choice.
- Mark field selection as repaired when a selected field is irrelevant, redundant, unavailable for the current action context, or when an important decision-critical field is missing.
- Keep each original field when it is valid, grounded, and useful.
- Repair field_analysis.value when it states a concrete false fact, misses a required current-state constraint, invents unavailable cards/resources/roles, misreads a visible score, or applies the rule objective backwards.
{field_count_rule}
{field_selection_rule}
- Each field_analysis entry must have the same field name and order as used_fields.
- Each field_analysis.value must be one concise sentence.

Return valid JSON only with these keys:
{{
  "used_fields": ["2 to 6 field names"],
  "field_analysis": [
    {{"field": "same field name as used_fields entry", "value": "corrected grounded value"}}
  ],
  "field_selection_verdict": "keep or repaired",
  "field_selection_reason": "one short sentence naming why the selected fields are sufficient or what was repaired",
  "field_value_verdict": "keep or repaired",
  "field_value_reason": "one short sentence naming the key grounded fact or repair"
}}

# Field Register
{json.dumps(valid_fields, ensure_ascii=False, indent=2)}

# Required Field Set
{json.dumps(required_fields, ensure_ascii=False, indent=2)}

# Rules Summary
{state.get("rules_summary", "")}

# Action Instructions
{state.get("action_instructions", "")}

# Observation
{state.get("observation_text", "")}

# Available Action Details
Predefined actions:
{json.dumps(state["predefined_actions"], ensure_ascii=False, indent=2)}

Openended actions:
{json.dumps(state["openended_actions"], ensure_ascii=False, indent=2)}

# Draft Field Rationale JSON
{json.dumps(draft_payload, ensure_ascii=False, indent=2)}
"""
        return [
            {
                "role": "system",
                "content": (
                    "You repair game-playing field values and return only "
                    "the corrected field rationale JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ]

    def _checker_messages_for_state(
        self,
        state: Dict[str, Any],
        draft_response: str,
        draft_payload: Dict[str, Any],
        draft_action: Action,
    ) -> List[Dict[str, str]]:
        valid_predefined = list(state["predefined_actions"].keys())
        valid_openended = list(state["openended_actions"].keys())
        action_reference = ""
        if self.include_action_id_reference:
            action_reference = format_action_id_reference(
                state["predefined_actions"],
                state["openended_actions"],
                game_id=state.get("game_id"),
                observation_text=state.get("observation_text", ""),
                action_instructions=state.get("action_instructions", ""),
            )
        action_reference_block = (
            f"\n# Action ID Reference\n{action_reference}\n"
            if action_reference
            else ""
        )
        draft_action_meaning = (
            state["predefined_actions"].get(draft_action.action_id)
            or state["openended_actions"].get(draft_action.action_id)
            or ""
        )
        prompt = f"""You are an action checker for a game-playing field-rationale agent.

The field/value repair agent has already checked and repaired the field_analysis.
Your job is only to check whether the draft action matches the checked field/value analysis and the available action details.

Default to keeping the draft action.

Rules:
- Action ids are opaque labels. Numeric ids such as "0", "1", "2", or "3" have no meaning by themselves.
- Use # Available Action Details only to map action ids to meanings.
- Treat the checked field_analysis as the fixed evidence for the action decision.
- Do not rewrite fields or field values.
- Do not choose a better action just because it also seems reasonable.
- Correct the action only when the draft action is illegal, impossible, malformed for the selected action, directly contradicts the checked field/value analysis, or is clearly dominated by another legal action under the checked field/value analysis.
- Keep the draft action if several legal actions are plausibly close in value.
- If the chosen action is openended, keep or minimally adjust openended_response so it matches the chosen action and the required response format.

Return valid JSON only with these keys:
{{
  "action": "one valid action id",
  "openended_response": "only if the chosen action is openended",
  "action_verdict": "keep or corrected",
  "checker_verdict": "keep or corrected",
  "checker_reason": "one short sentence naming the action rationale or correction"
}}

Valid predefined actions: {valid_predefined}
Valid openended actions: {valid_openended}

# Rules Summary
{state.get("rules_summary", "")}

# Action Instructions
{state.get("action_instructions", "")}

# Observation
{state.get("observation_text", "")}

# Available Action Details
Predefined actions:
{json.dumps(state["predefined_actions"], ensure_ascii=False, indent=2)}

Openended actions:
{json.dumps(state["openended_actions"], ensure_ascii=False, indent=2)}
{action_reference_block}

# Checked Field Rationale JSON
{json.dumps(draft_payload, ensure_ascii=False, indent=2)}

# Draft Parsed Action
{json.dumps(
    {
        "action": draft_action.action_id,
        "meaning": draft_action_meaning,
        "openended_response": draft_action.openended_response,
    },
    ensure_ascii=False,
    indent=2,
)}
"""
        return [
            {
                "role": "system",
                "content": (
                    "You verify a game-playing field rationale and return only "
                    "the final legal action JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ]

    def _run_field_checker(
        self,
        state: Dict[str, Any],
        draft_response: str,
        draft_parse_metadata: Dict[str, Any],
        draft_action: Action,
    ) -> tuple[Action, Dict[str, Any]]:
        checker_model = self.checker_model_name or self.model_name
        draft_payload = draft_parse_metadata.get("payload") or {}
        field_value_trace = self._run_field_value_repair(
            state,
            draft_payload,
            checker_model,
        )
        checked_field_payload = field_value_trace.get("repaired_payload") or draft_payload
        checker_messages = self._checker_messages_for_state(
            state,
            draft_response,
            checked_field_payload,
            draft_action,
        )
        valid_predefined = state["predefined_actions"]
        valid_openended = state["openended_actions"]
        attempts = []
        last_error = None
        for _ in range(self.response_retries):
            completion = generate_completion(
                self.checker_backend,
                messages=checker_messages,
                model_name=checker_model,
                temperature=self.checker_temperature,
                max_tokens=self.checker_max_tokens,
                timeout=self.checker_timeout,
                base_url=self.checker_base_url,
                api_key=self.checker_api_key,
                json_mode=True,
            )
            raw_checker_response = completion["content"]
            self.print("checker response:", raw_checker_response)
            try:
                checked_action, checked_parse_metadata = parse_action_response_with_metadata(
                    raw_checker_response,
                    valid_predefined,
                    valid_openended,
                    profile=state.get("profile"),
                    allow_fallback=False,
                    require_field_application=False,
                )
                return checked_action, {
                    "enabled": True,
                    "backend": self.checker_backend,
                    "model_name": checker_model,
                    "base_url": self.checker_base_url,
                    "field_value_repair": field_value_trace,
                    "messages": checker_messages,
                    "raw_response": raw_checker_response,
                    "parsed_response": checked_parse_metadata.get("payload"),
                    "parse": checked_parse_metadata,
                    "action_changed": (
                        checked_action.action_id != draft_action.action_id
                        or checked_action.openended_response != draft_action.openended_response
                    ),
                    "fallback_used": False,
                    "attempts": attempts,
                }
            except ValueError as exc:
                last_error = str(exc)
                attempts.append(
                    {
                        "raw_response": raw_checker_response,
                        "error": last_error,
                    }
                )
                checker_messages.append(
                    {"role": "assistant", "content": raw_checker_response}
                )
                checker_messages.append(
                    {
                        "role": "user",
                        "content": action_feedback_message(
                            raw_checker_response,
                            valid_predefined,
                            valid_openended,
                            require_field_application=False,
                        ),
                    }
                )

        return draft_action, {
            "enabled": True,
            "backend": self.checker_backend,
            "model_name": checker_model,
            "base_url": self.checker_base_url,
            "field_value_repair": field_value_trace,
            "messages": checker_messages,
            "error": last_error,
            "fallback_used": True,
            "fallback_reason": "checker_failed_after_retries_kept_draft_action",
            "attempts": attempts,
        }

    def _run_field_value_repair(
        self,
        state: Dict[str, Any],
        draft_payload: Dict[str, Any],
        checker_model: str,
    ) -> Dict[str, Any]:
        mapping = theory_mapping_for_game(state.get("game_id"))
        valid_fields = set(
            field_register_for_prompt(mapping, state.get("prompt_context"))
        )
        required_fields = []
        if self.prompt_output_mode == "required_field_analysis":
            required_fields = required_fields_for_prompt(
                state.get("game_id"), state.get("prompt_context")
            )
        repair_messages = self._field_value_repair_messages_for_state(
            state,
            draft_payload,
        )
        attempts = []
        last_error = None
        for _ in range(self.response_retries):
            completion = generate_completion(
                self.checker_backend,
                messages=repair_messages,
                model_name=checker_model,
                temperature=self.checker_temperature,
                max_tokens=self.checker_max_tokens,
                timeout=self.checker_timeout,
                base_url=self.checker_base_url,
                api_key=self.checker_api_key,
                json_mode=True,
            )
            raw_repair_response = completion["content"]
            self.print("field value repair response:", raw_repair_response)
            try:
                repaired_payload = _load_json_like(raw_repair_response)
                repaired_used_fields = repaired_payload.get("used_fields")
                repaired_field_analysis = repaired_payload.get("field_analysis")
                if not isinstance(repaired_used_fields, list):
                    raise ValueError("field repair did not return used_fields list")
                if not isinstance(repaired_field_analysis, list):
                    raise ValueError("field repair did not return field_analysis list")
                if required_fields:
                    if repaired_used_fields != required_fields:
                        raise ValueError(
                            "field repair used_fields must exactly match required fields: "
                            f"{required_fields}"
                        )
                elif len(repaired_used_fields) < 2 or len(repaired_used_fields) > 6:
                    raise ValueError("field repair must return 2 to 6 used_fields")
                invalid_fields = [
                    field for field in repaired_used_fields if field not in valid_fields
                ]
                if invalid_fields:
                    raise ValueError(
                        f"field repair returned invalid fields: {invalid_fields}"
                    )
                if len(repaired_used_fields) != len(repaired_field_analysis):
                    raise ValueError("field repair used_fields and field_analysis length differ")
                for index, analysis in enumerate(repaired_field_analysis):
                    if not isinstance(analysis, dict):
                        raise ValueError("field_analysis entries must be objects")
                    if analysis.get("field") != repaired_used_fields[index]:
                        raise ValueError("field_analysis fields must match used_fields order")
                    value = analysis.get("value")
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError("field_analysis.value must be a non-empty string")

                checked_payload = dict(draft_payload)
                checked_payload["used_fields"] = repaired_used_fields
                checked_payload["field_analysis"] = repaired_field_analysis
                return {
                    "enabled": True,
                    "backend": self.checker_backend,
                    "model_name": checker_model,
                    "base_url": self.checker_base_url,
                    "messages": repair_messages,
                    "raw_response": raw_repair_response,
                    "parsed_response": repaired_payload,
                    "repaired_payload": checked_payload,
                    "field_selection_changed": (
                        repaired_used_fields != draft_payload.get("used_fields")
                    ),
                    "field_values_changed": (
                        repaired_field_analysis != draft_payload.get("field_analysis")
                    ),
                    "fallback_used": False,
                    "attempts": attempts,
                }
            except ValueError as exc:
                last_error = str(exc)
                attempts.append(
                    {
                        "raw_response": raw_repair_response,
                        "error": last_error,
                    }
                )
                repair_messages.append(
                    {"role": "assistant", "content": raw_repair_response}
                )
                repair_messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your previous response was invalid. Return valid JSON "
                            "with used_fields, field_analysis, field_value_verdict, "
                            "and field_value_reason only."
                        ),
                    }
                )

        return {
            "enabled": True,
            "backend": self.checker_backend,
            "model_name": checker_model,
            "base_url": self.checker_base_url,
            "messages": repair_messages,
            "error": last_error,
            "fallback_used": True,
            "fallback_reason": "field_value_repair_failed_kept_draft_fields",
            "attempts": attempts,
            "repaired_payload": draft_payload,
            "field_selection_changed": False,
            "field_values_changed": False,
        }

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
            required_fields = []
            if self.prompt_output_mode == "required_field_analysis":
                required_fields = required_fields_for_prompt(
                    state.get("game_id"), state.get("prompt_context")
                )
            field_schema = {
                "valid_fields": valid_fields,
                "required_fields": required_fields,
                "min_fields": len(required_fields) if required_fields else 2,
                "max_fields": len(required_fields) if required_fields else 6,
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
                final_action = action
                checker_trace = {"enabled": False}
                if self.enable_field_checker:
                    final_action, checker_trace = self._run_field_checker(
                        state,
                        raw_response,
                        parse_metadata,
                        action,
                    )
                trace = {
                    "mode": self.agent_mode,
                    "prompt_output_mode": self.prompt_output_mode,
                    "backend": self.backend,
                    "model_name": self.model_name,
                    "field_checker": checker_trace,
                    "observation": state["observation_text"],
                    "prompt_context": state.get("prompt_context"),
                    "messages": messages,
                    "raw_response": raw_response,
                    "parsed_response": parse_metadata.get("payload"),
                    "parse": parse_metadata,
                    "draft_action": {
                        "action_id": action.action_id,
                        "openended_response": action.openended_response,
                    },
                    "action": {
                        "action_id": final_action.action_id,
                        "openended_response": final_action.openended_response,
                    },
                }
                trace.update(
                    action_trace_fields(
                        available_actions,
                        final_action.action_id,
                        game_id=state.get("game_id"),
                        observation_text=state["observation_text"],
                        action_instructions=state["action_instructions"],
                    )
                )
                self.traces.append(trace)
                return final_action
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
