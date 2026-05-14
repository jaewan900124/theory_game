# pig Prompt Samples

## Source

- `source_file`: `experiments/qwen3_14b_interaction_field_think_vs_baseline_allgames_10_split_v3/pig/theory_interaction_field_agent_qwen3-14b-ollama-think_prompt_agent_qwen3-14b-ollama-think.jsonl`
- `jsonl_rows`: `10`

---

## Interaction Field Prompt

### Metadata

- `jsonl_line`: `1`
- `step_index`: `1`
- `agent`: `TheoryInteractionFieldAgent`
- `move`: `<roll>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: `{\n  "action": "<roll>",\n  "used_rule": "P2",\n  "used_fields": ["roll_has_no_bust_loss", "stop_wins_now"],\n  "verifier_passed": true\n}`

### Prompt

```text
Pig is a fast-paced dice game where players risk accumulating points with each roll but risk losing them all if they roll a 1. Each player must decide when to stop rolling and bank their points, aiming to be the first to reach 100 points.
    You are playing Pig with the other. 
Right now, your current score is 0 and your opponent's current score is 0. In this turn, you have earned 0 score.
    
    The legal moves are: <roll>, <stop>.
You are not explaining theory.
You are executing a decision program.

Game:
pig

Mapped theory:
stochastic_expected_value

Current state:
{"self_current_score": 0, "opponent_current_score": 0, "turn_total_score": 0, "state": "Scores: 0 0, Turn total: 0\nCurrent player: 0\n", "openspiel_legal_actions": [0, 1], "legal_moves": ["<roll>", "<stop>"], "env_name": "pig"}

Legal actions:
["<roll>", "<stop>"]

Computed fields:
- score_after_stop:
  Role: informational
  Operator: compare
  Calculation: score_after_stop=self_score+turn_total
  Value:
    0

- stop_wins_now:
  Role: verifier_only
  Operator: verify
  Calculation: Compare score_after_stop to target_score.
  Value:
    false

- roll_has_no_bust_loss:
  Role: verifier_only
  Operator: verify
  Calculation: Check whether turn_total_score is 0.
  Value:
    true

- bust_loss:
  Role: informational
  Operator: compare
  Calculation: Bust loss equals current turn_total_score.
  Value:
    0

- score_race_pressure:
  Role: tie_breaker
  Operator: compare
  Priority: 5
  Calculation: Compute target_score minus each permanent score.
  Value:
    self_distance: 100
    opponent_distance: 100
    score_after_stop_distance: 100

- one_roll_heuristic_value_by_action:
  Role: action_value
  Operator: maximize
  Priority: 6
  Calculation: Use probability 1/6 for bust and 5/6 for safe outcomes. Approximate safe gain by average of 2..6.
  Value:
    <stop>: 0
    <roll>: 3.3333333333333335

- current_scores:
  Role: informational
  Operator: compare
  Calculation: Read self_score, opponent_score, and turn_total.
  Value:
    self_score: 0
    opponent_score: 0
    turn_total: 0

- target_score:
  Role: informational
  Operator: compare
  Calculation: Winning threshold from rules or observation.
  Value:
    100

- stop_or_roll_comparison:
  Role: informational
  Operator: compare
  Calculation: Compare legal stop/roll actions by risk-adjusted value.
  Value:
    <stop>: {"score_after_action": 0, "certain": true, "bust_loss": 0}
    <roll>: {"approx_expected_score_after_one_roll": 3.3333333333333335, "bust_probability": 0.16666666666666666, "bust_loss": 0}

Decision program:
P0. Choose only from legal_actions.
P1. If stop_wins_now is true and <stop> is legal, choose <stop>. (stop_if_winning)
P2. If roll_has_no_bust_loss is true and stop_wins_now is false, choose <roll>. (roll_if_no_bust_loss)
P3. If one_roll_heuristic_value_by_action is available, choose the remaining legal action with the highest value. (maximize_one_roll_heuristic_value)
P4. If tied, use the listed tie-break rule if available; otherwise choose the first tied legal action.
P5. Do not use unavailable fields as if they were computed.
P6. Before final answer, run verifier checks.

Verifier:
- legal_action_only: selected action is in legal_actions
- roll_when_turn_total_zero: if turn_total is 0 and stop_wins_now is false, selected action is <roll> [field: roll_has_no_bust_loss]
- stop_when_winning: if stop_wins_now is true, selected action is <stop> [field: stop_wins_now]
- required_game_fields_present: all game schema required_derived_fields are present as computed or unavailable fields

Return only valid JSON:
{
  "action": "...",
  "used_rule": "P?",
  "used_fields": [
    "..."
  ],
  "verifier_passed": true
}
```

---

## Baseline PromptAgent Prompt

### Metadata

- `jsonl_line`: `1`
- `step_index`: `6`
- `agent`: `PromptAgent`
- `move`: `<roll>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: `<Action:<roll>>`

### Prompt

```text
Pig is a fast-paced dice game where players risk accumulating points with each roll but risk losing them all if they roll a 1. Each player must decide when to stop rolling and bank their points, aiming to be the first to reach 100 points.
    You are playing Pig with the other. 
Right now, your current score is 0 and your opponent's current score is 0. In this turn, you have earned 0 score.
    
    The legal moves are: <roll>, <stop>.
You must choose an legal action to set up advantages.

Your output must be in the following format:

Action:
Your action wrapped with <>, e.g., <stop>

Please return your answer without explanation!
```
