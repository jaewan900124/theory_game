from gamingbench.prompts.regex_and_format import get_step_env_regex_and_format
from gamingbench.prompts.theory_prompt_builder import mapped_theory_guidance


NIM_FIELD_COT_GUIDE = """Field workflow:
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
{action} -> next_state=...; transition_check=valid/invalid; phase=...; key_value=...; opponent_position_value=...

Rules:
- transition_check must verify that the action changes exactly one pile by the stated take amount.
- Do not write separate long sections for next_state, phase, nim_sum, and opponent_position_value.
- Do not stop after surface features such as singleton_count or large pile count.
- The final decision must be based on opponent_position_value.
- Always finish with Action: on its own line.
"""


PIG_FIELD_COT_GUIDE = """Field workflow:
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
<stop> -> score_after_stop=...; target_check=...; bank_value=...; stop_value=...
<roll> -> bust_loss=...; bust_loss_check=...; one_roll_expected_turn_total=...; roll_can_win_next=...; roll_value=...

Rules:
- target_check must verify whether score_after_stop reaches the target score.
- bust_loss_check must verify that bust_loss equals turn_total, not permanent score.
- If stop_wins_now is true, choose <stop>.
- If turn_total is 0, usually choose <roll> because <stop> banks nothing.
- Do not stop merely because bust risk exists; compare bust risk against expected roll value and score race pressure.
- Do not roll merely because the target is far away; check whether bank_value is already strategically sufficient.
- The final decision must be based on stop_vs_roll_value.
- Always finish with Action: on its own line.
"""


GAME_FIELD_COT_GUIDES = {
    "tictactoe": """Field workflow:
Read, derive, classify, evaluate, and decide in that order.
Use compact candidate rows; do not write separate sections for every field.

Theory:
backward-induction-style lookahead; subgame-perfect reasoning; maxmin defense

Field bundles:
- observe_bundle = board + self_mark + opponent_mark + legal_actions + win condition
- transition_bundle = candidate_action + next_board
- tactical_value_bundle = line_check + immediate_win + immediate_block + fork_creation + fork_prevention
- opponent_response_bundle = opponent_best_reply + continuation_value
- decision_bundle = selected_action + tactical_or_continuation_reason

Candidate row format:
{action} -> next_board=...; line_check=win_line/block_line/none; line=...; tactic=win/block/fork/safe/weak; opponent_reply=...; continuation_value=...

Verification rules:
- Only mark tactic=win if line_check names a completed three-in-a-row for me.
- Only mark tactic=block if line_check names an opponent two-in-a-row whose missing cell is this action.
- If line_check=none, do not call the action win or block.

Final decision rule:
Prefer immediate win, then forced block, then fork or best continuation value.
Always finish with Action: on its own line.
""",
    "connect4": """Field workflow:
Read, derive, classify, evaluate, and decide in that order.
Use compact candidate rows; do not write separate sections for every field.

Theory:
backward-induction-style lookahead; threat-space reasoning; maxmin defense

Field bundles:
- observe_bundle = board + column_heights + self_disc + opponent_disc + legal_columns
- transition_bundle = candidate_column + drop_position + next_board
- threat_value_bundle = line_check + immediate_win + immediate_block + created_threats + center_control
- opponent_response_bundle = allowed_opponent_win + opponent_best_reply + continuation_value
- decision_bundle = selected_column + threat_or_defense_reason

Candidate row format:
{column_action} -> drop=...; line_check=win_line/block_line/threat_line/none; line=...; immediate=win/block/none; threats=...; opponent_risk=...; continuation_value=...

Verification rules:
- Only mark immediate=win if line_check names a completed four-in-a-row for me.
- Only mark immediate=block if line_check names an opponent immediate four-in-a-row threat blocked by this action.
- opponent_risk must note if this move allows an opponent immediate win.

Final decision rule:
Prefer immediate win, then block opponent immediate win, then highest safe threat-space value.
Always finish with Action: on its own line.
""",
    "breakthrough": """Field workflow:
Read, derive, classify, evaluate, and decide in that order.
Use compact candidate rows; do not write separate sections for every field.

Theory:
backward-induction-style race analysis; capture and promotion threat analysis

Field bundles:
- observe_bundle = board + self_pieces + opponent_pieces + legal_actions + promotion objective
- transition_bundle = candidate_move + next_board + capture_value
- race_value_bundle = move_legality_check + promotion_check + capture_check + promotion_distance + immediate_promotion + material_balance + race_value
- opponent_response_bundle = opponent_promotion_threat + opponent_capture_reply + piece_safety
- decision_bundle = selected_move + race_or_capture_reason

Candidate row format:
{move} -> next_board=...; move_legality_check=...; promotion_check=...; capture_check=...; opponent_threat=...; race_value=...

Verification rules:
- move_legality_check must verify forward movement or legal diagonal capture.
- promotion_check must verify whether the move reaches the opponent home row.
- capture_check must verify whether the destination contains an opponent piece.

Final decision rule:
Prefer immediate promotion, then stopping opponent promotion, then best safe race/capture value.
Always finish with Action: on its own line.
""",
    "first_sealed_auction": """Field workflow:
Read, derive, evaluate, and decide in that order.
Use compact candidate rows; do not write separate sections for every field.

Theory:
bid shading and expected payoff maximization under hidden opponent valuation

Field bundles:
- observe_bundle = private_valuation + legal_bids + auction_payment_rule
- belief_bundle = opponent_value_belief + win_probability_belief
- surplus_risk_bundle = bid_validity_check + candidate_bid + surplus_if_win + overbid_risk
- expected_utility_bundle = win_probability_belief + surplus_if_win + expected_utility
- decision_bundle = selected_bid + bid_shading_reason

Candidate row format:
{bid} -> bid_validity_check=...; win_prob=...; surplus_if_win=...; overbid_risk=...; expected_utility=...

Verification rules:
- bid_validity_check must verify that the bid is legal.
- surplus_if_win must be private_valuation - bid.
- overbid_risk is true if bid exceeds private_valuation.

Final decision rule:
Choose the legal bid with the best expected utility while avoiding bids above private value unless forced by the action space.
Always finish with Action: on its own line.
""",
    "kuhn_poker": """Field workflow:
Read, update belief, evaluate, and decide in that order.
Use compact candidate rows; do not write separate sections for every field.

Theory:
information-set reasoning; belief updating; mixed-strategy bluff/call incentives

Field bundles:
- observe_bundle = private_card + public_betting_history + legal_actions + pot_size
- belief_bundle = belief_basis + opponent_card_belief + action_context
- hand_value_bundle = card_strength + showdown_value
- betting_value_bundle = bluff_incentive + call_or_fold_threshold + expected_action_value
- decision_bundle = selected_action + information_set_reason

Candidate row format:
{action} -> belief_basis=...; hand_value=...; bluff_or_call_value=...; expected_action_value=...

Belief rule:
- belief_basis must cite the private card and public betting history; do not claim hidden cards are known.

Final decision rule:
Choose the legal action with the best information-set expected value, accounting for value betting, bluffing, calling, or folding.
Always finish with Action: on its own line.
""",
    "liars_dice": """Field workflow:
Read, update belief, evaluate, and decide in that order.
Use compact candidate rows; do not write separate sections for every field.

Theory:
Bayesian belief updating; bluff detection; mixed-strategy bidding

Field bundles:
- observe_bundle = self_dice + public_bid_history + last_bid + legal_actions
- belief_bundle = belief_basis + opponent_dice_belief + claim_probability
- liar_call_bundle = last_bid + claim_probability + liar_call_value
- raise_bundle = candidate_bid + raise_strength + bluff_risk
- decision_bundle = expected_action_value + selected_action + belief_reason

Candidate row format:
{action} -> belief_basis=...; claim_probability=...; call_value=...; raise_or_bluff_risk=...; expected_action_value=...

Belief rule:
- belief_basis must cite self dice and public bid history; do not claim the opponent dice are known.

Final decision rule:
Choose <Liar> if the last claim is unlikely enough; otherwise choose the legal bid with the best belief-adjusted value.
Always finish with Action: on its own line.
""",
    "negotiation": """Field workflow:
Read, infer preference, evaluate payoff/agreement value, and decide in that order.
Use compact candidate rows; do not write separate sections for every field.

Theory:
bargaining reasoning; private-preference inference; acceptance threshold analysis

Field bundles:
- observe_bundle = item_pool + self_value_vector + current_stage + legal_actions
- history_belief_bundle = most_recent_proposal + most_recent_utterance + public_history + opponent_preference_belief
- payoff_bundle = allocation_check + candidate_action + self_payoff_by_candidate + concession_cost
- agreement_bundle = opponent_acceptance_likelihood + acceptance_threshold + concession_or_signal_value
- decision_bundle = selected_action + bargaining_reason

Candidate row format:
{proposal_or_utterance_or_agree} -> allocation_check=...; self_payoff=...; belief_effect=...; acceptance_likelihood=...; bargaining_value=...

Verification rules:
- allocation_check must verify that item quantities obey the current legal-action constraints.
- self_payoff must use self_value_vector, not guessed opponent values.

Final decision rule:
Accept only if the current offer clears the acceptance threshold; otherwise choose the legal proposal or utterance with the best payoff-agreement tradeoff.
Always finish with Action: on its own line.
""",
    "python_iterated_prisoners_dilemma": """Field workflow:
Read, summarize history, evaluate repeated-game incentives, and decide in that order.
Use compact candidate rows; do not write separate sections for every field.

Theory:
history-dependent repeated-game reasoning; cooperation, retaliation, and forgiveness

Field bundles:
- observe_bundle = round_index + public_action_history + legal_actions + payoff rule
- history_pattern_bundle = self_previous_actions + opponent_previous_actions + last_opponent_action + cooperation_rate + defection_pattern
- incentive_bundle = one_shot_payoff_incentive + future_interaction_value
- strategy_state_bundle = history_check + punishment_state + forgiveness_condition + retaliation_or_cooperation_value
- decision_bundle = selected_action + repeated_game_reason

Candidate row format:
{action} -> history_check=...; history_pattern=...; one_shot_value=...; future_value=...; repeated_game_value=...

Verification rule:
- history_check must use the actual public history and distinguish self actions from opponent actions.

Final decision rule:
Choose the action with the best repeated-game value: cooperate when future cooperation is credible, retaliate against recent defection, and forgive when cooperation can be restored.
Always finish with Action: on its own line.
""",
}


def _format_default_field_cot_guidance(env_name):
    guidance = mapped_theory_guidance(env_name, max_steps=None)
    fields = "\n".join(f"- {field}" for field in guidance["prompt_state_fields"])
    steps = "\n".join(f"- {step}" for step in guidance["steps"])
    field_section = f"\nDecision fields to compute in order:\n{fields}\n" if fields else ""
    return f"""Use the mapped game-theory concept while reasoning:
Theory: {guidance["concept"]}
Why it fits: {guidance["why"]}
{field_section}
CoT checklist:
{steps}
- Compare candidate actions by the final state-value field, not by surface features alone.
- Commit to one legal action only after the checklist is complete.
"""


def construct_step_prompt(observation):
    env_name = observation.get("env_name", "")
    regex, format = get_step_env_regex_and_format(env_name)
    legal_moves = observation.get("legal_moves", [])

    if env_name == "nim":
        theory_guidance = NIM_FIELD_COT_GUIDE
        thought_instruction = (
            "State: ...\n"
            "Candidate rows:\n"
            "One compact row per legal action using next_state, phase, key_value, and opponent_position_value.\n"
            "Best candidate: ...\n"
            "Final check: opponent_position_value favors ..."
        )
    elif env_name == "pig":
        theory_guidance = PIG_FIELD_COT_GUIDE
        thought_instruction = (
            "State: ...\n"
            "Candidate rows:\n"
            "One compact row for <stop> and one compact row for <roll> using the row format above.\n"
            "Best candidate: ...\n"
            "Final check: stop_vs_roll_value favors ..."
        )
    elif env_name in GAME_FIELD_COT_GUIDES:
        theory_guidance = GAME_FIELD_COT_GUIDES[env_name]
        thought_instruction = (
            "State: ...\n"
            "Candidate rows:\n"
            "One compact row per important legal action using the row format above.\n"
            "Best candidate: ...\n"
            "Final check: final value favors ..."
        )
    else:
        theory_guidance = _format_default_field_cot_guidance(env_name)
        thought_instruction = "Your concise field-by-field game-theory reasoning."

    if len(legal_moves) <= 10:
        action_reminder = (
            "Remember, you can only choose one move from the legal actions "
            f"which is {legal_moves}"
        )
    else:
        action_reminder = "Remember, you can only choose one move from the legal actions."

    prompt = f"""First think through the decision fields, then choose one legal action to set up advantages.

{theory_guidance}
Your output must be in the following format strictly:

Thought:
{thought_instruction}

Action:
Your action wrapped by <>, i.e., {format}

{action_reminder}
"""
    return {
        "prompt": prompt,
        "regex": regex,
    }
