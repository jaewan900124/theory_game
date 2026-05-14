# tictactoe Prompt Samples

## Source

- `source_file`: `experiments/qwen3_14b_interaction_field_think_vs_baseline_allgames_10_split_v3/tictactoe/theory_interaction_field_agent_qwen3-14b-ollama-think_prompt_agent_qwen3-14b-ollama-think.jsonl`
- `jsonl_rows`: `10`

---

## Interaction Field Prompt

### Metadata

- `jsonl_line`: `1`
- `step_index`: `1`
- `agent`: `TheoryInteractionFieldAgent`
- `move`: `<C2R2>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: `{\n  "action": "<C2R2>",\n  "used_rule": "P3",\n  "used_fields": ["heuristic_tiebreak_center_corner_edge"],\n  "verifier_passed": true\n}`

### Prompt

```text
Tic Tac Toe is a two-player game played on a grid. Players take turns marking a space with their respective symbols. The goal is to get 3 of one's own symbols in a row, either horizontally, vertically, or diagonally, before the opponent does. If all nine squares are filled and no player has three in a row, the game is a draw. The Tic Tac Toe game is played on a 3 by 3 grid, with the winning length as 3.
Each move is represented by a string consisting of two parts: the column (C) and the row (R), in that order. For instance, C1R2 means the movement at the position of the first column and the second row of the grid. You are playing this game with the user (opponent).
You are the first to go.
Currently, the legal actions are <C1R1>, <C2R1>, <C3R1>, <C1R2>, <C2R2>, <C3R2>, <C1R3>, <C2R3>, <C3R3>.
You are not explaining theory.
You are executing a decision program.

Game:
tictactoe

Mapped theory:
sequential_lookahead

Current state:
{"opponent_moves": [], "self_moves": [], "state": "...\n...\n...", "openspiel_legal_actions": [0, 1, 2, 3, 4, 5, 6, 7, 8], "legal_moves": ["<C1R1>", "<C2R1>", "<C3R1>", "<C1R2>", "<C2R2>", "<C3R2>", "<C1R3>", "<C2R3>", "<C3R3>"], "env_name": "tictactoe"}

Legal actions:
["<C1R1>", "<C2R1>", "<C3R1>", "<C1R2>", "<C2R2>", "<C3R2>", "<C1R3>", "<C2R3>", "<C3R3>"]

Computed fields:
- immediate_win_actions:
  Role: tactical_set
  Operator: choose_if_nonempty
  Priority: 1
  Calculation: Scan every winning line. If it has two self marks and one legal empty cell, add the empty action.
  Value:
    []

- opponent_immediate_win_actions:
  Role: verifier_only
  Operator: verify
  Calculation: Scan every winning line. If it has two opponent marks and one legal empty cell, add the empty action.
  Value:
    []

- immediate_block_actions:
  Role: tactical_set
  Operator: choose_if_nonempty
  Priority: 2
  Calculation: Use opponent_immediate_win_actions as required block squares.
  Value:
    []

- board_reading:
  Role: informational
  Operator: compare
  Calculation: Reconstruct all occupied cells by player from board or public move history.
  Value:
    self_moves: []
    opponent_moves: []
    empty_legal_cells: ["<C1R1>", "<C2R1>", "<C3R1>", "<C1R2>", "<C2R2>", "<C3R2>", "<C1R3>", "<C2R3>", "<C3R3>"]

- fork_creation_actions:
  Role: tactical_set
  Operator: choose_if_nonempty
  Calculation: Legal actions creating at least two next-turn winning threats.
  Value:
    []

- fork_block_actions:
  Role: tactical_set
  Operator: choose_if_nonempty
  Calculation: Legal actions preventing opponent fork threats.
  Value:
    []

- heuristic_tiebreak_center_corner_edge:
  Role: heuristic_tiebreaker
  Operator: compare
  Calculation: Classify legal actions as center, corner, or edge only as a heuristic tie-breaker after tactical checks.
  Value:
    center: ["<C2R2>"]
    corners: ["<C1R1>", "<C3R1>", "<C1R3>", "<C3R3>"]
    edges: ["<C2R1>", "<C1R2>", "<C3R2>", "<C2R3>"]

Decision program:
P0. Choose only from legal_actions.
P1. If immediate_win_actions is non-empty and available, choose from it. (win_now)
P2. If immediate_block_actions is non-empty and available, choose from it. (block_now)
P3. If tied, use the listed tie-break rule if available; otherwise choose the first tied legal action.
P4. Do not use unavailable fields as if they were computed.
P5. Before final answer, run verifier checks.

Verifier:
- legal_action_only: selected action is in legal_actions
- block_if_required: if immediate_win_actions empty and immediate_block_actions nonempty, selected action is in immediate_block_actions [field: immediate_block_actions]
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
- `move`: `<C1R1>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: `<Action:<C1R1>>`

### Prompt

```text
Tic Tac Toe is a two-player game played on a grid. Players take turns marking a space with their respective symbols. The goal is to get 3 of one's own symbols in a row, either horizontally, vertically, or diagonally, before the opponent does. If all nine squares are filled and no player has three in a row, the game is a draw. The Tic Tac Toe game is played on a 3 by 3 grid, with the winning length as 3.
Each move is represented by a string consisting of two parts: the column (C) and the row (R), in that order. For instance, C1R2 means the movement at the position of the first column and the second row of the grid. You are playing this game with the user (opponent).
Your opponent has finished actions: <C2R2>. 
Currently, the legal actions are <C1R1>, <C2R1>, <C3R1>, <C1R2>, <C3R2>, <C1R3>, <C2R3>, <C3R3>.
You must choose an legal action to set up advantages.

Your output must be in the following format:

Action:
Your action wrapped with <>, <CxRy>, e.g., <C1R1>, <C3R3>

Please return your answer without explanation!
```
