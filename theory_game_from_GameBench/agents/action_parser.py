import ast
import json
import re
from typing import Any, Dict, List, Optional

from api.classes import Action


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _extract_json_blob(raw_text: str) -> str:
    text = (raw_text or "").strip()
    fenced = _JSON_BLOCK_RE.search(text)
    if fenced:
        return fenced.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def _load_json_like(raw_text: str) -> Dict[str, Any]:
    blob = _extract_json_blob(raw_text)
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        try:
            value = ast.literal_eval(blob)
        except (ValueError, SyntaxError) as exc:
            raise ValueError(f"Could not parse model output as JSON: {raw_text}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Model output is not a JSON object: {raw_text}")
        return value


def _first_action(predefined: Dict[str, str], openended: Dict[str, str]) -> Optional[str]:
    for action in predefined:
        return action
    for action in openended:
        return action
    return None


def _fallback_openended_response(
    selected_action: str,
    openended: Dict[str, str],
    profile: Optional[Dict[str, Any]],
) -> str:
    if profile:
        action_defaults = profile.get("openended_response_defaults", {})
        if selected_action in action_defaults:
            return action_defaults[selected_action]
    default_response = openended.get(selected_action)
    if isinstance(default_response, str) and default_response.strip():
        return default_response
    return ""


def parse_action_response(
    raw_text: str,
    predefined: Dict[str, str],
    openended: Dict[str, str],
    profile: Optional[Dict[str, Any]] = None,
    allow_fallback: bool = True,
) -> Action:
    action, _ = parse_action_response_with_metadata(
        raw_text,
        predefined,
        openended,
        profile=profile,
        allow_fallback=allow_fallback,
    )
    return action


def parse_action_response_with_metadata(
    raw_text: str,
    predefined: Dict[str, str],
    openended: Dict[str, str],
    profile: Optional[Dict[str, Any]] = None,
    allow_fallback: bool = True,
    require_field_application: bool = True,
) -> tuple[Action, Dict[str, Any]]:
    payload = _load_json_like(raw_text)
    metadata: Dict[str, Any] = {
        "payload": payload,
        "fallback_used": False,
        "fallback_reason": None,
        "selected_action_raw": None,
        "selected_action_final": None,
        "action_type": None,
        "openended_response_fallback_used": False,
        "field_application_present": isinstance(payload.get("field_application"), dict),
        "used_rule": payload.get("used_rule"),
        "used_fields": payload.get("used_fields"),
        "rule_analysis": payload.get("rule_analysis"),
        "field_analysis": payload.get("field_analysis"),
    }
    if require_field_application and not metadata["field_application_present"] and not allow_fallback:
        raise ValueError("Model output did not include the required field_application object.")

    selected_action = (
        payload.get("selected_action")
        or payload.get("action")
        or payload.get("action_id")
    )
    metadata["selected_action_raw"] = selected_action
    if not isinstance(selected_action, str) or not selected_action.strip():
        if not allow_fallback:
            raise ValueError("Model output did not include a non-empty selected_action.")
        fallback = _first_action(predefined, openended)
        if fallback is None:
            raise ValueError("No valid actions are available for fallback.")
        selected_action = fallback
        metadata["fallback_used"] = True
        metadata["fallback_reason"] = "missing_selected_action"
    selected_action = selected_action.strip()

    valid_predefined = set(predefined.keys())
    valid_openended = set(openended.keys())
    valid_actions = valid_predefined | valid_openended
    if selected_action not in valid_actions:
        if not allow_fallback:
            raise ValueError(f"Invalid selected_action: {selected_action}")
        fallback = _first_action(predefined, openended)
        if fallback is None:
            raise ValueError(f"Invalid selected action and no fallback is available: {selected_action}")
        selected_action = fallback
        metadata["fallback_used"] = True
        metadata["fallback_reason"] = "invalid_selected_action"

    action_type = payload.get("action_type")
    if selected_action in valid_openended:
        action_type = "openended"
    elif selected_action in valid_predefined:
        action_type = "predefined"
    metadata["action_type"] = action_type

    openended_response = payload.get("openended_response")
    if action_type == "openended":
        if openended_response is None:
            if not allow_fallback:
                raise ValueError(f"Openended action requires openended_response: {selected_action}")
            openended_response = _fallback_openended_response(selected_action, openended, profile)
            metadata["openended_response_fallback_used"] = True
        elif not isinstance(openended_response, str):
            openended_response = str(openended_response)
    else:
        openended_response = None

    metadata["selected_action_final"] = selected_action
    return Action(action_id=selected_action, openended_response=openended_response), metadata


def action_feedback_message(
    raw_text: str,
    predefined: Dict[str, str],
    openended: Dict[str, str],
    require_field_application: bool = True,
) -> str:
    valid_actions: List[str] = list(predefined.keys()) + list(openended.keys())
    field_application_instruction = (
        "Include the required field_application object that applies the predefined theory fields.\n"
        if require_field_application
        else ""
    )
    return (
        "Your previous response was invalid or incomplete.\n"
        "Return valid JSON only.\n"
        f"Valid actions: {valid_actions}\n"
        f"{field_application_instruction}"
        "Copy one valid action id exactly into 'selected_action'.\n"
        "If you choose an openended action, include an 'openended_response' string."
    )
