import ast
import json
import re
from typing import Any, Dict, List, Optional

from api.classes import Action


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


class FieldValidationError(ValueError):
    pass


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
    field_schema: Optional[Dict[str, Any]] = None,
) -> Action:
    action, _ = parse_action_response_with_metadata(
        raw_text,
        predefined,
        openended,
        profile=profile,
        allow_fallback=allow_fallback,
        field_schema=field_schema,
    )
    return action


def _field_validation_error(payload: Dict[str, Any], field_schema: Dict[str, Any]) -> Optional[str]:
    valid_fields = list(field_schema.get("valid_fields") or [])
    valid_field_set = set(valid_fields)
    min_fields = int(field_schema.get("min_fields", 0))
    max_fields = int(field_schema.get("max_fields", len(valid_fields) or 9999))
    require_used_fields = field_schema.get("require_used_fields", True)
    require_field_analysis = field_schema.get("require_field_analysis", False)
    required_fields = field_schema.get("required_fields") or []

    used_fields = payload.get("used_fields")
    if used_fields is None:
        return "Model output did not include required used_fields." if require_used_fields else None
    if not isinstance(used_fields, list) or not all(isinstance(field, str) for field in used_fields):
        return "used_fields must be a list of field-name strings."
    if len(used_fields) < min_fields or len(used_fields) > max_fields:
        return f"used_fields must contain {min_fields} to {max_fields} fields."
    duplicate_fields = sorted({field for field in used_fields if used_fields.count(field) > 1})
    if duplicate_fields:
        return f"used_fields contains duplicate fields: {duplicate_fields}"
    invalid_fields = [field for field in used_fields if field not in valid_field_set]
    if invalid_fields:
        return f"used_fields contains invalid fields: {invalid_fields}"
    if required_fields and used_fields != required_fields:
        return (
            "used_fields must exactly match the required field set in order: "
            f"{required_fields}"
        )

    field_analysis = payload.get("field_analysis")
    if not require_field_analysis:
        return None
    if not isinstance(field_analysis, list):
        return "field_analysis must be a list with one object per used field."
    if len(field_analysis) != len(used_fields):
        return "field_analysis must contain exactly one object per used_fields entry."
    for index, analysis in enumerate(field_analysis):
        if not isinstance(analysis, dict):
            return "Each field_analysis entry must be an object."
        if analysis.get("field") != used_fields[index]:
            return "field_analysis fields must match used_fields in the same order."
        value = analysis.get("value")
        if not isinstance(value, str) or not value.strip():
            return "Each field_analysis.value must be a non-empty string."
        if len(value.split()) > int(field_schema.get("max_analysis_words", 30)):
            return "Each field_analysis.value must be at most 30 words."
    return None


def parse_action_response_with_metadata(
    raw_text: str,
    predefined: Dict[str, str],
    openended: Dict[str, str],
    profile: Optional[Dict[str, Any]] = None,
    allow_fallback: bool = True,
    require_field_application: bool = True,
    field_schema: Optional[Dict[str, Any]] = None,
) -> tuple[Action, Dict[str, Any]]:
    payload = _load_json_like(raw_text)
    field_validation_error = (
        _field_validation_error(payload, field_schema) if field_schema else None
    )
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
        "field_validation_error": field_validation_error,
    }
    if require_field_application and not metadata["field_application_present"] and not allow_fallback:
        raise ValueError("Model output did not include the required field_application object.")
    if field_validation_error and not allow_fallback:
        raise FieldValidationError(field_validation_error)

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
    field_error: Optional[str] = None,
    valid_fields: Optional[List[str]] = None,
) -> str:
    valid_actions: List[str] = list(predefined.keys()) + list(openended.keys())
    field_application_instruction = (
        "Include the required field_application object that applies the predefined theory fields.\n"
        if require_field_application
        else ""
    )
    field_instruction = ""
    if field_error:
        field_instruction = (
            f"Field rationale error: {field_error}\n"
            "Copy field names exactly from the Field Register into used_fields. "
            "Do not put output key names such as action, used_fields, field_analysis, "
            "or openended_response inside used_fields.\n"
        )
        if valid_fields:
            field_instruction += f"Valid fields: {valid_fields}\n"
    return (
        "Your previous response was invalid or incomplete.\n"
        "Return valid JSON only.\n"
        f"Valid actions: {valid_actions}\n"
        f"{field_application_instruction}"
        f"{field_instruction}"
        "Copy one valid action id exactly into 'action' or 'selected_action'.\n"
        "If you choose an openended action, include an 'openended_response' string."
    )
