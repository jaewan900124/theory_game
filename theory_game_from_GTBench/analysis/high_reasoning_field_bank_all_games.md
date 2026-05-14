# High-Reasoning Field Bank Across GTBench Games

## Purpose

This file is a separate experiment artifact.

It is not meant to replace the current `field_schemas` or the current
`high_engineering` profile. The goal here is to collect a much wider bank of
`high_reasoning` candidate fields for each GTBench game, grounded in:

```text
game rules and objective x information structure x mapped game theory
```

The emphasis is not on directly outputting an answer. The emphasis is on
building richer intermediate derived fields that a stronger reasoning model can
use.

## Scope Boundary

This file should exclude fields that are already part of the base environment
input or are trivially read from the raw observation.

So this file is **not** the place for base fields such as:

- raw board state
- legal actions
- current player / turn owner
- direct private card or valuation text
- directly observed public history strings

Those are assumed to already enter the prompt or schema.

This file should contain only:

- rule-derived fields,
- action-indexed consequence fields,
- belief-update fields,
- continuation-value fields,
- theory-specific comparison fields.

## Design Rules

Use a field only if it is consistent with the following:

1. Rule-grounded: the field should come from the actual game rules, action
   semantics, payoff structure, or observed history.
2. Theory-motivated: the field should correspond to the mapped theory, such as
   backward induction, belief update, expected value, dominance, or bargaining.
3. Action-discriminative: the field should help compare legal actions.
4. Verifier-friendly: a later checker should be able to verify the field from
   state, legal actions, and allowed private information.
5. Non-prescriptive: do not store `best_action`, `optimal_move`,
   `recommended_bid`, or equivalent answer fields.
6. Honest under uncertainty: if a value cannot be derived from rules plus
   available information, mark it `unavailable` instead of guessing.

## Suggested Output Style

For implementation experiments, these fields work best when represented as one
of the following:

- scalar state summaries,
- action-indexed maps,
- belief distributions,
- candidate-set lists,
- categorical risk or continuation classes,
- explicit `unavailable` markers.

## Tic-Tac-Toe

Theory anchor:
`backward induction + threat-space reasoning + maxmin defense`

Rule x theory interaction:
Perfect information and deterministic transitions make short tactical lookahead
legitimate. The most useful fields are those that expose forced wins, forced
blocks, forks, and draw-preserving continuations.

### Proposed high_reasoning fields

- `line_status_by_line`: for each winning line, count self marks, opponent
  marks, and empty cells.
- `open_lines_by_player`: lines still completable by each player.
- `immediate_win_actions`: legal moves that complete a line immediately.
- `immediate_block_actions`: legal moves that stop the opponent's immediate win.
- `fork_creation_actions`: legal moves creating at least two next-turn winning
  threats.
- `fork_block_actions`: legal moves that prevent the opponent from creating a
  fork.
- `dual_threat_count_by_action`: number of future winning threats produced by
  each legal move.
- `opponent_immediate_reply_threats_by_action`: opponent immediate wins
  available after each candidate move.
- `forced_reply_count_by_action`: how many opponent replies are forced after
  each move.
- `center_control_status`: whether center is occupied and by whom.
- `corner_pair_potential_by_action`: whether a move creates or breaks strong
  corner-based fork structures.
- `line_completion_distance_by_action`: minimum remaining moves to complete a
  winning line after each candidate move.
- `draw_preserving_actions`: moves that avoid immediate tactical loss and keep
  a drawable continuation alive.
- `symmetry_class_by_action`: equivalence classes among legal actions under
  board symmetry, useful for compression.
- `continuation_pressure_by_action`: coarse class such as `forcing`,
  `neutral`, `defensive_only`, or `self_exposing`.

## Connect Four

Theory anchor:
`backward induction + threat-space reasoning + maxmin defense`

Rule x theory interaction:
Gravity changes action consequences, so legal reasoning must compute landing
rows first. Threat-space fields matter more than generic positional language.

### Proposed high_reasoning fields

- `playable_row_by_column`: landing row for a disc in each legal column.
- `immediate_win_columns`: legal columns that create four in a row now.
- `immediate_block_columns`: legal columns that stop an opponent immediate win.
- `threat_cells_by_player`: open cells that would complete a future four if
  made playable.
- `vertical_completion_windows_by_column`: vertical three-plus-empty patterns
  enabled by each column.
- `horizontal_completion_windows_by_column`: horizontal threat windows touched
  by each candidate column.
- `diagonal_completion_windows_by_column`: diagonal threat windows touched by
  each candidate column.
- `double_threat_columns`: columns that create two distinct winning threats for
  the next turn.
- `opponent_immediate_reply_wins_by_column`: opponent winning columns after
  each candidate move.
- `unsafe_columns`: legal columns that hand the opponent an immediate win or
  decisive forcing threat.
- `support_dependency_by_column`: whether a future threat depends on filling
  supporting cells underneath it.
- `odd_even_threat_parity_by_column`: parity-relevant threat timing by landing
  row and move order.
- `center_distance_by_column`: distance from the center column, used only after
  tactical filters.
- `future_playability_shift_by_column`: which currently unavailable cells
  become playable after a move.
- `forcing_status_by_column`: whether the move is `winning_now`,
  `must_block`, `threatening`, `safe_positional`, or `unsafe`.

## Breakthrough

Theory anchor:
`backward induction + race-to-promotion analysis + capture threat analysis`

Rule x theory interaction:
Every move changes both promotion race and tactical vulnerability. Good fields
must expose whether a move accelerates promotion, stops the opponent race, or
walks into immediate tactical punishment.

### Proposed high_reasoning fields

- `immediate_promotion_actions`: legal actions that reach the goal row now.
- `opponent_immediate_promotion_threats`: opponent actions that promote next
  turn if not stopped.
- `capture_actions`: legal diagonal captures and captured target coordinates.
- `destination_defense_status_by_action`: whether the landing square is
  defended by friendly pieces.
- `recapture_risk_by_action`: whether the moved piece can be captured
  immediately after the move.
- `promotion_distance_by_piece`: remaining forward steps to promote for each
  relevant piece.
- `fastest_promotion_lane_by_piece`: least-obstructed lane toward promotion for
  each advanced piece.
- `lane_blocker_count_by_piece`: number of opposing blockers in a piece's most
  direct race lane.
- `material_swing_by_action`: immediate material gain or loss caused by a move.
- `passed_pawn_flag_by_action`: whether the moved piece becomes effectively
  unblocked on its lane after the action.
- `back_rank_guard_status`: whether the current move weakens the defense
  against enemy breakthroughs.
- `race_leader_after_action`: which side has the fastest promotion route after
  the move.
- `opponent_counterpromotion_risk_by_action`: whether a candidate move fails to
  address a stronger opponent race threat.
- `continuation_race_pressure_by_action`: coarse continuation class such as
  `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

## Nim

Theory anchor:
`backward induction + combinatorial state evaluation under misere objective`

Rule x theory interaction:
This environment is misere Nim, so the normal-play nim-sum shortcut must be
combined with endgame parity logic. Good fields should expose successor states
rather than directly encode the final move.

### Proposed high_reasoning fields

- `legal_move_effects`: successor pile state for every legal move.
- `total_matches_after_action`: total remaining matches after each move.
- `nonzero_pile_count_by_action`: number of nonempty piles in each successor.
- `large_pile_count_by_action`: number of piles with size greater than one in
  each successor.
- `singleton_count_by_action`: number of size-one piles in each successor.
- `phase_classification_by_action`: `normal_phase` versus `misere_endgame`
  after each action.
- `nim_sum_by_action`: xor value of the successor state when normal-phase logic
  is relevant.
- `zero_nim_sum_flag_by_action`: whether the successor nim-sum is zero.
- `all_singletons_flag_by_action`: whether the successor state contains only
  singleton piles.
- `terminal_take_last_flag_by_action`: whether the move removes the final
  remaining match.
- `endgame_parity_target_by_action`: whether the successor singleton parity is
  favorable under misere endgame logic.
- `opponent_position_value_by_action`: whether the opponent receives a winning,
  losing, or unclear continuation state.
- `forced_loss_indicator`: whether every legal move passes a winning state to
  the opponent.
- `action_equivalence_classes_by_successor_state`: actions that differ
  syntactically but induce the same successor state class.

## Pig

Theory anchor:
`stochastic stopping + expected value + race-adjusted risk management`

Rule x theory interaction:
The choice is between a certain banked score and a risky continuation with a
chance-node bust. Useful fields compare stop value, roll value, and race
pressure without hard-coding a policy table.

### Proposed high_reasoning fields

- `score_after_stop`: score obtained by banking the current turn total.
- `stop_wins_now`: whether stopping reaches or exceeds target immediately.
- `stop_leaves_opponent_near_finish`: whether stopping hands the turn to an
  opponent who is already close to winning.
- `bust_probability`: probability of losing the current turn total on the next
  roll.
- `bust_loss`: number of temporary points lost if a bust occurs now.
- `safe_roll_outcome_distribution`: non-bust roll outcomes and resulting new
  turn totals.
- `expected_safe_gain`: expected point gain conditional on not busting.
- `one_roll_expected_value`: one-step expected value proxy for choosing `roll`.
- `score_gap`: `self_score - opponent_score`.
- `self_distance_to_target`: points needed for self to finish.
- `opponent_distance_to_target`: points needed for opponent to finish.
- `race_pressure_class`: coarse state such as `ahead_safe`, `behind_chasing`,
  `must_finish_soon`, or `opponent_threatening`.
- `bank_value_ratio`: current bankable value relative to the remaining distance
  to target.
- `desperation_level`: how much extra variance is justified by the score race.
- `roll_vs_stop_margin`: compact comparison between certain stop value and
  risk-adjusted roll value.

## First-Sealed Auction

Theory anchor:
`private-value first-price auction + bid shading + expected surplus`

Rule x theory interaction:
Each player knows only its own value and chooses a sealed bid. The key
theory-grounded tradeoff is higher win probability versus lower surplus if the
bid wins.

### Proposed high_reasoning fields

- `bid_rank_order`: legal bids sorted from least to most aggressive.
- `bid_shading_amount`: `valuation - bid` for each legal bid.
- `bid_shading_ratio`: `(valuation - bid) / valuation` where defined.
- `overbid_actions`: legal bids above private value.
- `zero_surplus_actions`: bids equal to private value.
- `positive_surplus_actions`: bids below private value.
- `surplus_if_win_by_bid`: payoff if each bid wins.
- `win_probability_assumption_by_bid`: explicit assumed winning chance for each
  candidate bid under the current belief model.
- `expected_surplus_by_bid`: win-probability-weighted surplus for each bid.
- `tie_case_if_bid_equals_opponent`: tie-handling assumption if the rules or
  implementation specify one.
- `profit_floor_by_bid`: worst-case profit implication if the bid wins.
- `regret_if_lose_with_low_bid`: missed-value pressure from shading too much.
- `regret_if_win_with_high_bid`: profit erosion from shading too little.
- `robust_bid_interval_under_belief_range`: bids that remain reasonable across
  a range of opponent bid beliefs.
- `aggressiveness_class_by_bid`: coarse label such as `too_passive`,
  `moderate_shade`, `near_value`, or `overbid`.

## Kuhn Poker

Theory anchor:
`information-set reasoning + belief update + mixed bluff/value incentives`

Rule x theory interaction:
Private card plus public betting history define the information set. Good
fields should expose card-conditioned incentives, belief-conditioned expected
value, and whether the action is a call, fold, check, or bluff opportunity.

### Proposed high_reasoning fields

- `information_set_class`: coarse label for the current node such as
  `opening_action`, `facing_bet`, or `post-check response`.
- `hand_strength_class`: weak, medium, or strong relative to the deck.
- `pot_size`: current pot before acting.
- `facing_bet`: whether my current choice responds to an opponent bet.
- `legal_action_context`: semantic mapping of available actions in this node.
- `possible_opponent_cards`: opponent cards consistent with my private card.
- `posterior_over_opponent_cards`: belief over those cards from public history.
- `showdown_result_by_opponent_card`: win/loss outcome if the hand reaches
  showdown against each possible opponent card.
- `fold_value`: guaranteed value of folding when that action is legal.
- `call_value_by_opponent_card`: card-conditioned payoff if I call.
- `bet_fold_equity`: value gained when a bet induces folds.
- `bluff_incentive`: whether weak-card betting can profit from fold equity.
- `value_bet_incentive`: whether strong-card betting extracts value from worse
  hands or calls.
- `expected_value_by_action`: belief-weighted expected value for each legal
  action.
- `opponent_response_if_i_bet`: likely reply classes after each betting action.
- `action_risk_profile`: coarse class such as `thin_value`, `clear_bluff`,
  `safe_check`, `defensive_fold`, or `high_variance_call`.

## Liar's Dice

Theory anchor:
`Bayesian belief update + bluff detection + uncertainty-aware raise/challenge`

Rule x theory interaction:
The current public bid constrains legal raises, while private dice evidence
changes the credibility of both the current bid and higher raises. Good fields
must quantify uncertainty without pretending hidden dice are known.

### Proposed high_reasoning fields

- `minimum_next_bid_rule`: exact legality rule for the next non-challenge raise.
- `legal_raise_space`: all legal raises from the current state.
- `my_face_count`: how many of the bid face I personally hold.
- `my_bid_support_count`: how many of the current bid are directly supported by
  my private dice.
- `unknown_dice_count`: number of dice whose faces I do not observe.
- `probability_current_bid_true`: belief that the current bid is true given my
  dice and public history.
- `probability_each_raise_true`: truth probability estimate for each legal raise.
- `slack_above_current_bid`: how far the current bid is above my private
  evidence before relying on unknown dice.
- `challenge_threshold_gap`: amount by which the current bid exceeds a chosen
  plausibility threshold.
- `bluff_pressure_index`: how strongly the current state pressures someone to
  bluff rather than continue honestly.
- `conservative_raise_candidates`: raises with relatively high truth support.
- `aggressive_raise_candidates`: legally available raises that rely on stronger
  bluff assumptions.
- `opponent_bluff_likelihood_from_history`: history-based belief about whether
  the opponent tends to overstate bids.
- `liar_vs_raise_ev_proxy`: compact comparison between challenging now and
  continuing the bidding sequence.
- `consistency_with_private_evidence`: whether a candidate action is aligned
  with, stretches, or contradicts my own dice evidence.

## Negotiation

Theory anchor:
`private-value bargaining + strategic communication + agreement tradeoff`

Rule x theory interaction:
The game mixes concrete proposals and cheap-talk-like utterances. Useful fields
must separate self payoff, feasibility, inferred opponent demands, and the
cost of delaying agreement.

### Proposed high_reasoning fields

- `self_payoff_of_latest_offer`: my utility if I accept the current offer.
- `disagreement_payoff`: utility of ending without agreement if that is defined,
  otherwise the default zero-like baseline.
- `minimum_acceptable_payoff`: threshold below which agreement is not worth
  taking given current information.
- `max_self_payoff_feasible_offer`: best self-side feasible offer in the legal
  proposal space.
- `concession_cost_by_candidate_offer`: how much self utility each candidate
  concession gives up.
- `high_value_item_priority`: ranking of items by my private value density.
- `bundle_substitutability_from_self_view`: which items are near-substitutes or
  complements from my utility perspective.
- `offer_feasibility_check`: whether a candidate allocation respects item-pool
  constraints.
- `acceptance_probability_proxy_by_offer`: belief-based estimate that the
  opponent may accept a candidate offer.
- `opponent_demand_pattern_from_history`: revealed preference clues from past
  offers and utterances.
- `utterance_offer_consistency`: whether a message and a concrete proposal tell
  the same strategic story.
- `pareto_candidate_status_from_self_side`: whether a proposal looks efficient
  from my utility side without assuming exact opponent values.
- `strategic_stage_goal`: coarse goal such as `close_now`, `probe_preferences`,
  `signal toughness`, or `trade for agreement`.
- `agree_vs_counteroffer_margin`: compact comparison between accepting now and
  holding out for a better but less certain outcome.

## Iterated Prisoner's Dilemma

Theory anchor:
`repeated-game incentives + trigger-style punishment + reciprocity detection`

Rule x theory interaction:
A single round favors defection, but repeated interaction changes incentives if
cooperation is credible. Good fields should summarize the observed history and
separate short-run temptation from long-run cooperation value.

### Proposed high_reasoning fields

- `opponent_recent_actions`: short recent suffix of opponent behavior.
- `opponent_cooperation_rate`: fraction of opponent cooperative moves.
- `opponent_defection_rate`: fraction of opponent defection moves.
- `opponent_streak_type`: current streak such as repeated cooperation or
  repeated defection.
- `reciprocity_pattern_flag`: whether the opponent appears to mirror my last
  action or respond conditionally.
- `forgiveness_pattern_flag`: whether the opponent returns to cooperation after
  punishment phases.
- `trigger_strategy_state`: coarse repeated-game state such as `cooperate`,
  `punish`, `test_repair`, or `exploit-resistant`.
- `last_round_outcome`: previous round action profile and payoff implication.
- `stage_game_payoff_table`: the one-shot payoff ordering relevant this round.
- `one_step_best_response`: immediate one-round best response to the opponent's
  likely current action.
- `future_cooperation_value_proxy`: rough long-run value of keeping mutual
  cooperation alive.
- `punishment_credibility`: whether current history makes retaliation threats
  believable.
- `exploitation_risk_if_silent`: risk of being repeatedly exploited by
  cooperating now.
- `repair_opportunity_flag`: whether one side defected recently but the history
  still supports restoring cooperation.
- `current_action_long_run_tradeoff`: compact summary of short-run gain versus
  long-run relationship value.

## Using This File

This file is intentionally broader than the current production schema.

A practical next step is:

1. choose one game,
2. select a subset of fields that remain computable from the available state,
3. mark uncertain fields as `unavailable`,
4. convert the chosen set into either:
   - a reasoning-only prompt field bundle, or
   - a distillation schema for structured supervision.

The key principle is:

```text
more fields is not the goal by itself
better rule-theory interaction fields is the goal
```
