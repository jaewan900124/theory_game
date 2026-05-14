import json
from pathlib import Path

import yaml


CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"
FIELD_SCHEMA_DIR = CONFIG_DIR / "field_schemas"
ALIASES_PATH = FIELD_SCHEMA_DIR / "aliases.yaml"


COMMON_OUTPUT_SCHEMA = {
    "state_reconstruction": {
        "my_role": "",
        "current_turn_owner": "",
        "legal_actions": [],
        "public_state_summary": "",
        "private_information_used": {},
        "hidden_information_not_assumed": True,
        "state_consistency_checks": [],
    },
    "game_specific_derived_fields": {},
    "mapped_theory_use": {
        "primary_theory": "",
        "auxiliary_theories": [],
        "theory_applies_to_current_state": True,
        "theory_limitations_in_current_state": [],
    },
    "theory_evidence_fields": {},
    "objective_alignment": {
        "environment_objective": "",
        "theory_objective": "",
        "objective_mismatch_risk": "",
        "decision_priority": "",
    },
    "decision_fields": {
        "candidate_actions_supported": [],
        "candidate_actions_discouraged": [],
        "immediate_tactical_overrides": [],
        "uncertainty_notes": [],
    },
    "invalid_theory_checks": {
        "hidden_information_assumption": False,
        "unmapped_theory_used": False,
        "wrong_turn_perspective": False,
        "illegal_action_selected": False,
        "theory_specific_invalid_claims": [],
    },
    "final_decision": {
        "selected_action": "",
        "action_source": "",
        "confidence": "",
    },
}


ACTION_SOURCE_VALUES = [
    "immediate_win",
    "immediate_block",
    "forced_promotion",
    "forced_defense",
    "backward_induction",
    "threat_space",
    "bayesian_expected_value",
    "auction_expected_surplus",
    "auction_truthful_dominance",
    "best_response",
    "dominance",
    "mixed_strategy_support",
    "trigger_strategy",
    "risk_dominance",
    "payoff_dominance",
    "signaling_equilibrium",
    "public_goods_private_best_response",
    "objective_aligned_fallback",
]


FIELD_USAGE_RULES_BY_GAME = {
    "tictactoe": [
        {"rule_id": "win_now", "if": "immediate_win_actions is non_empty", "choose_from": "immediate_win_actions"},
        {"rule_id": "block_now", "if": "immediate_block_actions is non_empty", "choose_from": "immediate_block_actions"},
        {"rule_id": "create_fork", "if": "fork_creation_actions is non_empty", "choose_from": "fork_creation_actions"},
        {"rule_id": "block_fork", "if": "fork_block_actions is non_empty", "choose_from": "fork_block_actions"},
        {"rule_id": "positional_fallback", "if": "no tactical rule triggered", "choose_by": "heuristic_tiebreak_center_corner_edge order center, corner, edge"},
    ],
    "connect4": [
        {"rule_id": "win_now", "if": "immediate_win_columns is non_empty", "choose_from": "immediate_win_columns"},
        {"rule_id": "block_now", "if": "immediate_block_columns is non_empty", "choose_from": "immediate_block_columns"},
        {"rule_id": "avoid_giving_win", "if": "dangerous_moves_that_enable_opponent_win is non_empty", "discard": "dangerous_moves_that_enable_opponent_win"},
        {"rule_id": "center_control", "if": "no forcing rule triggered", "choose_by": "minimize heuristic_tiebreak_center_distance_by_column after unsafe moves are discarded"},
    ],
    "breakthrough": [
        {"rule_id": "promote_now", "if": "immediate_promotion_actions is non_empty", "choose_from": "immediate_promotion_actions"},
        {"rule_id": "stop_opponent_promotion", "if": "opponent_immediate_promotion_threats is non_empty", "choose_from": "defensive_block_or_capture_actions"},
        {"rule_id": "capture_or_race", "if": "no forced promotion/defense", "choose_by": "promotion_race_evaluation, then capture_actions"},
    ],
    "first_price_auction": [
        {"rule_id": "discard_overbids", "always": True, "discard": "overbid_actions"},
        {"rule_id": "win_rate_with_positive_surplus", "if": "environment objective rewards winning more than surplus", "choose_by": "objective_sensitive_bid_fields and surplus_if_win_by_bid"},
        {"rule_id": "expected_surplus", "if": "expected_surplus_by_bid is available", "choose": "argmax expected_surplus_by_bid"},
        {"rule_id": "tradeoff_fallback", "if": "expected surplus is uncertain", "choose_by": "win_probability_surplus_tradeoff"},
    ],
    "second_price_auction": [
        {"rule_id": "truthful_dominance", "if": "truthful_bid is legal", "choose": "truthful_bid"},
        {"rule_id": "nearest_truthful_legal", "if": "truthful_bid is not legal", "choose": "nearest legal bid not exceeding valuation"},
    ],
    "liars_dice": [
        {"rule_id": "challenge_false_bid", "if": "estimated_probability_current_bid_true is below challenge threshold", "choose": "challenge action"},
        {"rule_id": "legal_raise_with_evidence", "if": "my_dice_evidence supports a raise", "choose_by": "legal_raise_space"},
        {"rule_id": "least_risky_raise", "if": "must raise and evidence is weak", "choose": "minimum legal raise"},
    ],
    "kuhn_poker": [
        {"rule_id": "respect_turn_context", "always": True, "discard": "actions inconsistent with facing_bet/legal_action_context"},
        {"rule_id": "strong_hand_value", "if": "hand_strength_class is strong", "prefer": "bet/call legal action"},
        {"rule_id": "weak_hand_control", "if": "hand_strength_class is weak", "prefer": "pass/fold legal action unless bluff rule is triggered"},
        {"rule_id": "bayesian_ev", "if": "expected_value_by_action is available", "choose": "argmax expected_value_by_action"},
    ],
    "iterated_prisoners_dilemma": [
        {"rule_id": "punish_defection", "if": "trigger_strategy_state indicates punishment", "choose": "defect/testify action"},
        {"rule_id": "maintain_cooperation", "if": "opponent_recent_actions show cooperation", "choose": "cooperate/silent action"},
        {"rule_id": "best_response_pattern", "if": "pattern_detection shows exploitation", "choose_by": "next_action_implications"},
    ],
    "negotiation": [
        {"rule_id": "agree_if_acceptable", "if": "acceptance_threshold_model is available and latest offer payoff meets it and Agree is legal", "choose": "<Agree>"},
        {"rule_id": "offer_high_self_payoff", "if": "proposal is required", "choose": "candidate with best self payoff that keeps agreement_probability_by_action plausible"},
        {"rule_id": "utterance_alignment", "if": "utterance is required", "choose": "utterance supporting next beneficial proposal"},
    ],
    "nim": [
        {"rule_id": "take_terminal_win", "if": "terminal_actions contains winning legal action", "choose_from": "terminal_actions"},
        {"rule_id": "move_to_losing_state", "if": "opponent_position_value_by_action marks an opponent-losing successor", "choose_by": "opponent_position_value_by_action"},
        {"rule_id": "misere_parity", "if": "misere_rule_check indicates endgame parity matters", "choose_by": "singleton_parity_by_action"},
        {"rule_id": "least_bad", "if": "no winning move", "choose_from": "losing_moves with best opponent_position_value_by_action"},
    ],
    "pig": [
        {"rule_id": "stop_wins_now", "if": "stop_wins_now is true", "choose": "<stop>"},
        {"rule_id": "roll_at_zero", "if": "turn_total is 0 and <roll> is legal", "choose": "<roll>"},
        {"rule_id": "bank_near_target", "if": "score_after_stop is close to target_score", "choose": "<stop>"},
        {"rule_id": "bank_when_bust_risk_high", "if": "bust_loss is large relative to one_roll_heuristic_value_by_action", "choose": "<stop>"},
        {"rule_id": "roll_when_race_pressure_high", "if": "score_race_pressure favors catching up and bust risk is acceptable", "choose": "<roll>"},
    ],
    "matching_pennies": [
        {"rule_id": "avoid_deterministic_pattern", "if": "history suggests predictable play", "choose_by": "mixed_strategy_support"},
        {"rule_id": "best_response_if_belief_available", "if": "opponent_action_belief is skewed", "choose": "best_response_by_belief"},
    ],
    "stag_hunt": [
        {"rule_id": "payoff_dominant_if_trust", "if": "belief supports cooperation", "choose": "payoff_dominant_action"},
        {"rule_id": "risk_dominant_if_uncertain", "if": "belief is uncertain or low trust", "choose": "risk_dominant_action"},
    ],
    "centipede_game": [
        {"rule_id": "backward_induction_stop", "if": "backward_induction_action is available", "choose": "backward_induction_action"},
        {"rule_id": "continuation_value_override", "if": "continuation_value_by_action supports pass", "choose": "pass action"},
    ],
    "signaling_game": [
        {"rule_id": "sequential_rational_response", "if": "receiver role", "choose": "best response to receiver_belief_after_signal"},
        {"rule_id": "incentive_compatible_signal", "if": "sender role", "choose": "signal satisfying incentive_compatibility_check"},
    ],
    "public_goods_game": [
        {"rule_id": "private_best_response", "if": "dominant private incentive exists", "choose": "private_best_response_contribution"},
        {"rule_id": "cooperative_if_enforced", "if": "punishment/repetition supports cooperation", "choose": "cooperative contribution"},
    ],
}


PROGRAM_OUTPUT_SCHEMA = {
    "state_reconstruction": {
        "my_role": "",
        "current_turn_owner": "",
        "legal_actions": [],
        "public_state_summary": "",
        "private_information_used": {},
        "hidden_information_not_assumed": True,
    },
    "computed_fields": {},
    "theory_application": {
        "primary_theory": "",
        "operational_meaning": "",
        "evidence_fields_used": [],
        "theory_limitations": [],
    },
    "field_usage": {
        "triggered_rules": [],
        "highest_priority_triggered_rule": "",
        "candidate_actions_from_rule": [],
        "discarded_actions_by_rule": [],
        "why_rule_selects_action": "",
    },
    "decision": {
        "selected_action": "",
        "reason_code": "",
        "confidence": "",
    },
    "validity": {
        "selected_action_is_legal": True,
        "no_hidden_information_used": True,
        "highest_priority_rule_followed": True,
        "no_required_field_left_uncomputed": True,
        "invalid_claims": [],
    },
    "final_decision": {
        "selected_action": "",
        "action_source": "",
        "confidence": "",
    },
}


REASONING_MODE_INSTRUCTIONS = {
    "normal": """[Reasoning Mode]
normal
- Output only the required JSON object.
- Keep every field compact and decision-relevant.
- Do not include chain-of-thought or scratch work.""",
    "cot": """[Reasoning Mode]
cot
- Think through the reconstruction and theory application before answering, but do not output long chain-of-thought.
- The visible answer must still be valid JSON only.
- Put only compact computed results in the required fields; do not add an essay or hidden-step transcript.
- Use state_reconstruction -> game_specific_derived_fields -> theory_evidence_fields -> final_decision order internally.""",
}


def _load_yaml(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_field_schema_aliases():
    return _load_yaml(ALIASES_PATH)


def canonical_game_id(game_id, aliases=None):
    aliases = aliases or load_field_schema_aliases()
    return aliases.get("game_aliases", {}).get(game_id, game_id)


def canonical_theory_id(theory_id, aliases=None):
    aliases = aliases or load_field_schema_aliases()
    normalized = theory_id.strip().lower().replace("_", " ")
    alias = aliases.get("theory_aliases", {}).get(normalized)
    if alias:
        return alias
    return theory_id.strip().lower().replace(" ", "_").replace("-", "_")


def split_mapped_theories(mapped_theories):
    if not mapped_theories:
        return []
    if isinstance(mapped_theories, list):
        return mapped_theories
    if isinstance(mapped_theories, str):
        parts = []
        for chunk in mapped_theories.replace(";", ",").split(","):
            item = chunk.strip()
            if item:
                parts.append(item)
        return parts
    return []


def load_game_field_schema(game_id):
    canonical = canonical_game_id(game_id)
    path = FIELD_SCHEMA_DIR / "games" / f"{canonical}.yaml"
    if not path.exists():
        raise KeyError(f"No game field schema exists for game_id={game_id} canonical={canonical}")
    return _load_yaml(path)


def load_theory_field_schema(theory_id):
    canonical = canonical_theory_id(theory_id)
    path = FIELD_SCHEMA_DIR / "theories" / f"{canonical}.yaml"
    if not path.exists():
        raise KeyError(f"No theory field schema exists for theory_id={theory_id} canonical={canonical}")
    return _load_yaml(path)


def default_theories_for_game(game_id):
    aliases = load_field_schema_aliases()
    canonical = canonical_game_id(game_id, aliases)
    return aliases.get("default_theories_by_game", {}).get(canonical, [])


def resolve_theory_schemas(game_id, mapped_theories=None):
    aliases = load_field_schema_aliases()
    theory_ids = [
        canonical_theory_id(theory, aliases)
        for theory in split_mapped_theories(mapped_theories)
    ]
    if not theory_ids:
        theory_ids = default_theories_for_game(game_id)

    seen = set()
    schemas = []
    for theory_id in theory_ids:
        canonical = canonical_theory_id(theory_id, aliases)
        if canonical in seen:
            continue
        seen.add(canonical)
        schemas.append(load_theory_field_schema(canonical))
    return schemas


def required_field_names(field_mapping):
    return list((field_mapping or {}).keys())


def build_game_specific_field_shape(game_schema):
    return {
        field_name: {
            "value": "",
            "check": spec.get("instruction", ""),
        }
        for field_name, spec in game_schema.get("required_derived_fields", {}).items()
    }


def build_theory_evidence_field_shape(theory_schemas):
    result = {}
    for theory in theory_schemas:
        theory_id = theory["theory_id"]
        result[theory_id] = {
            field_name: {
                "value": "",
                "check": spec.get("instruction", ""),
            }
            for field_name, spec in theory.get("required_theory_evidence_fields", {}).items()
        }
    return result


def build_program_computed_field_shape(game_schema, theory_schemas):
    shape = {
        field_name: ""
        for field_name in game_schema.get("required_derived_fields", {})
    }
    for theory in theory_schemas:
        theory_id = theory["theory_id"]
        shape[f"{theory_id}_evidence"] = {
            field_name: ""
            for field_name in theory.get("required_theory_evidence_fields", {})
        }
    return shape


def compact_theory_program(theory_schemas):
    return [
        {
            "theory_id": theory["theory_id"],
            "operations": theory.get("theory_operations", []),
            "required_evidence_fields": required_field_names(
                theory.get("required_theory_evidence_fields", {})),
            "decision_implication": theory.get("decision_implications", ""),
            "invalid_claims": theory.get("invalid_theory_claims", []),
        }
        for theory in theory_schemas
    ]


def json_safe(value):
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def build_field_usage_program_prompt(
    game_id,
    legal_actions,
    observation=None,
    mapped_theories=None,
    payoff_information=None,
    reasoning_mode="normal",
):
    observation = observation or {}
    safe_observation = json_safe(observation)
    canonical_game = canonical_game_id(game_id)
    game_schema = load_game_field_schema(canonical_game)
    theory_schemas = resolve_theory_schemas(canonical_game, mapped_theories)
    theory_ids = [schema["theory_id"] for schema in theory_schemas]
    usage_rules = FIELD_USAGE_RULES_BY_GAME.get(canonical_game, [
        {"rule_id": "theory_best_supported_action", "if": "computed fields identify supported actions", "choose": "best supported legal action"},
        {"rule_id": "legal_fallback", "if": "no rule clearly applies", "choose": "first supported legal action, otherwise first legal action"},
    ])

    output_schema = dict(PROGRAM_OUTPUT_SCHEMA)
    output_schema["state_reconstruction"] = dict(PROGRAM_OUTPUT_SCHEMA["state_reconstruction"])
    output_schema["state_reconstruction"]["legal_actions"] = legal_actions
    output_schema["computed_fields"] = build_program_computed_field_shape(
        game_schema, theory_schemas)

    if reasoning_mode not in REASONING_MODE_INSTRUCTIONS:
        raise ValueError(f"Unknown reasoning_mode: {reasoning_mode}")

    prompt = f"""You are an autonomous game-playing agent.

Your strategy has already been designed from the game rules and mapped game theory.
Do not invent a new strategy. Execute the field program below.

Your task:
1. Reconstruct the current state.
2. Compute every required field in computed_fields.
3. Apply field_usage_rules in priority order.
4. Select an action only from the highest-priority triggered rule.

Do not output chain-of-thought.
Do not write an essay.
Return compact valid JSON only.

{REASONING_MODE_INSTRUCTIONS[reasoning_mode]}

[Game ID]
{canonical_game}

[Legal Actions]
{json.dumps(legal_actions, ensure_ascii=False)}

[Current Observation]
{json.dumps(safe_observation, ensure_ascii=False)}

[Payoff Information]
{json.dumps(json_safe(payoff_information or observation.get("payoff_information", "")), ensure_ascii=False)}

[Required Computed Fields From Game Rules]
Compute these fields directly from the current state:
{json.dumps(required_field_names(game_schema.get("required_derived_fields", {})), indent=2, ensure_ascii=False)}

[Required Computed Fields From Mapped Theory]
Compute the listed evidence fields under <theory_id>_evidence:
{json.dumps(compact_theory_program(theory_schemas), indent=2, ensure_ascii=False)}

[Field Usage Rules]
Apply these rules in order. The first triggered rule that yields legal candidate actions determines the decision.
{json.dumps(usage_rules, indent=2, ensure_ascii=False)}

[Game Failure Modes To Guard Against]
common_failure_modes={json.dumps(game_schema.get("common_failure_modes", []), ensure_ascii=False)}
invalid_claims={json.dumps(game_schema.get("invalid_claims", []), ensure_ascii=False)}
objective_alignment_notes={json.dumps(game_schema.get("objective_alignment_notes", ""), ensure_ascii=False)}

[Hard Constraints]
- selected_action must be one of legal_actions: {json.dumps(legal_actions, ensure_ascii=False)}.
- decision.selected_action and final_decision.selected_action must be identical.
- decision.reason_code must be the rule_id of highest_priority_triggered_rule.
- final_decision.action_source must be compact and compatible with decision.reason_code.
- If no rule has a valid candidate, use objective_aligned_fallback and choose a legal action.
- Do not assume hidden information.
- Private-information games must separate known private information from beliefs about unknown information.
- Board games must compute tactical fields before positional fallback.
- Sequential games must keep the current turn perspective consistent.
- Auction games must separate win-rate pressure from expected-surplus pressure.

[Output Schema]
Return valid JSON only with this exact top-level shape:
{json.dumps(output_schema, indent=2, ensure_ascii=False)}
"""
    return {
        "prompt": prompt,
        "game_id": canonical_game,
        "game_schema": game_schema,
        "theory_ids": theory_ids,
        "theory_schemas": theory_schemas,
        "field_usage_rules": usage_rules,
        "output_schema": output_schema,
    }


def build_field_schema_prompt(
    game_id,
    legal_actions,
    observation=None,
    mapped_theories=None,
    payoff_information=None,
    reasoning_mode="normal",
):
    observation = observation or {}
    safe_observation = json_safe(observation)
    canonical_game = canonical_game_id(game_id)
    game_schema = load_game_field_schema(canonical_game)
    theory_schemas = resolve_theory_schemas(canonical_game, mapped_theories)
    theory_ids = [schema["theory_id"] for schema in theory_schemas]

    output_schema = dict(COMMON_OUTPUT_SCHEMA)
    output_schema["state_reconstruction"] = dict(COMMON_OUTPUT_SCHEMA["state_reconstruction"])
    output_schema["state_reconstruction"]["legal_actions"] = legal_actions
    output_schema["game_specific_derived_fields"] = build_game_specific_field_shape(game_schema)
    output_schema["theory_evidence_fields"] = build_theory_evidence_field_shape(theory_schemas)
    if reasoning_mode not in REASONING_MODE_INSTRUCTIONS:
        raise ValueError(f"Unknown reasoning_mode: {reasoning_mode}")

    prompt = f"""You are an autonomous game-playing agent using field-based game-theoretic reasoning.

Your task is to choose one legal action from the current game state.

Do not output long chain-of-thought.
Do not write a full essay.
Do not restate the entire game rules.
Use compact, checkable JSON fields only.

{REASONING_MODE_INSTRUCTIONS[reasoning_mode]}

[Game ID]
{canonical_game}

[Legal Actions]
{json.dumps(legal_actions, ensure_ascii=False)}

[Current Observation]
{json.dumps(safe_observation, ensure_ascii=False)}

[Payoff Information]
{json.dumps(json_safe(payoff_information or observation.get("payoff_information", "")), ensure_ascii=False)}

[Required Game-Specific Derived Fields]
Populate every field below inside game_specific_derived_fields:
{json.dumps(game_schema.get("required_derived_fields", {}), indent=2, ensure_ascii=False)}

[Game Failure Modes To Guard Against]
common_failure_modes={json.dumps(game_schema.get("common_failure_modes", []), ensure_ascii=False)}
invalid_claims={json.dumps(game_schema.get("invalid_claims", []), ensure_ascii=False)}
objective_alignment_notes={json.dumps(game_schema.get("objective_alignment_notes", ""), ensure_ascii=False)}

[Mapped Theory Schemas]
Use only these mapped theories unless a theory is explicitly listed as auxiliary:
{json.dumps(theory_schemas, indent=2, ensure_ascii=False)}

[Decision Priority Rules]
- First reconstruct the state and compute all required game_specific_derived_fields.
- Then apply mapped theories to those derived fields inside theory_evidence_fields.
- Immediate legal wins, forced blocks, forced promotion, and forced defense override non-forcing theory fields.
- If theory does not determine a unique action, represent uncertainty and choose a legal fallback from supported actions.
- selected_action must be copied exactly from state_reconstruction.legal_actions.
- selected_action must be one of legal_actions: {json.dumps(legal_actions, ensure_ascii=False)}.
- final_decision.action_source must be one of: {json.dumps(ACTION_SOURCE_VALUES, ensure_ascii=False)}.
- confidence must be one of: ["high", "medium", "low"].

[Output Schema]
Return valid JSON only with this exact top-level shape:
{json.dumps(output_schema, indent=2, ensure_ascii=False)}

[Invalid Claim Checks]
- Do not invent hidden information.
- Private-information games must distinguish private_information_used from beliefs.
- Sequential games must keep current_turn_owner/current_actor perspective consistent.
- Board games must include reconstruction and immediate tactical checks.
- Auction games must include objective alignment between expected reward and win-rate if the environment objective is available.
"""
    return {
        "prompt": prompt,
        "game_id": canonical_game,
        "game_schema": game_schema,
        "theory_ids": theory_ids,
        "theory_schemas": theory_schemas,
        "output_schema": output_schema,
    }
