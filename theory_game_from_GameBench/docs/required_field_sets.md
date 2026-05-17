# Required Field Sets

This document is the source-of-truth draft for fixed `required_field_analysis`
field sets. Code should only be updated after these sets are reviewed against
real transcripts.

Principles:
- Required fields are the minimum fields that must be computed for every
  decision in the action-space context.
- Optional fields may be useful but should not be forced if they are mostly
  formatting, redundant, or only sometimes relevant.
- Each required set must be a subset of the context `active_fields` in
  `prompts/theory_fields.py`.
- Required sets should remove field-selection variance so experiments measure
  field-value quality and action consistency.

## Air, Land, and Sea

### normal_deploy_improvise_withdraw

Required:
- playable_faceup_cards_by_matching_theater
- playable_facedown_cards_by_theater
- withdrawal_points_given_remaining_hand
- current_theater_majority_status
- card_conservation_value
- faceup_deploy_control_swing
- facedown_improvise_information_value
- action_risk_by_commitment_and_information
- candidate_card_or_withdraw_values

Optional:
- none

Rationale:
The main turn always requires comparing legal face-up plays, face-down
improvises, and withdrawal against theater control and future hand value.

Validation:
- Legal card/theater constraints are grounded in available actions.
- Withdrawal is compared against continuation value.
- Candidate values mention the selected action and the strongest alternatives.

### tactical_effect_resolution

Required:
- triggering_tactical_card
- legal_effect_targets_or_extra_play_options
- own_vs_opponent_card_ownership
- control_swing_after_effect
- reveal_or_cover_information_cost
- effect_target_risk_by_option
- do_nothing_or_skip_value_if_available
- candidate_effect_target_values

Optional:
- none

Rationale:
Follow-up effects are highly rule-sensitive. The agent must know the triggering
card, legal targets, ownership, control impact, and skip value if present.

Validation:
- Effect targets are legal and refer to visible/action-listed objects.
- The selected target has a concrete control or risk advantage.
- Skip/no-op is considered when available.

## Arctic Scavengers

### resource_gathering

Required:
- available_standard_and_modifier_cards
- unused_once_per_round_actions
- dig_draw_hunt_hire_trash_feasibility
- food_and_medicine_budget
- deck_improvement_vs_skirmish_cost
- resource_action_cost_or_risk
- candidate_resource_action_values
- openended_list_command

Optional:
- none

Rationale:
Resource turns require checking usable cards, once-per-round constraints,
feasible commands, budgets, and whether improving the deck is worth weakening
the skirmish.

Validation:
- Commands only use available cards/resources.
- Once-per-round actions are not reused.
- The openended response follows the required command format.

### interrupt_response

Required:
- opponent_announced_action
- available_sniper_or_saboteur_cards
- valid_interrupt_targets
- value_of_canceling_opponent_action
- discard_cost_of_interrupt
- interrupt_target_or_discard_risk
- interrupt_feasibility_by_action
- candidate_interrupt_values

Optional:
- none

Rationale:
Interrupts are useful only when feasible and when canceling the opponent action
is worth the discard or target risk.

Validation:
- Interrupt action is legal for the current response window.
- Target/discard choices are available in the observation.
- Candidate values compare interrupting versus declining.

### skirmish_action

Required:
- own_visible_fight_and_people_score
- opponent_visible_fight_and_people_score
- sniper_or_saboteur_targets
- contested_resource_value
- skirmish_action_risk
- candidate_skirmish_action_values

Optional:
- none

Rationale:
Skirmish choices depend on visible fight/people scores, available tactical
targets, contested resource value, and whether spending cards improves the
contest enough.

Validation:
- Score values are read from the visible state.
- Target cards are legal and valuable.
- STOP/pass is chosen when extra action risk exceeds value.

### dig_card_selection

Required:
- drawn_junkyard_cards
- card_added_to_reserve_value
- cards_returned_to_junkyard_cost
- card_keep_risk_or_opportunity_cost
- candidate_dig_keep_values

Optional:
- none

Rationale:
Choosing a dig card is a direct comparison among drawn cards: keep value,
return cost, and future deck impact.

Validation:
- Kept card is one of the drawn cards.
- Returned-card opportunity cost is considered.
- Candidate values rank all plausible keep choices.

## Are You the Traitor?

### target_selection

Required:
- role_context_from_observation
- players_available_to_question_or_accuse
- information_gain_by_target
- team_objective_alignment
- risk_of_revealing_private_role
- candidate_target_values

Optional:
- none

Rationale:
Target choice must account for private role, legal targets, expected
information gain, team objective, and leakage risk.

Validation:
- Target id is legal.
- Role/team objective is not inverted.
- Selection trades off information gain and private-role leakage.

### question_generation

Required:
- role_context_from_observation
- current_conversation_history
- diagnostic_question_candidates
- information_to_elicit_or_hide
- question_leakage_risk
- candidate_question_values

Optional:
- none

Rationale:
Questions must be diagnostic while protecting private role and team objective.

Validation:
- Question is relevant to unresolved role beliefs.
- It does not reveal private information unnecessarily.
- Candidate values explain why this question is better than silence/generic talk.

### answer_generation

Required:
- role_context_from_observation
- current_conversation_history
- question_asked
- safe_answer_consistent_with_role
- deception_or_revelation_risk
- candidate_answer_values

Optional:
- none

Rationale:
Answers must respond to the actual question while staying consistent with the
role and managing deception/revelation risk.

Validation:
- Answer addresses the question.
- It does not contradict private role/team objective.
- Risk of revealing or deceptive inconsistency is explicit.

### stop_or_continue_accusation

Required:
- role_context_from_observation
- current_conversation_history
- accusation_confidence
- wrong_accusation_penalty
- continue_conversation_value
- stop_now_expected_value
- candidate_stop_or_pass_values

Optional:
- none

Rationale:
Stopping requires enough accusation confidence to justify the wrong-accusation
penalty relative to gathering more information.

Validation:
- STOP/pass action is legal.
- Confidence and penalty are explicitly compared.
- Continue value is not ignored.

### accused_selection

Required:
- role_context_from_observation
- players_available_to_question_or_accuse
- traitor_or_target_suspicion_by_player
- team_objective_alignment
- accusation_confidence
- wrong_accusation_risk
- candidate_accusation_values

Optional:
- none

Rationale:
Accused selection must rank legal players by suspicion and objective alignment,
with explicit wrong-accusation risk.

Validation:
- Accused id is legal.
- Suspicion is grounded in conversation/private info.
- Wrong-accusation risk is considered.

## Codenames

### submit_clue

Required:
- own_team_unrevealed_words_with_private_types
- opponent_neutral_and_assassin_words_to_avoid
- safe_target_cluster_for_this_clue
- expected_operative_interpretation_for_each_clue
- clue_ambiguity_or_forbidden_word_risk
- clue_number_risk_budget_by_candidate

Optional:
- candidate_one_word_clues
- openended_format_word_comma_number

Rationale:
Spymaster clue generation must identify safe team targets, avoid forbidden
cards, predict teammate interpretation, and set a conservative clue number.

Validation:
- Clue does not strongly attract assassin, opponent, or neutral words.
- Count matches high-confidence intended targets only.
- Field values do not endorse one clue while action outputs another.

### guess_or_end_turn

Required:
- current_clue_and_guess_limit
- unrevealed_candidate_words
- semantic_match_to_current_clue
- public_history_from_last_hint_and_guesses
- unknown_assassin_risk
- unknown_opponent_or_neutral_risk
- guess_vs_end_turn_value
- candidate_guess_or_end_turn_values

Optional:
- none

Rationale:
Operatives must rank clue matches, account for public history, consider hidden
assassin/opponent/neutral risk, and compare guessing against ending the turn.

Validation:
- Candidate values include end_turn when risk is high or clue budget is spent.
- Guess count does not exceed clue risk budget.
- Semantic fit is not treated as certainty.

## Hive

### piece_type_selection

Required:
- list_place_or_list_move_actions
- queen_placement_deadline
- piece_type_attack_defense_role
- followup_move_count_after_listing
- queen_timing_or_exposure_risk
- candidate_piece_action_values

Optional:
- none

Rationale:
Listing a piece action determines follow-up options and must respect queen
timing, attack/defense role, and exposure risk.

Validation:
- Selected list action is legal.
- Queen-placement deadline is not violated.
- Candidate values compare attack, defense, and mobility.

### placement_hex_choice

Required:
- legal_hexes_for_active_piece
- adjacency_to_own_and_opponent_pieces
- queen_pressure_created
- future_mobility_preserved
- queen_exposure_or_mobility_risk
- candidate_placement_hex_values

Optional:
- none

Rationale:
Placement choice must compare legal hexes by adjacency, pressure, future
mobility, and queen exposure.

Validation:
- Hex is legal for the active piece.
- One-hive/placement constraints are respected by available actions.
- Candidate values rank plausible hexes.

### movement_hex_choice

Required:
- active_piece_current_hex
- legal_destination_hexes
- one_hive_and_slide_legality
- queen_surround_progress
- own_queen_escape_squares
- own_queen_trap_risk
- candidate_movement_hex_values

Optional:
- none

Rationale:
Movement must preserve Hive legality while balancing opponent queen pressure and
own queen safety.

Validation:
- Destination is in legal actions.
- Move does not ignore one-hive/slide constraints.
- Own queen trap risk is explicitly evaluated.

## Pit

### offer_trade

Required:
- own_surplus_commodities
- target_corner_commodity
- bull_or_bear_exposure
- quantity_to_offer_without_harming_target
- signal_leakage_from_offer
- offer_signal_or_target_set_risk
- candidate_offer_values

Optional:
- none

Rationale:
Offers should trade surplus while preserving target corner progress and
minimizing signal leakage or Bull/Bear risk.

Validation:
- Offered commodity and quantity are legal.
- Offer does not give away target-critical cards.
- Signal/risk tradeoff is explicit.

### accept_trade

Required:
- pending_trade_offered_commodity_and_quantity
- requested_response_commodity_cost
- target_corner_progress_before_after_trade
- bull_or_bear_risk_change
- accept_vs_make_new_offer_value
- candidate_accept_or_offer_values

Optional:
- none

Rationale:
Accepting a trade requires comparing immediate target progress, commodity cost,
and Bull/Bear risk against making a new offer.

Validation:
- Accept action matches the pending trade.
- Requested card cost is available and worthwhile.
- Reject/new-offer is considered when trade worsens target progress.

## Santorini

### placement_phase

Required:
- own_unplaced_pawn
- empty_board_squares
- centrality_and_future_mobility_value
- pair_spacing_between_own_pawns
- opponent_placement_pressure
- placement_safety_or_containment_risk
- candidate_placement_values

Optional:
- none

Rationale:
Initial placement should optimize centrality, spacing, mobility, and resistance
to early containment.

Validation:
- Placement square is empty/legal.
- Both own-pawn spacing and opponent pressure are considered.
- Candidate values compare at least the strongest legal squares.

### move_build_phase

Required:
- legal_move_squares
- legal_build_squares_after_move
- immediate_win_moves
- opponent_immediate_win_threats
- mobility_after_action
- height_access_to_level_three
- candidate_move_build_values

Optional:
- none

Rationale:
Move-build decisions must check immediate wins, opponent threats, legal
move/build pairs, future mobility, and level-three access.

Validation:
- Selected move/build pair is legal.
- Immediate win or block is prioritized when present.
- Candidate values compare move and build together, not independently.

## Sea Battle

### simultaneous_move_and_shoot

Required:
- candidate_first_movement_claims
- candidate_second_movement_claims_after_turn
- rock_collision_risk
- ship_collision_risk_with_teammates_and_opponents
- post_move_left_and_right_shot_lanes
- expected_damage_dealt_minus_taken
- own_damage_survival_margin
- nearest_teammate_spacing
- nearest_opponent_bearing
- focus_fire_or_evasion_value

Optional:
- none

Rationale:
The simultaneous move must evaluate both movement phases, collision risk, shot
lanes, damage tradeoff, survival, ally spacing, and focus/evasion value.

Validation:
- Movement claims are legal and formatted correctly.
- Collision risks are considered before shot value.
- Candidate values include both movement and shooting consequences.

## Two Rooms and a Boom

### target_selection

Required:
- own_team_and_special_role
- roommates_available_to_question
- claims_heard_so_far
- diagnostic_question_targets
- safe_claim_or_answer_policy
- information_leakage_risk
- candidate_target_values

Optional:
- none

Rationale:
Target selection must use private role/team objective, current claims, and
information-leakage risk.

Validation:
- Target is a legal roommate/player id.
- Target value is grounded in claims and team goal.
- Private role leakage is considered.

### question_generation

Required:
- own_team_and_special_role
- claims_heard_so_far
- diagnostic_question_targets
- safe_claim_or_answer_policy
- information_leakage_risk
- candidate_question_values

Optional:
- none

Rationale:
Generated questions should be diagnostic while following a safe claim policy.

Validation:
- Question targets unresolved team/role information.
- It does not unnecessarily reveal own sensitive role.
- Candidate values justify the wording.

### answer_generation

Required:
- own_team_and_special_role
- question_asked
- safe_claim_or_answer_policy
- information_leakage_risk
- candidate_answer_values

Optional:
- none

Rationale:
Answers must respond to the question while preserving team objective and safe
claim policy.

Validation:
- Answer addresses the asked question.
- It does not leak sensitive role/team information without value.
- Candidate values justify truth, refusal, or ambiguity.

### leader_hostage_trade

Required:
- eligible_hostages_to_trade
- posterior_president_location
- posterior_bomber_location
- team_goal_same_or_separate
- trade_effect_on_final_co_location
- trade_information_leakage_risk
- candidate_trade_values

Optional:
- none

Rationale:
Leader trades must reason about eligible hostages, President/Bomber posteriors,
team goal, co-location effect, and leakage.

Validation:
- Selected hostage is eligible.
- Trade value matches own team objective.
- Candidate values compare President/Bomber location consequences.

## Tic-Tac-Toe

### mark_empty_square

Required:
- board_state
- legal_empty_squares
- own_immediate_wins
- opponent_immediate_wins
- fork_threats
- candidate_action_values

Optional:
- none

Rationale:
Tic-Tac-Toe decisions require board state, legal moves, immediate wins, blocks,
forks, and candidate action ranking.

Validation:
- Selected square is empty/legal.
- Immediate win or block is prioritized.
- Fork creation/prevention is considered when no immediate win/block exists.
