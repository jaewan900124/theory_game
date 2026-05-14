# Theory Game Prompt References

This directory is the reference hub for building theory-guided prompts across
GameBench, GTBench, and TMGBench style games.

## Start Here

Use these markdown files in this order when adding or revising a prompt:

1. `game_theory_mapping.md`
   - Maps benchmark game families to game-theoretic models and solution concepts.
   - Use this first to decide whether the game is strategic, extensive-form,
     Bayesian, repeated, stochastic, bargaining, or mixed-strategy.

2. `prompt_field_design.md`
   - Defines the field-register prompt pattern used by GameBench
     `high_reasoning` and `high_distill`.
   - Use this to decide which fields belong in the prompt and how the two modes
     should differ.

3. `game_prompt_template.md`
   - Fill-in template for adding a new game to a prompt mapping.
   - Copy this structure into the relevant prompt code or a design note before
     implementation.

4. `gamebench_prompt_examples.md`
   - Compact examples of current GameBench prompt mappings.
   - Use this for style and field naming consistency.

## Source PDFs

The PDFs in this directory are source material. Prefer markdown summaries for
prompt engineering, and use PDFs only when a mapping or theory claim needs to be
checked against the original text.

| File | Role |
| --- | --- |
| `OsborneRubinsteinMasterpiece.pdf` | Main game theory reference for strategic, Bayesian, extensive, repeated, and bargaining games. |
| `2214_GameBench_Evaluating_Stra.pdf` | GameBench paper and game descriptions. |
| `2402.12275v3.pdf`, `2402.12348v2.pdf`, `2403.11807v7.pdf`, `2510.04542v1.pdf`, `5145_Competing_Large_Language_.pdf`, `NeurIPS-2024-amortized-planning-with-large-scale-transformers-a-case-study-on-chess-Paper-Conference.pdf`, `1-s2.0-S0925231226004030-main.pdf` | Supporting references for LLM game playing, planning, strategic reasoning, or benchmark context. |

## Prompt-Building Rule Of Thumb

Do not start from generic chain-of-thought instructions. Start from the game
model:

1. Identify players, legal actions, payoff/objective, information structure,
   timing, chance, and hidden state.
2. Identify role-specific specs: each role or phase that sees different
   information or has a different objective must get its own field set.
3. Identify action-space-specific programs: when available actions change from
   clueing to guessing, deploying to resolving an effect, placement to
   move-build, or speaking to trading, the decision program must change too.
4. Write field computation targets: short statements of what must be computed
   to solve the current role/action-space decision.
5. Convert those targets into a field register with observable state fields.
6. For `high_reasoning`, provide field targets, active fields, and a reasoning workflow.
7. For `high_distill`, provide field targets, active fields, and an explicit P0/P1/P2-style compiled
   decision program.
8. Always require exact legal action ids and a verifier layer.

## Design Boundary

Field design is a design-time task. A human or Codex-style design agent should
read the game rules, implementation, observations, available action shapes, and
game-theoretic frame, then write the role-specific specs,
action-space-specific programs, field computation targets, and active field
registers before experiments.

Runtime game-playing models should not invent new fields. They should receive a
predefined field register, compute current field values from the observation and
available actions, and select a legal action. When possible, the prompt builder
should provide only the active role/action-space spec instead of asking the
runtime model to choose among many candidate specs.
