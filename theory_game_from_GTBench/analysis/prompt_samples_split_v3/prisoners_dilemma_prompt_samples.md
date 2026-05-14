# prisoners_dilemma Prompt Samples

## Source

- `source_file`: `experiments/qwen3_14b_interaction_field_think_vs_baseline_allgames_10_split_v3/prisoners_dilemma/theory_interaction_field_agent_qwen3-14b-ollama-think_prompt_agent_qwen3-14b-ollama-think.jsonl`
- `jsonl_rows`: `10`

---

## Interaction Field Prompt

### Metadata

- `jsonl_line`: `1`
- `step_index`: `1`
- `agent`: `TheoryInteractionFieldAgent`
- `move`: `<Testify>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: `{\n  "action": "<Testify>",\n  "used_rule": "P2",\n  "used_fields": [\n    "stage_game_worst_case_payoff_by_action",\n    "future_interaction_value",\n    "opponent_recent_defection"\n  ],\n  "verifier_passed": true\n}`

### Prompt

```text
You and your partner are in the Prisoner's Dilemma situation. Specifically, if you <Testify> against your partner and your partner remains <Silent>, you will go free while your partner will get 3 years in prison on the main charge. If you remain <Silent> but your partner <Testify> against you, you will serve 3 years in prison and your partner will be set free. If you and your partner <Testify> against each other, you and your partner will each serve 2 years. 
If both you and your partner remain <Silent>, you and your partner will each server 1 year.

In this new round, you and your partner are making decision simultaneously and you do not know your partner's decision.

The legal actions are: <Testify>, <Silent>.
You are not explaining theory.
You are executing a decision program.

Game:
python_iterated_prisoners_dilemma

Mapped theory:
repeated_game_trigger_strategy

Current state:
{"self_moves": "", "opponent_moves": "", "openspiel_legal_actions": [0, 1], "legal_moves": ["<Silent>", "<Testify>"], "env_name": "python_iterated_prisoners_dilemma"}

Legal actions:
["<Silent>", "<Testify>"]

Computed fields:
- history_summary:
  Role: informational
  Operator: compare
  Calculation: Read self and opponent histories from observation.
  Value:
    self: []
    opponent: []

- opponent_defection_count:
  Role: informational
  Operator: compare
  Calculation: Count opponent Testify/D actions.
  Value:
    0

- opponent_cooperation_count:
  Role: informational
  Operator: compare
  Calculation: Count opponent Silent/C actions.
  Value:
    0

- trigger_strategy_state:
  Role: informational
  Operator: compare
  Calculation: Set punish only after observed recent defection. Use no_history when there is no evidence of cooperation or defection.
  Value:
    "no_history"

- opponent_recent_defection:
  Role: verifier_only
  Operator: verify
  Calculation: Check only the latest observed opponent action. Return false when no opponent action has been observed.
  Value:
    false

- stage_game_payoff_bounds_by_action:
  Role: informational
  Operator: compare
  Calculation: Use Prisoner's Dilemma payoff rule. For each legal action, record worst and best payoff across opponent actions.
  Value:
    <Silent>: {"worst_case": 0, "best_case": 5, "if_opponent_silent": 5, "if_opponent_testify": 0}
    <Testify>: {"worst_case": 1, "best_case": 10, "if_opponent_silent": 10, "if_opponent_testify": 1}

- stage_game_worst_case_payoff_by_action:
  Role: ranking_score
  Operator: maximize
  Priority: 2
  Calculation: Take the minimum payoff for each action across possible opponent actions.
  Value:
    <Silent>: 0
    <Testify>: 1

- strictly_dominant_stage_actions:
  Role: informational
  Operator: compare
  Calculation: Compare payoffs under each possible opponent action. Include an action only if it is strictly better in every case.
  Value:
    ["<Testify>"]

- future_interaction_value:
  Role: informational
  Operator: verify
  Calculation: Require a horizon/discount or opponent cooperation model. If absent, mark unavailable instead of assuming cooperation.
  Value: unavailable
  Reason: discount/horizon or opponent cooperation model is missing

- opponent_recent_actions:
  Role: informational
  Operator: compare
  Calculation: Most recent opponent actions in order.
  Value:
    []

- opponent_cooperation_rate:
  Role: informational
  Operator: compare
  Calculation: Observed cooperation rate.
  Value:
    0

- opponent_defection_rate:
  Role: informational
  Operator: compare
  Calculation: Observed defection rate.
  Value:
    0

- pattern_detection:
  Role: informational
  Operator: compare
  Calculation: Detect always defect, tit-for-tat, cooperation, or noisy pattern.
  Value:
    pattern: no_history
    sample_size: 0

- next_action_implications:
  Role: informational
  Operator: compare
  Calculation: Compare Silent and Testify for current and future consequences.
  Value:
    <Silent>: {"stage_worst_case": 0, "requires_future_cooperation": true}
    <Testify>: {"stage_worst_case": 1, "requires_future_cooperation": false}

Decision program:
P0. Choose only from legal_actions.
P1. If opponent_recent_defection is true and <Testify> is legal, select <Testify>. (retaliate_after_observed_defection)
P2. If stage_game_worst_case_payoff_by_action is available, choose the remaining legal action with the highest value. (avoid_first_round_exploitation_without_future_value)
P3. If tied, use the listed tie-break rule if available; otherwise choose the first tied legal action.
P4. Do not use unavailable fields as if they were computed.
P5. Before final answer, run verifier checks.

Verifier:
- legal_action_only: selected action is in legal_actions
- retaliate_after_defection: if true, selected action should be <Testify> [field: opponent_recent_defection]
- no_assumed_future_cooperation: do not select <Silent> solely from empty history when future_interaction_value is unavailable [field: future_interaction_value]
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
- `step_index`: `2`
- `agent`: `PromptAgent`
- `move`: `<Testify>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: `Action: <Testify>`

### Prompt

```text
You and your partner are in the Prisoner's Dilemma situation. Specifically, if you <Testify> against your partner and your partner remains <Silent>, you will go free while your partner will get 3 years in prison on the main charge. If you remain <Silent> but your partner <Testify> against you, you will serve 3 years in prison and your partner will be set free. If you and your partner <Testify> against each other, you and your partner will each serve 2 years. 
If both you and your partner remain <Silent>, you and your partner will each server 1 year.

In this new round, you and your partner are making decision simultaneously and you do not know your partner's decision.

The legal actions are: <Testify>, <Silent>.
You must choose an legal action to set up advantages.

Your output must be in the following format:

Action:
Your action wrapped with <>, <Testify|Silent>, e.g., <Testify>, <Silent>

Please return your answer without explanation!
```
