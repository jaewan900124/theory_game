# Field Engineering Profiles

This directory defines policy boundaries for game-specific field engineering.

The goal is to let us derive fields from:

- game rules,
- publicly or privately observed current state,
- game-theoretic structure,

without turning the compiler into a hidden action solver.

## Profile Meanings

- `low_engineering`:
  State structuring and action-consequence descriptions only.
- `high_engineering`:
  Richer consequence scoring and risk summaries are allowed, but the code still
  must not decide the action directly.

## Hard Constraints

- Fields may describe or score actions.
- Fields may not directly choose an action.
- Do not add `best_action`, `optimal_move`, `recommended_action`, or equivalent.
- Do not hard-code game-theoretic equilibrium prescriptions as direct action
  outputs.
- If a quantity cannot be computed from rules plus current information, mark it
  unavailable instead of guessing.

## Runtime Modes

- `reasoning`:
  Keep only the fields allowed by the selected profile and remove decision
  rules. This isolates field quality from hand-written action selection.
- `distill`:
  Keep only the fields allowed by the selected profile and also keep decision
  rules that depend on those allowed fields. This supports policy-execution or
  distillation experiments.

## Intended Usage

The compiler can enforce these profiles at runtime through
`engineering_profile` plus `engineering_profile_mode`.
