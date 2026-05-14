from dataclasses import dataclass, field
import ast
import base64
from io import BytesIO
import json
import re
from typing import Any, Dict, List, Optional

from api.classes import Action, Agent, AvailableActions, Observation, Rules
from agents.backends import generate_completion


ACTION_FORMAT_INSTRUCTIONS_NO_OPENENDED = """\
Return actions in json with the following keys.
{
    "action": str,
}
"""

ACTION_FORMAT_INSTRUCTIONS_WITH_OPENENDED = """\
Return actions in json with the following keys.
{
    "action": str,
    "openended_response": Optional[str],
}
Include the openended response only if you have chosen an openended action.
"""


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()


def _extract_json_blob(raw_text: str) -> str:
    text = (raw_text or "").strip()
    fenced = _JSON_BLOCK_RE.search(text)
    if fenced:
        return fenced.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def _load_json_like(raw_text: str) -> Dict[str, Any]:
    blob = _extract_json_blob(raw_text)
    try:
        payload = json.loads(blob)
    except json.JSONDecodeError:
        try:
            payload = ast.literal_eval(blob)
        except (ValueError, SyntaxError) as exc:
            raise ValueError(f"Could not parse model output as JSON: {raw_text}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Model output is not a JSON object: {raw_text}")
    return payload


def _first_action(available_actions: AvailableActions) -> Optional[str]:
    for action_id in available_actions.predefined:
        return action_id
    for action_id in available_actions.openended:
        return action_id
    return None


def _action_details(available_actions: AvailableActions, action_id: str) -> str:
    predefined = available_actions.predefined.get(action_id)
    openended = available_actions.openended.get(action_id)
    return " ".join(part for part in [predefined, openended] if part)


@dataclass
class BasicPromptAgent(Agent):
    agent_type_id: str = "basic_prompt"
    backend: str = "ollama"
    model_name: str = "qwen3:8b"
    system_message: str = (
        "You are an agent playing a game. Select the action that maximizes "
        "your probability of winning."
    )
    temperature: float = 1.0
    max_tokens: int = 512
    timeout: int = 180
    response_retries: int = 3
    base_url: str = None
    api_key: str = None
    transparent_reasoning: bool = False
    traces: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        backend_slug = _slug(self.backend)
        model_slug = _slug(self.model_name)
        self.agent_type_id = f"basic_{backend_slug}_{model_slug}"

    def print(self, *args, **kwargs):
        if self.transparent_reasoning:
            print(self.agent_type_id, *args, **kwargs)

    def _format_prompt(
        self,
        rules: Rules,
        observation: Observation,
        available_actions: AvailableActions,
        details_dict: Dict[str, str],
    ) -> str:
        valid_actions = []
        prompt = (
            f"You are playing a game called {rules.title}. "
            f"The rules are as follows:\n{rules.summary}\n"
        )
        if rules.additional_details is not None:
            prompt += (
                "The following are headings with additional information about "
                "the rules that you can expand by taking the action "
                "Explain(<heading key>).\n"
            )
            prompt += json.dumps(details_dict, indent=4)

        prompt += (
            "\n# Observation\n"
            "The following describes the current state of the game:\n"
            f"{observation.text}\n"
        )
        if observation.image is not None:
            buffered = BytesIO()
            observation.image.save(buffered, format="JPEG")
            encoded = base64.b64encode(buffered.getvalue()).decode("ascii")
            prompt += (
                "\nAn image observation was also provided, but this text-only "
                "agent cannot inspect images directly. Use the textual "
                "observation above.\n"
                f"[image/jpeg base64 omitted, {len(encoded)} chars]\n"
            )

        prompt += "\n# Actions\n"
        prompt += f"{available_actions.instructions}\n"
        if available_actions.openended:
            prompt += ACTION_FORMAT_INSTRUCTIONS_WITH_OPENENDED
            prompt += "The following are openended actions you can take\n"
            prompt += str(list(available_actions.openended.keys())) + "\n"
            valid_actions += list(available_actions.openended)
        else:
            prompt += ACTION_FORMAT_INSTRUCTIONS_NO_OPENENDED

        if available_actions.predefined:
            prompt += "The following are predefined actions you can take:\n"
            prompt += str(list(available_actions.predefined)) + "\n"
            valid_actions += list(available_actions.predefined)

        if any(
            available_actions.predefined.get(action) is not None
            or available_actions.openended.get(action)
            for action in valid_actions
        ):
            prompt += (
                "Return the action Explain(<action>) to receive additional "
                "info about what any of the above actions do.\n"
            )

        prompt += (
            "\nTo summarize, if you choose a predefined action, you must "
            "return json with an 'action' key which contains one of the "
            "following valid actions:\n"
        )
        prompt += str(list(available_actions.predefined))
        prompt += (
            "\nOr if you choose an openended action, you must return json "
            "with an 'action' key which contains one of the following valid "
            "actions and an 'openended_response' key which contains your "
            "response to the prompt:\n"
        )
        prompt += str(list(available_actions.openended))
        prompt += "\nReturn valid JSON only."
        return prompt

    def _completion(self, messages):
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
        return completion["content"]

    def take_action(
        self,
        rules: Rules,
        observation: Observation,
        available_actions: AvailableActions,
        show_state: bool,
    ) -> Action:
        if not available_actions.predefined and not available_actions.openended:
            raise ValueError("No actions are available.")

        details_dict = {}
        if rules.additional_details is not None:
            details_dict = {
                f"H{i + 1}": topic for i, topic in enumerate(rules.additional_details)
            }

        messages = [{"role": "system", "content": self.system_message}]
        messages.append(
            {
                "role": "user",
                "content": self._format_prompt(
                    rules, observation, available_actions, details_dict
                ),
            }
        )

        valid_actions = set(available_actions.predefined) | set(
            available_actions.openended
        )
        raw_response = ""
        last_error = None

        for _ in range(self.response_retries):
            raw_response = self._completion(messages)
            messages.append({"role": "assistant", "content": raw_response})
            self.print("response:", raw_response)

            try:
                payload = _load_json_like(raw_response)
                selected_action = payload["action"]
            except Exception as exc:
                last_error = str(exc)
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your previous response was invalid. Return JSON "
                            "only with an 'action' key, and include "
                            "'openended_response' if you choose an openended "
                            "action."
                        ),
                    }
                )
                continue

            if (
                selected_action in available_actions.openended
                and "openended_response" not in payload
            ):
                last_error = "Openended action did not include openended_response."
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "You chose an openended action, so your JSON must "
                            "have an 'openended_response' key."
                        ),
                    }
                )
                continue

            explain = re.findall(r"Explain\((H\d+)\)", selected_action)
            if explain:
                heading = explain[0]
                topic = details_dict.get(heading)
                if topic is None:
                    last_error = f"Invalid rule explanation heading: {heading}"
                    messages.append(
                        {
                            "role": "user",
                            "content": "This is an invalid Explain action.",
                        }
                    )
                    continue
                messages.append(
                    {
                        "role": "user",
                        "content": str(rules.additional_details.get(topic, "")),
                    }
                )
                continue

            explain = re.findall(r"Explain\((.+)\)", selected_action)
            if explain:
                action_id = explain[0]
                desc = _action_details(available_actions, action_id)
                if not desc:
                    last_error = f"Invalid action explanation target: {action_id}"
                    messages.append(
                        {
                            "role": "user",
                            "content": "This is an invalid Explain action.",
                        }
                    )
                    continue
                messages.append({"role": "user", "content": desc})
                continue

            if selected_action in valid_actions:
                openended_response = payload.get("openended_response")
                if selected_action not in available_actions.openended:
                    openended_response = None
                elif openended_response is None:
                    openended_response = ""
                elif not isinstance(openended_response, str):
                    openended_response = str(openended_response)

                action = Action(
                    action_id=selected_action,
                    openended_response=openended_response,
                )
                self.traces.append(
                    {
                        "backend": self.backend,
                        "model_name": self.model_name,
                        "observation": str(observation.text),
                        "messages": messages,
                        "raw_response": raw_response,
                        "parsed_response": payload,
                        "action": {
                            "action_id": action.action_id,
                            "openended_response": action.openended_response,
                        },
                    }
                )
                return action

            last_error = f"Invalid action: {selected_action}"
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"{selected_action} is not one of the valid actions. "
                        "As a reminder, the valid actions are as follows:\n"
                        f"{str(list(valid_actions))}\n"
                        "Please return JSON with the key 'action' and "
                        "optionally 'openended_response'."
                    ),
                }
            )

        self.traces.append(
            {
                "backend": self.backend,
                "model_name": self.model_name,
                "observation": str(observation.text),
                "messages": messages,
                "raw_response": raw_response,
                "error": last_error,
                "fallback_used": True,
                "action": {
                    "action_id": None,
                    "openended_response": None,
                },
            }
        )
        return Action(action_id=None)
