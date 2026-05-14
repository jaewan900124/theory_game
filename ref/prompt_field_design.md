# Field-Register Prompt Design

This note defines the reusable prompt structure for theory-guided game agents.
It is written to match the current GameBench `high_reasoning` and
`high_distill` prompt design, but the same pattern can be reused for new games.

## Core Idea

A field-register prompt separates game understanding from action selection.

The prompt should define a fixed set of fields that the runtime model must
compute from the current observation. The model then chooses an action using
those fields, the legal action list, and game rules.

Use game theory to choose fields, not to override the rules. The current game
implementation, observation, and available actions remain authoritative.

Field design itself is not a runtime model choice. It is a design-time step:
read the game rules, game structure, observations, action-space shapes, role
structure, and game-theoretic frame; then write the field register that the
runtime model will execute.

```text
Design-time Codex or human
rules + implementation + observations + action spaces + game theory
        |
        v
role-specific specs + action-space-specific programs + verifier checks
field computation targets + active field register
        |
        v
Runtime game-playing model
compute field values -> compare legal actions -> output selected_action
```

## Prompt Modes

### high_reasoning

Purpose:

- Game theory plus game rules define a field register.
- The active role/action-space spec should already be selected when feasible.
- The model computes field values from the observation.
- The model compares candidate legal actions itself.

Include:

- `Field register: base fields`
- `Active role-specific field set` when roles or phases differ
- `Active action-space context` when available actions have different meanings
- `Field computation targets`
- `Reasoning workflow`
- `Verifier checks`

Do not include:

- A compiled P0/P1/P2 decision program.

Expected trace shape:

```json
{
  "field_application": {
    "computed_fields": {},
    "candidate_action_values": [],
    "reasoned_selection": "...",
    "verifier_checks": []
  },
  "selected_action": "..."
}
```

### high_distill

Purpose:

- Game theory plus game rules define a field register.
- The active role/action-space spec should already be selected when feasible.
- The prompt also supplies a compact decision program for that active context.
- The model executes the program step by step and reports the trace.

Include:

- `Field register: base fields`
- `Active role-specific field set` when roles or phases differ
- `Active action-space-specific program`
- `Field computation targets`
- `Compiled decision program`
- `Verifier checks`

The decision program should use numbered rules:

```text
P0. Choose only from the current available action ids.
P1. ...
P2. ...
P3. ...
P*. Do not use unavailable fields as if they were computed.
P*. If tied, choose the legal action with the strongest verifier-passing best-response case.
```

Expected trace shape:

```json
{
  "field_application": {
    "computed_fields": {},
    "decision_program_trace": [],
    "used_rule": "...",
    "verifier_checks": [],
    "verifier_passed": true
  },
  "selected_action": "..."
}
```

## Field Register Design

The prompt has two layers:

- `Field computation targets`: natural-language statements of what must be
  computed to solve the active decision.
- Active fields: compact snake_case JSON keys where the model writes the
  computed results.

Targets answer "what must be figured out"; fields answer "where the result goes
in the trace."

Example:

```text
Field computation target:
- Compute safe clusters of unrevealed own-team words from private card colors.

Active fields:
- own_team_unrevealed_words_with_private_types
- safe_target_cluster_for_this_clue
```

Field values do not have to be numeric. A field can be a state extraction, a
belief estimate, a legal constraint, a risk label, a candidate-value comparison,
or an output-format guard. The important rule is that the field must be useful
for the current decision and computable from the observation, action list,
private information, public history, or rules.

Good fields are:

- directly computable from the observation, action list, rules, or private state
- payoff-relevant
- reusable across turns
- named as stable snake_case identifiers
- compact enough for a model to fill without exhausting output tokens

Avoid fields that:

- require hidden implementation details not visible in the prompt
- duplicate the same calculation under several names
- ask the model to simulate a full game tree when a bounded tactical field is enough
- encode the final answer directly without intermediate state

Avoid answer-like field names such as `best_action`, `best_offer_action`, or
`selected_best_response`. Prefer candidate comparison fields:

```text
candidate_offer_values
candidate_placement_hex_values
candidate_guess_or_end_turn_values
```

Field definitions should usually stay short. Do not put long prose definitions
for every field into the runtime prompt unless the game requires it. Prefer a
compact design artifact that records each field's source and purpose, then use
short field names in the prompt:

```text
field_name: source -> purpose
withdrawal_value_now: rules + hand size -> compare stop value to continuation value
```

## Role-Specific Specs

A role-specific spec is the field set and reasoning target for one role, phase,
or information position in the game.

Use role-specific specs when different agents or phases see different
information, have different objectives, or must produce different kinds of
outputs. The spec is chosen during prompt design or prompt compilation; the
runtime model should normally receive the active spec rather than all possible
specs.

Examples:

| Game | Role-specific specs |
| --- | --- |
| Codenames | `spymaster_signal_design`, `operative_signal_interpretation` |
| Two Rooms and a Boom | `leader_hostage_trade`, `nonleader_information_gathering`, `special_role_policy` |
| Santorini | `placement_phase`, `move_build_phase` |
| Air, Land, and Sea | `main_turn_deploy_improvise_withdraw`, `tactical_followup_effect_resolution` |

Each role-specific spec should state:

- role or phase name
- information available to the agent
- objective in that role or phase
- field names to compute
- legal output type: predefined action id, open-ended response, or both
- verifier checks specific to that role or phase

Do not rely on a generic field set when the role changes the information state.
For example, a Codenames spymaster knows private card colors and designs a
signal, while an operative only interprets public clues and visible board
history. These need different fields.

## Action-Space-Specific Programs

An action-space-specific program is the decision procedure for the current shape
of available actions.

Use it when the same game or even the same player can face qualitatively
different action lists. The action list is not just syntax; it often tells the
agent which rule module is active.

Examples:

| Game | Action-space context | Program implication |
| --- | --- | --- |
| Codenames | `submit_clue` | design a one-word clue and number |
| Codenames | `guess_*`, `end_turn` | infer intended word and decide guess vs stop |
| Air, Land, and Sea | `Play ... faceup`, `Play ... facedown`, `Withdraw` | compare deploy, improvise, and outside option |
| Air, Land, and Sea | `Flip`, `Move`, `Return`, `Do nothing` | resolve a tactical effect by target value and risk |
| Santorini | coordinate action ids like `(x, y)` | place pawn for future mobility |
| Santorini | `Move ..., build ...` | check immediate win, block, mobility, and build value |
| Two Rooms and a Boom | choose target player | maximize information gain or team coordination |
| Two Rooms and a Boom | open-ended question/answer | elicit or protect role information |
| Two Rooms and a Boom | hostage trade | move posterior room configuration toward team objective |

For `high_distill`, the compiled decision program should be scoped to this
active action-space context. A single game-level P1/P2/P3 program is usually too
blunt when the available actions switch from communication to trading, or from
normal card play to effect resolution.

For `high_reasoning`, the reasoning workflow should also be scoped to the active
action-space context, even though it remains less rigid than a compiled program.

Recommended design-time record:

```yaml
action_space_context:
  name:
  trigger:
    - action-description or observation pattern used by the prompt builder
  field_computation_targets:
    - compute what is necessary for the active decision
  fields:
    - field_name
  high_reasoning_workflow:
    - ...
  high_distill_program:
    - P0. ...
    - P1. ...
  verifier_checks:
    - ...
```

## Field Categories

Most games need some subset of these:

| Category | Example field names |
| --- | --- |
| Legal action filtering | `legal_action_set`, `legal_output_format`, `openended_command_format` |
| Public state | `board_state`, `score_state`, `payoff_relevant_state_variables` |
| Private information | `own_private_card`, `own_valuation`, `known_private_information` |
| Beliefs | `posterior_beliefs_about_roles`, `beliefs_about_hidden_state` |
| Threats and tactics | `own_immediate_wins`, `opponent_immediate_wins`, `fork_threats` |
| Value comparison | `candidate_action_values`, `expected_value_by_action` |
| Constraints and risk | `risk_or_constraint_checks`, `collision_risk`, `budget_feasibility` |
| Communication | `public_claims_and_conversation`, `information_to_elicit_or_hide` |
| Verification | `verifier_checks`, `legal_output_format` |

## Choosing The Theory Frame

Use `game_theory_mapping.md` to pick the frame:

- Perfect-information board game: extensive game, backward induction, maxmin.
- Hidden-information game: imperfect-information extensive game, beliefs,
  sequential equilibrium logic.
- Auction: Bayesian game, private values, bid shading or dominant strategy.
- Negotiation: bargaining, private preferences, signaling or cheap talk.
- Repeated game: one-shot incentive plus history-dependent retaliation or cooperation.
- One-shot matrix game: strategic game and pure best-response/Nash checks.
- Stochastic stopping game: expected value, risk, continuation value.

## Verifier Layer

Every prompt should require checks that are easy to audit:

- `selected_action` is copied exactly from available action ids.
- Open-ended responses are present when required.
- The action respects hard rules and phase constraints.
- The decision used current observation fields, not outside assumptions.
- Critical tactical checks were performed for the game type.

## Output Length Discipline

Field-register prompts can become too verbose. Keep runtime traces bounded:

- Field values should be one phrase, number, list, or short sentence.
- `candidate_action_values` should compare the strongest 2-3 actions, not every
  legal action unless the legal set is very small.
- `decision_program_trace` should have one entry per program step.
- Do not ask the model to restate full rules in computed fields.
