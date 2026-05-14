from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import yaml

from gamingbench.interaction_fields.prompt import build_small_model_prompt
from gamingbench.interaction_fields.required_fields import _canonical_game_id
from gamingbench.interaction_fields.schemas import CompiledDecisionProgram, InteractionFieldSpec


PROFILE_CONFIG_PATH = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "engineering_profiles"
    / "game_field_engineering_profiles.yaml"
)

DIRECT_ANSWER_FIELD_RE = re.compile(
    r"(recommended_action|optimal_move|best_action|best_move|must_play|choose_action)",
    re.IGNORECASE,
)


def load_engineering_profiles() -> Dict[str, Any]:
    with PROFILE_CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _game_profile(game_id: str, engineering_profile: str) -> Optional[Mapping[str, Any]]:
    config = load_engineering_profiles()
    games = config.get("games") or {}
    canonical = _canonical_game_id(game_id)
    spec = games.get(canonical) or games.get(game_id)
    if not isinstance(spec, Mapping):
        return None
    level = spec.get(engineering_profile)
    return level if isinstance(level, Mapping) else None


def _validate_no_direct_answer_fields(fields: list[InteractionFieldSpec], strict: bool) -> None:
    invalid = [field.field_id for field in fields if DIRECT_ANSWER_FIELD_RE.search(field.field_id)]
    if invalid and strict:
        raise ValueError(f"engineering profile violation: direct-answer field ids present: {invalid}")


def _field_value(program: CompiledDecisionProgram, field_id: str) -> Any:
    for field in program.computed_fields:
        if field.field_id == field_id:
            return field.value
    return None


def _allowed_fields_for_level(program: CompiledDecisionProgram, level: Mapping[str, Any]) -> set[str]:
    selector_field = level.get("context_selector_field")
    if not selector_field:
        return set(level.get("allowed_fields") or [])

    shared_fields = set(level.get("shared_allowed_fields") or [])
    selector_value = _field_value(program, str(selector_field))
    if selector_value is True:
        context_fields = set(level.get("when_selector_true_allowed_fields") or [])
    elif selector_value is False:
        context_fields = set(level.get("when_selector_false_allowed_fields") or [])
    else:
        context_fields = set(level.get("fallback_allowed_fields") or [])
    return shared_fields | context_fields


def apply_engineering_profile(
    program: CompiledDecisionProgram,
    engineering_profile: Optional[str],
    *,
    mode: str = "reasoning",
    strict: bool = False,
    state_summary: str = "",
) -> CompiledDecisionProgram:
    if not engineering_profile:
        return program

    if mode not in {"reasoning", "distill"}:
        raise ValueError(f"unknown engineering profile mode: {mode!r}")

    level = _game_profile(program.game_id, engineering_profile)
    if level is None:
        if strict:
            raise ValueError(
                f"engineering profile {engineering_profile!r} is not defined for game {program.game_id!r}"
            )
        return program

    allowed_fields = _allowed_fields_for_level(program, level)
    filtered_fields = [field for field in program.computed_fields if field.field_id in allowed_fields]
    filtered_rules = [
        rule for rule in program.decision_rules if rule.field_id in allowed_fields
    ]
    filtered_tie_break_rules = [
        rule for rule in program.tie_break_rules if rule.field_id in allowed_fields
    ]
    filtered_checks = [
        check
        for check in program.verifier_checks
        if check.field_id is None or check.field_id in allowed_fields
    ]

    _validate_no_direct_answer_fields(filtered_fields, strict)

    profiled = CompiledDecisionProgram(
        game_id=program.game_id,
        theory_id=program.theory_id,
        current_player=program.current_player,
        legal_actions=list(program.legal_actions),
        computed_fields=filtered_fields,
        decision_rules=filtered_rules if mode == "distill" else [],
        tie_break_rules=filtered_tie_break_rules if mode == "distill" else [],
        verifier_checks=filtered_checks,
        final_output_schema=dict(program.final_output_schema or {}),
    )
    profiled.small_model_prompt = build_small_model_prompt(profiled, state_summary=state_summary)
    return profiled
