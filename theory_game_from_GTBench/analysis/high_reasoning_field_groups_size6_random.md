# Random Size-6 High-Reasoning Field Groups

## Purpose

This file samples random field groups from
`high_reasoning_field_bank_all_games.md` for experimentation.

## Sampling Rule

- Source: the derived-only high-reasoning field bank.
- Group size: `6`.
- Sampling style: random with fixed seed `42`.
- Per-game count: `10` groups.
- Diversity constraint used here:
  for any two groups within the same game, overlap is at most `4` fields.

This is a stronger version of "at least 2 fields must differ" and avoids
near-duplicate groups.

## Tic-Tac-Toe

### Group 1

- `open_lines_by_player`
- `immediate_block_actions`
- `center_control_status`
- `line_completion_distance_by_action`
- `draw_preserving_actions`
- `continuation_pressure_by_action`

### Group 2

- `line_status_by_line`
- `immediate_block_actions`
- `dual_threat_count_by_action`
- `corner_pair_potential_by_action`
- `line_completion_distance_by_action`
- `symmetry_class_by_action`

### Group 3

- `open_lines_by_player`
- `fork_creation_actions`
- `fork_block_actions`
- `center_control_status`
- `line_completion_distance_by_action`
- `draw_preserving_actions`

### Group 4

- `fork_creation_actions`
- `fork_block_actions`
- `opponent_immediate_reply_threats_by_action`
- `forced_reply_count_by_action`
- `corner_pair_potential_by_action`
- `continuation_pressure_by_action`

### Group 5

- `open_lines_by_player`
- `dual_threat_count_by_action`
- `opponent_immediate_reply_threats_by_action`
- `center_control_status`
- `line_completion_distance_by_action`
- `draw_preserving_actions`

### Group 6

- `open_lines_by_player`
- `immediate_win_actions`
- `immediate_block_actions`
- `fork_creation_actions`
- `center_control_status`
- `symmetry_class_by_action`

### Group 7

- `open_lines_by_player`
- `fork_creation_actions`
- `fork_block_actions`
- `opponent_immediate_reply_threats_by_action`
- `center_control_status`
- `corner_pair_potential_by_action`

### Group 8

- `immediate_win_actions`
- `immediate_block_actions`
- `dual_threat_count_by_action`
- `forced_reply_count_by_action`
- `center_control_status`
- `symmetry_class_by_action`

### Group 9

- `immediate_win_actions`
- `forced_reply_count_by_action`
- `center_control_status`
- `corner_pair_potential_by_action`
- `draw_preserving_actions`
- `symmetry_class_by_action`

### Group 10

- `immediate_win_actions`
- `fork_creation_actions`
- `opponent_immediate_reply_threats_by_action`
- `draw_preserving_actions`
- `symmetry_class_by_action`
- `continuation_pressure_by_action`

## Connect Four

### Group 1

- `immediate_win_columns`
- `immediate_block_columns`
- `diagonal_completion_windows_by_column`
- `opponent_immediate_reply_wins_by_column`
- `odd_even_threat_parity_by_column`
- `center_distance_by_column`

### Group 2

- `threat_cells_by_player`
- `vertical_completion_windows_by_column`
- `horizontal_completion_windows_by_column`
- `diagonal_completion_windows_by_column`
- `support_dependency_by_column`
- `odd_even_threat_parity_by_column`

### Group 3

- `playable_row_by_column`
- `immediate_block_columns`
- `vertical_completion_windows_by_column`
- `unsafe_columns`
- `center_distance_by_column`
- `forcing_status_by_column`

### Group 4

- `vertical_completion_windows_by_column`
- `horizontal_completion_windows_by_column`
- `double_threat_columns`
- `support_dependency_by_column`
- `odd_even_threat_parity_by_column`
- `future_playability_shift_by_column`

### Group 5

- `immediate_block_columns`
- `threat_cells_by_player`
- `diagonal_completion_windows_by_column`
- `unsafe_columns`
- `future_playability_shift_by_column`
- `forcing_status_by_column`

### Group 6

- `playable_row_by_column`
- `threat_cells_by_player`
- `vertical_completion_windows_by_column`
- `horizontal_completion_windows_by_column`
- `center_distance_by_column`
- `future_playability_shift_by_column`

### Group 7

- `playable_row_by_column`
- `immediate_block_columns`
- `double_threat_columns`
- `support_dependency_by_column`
- `future_playability_shift_by_column`
- `forcing_status_by_column`

### Group 8

- `immediate_win_columns`
- `vertical_completion_windows_by_column`
- `horizontal_completion_windows_by_column`
- `opponent_immediate_reply_wins_by_column`
- `unsafe_columns`
- `future_playability_shift_by_column`

### Group 9

- `playable_row_by_column`
- `immediate_block_columns`
- `diagonal_completion_windows_by_column`
- `unsafe_columns`
- `support_dependency_by_column`
- `future_playability_shift_by_column`

### Group 10

- `playable_row_by_column`
- `immediate_win_columns`
- `immediate_block_columns`
- `diagonal_completion_windows_by_column`
- `opponent_immediate_reply_wins_by_column`
- `unsafe_columns`

## Breakthrough

### Group 1

- `opponent_immediate_promotion_threats`
- `destination_defense_status_by_action`
- `promotion_distance_by_piece`
- `fastest_promotion_lane_by_piece`
- `back_rank_guard_status`
- `opponent_counterpromotion_risk_by_action`

### Group 2

- `immediate_promotion_actions`
- `destination_defense_status_by_action`
- `recapture_risk_by_action`
- `promotion_distance_by_piece`
- `fastest_promotion_lane_by_piece`
- `lane_blocker_count_by_piece`

### Group 3

- `opponent_immediate_promotion_threats`
- `capture_actions`
- `promotion_distance_by_piece`
- `fastest_promotion_lane_by_piece`
- `material_swing_by_action`
- `race_leader_after_action`

### Group 4

- `immediate_promotion_actions`
- `recapture_risk_by_action`
- `material_swing_by_action`
- `back_rank_guard_status`
- `race_leader_after_action`
- `continuation_race_pressure_by_action`

### Group 5

- `opponent_immediate_promotion_threats`
- `destination_defense_status_by_action`
- `lane_blocker_count_by_piece`
- `material_swing_by_action`
- `race_leader_after_action`
- `continuation_race_pressure_by_action`

### Group 6

- `promotion_distance_by_piece`
- `fastest_promotion_lane_by_piece`
- `lane_blocker_count_by_piece`
- `material_swing_by_action`
- `back_rank_guard_status`
- `continuation_race_pressure_by_action`

### Group 7

- `opponent_immediate_promotion_threats`
- `capture_actions`
- `material_swing_by_action`
- `back_rank_guard_status`
- `opponent_counterpromotion_risk_by_action`
- `continuation_race_pressure_by_action`

### Group 8

- `destination_defense_status_by_action`
- `promotion_distance_by_piece`
- `fastest_promotion_lane_by_piece`
- `back_rank_guard_status`
- `race_leader_after_action`
- `continuation_race_pressure_by_action`

### Group 9

- `immediate_promotion_actions`
- `destination_defense_status_by_action`
- `promotion_distance_by_piece`
- `race_leader_after_action`
- `opponent_counterpromotion_risk_by_action`
- `continuation_race_pressure_by_action`

### Group 10

- `immediate_promotion_actions`
- `recapture_risk_by_action`
- `promotion_distance_by_piece`
- `material_swing_by_action`
- `passed_pawn_flag_by_action`
- `continuation_race_pressure_by_action`

## Nim

### Group 1

- `large_pile_count_by_action`
- `phase_classification_by_action`
- `zero_nim_sum_flag_by_action`
- `all_singletons_flag_by_action`
- `terminal_take_last_flag_by_action`
- `opponent_position_value_by_action`

### Group 2

- `total_matches_after_action`
- `large_pile_count_by_action`
- `all_singletons_flag_by_action`
- `terminal_take_last_flag_by_action`
- `endgame_parity_target_by_action`
- `opponent_position_value_by_action`

### Group 3

- `large_pile_count_by_action`
- `nim_sum_by_action`
- `all_singletons_flag_by_action`
- `terminal_take_last_flag_by_action`
- `forced_loss_indicator`
- `action_equivalence_classes_by_successor_state`

### Group 4

- `nonzero_pile_count_by_action`
- `large_pile_count_by_action`
- `phase_classification_by_action`
- `nim_sum_by_action`
- `zero_nim_sum_flag_by_action`
- `opponent_position_value_by_action`

### Group 5

- `total_matches_after_action`
- `phase_classification_by_action`
- `nim_sum_by_action`
- `zero_nim_sum_flag_by_action`
- `all_singletons_flag_by_action`
- `action_equivalence_classes_by_successor_state`

### Group 6

- `legal_move_effects`
- `singleton_count_by_action`
- `phase_classification_by_action`
- `endgame_parity_target_by_action`
- `forced_loss_indicator`
- `action_equivalence_classes_by_successor_state`

### Group 7

- `legal_move_effects`
- `nonzero_pile_count_by_action`
- `zero_nim_sum_flag_by_action`
- `all_singletons_flag_by_action`
- `endgame_parity_target_by_action`
- `action_equivalence_classes_by_successor_state`

### Group 8

- `legal_move_effects`
- `nonzero_pile_count_by_action`
- `large_pile_count_by_action`
- `singleton_count_by_action`
- `phase_classification_by_action`
- `endgame_parity_target_by_action`

### Group 9

- `total_matches_after_action`
- `large_pile_count_by_action`
- `endgame_parity_target_by_action`
- `opponent_position_value_by_action`
- `forced_loss_indicator`
- `action_equivalence_classes_by_successor_state`

### Group 10

- `total_matches_after_action`
- `large_pile_count_by_action`
- `singleton_count_by_action`
- `zero_nim_sum_flag_by_action`
- `endgame_parity_target_by_action`
- `opponent_position_value_by_action`

## Pig

### Group 1

- `score_after_stop`
- `bust_probability`
- `expected_safe_gain`
- `one_roll_expected_value`
- `score_gap`
- `roll_vs_stop_margin`

### Group 2

- `bust_probability`
- `expected_safe_gain`
- `one_roll_expected_value`
- `bank_value_ratio`
- `desperation_level`
- `roll_vs_stop_margin`

### Group 3

- `stop_leaves_opponent_near_finish`
- `bust_probability`
- `safe_roll_outcome_distribution`
- `self_distance_to_target`
- `desperation_level`
- `roll_vs_stop_margin`

### Group 4

- `bust_probability`
- `bust_loss`
- `score_gap`
- `opponent_distance_to_target`
- `desperation_level`
- `roll_vs_stop_margin`

### Group 5

- `stop_leaves_opponent_near_finish`
- `bust_probability`
- `expected_safe_gain`
- `self_distance_to_target`
- `race_pressure_class`
- `desperation_level`

### Group 6

- `one_roll_expected_value`
- `score_gap`
- `opponent_distance_to_target`
- `race_pressure_class`
- `desperation_level`
- `roll_vs_stop_margin`

### Group 7

- `score_after_stop`
- `bust_probability`
- `safe_roll_outcome_distribution`
- `one_roll_expected_value`
- `score_gap`
- `opponent_distance_to_target`

### Group 8

- `score_after_stop`
- `stop_leaves_opponent_near_finish`
- `bust_loss`
- `opponent_distance_to_target`
- `bank_value_ratio`
- `roll_vs_stop_margin`

### Group 9

- `expected_safe_gain`
- `score_gap`
- `opponent_distance_to_target`
- `race_pressure_class`
- `bank_value_ratio`
- `desperation_level`

### Group 10

- `stop_wins_now`
- `stop_leaves_opponent_near_finish`
- `bust_probability`
- `safe_roll_outcome_distribution`
- `self_distance_to_target`
- `bank_value_ratio`

## First-Sealed Auction

### Group 1

- `bid_shading_amount`
- `overbid_actions`
- `zero_surplus_actions`
- `tie_case_if_bid_equals_opponent`
- `robust_bid_interval_under_belief_range`
- `aggressiveness_class_by_bid`

### Group 2

- `bid_rank_order`
- `win_probability_assumption_by_bid`
- `tie_case_if_bid_equals_opponent`
- `profit_floor_by_bid`
- `regret_if_lose_with_low_bid`
- `regret_if_win_with_high_bid`

### Group 3

- `bid_rank_order`
- `overbid_actions`
- `zero_surplus_actions`
- `surplus_if_win_by_bid`
- `win_probability_assumption_by_bid`
- `regret_if_win_with_high_bid`

### Group 4

- `bid_shading_ratio`
- `zero_surplus_actions`
- `win_probability_assumption_by_bid`
- `expected_surplus_by_bid`
- `tie_case_if_bid_equals_opponent`
- `regret_if_lose_with_low_bid`

### Group 5

- `overbid_actions`
- `surplus_if_win_by_bid`
- `profit_floor_by_bid`
- `regret_if_lose_with_low_bid`
- `regret_if_win_with_high_bid`
- `aggressiveness_class_by_bid`

### Group 6

- `bid_rank_order`
- `bid_shading_amount`
- `overbid_actions`
- `win_probability_assumption_by_bid`
- `tie_case_if_bid_equals_opponent`
- `profit_floor_by_bid`

### Group 7

- `bid_shading_amount`
- `overbid_actions`
- `positive_surplus_actions`
- `surplus_if_win_by_bid`
- `expected_surplus_by_bid`
- `aggressiveness_class_by_bid`

### Group 8

- `bid_rank_order`
- `overbid_actions`
- `win_probability_assumption_by_bid`
- `regret_if_lose_with_low_bid`
- `regret_if_win_with_high_bid`
- `robust_bid_interval_under_belief_range`

### Group 9

- `zero_surplus_actions`
- `surplus_if_win_by_bid`
- `win_probability_assumption_by_bid`
- `regret_if_win_with_high_bid`
- `robust_bid_interval_under_belief_range`
- `aggressiveness_class_by_bid`

### Group 10

- `bid_rank_order`
- `zero_surplus_actions`
- `positive_surplus_actions`
- `profit_floor_by_bid`
- `regret_if_lose_with_low_bid`
- `regret_if_win_with_high_bid`

## Kuhn Poker

### Group 1

- `hand_strength_class`
- `legal_action_context`
- `possible_opponent_cards`
- `call_value_by_opponent_card`
- `expected_value_by_action`
- `action_risk_profile`

### Group 2

- `information_set_class`
- `hand_strength_class`
- `fold_value`
- `bet_fold_equity`
- `expected_value_by_action`
- `opponent_response_if_i_bet`

### Group 3

- `information_set_class`
- `possible_opponent_cards`
- `posterior_over_opponent_cards`
- `showdown_result_by_opponent_card`
- `call_value_by_opponent_card`
- `bluff_incentive`

### Group 4

- `information_set_class`
- `pot_size`
- `facing_bet`
- `call_value_by_opponent_card`
- `bluff_incentive`
- `value_bet_incentive`

### Group 5

- `legal_action_context`
- `showdown_result_by_opponent_card`
- `call_value_by_opponent_card`
- `bluff_incentive`
- `expected_value_by_action`
- `opponent_response_if_i_bet`

### Group 6

- `information_set_class`
- `pot_size`
- `facing_bet`
- `possible_opponent_cards`
- `bet_fold_equity`
- `action_risk_profile`

### Group 7

- `pot_size`
- `possible_opponent_cards`
- `call_value_by_opponent_card`
- `bluff_incentive`
- `value_bet_incentive`
- `action_risk_profile`

### Group 8

- `legal_action_context`
- `bluff_incentive`
- `value_bet_incentive`
- `expected_value_by_action`
- `opponent_response_if_i_bet`
- `action_risk_profile`

### Group 9

- `legal_action_context`
- `possible_opponent_cards`
- `posterior_over_opponent_cards`
- `showdown_result_by_opponent_card`
- `bluff_incentive`
- `value_bet_incentive`

### Group 10

- `hand_strength_class`
- `facing_bet`
- `posterior_over_opponent_cards`
- `showdown_result_by_opponent_card`
- `fold_value`
- `action_risk_profile`

## Liar's Dice

### Group 1

- `my_face_count`
- `probability_each_raise_true`
- `challenge_threshold_gap`
- `aggressive_raise_candidates`
- `opponent_bluff_likelihood_from_history`
- `consistency_with_private_evidence`

### Group 2

- `my_bid_support_count`
- `slack_above_current_bid`
- `bluff_pressure_index`
- `aggressive_raise_candidates`
- `opponent_bluff_likelihood_from_history`
- `consistency_with_private_evidence`

### Group 3

- `legal_raise_space`
- `my_face_count`
- `probability_each_raise_true`
- `bluff_pressure_index`
- `conservative_raise_candidates`
- `liar_vs_raise_ev_proxy`

### Group 4

- `minimum_next_bid_rule`
- `legal_raise_space`
- `my_face_count`
- `my_bid_support_count`
- `challenge_threshold_gap`
- `conservative_raise_candidates`

### Group 5

- `minimum_next_bid_rule`
- `my_bid_support_count`
- `probability_current_bid_true`
- `probability_each_raise_true`
- `challenge_threshold_gap`
- `liar_vs_raise_ev_proxy`

### Group 6

- `minimum_next_bid_rule`
- `my_bid_support_count`
- `probability_current_bid_true`
- `bluff_pressure_index`
- `conservative_raise_candidates`
- `consistency_with_private_evidence`

### Group 7

- `minimum_next_bid_rule`
- `legal_raise_space`
- `unknown_dice_count`
- `bluff_pressure_index`
- `conservative_raise_candidates`
- `liar_vs_raise_ev_proxy`

### Group 8

- `minimum_next_bid_rule`
- `my_face_count`
- `my_bid_support_count`
- `probability_each_raise_true`
- `bluff_pressure_index`
- `consistency_with_private_evidence`

### Group 9

- `legal_raise_space`
- `slack_above_current_bid`
- `challenge_threshold_gap`
- `conservative_raise_candidates`
- `liar_vs_raise_ev_proxy`
- `consistency_with_private_evidence`

### Group 10

- `minimum_next_bid_rule`
- `my_face_count`
- `probability_current_bid_true`
- `probability_each_raise_true`
- `bluff_pressure_index`
- `conservative_raise_candidates`

## Negotiation

### Group 1

- `self_payoff_of_latest_offer`
- `bundle_substitutability_from_self_view`
- `opponent_demand_pattern_from_history`
- `utterance_offer_consistency`
- `pareto_candidate_status_from_self_side`
- `agree_vs_counteroffer_margin`

### Group 2

- `disagreement_payoff`
- `minimum_acceptable_payoff`
- `max_self_payoff_feasible_offer`
- `offer_feasibility_check`
- `acceptance_probability_proxy_by_offer`
- `strategic_stage_goal`

### Group 3

- `disagreement_payoff`
- `max_self_payoff_feasible_offer`
- `concession_cost_by_candidate_offer`
- `bundle_substitutability_from_self_view`
- `acceptance_probability_proxy_by_offer`
- `opponent_demand_pattern_from_history`

### Group 4

- `self_payoff_of_latest_offer`
- `minimum_acceptable_payoff`
- `offer_feasibility_check`
- `opponent_demand_pattern_from_history`
- `pareto_candidate_status_from_self_side`
- `agree_vs_counteroffer_margin`

### Group 5

- `self_payoff_of_latest_offer`
- `disagreement_payoff`
- `max_self_payoff_feasible_offer`
- `high_value_item_priority`
- `opponent_demand_pattern_from_history`
- `utterance_offer_consistency`

### Group 6

- `self_payoff_of_latest_offer`
- `max_self_payoff_feasible_offer`
- `concession_cost_by_candidate_offer`
- `acceptance_probability_proxy_by_offer`
- `pareto_candidate_status_from_self_side`
- `agree_vs_counteroffer_margin`

### Group 7

- `self_payoff_of_latest_offer`
- `disagreement_payoff`
- `max_self_payoff_feasible_offer`
- `high_value_item_priority`
- `offer_feasibility_check`
- `agree_vs_counteroffer_margin`

### Group 8

- `max_self_payoff_feasible_offer`
- `high_value_item_priority`
- `bundle_substitutability_from_self_view`
- `offer_feasibility_check`
- `acceptance_probability_proxy_by_offer`
- `strategic_stage_goal`

### Group 9

- `self_payoff_of_latest_offer`
- `disagreement_payoff`
- `max_self_payoff_feasible_offer`
- `high_value_item_priority`
- `acceptance_probability_proxy_by_offer`
- `strategic_stage_goal`

### Group 10

- `disagreement_payoff`
- `concession_cost_by_candidate_offer`
- `opponent_demand_pattern_from_history`
- `utterance_offer_consistency`
- `strategic_stage_goal`
- `agree_vs_counteroffer_margin`

## Iterated Prisoner's Dilemma

### Group 1

- `opponent_recent_actions`
- `opponent_defection_rate`
- `reciprocity_pattern_flag`
- `trigger_strategy_state`
- `stage_game_payoff_table`
- `punishment_credibility`

### Group 2

- `opponent_defection_rate`
- `opponent_streak_type`
- `reciprocity_pattern_flag`
- `trigger_strategy_state`
- `one_step_best_response`
- `repair_opportunity_flag`

### Group 3

- `trigger_strategy_state`
- `last_round_outcome`
- `punishment_credibility`
- `exploitation_risk_if_silent`
- `repair_opportunity_flag`
- `current_action_long_run_tradeoff`

### Group 4

- `opponent_recent_actions`
- `reciprocity_pattern_flag`
- `forgiveness_pattern_flag`
- `trigger_strategy_state`
- `last_round_outcome`
- `punishment_credibility`

### Group 5

- `opponent_streak_type`
- `reciprocity_pattern_flag`
- `forgiveness_pattern_flag`
- `one_step_best_response`
- `punishment_credibility`
- `current_action_long_run_tradeoff`

### Group 6

- `opponent_recent_actions`
- `opponent_streak_type`
- `reciprocity_pattern_flag`
- `forgiveness_pattern_flag`
- `stage_game_payoff_table`
- `future_cooperation_value_proxy`

### Group 7

- `last_round_outcome`
- `stage_game_payoff_table`
- `one_step_best_response`
- `punishment_credibility`
- `exploitation_risk_if_silent`
- `repair_opportunity_flag`

### Group 8

- `forgiveness_pattern_flag`
- `trigger_strategy_state`
- `last_round_outcome`
- `stage_game_payoff_table`
- `future_cooperation_value_proxy`
- `current_action_long_run_tradeoff`

### Group 9

- `opponent_recent_actions`
- `opponent_streak_type`
- `trigger_strategy_state`
- `future_cooperation_value_proxy`
- `repair_opportunity_flag`
- `current_action_long_run_tradeoff`

### Group 10

- `opponent_recent_actions`
- `opponent_defection_rate`
- `opponent_streak_type`
- `one_step_best_response`
- `punishment_credibility`
- `repair_opportunity_flag`
