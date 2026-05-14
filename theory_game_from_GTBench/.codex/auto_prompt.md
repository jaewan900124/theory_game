# Auto Theory-Analysis Game Loop

You are operating inside:

```text
/home/nlpgpu7/jaewanpark/project/theory_game/theory_game_from_GTBench
```

Run the GTBench theory-analysis data loop without asking the user for additional input.

## Goal

For every supported GTBench game, run one complete match and collect turn-level theory-analysis records.

The important output is not only the selected action. For each Codex-controlled decision point, create a training-data-style record containing:

- game name
- current state
- legal actions
- game rule summary
- selected Osborne/Rubinstein-style theory
- why that theory applies to this game state
- structured state fields needed for reasoning
- concise theory-based analysis
- chosen action
- prompt text that could be used for SFT or distillation
- completion text that includes the analysis and final action

The opposing player should be `gemma4:31b` where an LLM opponent is needed. The opponent should use the current `TheoryAgent` prompt setup unless a game-specific wrapper forces another path.

## Games

Run one match each for:

- `tictactoe`
- `connect4`
- `breakthrough`
- `first_sealed_auction`
- `liars_dice`
- `negotiation`
- `nim`
- `pig`
- `kuhn_poker`
- `prisoners_dilemma`

## Required Output Files

Write outputs under:

```text
experiments/auto_theory_loop/
```

Required files:

```text
experiments/auto_theory_loop/status.json
experiments/auto_theory_loop/summary.md
experiments/auto_theory_loop/theory_records.jsonl
```

If a game already has a game-specific output directory, keep it and reference it from `summary.md`.

## Record Schema

Each line in `theory_records.jsonl` should follow this shape:

```json
{
  "game": "tictactoe",
  "match_index": 0,
  "turn_index": 0,
  "actor": "Codex",
  "opponent": "gemma4:31b",
  "state": {},
  "legal_actions": [],
  "game_rule_summary": "",
  "selected_theory": "",
  "theory_applicability": "",
  "state_fields": {},
  "analysis": "",
  "chosen_action": "",
  "training_prompt": "",
  "training_completion": "",
  "opponent_prompt": "",
  "opponent_response": "",
  "status": "ok"
}
```

For imperfect-information games, include private/public information fields:

```json
{
  "private_information": {},
  "public_history": {},
  "belief_state": {}
}
```

For stochastic games, include chance events:

```json
{
  "chance_events": []
}
```

## Theory Selection Guide

Use these mappings as the starting point:

- Tic-Tac-Toe, Connect4, Breakthrough: finite extensive-form game with perfect information; backward-induction-style lookahead; maxmin defense.
- Nim: finite extensive-form game with perfect information; backward induction; combinatorial-game state analysis.
- Pig: stochastic dynamic decision problem with chance nodes; expected value and stopping-risk analysis.
- First-price sealed-bid auction: Bayesian private-value strategic game; bid shading and expected payoff.
- Kuhn poker: imperfect-information extensive-form game; information sets, belief updating, mixed-strategy/bluff reasoning.
- Liar's Dice: imperfect-information extensive-form game with chance; Bayesian belief updating and bluff detection.
- Negotiation: bargaining game with private preferences and strategic communication.
- Iterated Prisoner's Dilemma: repeated strategic game; history-dependent cooperation/retaliation reasoning.

## Execution Rules

1. Do not ask the user for moves.
2. If Codex controls a player, choose the action automatically using the selected theory.
3. If `gemma4:31b` returns invalid or empty output, repair once by asking it to output exactly one legal action.
4. If repair fails, use a deterministic legal fallback, mark the record as repaired, and continue.
5. Stop only when one of these happens:
   - all games have one complete match,
   - tests/checks pass and no new work is needed,
   - no code or output changed since the previous loop,
   - max loop count is reached.
6. Update `status.json` after each loop.
7. Update `summary.md` with completed games, failed games, and next action.

## Verification

Run lightweight checks before finishing:

```bash
python -m py_compile scripts/*.py
```

If a new runner script is created, run it for at least one complete Tic-Tac-Toe match before marking the loop complete.

## Final Response

Return a short JSON-like summary:

```json
{
  "status": "complete|partial|blocked",
  "completed_games": [],
  "failed_games": [],
  "output_dir": "experiments/auto_theory_loop",
  "next_step": ""
}
```
