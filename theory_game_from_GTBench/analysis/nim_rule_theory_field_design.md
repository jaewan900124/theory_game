# Nim: Rule-Theory Interaction Field Design

## Purpose

This document sketches the methodology:

```text
game rules including objective x selected game theory -> interaction fields
```

The example game is `nim` from GTBench. The goal is not to add generic theory
text to the prompt. The goal is to define fields that are:

- grounded in the game rules and objective,
- motivated by the mapped game-theoretic theory,
- computable from the current state and legal actions,
- useful for choosing among legal actions,
- verifiable after the model selects an action.

## Source Rule Prompt

The baseline Nim rule prompt says:

```text
In Nim, a strategic game with a set of four piles containing 1, 3, 5, and 7
matches respectively, players aim to avoid taking the last match. During each
turn, a player may take any number of matches from a single pile, but must take
at least one and cannot exceed the number remaining in that pile. The objective
is to force the opponent to pick up the final match, thereby winning the game.
The action is presented in <pile:x, take:y>, which means take y match(es) from
the x-th pile.
```

From this, the environment objective is:

```text
Win by forcing the opponent to take the final match.
Equivalently, avoid being the player who takes the last remaining match.
```

This is misere Nim, not normal-play Nim.

## Theory Basis

The mapped theory for Nim is sequential lookahead / perfect-information
extensive-game reasoning.

From Osborne and Rubinstein, *A Course in Game Theory*, the relevant basis is:

- Chapter 6 studies extensive games with perfect information.
- An extensive game explicitly describes the sequential structure of decisions.
- Perfect information means that when a player moves, the player knows the
  earlier history.
- A finite-horizon extensive game can be analyzed by evaluating continuations
  from histories.
- Subgame perfect equilibrium requires optimal play after every history.
- The constructive proof of subgame-perfect equilibrium for finite perfect
  information games evaluates terminal outcomes and works backward through
  histories.

For Nim, this implies that the useful decision fields should be continuation
fields:

```text
current state -> legal action -> successor state -> opponent position value
```

The field should not merely describe Nim theory. It should compute the successor
state and classify whether the opponent is handed a losing or winning position.

## Field Design Criteria

Use a field only if it satisfies all five criteria:

1. Rule-computable: the value is determined from piles, legal actions, and the
   misere objective.
2. Theory-motivated: the value corresponds to a perfect-information continuation
   calculation.
3. Action-discriminative: the value can rank or filter legal actions.
4. Verifier-compatible: after an action is selected, the system can check whether
   the action respected the field.
5. Non-prescriptive: the field exposes computed values or candidate sets, not a
   hardcoded answer.

## Proposed Interaction Fields

### 1. `environment_objective`

Why needed:

The game is misere Nim. Normal Nim and misere Nim differ near the endgame. The
agent must know that taking the final match loses.

Computation:

```text
Read from rule prompt:
"players aim to avoid taking the last match"
"force the opponent to pick up the final match"
```

Value example:

```json
{
  "objective_type": "misere_takeaway",
  "losing_terminal_condition": "selected action takes the final remaining match",
  "winning_condition": "opponent is forced to take the final remaining match"
}
```

Decision use:

`verifier_only`.

Verification:

If selected action leaves total matches `0`, then the selected action violates
the objective unless no alternative exists and the current state is already
forced loss.

### 2. `pile_state`

Why needed:

Sequential reasoning needs the current state. In Nim, the full public state is
the vector of pile sizes.

Computation:

```text
Read pile counts directly from observation.
If direct pile counts are missing, infer each pile size from the maximum legal
take amount for that pile.
```

Value example:

```json
{"1": 1, "2": 3, "3": 5, "4": 7}
```

Decision use:

`informational`.

Verification:

Every legal action `<pile:i, take:k>` must satisfy `1 <= k <= pile_state[i]`.

### 3. `legal_move_effects`

Why needed:

Perfect-information lookahead requires evaluating the successor state after each
legal action. Without this field, the model may reason about the wrong pile
state.

Computation:

```text
For each legal action <pile:i, take:k>:
  successor = copy(pile_state)
  successor[i] = successor[i] - k
  remove or keep zero piles consistently
```

Value example:

```json
{
  "<pile:1, take:1>": {"2": 3, "3": 5, "4": 7},
  "<pile:4, take:7>": {"1": 1, "2": 3, "3": 5}
}
```

Decision use:

`informational`.

Verification:

Selected action must change exactly one pile, and the changed pile must decrease
by exactly the chosen take amount.

### 4. `phase_by_action`

Why needed:

The rule "normal Nim uses nim-sum zero" is not sufficient in misere endgames.
The agent must know whether each successor state is still normal phase or
misere endgame phase.

Computation:

```text
For each successor state:
  large_piles = piles with size > 1
  if count(large_piles) >= 2:
      phase = normal_phase
  else:
      phase = misere_endgame_phase
```

Decision use:

`switch_condition`.

Verification:

If phase is `misere_endgame_phase`, the decision rule must not blindly choose
the lowest normal nim-sum.

### 5. `nim_sum_by_action`

Why needed:

In normal-phase impartial combinatorial games like Nim, moving to nim-sum zero
hands the opponent a losing position under optimal play. This is the compact
continuation-value calculation.

Computation:

```text
For each successor state:
  nim_sum = XOR of all nonzero pile sizes
```

Value example:

```json
{
  "<pile:1, take:1>": 1,
  "<pile:2, take:2>": 2,
  "<pile:4, take:7>": 7
}
```

Decision use:

`ranking_score`, but only in `normal_phase`.

Verification:

If any normal-phase action has `nim_sum = 0`, selected action should be one of
those actions.

### 6. `singleton_parity_by_action`

Why needed:

In misere Nim endgames, the objective is to avoid taking the last match. When
only singleton piles remain, parity determines who is forced to take the last
match.

Computation:

```text
For each successor state:
  singleton_count = number of piles with size 1
  singleton_parity = odd if singleton_count % 2 == 1 else even
```

Decision use:

`ranking_score` in `misere_endgame_phase`.

Verification:

When all successor piles are singleton piles, selected action should leave an odd
number of singleton piles to the opponent when such an action exists.

### 7. `opponent_position_value_by_action`

Why needed:

This is the core interaction field. It combines the game objective with
sequential lookahead: after I move, is the opponent in a losing or non-losing
position?

Computation:

```text
For each legal action:
  successor = legal_move_effects[action]
  if successor has total matches 0:
      opponent_position = opponent_winning
      reason = I took the final match and lose under misere rule
  else if phase == normal_phase and nim_sum == 0:
      opponent_position = opponent_losing
  else if phase == misere_endgame_phase and all piles are singleton and
          singleton_parity == odd:
      opponent_position = opponent_losing
  else:
      opponent_position = opponent_not_proven_losing
```

Decision use:

`priority_candidate`.

Verification:

If any action has `opponent_position = opponent_losing`, selected action should
be one of those actions.

### 8. `current_position_value`

Why needed:

This field explains whether the current player is already in a winning or losing
position. This is essential for interpreting results. For example, the initial
state `[1, 3, 5, 7]` has nim-sum `0`, so the current player is losing in the
normal phase if the opponent plays optimally.

Computation:

```text
current_phase = normal_phase if at least two piles are larger than 1 else
                misere_endgame_phase
current_nim_sum = XOR of current nonzero pile sizes

if current_phase == normal_phase:
    current_player_losing iff current_nim_sum == 0
else:
    use singleton parity / exact terminal check
```

Value example for `[1, 3, 5, 7]`:

```json
{
  "current_phase": "normal_phase",
  "current_nim_sum": 0,
  "current_position_value": "current_player_losing",
  "reason": "normal-phase misere Nim with nim-sum 0"
}
```

Decision use:

`informational` and `result_interpretation`.

Verification:

If `current_position_value = current_player_losing`, the system should not mark
the agent as strategically wrong merely because it lost, unless it selected a
suboptimal action relative to `opponent_position_value_by_action`.

## Decision Program

The small-model prompt should use the fields as follows:

```text
P0. Choose only from legal_actions.
P1. Never choose an action that takes the final match if another legal action exists.
P2. If opponent_position_value_by_action contains opponent_losing actions, choose one of them.
P3. In normal_phase, prefer actions with successor nim_sum = 0.
P4. In misere_endgame_phase, use singleton parity rather than normal nim-sum.
P5. If no action is proven winning, choose among legal actions using a deterministic tie-breaker and report that the current position is not proven winning.
P6. Run verifier checks before returning.
```

## Verifier Checks

```text
V0. selected_action in legal_actions.
V1. selected_action changes exactly one pile by the stated amount.
V2. selected_action does not take the final match when a non-final action exists.
V3. if any opponent_losing action exists, selected_action is opponent_losing.
V4. if selected_action used normal nim-sum, selected action's phase is normal_phase.
V5. if selected_action used singleton parity, selected action's phase is misere_endgame_phase.
V6. if current_position_value is current_player_losing, evaluation should separate win/loss result from optimal-action correctness.
```

## Compact Prompt Shape

```text
You are not explaining Nim theory.
You are executing a decision program.

Game objective:
Avoid taking the final match; force opponent to take it.

Legal actions:
{legal_actions}

Computed fields:
- current_position_value: {...}
- opponent_position_value_by_action: {...}
- phase_by_action: {...}
- nim_sum_by_action: {...}
- singleton_parity_by_action: {...}

Decision program:
P0. Choose only from legal_actions.
P1. If opponent_losing actions exist, choose one.
P2. If normal_phase, use nim_sum = 0.
P3. If misere_endgame_phase, use singleton parity.
P4. If no winning action exists, choose a legal tie-break and report uncertainty.

Return JSON:
{
  "action": "...",
  "used_fields": ["..."],
  "verifier_passed": true
}
```

## Why This Methodology Is Testable

This design gives testable claims:

- Field correctness can be checked from piles and legal actions.
- The chosen action can be checked against the field values.
- Win/loss can be separated from optimal-action quality.
- If a game starts in a losing position, the method can still receive credit for
  selecting an optimal action.

For the current GTBench Nim initial state `[1, 3, 5, 7]`, this distinction is
important because the first player is in a losing position under optimal play.

