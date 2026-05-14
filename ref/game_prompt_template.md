# New Game Prompt Mapping Template

Use this template when adding a new game to a theory-guided prompt system.
The same information can be stored as markdown first and then converted into
the prompt mapping code.

## Game Identity

```yaml
game_id:
display_name:
implementation_path:
rules_source:
```

## Theory Mapping

```yaml
game_type:
solution_concept:
reference_basis:
  - Game implementation:
  - Benchmark paper or rulebook:
  - Theory reference:
osborne_rubinstein_mapping:
```

Questions to answer:

- Is the game simultaneous or sequential?
- Is information perfect, imperfect, private, or public?
- Are there chance nodes or stochastic outcomes?
- Is the objective zero-sum, team-based, cooperative, bargaining-based, or score-maximizing?
- Does the model need beliefs over hidden state or opponent type?
- Does the answer require a predefined action id, open-ended text, or both?
- Which roles or phases expose different information or objectives?
- Which available-action shapes indicate a different rule module or decision procedure?

## Field Register

Base fields:

```yaml
required_state_fields:
  - players_and_roles
  - legal_action_set
  - information_state_public_private
  - objective_or_payoff
  - payoff_relevant_state_variables
  - candidate_action_values
  - risk_or_constraint_checks
```

Role or phase-specific fields:

```yaml
role_specific_specs:
  role_or_phase_name:
    trigger:
      - observation or action-space pattern
    information_available:
      - public/private state visible to this role
    objective:
    output_type: predefined|openended|mixed
    field_computation_targets:
      - Compute what must be figured out for this role or phase.
    fields:
      - field_name
    verifier_checks:
      - role-specific check
```

Field checklist:

- Every field is observable from the current prompt or explicitly marked
  unavailable.
- Every active context has field computation targets that explain why the active
  fields are needed.
- Fields may be state summaries, belief estimates, constraints, risks,
  candidate-value comparisons, or output-format guards. They do not all need to
  be numeric scores.
- Every role/phase field set has a clear design-time trigger.
- Field names are stable snake_case.
- Field names should be intermediate computations, not final-answer aliases
  such as `best_action` or `selected_best_response`.
- No field requires a hidden full simulation unless the game state makes that
  feasible.
- The runtime model should not invent field names or choose from unrelated role
  specs when the prompt builder can provide the active spec.

## Action-Space-Specific Programs

Define a separate action-space program when the available actions imply a
different rule module.

```yaml
action_space_programs:
  context_name:
    trigger:
      - action ids or descriptions that identify this context
    active_role_specs:
      - role_or_phase_name
    additional_fields:
      - field_name
    field_computation_targets:
      - Compute the action-space-specific values, beliefs, risks, or constraints.
    high_reasoning_workflow:
      - Compute the active fields.
      - Compare the strongest legal candidate actions for this context.
      - Choose the best legal action.
    high_distill_program:
      - P0. Choose only from current available action ids.
      - P1. Apply the context-specific strategic filter.
      - P2. Compare remaining actions by payoff, continuation value, and risk.
      - P3. Select the verifier-passing best response.
    verifier_checks:
      - selected_action belongs to the current action-space context
```

Common action-space splits:

- clue submission vs guessing or ending turn
- card deployment/improvisation/withdrawal vs tactical effect resolution
- pawn placement vs move-build turns
- target selection vs question generation vs answer generation vs hostage trade
- normal movement vs interrupt/reaction windows

## high_reasoning Section

Use this mode when the model should reason from fields without an explicit
compiled decision program.

```yaml
decision_workflow:
  - Extract legal action ids from Available actions.
  - Compute the active role-specific and action-space-specific fields.
  - Compare the strongest legal candidate actions for the active context.
  - Choose the action with the strongest best-response case.
  - Run verifier checks.
```

Prompt should include:

- `Field register`
- `Field computation targets`
- `Reasoning workflow`
- `Verifier checks`

Prompt should not include:

- `Compiled decision program`

## high_distill Section

Use this mode when the model should execute a compact decision program.

```yaml
distill_rules_for_active_action_space:
  - P1. Keep only legal actions from the provided action ids.
  - P2. Apply the active role/action-space strategic filter.
  - P3. Compare remaining actions by payoff, continuation value, and risk.
  - P4. Break ties by verifier-passing best-response strength.
```

Prompt should include:

- `Field register`
- `Field computation targets`
- `Compiled decision program`
- `Verifier checks`

Trace should include:

- `decision_program_trace`
- `used_rule`
- `verifier_passed`

## Verifier Checks

```yaml
verifier_checks:
  - selected_action is copied exactly from the available action ids
  - openended_response is present if selected action requires free text
  - action respects phase-specific legal constraints
  - decision uses current observation and game rules
```

Add game-specific checks:

- Board games: selected square/cell/move is legal, immediate win/block checked.
- Hidden information: private state and public evidence separated, beliefs updated.
- Auctions: bid is feasible, private value handled correctly.
- Negotiation: offer format valid, private preferences and acceptance risk considered.
- Simultaneous movement: collision, occupation, and shooting/exposure risks checked.
- Communication games: claim/question supports role objective and does not leak
  private information unless strategically justified.

## Implementation Checklist

Before running experiments:

- Game-theoretic frame has been checked against the game rules and implementation.
- Role-specific specs are defined for roles/phases with different information,
  objectives, or output formats.
- Action-space-specific programs are defined for action lists that activate
  different rule modules.
- Field computation targets are defined for every active context.
- The prompt builder either selects the active role/action-space spec or gives
  an explicit, auditable selection rule.
- Prompt compiles/imports.
- Sample prompt contains `Field register`.
- `high_reasoning` contains `Reasoning workflow` and not `Compiled decision program`.
- `high_distill` contains `Compiled decision program`.
- Parser accepts `field_application` and `selected_action`.
- One short runtime smoke test produces transcript traces with the new schema.
