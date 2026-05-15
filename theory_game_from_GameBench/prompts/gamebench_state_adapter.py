from typing import Dict

from api.classes import AvailableActions, Observation, Rules
from prompts.game_profiles import canonical_game_id, profile_for_game
from prompts.theory_fields import detect_prompt_context


def normalize_gamebench_state(
    *,
    game_id: str,
    rules: Rules,
    observation: Observation,
    available_actions: AvailableActions,
) -> Dict[str, object]:
    predefined = dict(available_actions.predefined or {})
    openended = dict(available_actions.openended or {})
    canonical_id = canonical_game_id(game_id)
    profile = profile_for_game(canonical_id)

    details = rules.additional_details or {}
    detail_lines = []
    detail_headings = {}
    if isinstance(details, dict):
        detail_headings = {f"H{i + 1}": key for i, key in enumerate(details)}
        for key, value in details.items():
            detail_lines.append(f"- {key}: {value}")

    predefined_lines = []
    for action, description in predefined.items():
        if description:
            predefined_lines.append(f"- {action}: {description}")
        else:
            predefined_lines.append(f"- {action}")

    openended_lines = []
    for action, description in openended.items():
        if description:
            openended_lines.append(f"- {action}: {description}")
        else:
            openended_lines.append(f"- {action}")

    requires_free_text = bool(openended)
    prompt_context = detect_prompt_context(
        canonical_id,
        observation.text,
        available_actions.instructions,
        predefined,
        openended,
    )

    return {
        "game_id": canonical_id,
        "rules_title": rules.title,
        "rules_summary": rules.summary,
        "rules_details_text": "\n".join(detail_lines),
        "rules_detail_headings": detail_headings,
        "observation_text": observation.text,
        "action_instructions": available_actions.instructions,
        "predefined_actions": predefined,
        "openended_actions": openended,
        "predefined_actions_text": "\n".join(predefined_lines),
        "openended_actions_text": "\n".join(openended_lines),
        "requires_free_text": requires_free_text,
        "profile": profile,
        "prompt_context": prompt_context,
    }
