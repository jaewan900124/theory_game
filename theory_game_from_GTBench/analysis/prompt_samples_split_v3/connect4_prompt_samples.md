# connect4 Prompt Samples

## Source

- `source_file`: `experiments/qwen3_14b_interaction_field_think_vs_baseline_allgames_10_split_v3/connect4/theory_interaction_field_agent_qwen3-14b-ollama-think_prompt_agent_qwen3-14b-ollama-think.jsonl`
- `jsonl_rows`: `10`

---

## Interaction Field Prompt

### Metadata

- `jsonl_line`: `1`
- `step_index`: `1`
- `agent`: `TheoryInteractionFieldAgent`
- `move`: `<C4>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: `{\n  "action": "<C4>",\n  "used_rule": "P1",\n  "used_fields": ["heuristic_tiebreak_center_distance_by_column"],\n  "verifier_passed": true\n}`

### Prompt

```text
Connect 4 is a two-player connection board game, where the players choose a color and then take turns dropping colored discs into a vertically suspended grid. The pieces fall straight down, occupying the next available space within the column. The objective of the game is to be the first to form a horizontal, vertical, or diagonal line of four of one's own discs. You are a gaming agent that aims to beat me in Connect 4 games. 
    Each move is represented by a string consisting of two parts: the column (C) and the row (R), in that order. For instance, C1 means the first column.
Your opponent does not have any move so far. You do not have any move so far. Currently, the legal positions are <C1>,<C2>,<C3>,<C4>,<C5>,<C6>,<C7>
You are not explaining theory.
You are executing a decision program.

Game:
connect4

Mapped theory:
sequential_lookahead

Current state:
{"opponent_moves": [], "self_moves": [], "state": ".......\n.......\n.......\n.......\n.......\n.......\n", "openspiel_legal_actions": [0, 1, 2, 3, 4, 5, 6], "legal_moves": ["<C1>", "<C2>", "<C3>", "<C4>", "<C5>", "<C6>", "<C7>"], "env_name": "connect4"}

Legal actions:
["<C1>", "<C2>", "<C3>", "<C4>", "<C5>", "<C6>", "<C7>"]

Computed fields:
- minimax_value_by_action:
  Role: ranking_score
  Operator: maximize
  Priority: 10
  Calculation: Capability check failed before search. Return unavailable instead of claiming minimax.
  Value: unavailable
  Reason: no deterministic transition/search adapter is available for this sequential game

- board_reconstruction:
  Role: informational
  Operator: compare
  Calculation: Reconstruct discs by column and row using gravity and public history.
  Value:
    rows_bottom_to_top: [".......", ".......", ".......", ".......", ".......", "......."]
    self_mark: S
    opponent_mark: O
    reconstruction_reliable: True
    reliability_reason: ordered public history available or no mixed-column ambiguity

- column_heights:
  Role: informational
  Operator: compare
  Calculation: Compute current height for each column.
  Value:
    <C1>: 0
    <C2>: 0
    <C3>: 0
    <C4>: 0
    <C5>: 0
    <C6>: 0
    <C7>: 0

- playable_row_by_column:
  Role: informational
  Operator: compare
  Calculation: Map each legal column to the row where my disc would land.
  Value:
    <C1>: 1
    <C2>: 1
    <C3>: 1
    <C4>: 1
    <C5>: 1
    <C6>: 1
    <C7>: 1

- immediate_win_columns:
  Role: tactical_set
  Operator: choose_if_nonempty
  Calculation: Legal columns that create my four-in-a-row after gravity drop.
  Value:
    []

- immediate_block_columns:
  Role: tactical_set
  Operator: choose_if_nonempty
  Calculation: Legal columns that block opponent's immediate four-in-a-row.
  Value:
    []

- dangerous_moves_that_enable_opponent_win:
  Role: informational
  Operator: compare
  Calculation: Legal columns that allow an opponent immediate win on the next turn.
  Value:
    []

- heuristic_tiebreak_center_distance_by_column:
  Role: heuristic_tiebreaker
  Operator: minimize
  Calculation: Distance of each legal column from center; lower is more central; use only as a heuristic tie-breaker after tactical checks.
  Value:
    <C1>: 3
    <C2>: 2
    <C3>: 1
    <C4>: 0
    <C5>: 1
    <C6>: 2
    <C7>: 3

Decision program:
P0. Choose only from legal_actions.

P1. If tied, use the listed tie-break rule if available; otherwise choose the first tied legal action.
P2. Do not use unavailable fields as if they were computed.
P3. Before final answer, run verifier checks.

Verifier:
- legal_action_only: selected action is in legal_actions
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
- `move`: `<C3>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: `Action: <C3>`

### Prompt

```text
Connect 4 is a two-player connection board game, where the players choose a color and then take turns dropping colored discs into a vertically suspended grid. The pieces fall straight down, occupying the next available space within the column. The objective of the game is to be the first to form a horizontal, vertical, or diagonal line of four of one's own discs. You are a gaming agent that aims to beat me in Connect 4 games. 
    Each move is represented by a string consisting of two parts: the column (C) and the row (R), in that order. For instance, C1 means the first column.
Your opponent has finished moves: <C4> You do not have any move so far. Currently, the legal positions are <C1>,<C2>,<C3>,<C4>,<C5>,<C6>,<C7>
You must choose an legal action to set up advantages.

Your output must be in the following format:

Action:
Your action wrapped with <>, <Cx>, e.g., <C1>, <C7>

Please return your answer without explanation!
```
