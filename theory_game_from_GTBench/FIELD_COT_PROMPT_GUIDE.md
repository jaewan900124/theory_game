# Field-Based CoT Prompt Guide

This note describes how to write field-based chain-of-thought prompts for game agents.
The goal is to make the model work through the theory-relevant fields without producing an overly long answer that fails to reach the final action.

## Reusable Prompt Generation Method

Use this method whenever adding a new game-theoretic decision prompt.

Input:

```text
1. Game rules
2. Mapped game-theoretic theories
3. Current game state
4. Legal actions
```

Pipeline:

```text
game rules + mapped theories
-> generate theory-required decision fields
-> group related fields into compact bundles
-> ask the model to fill each bundle through compact candidate rows
-> choose one final legal action
-> end with a parseable Action line
```

Do not use one fixed field list for every game. Generate fields from the game type, information structure, action space, payoff structure, and mapped theories.

## Field Generation By Game Type

Use these as starting rules, then specialize them to the actual game.

```text
Complete-information deterministic games:
- current_state
- legal_actions
- candidate_action
- next_state
- phase_or_terminal_condition
- theory_key_value
- opponent_position_value
- selected_action

Imperfect-information games:
- private_information
- public_history
- hidden_information_set
- belief_update
- candidate_action
- expected_payoff
- opponent_likely_response
- selected_action

Auction games:
- private_valuation
- bid_space
- candidate_bid
- winning_probability
- surplus_if_win
- payment_or_price_risk
- expected_utility
- selected_bid

Sequential games:
- current_node
- legal_actions
- candidate_action
- continuation_state
- continuation_value
- subgame_value
- backward_induction_value
- selected_action

Repeated games:
- current_round_state
- past_history
- opponent_pattern
- cooperation_or_retaliation_incentive
- short_term_payoff
- future_value
- selected_action
```

## Bundle Construction

Bundles are an output-compression strategy. They do not remove the underlying fields.

The verifier should be able to recover or recompute each individual field from the bundle output. Each bundle should combine fields that are naturally analyzed together and avoid duplicated reasoning.

Recommended generic bundles:

```text
observe_bundle:
current state, legal actions, objective, important rule constraints

transition_or_belief_bundle:
candidate action and resulting next state, or belief update if hidden information exists

value_bundle:
phase classification, payoff value, expected utility, equilibrium-relevant value, or theory-specific key value

opponent_response_bundle:
opponent position value, likely response, best response, or backward-induction value

decision_bundle:
selected action and short theory-grounded reason
```

When the game has many legal actions, do not ask the model to write one section per field. Ask for one compact candidate row per important legal action.

## Reusable Final Prompt Template

Use this template after generating game-specific fields and bundles.

```text
You are making a game-theoretic decision.

## Game Rules
{game_rules_summary}

## Current State
{current_game_state}

## Legal Actions
{legal_actions}

## Mapped Game-Theoretic Theories
{mapped_theories}

Use the mapped theories only to guide the decision fields. Do not over-explain the theories.

## Field Bundle Workflow
Analyze the decision using compact field bundles.

The individual decision fields exist internally for verification, but do not write long separate sections for each field. Instead, fill related fields together through compact candidate rows.

Use these game-specific bundles:

{field_bundles}

Bundle mapping:
- observe_bundle fills the observation and rule-constraint fields.
- transition_or_belief_bundle fills candidate consequence or belief-update fields.
- value_bundle fills payoff, expected utility, phase value, or theory-key-value fields.
- opponent_response_bundle fills opponent value, likely response, best response, or continuation-value fields.
- decision_bundle fills selected_action and the final theory-grounded reason.

## Candidate Row Format
For each important legal action, write one compact row.

{candidate_row_format}

Rules:
- Each row must fill multiple fields at once.
- Do not repeat the same reasoning under separate field headings.
- Do not evaluate illegal actions.
- Prefer the action whose bundle values best satisfy the game objective.
- The final decision must be grounded in the mapped theories and the computed bundle values.

## Strict Output Format
Think briefly using compact candidate rows, then end with exactly one parseable action line.

Action:
{one legal action}
```

## Game-Specific Prompt Design Checklist

For each new game, write these six parts before implementing the prompt:

```text
1. Short game rule section
2. Short mapped theory section
3. Theory-required individual fields
4. Field bundles that compress those fields
5. Candidate row format
6. Strict final action format
```

Check the design with these questions:

```text
- Are the fields generated from this game's actual structure, not copied from another game?
- Can each bundle row be decomposed back into the individual fields?
- Is the final value field clear?
- Does the prompt avoid repeated candidate analysis across multiple sections?
- Does the final answer end with Action: and exactly one legal action?
```

## Game-Specific Field Bundles

This section gives reusable bundle designs for the current `gamingbench` games.
Use these as the default field-bundle source when creating a new field-based prompt.

### Tic-Tac-Toe

Theory:

```text
backward-induction-style lookahead; subgame-perfect reasoning; maxmin defense
```

Individual fields:

```text
board, self_mark, opponent_mark, legal_actions, candidate_action, next_board,
line_check, immediate_win, immediate_block, fork_creation, fork_prevention,
opponent_best_reply, continuation_value, selected_action
```

Bundles:

```text
observe_bundle = board + self_mark + opponent_mark + legal_actions + win condition
transition_bundle = candidate_action + next_board
tactical_value_bundle = line_check + immediate_win + immediate_block + fork_creation + fork_prevention
opponent_response_bundle = opponent_best_reply + continuation_value
decision_bundle = selected_action + tactical_or_continuation_reason
```

Candidate row format:

```text
{action} -> next_board=...; line_check=win_line/block_line/none; line=...; tactic=win/block/fork/safe/weak; opponent_reply=...; continuation_value=...
```

Final value:

```text
Prefer immediate win, then forced block, then fork or best continuation value.

Verification:

```text
Only mark tactic=win if line_check names a completed three-in-a-row for self.
Only mark tactic=block if line_check names an opponent two-in-a-row whose missing cell is this action.
If line_check=none, do not call the action win or block.
```
```

### Connect4

Theory:

```text
backward-induction-style lookahead; threat-space reasoning; maxmin defense
```

Individual fields:

```text
board, column_heights, self_disc, opponent_disc, legal_columns, candidate_column,
drop_position, next_board, immediate_win, immediate_block, created_threats,
line_check, allowed_opponent_win, center_control, continuation_value, selected_action
```

Bundles:

```text
observe_bundle = board + column_heights + self_disc + opponent_disc + legal_columns
transition_bundle = candidate_column + drop_position + next_board
threat_value_bundle = line_check + immediate_win + immediate_block + created_threats + center_control
opponent_response_bundle = allowed_opponent_win + opponent_best_reply + continuation_value
decision_bundle = selected_column + threat_or_defense_reason
```

Candidate row format:

```text
{column_action} -> drop=...; line_check=win_line/block_line/threat_line/none; line=...; immediate=win/block/none; threats=...; opponent_risk=...; continuation_value=...
```

Final value:

```text
Prefer immediate win, then block opponent immediate win, then highest safe threat-space value.

Verification:

```text
Only mark immediate=win if line_check names a completed four-in-a-row for self.
Only mark immediate=block if line_check names an opponent immediate four-in-a-row threat blocked by this action.
opponent_risk must note if this move allows an opponent immediate win.
```
```

### Breakthrough

Theory:

```text
backward-induction-style race analysis; capture and promotion threat analysis
```

Individual fields:

```text
board, self_pieces, opponent_pieces, legal_actions, candidate_move, next_board,
capture_value, promotion_distance, immediate_promotion, opponent_promotion_threat,
move_legality_check, promotion_check, capture_check, piece_safety, material_balance, race_value, selected_action
```

Bundles:

```text
observe_bundle = board + self_pieces + opponent_pieces + legal_actions + promotion objective
transition_bundle = candidate_move + next_board + capture_value
race_value_bundle = move_legality_check + promotion_check + capture_check + promotion_distance + immediate_promotion + material_balance + race_value
opponent_response_bundle = opponent_promotion_threat + opponent_capture_reply + piece_safety
decision_bundle = selected_move + race_or_capture_reason
```

Candidate row format:

```text
{move} -> next_board=...; move_legality_check=...; promotion_check=...; capture_check=...; opponent_threat=...; race_value=...
```

Final value:

```text
Prefer immediate promotion, then stopping opponent promotion, then best safe race/capture value.

Verification:

```text
move_legality_check verifies forward movement or legal diagonal capture.
promotion_check verifies whether the move reaches the opponent home row.
capture_check verifies whether the destination contains an opponent piece.
```
```

### Nim

Theory:

```text
backward induction; combinatorial-game state analysis
```

Individual fields:

```text
pile_sizes, legal_actions, last_match_loses, candidate_action, next_pile_sizes,
transition_check, large_pile_count, singleton_count, phase_classification, nim_sum_or_parity,
opponent_position_value, selected_action
```

Bundles:

```text
observe_bundle = pile_sizes + legal_actions + last_match_loses
transition_bundle = candidate_action + next_pile_sizes + transition_check
phase_value_bundle = large_pile_count + singleton_count + phase_classification + nim_sum_or_parity
opponent_value_bundle = opponent_position_value + backward_induction_reason
decision_bundle = selected_action + selection_reason
```

Candidate row format:

```text
{action} -> next_state=...; transition_check=valid/invalid; phase=...; key_value=...; opponent_position_value=...
```

Final value:

```text
Prefer the legal action that gives the opponent a losing state under backward induction.

Verification:

```text
transition_check verifies that the action changes exactly one pile by the stated take amount.
```
```

### Pig

Theory:

```text
expected-value stopping analysis; dynamic risk/reward comparison
```

Individual fields:

```text
self_score, opponent_score, turn_total, target_score, legal_actions,
score_after_stop, stop_wins_now, bank_value, bust_loss, bust_probability,
target_check, bust_loss_check, safe_roll_average_gain, one_roll_expected_turn_total, roll_can_win_next,
score_race_pressure, stop_vs_roll_value, selected_action
```

Bundles:

```text
observe_bundle = self_score + opponent_score + turn_total + target_score + legal_actions
stop_value_bundle = score_after_stop + target_check + stop_wins_now + bank_value
roll_value_bundle = bust_loss + bust_loss_check + bust_probability + safe_roll_average_gain + one_roll_expected_turn_total + roll_can_win_next
race_pressure_bundle = self_distance_to_target + opponent_distance_to_target + score_race_pressure
decision_bundle = stop_vs_roll_value + selected_action + selection_reason
```

Candidate row format:

```text
<stop> -> score_after_stop=...; target_check=...; bank_value=...; stop_value=...
<roll> -> bust_loss=...; bust_loss_check=...; expected_turn_total=...; roll_can_win_next=...; roll_value=...
```

Final value:

```text
Choose <stop> if it wins now or has better stopping value; choose <roll> if expected/race value justifies bust risk.

Verification:

```text
target_check verifies whether score_after_stop reaches target_score.
bust_loss_check verifies that bust_loss equals turn_total, not permanent score.
```
```

### First-Price Sealed-Bid Auction

Theory:

```text
bid shading and expected payoff maximization under hidden opponent valuation
```

Individual fields:

```text
private_valuation, legal_bids, bid_validity_check, candidate_bid, opponent_value_belief,
win_probability_belief, surplus_if_win, overbid_risk, expected_utility,
selected_bid
```

Bundles:

```text
observe_bundle = private_valuation + legal_bids + auction_payment_rule
belief_bundle = opponent_value_belief + win_probability_belief
surplus_risk_bundle = bid_validity_check + candidate_bid + surplus_if_win + overbid_risk
expected_utility_bundle = win_probability_belief + surplus_if_win + expected_utility
decision_bundle = selected_bid + bid_shading_reason
```

Candidate row format:

```text
{bid} -> bid_validity_check=...; win_prob=...; surplus_if_win=...; overbid_risk=...; expected_utility=...
```

Final value:

```text
Choose the legal bid with the best expected utility while avoiding bids above private value unless forced by the action space.

Verification:

```text
bid_validity_check verifies that the bid is legal.
surplus_if_win must be private_valuation - bid.
overbid_risk is true if bid exceeds private_valuation.
```
```

### Kuhn Poker

Theory:

```text
information-set reasoning; belief updating; mixed-strategy bluff/call incentives
```

Individual fields:

```text
private_card, public_betting_history, legal_actions, pot_size, belief_basis, card_strength,
opponent_card_belief, action_context, showdown_value, bluff_incentive,
call_or_fold_threshold, expected_action_value, selected_action
```

Bundles:

```text
observe_bundle = private_card + public_betting_history + legal_actions + pot_size
belief_bundle = belief_basis + opponent_card_belief + action_context
hand_value_bundle = card_strength + showdown_value
betting_value_bundle = bluff_incentive + call_or_fold_threshold + expected_action_value
decision_bundle = selected_action + information_set_reason
```

Candidate row format:

```text
{action} -> belief_basis=...; hand_value=...; bluff_or_call_value=...; expected_action_value=...
```

Final value:

```text
Choose the legal action with the best information-set expected value, accounting for value betting, bluffing, calling, or folding.

Belief basis:

```text
belief_basis cites private_card and public_betting_history.
Do not claim hidden cards are known.
```
```

### Liar's Dice

Theory:

```text
Bayesian belief updating; bluff detection; mixed-strategy bidding
```

Individual fields:

```text
self_dice, public_bid_history, last_bid, legal_actions, candidate_action, belief_basis,
opponent_dice_belief, claim_probability, liar_call_value, raise_strength,
bluff_risk, expected_action_value, selected_action
```

Bundles:

```text
observe_bundle = self_dice + public_bid_history + last_bid + legal_actions
belief_bundle = belief_basis + opponent_dice_belief + claim_probability
liar_call_bundle = last_bid + claim_probability + liar_call_value
raise_bundle = candidate_bid + raise_strength + bluff_risk
decision_bundle = expected_action_value + selected_action + belief_reason
```

Candidate row format:

```text
{action} -> belief_basis=...; claim_probability=...; call_value=...; raise_or_bluff_risk=...; expected_action_value=...
```

Final value:

```text
Choose <Liar> if the last claim is unlikely enough; otherwise choose the legal bid with the best belief-adjusted value.

Belief basis:

```text
belief_basis cites self dice and public bid history.
Do not claim the opponent dice are known.
```
```

### Negotiation

Theory:

```text
bargaining reasoning; private-preference inference; acceptance threshold analysis
```

Individual fields:

```text
item_pool, self_value_vector, legal_actions, current_stage, most_recent_proposal,
most_recent_utterance, public_history, opponent_preference_belief,
self_payoff_by_candidate, allocation_check, opponent_acceptance_likelihood,
acceptance_threshold, concession_or_signal_value, selected_action
```

Bundles:

```text
observe_bundle = item_pool + self_value_vector + current_stage + legal_actions
history_belief_bundle = most_recent_proposal + most_recent_utterance + public_history + opponent_preference_belief
payoff_bundle = allocation_check + candidate_action + self_payoff_by_candidate + concession_cost
agreement_bundle = opponent_acceptance_likelihood + acceptance_threshold + concession_or_signal_value
decision_bundle = selected_action + bargaining_reason
```

Candidate row format:

```text
{proposal_or_utterance_or_agree} -> allocation_check=...; self_payoff=...; belief_effect=...; acceptance_likelihood=...; bargaining_value=...
```

Final value:

```text
Accept only if the current offer clears the acceptance threshold; otherwise choose the legal proposal or utterance with the best payoff-agreement tradeoff.

Verification:

```text
allocation_check verifies that item quantities obey the current legal-action constraints.
self_payoff must use self_value_vector, not guessed opponent values.
```
```

### Iterated Prisoner's Dilemma

Theory:

```text
history-dependent repeated-game reasoning; cooperation, retaliation, and forgiveness
```

Individual fields:

```text
round_index, public_action_history, self_previous_actions, opponent_previous_actions,
legal_actions, last_opponent_action, cooperation_rate, defection_pattern,
history_check, punishment_state, forgiveness_condition, one_shot_payoff_incentive,
future_interaction_value, selected_action
```

Bundles:

```text
observe_bundle = round_index + public_action_history + legal_actions + payoff rule
history_pattern_bundle = self_previous_actions + opponent_previous_actions + last_opponent_action + cooperation_rate + defection_pattern
incentive_bundle = one_shot_payoff_incentive + future_interaction_value
strategy_state_bundle = history_check + punishment_state + forgiveness_condition + retaliation_or_cooperation_value
decision_bundle = selected_action + repeated_game_reason
```

Candidate row format:

```text
{action} -> history_check=...; history_pattern=...; one_shot_value=...; future_value=...; repeated_game_value=...
```

Final value:

```text
Choose the action with the best repeated-game value: cooperate when future cooperation is credible, retaliate against recent defection, and forgive when cooperation can be restored.

Verification:

```text
history_check uses the actual public history and distinguishes self actions from opponent actions.
```
```

## Core Principle

Use this structure:

1. Give clear field definitions.
2. Apply the fields in compact candidate rows.
3. Make the final decision from the final value field.
4. Always end with a parseable action.

The model should understand the fields in detail, but it should not repeat every candidate under every field.

## Field Roles

Not every field is an arithmetic calculation. Use role labels so the model knows how to handle each field.

```text
[OBSERVE]
Read information directly from the game state or prompt.

[DERIVE]
Compute a consequence from the observed state and a candidate action.

[CLASSIFY]
Assign a type, phase, or condition label to the candidate state.

[EVALUATE]
Judge strategic value using the mapped theory.

[DECIDE]
Choose the final legal action using the evaluation fields.
```

Use role-specific verbs:

```text
Read observation fields.
Derive candidate consequences.
Classify candidate states.
Evaluate strategic value.
Decide the final action.
```

Avoid saying only "compute every field." That can make the model treat all fields as arithmetic, even when the field is a classification or strategic evaluation.

## Why This Is Needed

A bad field prompt often makes the model write like this:

```text
1. legal_move_effect:
   - candidate A ...
   - candidate B ...

2. large_pile_count:
   - candidate A ...
   - candidate B ...

3. singleton_count:
   - candidate A ...
   - candidate B ...
```

This repeats the same candidates many times. In games with many legal actions, the response can be truncated before the model reaches `Action:`.
If the parser then scans the whole reasoning text for a legal action, it may accidentally choose an action mentioned in the middle of the reasoning.

The better pattern is:

```text
candidate A -> next_state; field_1=...; field_2=...; final_value=...
candidate B -> next_state; field_1=...; field_2=...; final_value=...
```

This still computes the fields, but each candidate appears only once.

## Prompt Template

Use this template when creating a new field-based CoT prompt.

```text
First work through the decision fields, then choose one legal action.
Read, derive, classify, evaluate, and decide in that order.

Theory:
{mapped_theory_name}

Why it fits:
{short explanation connecting the game rule to the theory}

Field definitions:
1. [OBSERVE] {field_name}
{plain English definition}

2. [DERIVE] {field_name}
{plain English definition}

...

Candidate row format:
For each legal action, write one compact row:
{action} -> [DERIVE] {next_state}; [CLASSIFY] {phase}; [EVALUATE] {key_value}; [EVALUATE] {final_value_field}

Do not repeat the same candidate under every field.
Do not write a long paragraph for each candidate.

Final decision rule:
Choose the legal action with the best {final_value_field}.
The final decision must be based on {final_value_field}, not only on surface features.

Output format:
Thought:
{compact candidate rows}
Best candidate: ...
Final check: ...

Action:
{one legal action}
```

## Design Rules

- Field definitions should be explicit enough that the model knows what each field means.
- Field definitions should use role labels: `[OBSERVE]`, `[DERIVE]`, `[CLASSIFY]`, `[EVALUATE]`, `[DECIDE]`.
- Candidate rows should be compact enough that the model can evaluate all legal actions and still reach `Action:`.
- The final value field must be named and repeated as the final decision criterion.
- Avoid asking for long prose under each field.
- Avoid duplicated fields that express the same information.
- If a field is only needed in one phase of the game, say so.
- If the game has different phases, use a `phase` field and let each phase determine the key value field.
- The prompt should explicitly say: `Do not repeat the same candidate under every field.`
- The prompt should explicitly say: `Always finish with Action: on its own line.`

## Parser Safety Rule

The safest parser behavior is:

1. First search for a legal action after `Final Action:` or `Action:`.
2. If no action marker exists, ask for repair.
3. Do not use a legal action that appears only inside the reasoning text as the final move.

Reasoning text often mentions rejected candidate actions. Treating those as final moves creates false actions.

## Nim Example

Use detailed definitions:

```text
[OBSERVE] current_state:
Read the current pile sizes.

[DERIVE] next_state:
The pile state after applying one legal action.

[CLASSIFY] phase:
normal_phase if at least two piles have more than one match.
endgame_phase if zero or one pile has more than one match.

[EVALUATE] key_value:
In normal_phase, key_value is nim_sum.
In endgame_phase, key_value is singleton parity and final-match risk.

[EVALUATE] opponent_position_value:
The value of the state the opponent receives after my action.
Mark opponent=losing if optimal play from that state forces the opponent to take the final match.
Mark opponent=winning if the opponent has a reply that can force me to take the final match.

[DECIDE] final_action:
Choose the legal action with the best opponent_position_value.
```

Use compact rows:

```text
Thought:
State: [0,3,5,1].
Candidate rows:
<pile:2, take:1> -> [0,2,5,1]; phase=normal; nim_sum=6; opponent=winning
<pile:3, take:1> -> [0,3,4,1]; phase=normal; nim_sum=6; opponent=winning
<pile:4, take:1> -> [0,3,5,0]; phase=normal; nim_sum=6; opponent=winning
<pile:2, take:2> -> [0,1,5,1]; phase=endgame; singletons=2; opponent=winning
<pile:3, take:2> -> [0,3,3,1]; phase=normal; nim_sum=1; opponent=winning
<pile:2, take:3> -> [0,0,5,1]; phase=endgame; singletons=1; opponent=winning
<pile:3, take:3> -> [0,3,2,1]; phase=normal; nim_sum=0; opponent=losing
<pile:3, take:4> -> [0,3,1,1]; phase=endgame; singletons=2; opponent=winning
<pile:3, take:5> -> [0,3,0,1]; phase=endgame; singletons=1; opponent=winning
Best candidate: <pile:3, take:3>, because it gives the opponent a losing state.
Final check: opponent_position_value is best for <pile:3, take:3>.

Action:
<pile:3, take:3>
```

## Nim Ready-To-Use Field Prompt

```text
Field workflow:
Read, derive, classify, evaluate, and decide in that order.
Do not treat every field as arithmetic.
Do not repeat the same candidate under every field.

Theory:
backward induction; combinatorial-game state analysis

Why it fits:
Nim is a deterministic perfect-information game. The pile state fully determines the strategic position, and the best action is found by evaluating the state given to the opponent.

Field definitions:
1. [OBSERVE] current_state
Read the current pile sizes from the observation.

2. [OBSERVE] legal_actions
Read the legal actions. Each legal action removes one or more matches from exactly one pile.

3. [OBSERVE] last_match_loses
This is misere Nim: the player who takes the final remaining match loses.

4. [DERIVE] next_state
For each legal action, derive the pile state after applying that action.

5. [CLASSIFY] phase
Classify each next_state:
- normal_phase: at least two piles have more than one match.
- endgame_phase: zero or one pile has more than one match.

6. [EVALUATE] key_value
Use the phase-specific value:
- normal_phase: key_value = nim_sum of all nonzero pile sizes in next_state.
- endgame_phase: key_value = singleton_count and final-match parity.

7. [EVALUATE] opponent_position_value
Evaluate the state the opponent receives after my action.
Use backward induction:
- opponent=losing if optimal play from next_state forces the opponent to take the final match.
- opponent=winning if the opponent has a reply that can force me to take the final match.

8. [DECIDE] final_action
Choose the legal action with the best opponent_position_value.
Prefer actions that give the opponent a losing state.

Candidate row format:
For each legal action, write exactly one compact row:
{action} -> next_state=...; phase=...; key_value=...; opponent_position_value=...

Rules:
- Do not write separate long sections for next_state, phase, nim_sum, and opponent_position_value.
- Do not stop after surface features such as singleton_count or large pile count.
- The final decision must be based on opponent_position_value.
- Always finish with Action: on its own line.

Output format:
Thought:
State: ...
Candidate rows:
...
Best candidate: ...
Final check: opponent_position_value favors ...

Action:
{one legal action}
```

## Pig Example

Use detailed definitions:

```text
[OBSERVE] current_scores:
Read self_score, opponent_score, and turn_total.

[OBSERVE] target_score:
Read the target score from the game rule prompt.

[DERIVE] score_after_stop:
self_score + turn_total.

[CLASSIFY] stop_wins_now:
Whether score_after_stop reaches or exceeds the target score.

[EVALUATE] bust_risk:
Rolling has a 1/6 chance of losing the current turn_total.

[DERIVE] one_roll_expected_turn_total:
Approximate value of rolling once more: (5/6) * (turn_total + 4).

[CLASSIFY] roll_can_win_next:
Whether a safe roll can immediately create a winning stop opportunity.

[EVALUATE] score_race_pressure:
How close each player is to the target score.

[EVALUATE] stop_vs_roll_value:
The final comparison between stopping and rolling.

[DECIDE] final_action:
Choose <roll> or <stop> using stop_vs_roll_value.
```

Use compact rows:

```text
Thought:
State: self=12, opponent=18, turn_total=7, target=20.
score_after_stop=19; stop_wins_now=false.
Candidate rows:
<stop> -> bank=7; next_score=19; value=does_not_win_and_gives_opponent_chance
<roll> -> bust_loss=7; safe_gain_avg=4; safe_roll_can_win=true; value=high_risk_but_can_win_next
Best candidate: <roll>, because stopping leaves me at 19 while the opponent is close to winning.
Final check: stop_vs_roll_value favors rolling because a safe roll can reach the target.

Action:
<roll>
```

## Pig Ready-To-Use Field Prompt

```text
Field workflow:
Read, derive, classify, evaluate, and decide in that order.
Do not treat every field as arithmetic.
Do not repeat the same candidate under every field.

Theory:
expected-value stopping analysis; dynamic risk/reward comparison

Why it fits:
Pig alternates between player decisions and dice chance events. The key strategic question is whether to bank the current turn total or risk rolling for additional points.

Field definitions:
1. [OBSERVE] current_scores
Read self_score, opponent_score, and turn_total from the observation.

2. [OBSERVE] target_score
Read the target score from the game rule prompt. A player wins by banking enough points to reach or exceed this target.

3. [OBSERVE] legal_actions
The legal actions are <roll> and <stop>.

4. [DERIVE] score_after_stop
Compute self_score + turn_total. This is the permanent score after choosing <stop>.

5. [CLASSIFY] stop_wins_now
Check whether score_after_stop >= target_score.
If true, <stop> wins immediately and should be chosen.

6. [EVALUATE] bank_value
The certain value of <stop> is banking turn_total points.
If turn_total is 0, <stop> banks 0 and gives up the turn.

7. [EVALUATE] bust_risk
Rolling has a 1/6 chance to roll a 1 and lose the current turn_total.
The bust_loss is turn_total, not the permanent score.

8. [DERIVE] safe_roll_value
Rolling has a 5/6 chance to add a safe die value from 2 to 6.
Use 4 as the average safe gain.

9. [DERIVE] one_roll_expected_turn_total
Approximate one more roll as (5/6) * (turn_total + 4).
Use this as a quick comparison against bank_value.

10. [CLASSIFY] roll_can_win_next
Check whether a safe roll can immediately create a winning stop opportunity:
- if self_score + turn_total + 2 >= target_score, any safe roll reaches the target.
- if self_score + turn_total + 6 >= target_score, some safe rolls reach the target.

11. [EVALUATE] score_race_pressure
Compare distances to target:
- self_distance_to_target = target_score - self_score.
- opponent_distance_to_target = target_score - opponent_score.
If the opponent is close to the target, banking too little may give them the next winning chance.
If I am far behind, rolling may be necessary even with bust risk.

12. [EVALUATE] stop_vs_roll_value
Compare <stop> and <roll> using stop_wins_now, bank_value, bust_risk, one_roll_expected_turn_total, roll_can_win_next, and score_race_pressure.

13. [DECIDE] final_action
Choose exactly one legal action, <roll> or <stop>, based on stop_vs_roll_value.

Candidate row format:
Write one compact row for each legal action:
<stop> -> score_after_stop=...; stop_wins_now=...; bank_value=...; stop_value=...
<roll> -> bust_loss=...; one_roll_expected_turn_total=...; roll_can_win_next=...; roll_value=...

Rules:
- If stop_wins_now is true, choose <stop>.
- If turn_total is 0, usually choose <roll> because <stop> banks nothing.
- Do not stop merely because bust risk exists; compare bust risk against expected roll value and score race pressure.
- Do not roll merely because the target is far away; check whether bank_value is already strategically sufficient.
- The final decision must be based on stop_vs_roll_value.
- Always finish with Action: on its own line.

Output format:
Thought:
State: ...
Candidate rows:
...
Best candidate: ...
Final check: stop_vs_roll_value favors ...

Action:
{<roll> or <stop>}
```

## Checklist For Adding A New Game

When adding a new game, fill in:

```text
Theory:
{mapped theory}

State fields:
{what the model must read from the observation}

Candidate row fields:
{what each legal action row should contain, using role labels}

Final value field:
{the one field that decides the action}

Final decision rule:
{how to choose from the candidate rows}
```

Example:

```text
Candidate row format:
{action} -> [DERIVE] next_state=...; [CLASSIFY] phase=...; [EVALUATE] key_value=...; [EVALUATE] final_value=...

Final value field:
opponent_position_value

Final decision rule:
Choose the action that gives the opponent a losing state.
```
