from __future__ import annotations

import json
from typing import Any, Mapping, Optional, Sequence

from gamingbench.interaction_fields.adapters import GameAdapter, ObservationGameAdapter
from gamingbench.interaction_fields.engineering_profiles import apply_engineering_profile
from gamingbench.interaction_fields.handlers import TheoryHandler, handlers_for_mapping
from gamingbench.interaction_fields.mapping import mapping_for_game
from gamingbench.interaction_fields.prompt import (
    DEFAULT_FINAL_OUTPUT_SCHEMA,
    MATRIX_FINAL_OUTPUT_SCHEMA,
    build_small_model_prompt,
)
from gamingbench.interaction_fields.required_fields import add_required_game_fields
from gamingbench.interaction_fields.schemas import CompiledDecisionProgram


def _state_summary(adapter: GameAdapter) -> str:
    state = adapter.state()
    try:
        return json.dumps(state, ensure_ascii=False, default=str)
    except TypeError:
        return str(state)


def compile_interaction_fields(
    adapter: GameAdapter,
    mapping_entry: Optional[Mapping[str, Any]] = None,
    handlers: Optional[Sequence[TheoryHandler]] = None,
    engineering_profile: Optional[str] = None,
    engineering_profile_mode: str = "reasoning",
    strict: bool = False,
) -> CompiledDecisionProgram:
    """Compile game rules x mapped theory into executable interaction fields."""

    mapping_entry = dict(mapping_entry or mapping_for_game(adapter.game_id))
    selected_handlers = handlers_for_mapping(mapping_entry, handlers)
    all_fields = []
    all_rules = []
    all_checks = []
    theory_ids = []
    for handler in selected_handlers:
        fields, rules, checks = handler.compile(adapter, mapping_entry)
        all_fields.extend(fields)
        all_rules.extend(rules)
        all_checks.extend(checks)
        theory_ids.append(handler.theory_id)

    all_fields, all_rules, all_checks = add_required_game_fields(
        adapter, all_fields, all_rules, all_checks
    )

    final_schema = MATRIX_FINAL_OUTPUT_SCHEMA if any(
        field.field_id == "mutual_best_response_cells" for field in all_fields
    ) else DEFAULT_FINAL_OUTPUT_SCHEMA

    program = CompiledDecisionProgram(
        game_id=adapter.game_id,
        theory_id="+".join(theory_ids),
        current_player=str(adapter.current_player()) if adapter.current_player() is not None else None,
        legal_actions=[str(action) for action in adapter.legal_actions()],
        computed_fields=all_fields,
        decision_rules=sorted(all_rules, key=lambda rule: rule.priority),
        verifier_checks=all_checks,
        final_output_schema=final_schema,
    )
    state_summary = _state_summary(adapter)
    program.small_model_prompt = build_small_model_prompt(program, state_summary=state_summary)
    return apply_engineering_profile(
        program,
        engineering_profile,
        mode=engineering_profile_mode,
        strict=strict,
        state_summary=state_summary,
    )


def compile_from_observation(
    game_id: str,
    observation: Mapping[str, Any],
    mapping_entry: Optional[Mapping[str, Any]] = None,
    engineering_profile: Optional[str] = None,
    engineering_profile_mode: str = "reasoning",
    strict: bool = False,
) -> CompiledDecisionProgram:
    adapter = ObservationGameAdapter(game_id, observation)
    return compile_interaction_fields(
        adapter,
        mapping_entry=mapping_entry,
        engineering_profile=engineering_profile,
        engineering_profile_mode=engineering_profile_mode,
        strict=strict,
    )
