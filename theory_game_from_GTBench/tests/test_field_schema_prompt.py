from pathlib import Path

import yaml

from gamingbench.prompts.field_schema_prompt_builder import (
    build_field_schema_prompt,
    build_field_usage_program_prompt,
    canonical_game_id,
    load_game_field_schema,
    load_theory_field_schema,
)


ROOT = Path(__file__).resolve().parents[1]
FIELD_SCHEMA_DIR = ROOT / "gamingbench" / "configs" / "field_schemas"
GAME_DIR = FIELD_SCHEMA_DIR / "games"
THEORY_DIR = FIELD_SCHEMA_DIR / "theories"


REQUESTED_GAMES = {
    "tictactoe",
    "connect4",
    "breakthrough",
    "liars_dice",
    "kuhn_poker",
    "first_price_auction",
    "second_price_auction",
    "iterated_prisoners_dilemma",
    "matching_pennies",
    "stag_hunt",
    "centipede_game",
    "signaling_game",
    "public_goods_game",
}


def read_yaml(path):
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_all_requested_game_schemas_exist_and_are_constrained():
    existing = {path.stem for path in GAME_DIR.glob("*.yaml")}
    assert REQUESTED_GAMES <= existing

    for game_id in REQUESTED_GAMES:
        schema = read_yaml(GAME_DIR / f"{game_id}.yaml")
        assert schema["game_id"] == game_id
        assert schema["required_state_fields"]
        assert schema["required_derived_fields"]
        assert schema["common_failure_modes"]
        assert schema["invalid_claims"]
        assert "objective_alignment_notes" in schema

        for field_name, field_spec in schema["required_derived_fields"].items():
            assert field_name
            assert field_spec["required"] is True
            assert field_spec["type"]
            assert field_spec["instruction"]


def test_theory_schemas_have_required_evidence_fields():
    for path in THEORY_DIR.glob("*.yaml"):
        schema = read_yaml(path)
        assert schema["theory_id"] == path.stem
        assert schema["required_theory_evidence_fields"]
        assert schema["theory_operations"]
        assert schema["decision_implications"]
        assert schema["invalid_theory_claims"]

        for field_name, field_spec in schema["required_theory_evidence_fields"].items():
            assert field_name
            assert field_spec["required"] is True
            assert field_spec["type"]
            assert field_spec["instruction"]


def test_aliases_map_repo_game_ids_to_new_registry_names():
    assert canonical_game_id("tic_tac_toe") == "tictactoe"
    assert canonical_game_id("first_sealed_auction") == "first_price_auction"
    assert canonical_game_id("python_iterated_prisoners_dilemma") == "iterated_prisoners_dilemma"


def test_prompt_includes_game_specific_and_theory_specific_required_fields():
    prompt_data = build_field_schema_prompt(
        "tictactoe",
        ["<C1R1>", "<C2R2>"],
        observation={"env_name": "tictactoe", "legal_moves": ["<C1R1>", "<C2R2>"]},
    )
    prompt = prompt_data["prompt"]

    assert "game_specific_derived_fields" in prompt
    assert "theory_evidence_fields" in prompt
    assert "board_reading" in prompt
    assert "immediate_win_actions" in prompt
    assert "current_node_value" in prompt
    assert "selected_action must be one of legal_actions" in prompt
    assert '"<C1R1>"' in prompt


def test_prompt_reasoning_modes_are_distinct():
    normal = build_field_schema_prompt(
        "connect4",
        ["<C1>", "<C2>"],
        observation={"env_name": "connect4"},
        reasoning_mode="normal",
    )["prompt"]
    cot = build_field_schema_prompt(
        "connect4",
        ["<C1>", "<C2>"],
        observation={"env_name": "connect4"},
        reasoning_mode="cot",
    )["prompt"]

    assert "[Reasoning Mode]\nnormal" in normal
    assert "[Reasoning Mode]\ncot" in cot
    assert "Output only the required JSON object" in normal
    assert "Think through the reconstruction and theory application before answering" in cot
    assert "valid JSON only" in cot


def test_field_usage_program_prompt_adds_action_program_layer():
    prompt_data = build_field_usage_program_prompt(
        "tictactoe",
        ["<C1R1>", "<C2R2>"],
        observation={"env_name": "tictactoe", "legal_moves": ["<C1R1>", "<C2R2>"]},
    )
    prompt = prompt_data["prompt"]

    assert "Do not invent a new strategy. Execute the field program below." in prompt
    assert "[Field Usage Rules]" in prompt
    assert "computed_fields" in prompt
    assert "field_usage" in prompt
    assert "highest_priority_triggered_rule" in prompt
    assert "win_now" in prompt
    assert "block_now" in prompt
    assert "positional_fallback" in prompt
    assert "decision.selected_action and final_decision.selected_action must be identical" in prompt


def test_field_usage_program_is_game_specific():
    auction = build_field_usage_program_prompt(
        "first_sealed_auction",
        ["<0>", "<1>"],
        observation={"env_name": "first_sealed_auction", "valuation": 2},
    )["prompt"]
    pig = build_field_usage_program_prompt(
        "pig",
        ["<roll>", "<stop>"],
        observation={"env_name": "pig", "turn_total_score": 0},
    )["prompt"]

    assert "win_rate_with_positive_surplus" in auction
    assert "expected_surplus" in auction
    assert "stop_wins_now" in pig
    assert "roll_at_zero" in pig


def test_private_information_games_include_hidden_information_guards():
    for game_id in ["liars_dice", "kuhn_poker", "first_price_auction", "second_price_auction", "signaling_game"]:
        schema = load_game_field_schema(game_id)
        assert "hidden_information_not_assumed" in schema["required_state_fields"]
        prompt = build_field_schema_prompt(game_id, ["<A>"], observation={"env_name": game_id})["prompt"]
        assert "Do not invent hidden information" in prompt
        assert "private_information_used" in prompt


def test_sequential_games_include_turn_perspective_or_node_fields():
    required_by_game = {
        "kuhn_poker": ["turn_and_history_perspective", "current_actor", "is_my_turn"],
        "breakthrough": ["promotion_row_by_player", "opponent_immediate_promotion_threats"],
        "centipede_game": ["current_node", "current_actor", "backward_induction_action"],
        "signaling_game": ["observed_signal", "receiver_belief_after_signal"],
    }
    for game_id, fields in required_by_game.items():
        schema = load_game_field_schema(game_id)
        for field in fields:
            assert field in schema["required_derived_fields"]


def test_board_games_include_reconstruction_and_immediate_tactical_checks():
    checks = {
        "tictactoe": ["board_reading", "immediate_win_actions", "immediate_block_actions"],
        "connect4": ["board_reconstruction", "immediate_win_columns", "immediate_block_columns"],
        "breakthrough": ["board_reconstruction", "immediate_promotion_actions", "opponent_immediate_promotion_threats"],
    }
    for game_id, fields in checks.items():
        schema = load_game_field_schema(game_id)
        for field in fields:
            assert field in schema["required_derived_fields"]


def test_auction_objective_alignment_and_theory_fields():
    first_price = load_game_field_schema("first_price_auction")
    assert "expected surplus" in first_price["objective_alignment_notes"]
    assert "winner count" in first_price["objective_alignment_notes"]
    assert "objective_sensitive_bid_fields" in first_price["required_derived_fields"]

    first_price_theory = load_theory_field_schema("private_value_first_price_auction")
    assert "expected_surplus_by_bid" in first_price_theory["required_theory_evidence_fields"]
    assert "win_probability_assumption_by_bid" in first_price_theory["required_theory_evidence_fields"]

    second_price = load_game_field_schema("second_price_auction")
    assert "truthful_bid" in second_price["required_derived_fields"]
    second_price_theory = load_theory_field_schema("dominant_strategy_second_price_auction")
    assert "truthful_bid_deviation_check" in second_price_theory["required_theory_evidence_fields"]
