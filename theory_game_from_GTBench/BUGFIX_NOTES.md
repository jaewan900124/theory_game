# Bugfix Notes

## 2026-05-10: Iterated Prisoner's Dilemma history prompt bug

### Problem

`gamingbench/prompts/observation_prompts/prisoners_dilemma.py` rendered past-round decisions incorrectly.

The prompt builder received separate histories:

- `self_moves`
- `opponent_moves`

But the old loop zipped them in reversed variable order and computed both displayed actions from the same variable:

```python
for round_idx, (self, opponent) in enumerate(zip(opponent_moves, self_moves)):
    self_move = '<Silent>' if self == 'C' else '<Testify>'
    opponent_move = '<Silent>' if self == 'C' else '<Testify>'
```

This could make the prompt show both players as having taken the same historical action even when they did not.

### Impact

Any previous `prisoners_dilemma` experiments that depended on repeated-game history may have misleading prompts when historical actions differed between players.

Cases where both players always made the same move, such as both repeatedly choosing `<Testify>`, are not visibly affected.

### Fix

The loop now uses the correct histories and variables:

```python
for round_idx, (self_action, opponent_action) in enumerate(zip(self_moves, opponent_moves)):
    self_move = '<Silent>' if self_action == 'C' else '<Testify>'
    opponent_move = '<Silent>' if opponent_action == 'C' else '<Testify>'
```

### Validation

Sample observation:

```python
{"self_moves": "CD", "opponent_moves": "DC"}
```

Now renders:

```text
In the 1th round, you decided to <Silent> and your opponent decided to <Testify>.
In the 2th round, you decided to <Testify> and your opponent decided to <Silent>.
```
