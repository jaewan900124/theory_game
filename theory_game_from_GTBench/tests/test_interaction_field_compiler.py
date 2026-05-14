from gamingbench.interaction_fields import (
    MatrixGameAdapter,
    compile_from_observation,
    compile_interaction_fields,
)
from gamingbench.interaction_fields.required_fields import load_game_schema


def field(program, field_id):
    for item in program.computed_fields:
        if item.field_id == field_id:
            return item
    raise AssertionError(f"missing field: {field_id}")


def test_matrix_game_with_no_pure_nash_returns_empty_set():
    # Matching pennies: no pure Nash equilibrium.
    matrix = {
        ("H", "H"): (1, -1),
        ("H", "T"): (-1, 1),
        ("T", "H"): (-1, 1),
        ("T", "T"): (1, -1),
    }
    adapter = MatrixGameAdapter(matrix, ["H", "T"], ["H", "T"])
    program = compile_interaction_fields(
        adapter,
        mapping_entry={
            "solution_concept": "pure Nash equilibrium in normal-form payoff matrix",
            "game_type": "normal-form payoff matrix game",
        },
    )

    assert field(program, "mutual_best_response_cells").value == []
    assert program.final_output_schema["answer"] == [["A1", "B2"]]


def test_matrix_game_with_multiple_equilibria_returns_complete_set():
    # Coordination game with two pure equilibria.
    matrix = {
        ("A", "A"): (2, 2),
        ("A", "B"): (0, 0),
        ("B", "A"): (0, 0),
        ("B", "B"): (1, 1),
    }
    adapter = MatrixGameAdapter(matrix, ["A", "B"], ["A", "B"])
    program = compile_interaction_fields(
        adapter,
        mapping_entry={
            "solution_concept": "pure Nash equilibrium in normal-form payoff matrix",
            "game_type": "normal-form payoff matrix game",
        },
    )

    assert field(program, "mutual_best_response_cells").value == [["A", "A"], ["B", "B"]]


def test_tictactoe_immediate_opponent_win_threat_prioritizes_blocking():
    observation = {
        "env_name": "tictactoe",
        "self_moves": ["<C2R2>"],
        "opponent_moves": ["<C1R1>", "<C2R1>"],
        "legal_moves": ["<C3R1>", "<C1R2>", "<C3R2>", "<C1R3>", "<C2R3>", "<C3R3>"],
    }
    program = compile_from_observation("tictactoe", observation)

    assert field(program, "immediate_win_actions").value == []
    assert field(program, "immediate_block_actions").value == ["<C3R1>"]
    rule_ids = [rule.rule_id for rule in program.decision_rules]
    assert rule_ids[:2] == ["win_now", "block_now"]
    assert "immediate_block_actions" in program.small_model_prompt


def test_auction_filters_negative_surplus_overbids():
    observation = {
        "env_name": "first_sealed_auction",
        "valuation": 3.0,
        "legal_moves": ["<0>", "<1>", "<2>", "<3>", "<4>", "<5>"],
    }
    program = compile_from_observation("first_sealed_auction", observation)

    assert field(program, "surplus_if_win_by_bid").value["<5>"] == -2.0
    assert field(program, "overbid_actions").value == ["<4>", "<5>"]
    assert field(program, "expected_utility_by_bid").value["status"] == "unavailable"
    assert "win_probability_by_action" in field(program, "expected_utility_by_bid").value["reason"]
    assert "You are not explaining theory." in program.small_model_prompt
    assert "- surplus_if_win_by_bid:" in program.small_model_prompt
    assert "Calculation: surplus_if_win(bid)=private_value-bid" in program.small_model_prompt
    assert "Value: unavailable" in program.small_model_prompt
    assert "Decision program:" in program.small_model_prompt
    assert "Verifier:" in program.small_model_prompt


def test_missing_probability_or_belief_input_produces_unavailable_fields():
    auction = compile_from_observation(
        "first_sealed_auction",
        {"valuation": 5.0, "legal_moves": ["<0>", "<1>", "<2>"]},
    )
    assert field(auction, "expected_utility_by_bid").value["status"] == "unavailable"

    poker = compile_from_observation(
        "kuhn_poker",
        {"legal_moves": ["<Pass>", "<Bet>"], "private_card": "Q"},
    )
    assert field(poker, "belief_state").value["status"] == "unavailable"
    assert field(poker, "expected_value_by_action").value["status"] == "unavailable"


def test_pig_turn_total_zero_prioritizes_roll_without_fake_chance_values():
    program = compile_from_observation(
        "pig",
        {
            "self_current_score": 25,
            "opponent_current_score": 12,
            "turn_total_score": 0,
            "legal_moves": ["<roll>", "<stop>"],
        },
    )

    assert field(program, "score_after_stop").value == 25
    assert field(program, "stop_wins_now").value is False
    assert field(program, "roll_has_no_bust_loss").value is True
    assert "pig_priority_actions" not in [item.field_id for item in program.computed_fields]
    assert "roll_when_turn_total_zero" in program.small_model_prompt


def test_pig_stop_wins_now_prioritizes_stop():
    program = compile_from_observation(
        "pig",
        {
            "self_current_score": 25,
            "opponent_current_score": 12,
            "turn_total_score": 5,
            "legal_moves": ["<roll>", "<stop>"],
        },
    )

    assert field(program, "score_after_stop").value == 30
    assert field(program, "stop_wins_now").value is True
    assert "stop_if_winning" in program.small_model_prompt


def test_nim_computes_successor_fields_from_legal_actions():
    program = compile_from_observation(
        "nim",
        {
            "legal_moves": [
                "<pile:1, take:1>",
                "<pile:2, take:1>",
                "<pile:2, take:2>",
                "<pile:2, take:3>",
            ],
        },
    )

    assert field(program, "pile_state_from_legal_actions").value == {1: 1, 2: 3}
    assert field(program, "legal_move_effects").value["<pile:2, take:3>"] == {1: 1}
    assert "winning_moves" not in [item.field_id for item in program.computed_fields]
    assert field(program, "opponent_position_value_by_action").value["<pile:2, take:3>"] == "opponent_losing"


def test_prisoners_dilemma_alias_uses_repeated_game_handler():
    program = compile_from_observation(
        "python_iterated_prisoners_dilemma",
        {"self_moves": "", "opponent_moves": "", "legal_moves": ["<Silent>", "<Testify>"]},
    )

    assert program.theory_id == "repeated_game_trigger_strategy"
    assert field(program, "trigger_strategy_state").value == "no_history"
    assert field(program, "opponent_recent_defection").value is False
    assert field(program, "stage_game_worst_case_payoff_by_action").value == {
        "<Silent>": 0,
        "<Testify>": 1,
    }
    assert field(program, "strictly_dominant_stage_actions").value == ["<Testify>"]
    assert field(program, "future_interaction_value").value["status"] == "unavailable"
    assert "recommended_repeated_game_actions" not in [item.field_id for item in program.computed_fields]
    assert "do not select <Silent> solely from empty history" in program.small_model_prompt


def test_prisoners_dilemma_observed_defection_sets_retaliation_condition():
    program = compile_from_observation(
        "python_iterated_prisoners_dilemma",
        {"self_moves": "C", "opponent_moves": "D", "legal_moves": ["<Silent>", "<Testify>"]},
    )

    assert field(program, "trigger_strategy_state").value == "punish"
    assert field(program, "opponent_recent_defection").value is True
    assert "retaliate_after_observed_defection" in program.small_model_prompt


def test_required_game_schema_fields_are_present_even_when_unavailable():
    for game_id in ["negotiation", "kuhn_poker", "connect4"]:
        program = compile_from_observation(game_id, {"legal_moves": ["<A>"]})
        field_ids = {item.field_id for item in program.computed_fields}
        required = set(load_game_schema(game_id).get("required_derived_fields", {}))
        assert required <= field_ids


def test_negotiation_required_fields_compute_accept_payoff_from_complement():
    program = compile_from_observation(
        "negotiation",
        {
            "self_value_vector": [10, 1, 7],
            "item_pool": [5, 5, 5],
            "turn_type": "Proposal",
            "most_recent_proposal": ["2", "5", "2"],
            "legal_moves": ["<Agree>", "<Proposal: [5, 0, 5]>", "<Proposal: [3, 0, 3]>"],
        },
    )

    assert field(program, "self_payoff_of_latest_offer").value == 51
    assert field(program, "latest_offer_if_any").value["my_accept_allocation"] == [3, 0, 3]
    assert field(program, "proposal_payoff_by_candidate").value["<Proposal: [5, 0, 5]>"] == 85
    assert field(program, "legal_agree_available").value is True
    assert field(program, "acceptance_threshold_model").value["status"] == "unavailable"


def test_low_engineering_profile_filters_nim_fields_and_removes_decision_rules():
    program = compile_from_observation(
        "nim",
        {
            "legal_moves": [
                "<pile:1, take:1>",
                "<pile:2, take:1>",
                "<pile:2, take:2>",
                "<pile:2, take:3>",
            ],
        },
        engineering_profile="low_engineering",
        strict=True,
    )

    field_ids = {item.field_id for item in program.computed_fields}
    assert field_ids == {
        "pile_state_from_legal_actions",
        "legal_move_effects",
        "misere_phase_by_action",
        "singleton_parity_by_action",
        "misere_rule_check",
    }
    assert program.decision_rules == []
    assert "prefer_opponent_losing_position" not in program.small_model_prompt
    assert "minimize_successor_nim_sum" not in program.small_model_prompt


def test_high_engineering_profile_keeps_allowed_kuhn_fields_only():
    program = compile_from_observation(
        "kuhn_poker",
        {
            "legal_moves": ["<Pass>", "<Bet>"],
            "private_card": "Q",
            "moves": "p",
            "player_idx": 1,
        },
        engineering_profile="high_engineering",
        strict=True,
    )

    field_ids = {item.field_id for item in program.computed_fields}
    assert field_ids == {
        "turn_and_history_perspective",
        "my_player_id",
        "current_actor",
        "is_my_turn",
        "public_history",
        "private_card_fields",
        "legal_action_context",
        "facing_bet",
        "hand_strength_class",
        "possible_opponent_cards_excluding_private_card",
        "opponent_card_belief_probabilities",
        "action_payoff_by_opponent_card",
        "expected_value_by_action",
    }
    assert program.decision_rules == []


def test_high_engineering_distill_filters_verifier_checks_to_retained_fields():
    program = compile_from_observation(
        "kuhn_poker",
        {
            "legal_moves": ["<Pass>", "<Bet>"],
            "private_card": "Q",
            "moves": "p",
            "player_idx": 1,
        },
        engineering_profile="high_engineering",
        engineering_profile_mode="distill",
        strict=True,
    )

    field_ids = {item.field_id for item in program.computed_fields}
    verifier_field_ids = {check.field_id for check in program.verifier_checks if check.field_id}
    assert verifier_field_ids <= field_ids
    assert "belief_state" not in verifier_field_ids


def test_high_engineering_reasoning_mode_removes_nim_decision_rules():
    program = compile_from_observation(
        "nim",
        {
            "legal_moves": [
                "<pile:1, take:1>",
                "<pile:2, take:1>",
                "<pile:2, take:2>",
                "<pile:2, take:3>",
            ],
        },
        engineering_profile="high_engineering",
        engineering_profile_mode="reasoning",
        strict=True,
    )

    assert program.decision_rules == []
    assert "prefer_opponent_losing_position" not in program.small_model_prompt
    assert "minimize_successor_nim_sum" not in program.small_model_prompt


def test_high_engineering_distill_mode_keeps_only_rules_supported_by_allowed_fields():
    program = compile_from_observation(
        "nim",
        {
            "legal_moves": [
                "<pile:1, take:1>",
                "<pile:2, take:1>",
                "<pile:2, take:2>",
                "<pile:2, take:3>",
            ],
        },
        engineering_profile="high_engineering",
        engineering_profile_mode="distill",
        strict=True,
    )

    rule_ids = [rule.rule_id for rule in program.decision_rules]
    assert rule_ids == ["minimize_successor_nim_sum"]
    assert "minimize_successor_nim_sum" in program.small_model_prompt
    assert "prefer_opponent_losing_position" not in program.small_model_prompt


def test_high_engineering_distill_mode_keeps_pig_selection_rules():
    program = compile_from_observation(
        "pig",
        {
            "self_current_score": 25,
            "opponent_current_score": 12,
            "turn_total_score": 5,
            "legal_moves": ["<roll>", "<stop>"],
        },
        engineering_profile="high_engineering",
        engineering_profile_mode="distill",
        strict=True,
    )

    rule_ids = [rule.rule_id for rule in program.decision_rules]
    assert rule_ids == [
        "stop_if_winning",
        "roll_if_no_bust_loss",
        "maximize_one_roll_heuristic_value",
    ]
    assert "stop_if_winning" in program.small_model_prompt
    assert "maximize_one_roll_heuristic_value" in program.small_model_prompt


def test_connect4_required_tactical_fields_are_computed():
    program = compile_from_observation(
        "connect4",
        {
            "self_moves": ["<C1>", "<C1>", "<C1>"],
            "opponent_moves": [],
            "legal_moves": ["<C1>", "<C2>", "<C3>", "<C4>", "<C5>", "<C6>", "<C7>"],
        },
    )

    assert field(program, "column_heights").value["<C1>"] == 3
    assert field(program, "playable_row_by_column").value["<C1>"] == 4
    assert field(program, "immediate_win_columns").value == ["<C1>"]
    assert field(program, "heuristic_tiebreak_center_distance_by_column").value["<C4>"] == 0


def test_kuhn_poker_required_information_set_fields_are_computed():
    program = compile_from_observation(
        "kuhn_poker",
        {"private_card": "K", "history": "", "legal_moves": ["<Pass>", "<Bet>"]},
    )

    assert field(program, "private_card_fields").value["card"] == "K"
    assert field(program, "hand_strength_class").value == "strong"
    assert field(program, "possible_opponent_cards_excluding_private_card").value == ["J", "Q"]
    assert field(program, "opponent_card_belief_probabilities").value == {"J": 0.5, "Q": 0.5}
    assert field(program, "current_actor").value["status"] == "unavailable"


def test_kuhn_poker_numeric_observation_fields_are_normalized():
    program = compile_from_observation(
        "kuhn_poker",
        {"card": "1", "moves": "b", "player_idx": 1, "legal_moves": ["<Pass>", "<Bet>"]},
    )

    assert field(program, "my_player_id").value == 1
    assert field(program, "public_history").value == "b"
    assert field(program, "private_card_fields").value["card"] == "Q"
    assert field(program, "hand_strength_class").value == "medium"
    assert field(program, "possible_opponent_cards_excluding_private_card").value == ["J", "K"]
    assert field(program, "facing_bet").value is True
    assert field(program, "legal_action_context").value["<Pass>"] == "fold"
    assert field(program, "legal_action_context").value["<Bet>"] == "call_or_raise"
    assert field(program, "opponent_card_belief_probabilities").value == {"J": 0.5, "K": 0.5}
    assert field(program, "action_payoff_by_opponent_card").value == {
        "<Pass>": {"J": -1.0, "K": -1.0},
        "<Bet>": {"J": 2.0, "K": -2.0},
    }
    assert field(program, "expected_value_by_action").value == {"<Pass>": -1.0, "<Bet>": 0.0}


def test_kuhn_poker_facing_bet_ev_prefers_call_with_king_and_fold_with_jack():
    king_program = compile_from_observation(
        "kuhn_poker",
        {"card": "2", "moves": "b", "player_idx": 1, "legal_moves": ["<Pass>", "<Bet>"]},
        engineering_profile="high_engineering",
        engineering_profile_mode="distill",
        strict=True,
    )
    jack_program = compile_from_observation(
        "kuhn_poker",
        {"card": "0", "moves": "b", "player_idx": 1, "legal_moves": ["<Pass>", "<Bet>"]},
        engineering_profile="high_engineering",
        engineering_profile_mode="distill",
        strict=True,
    )

    assert field(king_program, "expected_value_by_action").value == {"<Pass>": -1.0, "<Bet>": 2.0}
    assert field(jack_program, "expected_value_by_action").value == {"<Pass>": -1.0, "<Bet>": -2.0}
    assert [rule.rule_id for rule in king_program.decision_rules] == ["maximize_expected_value"]
    assert "maximize_expected_value" in king_program.small_model_prompt


def test_required_field_aliases_prevent_duplicate_unavailable_fields():
    tic = compile_from_observation(
        "tictactoe",
        {"self_moves": [], "opponent_moves": [], "legal_moves": ["<C1R1>", "<C2R2>"]},
    )
    tic_ids = {item.field_id for item in tic.computed_fields}
    assert "immediate_win_actions" in tic_ids
    assert "terminal_win_actions" not in tic_ids

    nim = compile_from_observation(
        "nim",
        {"legal_moves": ["<pile:1, take:1>", "<pile:2, take:1>", "<pile:2, take:2>"]},
    )
    nim_ids = {item.field_id for item in nim.computed_fields}
    assert "pile_state_from_legal_actions" in nim_ids
    assert "pile_state" not in nim_ids
    assert "phase_classification_by_action" not in nim_ids


def test_pig_and_auction_required_fields_are_computed_not_placeholder_only():
    pig = compile_from_observation(
        "pig",
        {
            "self_current_score": 12,
            "opponent_current_score": 9,
            "turn_total_score": 4,
            "legal_moves": ["<roll>", "<stop>"],
        },
    )
    assert field(pig, "current_scores").value == {"self_score": 12, "opponent_score": 9, "turn_total": 4}
    assert field(pig, "target_score").value == 30
    assert "<roll>" in field(pig, "stop_or_roll_comparison").value

    auction = compile_from_observation(
        "first_sealed_auction",
        {"valuation": 3, "legal_moves": ["<0>", "<1>", "<2>", "<3>", "<4>"]},
    )
    assert field(auction, "private_valuation").value == 3.0
    assert field(auction, "bid_space").value["<4>"] == 4
    assert field(auction, "zero_surplus_actions").value == ["<3>"]
    assert field(auction, "positive_surplus_actions").value == ["<0>", "<1>", "<2>"]


def test_liars_dice_does_not_attach_auction_handler():
    program = compile_from_observation(
        "liars_dice",
        {"legal_moves": ["<Liar>", "<2 dices, 3 value>"]},
    )

    field_ids = [item.field_id for item in program.computed_fields]
    assert "expected_utility_by_bid" not in field_ids
    assert program.theory_id == "stochastic_expected_value+belief_weighted_expected_utility"


def test_compiler_processes_every_repo_game_mapping_safely():
    games = [
        "tictactoe",
        "connect4",
        "breakthrough",
        "nim",
        "pig",
        "first_sealed_auction",
        "kuhn_poker",
        "liars_dice",
        "negotiation",
        "prisoners_dilemma",
    ]
    for game_id in games:
        program = compile_from_observation(game_id, {"legal_moves": ["<A>"]})
        assert program.game_id == game_id
        assert program.computed_fields
        assert program.small_model_prompt
        for item in program.computed_fields:
            assert item.calculation["steps"]
            assert item.decision_role
            assert item.operator
            assert item.invariants
