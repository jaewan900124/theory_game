# GameBench Prompt Mapping Examples

These are compact examples of field-register mappings used for GameBench style
prompts. Use them as naming and structure references when adding another game.

## Generic Fallback

Theory frame:

- Game with legal actions, payoff-relevant state, and strategic opponents.
- Best response under the current information set.

Base fields:

- `players_and_roles`
- `legal_action_set`
- `information_state_public_private`
- `objective_or_payoff`
- `payoff_relevant_state_variables`
- `beliefs_about_opponents_or_teammates`
- `candidate_action_values`
- `risk_or_constraint_checks`
- `legal_output_format`

Distill rules:

- P1. Keep only legal actions from the provided action ids.
- P2. Compare actions by immediate objective impact, future strategic value, and
  rule constraints.
- P3. Return the legal action with the strongest best-response case.

## Perfect-Information Board Game

Example games:

- Tic-Tac-Toe
- Connect Four
- Breakthrough
- Santorini

Theory frame:

- Finite extensive game with perfect information.
- Backward induction, maxmin, and terminal threat checks.

Useful fields:

- `board_state`
- `legal_empty_squares` or `legal_moves`
- `own_immediate_wins`
- `opponent_immediate_wins`
- `fork_threats`
- `candidate_action_values`
- `legal_output_format`

Distill pattern:

- P1. Win immediately if possible.
- P2. Else block an immediate loss.
- P3. Else create or block forced threats.
- P4. Else choose the strongest legal positional move.

Verifier:

- selected action is legal and listed
- terminal win/block checks were performed
- move does not violate board constraints

## Hidden-Information Sequential Game

Example games:

- Kuhn Poker
- Liar's Dice
- Air, Land, and Sea

Theory frame:

- Extensive game with imperfect information.
- Belief update, sequential rationality, mixed/bluff incentives.

Useful fields:

- `own_private_information`
- `public_history`
- `legal_action_set`
- `posterior_beliefs_about_hidden_state`
- `opponent_range_or_type_beliefs`
- `candidate_action_values`
- `bluff_or_reveal_risk`
- `legal_output_format`

Distill pattern:

- P1. Keep legal actions for the current information set.
- P2. Update beliefs from private information and public history.
- P3. Remove actions that are dominated under the current belief.
- P4. Choose the legal action with the best value after bluff/call/risk checks.

Verifier:

- private information is used only as observed by the agent
- hidden state is treated as belief, not fact
- action is legal for current phase

## Priority GameBench Role And Action-Space Specs

These are the preferred design targets for the current GameBench prompt work.
They are not generic templates; they are game-specific specs that combine game
rules, observed action shapes, role structure, and game-theoretic framing.

Current active-context coverage:

| Game | Active action-space contexts | Main field target shape |
| --- | --- | --- |
| `air_land_sea` | `normal_deploy_improvise_withdraw`, `tactical_effect_resolution` | theater control, withdrawal value, tactical target swing, reveal/cover risk |
| `arctic_scavengers` | `resource_gathering`, `interrupt_response`, `skirmish_action`, `dig_card_selection` | resource feasibility, deck value, skirmish swing, discard/opportunity cost |
| `are_you_the_traitor` | `target_selection`, `question_generation`, `answer_generation`, `stop_or_continue_accusation`, `accused_selection` | private role objective, role beliefs, diagnostic speech value, accusation risk |
| `codenames` | `submit_clue`, `guess_or_end_turn` | safe clue clusters, clue ambiguity, semantic guess fit, assassin/opponent risk |
| `hive` | `piece_type_selection`, `placement_hex_choice`, `movement_hex_choice` | queen timing, legal hex constraints, queen pressure, mobility/trap risk |
| `pit` | `offer_trade`, `accept_trade` | target commodity set, trade opportunity cost, Bull/Bear exposure, signal leakage |
| `santorini` | `placement_phase`, `move_build_phase` | placement mobility, immediate win/block, height access, containment risk |
| `sea_battle` | `simultaneous_move_and_shoot` | post-move heading, collision risk, shot lanes, team spacing, survival margin |
| `two_rooms_and_a_boom` | `target_selection`, `question_generation`, `answer_generation`, `leader_hostage_trade` | role-location beliefs, leakage risk, safe signaling, final co-location impact |
| `tic_tac_toe` | `mark_empty_square` | immediate win/block, fork threats, minimax square value |

### Air, Land, and Sea

Theory frame:

- Two-player finite-horizon card battle with imperfect information.
- Theaters create local majority contests.
- Cards are scarce commitments with future option value.
- Withdrawal is an outside option whose payoff depends on remaining hand size.
- Tactical cards can temporarily change the action space into an effect
  resolution problem.

Role-specific specs:

- `main_turn_deploy_improvise_withdraw`
  - Active when actions include normal card play and withdrawal.
  - Targets: compute theater status, card-action control swing, withdrawal value,
    and face-up versus face-down commitment risk.
  - Fields: `hand_cards_and_remaining_cards`, `theater_control_state`,
    `withdrawal_value_now`, `faceup_deploy_control_swing`,
    `facedown_improvise_information_value`,
    `action_risk_by_commitment_and_information`,
    `candidate_card_or_withdraw_values`.
- `tactical_followup_effect_resolution`
  - Active when actions include effect targets such as Flip, Move, Return,
    adjacent-theater choice, extra play, or do nothing.
  - Targets: compute the triggering effect, legal targets, each target's control
    swing, target risk, and do-nothing value.
  - Fields: `triggering_tactical_card`, `legal_effect_targets`,
    `control_swing_after_effect`, `reveal_or_cover_information_cost`,
    `effect_target_risk_by_option`, `do_nothing_or_skip_value_if_available`,
    `candidate_effect_target_values`.

Action-space-specific programs:

```text
normal_deploy_improvise_withdraw
P0. Keep only listed action ids.
P1. Compute withdrawal value from remaining hand and current battle outlook.
P2. Compare face-up deploy, face-down improvise, and withdrawal.
P3. Prefer actions that flip or secure theater control without wasting decisive future cards.
P4. Select the best verifier-passing action.

tactical_effect_resolution
P0. Keep only listed effect-resolution action ids.
P1. Identify the triggering effect and legal targets.
P2. Estimate theater-control swing for each target.
P3. Subtract reveal, cover, movement, or return risk.
P4. Choose the best effect target, or do nothing when all targets are negative.
```

Verifier:

- selected action id is listed
- deploy/improvise/withdraw constraints match the current action space
- tactical effect target is legal for the triggering card
- hidden cards are treated as beliefs unless revealed

### Two Rooms and a Boom

Theory frame:

- Team hidden-role social deduction game.
- Private cards define types and objectives.
- Conversation is signaling or cheap talk.
- Leaders control hostage trades that change final President-Bomber
  co-location probability.

Role-specific specs:

- `target_selection`
  - Active when choosing another player to talk to.
  - Targets: compute private objective, target information gain, and leakage
    risk for each legal target.
  - Fields: `roommates_available`, `own_team_and_special_role`,
    `information_gain_by_target`, `risk_of_revealing_private_role`,
    `team_objective_alignment`, `candidate_target_values`.
- `question_generation`
  - Active when producing an open-ended question.
  - Targets: compute the role-location belief gap, diagnostic questions, and
    special-role leakage risk.
  - Fields: `diagnostic_question_target`, `belief_gap_to_resolve`,
    `safe_question_wording`, `information_leakage_risk`,
    `candidate_question_values`.
- `answer_generation`
  - Active when answering another player.
  - Targets: compute what was asked, safe/unsafe private facts, and truth,
    partial-disclosure, silence, or misdirection value.
  - Fields: `own_private_role`, `question_asked`, `truthful_answer_value`,
    `deceptive_or_partial_answer_value`, `leakage_risk`,
    `candidate_answer_values`.
- `leader_hostage_trade`
  - Active when a leader chooses a hostage/trade.
  - Targets: compute posterior President/Bomber locations, trade effect on final
    co-location, and leakage/opponent-helping risk.
  - Fields: `eligible_hostages_to_trade`, `posterior_president_location`,
    `posterior_bomber_location`, `team_goal_same_or_separate`,
    `trade_effect_on_final_co_location`, `candidate_trade_values`.
- `special_role_policy`
  - Used when the agent is President, Bomber, or has a role whose identity
    strongly changes signaling risk.
  - Fields: `special_role_revelation_risk`, `safe_signal_to_team`,
    `misdirection_value_against_opponents`.

Action-space-specific programs:

```text
choose_discussion_target
P0. Keep only listed target-player ids.
P1. Prefer targets with high information gain for locating President/Bomber or team.
P2. Penalize targets likely to expose own special role to opponents.
P3. Select the target that best improves team-objective beliefs.

ask_or_answer
P0. Produce the required open-ended text.
P1. Separate private role facts from public claims.
P2. Ask or answer to improve team beliefs while limiting leakage.
P3. Use deception or partial disclosure only when it advances the team objective.

leader_trade
P0. Keep only legal hostage/trade actions.
P1. Estimate current President and Bomber room beliefs.
P2. Choose the trade that moves final co-location toward the team objective.
P3. Avoid trades that reveal or expose a critical special role without benefit.
```

Verifier:

- open-ended response is concrete and phase-appropriate
- action supports Red same-room or Blue separate-room objective
- private role leakage is explicitly considered
- leader trades use eligible players only

### Santorini

Theory frame:

- Two-player deterministic perfect-information spatial game.
- Move-build actions create immediate win threats and mobility constraints.
- Practical solution concept is bounded backward-induction-style tactical search:
  win, block, preserve mobility, and restrict opponent mobility.

Role-specific specs:

- `placement_phase`
  - Active when action ids are board coordinates and instructions mention
    initial pawn placement.
  - Fields: `own_unplaced_pawn`, `empty_board_squares`,
    `centrality_and_future_mobility_value`, `pair_spacing_between_own_pawns`,
    `opponent_placement_pressure`, `candidate_placement_values`.
- `move_build_phase`
  - Active when action ids encode move-build pairs.
  - Fields: `active_pawn`, `legal_move_squares`,
    `legal_build_squares_after_move`, `immediate_win_moves`,
    `opponent_immediate_win_threats`, `mobility_after_action`,
    `height_access_to_level_three`, `candidate_move_build_values`.

Action-space-specific programs:

```text
placement
P0. Keep only listed coordinate action ids.
P1. Prefer placements with high centrality and future mobility.
P2. Maintain useful spacing between own pawns.
P3. Avoid placements that give the opponent easy containment.

move_build
P0. Keep only listed move-build action ids.
P1. Take an immediate winning move to level 3 if listed.
P2. Else block opponent immediate level-3 threats.
P3. Else choose move-build pairs that improve own height access and reduce opponent mobility.
P4. Verify both move and build are legal in the selected action id.
```

Verifier:

- placement coordinate or move-build action id is listed
- immediate win and immediate block were checked
- move/build constraints are respected
- mobility after the action is considered

### Codenames

Theory frame:

- Cooperative asymmetric-information signaling game.
- Spymaster has private word-color information and sends a constrained signal.
- Operative has public board/history and interprets the signal under risk.
- Assassin, opponent, and neutral words create terminal or tempo risks.

Role-specific specs:

- `spymaster_signal_design`
  - Active when the legal action is `submit_clue`.
  - Targets: compute safe target clusters, clue candidates, operative
    interpretation, forbidden-word ambiguity, and clue-number risk.
  - Fields: `team_color`, `own_team_unrevealed_words_with_private_types`,
    `opponent_neutral_and_assassin_words_to_avoid`,
    `safe_target_cluster_for_this_clue`, `candidate_one_word_clues`,
    `expected_operative_interpretation_for_each_clue`,
    `clue_ambiguity_or_forbidden_word_risk`,
    `clue_number_risk_budget_by_candidate`,
    `openended_format_word_comma_number`.
- `operative_signal_interpretation`
  - Active when actions include `guess_*` or `end_turn`.
  - Targets: compute clue budget, semantic fit, public-history evidence, hidden
    color risk, and guess value versus ending turn.
  - Fields: `team_color`, `current_clue_and_guess_limit`,
    `unrevealed_candidate_words`, `semantic_match_to_current_clue`,
    `public_history_from_last_hint_and_guesses`, `unknown_assassin_risk`,
    `unknown_opponent_or_neutral_risk`, `guess_vs_end_turn_value`,
    `candidate_guess_or_end_turn_values`.

Action-space-specific programs:

```text
submit_clue
P0. Select `submit_clue` only and produce `word,number`.
P1. Build safe target clusters from own unrevealed team words.
P2. Reject clues with high overlap to opponent, neutral, or assassin words.
P3. Prefer the clue with the best safe expected operative interpretation.
P4. Choose a conservative number when ambiguity is high.

guess_or_end_turn
P0. Keep only listed `guess_*` and `end_turn` actions.
P1. Rank unrevealed words by semantic match to the current clue and public history.
P2. Penalize likely assassin, opponent, and neutral candidates.
P3. Guess when best candidate value exceeds end-turn value; otherwise end turn.
P4. Do not exceed the clue-number risk budget unless the rules and board state justify it.
```

Verifier:

- clue response is exactly one word plus a number
- guessed word action id is listed
- clue/guess is grounded in visible board words and current history
- assassin and opponent-card risks are considered

## Auction

Example games:

- First-price sealed auction
- Second-price auction variants

Theory frame:

- Bayesian game with private values.
- Bid shading for first-price auctions; dominant truthful bidding for
  second-price auctions when rules match the standard private-value setting.

Useful fields:

- `own_private_value`
- `bid_space_or_legal_actions`
- `opponent_value_distribution_or_belief`
- `win_probability_by_bid`
- `surplus_if_win`
- `expected_value_by_bid`
- `budget_or_rule_constraints`

Distill pattern:

- P1. Keep feasible bids.
- P2. Reject bids above value unless rules justify it.
- P3. Compare expected surplus, not just win probability.
- P4. Choose the bid with strongest verifier-passing expected value.

Verifier:

- bid is legal and feasible
- private value is not confused with opponent value
- expected surplus is checked

## Negotiation And Bargaining

Example games:

- Negotiation
- two-party bargaining with private preferences

Theory frame:

- Bargaining game with private preferences and strategic communication.
- Alternating-offer logic, acceptance thresholds, outside options, and signaling.

Useful fields:

- `own_private_preferences`
- `public_offer_history`
- `opponent_preference_beliefs`
- `own_acceptance_threshold`
- `opponent_likely_acceptance`
- `proposal_value_to_self`
- `proposal_acceptance_risk`
- `message_signal_value`

Distill pattern:

- P1. Keep legal proposal or utterance formats.
- P2. Reject offers below own threshold unless strategically justified.
- P3. Prefer offers with high own value and plausible opponent acceptance.
- P4. Use messages to elicit information or support the offer without leaking
  unnecessary private preferences.

Verifier:

- offer/message format is valid
- private preferences are considered
- acceptance risk is checked

## Social Deduction And Team Communication

Example games:

- Are You the Traitor?
- Two Rooms and a Boom
- Codenames

Theory frame:

- Bayesian game with private roles or private information.
- Signaling, cheap talk, team objectives, and belief updates.

Useful fields:

- `own_team_role_and_target`
- `known_private_information`
- `public_claims_and_conversation`
- `posterior_beliefs_about_roles`
- `team_objective`
- `information_to_elicit_or_hide`
- `candidate_speech_or_action_values`
- `deception_or_revelation_risk`

Distill pattern:

- P1. Identify own role/team objective.
- P2. Update beliefs from public claims and private information.
- P3. Select a legal communication/action that advances team objective.
- P4. Avoid leaking private information unless the benefit outweighs risk.

Verifier:

- speech/action is legal for the current phase
- private information leakage is checked
- action supports the team objective

## Simultaneous Spatial Tactics

Example games:

- Sea Battle
- collision or movement/shooting team games

Theory frame:

- Simultaneous-move Markov game with team coordination.
- Best response under uncertain joint movement.

Useful fields:

- `own_position_heading_damage`
- `teammate_positions`
- `opponent_positions`
- `rocks_and_collision_hazards`
- `candidate_movement_paths`
- `candidate_shot_lanes`
- `expected_damage_given_and_received`
- `team_coordination_value`
- `candidate_action_values`

Distill pattern:

- P1. Avoid self-damaging movement into rocks or collisions.
- P2. Among safe actions, prefer likely shots on opponents.
- P3. Break ties by preserving team spacing and reducing exposure.

Verifier:

- selected action is listed
- collision and rock risks are checked
- attack direction is evaluated after movement/heading changes
