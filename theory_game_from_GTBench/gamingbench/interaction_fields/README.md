# Interaction-Field Compiler

This module compiles `game rules x mapped theory` into deterministic interaction
fields and a compact small-model decision program.

## Mapping Source

The compiler uses the repository's existing mapping file:

`gamingbench/configs/game_theory_mapping.json`

Do not add a second game-to-theory mapping. `compile_from_observation(game_id,
observation)` reads the existing mapping and selects theory handlers from the
mapped `solution_concept` and `game_type`.

## Field Computation

An interaction field is useful only when it has:

- deterministic inputs from the current state or game interface,
- exact calculation steps,
- decision-use semantics,
- priority/ranking/filter semantics,
- verifier conditions.

The compiler returns `InteractionFieldSpec` objects. Each field records its
source game, source theory handler, required capabilities, calculation method,
computed value, decision role, operator, invariants, and the failure mode it
guards against.

## Unavailable Fields

If a required capability is missing, the compiler does not guess. It returns:

```json
{"status": "unavailable", "reason": "..."}
```

Examples:

- auction expected utility is unavailable when no win-probability model exists,
- belief-weighted expected utility is unavailable when no belief state exists,
- minimax values are unavailable when no transition/utility capability exists.

Unavailable fields are still included in the compiled program so downstream
evaluation can measure missing capabilities instead of silently accepting
hallucinated values.

## Adding a Game Adapter

Implement a `GameAdapter` subclass in `adapters.py` or near the game code.
Expose only capabilities the game can support. Common optional capabilities:

- `legal_actions(player=None)`
- `payoff_matrix()`
- `private_value()`
- `win_probability_by_action()`
- `chance_outcomes(action=None)`
- `belief_state()`
- game-specific readers such as `tictactoe_board()`

Do not implement a method by returning fabricated values. If the information is
not available, omit the capability or return `None` so handlers can emit
`unavailable`.

## Adding a Theory Handler

Implement a `TheoryHandler` subclass in `handlers.py` with:

- `theory_id`
- `required_game_capabilities`
- `supports_text(mapping_text)`
- `compile(adapter, mapping_entry)`

The handler should produce executable or semi-executable field specs, not
natural-language theory summaries. Add the handler to `DEFAULT_HANDLERS`.

## Small-Model Prompt

`CompiledDecisionProgram.small_model_prompt` is intentionally compact. It
contains:

- legal actions,
- computed field values,
- short calculation reminders,
- ordered decision rules,
- verifier checks,
- strict final JSON schema.

The prompt tells the small model to execute the program, not explain theory.
