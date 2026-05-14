# Game Theory Mapping

Reference: Martin J. Osborne and Ariel Rubinstein, *A Course in Game Theory*, `ref/OsborneRubinsteinMasterpiece.pdf`.

This file maps the benchmark games in this repository to the main game-theoretic models and solution concepts that should be used when designing theory-guided prompts, analyses, or evaluation labels. Page numbers can shift across PDF renderings, so references use chapter and section numbers from the book.

Related prompt-engineering references:

- `ref/README.md`: reference hub and recommended reading order.
- `ref/prompt_field_design.md`: field-register prompt structure for `high_reasoning` and `high_distill`.
- `ref/game_prompt_template.md`: fill-in template for adding a new game prompt mapping.
- `ref/gamebench_prompt_examples.md`: compact examples of reusable GameBench prompt patterns.

## Reference Guide

| Theory concept | Osborne-Rubinstein location | Short explanation | Role in this repo | How it should affect the answer or reasoning |
| --- | --- | --- | --- | --- |
| Strategic game | Ch. 2.1 | A model in which each player chooses an action once, each player's payoff depends on the whole action profile, and choices are analyzed as simultaneous strategic choices. | Core model for one-shot normal-form games, including TMGBench. | Treat the payoff matrix as the authoritative object. Identify players, actions, and payoffs before choosing an outcome. |
| Nash equilibrium | Ch. 2.2 | An action profile where every player's chosen action is a best response to the other players' chosen actions. No player can improve by deviating alone. | Primary answer criterion for TMGBench and many one-shot strategic settings. | Return only action profile(s) that survive mutual best-response checks. Do not choose an outcome only because it has the largest total payoff or looks socially desirable. |
| Strictly competitive games / maxmin reasoning | Ch. 2.5 | A two-player setting where one player's gain is aligned with the other player's loss; security-level and maxmin reasoning become central. | Used for zero-sum-like board games and winner-loser settings. | Reason about preventing the opponent's best outcome as well as improving the agent's own outcome. In pure-action settings, still check Nash/best responses; in mixed settings, consider indifference. |
| Bayesian games | Ch. 2.6 | A strategic game with private information, where players may have types, private values, private cards, or hidden observations. | Used for auctions, poker-like games, dice games, and private-preference negotiation. | Condition reasoning on the agent's private information and beliefs over hidden information. Avoid assuming the opponent's type or value is known unless the game reveals it. |
| Mixed-strategy Nash equilibrium | Ch. 3.1 | A Nash equilibrium where players randomize over actions, often making opponents indifferent among selected actions. | Relevant when no pure equilibrium exists or when bluffing/randomization is strategically necessary. | If the benchmark expects pure action outputs, report no pure selected outcome when no pure NE exists. If mixed strategies are required, solve by indifference rather than selecting a single pure outcome. |
| Rationalizability and dominated actions | Ch. 4 | A reasoning process that removes actions that cannot be justified as best responses, including strictly or weakly dominated actions. | Useful as a reasoning aid for matrix games and sequential choices. | Prune clearly dominated actions before final equilibrium checks, but do not replace the final answer criterion unless the task explicitly asks for dominance-solvability. |
| Extensive games with perfect information | Ch. 6.1 | A sequential game in which players observe previous actions and know the current decision node. | Model for board games and sequential perfect-information games. | Reason from the current state and legal moves. Use observed history and terminal outcomes rather than treating the game as a one-shot matrix. |
| Subgame-perfect equilibrium / backward induction | Ch. 6.2 | A refinement for extensive games requiring optimal play after every possible history; in finite perfect-information games it is found by backward induction. | Primary reasoning principle for finite sequential games such as Tic-Tac-Toe, Connect Four, Breakthrough, and Nim. | Work backward from terminal wins/losses or forced outcomes. Prefer moves that preserve optimal continuation play, not just immediate local gains. |
| Repeated games | Ch. 8 | A model in which a stage game is played repeatedly, allowing history-dependent strategies, rewards, and punishments. | Used for Iterated Prisoner's Dilemma and other multi-round strategic interactions. | Distinguish one-shot incentives from repeated-game incentives. Consider cooperation, retaliation, forgiveness, and end-game effects when history matters. |
| Extensive games with imperfect information | Ch. 11 | A sequential game where some past actions, chance events, or private observations are hidden from at least one player. | Used for Kuhn Poker, Liar's Dice, and hidden-state sequential games. | Track information sets: what the agent knows, what the opponent may know, and which histories are indistinguishable. |
| Sequential equilibrium / perfect Bayesian equilibrium | Ch. 12 | A solution concept for imperfect-information extensive games combining sequential rationality with beliefs about hidden histories or types. | Used for poker, dice, signaling-like negotiation, and sequential private-information games. | Update beliefs from public actions, then choose actions that are optimal under those beliefs. For prompts, explicitly separate evidence, belief update, and action choice. |
| Bargaining games of alternating offers | Ch. 7 | A sequential negotiation model where players propose and respond to offers over time. | Used for negotiation environments with proposal/acceptance structure. | Consider outside options, patience, deadline pressure, and the opponent's likely acceptance threshold. |
| Nash bargaining solution | Ch. 15 | A cooperative bargaining solution that selects an agreement based on surplus division relative to disagreement outcomes. | Useful for analyzing negotiated agreements, but not usually the direct answer rule in non-cooperative simulations. | Use as a fairness or agreement-selection reference when the task asks for a cooperative solution; otherwise keep non-cooperative strategic incentives separate. |

## GTBench Games

| Game | Main model | Primary solution concepts | Reference | Notes for prompts |
| --- | --- | --- | --- | --- |
| Tic-Tac-Toe | Finite extensive game with perfect information; strictly competitive board game | Backward induction, subgame-perfect equilibrium, maxmin reasoning | Ch. 6.1-6.2; Ch. 2.5 | The prompt should emphasize legal move filtering, immediate win/block checks, and game-tree lookahead. |
| Connect Four | Finite extensive game with perfect information; strictly competitive connection game | Backward induction, subgame-perfect equilibrium, maxmin reasoning | Ch. 6.1-6.2; Ch. 2.5 | The practical reasoning target is bounded lookahead: win threats, blocks, forks, and avoiding opponent forced wins. |
| Breakthrough | Finite extensive game with perfect information; strictly competitive board game | Backward induction, subgame-perfect equilibrium, maxmin reasoning | Ch. 6.1-6.2; Ch. 2.5 | The prompt should treat board state and legal moves as sufficient information; evaluate advancement, captures, and race-to-goal threats. |
| Nim | Finite extensive game with perfect information; impartial combinatorial game | Backward induction, subgame-perfect equilibrium; dominated move avoidance | Ch. 6.1-6.2; Ch. 4 | In this implementation the objective is misere-like: avoid taking the final match. Prompts should reason from terminal states backward. |
| Pig | Stochastic extensive game with perfect information plus chance nodes | Dynamic decision-making under risk; expected payoff; stopping problem | Ch. 6.3; Ch. 6.1-6.2 | The key decision is roll vs. stop. Prompts should compare expected gain against bust risk and current score race. |
| First-price sealed-bid auction | Strategic game; Bayesian game when valuations are private | Nash equilibrium, Bayesian Nash equilibrium, bid shading | Ch. 2.3 Example 18.1; Ch. 2.6 | The GTBench prompt says the agent knows its own valuation but not the opponent's. Treat this as private-value Bayesian reasoning. |
| Kuhn Poker | Extensive game with imperfect information | Mixed strategies, sequential equilibrium, belief-based bluff/call reasoning | Ch. 11; Ch. 12; Ch. 3.1 | Private card and hidden third card create information sets. Prompts should reason over card strength, observed betting history, and bluff incentives. |
| Liar's Dice | Extensive game with imperfect information and chance | Bayesian belief updating, mixed strategies, sequential equilibrium | Ch. 11; Ch. 12; Ch. 3.1 | The agent observes its die but not the opponent's die. Prompts should reason over posterior likelihood of bids and strategic bluffing. |
| Negotiation | Bargaining game with private preferences and strategic communication | Alternating-offer bargaining, Nash bargaining, Bayesian/signaling reasoning | Ch. 7; Ch. 15; Ch. 2.6; Ch. 12.3 | The GTBench environment separates proposal and utterance. The utterance stage can be treated as signaling or cheap-talk-like strategic communication. |
| Iterated Prisoner's Dilemma | Repeated strategic game | Stage-game Nash equilibrium, repeated-game cooperation, trigger/tit-for-tat-like punishment | Ch. 2.3 Example 16.2; Ch. 8 | Prompts should distinguish one-shot incentives from history-dependent repeated-game incentives. |

## TMGBench Mapping

TMGBench uses two-player 2x2 payoff matrices. The dataset files are not named by canonical game labels, so the safest mapping is by payoff-structure class rather than filename. For the current TMGBench evaluation scripts, the direct label is the set of pure-strategy Nash equilibria.

| TMGBench case type | Main model | Primary solution concepts | Reference | Answer role | Reasoning instruction |
| --- | --- | --- | --- | --- | --- |
| Any 2x2 one-shot matrix game | Strategic game | Pure-strategy Nash equilibrium via best responses | Ch. 2.1-2.2 | Direct answer criterion | Read the payoff matrix, compute A's best response to each B action, compute B's best response to each A action, and return the mutual best-response cell(s). |
| Matrix game with no pure equilibrium | Strategic game with mixed strategies | Mixed-strategy Nash equilibrium | Ch. 3.1 | Fallback concept, not the current pure-output label | If no cell is a mutual best response, return an empty pure-outcome list under the current benchmark format. Mention mixed equilibrium only as the reason no pure action profile is selected. |
| Prisoner's-Dilemma-like matrix | Strategic game; repeated game only if history is added | Dominant strategy, Nash equilibrium, Pareto tension | Ch. 2.3 Example 16.2; Ch. 8 if repeated | Reasoning aid; final answer remains pure NE | Identify dominant actions if present. Do not choose mutual cooperation or the socially best cell unless it is also stable against unilateral deviation. |
| Coordination / Battle-of-the-Sexes-like matrix | Strategic game | Multiple Nash equilibria, sometimes mixed equilibrium | Ch. 2.2; Ch. 3.1 | Reasoning aid; final answer is all pure NE | If multiple pure equilibria exist, return all of them. Do not apply payoff dominance, risk dominance, or fairness refinements unless the prompt explicitly asks for them. |
| Strictly competitive / zero-sum-like matrix | Strictly competitive strategic game | Maxmin, Nash equilibrium | Ch. 2.5; Ch. 3.1 | Reasoning aid; final answer remains pure NE when using TMGBench labels | Check whether pure mutual best responses exist. If not, do not force a pure winner; the theoretical continuation is mixed/maxmin reasoning. |
| Dominance-solvable matrix | Strategic game | Iterated elimination of dominated actions | Ch. 4.2-4.3 | Reasoning shortcut, not a separate label | Remove strictly dominated actions to simplify reasoning, then still verify the remaining outcome by the pure Nash best-response condition. |

### TMGBench Prompt Template

Use this theory-guided instruction when the goal is to make the model reason with the correct theory while still matching the benchmark label:

````text
This is a two-player 2x2 strategic game. Use the payoff matrix as the authoritative source.

Apply pure-strategy Nash equilibrium reasoning:
1. For each fixed action of player B, identify player A's best response.
2. For each fixed action of player A, identify player B's best response.
3. Select only the action profile(s) where both players are choosing best responses to each other.

Do not select an outcome merely because it maximizes total payoff, seems fair, or is Pareto efficient. If there is no pure-strategy Nash equilibrium, return an empty list under this benchmark's output format.

Finally output:
```python
answer = [("Ax", "By")]
```
````

## Prompting Implications

- For GTBench perfect-information board games, theory-guided prompts should prioritize legal action filtering, terminal threat detection, and backward induction-style lookahead.
- For hidden-information games, prompts should explicitly track private information, public history, beliefs about hidden states, and incentives to randomize or bluff.
- For auctions and negotiation, prompts should avoid treating the problem as pure payoff maximization over known outcomes; the opponent's private value or preference matters.
- For TMGBench, the most robust baseline theory prompt is best-response reasoning for pure-strategy Nash equilibrium, with a fallback note that no pure selected outcome exists when no pure Nash equilibrium exists.

## GameBench Prompt Design Implications

For GameBench-style prompts, the theory mapping is not enough by itself. The
prompt design must also bind the theory model to the game's role structure and
current available-action shape.

- If roles expose different information or objectives, write role-specific
  specs. Example: Codenames spymaster signaling is not the same problem as
  Codenames operative interpretation.
- If action spaces activate different rule modules, write action-space-specific
  programs. Example: Air, Land, and Sea normal deploy/improvise/withdraw actions
  need a different program from Flip/Move/Return tactical effect resolution.
- For each role/action-space context, write field computation targets before
  field names. Targets state what must be computed from rules, observation,
  private/public information, and game theory to solve the current decision.
- The runtime model should compute values for predefined fields; it should not
  invent new field names or silently switch to an unrelated role/action-space
  spec.
- `high_reasoning` should receive field computation targets, active fields, and
  a scoped reasoning workflow.
- `high_distill` should receive field computation targets, active fields, and a
  scoped P0/P1/P2-style compiled decision program.
