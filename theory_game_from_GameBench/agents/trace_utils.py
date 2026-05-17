import json
import re
from typing import Any, Dict, Optional

from api.classes import AvailableActions


def _normalize_game_id(game_id: Optional[str]) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", game_id or "").strip("_").lower()


def _contextual_action_description(
    *,
    action_id: str,
    description: Optional[str],
    game_id: Optional[str],
    observation_text: str,
    action_instructions: str,
) -> Optional[str]:
    if description and description != action_id:
        return description

    normalized_game_id = _normalize_game_id(game_id)
    observation_lower = (observation_text or "").lower()
    instructions_lower = (action_instructions or "").lower()

    if normalized_game_id == "are_you_the_traitor" and action_id.isdigit():
        return (
            f"Select player {action_id} as the current player target "
            "(conversation partner or accusation target, depending on this turn)."
        )

    if normalized_game_id == "two_rooms_and_a_boom" and action_id.isdigit():
        if "leader of room" in observation_lower and "need to talk" not in observation_lower:
            return f"Select player/card {action_id} as the hostage/card to trade."
        if "need to talk" in observation_lower:
            return f"Talk to player/card {action_id}."
        return (
            f"Select player/card {action_id} as the current room target "
            "(conversation partner or hostage/card trade target, depending on this turn)."
        )

    if normalized_game_id == "codenames":
        if action_id == "end_turn":
            return "End the current guessing turn."
        match = re.fullmatch(r"guess_(\d+)", action_id)
        if match:
            board_words = _codenames_board_words(observation_text)
            index = int(match.group(1))
            if index < len(board_words):
                return f"Guess the board word: {board_words[index]}."
            return f"Guess board word at index {index}."

    if description:
        return description
    if action_id.isdigit() and "return your actions as tuples" in instructions_lower:
        return f"Select target id {action_id} from the current candidate list."
    return None


def _codenames_board_words(observation_text: str):
    words = []
    in_board = False
    for raw_line in (observation_text or "").splitlines():
        line = raw_line.strip()
        if line == "Current board:":
            in_board = True
            continue
        if not in_board:
            continue
        if not line:
            break
        match = re.match(r"^(.*?)\s+\((?:RED|BLUE|NEUTRAL|ASSASSIN|UNKNOWN)\)\s+\((?:HIDDEN|REVEALED)\)$", line)
        if match:
            words.append(match.group(1))
    return words


def action_trace_fields(
    available_actions: AvailableActions,
    action_id: Optional[str],
    *,
    game_id: Optional[str] = None,
    observation_text: str = "",
    action_instructions: str = "",
) -> Dict[str, Any]:
    """Return fair post-selection action interpretation fields for traces."""
    if action_id in available_actions.predefined:
        return {
            "selected_action_type": "predefined",
            "selected_action_description": _contextual_action_description(
                action_id=action_id,
                description=available_actions.predefined[action_id],
                game_id=game_id,
                observation_text=observation_text,
                action_instructions=action_instructions,
            ),
            "selected_action_valid": True,
        }
    if action_id in available_actions.openended:
        return {
            "selected_action_type": "openended",
            "selected_action_description": _contextual_action_description(
                action_id=action_id,
                description=available_actions.openended[action_id],
                game_id=game_id,
                observation_text=observation_text,
                action_instructions=action_instructions,
            ),
            "selected_action_valid": True,
        }
    return {
        "selected_action_type": "unknown",
        "selected_action_description": None,
        "selected_action_valid": False,
    }


def format_action_id_reference(
    predefined_actions: Dict[str, str],
    openended_actions: Dict[str, str],
    *,
    game_id: Optional[str] = None,
    observation_text: str = "",
    action_instructions: str = "",
) -> str:
    reference = {}
    if predefined_actions:
        reference["predefined"] = [
            {
                "id": action_id,
                "meaning": _contextual_action_description(
                    action_id=action_id,
                    description=description,
                    game_id=game_id,
                    observation_text=observation_text,
                    action_instructions=action_instructions,
                ),
            }
            for action_id, description in predefined_actions.items()
        ]
    if openended_actions:
        reference["openended"] = [
            {
                "id": action_id,
                "meaning": _contextual_action_description(
                    action_id=action_id,
                    description=description,
                    game_id=game_id,
                    observation_text=observation_text,
                    action_instructions=action_instructions,
                ),
            }
            for action_id, description in openended_actions.items()
        ]
    reference = {
        key: [item for item in value if item["meaning"]]
        for key, value in reference.items()
    }
    reference = {key: value for key, value in reference.items() if value}
    if not reference:
        return ""
    return (
        "Action ID Reference for interpreting the valid action ids above:\n"
        f"{json.dumps(reference, indent=2)}"
    )
