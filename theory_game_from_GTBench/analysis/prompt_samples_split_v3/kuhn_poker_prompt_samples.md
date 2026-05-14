# kuhn_poker Prompt Samples

## Source

- `source_file`: `experiments/qwen3_14b_interaction_field_think_vs_baseline_allgames_10_split_v3/kuhn_poker/theory_interaction_field_agent_qwen3-14b-ollama-think_prompt_agent_qwen3-14b-ollama-think.jsonl`
- `jsonl_rows`: `10`

---

## Interaction Field Prompt

### Metadata

- `jsonl_line`: `1`
- `step_index`: `1`
- `agent`: `TheoryInteractionFieldAgent`
- `move`: `<Bet>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: `{\n  "action": "<Bet>",\n  "used_rule": "P0",\n  "used_fields": [\n    "legal_actions",\n    "legal_action_context",\n    "possible_opponent_cards_excluding_private_card"\n  ],\n  "verifier_passed": true\n}`

### Prompt

```text
Kuhn poker is a simple model zero-sum two-player imperfect-information game, amenable to a complete game-theoretic analysis. In Kuhn poker, the deck includes only three playing cards: a King (K), a Queen (Q), and a Jack (J).
One card is dealt to each player, and the third is put aside unseen. The players take turns either <Bet> to match the bet raised by the opponent or <Pas> to conceds the game.
If a player bets, the other player must either call the bet by matching it or fold by conceding the game. If both players pass, the game is over, and the player with the higher-ranking card wins. The card rankings are as follows: King (K) > Queen (Q) > Jack (J).

You are playing Kuhn poker with the opponent. The actions are denoted by <Bet> and <Pass>.
In this match, your card is King (K).

Your legal moves are: <Pass>, <Bet>.
You are not explaining theory.
You are executing a decision program.

Game:
kuhn_poker

Mapped theory:
belief_weighted_expected_utility

Current state:
{"card": "2", "moves": null, "player_idx": 0, "state": "2 1", "openspiel_legal_actions": [0, 1], "legal_moves": ["<Pass>", "<Bet>"], "env_name": "kuhn_poker"}

Legal actions:
["<Pass>", "<Bet>"]

Computed fields:
- belief_state:
  Role: informational
  Operator: verify
  Calculation: Read provided belief_state. If absent, return unavailable instead of inventing beliefs.
  Value: unavailable
  Reason: belief_state/probability model is missing

- turn_and_history_perspective:
  Role: informational
  Operator: compare
  Calculation: Interpret public betting history from my current player's perspective.
  Value:
    public_history: 
    interpretation: Pass is fold when facing a bet, otherwise check; Bet is bet/call depending on history.

- my_player_id:
  Role: interface_required_state
  Operator: verify
  Calculation: My player index or role if provided.
  Value: unavailable
  Reason: player id is missing

- current_actor:
  Role: interface_required_state
  Operator: verify
  Calculation: Who is to act now.
  Value: unavailable
  Reason: current actor is missing

- is_my_turn:
  Role: interface_required_state
  Operator: verify
  Calculation: Whether the current actor is me.
  Value: unavailable
  Reason: current actor/my player id is missing

- public_history:
  Role: informational
  Operator: compare
  Calculation: Public pass/bet history exactly as observed.
  Value:
    ""

- private_card_fields:
  Role: informational
  Operator: compare
  Calculation: My known private card and rank class.
  Value:
    card: 2
    known_to_me_only: True

- legal_action_context:
  Role: informational
  Operator: compare
  Calculation: Meaning of Pass/Bet in this information set: check/bet/fold/call.
  Value:
    facing_bet: False
    <Pass>: check
    <Bet>: bet

- facing_bet:
  Role: informational
  Operator: compare
  Calculation: Whether I am responding to an opponent bet.
  Value:
    false

- possible_opponent_cards_excluding_private_card:
  Role: informational
  Operator: compare
  Calculation: Possible opponent cards after excluding my known private card.
  Value:
    ["J", "Q", "K"]

- opponent_card_belief_probabilities:
  Role: uncertainty_guard
  Operator: verify
  Calculation: Probability model over opponent cards if provided; unavailable otherwise.
  Value: unavailable
  Reason: no deterministic opponent card probability model is available

- hand_strength_class:
  Role: informational
  Operator: compare
  Calculation: Weak, medium, or strong within Kuhn deck.
  Value:
    "unknown"

Decision program:
P0. Choose only from legal_actions.

P1. If tied, use the listed tie-break rule if available; otherwise choose the first tied legal action.
P2. Do not use unavailable fields as if they were computed.
P3. Before final answer, run verifier checks.

Verifier:
- no_hallucinated_hidden_state: belief-dependent fields unavailable when no belief model exists [field: belief_state]
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
- `move`: `<Bet>`
- `model`: `qwen3:14b_think`
- `prompt_type`: `move`
- `llm_output`: ``

### Prompt

```text
Kuhn poker is a simple model zero-sum two-player imperfect-information game, amenable to a complete game-theoretic analysis. In Kuhn poker, the deck includes only three playing cards: a King (K), a Queen (Q), and a Jack (J).
One card is dealt to each player, and the third is put aside unseen. The players take turns either <Bet> to match the bet raised by the opponent or <Pas> to conceds the game.
If a player bets, the other player must either call the bet by matching it or fold by conceding the game. If both players pass, the game is over, and the player with the higher-ranking card wins. The card rankings are as follows: King (K) > Queen (Q) > Jack (J).

You are playing Kuhn poker with the opponent. The actions are denoted by <Bet> and <Pass>.
In this match, your card is Queen (Q).
Here are the past moves in this match:
In the 1st round, you choose to <Bet>;

Your legal moves are: <Pass>, <Bet>.
You must choose an legal action to set up advantages.

Your output must be in the following format:

Action:
Your action wrapped with <>, <Pass|Bet> e.g., <Pass>

Please return your answer without explanation!
```
