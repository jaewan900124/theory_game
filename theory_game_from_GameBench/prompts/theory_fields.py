from prompts.game_profiles import canonical_game_id


GENERIC_THEORY_MAPPING = {
    "display_name": "GameBench game",
    "game_type": "game with legal actions, payoff-relevant state, and strategic opponents",
    "solution_concept": "best response under the current information set, with equilibrium or coordination logic when applicable",
    "reference_basis": [
        "GameBench paper Appendix G: rules shown to language-model agents",
        "GameBench implementation: current game class rules, observations, and available actions",
        "ref/game_theory_mapping.md: strategic, Bayesian, extensive-form, and best-response mappings",
        "Osborne and Rubinstein: strategic games, Bayesian games, extensive games, and equilibrium concepts",
    ],
    "osborne_rubinstein_mapping": (
        "Model the current prompt as a game: identify players, actions, preferences over outcomes, "
        "information available to each player, chance or simultaneous moves, and the legal action set. "
        "Use the rules as authoritative and use game theory only to organize decision fields."
    ),
    "required_state_fields": [
        "players_and_roles",
        "legal_action_set",
        "information_state_public_private",
        "objective_or_payoff",
        "payoff_relevant_state_variables",
        "beliefs_about_opponents_or_teammates",
        "candidate_action_values",
        "risk_or_constraint_checks",
        "legal_output_format",
    ],
    "field_computation_targets": [
        "Compute the legal action set and required output format from Available actions.",
        "Compute the public/private information state and payoff-relevant variables from the observation.",
        "Compute candidate action values and risk or constraint checks before selecting a legal response.",
    ],
    "decision_workflow": [
        "Extract the legal action set from Available actions, not from memory.",
        "Extract the current public and private information from the observation.",
        "Map each plausible action to its payoff-relevant consequences under the rules.",
        "Choose a legal best response for the stated objective and verify the output format.",
    ],
    "distill_rules": [
        "P1. Keep only legal actions from the provided action ids.",
        "P2. Compare actions by immediate objective impact, future strategic value, and rule constraints.",
        "P3. Return the legal action with the strongest best-response case.",
    ],
    "verifier_checks": [
        "selected_action is copied exactly from the available action ids",
        "openended_response is present when the selected action requires free text",
        "the decision uses the current observation and game rules",
    ],
}


GAMEBENCH_THEORY_MAPPINGS = {
    "air_land_sea": {
        "display_name": "Air, Land, and Sea",
        "game_type": "two-player sequential card battle with hidden hands, theater control, and an outside option to withdraw",
        "solution_concept": "finite-horizon best response with option-value reasoning and tactical commitment",
        "reference_basis": [
            "GameBench paper Appendix F/G: Air, Land, and Sea description and rules",
            "GameBench implementation: games/air_land_sea/game.py",
            "Air Land and Sea rulebook: games/air_land_sea/Air_Land_and_Sea_Rulebook_Revised.pdf",
            "Game theory: finite extensive game with imperfect information, best response, and outside-option evaluation",
        ],
        "osborne_rubinstein_mapping": (
            "Model each turn as an extensive-form decision. Actions allocate scarce cards to theaters, "
            "change future control probabilities, and may trigger tactical effects. Withdrawal is an outside option "
            "whose payoff depends on remaining cards."
        ),
        "required_state_fields": [
            "hand_cards_and_remaining_cards",
            "theater_control_state",
            "commander_tie_rule",
            "withdrawal_value_now",
            "card_deploy_or_improvise_value",
            "tactical_ability_effects",
            "future_turn_option_value",
            "candidate_action_values",
            "legal_output_format",
        ],
        "role_or_phase_fields": {
            "main_turn_deploy_improvise_withdraw": [
                "playable_faceup_cards_by_matching_theater",
                "playable_facedown_cards_by_theater",
                "withdrawal_points_given_remaining_hand",
                "current_theater_majority_status",
                "card_conservation_value",
                "faceup_deploy_control_swing",
                "facedown_improvise_information_value",
                "action_risk_by_commitment_and_information",
                "candidate_card_or_withdraw_values",
            ],
            "tactical_followup_effect_resolution": [
                "triggering_tactical_card",
                "legal_followup_targets_or_extra_play_options",
                "own_vs_opponent_card_ownership",
                "control_swing_after_effect",
                "risk_of_revealing_or_covering_key_card",
                "do_nothing_or_skip_value_if_available",
                "candidate_effect_target_values",
            ],
        },
        "role_or_phase_selection_rule": (
            "If the action list contains normal Play/Withdraw actions, use main_turn_deploy_improvise_withdraw. "
            "If the action list asks to Flip, Move, Return, choose an adjacent theater, play a drawn card, do nothing, or otherwise resolve a tactical ability, use tactical_followup_effect_resolution."
        ),
        "decision_workflow": [
            "Identify theaters currently won, lost, and contested.",
            "Compare deploying face up, improvising face down, and withdrawing if available.",
            "Value high-impact tactical cards by how they change theater control, not only printed strength.",
            "Choose the action that maximizes expected battle or match value under the legal action list.",
        ],
        "distill_rules": [
            "P1. If withdrawal value exceeds likely continuation value, withdraw.",
            "P2. Otherwise prefer a legal card action that flips theater control or preserves decisive future options.",
            "P3. Break ties by conserving high-value flexible cards and improving the weakest contested theater.",
        ],
        "verifier_checks": [
            "the chosen action is one of the listed action ids",
            "the action respects theater and face-up or face-down restrictions",
            "withdrawal is chosen only when its payoff beats continuation value",
        ],
    },
    "arctic_scavengers": {
        "display_name": "Arctic Scavengers",
        "game_type": "two-player deck-building game with resource allocation, delayed payoffs, and skirmish contests",
        "solution_concept": "dynamic programming heuristic over deck growth, food economy, and skirmish strength",
        "reference_basis": [
            "GameBench paper Appendix F/G: Arctic Scavengers description and rules",
            "GameBench implementation: games/arctic_scavengers/arctic_scavengers.py",
            "Game theory: finite-horizon dynamic choice, resource allocation, and best response under hidden future draws",
        ],
        "osborne_rubinstein_mapping": (
            "Model each action as allocating current hand resources between immediate contested-resource strength "
            "and long-run deck improvement. The state includes hidden future draws, current hand, food, piles, and used actions."
        ),
        "required_state_fields": [
            "current_hand_actions",
            "food_available",
            "actions_already_used_this_round",
            "junkyard_and_mercenary_options",
            "current_skirmish_strength",
            "deck_improvement_value",
            "opponent_interruption_risk",
            "candidate_action_values",
            "openended_command_format",
        ],
        "role_or_phase_fields": {
            "resource_gathering_action": [
                "available_standard_and_modifier_cards",
                "unused_once_per_round_actions",
                "dig_draw_hunt_hire_trash_feasibility",
                "food_and_medicine_budget",
                "deck_improvement_vs_skirmish_cost",
                "openended_list_command",
            ],
            "interrupt_response": [
                "opponent_announced_action",
                "available_sniper_or_saboteur_cards",
                "valid_interrupt_targets",
                "value_of_canceling_opponent_action",
                "discard_cost_of_interrupt",
                "interrupt_target_or_discard_risk",
                "candidate_interrupt_values",
            ],
            "skirmish_action": [
                "own_visible_fight_and_people_score",
                "opponent_visible_fight_and_people_score",
                "sniper_or_saboteur_targets",
                "contested_resource_value",
                "skirmish_action_risk",
                "candidate_skirmish_action_values",
            ],
            "dig_card_selection": [
                "drawn_junkyard_cards",
                "card_added_to_reserve_value",
                "cards_returned_to_junkyard_cost",
                "card_keep_risk_or_opportunity_cost",
                "candidate_dig_keep_values",
            ],
        },
        "role_or_phase_selection_rule": (
            "Use resource_gathering_action for DIG/DRAW/HUNT/HIRE/TRASH/STOP command prompts, interrupt_response when responding to an opponent action, "
            "skirmish_action for SNIPE/SABOTEUR/STOP skirmish prompts, and dig_card_selection when choosing one drawn junkyard card."
        ),
        "decision_workflow": [
            "List usable cards and which once-per-round actions remain.",
            "Compare DIG, DRAW, HUNT, HIRE, TRASH, and STOP by deck value and skirmish value.",
            "Spend food only when the hired card improves future turns enough to justify the cost.",
            "For openended commands, output the exact structured command required by the action description.",
        ],
        "distill_rules": [
            "P1. Do not reuse an action already performed this round.",
            "P2. Prefer actions that either improve the deck materially or win the next contested resource.",
            "P3. Stop when further actions would consume useful skirmish cards without sufficient deck value.",
        ],
        "verifier_checks": [
            "selected_action is legal and unused when the rule says once per round",
            "openended_response names cards that appear usable from the observation",
            "food spending is feasible",
        ],
    },
    "are_you_the_traitor": {
        "display_name": "Are You the Traitor?",
        "game_type": "team social-deduction game with asymmetric private roles and strategic communication",
        "solution_concept": "Bayesian belief updating, signaling, cheap talk, and team-objective best response",
        "reference_basis": [
            "GameBench paper Appendix F/G: Are You the Traitor description and rules",
            "GameBench implementation: games/are_you_the_traitor/aytt.py",
            "Game theory: Bayesian game with private types, imperfect-information extensive game, belief updating, and signaling/cheap-talk reasoning",
        ],
        "osborne_rubinstein_mapping": (
            "Model each player as having private type information. Speech actions are signals that may reveal, conceal, "
            "or elicit information. The best response depends on team objective, role, target, and posterior beliefs."
        ),
        "required_state_fields": [
            "own_team_role_and_target",
            "known_private_information",
            "public_claims_and_conversation",
            "posterior_beliefs_about_roles",
            "team_objective",
            "information_to_elicit_or_hide",
            "candidate_speech_or_action_values",
            "deception_or_revelation_risk",
        ],
        "role_or_phase_fields": {
            "traitor_undercover": [
                "known_keyholder_identity",
                "belief_about_evil_wizard_identity",
                "safe_signal_to_evil_wizard",
                "risk_of_good_wizard_detection",
                "misdirection_or_silence_value",
            ],
            "evil_wizard_deception": [
                "candidate_keyholder_beliefs",
                "candidate_traitor_beliefs",
                "claim_to_induce_key_transfer",
                "risk_of_good_team_accusation",
                "target_to_question_or_accuse",
            ],
            "good_wizard_trust_building": [
                "candidate_keyholder_beliefs",
                "candidate_traitor_beliefs",
                "trustworthy_signal_to_keyholder",
                "evil_wizard_distinguishing_question",
                "accusation_confidence",
            ],
            "key_holder_screening": [
                "wizard_identity_beliefs",
                "key_secrecy_risk",
                "question_to_identify_good_wizard",
                "false_claim_or_nonanswer_value",
                "handoff_or_accusation_threshold",
            ],
            "guard_traitor_hunt": [
                "traitor_suspicion_by_player",
                "keyholder_protection_policy",
                "wizard_identity_beliefs",
                "decoy_claim_value",
                "accusation_confidence",
            ],
            "target_selection": [
                "players_available_to_question_or_accuse",
                "information_gain_by_target",
                "team_objective_alignment",
                "risk_of_revealing_private_role",
            ],
            "question_answer_or_stop": [
                "current_conversation_history",
                "most_diagnostic_question",
                "safe_answer_consistent_with_role",
                "stop_now_expected_value",
            ],
        },
        "role_or_phase_selection_rule": (
            "Choose the role field matching the private context: traitor, evil_wizard, good_wizard, key_holder, or guard. "
            "Combine it with target_selection for numeric player-choice actions and with question_answer_or_stop for openended speech or STOP/Pass decisions."
        ),
        "decision_workflow": [
            "Condition on your private role and team objective.",
            "Separate truthful information, strategic ambiguity, and probing questions.",
            "Choose communication that improves your team's ability to identify the right target or mislead the other team.",
            "Avoid revealing private information that directly helps the opposing team unless it is strategically necessary.",
        ],
        "distill_rules": [
            "P1. If uncertain, ask the question that most separates possible hidden roles.",
            "P2. If your private role is valuable to conceal, use a claim that protects it while advancing team objective.",
            "P3. Prefer speech that creates actionable role beliefs rather than generic chatter.",
        ],
        "verifier_checks": [
            "openended_response is a concrete utterance",
            "the utterance is consistent with own team objective",
            "private information is not leaked without strategic reason",
        ],
    },
    "codenames": {
        "display_name": "Codenames",
        "game_type": "team word-association game with asymmetric information and risk of terminal negative outcomes",
        "solution_concept": "cooperative signaling under asymmetric information and risk-dominant clue selection",
        "reference_basis": [
            "GameBench paper Appendix F/G: Codenames description and rules",
            "GameBench implementation: games/codenames/game.py",
            "Game theory: asymmetric-information team game, signaling from spymaster to operative, belief-based interpretation, and terminal-risk avoidance",
        ],
        "osborne_rubinstein_mapping": (
            "Spymasters choose signals that induce teammates to select target words while avoiding opponent, neutral, "
            "and assassin cards. Operatives choose guesses by Bayesian interpretation of the clue and public board."
        ),
        "required_state_fields": [
            "agent_role_spymaster_or_operative",
            "team_color",
            "visible_word_grid",
            "revealed_words_and_last_turn_history",
            "current_team_turn",
            "active_role_specific_field_set",
        ],
        "role_or_phase_fields": {
            "spymaster_signal_design": [
                "own_team_unrevealed_words_with_private_types",
                "opponent_neutral_and_assassin_words_to_avoid",
                "safe_target_cluster_for_this_clue",
                "candidate_one_word_clues",
                "expected_operative_interpretation_for_each_clue",
                "clue_ambiguity_or_forbidden_word_risk",
                "clue_number_risk_budget_by_candidate",
                "openended_format_word_comma_number",
            ],
            "operative_signal_interpretation": [
                "current_clue_and_guess_limit",
                "unrevealed_candidate_words",
                "semantic_match_to_current_clue",
                "public_history_from_last_hint_and_guesses",
                "unknown_assassin_risk",
                "unknown_opponent_or_neutral_risk",
                "guess_vs_end_turn_value",
                "candidate_guess_or_end_turn_values",
            ],
        },
        "role_or_phase_selection_rule": (
            "If the observation says Spymaster or the only legal action is submit_clue, use spymaster_signal_design. "
            "If the observation says Operative or legal actions are guess_* / end_turn, use operative_signal_interpretation."
        ),
        "decision_workflow": [
            "If spymaster, find a clue that links team words and avoids opponent, neutral, and assassin words.",
            "If operative, infer the intended team words from the current clue and visible board.",
            "Use the number in the clue as a constraint on risk taking.",
            "For clue submission, return one word and a number in the required format.",
        ],
        "distill_rules": [
            "P1. Never clue or guess the assassin if avoidable.",
            "P2. Prefer one safe target over multiple targets with high forbidden-word ambiguity.",
            "P3. For openended clue, output exactly 'word,number'.",
        ],
        "verifier_checks": [
            "clue is one word plus a number when submit_clue is chosen",
            "guess or clue is grounded in visible board words",
            "assassin and opponent-card risk are considered",
        ],
    },
    "hive": {
        "display_name": "Hive",
        "game_type": "two-player deterministic abstract strategy game with placement and movement constraints",
        "solution_concept": "minimax-style best response with mobility, queen safety, and constraint satisfaction",
        "reference_basis": [
            "GameBench paper Appendix F/G: Hive description and rules",
            "GameBench implementation: games/hive/game.py",
            "Game theory: finite extensive game with perfect information, maxmin/minimax-style best response, and constraint satisfaction",
        ],
        "osborne_rubinstein_mapping": (
            "Model the board as a deterministic perfect-information game. Legal moves are constrained by one-hive, freedom-to-move, "
            "piece movement, and queen-placement rules. Payoff is capture of the opposing queen while avoiding own queen capture."
        ),
        "required_state_fields": [
            "own_queen_status",
            "opponent_queen_status",
            "legal_placement_or_movement_options",
            "one_hive_and_slide_constraints",
            "threats_to_own_queen",
            "threats_to_opponent_queen",
            "mobility_and_blocking_value",
            "candidate_action_values",
        ],
        "role_or_phase_fields": {
            "piece_type_selection": [
                "list_place_or_list_move_actions",
                "queen_placement_deadline",
                "piece_type_attack_defense_role",
                "followup_move_count_after_listing",
                "queen_timing_or_exposure_risk",
                "candidate_piece_action_values",
            ],
            "placement_hex_choice": [
                "legal_hexes_for_active_piece",
                "adjacency_to_own_and_opponent_pieces",
                "queen_pressure_created",
                "future_mobility_preserved",
                "queen_exposure_or_mobility_risk",
                "candidate_placement_hex_values",
            ],
            "movement_hex_choice": [
                "active_piece_current_hex",
                "legal_destination_hexes",
                "one_hive_and_slide_legality",
                "queen_surround_progress",
                "own_queen_escape_squares",
                "own_queen_trap_risk",
                "candidate_movement_hex_values",
            ],
        },
        "role_or_phase_selection_rule": (
            "If actions start with list_place/list_move, use piece_type_selection. "
            "If actions start with place_, use placement_hex_choice. If actions start with move_, use movement_hex_choice."
        ),
        "decision_workflow": [
            "Verify queen placement timing and movement legality.",
            "Prioritize immediate wins, then blocking immediate losses.",
            "Evaluate moves by whether they surround the opponent queen or improve mobility around key pieces.",
            "Avoid moves that break the hive or trap own queen unless they force a win.",
        ],
        "distill_rules": [
            "P1. If a legal action wins immediately, choose it.",
            "P2. Else block any opponent immediate win.",
            "P3. Else improve queen pressure while preserving own queen mobility and all movement constraints.",
        ],
        "verifier_checks": [
            "selected_action is listed as legal",
            "queen placement and one-hive constraints are respected",
            "candidate comparison includes attack and defense",
        ],
    },
    "pit": {
        "display_name": "Pit",
        "game_type": "commodity trading game with private hands, bargaining, and set-collection payoffs",
        "solution_concept": "Bayesian bargaining and expected-value trade selection under private information",
        "reference_basis": [
            "GameBench paper Appendix F/G: Pit description and rules",
            "GameBench implementation: games/pit/pit.py",
            "Game theory: bargaining with private hands, Bayesian belief over counterpart holdings, and expected set-completion value",
        ],
        "osborne_rubinstein_mapping": (
            "Model each trade as exchanging private hand composition for a more valuable set. Offers and acceptances reveal signals "
            "about opponents' holdings. Best response maximizes expected set-completion value net of opportunity cost."
        ),
        "required_state_fields": [
            "own_hand_counts",
            "commodity_values",
            "current_pending_trades",
            "target_set_or_high_value_commodity",
            "cards_to_offer",
            "cards_to_seek_or_trade_acceptance_value",
            "beliefs_from_trade_signals",
            "candidate_trade_values",
        ],
        "role_or_phase_fields": {
            "offer_trade": [
                "own_surplus_commodities",
                "target_corner_commodity",
                "bull_or_bear_exposure",
                "quantity_to_offer_without_harming_target",
                "signal_leakage_from_offer",
                "offer_signal_or_target_set_risk",
                "candidate_offer_values",
            ],
            "accept_trade": [
                "pending_trade_offered_commodity_and_quantity",
                "requested_response_commodity_cost",
                "target_corner_progress_before_after_trade",
                "bull_or_bear_risk_change",
                "accept_vs_make_new_offer_value",
                "candidate_accept_or_offer_values",
            ],
        },
        "role_or_phase_selection_rule": (
            "If pending trades appear and Accept_* actions are legal, use accept_trade. Otherwise use offer_trade."
        ),
        "decision_workflow": [
            "Identify the commodity set closest to completion and its point value.",
            "Offer surplus or low-fit cards while protecting cards needed for the target set.",
            "Accept trades that increase expected set-completion value.",
            "Account for Bull and Bear effects when they appear in the observation.",
        ],
        "distill_rules": [
            "P1. Keep cards in the best target commodity unless the trade gives a higher-value target.",
            "P2. Offer duplicates or off-target commodities first.",
            "P3. Accept only trades that improve expected set value or reduce Bear risk.",
        ],
        "verifier_checks": [
            "trade proposal uses cards available in own hand",
            "openended_response follows the action description",
            "accepted trade improves expected commodity value",
        ],
    },
    "santorini": {
        "display_name": "Santorini",
        "game_type": "two-player deterministic spatial game with move-build turns and immediate win conditions",
        "solution_concept": "minimax-style best response with tactical win, block, and mobility evaluation",
        "reference_basis": [
            "GameBench paper Appendix F/G: Santorini description and rules",
            "GameBench implementation: games/santorini/santorini.py",
            "Santorini rulebook: games/santorini/rulebook.pdf",
            "Game theory: finite extensive game with perfect information, backward-induction-style tactical search, and maxmin defense",
        ],
        "osborne_rubinstein_mapping": (
            "Model each turn as a move followed by a build. Legal actions are constrained by adjacency, height difference, occupancy, "
            "and domes. Payoff is immediate win by moving to level 3 or forcing opponent immobility."
        ),
        "required_state_fields": [
            "current_phase_placement_or_move_build",
            "active_pawn",
            "board_heights_and_occupancy",
            "legal_action_set",
            "active_phase_specific_field_set",
        ],
        "role_or_phase_fields": {
            "placement_phase": [
                "own_unplaced_pawn",
                "empty_board_squares",
                "centrality_and_future_mobility_value",
                "pair_spacing_between_own_pawns",
                "opponent_placement_pressure",
                "candidate_placement_values",
            ],
            "move_build_phase": [
                "legal_move_squares",
                "legal_build_squares_after_move",
                "immediate_win_moves",
                "opponent_immediate_win_threats",
                "mobility_after_action",
                "height_access_to_level_three",
                "candidate_move_build_values",
            ],
        },
        "role_or_phase_selection_rule": (
            "If the observation is placing pawns or legal actions are board coordinates before movement, use placement_phase. "
            "If the action ids encode move/build pairs or the observation describes a current pawn turn, use move_build_phase."
        ),
        "required_state_fields_legacy": [
            "immediate_win_moves",
            "opponent_immediate_win_threats",
            "mobility_after_action",
            "candidate_move_build_values",
        ],
        "decision_workflow": [
            "Check for a legal immediate win by moving to level 3.",
            "If no immediate win, block the opponent's immediate level-3 threats.",
            "Choose move-build pairs that improve own height access and reduce opponent mobility.",
            "Verify the move and build are both legal in the listed action id.",
        ],
        "distill_rules": [
            "P1. Take an immediate winning move if listed.",
            "P2. Else build to block opponent immediate wins.",
            "P3. Else maximize own future access to level 3 while preserving mobility.",
        ],
        "verifier_checks": [
            "move is adjacent and does not climb more than one level",
            "build is adjacent to the moved pawn and on an unoccupied non-dome square",
            "selected_action is exactly listed",
        ],
    },
    "sea_battle": {
        "display_name": "Sea Battle",
        "game_type": "multi-agent team simultaneous-move tactical game with spatial collision and shooting risk",
        "solution_concept": "Markov best response with team coordination, collision avoidance, and expected damage",
        "reference_basis": [
            "GameBench paper Appendix F/G: Sea Battle description and rules",
            "GameBench implementation: games/sea_battle.py",
            "Game theory: simultaneous-move team game, Markov state evaluation, collision-risk management, and best response to uncertain joint actions",
        ],
        "osborne_rubinstein_mapping": (
            "Model the turn as simultaneous actions by all ships. Each action changes position, heading, collision risk, line-of-fire, "
            "and expected damage. Payoff is team survival and sinking all opposing ships."
        ),
        "required_state_fields": [
            "own_position_heading_damage",
            "teammate_positions",
            "opponent_positions",
            "rocks_and_collision_hazards",
            "candidate_movement_paths",
            "candidate_shot_lanes",
            "expected_damage_given_and_received",
            "team_coordination_value",
            "candidate_action_values",
        ],
        "role_or_phase_fields": {
            "simultaneous_move_and_shoot_plan": [
                "candidate_first_movement_claims",
                "candidate_second_movement_claims_after_turn",
                "rock_collision_risk",
                "ship_collision_risk_with_teammates_and_opponents",
                "post_move_left_and_right_shot_lanes",
                "expected_damage_dealt_minus_taken",
            ],
            "team_ship_role": [
                "own_damage_survival_margin",
                "nearest_teammate_spacing",
                "nearest_opponent_bearing",
                "focus_fire_or_evasion_value",
            ],
        },
        "role_or_phase_selection_rule": (
            "Sea Battle has symmetric ship roles but simultaneous movement and shooting. Always use simultaneous_move_and_shoot_plan; add team_ship_role for team spacing and survival."
        ),
        "decision_workflow": [
            "Reject actions likely to collide with rocks, teammates, or opponents unless they create a decisive advantage.",
            "Prefer actions that create a firing lane on opponents while reducing exposure.",
            "Coordinate implicitly by preserving spacing with teammates.",
            "Choose the legal action with the best team survival and damage tradeoff.",
        ],
        "distill_rules": [
            "P1. Avoid self-damaging movement into rocks or collisions.",
            "P2. Among safe actions, prefer those with a likely shot on an opponent.",
            "P3. Break ties by preserving distance from high-threat opponents and teammates.",
        ],
        "verifier_checks": [
            "selected_action is exactly listed",
            "collision and rock risks are checked",
            "shooting direction is evaluated from the post-move heading",
        ],
    },
    "two_rooms_and_a_boom": {
        "display_name": "Two Rooms and a Boom",
        "game_type": "team social-deduction game with hidden roles, rooms, leaders, and hostage trades",
        "solution_concept": "Bayesian belief updating, signaling, and team-objective coordination under limited communication",
        "reference_basis": [
            "GameBench paper Appendix F/G: Two Rooms and a Boom description and rules",
            "GameBench implementation: games/two_rooms_and_a_boom/two_rooms.py",
            "Game theory: Bayesian hidden-role game, imperfect-information extensive game, signaling, and team-objective coordination",
        ],
        "osborne_rubinstein_mapping": (
            "Model private cards as types and room conversations or trades as signals. Leaders choose trades to control the final "
            "President-Bomber co-location event. Non-leaders communicate to update team beliefs."
        ),
        "required_state_fields": [
            "own_team_and_special_role",
            "room_members_and_known_claims",
            "leader_status",
            "round_number_or_remaining_trades",
            "beliefs_about_president_and_bomber_locations",
            "team_objective_same_or_separate_rooms",
            "information_leakage_risk",
            "active_role_specific_field_set",
        ],
        "role_or_phase_fields": {
            "leader_hostage_trade": [
                "eligible_hostages_to_trade",
                "posterior_president_location",
                "posterior_bomber_location",
                "team_goal_same_or_separate",
                "trade_effect_on_final_co_location",
                "trade_information_leakage_risk",
                "candidate_trade_values",
            ],
            "nonleader_information_gathering": [
                "own_team_and_special_role",
                "roommates_available_to_question",
                "claims_heard_so_far",
                "diagnostic_question_targets",
                "safe_claim_or_answer_policy",
                "candidate_question_or_answer_values",
            ],
            "special_role_policy": [
                "special_role_private_status",
                "team_objective_from_private_role",
                "safe_signal_value_to_team",
                "misdirection_or_silence_value",
                "special_role_revelation_risk",
            ],
        },
        "role_or_phase_selection_rule": (
            "If the observation says I am the Leader or legal actions choose a hostage after discussion, use leader_hostage_trade. "
            "For ordinary question/answer turns, use nonleader_information_gathering plus special_role_policy if the observation reveals President or Bomber."
        ),
        "decision_workflow": [
            "Condition on whether your team wants President and Bomber together or apart.",
            "Use conversation to locate special roles while limiting information leakage to the other team.",
            "If leader, prefer trades that move the posterior room configuration toward your team objective.",
            "If speaking, ask or claim information that improves role-location beliefs.",
        ],
        "distill_rules": [
            "P1. If lacking role-location information, ask the most diagnostic safe question.",
            "P2. If leader and a trade is available, trade to move President and Bomber toward your team objective.",
            "P3. Avoid revealing special-role information to likely opponents unless it induces a favorable trade.",
        ],
        "verifier_checks": [
            "openended_response is a concrete question, claim, or trade instruction",
            "the action supports the team's same-room or separate-room objective",
            "private role information is protected unless strategically justified",
        ],
    },
    "tic_tac_toe": {
        "display_name": "Tic-Tac-Toe",
        "game_type": "two-player deterministic zero-sum perfect-information game",
        "solution_concept": "minimax best response",
        "reference_basis": [
            "GameBench implementation: games/tic_tac_toe.py",
            "ref/game_theory_mapping.md: Tic-Tac-Toe mapping to finite extensive perfect-information game",
            "Game theory: backward induction, minimax/maxmin reasoning, and immediate win/block checks",
        ],
        "osborne_rubinstein_mapping": (
            "Model the board as a finite zero-sum game. Legal actions are empty squares. "
            "Best response checks immediate win, immediate block, fork creation or prevention, center, corners, then edges."
        ),
        "required_state_fields": [
            "board_state",
            "legal_empty_squares",
            "own_immediate_wins",
            "opponent_immediate_wins",
            "fork_threats",
            "candidate_action_values",
        ],
        "decision_workflow": [
            "Take an immediate win.",
            "Block an opponent immediate win.",
            "Create or block forks, then prefer center, corners, and edges.",
        ],
        "distill_rules": [
            "P1. Win if possible.",
            "P2. Else block a loss.",
            "P3. Else choose the strongest minimax square.",
        ],
        "verifier_checks": [
            "selected square is empty and listed",
            "immediate win and block were checked",
        ],
    },
}


GAMEBENCH_ACTIVE_CONTEXTS = {
    "air_land_sea": {
        "default": "normal_deploy_improvise_withdraw",
        "contexts": {
            "normal_deploy_improvise_withdraw": {
                "role_specs": ["main_turn_deploy_improvise_withdraw"],
                "fields": [
                    "playable_faceup_cards_by_matching_theater",
                    "playable_facedown_cards_by_theater",
                    "withdrawal_points_given_remaining_hand",
                    "current_theater_majority_status",
                    "card_conservation_value",
                    "faceup_deploy_control_swing",
                    "facedown_improvise_information_value",
                    "action_risk_by_commitment_and_information",
                    "candidate_card_or_withdraw_values",
                ],
                "reasoning_workflow": [
                    "Identify theaters currently won, lost, and contested.",
                    "Compare face-up deploy, face-down improvise, and withdraw if available.",
                    "Value tactical text by theater-control swing and future option cost.",
                    "Choose the legal action with the best battle or match value.",
                ],
                "distill_rules": [
                    "P1. Compute withdrawal value from remaining hand and current battle outlook.",
                    "P2. Compare legal face-up deploy, face-down improvise, and withdraw actions.",
                    "P3. Prefer actions that flip or secure theater control without wasting decisive future cards.",
                    "P4. Select the best verifier-passing action.",
                ],
                "verifier_checks": [
                    "selected_action is one of the listed action ids",
                    "deploy, improvise, and withdraw constraints match the current action space",
                    "hidden or facedown cards are treated as beliefs unless revealed",
                ],
            },
            "tactical_effect_resolution": {
                "role_specs": ["tactical_followup_effect_resolution"],
                "fields": [
                    "triggering_tactical_card",
                    "legal_effect_targets_or_extra_play_options",
                    "own_vs_opponent_card_ownership",
                    "control_swing_after_effect",
                    "reveal_or_cover_information_cost",
                    "effect_target_risk_by_option",
                    "do_nothing_or_skip_value_if_available",
                    "candidate_effect_target_values",
                ],
                "reasoning_workflow": [
                    "Identify the tactical effect being resolved and the listed legal targets.",
                    "Estimate how each effect target changes theater control or future options.",
                    "Subtract reveal, cover, movement, return, or skipped-effect risk.",
                    "Choose the effect target with positive value, otherwise choose the legal do-nothing option if available.",
                ],
                "distill_rules": [
                    "P1. Identify the triggering effect and legal targets.",
                    "P2. Estimate theater-control swing for each target.",
                    "P3. Subtract reveal, cover, movement, return, or skipped-effect risk.",
                    "P4. Choose the best effect target, or do nothing when all targets are negative.",
                ],
                "verifier_checks": [
                    "selected_action is one of the listed effect-resolution action ids",
                    "the chosen target is legal for the triggering card",
                    "do nothing is used only when effect targets have no positive value",
                ],
            },
        },
    },
    "arctic_scavengers": {
        "default": "resource_gathering",
        "contexts": {
            "resource_gathering": {
                "role_specs": ["resource_gathering_action"],
                "fields": [
                    "available_standard_and_modifier_cards",
                    "unused_once_per_round_actions",
                    "dig_draw_hunt_hire_trash_feasibility",
                    "food_and_medicine_budget",
                    "deck_improvement_vs_skirmish_cost",
                    "resource_action_cost_or_risk",
                    "candidate_resource_action_values",
                    "openended_list_command",
                ],
                "reasoning_workflow": [
                    "List usable cards and once-per-round actions that remain.",
                    "Compare DIG, DRAW, HUNT, HIRE, TRASH, and STOP by deck value and skirmish cost.",
                    "Spend food or medicine only when the hire improves future rounds enough.",
                    "Return the exact structured openended command required by the action description.",
                ],
                "distill_rules": [
                    "P1. Reject actions already used this round or infeasible with the visible hand.",
                    "P2. Prefer actions that materially improve the deck or preserve skirmish strength.",
                    "P3. Stop when further actions consume useful skirmish cards without sufficient deck value.",
                ],
                "verifier_checks": [
                    "openended_response uses the required list command format",
                    "named cards appear usable from the current hand",
                    "food and medicine spending is feasible",
                ],
            },
            "interrupt_response": {
                "role_specs": ["interrupt_response"],
                "fields": [
                    "opponent_announced_action",
                    "available_sniper_or_saboteur_cards",
                    "valid_interrupt_targets",
                    "value_of_canceling_opponent_action",
                    "discard_cost_of_interrupt",
                    "interrupt_target_or_discard_risk",
                    "interrupt_feasibility_by_action",
                    "candidate_interrupt_values",
                ],
                "reasoning_workflow": [
                    "Read the opponent's announced action as the public target.",
                    "Check whether SNIPER or SABOTEUR is legal and has a valid target.",
                    "Compare canceling value against the discard cost.",
                    "Interrupt only when the expected swing exceeds the card cost; otherwise STOP.",
                ],
                "distill_rules": [
                    "P1. Keep only legal SNIPER, SABOTEUR, or STOP actions.",
                    "P2. Remove interrupts without a valid target or required card.",
                    "P3. Choose an interrupt only if canceling value exceeds discard cost; otherwise STOP.",
                ],
                "verifier_checks": [
                    "interrupt target appears in the opponent's announced or visible cards",
                    "the required interrupt card is available",
                    "STOP is selected when no valid positive-value interrupt exists",
                ],
            },
            "skirmish_action": {
                "role_specs": ["skirmish_action"],
                "fields": [
                    "own_visible_fight_and_people_score",
                    "opponent_visible_fight_and_people_score",
                    "sniper_or_saboteur_targets",
                    "contested_resource_value",
                    "skirmish_action_risk",
                    "candidate_skirmish_action_values",
                ],
                "reasoning_workflow": [
                    "Compute the current fight and people comparison.",
                    "Identify legal SNIPER or SABOTEUR targets that change the skirmish result.",
                    "Prefer attacks that win or protect the contested resource.",
                    "STOP when no legal attack improves the skirmish outcome.",
                ],
                "distill_rules": [
                    "P1. Keep legal SNIPER, SABOTEUR, and STOP actions.",
                    "P2. Remove attacks that do not change or protect the skirmish result.",
                    "P3. Select the highest swing legal attack, otherwise STOP.",
                ],
                "verifier_checks": [
                    "target card is visible and valid for SNIPER or SABOTEUR",
                    "skirmish fight and people scores are considered",
                    "selected_action is legal for the skirmish phase",
                ],
            },
            "dig_card_selection": {
                "role_specs": ["dig_card_selection"],
                "fields": [
                    "drawn_junkyard_cards",
                    "card_added_to_reserve_value",
                    "cards_returned_to_junkyard_cost",
                    "card_keep_risk_or_opportunity_cost",
                    "candidate_dig_keep_values",
                ],
                "reasoning_workflow": [
                    "List the drawn junkyard cards.",
                    "Compare each card's reserve-deck value for future actions and tribe strength.",
                    "Keep the highest future-value legal card.",
                ],
                "distill_rules": [
                    "P1. Keep only listed drawn-card action ids.",
                    "P2. Rank cards by future deck value and synergy with current needs.",
                    "P3. Select the best listed card to keep.",
                ],
                "verifier_checks": [
                    "selected_action is one of the drawn card names",
                    "the kept card value is grounded in the visible card text",
                ],
            },
        },
    },
    "are_you_the_traitor": {
        "default": "target_selection",
        "role_overlays": {
            "traitor_undercover": [
                "known_keyholder_identity",
                "belief_about_evil_wizard_identity",
                "safe_signal_to_evil_wizard",
                "risk_of_good_wizard_detection",
                "misdirection_or_silence_value",
            ],
            "evil_wizard_deception": [
                "candidate_keyholder_beliefs",
                "candidate_traitor_beliefs",
                "claim_to_induce_key_transfer",
                "risk_of_good_team_accusation",
            ],
            "good_wizard_trust_building": [
                "candidate_keyholder_beliefs",
                "candidate_traitor_beliefs",
                "trustworthy_signal_to_keyholder",
                "evil_wizard_distinguishing_question",
            ],
            "key_holder_screening": [
                "wizard_identity_beliefs",
                "key_secrecy_risk",
                "question_to_identify_good_wizard",
                "handoff_or_accusation_threshold",
            ],
            "guard_traitor_hunt": [
                "traitor_suspicion_by_player",
                "keyholder_protection_policy",
                "wizard_identity_beliefs",
                "accusation_confidence",
            ],
        },
        "contexts": {
            "target_selection": {
                "role_specs": ["target_selection"],
                "fields": [
                    "role_context_from_observation",
                    "players_available_to_question_or_accuse",
                    "information_gain_by_target",
                    "team_objective_alignment",
                    "risk_of_revealing_private_role",
                    "candidate_target_values",
                ],
                "reasoning_workflow": [
                    "Choose the player whose answer would most reduce role uncertainty.",
                    "Prefer targets relevant to the private role objective.",
                    "Avoid target choices that expose valuable private information without benefit.",
                ],
                "distill_rules": [
                    "P1. Keep only listed player-id actions.",
                    "P2. Score targets by information gain for hidden roles and team objective.",
                    "P3. Penalize exposure risk and select the best legal target.",
                ],
                "verifier_checks": [
                    "selected_action is a listed player id",
                    "target choice is tied to role belief or team objective",
                ],
            },
            "question_generation": {
                "role_specs": ["question_answer_or_stop"],
                "fields": [
                    "role_context_from_observation",
                    "current_conversation_history",
                    "diagnostic_question_candidates",
                    "information_to_elicit_or_hide",
                    "question_leakage_risk",
                    "candidate_question_values",
                ],
                "reasoning_workflow": [
                    "Separate private role facts from public conversation.",
                    "Ask a concrete question that distinguishes likely hidden roles.",
                    "Word the question to avoid revealing critical private information.",
                ],
                "distill_rules": [
                    "P1. Produce a concrete openended question.",
                    "P2. Prefer the question that most separates hidden-role hypotheses.",
                    "P3. Avoid revealing private information unless it advances the team objective.",
                ],
                "verifier_checks": [
                    "openended_response is a concrete question",
                    "question is role-diagnostic rather than generic",
                ],
            },
            "answer_generation": {
                "role_specs": ["question_answer_or_stop"],
                "fields": [
                    "role_context_from_observation",
                    "current_conversation_history",
                    "question_asked",
                    "safe_answer_consistent_with_role",
                    "deception_or_revelation_risk",
                    "candidate_answer_values",
                ],
                "reasoning_workflow": [
                    "Identify what was asked and what private facts are risky.",
                    "Choose a truthful, partial, or deceptive answer that supports the team objective.",
                    "Avoid direct private-role leakage unless strategically justified.",
                ],
                "distill_rules": [
                    "P1. Produce a concrete openended answer.",
                    "P2. Protect private role information when disclosure helps the opposing team.",
                    "P3. Use partial disclosure or misdirection only when it improves team outcome.",
                ],
                "verifier_checks": [
                    "openended_response is a concrete answer",
                    "private information leakage is checked",
                ],
            },
            "stop_or_continue_accusation": {
                "role_specs": ["question_answer_or_stop"],
                "fields": [
                    "role_context_from_observation",
                    "current_conversation_history",
                    "accusation_confidence",
                    "wrong_accusation_penalty",
                    "continue_conversation_value",
                    "stop_now_expected_value",
                    "candidate_stop_or_pass_values",
                ],
                "reasoning_workflow": [
                    "Estimate whether current role beliefs justify an accusation.",
                    "Compare STOP against Pass using wrong-accusation risk.",
                    "Stop only when the best accusation is confident enough.",
                ],
                "distill_rules": [
                    "P1. Keep only STOP or Pass actions.",
                    "P2. Choose STOP only if accusation confidence exceeds wrong-accusation risk.",
                    "P3. Otherwise choose Pass.",
                ],
                "verifier_checks": [
                    "selected_action is STOP or Pass exactly as listed",
                    "wrong accusation risk is considered",
                ],
            },
            "accused_selection": {
                "role_specs": ["target_selection"],
                "fields": [
                    "role_context_from_observation",
                    "players_available_to_question_or_accuse",
                    "traitor_or_target_suspicion_by_player",
                    "team_objective_alignment",
                    "accusation_confidence",
                    "wrong_accusation_risk",
                    "candidate_accusation_values",
                ],
                "reasoning_workflow": [
                    "Rank possible accused players using the conversation and private role objective.",
                    "Select the player whose accusation best advances the team objective.",
                    "Avoid low-confidence accusations when possible.",
                ],
                "distill_rules": [
                    "P1. Keep only listed accused player ids.",
                    "P2. Rank candidates by suspicion and team objective alignment.",
                    "P3. Select the highest-confidence legal accused player.",
                ],
                "verifier_checks": [
                    "selected_action is a listed player id",
                    "accusation target is justified by belief state",
                ],
            },
        },
    },
    "codenames": {
        "default": "guess_or_end_turn",
        "contexts": {
            "submit_clue": {
                "role_specs": ["spymaster_signal_design"],
                "fields": [
                    "own_team_unrevealed_words_with_private_types",
                    "opponent_neutral_and_assassin_words_to_avoid",
                    "safe_target_cluster_for_this_clue",
                    "candidate_one_word_clues",
                    "expected_operative_interpretation_for_each_clue",
                    "clue_ambiguity_or_forbidden_word_risk",
                    "clue_number_risk_budget_by_candidate",
                    "openended_format_word_comma_number",
                ],
                "reasoning_workflow": [
                    "Build safe target clusters from own unrevealed team words.",
                    "Reject clues with strong overlap to opponent, neutral, or assassin words.",
                    "Choose a clue and number that a teammate is likely to interpret safely.",
                    "Return exactly one word and a number in the required format.",
                ],
                "distill_rules": [
                    "P1. Select submit_clue and produce word,number.",
                    "P2. Reject clue candidates with high opponent, neutral, or assassin ambiguity.",
                    "P3. Prefer the best safe expected operative interpretation.",
                    "P4. Use a conservative number when ambiguity is high.",
                ],
                "verifier_checks": [
                    "openended_response is exactly one word plus a number",
                    "clue is grounded in visible board words and private types",
                    "assassin and opponent-card risks are considered",
                ],
            },
            "guess_or_end_turn": {
                "role_specs": ["operative_signal_interpretation"],
                "fields": [
                    "current_clue_and_guess_limit",
                    "unrevealed_candidate_words",
                    "semantic_match_to_current_clue",
                    "public_history_from_last_hint_and_guesses",
                    "unknown_assassin_risk",
                    "unknown_opponent_or_neutral_risk",
                    "guess_vs_end_turn_value",
                    "candidate_guess_or_end_turn_values",
                ],
                "reasoning_workflow": [
                    "Rank unrevealed words by semantic fit to the current clue and public history.",
                    "Penalize candidates likely to be assassin, opponent, or neutral words.",
                    "Use the clue number as a risk budget.",
                    "Guess only when the best candidate exceeds end-turn value.",
                ],
                "distill_rules": [
                    "P1. Keep only listed guess_* and end_turn actions.",
                    "P2. Rank words by semantic match to current clue and public history.",
                    "P3. Penalize assassin, opponent, and neutral risk.",
                    "P4. Guess if best candidate beats end_turn; otherwise end_turn.",
                ],
                "verifier_checks": [
                    "selected guess or end_turn action id is listed",
                    "guess is grounded in the current clue and board",
                    "assassin and opponent-card risks are considered",
                ],
            },
        },
    },
    "hive": {
        "default": "piece_type_selection",
        "contexts": {
            "piece_type_selection": {
                "role_specs": ["piece_type_selection"],
                "fields": [
                    "list_place_or_list_move_actions",
                    "queen_placement_deadline",
                    "piece_type_attack_defense_role",
                    "followup_move_count_after_listing",
                    "queen_timing_or_exposure_risk",
                    "candidate_piece_action_values",
                ],
                "reasoning_workflow": [
                    "Identify whether listing placement or movement options best advances queen pressure.",
                    "Respect queen placement timing and defensive needs.",
                    "Choose the piece action whose follow-up options are strongest.",
                ],
                "distill_rules": [
                    "P1. Keep legal list_place, list_move, or pass actions.",
                    "P2. If queen timing requires placement, prioritize queen-safe placement listing.",
                    "P3. Otherwise choose the piece that creates the strongest attack or defense follow-up.",
                ],
                "verifier_checks": [
                    "selected_action is listed",
                    "queen placement timing is considered",
                ],
            },
            "placement_hex_choice": {
                "role_specs": ["placement_hex_choice"],
                "fields": [
                    "legal_hexes_for_active_piece",
                    "adjacency_to_own_and_opponent_pieces",
                    "queen_pressure_created",
                    "future_mobility_preserved",
                    "queen_exposure_or_mobility_risk",
                    "candidate_placement_hex_values",
                ],
                "reasoning_workflow": [
                    "Compare legal placement hexes by queen pressure and own mobility.",
                    "Avoid placements that expose own queen or violate adjacency constraints.",
                    "Choose the placement that improves attack or defense most.",
                ],
                "distill_rules": [
                    "P1. Keep only listed place actions.",
                    "P2. Prefer placements that increase opponent queen pressure without trapping own pieces.",
                    "P3. Select the best legal placement hex.",
                ],
                "verifier_checks": [
                    "selected_action is a listed placement",
                    "placement constraints and mobility are considered",
                ],
            },
            "movement_hex_choice": {
                "role_specs": ["movement_hex_choice"],
                "fields": [
                    "active_piece_current_hex",
                    "legal_destination_hexes",
                    "one_hive_and_slide_legality",
                    "queen_surround_progress",
                    "own_queen_escape_squares",
                    "own_queen_trap_risk",
                    "candidate_movement_hex_values",
                ],
                "reasoning_workflow": [
                    "Keep only legal movement destinations that preserve hive constraints.",
                    "Prefer moves that surround the opponent queen or open own queen escape.",
                    "Avoid moves that break the hive or lose queen mobility.",
                ],
                "distill_rules": [
                    "P1. Keep only listed move actions.",
                    "P2. Reject moves that break one-hive or slide constraints.",
                    "P3. Prefer queen pressure while preserving own queen mobility.",
                ],
                "verifier_checks": [
                    "selected_action is a listed movement",
                    "one-hive and slide constraints are considered",
                ],
            },
        },
    },
    "pit": {
        "default": "offer_trade",
        "contexts": {
            "offer_trade": {
                "role_specs": ["offer_trade"],
                "fields": [
                    "own_surplus_commodities",
                    "target_corner_commodity",
                    "bull_or_bear_exposure",
                    "quantity_to_offer_without_harming_target",
                    "signal_leakage_from_offer",
                    "offer_signal_or_target_set_risk",
                    "candidate_offer_values",
                ],
                "reasoning_workflow": [
                    "Identify the strongest target commodity set from own hand.",
                    "Offer surplus or low-fit commodities first.",
                    "Avoid offers that damage the target set or expose too much information.",
                ],
                "distill_rules": [
                    "P1. Keep only listed Offer_* actions.",
                    "P2. Protect cards in the best target commodity set.",
                    "P3. Offer duplicates or off-target commodities with the least opportunity cost.",
                ],
                "verifier_checks": [
                    "selected_action is a listed Offer_* action",
                    "offered commodity is available in own hand",
                ],
            },
            "accept_trade": {
                "role_specs": ["accept_trade"],
                "fields": [
                    "pending_trade_offered_commodity_and_quantity",
                    "requested_response_commodity_cost",
                    "target_corner_progress_before_after_trade",
                    "bull_or_bear_risk_change",
                    "accept_vs_make_new_offer_value",
                    "candidate_accept_or_offer_values",
                ],
                "reasoning_workflow": [
                    "Read the pending trade and own requested response cost.",
                    "Compare target-set progress before and after accepting.",
                    "Accept only if expected set value improves over making a new offer.",
                ],
                "distill_rules": [
                    "P1. Keep listed Accept_* and Offer_* actions.",
                    "P2. Prefer Accept_* only when it improves expected set-completion value.",
                    "P3. Otherwise choose the best low-cost Offer_* action.",
                ],
                "verifier_checks": [
                    "selected_action is listed",
                    "acceptance value is compared with own hand cost",
                ],
            },
        },
    },
    "santorini": {
        "default": "move_build_phase",
        "contexts": {
            "placement_phase": {
                "role_specs": ["placement_phase"],
                "fields": [
                    "own_unplaced_pawn",
                    "empty_board_squares",
                    "centrality_and_future_mobility_value",
                    "pair_spacing_between_own_pawns",
                    "opponent_placement_pressure",
                    "placement_safety_or_containment_risk",
                    "candidate_placement_values",
                ],
                "reasoning_workflow": [
                    "Compare legal placement squares by centrality and future mobility.",
                    "Maintain useful spacing between own pawns.",
                    "Avoid placements that make early containment easy.",
                ],
                "distill_rules": [
                    "P1. Keep only listed coordinate action ids.",
                    "P2. Prefer central and mobile placements with good own-pawn spacing.",
                    "P3. Avoid placements that give the opponent easy containment.",
                ],
                "verifier_checks": [
                    "selected_action is a listed coordinate",
                    "future mobility and pawn spacing are considered",
                ],
            },
            "move_build_phase": {
                "role_specs": ["move_build_phase"],
                "fields": [
                    "legal_move_squares",
                    "legal_build_squares_after_move",
                    "immediate_win_moves",
                    "opponent_immediate_win_threats",
                    "mobility_after_action",
                    "height_access_to_level_three",
                    "candidate_move_build_values",
                ],
                "reasoning_workflow": [
                    "Check for a legal immediate win by moving to level 3.",
                    "If no immediate win, block the opponent's immediate level-3 threats.",
                    "Choose move-build pairs that improve own height access and reduce opponent mobility.",
                    "Verify the selected action contains both a legal move and build.",
                ],
                "distill_rules": [
                    "P1. Take an immediate winning move if listed.",
                    "P2. Else block opponent immediate level-3 threats.",
                    "P3. Else maximize future level-3 access while preserving mobility.",
                    "P4. Verify both move and build are legal in the selected action id.",
                ],
                "verifier_checks": [
                    "selected_action is a listed move-build action",
                    "immediate win and block were checked",
                    "move and build constraints are respected",
                ],
            },
        },
    },
    "sea_battle": {
        "default": "simultaneous_move_and_shoot",
        "contexts": {
            "simultaneous_move_and_shoot": {
                "role_specs": ["simultaneous_move_and_shoot_plan", "team_ship_role"],
                "fields": [
                    "candidate_first_movement_claims",
                    "candidate_second_movement_claims_after_turn",
                    "rock_collision_risk",
                    "ship_collision_risk_with_teammates_and_opponents",
                    "post_move_left_and_right_shot_lanes",
                    "expected_damage_dealt_minus_taken",
                    "own_damage_survival_margin",
                    "nearest_teammate_spacing",
                    "nearest_opponent_bearing",
                    "focus_fire_or_evasion_value",
                ],
                "reasoning_workflow": [
                    "Reject actions likely to collide with rocks, teammates, or opponents.",
                    "Among safe actions, prefer post-move shot lanes on opponents.",
                    "Account for own survival margin and likely return fire.",
                    "Break ties by preserving team spacing.",
                ],
                "distill_rules": [
                    "P1. Remove actions with high rock, ship, or sinking risk.",
                    "P2. Among safe actions, prefer likely post-move shots on opponents.",
                    "P3. Break ties by survival margin, nearest opponent bearing, and teammate spacing.",
                ],
                "verifier_checks": [
                    "selected_action is exactly listed",
                    "collision and rock risks are checked",
                    "shooting direction is evaluated from the post-move heading",
                ],
            },
        },
    },
    "two_rooms_and_a_boom": {
        "default": "target_selection",
        "role_overlays": {
            "special_role_policy": [
                "special_role_private_status",
                "team_objective_from_private_role",
                "safe_signal_value_to_team",
                "misdirection_or_silence_value",
                "special_role_revelation_risk",
            ],
        },
        "contexts": {
            "target_selection": {
                "role_specs": ["nonleader_information_gathering"],
                "fields": [
                    "own_team_and_special_role",
                    "roommates_available_to_question",
                    "claims_heard_so_far",
                    "diagnostic_question_targets",
                    "safe_claim_or_answer_policy",
                    "information_leakage_risk",
                    "candidate_target_values",
                ],
                "reasoning_workflow": [
                    "Choose the roommate whose response most improves President/Bomber or team-location beliefs.",
                    "Protect private role information unless disclosure helps the team objective.",
                    "Prefer targets aligned with same-room or separate-room objective.",
                ],
                "distill_rules": [
                    "P1. Keep only listed player-id actions.",
                    "P2. Rank targets by information gain and team-objective alignment.",
                    "P3. Penalize private role leakage and select the best target.",
                ],
                "verifier_checks": [
                    "selected_action is a listed player id",
                    "target choice supports team objective",
                ],
            },
            "question_generation": {
                "role_specs": ["nonleader_information_gathering"],
                "fields": [
                    "own_team_and_special_role",
                    "claims_heard_so_far",
                    "diagnostic_question_targets",
                    "safe_claim_or_answer_policy",
                    "information_leakage_risk",
                    "candidate_question_values",
                ],
                "reasoning_workflow": [
                    "Ask a concrete question that improves role or team-location beliefs.",
                    "Use wording that protects own special role if needed.",
                    "Avoid generic chatter that does not affect trades or final room configuration.",
                ],
                "distill_rules": [
                    "P1. Produce the required openended question.",
                    "P2. Prefer diagnostic questions about team, role, room, or leader-relevant information.",
                    "P3. Avoid revealing private special-role information without benefit.",
                ],
                "verifier_checks": [
                    "openended_response is a concrete question",
                    "question improves role-location beliefs or team coordination",
                ],
            },
            "answer_generation": {
                "role_specs": ["nonleader_information_gathering"],
                "fields": [
                    "own_team_and_special_role",
                    "question_asked",
                    "safe_claim_or_answer_policy",
                    "information_leakage_risk",
                    "candidate_answer_values",
                ],
                "reasoning_workflow": [
                    "Identify the question and which private facts are risky.",
                    "Answer to improve team coordination while limiting leakage to opponents.",
                    "Use partial disclosure only when it moves trades or beliefs toward the objective.",
                ],
                "distill_rules": [
                    "P1. Produce the required openended answer.",
                    "P2. Protect special-role information unless disclosure supports the team objective.",
                    "P3. Give a concrete answer rather than generic refusal when safe.",
                ],
                "verifier_checks": [
                    "openended_response is a concrete answer",
                    "private role leakage is considered",
                ],
            },
            "leader_hostage_trade": {
                "role_specs": ["leader_hostage_trade"],
                "fields": [
                    "eligible_hostages_to_trade",
                    "posterior_president_location",
                    "posterior_bomber_location",
                    "team_goal_same_or_separate",
                    "trade_effect_on_final_co_location",
                    "trade_information_leakage_risk",
                    "candidate_trade_values",
                ],
                "reasoning_workflow": [
                    "Condition on whether the team wants President and Bomber together or apart.",
                    "Estimate President and Bomber room-location beliefs.",
                    "Choose the eligible hostage trade that moves final co-location toward team objective.",
                    "Avoid trades that expose a critical special role without benefit.",
                ],
                "distill_rules": [
                    "P1. Keep only listed hostage player ids.",
                    "P2. Estimate President/Bomber room beliefs and team objective.",
                    "P3. Select the trade that most improves final co-location outcome.",
                    "P4. Penalize special-role leakage or opponent-helping trades.",
                ],
                "verifier_checks": [
                    "selected_action is an eligible player id",
                    "trade supports same-room or separate-room objective",
                    "private role leakage is considered",
                ],
            },
        },
    },
    "tic_tac_toe": {
        "default": "mark_empty_square",
        "contexts": {
            "mark_empty_square": {
                "role_specs": [],
                "fields": [
                    "board_state",
                    "legal_empty_squares",
                    "own_immediate_wins",
                    "opponent_immediate_wins",
                    "fork_threats",
                    "candidate_action_values",
                ],
                "reasoning_workflow": [
                    "Take an immediate win.",
                    "Block an opponent immediate win.",
                    "Create or block forks, then prefer center, corners, and edges.",
                ],
                "distill_rules": [
                    "P1. Win if possible.",
                    "P2. Else block a loss.",
                    "P3. Else choose the strongest minimax square.",
                ],
                "verifier_checks": [
                    "selected square is empty and listed",
                    "immediate win and block were checked",
                ],
            },
        },
    },
}


GAMEBENCH_FIELD_TARGETS = {
    "air_land_sea": {
        "normal_deploy_improvise_withdraw": [
            "Compute which theaters are currently won, lost, or swingable.",
            "Compute each legal card action's theater-control swing and future hand cost.",
            "Compute whether withdrawing now beats the continuation value.",
            "Compute commitment and information risk from face-up versus face-down play.",
        ],
        "tactical_effect_resolution": [
            "Compute the tactical effect currently being resolved and its legal target set.",
            "Compute each target's theater-control swing after the effect resolves.",
            "Compute reveal, cover, movement, or return risk for each legal target.",
            "Compute when the legal do-nothing option is better than using the effect.",
        ],
    },
    "arctic_scavengers": {
        "resource_gathering": [
            "Compute which resource actions are feasible with the visible hand and unused action limits.",
            "Compute deck-improvement value versus the skirmish strength sacrificed by each command.",
            "Compute food and medicine feasibility for HUNT and HIRE lines.",
            "Compute the exact openended command needed for the best legal resource line.",
        ],
        "interrupt_response": [
            "Compute the value of canceling or weakening the opponent's announced action.",
            "Compute whether SNIPER or SABOTEUR is legal with a valid target.",
            "Compute the discard and future-hand cost of interrupting.",
            "Compute STOP value when no interrupt has positive net value.",
        ],
        "skirmish_action": [
            "Compute current fight and tribe-size comparison before extra attacks.",
            "Compute which SNIPER or SABOTEUR target would change the contested-resource result.",
            "Compute attack risk from spending or exposing skirmish cards.",
            "Compute STOP value when attacks do not improve the skirmish outcome.",
        ],
        "dig_card_selection": [
            "Compute each drawn junkyard card's future deck value.",
            "Compute synergy with current resource, fight, food, and tribe needs.",
            "Compute opportunity cost of returning the other drawn cards.",
            "Compute candidate keep values for the listed card actions.",
        ],
    },
    "are_you_the_traitor": {
        "target_selection": [
            "Compute private role objective from the current context.",
            "Compute which target would most reduce hidden-role uncertainty.",
            "Compute team-objective value and private-role exposure risk for each target.",
        ],
        "question_generation": [
            "Compute the hidden-role belief gap that the next question should resolve.",
            "Compute diagnostic question candidates that separate likely roles.",
            "Compute leakage risk from each possible question wording.",
        ],
        "answer_generation": [
            "Compute what the question asks and which private facts are dangerous to reveal.",
            "Compute truthful, partial, and deceptive answer values for the team objective.",
            "Compute revelation risk against likely opposing roles.",
        ],
        "stop_or_continue_accusation": [
            "Compute accusation confidence from public conversation and private role context.",
            "Compute wrong-accusation penalty versus continued information gathering value.",
            "Compute STOP versus Pass values under the current belief state.",
        ],
        "accused_selection": [
            "Compute suspicion over each legal accused player.",
            "Compute which accusation best advances the private team objective.",
            "Compute wrong-accusation risk for each candidate target.",
        ],
    },
    "codenames": {
        "submit_clue": [
            "Compute safe clusters of unrevealed own-team words from private card colors.",
            "Compute clue candidates and predicted operative interpretations.",
            "Compute ambiguity risk against opponent, neutral, and assassin words.",
            "Compute the clue-number risk budget before producing word,number.",
        ],
        "guess_or_end_turn": [
            "Compute the current clue, remaining guess budget, and unrevealed candidates.",
            "Compute semantic fit of each legal guess to the clue and public history.",
            "Compute assassin, opponent, and neutral risk as uncertainty, not fact.",
            "Compute guess value versus end-turn value.",
        ],
    },
    "hive": {
        "piece_type_selection": [
            "Compute whether the current decision should list placement or movement follow-ups.",
            "Compute queen timing, queen safety, and attack-defense role by piece type.",
            "Compute follow-up option value for each listed piece action.",
        ],
        "placement_hex_choice": [
            "Compute legal placement hexes for the active piece.",
            "Compute queen pressure, future mobility, and adjacency consequences by hex.",
            "Compute own queen exposure or mobility risk from each placement.",
        ],
        "movement_hex_choice": [
            "Compute legal destination hexes for the active piece under Hive constraints.",
            "Compute queen-surround progress and own queen escape impact by move.",
            "Compute one-hive, slide, and trapping risk for each destination.",
        ],
    },
    "pit": {
        "offer_trade": [
            "Compute own target commodity set and surplus off-target cards.",
            "Compute opportunity cost of each listed Offer action.",
            "Compute market, Bull/Bear, and signal-leakage risk from each offer.",
        ],
        "accept_trade": [
            "Compute what the pending trade gives and what the response costs.",
            "Compute target-set progress before and after each Accept action.",
            "Compute Bull/Bear risk and whether making a new offer has higher value.",
        ],
    },
    "santorini": {
        "placement_phase": [
            "Compute centrality and future mobility of each legal placement square.",
            "Compute useful spacing between own pawns after placement.",
            "Compute containment or pressure risk created by each placement.",
        ],
        "move_build_phase": [
            "Compute immediate winning move-build actions if any are listed.",
            "Compute opponent immediate level-3 threats that need blocking.",
            "Compute mobility, height access, and opponent-mobility reduction for each move-build action.",
        ],
    },
    "sea_battle": {
        "simultaneous_move_and_shoot": [
            "Compute post-move position and heading for each legal movement pattern.",
            "Compute rock, ship-collision, and sinking risk under simultaneous movement.",
            "Compute left/right shot lanes after movement and expected damage swing.",
            "Compute team spacing and survival value before selecting the action.",
        ],
    },
    "two_rooms_and_a_boom": {
        "target_selection": [
            "Compute private team or special-role objective from the context.",
            "Compute which target best improves President/Bomber or team-location beliefs.",
            "Compute information leakage risk from talking to each legal target.",
        ],
        "question_generation": [
            "Compute the role-location belief gap relevant to the team's same-room or separate-room objective.",
            "Compute diagnostic question candidates for the chosen target.",
            "Compute special-role leakage risk from each question.",
        ],
        "answer_generation": [
            "Compute what was asked and which private role facts are safe or unsafe.",
            "Compute answer candidates that help the team objective while limiting leakage.",
            "Compute value of truth, partial disclosure, silence, or misdirection.",
        ],
        "leader_hostage_trade": [
            "Compute posterior President and Bomber room locations from leader context.",
            "Compute how each legal hostage trade changes final co-location probability.",
            "Compute leakage or opponent-helping risk from trading each eligible hostage.",
        ],
    },
    "tic_tac_toe": {
        "mark_empty_square": [
            "Compute immediate winning squares and immediate blocks.",
            "Compute fork creation and fork prevention opportunities.",
            "Compute minimax value for remaining legal empty squares.",
        ],
    },
}


def theory_mapping_for_game(game_id: str):
    return GAMEBENCH_THEORY_MAPPINGS.get(canonical_game_id(game_id), GENERIC_THEORY_MAPPING)


def _action_blob(predefined_actions, openended_actions, action_instructions):
    pieces = [action_instructions or ""]
    for action, description in (predefined_actions or {}).items():
        pieces.append(str(action))
        pieces.append(str(description or ""))
    for action, description in (openended_actions or {}).items():
        pieces.append(str(action))
        pieces.append(str(description or ""))
    return "\n".join(pieces).lower()


def _all_predefined_ids(predefined_actions):
    return [str(action) for action in (predefined_actions or {}).keys()]


def _numeric_action_ids(predefined_actions):
    ids = _all_predefined_ids(predefined_actions)
    return bool(ids) and all(action.isdigit() for action in ids)


def _tuple_coordinate_actions(predefined_actions):
    ids = _all_predefined_ids(predefined_actions)
    if not ids:
        return False
    return all(action.strip().startswith("(") and action.strip().endswith(")") for action in ids)


def _detect_are_you_role_overlay(observation_text):
    text = (observation_text or "").lower()
    if "i am player 0" in text or "as the traitor" in text or "i am the traitor" in text:
        return "traitor_undercover"
    if (
        "i am player 1" in text
        or "i am the evil wizard" in text
        or "as the evil wizard" in text
    ):
        return "evil_wizard_deception"
    if (
        "i am player 2" in text
        or "i am the good wizard" in text
        or "as the good wizard" in text
    ):
        return "good_wizard_trust_building"
    if (
        "i am player 3" in text
        or "i am the keyholder" in text
        or "i am the key holder" in text
        or "as the keyholder" in text
        or "as the key holder" in text
    ):
        return "key_holder_screening"
    if (
        "i am player 4" in text
        or "i am a guard" in text
        or "as a guard" in text
        or "in my role as a guard" in text
    ):
        return "guard_traitor_hunt"
    return None


def _detect_two_rooms_role_overlay(observation_text):
    text = (observation_text or "").lower()
    if "president" in text or "bomber" in text:
        return "special_role_policy"
    return None


def detect_prompt_context(
    game_id,
    observation_text,
    action_instructions,
    predefined_actions,
    openended_actions,
):
    """Select a pre-authored prompt context from the current action space.

    This router does not create strategy fields. It only chooses among field
    specs authored in GAMEBENCH_ACTIVE_CONTEXTS so the runtime model executes
    the active field/program rather than selecting from every game-level option.
    """

    game_key = canonical_game_id(game_id)
    game_spec = GAMEBENCH_ACTIVE_CONTEXTS.get(game_key)
    if not game_spec:
        return {
            "active_action_space_program": "generic_best_response",
            "active_role_specs": [],
            "context_detection_confidence": "low",
            "context_detection_rule": "no game-specific prompt context spec was found",
            "active_fields": [],
            "reasoning_workflow": GENERIC_THEORY_MAPPING["decision_workflow"],
            "distill_rules": GENERIC_THEORY_MAPPING["distill_rules"],
            "verifier_checks": GENERIC_THEORY_MAPPING["verifier_checks"],
        }

    blob = _action_blob(predefined_actions, openended_actions, action_instructions)
    predefined_ids = set(_all_predefined_ids(predefined_actions))
    openended_ids = set(str(action) for action in (openended_actions or {}).keys())
    observation_lower = (observation_text or "").lower()
    context_name = game_spec["default"]
    confidence = "medium"
    rule = "default action-space program"

    if game_key == "air_land_sea":
        effect_terms = ("flip", "move", "return", "adjacent theater", "drawn card", "do nothing", "not move", "not return")
        if any(term in blob for term in effect_terms) and not any(term in blob for term in ("withdraw", "deploy", "improvise")):
            context_name = "tactical_effect_resolution"
            confidence = "high"
            rule = "effect-resolution action descriptions detected"
        elif any(term in blob for term in ("play ", "withdraw", "deploy", "improvise")):
            context_name = "normal_deploy_improvise_withdraw"
            confidence = "high"
            rule = "normal Play/Withdraw action descriptions detected"

    elif game_key == "arctic_scavengers":
        if predefined_ids and not openended_ids:
            context_name = "dig_card_selection"
            confidence = "high"
            rule = "predefined drawn-card choices detected"
        elif {"DIG", "DRAW", "HIRE", "HUNT", "TRASH"} & openended_ids:
            context_name = "resource_gathering"
            confidence = "high"
            rule = "resource-gathering openended actions detected"
        elif {"SNIPER", "SABOTEUR"} & openended_ids:
            if "opponent has announced" in observation_lower:
                context_name = "interrupt_response"
                confidence = "high"
                rule = "opponent-announced action response detected"
            else:
                context_name = "skirmish_action"
                confidence = "medium"
                rule = "SNIPER/SABOTEUR action space detected"

    elif game_key == "are_you_the_traitor":
        if openended_ids:
            if "answer" in blob or "asked me" in observation_lower:
                context_name = "answer_generation"
                confidence = "high"
                rule = "openended answer prompt detected"
            else:
                context_name = "question_generation"
                confidence = "high"
                rule = "openended question prompt detected"
        elif {"STOP", "Pass", "pass"} & predefined_ids:
            context_name = "stop_or_continue_accusation"
            confidence = "high"
            rule = "STOP/Pass accusation gate detected"
        elif _numeric_action_ids(predefined_actions):
            if "wrong accusation" in blob or "accus" in observation_lower:
                context_name = "accused_selection"
                confidence = "medium"
                rule = "numeric player ids with accusation context detected"
            else:
                context_name = "target_selection"
                confidence = "medium"
                rule = "numeric player ids detected"

    elif game_key == "codenames":
        if "submit_clue" in openended_ids:
            context_name = "submit_clue"
            confidence = "high"
            rule = "submit_clue openended action detected"
        elif "end_turn" in predefined_ids or any(action.startswith("guess_") for action in predefined_ids):
            context_name = "guess_or_end_turn"
            confidence = "high"
            rule = "guess/end_turn predefined actions detected"

    elif game_key == "hive":
        if any(action.startswith("place") for action in predefined_ids):
            context_name = "placement_hex_choice"
            confidence = "high"
            rule = "concrete placement actions detected"
        elif any(action.startswith("move") for action in predefined_ids):
            context_name = "movement_hex_choice"
            confidence = "high"
            rule = "concrete movement actions detected"
        elif any(action.startswith("list_place") or action.startswith("list_move") for action in predefined_ids):
            context_name = "piece_type_selection"
            confidence = "high"
            rule = "piece listing actions detected"

    elif game_key == "pit":
        if any(action.startswith("Accept_") for action in predefined_ids):
            context_name = "accept_trade"
            confidence = "high"
            rule = "Accept_* trade actions detected"
        elif any(action.startswith("Offer_") for action in predefined_ids):
            context_name = "offer_trade"
            confidence = "high"
            rule = "Offer_* trade actions detected"

    elif game_key == "santorini":
        if "initial pawn placement" in blob or _tuple_coordinate_actions(predefined_actions):
            context_name = "placement_phase"
            confidence = "high"
            rule = "initial placement coordinate actions detected"
        elif any(action.startswith("Move ") or "build" in action for action in predefined_ids):
            context_name = "move_build_phase"
            confidence = "high"
            rule = "move-build action ids detected"

    elif game_key == "sea_battle":
        context_name = "simultaneous_move_and_shoot"
        confidence = "high"
        rule = "Sea Battle has one simultaneous move-and-shoot action space"

    elif game_key == "two_rooms_and_a_boom":
        if openended_ids:
            if "answer" in blob or "asked me" in observation_lower:
                context_name = "answer_generation"
                confidence = "high"
                rule = "openended answer prompt detected"
            else:
                context_name = "question_generation"
                confidence = "high"
                rule = "openended question prompt detected"
        elif _numeric_action_ids(predefined_actions):
            if "leader" in observation_lower:
                context_name = "leader_hostage_trade"
                confidence = "medium"
                rule = "numeric player ids with leader context detected"
            else:
                context_name = "target_selection"
                confidence = "medium"
                rule = "numeric player ids detected"

    elif game_key == "tic_tac_toe":
        context_name = "mark_empty_square"
        confidence = "high"
        rule = "Tic-Tac-Toe has one mark-empty-square action space"

    contexts = game_spec["contexts"]
    context = contexts.get(context_name) or contexts[game_spec["default"]]
    active_fields = list(context.get("fields", []))
    role_specs = list(context.get("role_specs", []))
    candidate_contexts = []
    if confidence != "high":
        candidate_contexts = [name for name in contexts if name != context_name]

    overlay_name = None
    if game_key == "are_you_the_traitor":
        overlay_name = _detect_are_you_role_overlay(observation_text)
    elif game_key == "two_rooms_and_a_boom":
        overlay_name = _detect_two_rooms_role_overlay(observation_text)
    if overlay_name and overlay_name in game_spec.get("role_overlays", {}):
        role_specs.append(overlay_name)
        active_fields.extend(game_spec["role_overlays"][overlay_name])

    return {
        "active_action_space_program": context_name,
        "active_role_specs": role_specs,
        "context_detection_confidence": confidence,
        "context_detection_rule": rule,
        "candidate_action_space_programs_if_ambiguous": candidate_contexts,
        "field_targets": GAMEBENCH_FIELD_TARGETS.get(game_key, {}).get(context_name, []),
        "active_fields": active_fields,
        "reasoning_workflow": context.get("reasoning_workflow", []),
        "distill_rules": context.get("distill_rules", []),
        "verifier_checks": context.get("verifier_checks", []),
    }


def _bullet_lines(items):
    return "\n".join(f"- {item}" for item in items)


def _role_or_phase_lines(mapping):
    field_sets = mapping.get("role_or_phase_fields")
    if not field_sets:
        return ""

    lines = []
    selection_rule = mapping.get("role_or_phase_selection_rule")
    if selection_rule:
        lines.append(f"- Selection rule: {selection_rule}")
    for set_name, fields in field_sets.items():
        lines.append(f"- {set_name}:")
        lines.extend(f"  - {field}" for field in fields)
    return "\n".join(lines)


def _active_context_lines(active_context):
    if not active_context:
        return ""
    role_specs = active_context.get("active_role_specs") or []
    fields = active_context.get("active_fields") or []
    lines = [
        f"- Action-space program: {active_context.get('active_action_space_program', 'unresolved')}",
        f"- Context detection confidence: {active_context.get('context_detection_confidence', 'unknown')}",
        f"- Context detection rule: {active_context.get('context_detection_rule', 'unspecified')}",
    ]
    if role_specs:
        lines.append("- Active role-specific specs: " + ", ".join(role_specs))
    else:
        lines.append("- Active role-specific specs: none")
    candidates = active_context.get("candidate_action_space_programs_if_ambiguous") or []
    if candidates:
        lines.append("- Limited alternate action-space candidates if the selected context is contradicted: " + ", ".join(candidates))
    targets = active_context.get("field_targets") or []
    if targets:
        lines.append("- Field computation targets:")
        lines.extend(f"  - {target}" for target in targets)
    if fields:
        lines.append("- Active role/action-space fields:")
        lines.extend(f"  - {field}" for field in fields)
    return "\n".join(lines)


def _fallback_field_target_lines(mapping):
    targets = mapping.get("field_computation_targets") or GENERIC_THEORY_MAPPING["field_computation_targets"]
    if not targets:
        return ""
    return _bullet_lines(targets)


def _workflow_for_context(mapping, active_context):
    if active_context and active_context.get("reasoning_workflow"):
        return active_context["reasoning_workflow"]
    return mapping.get("decision_workflow", GENERIC_THEORY_MAPPING["decision_workflow"])


def _program_for_context(mapping, active_context):
    if active_context and active_context.get("distill_rules"):
        return active_context["distill_rules"]
    return mapping.get("distill_rules", GENERIC_THEORY_MAPPING["distill_rules"])


def _verifier_for_context(mapping, active_context):
    if active_context and active_context.get("verifier_checks"):
        return active_context["verifier_checks"]
    return mapping.get("verifier_checks", GENERIC_THEORY_MAPPING["verifier_checks"])


def field_register_for_prompt(mapping, active_context=None):
    fields = list(mapping.get("required_state_fields", []))
    active_fields = []
    if active_context:
        active_fields = list(active_context.get("active_fields") or [])
    seen = set()
    ordered = []
    for field in fields + active_fields:
        if field in seen:
            continue
        seen.add(field)
        ordered.append(field)
    return ordered


REQUIRED_FIELD_SETS_BY_GAME_CONTEXT = {
    "air_land_sea": {
        "normal_deploy_improvise_withdraw": [
            "playable_faceup_cards_by_matching_theater",
            "playable_facedown_cards_by_theater",
            "withdrawal_points_given_remaining_hand",
            "current_theater_majority_status",
            "card_conservation_value",
            "faceup_deploy_control_swing",
            "facedown_improvise_information_value",
            "action_risk_by_commitment_and_information",
            "candidate_card_or_withdraw_values",
        ],
        "tactical_effect_resolution": [
            "triggering_tactical_card",
            "legal_effect_targets_or_extra_play_options",
            "own_vs_opponent_card_ownership",
            "control_swing_after_effect",
            "reveal_or_cover_information_cost",
            "effect_target_risk_by_option",
            "do_nothing_or_skip_value_if_available",
            "candidate_effect_target_values",
        ],
    },
    "arctic_scavengers": {
        "resource_gathering": [
            "available_standard_and_modifier_cards",
            "unused_once_per_round_actions",
            "dig_draw_hunt_hire_trash_feasibility",
            "food_and_medicine_budget",
            "deck_improvement_vs_skirmish_cost",
            "resource_action_cost_or_risk",
            "candidate_resource_action_values",
            "openended_list_command",
        ],
        "interrupt_response": [
            "opponent_announced_action",
            "available_sniper_or_saboteur_cards",
            "valid_interrupt_targets",
            "value_of_canceling_opponent_action",
            "discard_cost_of_interrupt",
            "interrupt_target_or_discard_risk",
            "interrupt_feasibility_by_action",
            "candidate_interrupt_values",
        ],
        "skirmish_action": [
            "own_visible_fight_and_people_score",
            "opponent_visible_fight_and_people_score",
            "sniper_or_saboteur_targets",
            "contested_resource_value",
            "skirmish_action_risk",
            "candidate_skirmish_action_values",
        ],
        "dig_card_selection": [
            "drawn_junkyard_cards",
            "card_added_to_reserve_value",
            "cards_returned_to_junkyard_cost",
            "card_keep_risk_or_opportunity_cost",
            "candidate_dig_keep_values",
        ],
    },
    "are_you_the_traitor": {
        "target_selection": [
            "role_context_from_observation",
            "players_available_to_question_or_accuse",
            "information_gain_by_target",
            "team_objective_alignment",
            "risk_of_revealing_private_role",
            "candidate_target_values",
        ],
        "question_generation": [
            "role_context_from_observation",
            "current_conversation_history",
            "diagnostic_question_candidates",
            "information_to_elicit_or_hide",
            "question_leakage_risk",
            "candidate_question_values",
        ],
        "answer_generation": [
            "role_context_from_observation",
            "current_conversation_history",
            "question_asked",
            "safe_answer_consistent_with_role",
            "deception_or_revelation_risk",
            "candidate_answer_values",
        ],
        "stop_or_continue_accusation": [
            "role_context_from_observation",
            "current_conversation_history",
            "accusation_confidence",
            "wrong_accusation_penalty",
            "continue_conversation_value",
            "stop_now_expected_value",
            "candidate_stop_or_pass_values",
        ],
        "accused_selection": [
            "role_context_from_observation",
            "players_available_to_question_or_accuse",
            "traitor_or_target_suspicion_by_player",
            "team_objective_alignment",
            "accusation_confidence",
            "wrong_accusation_risk",
            "candidate_accusation_values",
        ],
    },
    "codenames": {
        "submit_clue": [
            "own_team_unrevealed_words_with_private_types",
            "opponent_neutral_and_assassin_words_to_avoid",
            "safe_target_cluster_for_this_clue",
            "expected_operative_interpretation_for_each_clue",
            "clue_ambiguity_or_forbidden_word_risk",
            "clue_number_risk_budget_by_candidate",
        ],
        "guess_or_end_turn": [
            "current_clue_and_guess_limit",
            "unrevealed_candidate_words",
            "semantic_match_to_current_clue",
            "public_history_from_last_hint_and_guesses",
            "unknown_assassin_risk",
            "unknown_opponent_or_neutral_risk",
            "guess_vs_end_turn_value",
            "candidate_guess_or_end_turn_values",
        ],
    },
    "hive": {
        "piece_type_selection": [
            "list_place_or_list_move_actions",
            "queen_placement_deadline",
            "piece_type_attack_defense_role",
            "followup_move_count_after_listing",
            "queen_timing_or_exposure_risk",
            "candidate_piece_action_values",
        ],
        "placement_hex_choice": [
            "legal_hexes_for_active_piece",
            "adjacency_to_own_and_opponent_pieces",
            "queen_pressure_created",
            "future_mobility_preserved",
            "queen_exposure_or_mobility_risk",
            "candidate_placement_hex_values",
        ],
        "movement_hex_choice": [
            "active_piece_current_hex",
            "legal_destination_hexes",
            "one_hive_and_slide_legality",
            "queen_surround_progress",
            "own_queen_escape_squares",
            "own_queen_trap_risk",
            "candidate_movement_hex_values",
        ],
    },
    "pit": {
        "offer_trade": [
            "own_surplus_commodities",
            "target_corner_commodity",
            "bull_or_bear_exposure",
            "quantity_to_offer_without_harming_target",
            "signal_leakage_from_offer",
            "offer_signal_or_target_set_risk",
            "candidate_offer_values",
        ],
        "accept_trade": [
            "pending_trade_offered_commodity_and_quantity",
            "requested_response_commodity_cost",
            "target_corner_progress_before_after_trade",
            "bull_or_bear_risk_change",
            "accept_vs_make_new_offer_value",
            "candidate_accept_or_offer_values",
        ],
    },
    "santorini": {
        "placement_phase": [
            "own_unplaced_pawn",
            "empty_board_squares",
            "centrality_and_future_mobility_value",
            "pair_spacing_between_own_pawns",
            "opponent_placement_pressure",
            "placement_safety_or_containment_risk",
            "candidate_placement_values",
        ],
        "move_build_phase": [
            "legal_move_squares",
            "legal_build_squares_after_move",
            "immediate_win_moves",
            "opponent_immediate_win_threats",
            "mobility_after_action",
            "height_access_to_level_three",
            "candidate_move_build_values",
        ],
    },
    "sea_battle": {
        "simultaneous_move_and_shoot": [
            "candidate_first_movement_claims",
            "candidate_second_movement_claims_after_turn",
            "rock_collision_risk",
            "ship_collision_risk_with_teammates_and_opponents",
            "post_move_left_and_right_shot_lanes",
            "expected_damage_dealt_minus_taken",
            "own_damage_survival_margin",
            "nearest_teammate_spacing",
            "nearest_opponent_bearing",
            "focus_fire_or_evasion_value",
        ],
    },
    "two_rooms_and_a_boom": {
        "target_selection": [
            "own_team_and_special_role",
            "roommates_available_to_question",
            "claims_heard_so_far",
            "diagnostic_question_targets",
            "safe_claim_or_answer_policy",
            "information_leakage_risk",
            "candidate_target_values",
        ],
        "question_generation": [
            "own_team_and_special_role",
            "claims_heard_so_far",
            "diagnostic_question_targets",
            "safe_claim_or_answer_policy",
            "information_leakage_risk",
            "candidate_question_values",
        ],
        "answer_generation": [
            "own_team_and_special_role",
            "question_asked",
            "safe_claim_or_answer_policy",
            "information_leakage_risk",
            "candidate_answer_values",
        ],
        "leader_hostage_trade": [
            "eligible_hostages_to_trade",
            "posterior_president_location",
            "posterior_bomber_location",
            "team_goal_same_or_separate",
            "trade_effect_on_final_co_location",
            "trade_information_leakage_risk",
            "candidate_trade_values",
        ],
    },
    "tic_tac_toe": {
        "mark_empty_square": [
            "board_state",
            "legal_empty_squares",
            "own_immediate_wins",
            "opponent_immediate_wins",
            "fork_threats",
            "candidate_action_values",
        ],
    },
}


def required_fields_for_prompt(game_id, active_context=None):
    game_key = canonical_game_id(game_id)
    context_name = None
    if active_context:
        context_name = active_context.get("active_action_space_program")
    return list(
        REQUIRED_FIELD_SETS_BY_GAME_CONTEXT.get(game_key, {}).get(context_name, [])
    )


def program_for_prompt(mapping, active_context=None):
    return list(_program_for_context(mapping, active_context))


def verifier_checks_for_prompt(mapping, active_context=None):
    return list(_verifier_for_context(mapping, active_context))


def format_theory_mapping_section(mapping, *, distilled: bool, active_context=None) -> str:
    role_or_phase_section = "" if active_context else _role_or_phase_lines(mapping)
    active_context_section = _active_context_lines(active_context)
    fallback_target_section = "" if active_context else _fallback_field_target_lines(mapping)
    reference_basis = _bullet_lines(mapping.get("reference_basis", GENERIC_THEORY_MAPPING["reference_basis"]))
    if distilled:
        parts = [
            "Prompt variant: high_distill",
            "You are executing a compiled field program built from game rules and game theory.",
            "The field register below is fixed by the experiment. Do not invent or redefine fields; compute their current values from the observation, then execute the decision program.",
            "Fields may summarize, score, or filter legal actions, but the final selected action must be produced only by the decision program and verifier.",
            "",
            "Game-theoretic frame",
            f"- Game: {mapping['display_name']}",
            f"- Model: {mapping['game_type']}",
            f"- Solution concept: {mapping['solution_concept']}",
            f"- Mapping: {mapping['osborne_rubinstein_mapping']}",
            "",
            "Reference basis",
            reference_basis,
            "",
            "Field register: base fields",
            _bullet_lines(mapping["required_state_fields"]),
        ]
        if fallback_target_section:
            parts.extend(
                [
                    "",
                    "Field computation targets",
                    fallback_target_section,
                ]
            )
        if active_context_section:
            parts.extend(
                [
                    "",
                    "Active role and action-space spec",
                    active_context_section,
                ]
            )
        if role_or_phase_section:
            parts.extend(
                [
                    "",
                    "Field register: role or phase-specific fields",
                    role_or_phase_section,
                ]
            )
        parts.extend(
            [
                "",
                "Compiled decision program",
                "- P0. Choose only from the current available action ids.",
                _bullet_lines(_program_for_context(mapping, active_context)),
                "- P*. Do not use unavailable fields as if they were computed.",
                "- P*. If tied, choose the legal action with the strongest verifier-passing best-response case.",
                "",
                "Verifier checks",
                _bullet_lines(_verifier_for_context(mapping, active_context)),
            ]
        )
        return "\n".join(parts)

    parts = [
        "Prompt variant: high_reasoning",
        "You are executing an engineered field reasoning prompt built from game rules and game theory.",
        "The field register below is fixed by the experiment. Do not invent or redefine fields; compute their current values from the observation, then reason over those fields to choose a legal action.",
        "Unlike high_distill, this variant does not give an executable decision program. The model must use the computed fields to compare candidate legal actions.",
        "",
        "Game-theoretic frame",
        f"- Game: {mapping['display_name']}",
        f"- Model: {mapping['game_type']}",
        f"- Solution concept: {mapping['solution_concept']}",
        f"- Mapping: {mapping['osborne_rubinstein_mapping']}",
        "",
        "Reference basis",
        reference_basis,
        "",
        "Field register: base fields",
        _bullet_lines(mapping["required_state_fields"]),
    ]
    if fallback_target_section:
        parts.extend(
            [
                "",
                "Field computation targets",
                fallback_target_section,
            ]
        )
    if active_context_section:
        parts.extend(
            [
                "",
                "Active role and action-space spec",
                active_context_section,
            ]
        )
    if role_or_phase_section:
        parts.extend(
            [
                "",
                "Field register: role or phase-specific fields",
                role_or_phase_section,
            ]
        )
    parts.extend(
        [
            "",
            "Reasoning workflow",
            _bullet_lines(_workflow_for_context(mapping, active_context)),
            "",
            "Verifier checks",
            _bullet_lines(_verifier_for_context(mapping, active_context)),
        ]
    )
    return "\n".join(parts)


def high_reasoning_output_schema():
    return {
        "state_summary": "brief current-state summary grounded in the observation",
        "field_application": {
            "reference_basis_used": ["reference labels from the precomputed field mapping"],
            "active_action_space_program_used": "copy the active action-space program name from the prompt",
            "active_role_spec_used": ["copy the active role-specific spec names from the prompt"],
            "context_detection_confidence": "copy low, medium, or high from the prompt",
            "active_field_set_used": "base fields plus active role/action-space field names",
            "computed_fields": {
                "every_base_and_active_role_or_action_space_field_name_verbatim": "value extracted from the current observation, or 'unobserved' if unavailable"
            },
            "unavailable_fields": ["field-register fields that cannot be filled from the current observation"],
            "candidate_action_values": [
                {
                    "action": "available action id",
                    "value_reason": "payoff or strategic reason",
                    "risk": "main rule or opponent risk",
                }
            ],
            "reasoned_selection": "why the selected legal action is strongest after comparing computed fields",
            "verifier_checks": ["checks confirming action legality and output format"],
        },
        "action_type": "predefined or openended",
        "selected_action": "copy exactly from the available action ids",
        "openended_response": "concrete string when action_type is openended, otherwise null",
        "confidence": "low, medium, or high",
    }


def high_distill_output_schema():
    return {
        "state_summary": "one-sentence current-state summary",
        "field_application": {
            "reference_basis_used": ["reference labels from the precomputed field mapping"],
            "active_action_space_program_used": "copy the active action-space program name from the prompt",
            "active_role_spec_used": ["copy the active role-specific spec names from the prompt"],
            "context_detection_confidence": "copy low, medium, or high from the prompt",
            "active_field_set_used": "base fields plus active role/action-space field names",
            "computed_fields": {
                "every_base_and_active_role_or_action_space_field_name_verbatim": "compact value from the current observation, or 'unobserved' if unavailable"
            },
            "unavailable_fields": ["field-register fields that are not visible in the current observation"],
            "decision_program_trace": [
                {
                    "step": "P0/P1/etc.",
                    "rule": "compiled program rule being executed",
                    "result": "actions kept, excluded, or selected",
                    "used_fields": ["field names used by this step"],
                }
            ],
            "used_rule": "final compiled program rule that selected the action",
            "verifier_checks": ["legal action and format checks"],
            "verifier_passed": True,
        },
        "action_type": "predefined or openended",
        "selected_action": "copy exactly from the available action ids",
        "openended_response": "concrete string when action_type is openended, otherwise null",
        "confidence": "low, medium, or high",
    }
