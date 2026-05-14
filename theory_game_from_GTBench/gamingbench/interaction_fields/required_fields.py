from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import yaml

from gamingbench.interaction_fields.adapters import GameAdapter
from gamingbench.interaction_fields.schemas import (
    DecisionRule,
    InteractionFieldSpec,
    VerifierCheck,
    unavailable,
)


FIELD_SCHEMA_DIR = Path(__file__).resolve().parents[1] / "configs" / "field_schemas"
ALIASES_PATH = FIELD_SCHEMA_DIR / "aliases.yaml"

FIELD_ALIASES_BY_GAME = {
    "nim": {
        "pile_state": "pile_state_from_legal_actions",
        "phase_classification_by_action": "misere_phase_by_action",
    },
}


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _canonical_game_id(game_id: str) -> str:
    aliases = _load_yaml(ALIASES_PATH).get("game_aliases", {})
    return aliases.get(game_id, game_id)


def load_game_schema(game_id: str) -> Dict[str, Any]:
    path = FIELD_SCHEMA_DIR / "games" / f"{_canonical_game_id(game_id)}.yaml"
    return _load_yaml(path) if path.exists() else {}


def _field(
    adapter: GameAdapter,
    field_id: str,
    spec: Mapping[str, Any],
    value: Any,
    *,
    output_type: Optional[str] = None,
    decision_role: str = "informational",
    operator: str = "compare",
    method: str = "custom_handler",
    steps: Optional[List[str]] = None,
    requirements: Optional[List[str]] = None,
) -> InteractionFieldSpec:
    canonical_game = _canonical_game_id(adapter.game_id)
    if field_id in {
        "immediate_win_columns",
        "immediate_block_columns",
        "fork_creation_actions",
        "fork_block_actions",
    }:
        decision_role = "tactical_set"
        operator = "choose_if_nonempty"
    elif field_id.startswith("heuristic_tiebreak_"):
        decision_role = "heuristic_tiebreaker"
        operator = "minimize" if "distance" in field_id else "compare"
    elif field_id in {
        "acceptance_threshold_model",
        "opponent_preference_belief_model",
        "opponent_card_belief_probabilities",
    }:
        decision_role = "uncertainty_guard"
        operator = "verify"
    elif canonical_game == "kuhn_poker" and field_id in {"my_player_id", "current_actor", "is_my_turn"}:
        decision_role = "interface_required_state"
        operator = "verify"
    return InteractionFieldSpec(
        field_id=field_id,
        source_game_id=adapter.game_id,
        source_theory_id="game_required_schema",
        description=str(spec.get("instruction") or f"Required game-specific field {field_id}."),
        raw_inputs=["state", "legal_actions"],
        requirements=requirements or ["legal_actions"],
        calculation={
            "method": method,
            "steps": steps or [str(spec.get("instruction") or "Compute from current observation when available.")],
            "handler": "required_game_field_enforcer",
        },
        output_type=output_type or str(spec.get("type") or "object"),
        value=value,
        decision_role=decision_role,
        priority=None,
        operator=operator,
        invariants=["Required game-schema fields must be present; use unavailable rather than omitting missing inputs."],
        failure_mode_if_ignored=f"Can ignore required game-specific evidence: {field_id}.",
    )


def _parse_ints(value: Any) -> Optional[List[int]]:
    if value is None:
        return None
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        try:
            return [int(item) for item in value]
        except (TypeError, ValueError):
            return None
    nums = re.findall(r"-?\d+", str(value))
    return [int(num) for num in nums] if nums else None


def _parse_proposal(action: Any) -> Optional[Tuple[int, int, int]]:
    nums = _parse_ints(action)
    if nums is None or len(nums) < 3:
        return None
    return tuple(nums[:3])


def _payoff(allocation: Sequence[int], values: Sequence[int]) -> int:
    return sum(int(a) * int(v) for a, v in zip(allocation, values))


def _negotiation_values(adapter: GameAdapter, obs: Mapping[str, Any], legal: List[str]) -> Dict[str, Any]:
    item_pool = _parse_ints(obs.get("item_pool"))
    values = _parse_ints(obs.get("self_value_vector"))
    latest = _parse_proposal(obs.get("most_recent_proposal"))
    legal_agree = "<Agree>" in legal
    proposal_actions = [action for action in legal if str(action).startswith("<Proposal:")]
    proposal_allocs = {action: _parse_proposal(action) for action in proposal_actions}
    proposal_allocs = {action: alloc for action, alloc in proposal_allocs.items() if alloc is not None}

    output: Dict[str, Any] = {
        "item_pool": item_pool if item_pool is not None else unavailable("item_pool is missing"),
        "self_value_vector": values if values is not None else unavailable("self_value_vector is missing"),
        "current_stage": obs.get("turn_type") or unavailable("turn_type/current stage is missing"),
        "latest_offer_if_any": list(latest) if latest is not None else None,
        "legal_agree_available": legal_agree,
        "opponent_preference_belief_model": unavailable("no deterministic opponent preference model is available"),
    }

    if item_pool is not None and values is not None and latest is not None and legal_agree:
        # In the OpenSpiel negotiation prompt, the opponent's proposal states
        # what the proposer keeps; the accepter receives the complement.
        complement = [pool - offered for pool, offered in zip(item_pool, latest)]
        output["self_payoff_of_latest_offer"] = _payoff(complement, values)
        output["latest_offer_if_any"] = {
            "proposer_allocation": list(latest),
            "my_accept_allocation": complement,
        }
    elif latest is None:
        output["self_payoff_of_latest_offer"] = None
    else:
        output["self_payoff_of_latest_offer"] = unavailable("item_pool/self values or legal <Agree> context is missing")

    if values is not None:
        proposal_payoffs = {
            action: _payoff(alloc, values)
            for action, alloc in proposal_allocs.items()
        }
        output["proposal_payoff_by_candidate"] = proposal_payoffs
    else:
        output["proposal_payoff_by_candidate"] = unavailable("self_value_vector is required to score proposals")

    if values is not None and item_pool is not None:
        latest_payoff = output["self_payoff_of_latest_offer"]
        if isinstance(latest_payoff, (int, float)):
            output["acceptance_threshold_model"] = {
                "latest_offer_payoff": latest_payoff,
                "status": "unavailable",
                "reason": "no deterministic acceptance threshold is specified by the game rules",
            }
        else:
            output["acceptance_threshold_model"] = {
                "latest_offer_payoff": latest_payoff,
                "status": "unavailable",
                "reason": "no accept payoff or deterministic threshold is available",
            }
    else:
        output["acceptance_threshold_model"] = unavailable("item_pool and self_value_vector are required")
    return output


def _parse_column(action: Any) -> Optional[int]:
    match = re.search(r"C(\d+)", str(action))
    return int(match.group(1)) if match else None


def _connect4_values(obs: Mapping[str, Any], legal: List[str]) -> Dict[str, Any]:
    ordered_history = obs.get("public_history") or obs.get("history")
    cols = [_parse_column(action) for action in legal]
    legal_cols = [col for col in cols if col is not None]
    width = max(legal_cols + [7])
    height = 6
    board = [["." for _ in range(width)] for _ in range(height)]

    def drop(col: int, mark: str, target: Optional[List[List[str]]] = None) -> Optional[int]:
        grid = target if target is not None else board
        c = col - 1
        if c < 0 or c >= width:
            return None
        for row in range(height):
            if grid[row][c] == ".":
                grid[row][c] = mark
                return row + 1
        return None

    reconstruction_reliable = False
    if isinstance(ordered_history, Sequence) and not isinstance(ordered_history, (str, bytes)):
        reconstruction_reliable = True
        for item in ordered_history:
            if isinstance(item, Mapping):
                action = item.get("action") or item.get("move")
                actor = str(item.get("player") or item.get("actor") or "")
                mark = "O" if "opponent" in actor.lower() or actor in {"1", "player_1"} else "S"
            else:
                action = item
                mark = "S"
            col = _parse_column(action)
            if col is not None:
                drop(col, mark)
    elif not (obs.get("self_moves") and obs.get("opponent_moves")):
        reconstruction_reliable = True
        for action in obs.get("self_moves") or []:
            col = _parse_column(action)
            if col is not None:
                drop(col, "S")
        for action in obs.get("opponent_moves") or []:
            col = _parse_column(action)
            if col is not None:
                drop(col, "O")
    else:
        column_counts: Dict[int, int] = {}
        for action in list(obs.get("self_moves") or []) + list(obs.get("opponent_moves") or []):
            col = _parse_column(action)
            if col is not None:
                column_counts[col] = column_counts.get(col, 0) + 1
        for action in obs.get("self_moves") or []:
            col = _parse_column(action)
            if col is not None:
                drop(col, "S")
        for action in obs.get("opponent_moves") or []:
            col = _parse_column(action)
            if col is not None:
                drop(col, "O")
        reconstruction_reliable = all(count <= 1 for count in column_counts.values())

    column_heights = {
        f"<C{col}>": sum(1 for row in range(height) if board[row][col - 1] != ".")
        for col in range(1, width + 1)
    }
    playable = {
        f"<C{col}>": column_heights[f"<C{col}>"] + 1
        for col in legal_cols
        if column_heights.get(f"<C{col}>", height) < height
    }

    def has_four(grid: List[List[str]], mark: str) -> bool:
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for row in range(height):
            for col in range(width):
                if grid[row][col] != mark:
                    continue
                for dr, dc in directions:
                    if all(
                        0 <= row + dr * k < height
                        and 0 <= col + dc * k < width
                        and grid[row + dr * k][col + dc * k] == mark
                        for k in range(4)
                    ):
                        return True
        return False

    def after_drop_win(action: str, mark: str, source: Optional[List[List[str]]] = None) -> bool:
        col = _parse_column(action)
        if col is None:
            return False
        grid = [row[:] for row in (source or board)]
        if drop(col, mark, grid) is None:
            return False
        return has_four(grid, mark)

    immediate_win = [action for action in legal if after_drop_win(action, "S")]
    immediate_block = [action for action in legal if after_drop_win(action, "O")]
    dangerous = []
    for action in legal:
        col = _parse_column(action)
        if col is None:
            continue
        grid = [row[:] for row in board]
        if drop(col, "S", grid) is None:
            continue
        if any(after_drop_win(reply, "O", grid) for reply in legal):
            dangerous.append(action)

    center_distance = {
        action: abs((_parse_column(action) or 4) - 4)
        for action in legal
    }
    return {
        "board_reconstruction": {
            "rows_bottom_to_top": ["".join(row) for row in board],
            "self_mark": "S",
            "opponent_mark": "O",
            "reconstruction_reliable": reconstruction_reliable,
            "reliability_reason": "ordered public history available or no mixed-column ambiguity" if reconstruction_reliable else "move order unavailable for columns containing both players",
        },
        "column_heights": column_heights,
        "playable_row_by_column": playable,
        "immediate_win_columns": immediate_win,
        "immediate_block_columns": immediate_block,
        "dangerous_moves_that_enable_opponent_win": dangerous,
        "heuristic_tiebreak_center_distance_by_column": center_distance,
    }


def _kuhn_values(obs: Mapping[str, Any], legal: List[str]) -> Dict[str, Any]:
    raw_card = obs.get("private_card") or obs.get("card") or obs.get("my_card")
    raw_card = str(raw_card) if raw_card is not None else None
    card = {"0": "J", "1": "Q", "2": "K", "j": "J", "q": "Q", "k": "K"}.get(
        raw_card or "",
        raw_card,
    )
    public_history = obs.get("public_history") or obs.get("history") or obs.get("moves") or "".join(
        str(action) for action in (obs.get("self_moves") or []) + (obs.get("opponent_moves") or [])
    )
    history_text = str(public_history or "")
    facing_bet = any(token in history_text.lower() for token in ["bet", "b", "<bet>"]) and "<Pass>" in legal
    rank = {"J": "weak", "Q": "medium", "K": "strong"}.get(card, "unknown")
    deck = ["J", "Q", "K"]
    possible = [item for item in deck if item != card] if card in deck else deck
    current_actor = obs.get("current_actor") or obs.get("current_player")
    is_my_turn = obs.get("is_my_turn")
    player_id = obs.get("my_player_id")
    if player_id is None:
        player_id = obs.get("player_id")
    if player_id is None:
        player_id = obs.get("player_idx")
    return {
        "turn_and_history_perspective": {
            "public_history": public_history or "",
            "interpretation": "In one-round Kuhn poker, Pass is fold when facing a bet and otherwise check; Bet is call when facing a bet and otherwise bet.",
        },
        "my_player_id": player_id if player_id is not None else unavailable("player id is missing"),
        "current_actor": current_actor if current_actor is not None else unavailable("current actor is missing"),
        "is_my_turn": bool(is_my_turn) if is_my_turn is not None else unavailable("current actor/my player id is missing"),
        "public_history": public_history or "",
        "private_card_fields": {"card": card or unavailable("private card is missing"), "known_to_me_only": card is not None},
        "legal_action_context": {
            "facing_bet": facing_bet,
            "<Pass>": "fold" if facing_bet else "check",
            "<Bet>": "call" if facing_bet else "bet",
        },
        "facing_bet": facing_bet,
        "possible_opponent_cards_excluding_private_card": possible,
        "opponent_card_belief_probabilities": unavailable("no deterministic opponent card probability model is available"),
        "hand_strength_class": rank,
    }


def _tictactoe_values(obs: Mapping[str, Any], legal: List[str]) -> Dict[str, Any]:
    self_moves = list(obs.get("self_moves") or [])
    opponent_moves = list(obs.get("opponent_moves") or [])
    self_set = set(self_moves)
    opponent_set = set(opponent_moves)
    legal_set = set(legal)
    lines = [
        ["<C1R1>", "<C2R1>", "<C3R1>"],
        ["<C1R2>", "<C2R2>", "<C3R2>"],
        ["<C1R3>", "<C2R3>", "<C3R3>"],
        ["<C1R1>", "<C1R2>", "<C1R3>"],
        ["<C2R1>", "<C2R2>", "<C2R3>"],
        ["<C3R1>", "<C3R2>", "<C3R3>"],
        ["<C1R1>", "<C2R2>", "<C3R3>"],
        ["<C3R1>", "<C2R2>", "<C1R3>"],
    ]

    def immediate_threats(marks: set, available: set) -> List[str]:
        threats = []
        for line in lines:
            if sum(cell in marks for cell in line) == 2:
                empties = [cell for cell in line if cell in available]
                if len(empties) == 1:
                    threats.append(empties[0])
        return threats

    def fork_actions(marks: set, other_marks: set) -> List[str]:
        forks = []
        for action in legal:
            new_marks = set(marks)
            new_marks.add(action)
            new_available = legal_set - {action}
            threats = set(immediate_threats(new_marks, new_available))
            if len(threats - other_marks) >= 2:
                forks.append(action)
        return forks

    opponent_forks = set(fork_actions(opponent_set, self_set))
    fork_blocks = []
    for action in legal:
        opp_legal_after = legal_set - {action}
        remaining_forks = []
        for opp_action in opp_legal_after:
            new_opp = set(opponent_set)
            new_opp.add(opp_action)
            new_available = opp_legal_after - {opp_action}
            if len(set(immediate_threats(new_opp, new_available))) >= 2:
                remaining_forks.append(opp_action)
        if opponent_forks and not remaining_forks:
            fork_blocks.append(action)

    center = [action for action in legal if action == "<C2R2>"]
    corners = [action for action in legal if action in {"<C1R1>", "<C3R1>", "<C1R3>", "<C3R3>"}]
    edges = [action for action in legal if action not in set(center + corners)]
    return {
        "board_reading": {
            "self_moves": self_moves,
            "opponent_moves": opponent_moves,
            "empty_legal_cells": legal,
        },
        "fork_creation_actions": fork_actions(self_set, opponent_set),
        "fork_block_actions": fork_blocks,
        "heuristic_tiebreak_center_corner_edge": {
            "center": center,
            "corners": corners,
            "edges": edges,
        },
    }


def _parse_nim_action(action: Any) -> Optional[Tuple[int, int]]:
    match = re.search(r"pile:(\d+),\s*take:(\d+)", str(action))
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _nim_values(legal: List[str]) -> Dict[str, Any]:
    parsed = {action: _parse_nim_action(action) for action in legal}
    valid = {action: item for action, item in parsed.items() if item is not None}
    pile_state: Dict[int, int] = {}
    for _, (pile, take) in valid.items():
        pile_state[pile] = max(pile_state.get(pile, 0), take)

    singleton_parity = {}
    for action, (pile, take) in valid.items():
        state = dict(pile_state)
        state[pile] = max(0, state[pile] - take)
        state = {key: value for key, value in state.items() if value > 0}
        singletons = sum(1 for value in state.values() if value == 1)
        singleton_parity[action] = "odd" if singletons % 2 else "even"
    return {
        "misere_rule_check": True,
        "singleton_parity_by_action": singleton_parity,
    }


def _pig_values(obs: Mapping[str, Any]) -> Dict[str, Any]:
    required = ("self_current_score", "opponent_current_score", "turn_total_score")
    if not all(key in obs for key in required):
        return {}
    self_score = int(obs["self_current_score"])
    opponent_score = int(obs["opponent_current_score"])
    turn_total = int(obs["turn_total_score"])
    target = int(obs.get("target_score", 30))
    score_after_stop = self_score + turn_total
    one_roll_expected_turn_total = (5 / 6) * (turn_total + 4)
    return {
        "current_scores": {
            "self_score": self_score,
            "opponent_score": opponent_score,
            "turn_total": turn_total,
        },
        "target_score": target,
        "stop_or_roll_comparison": {
            "<stop>": {
                "score_after_action": score_after_stop,
                "certain": True,
                "bust_loss": 0,
            },
            "<roll>": {
                "approx_expected_score_after_one_roll": self_score + one_roll_expected_turn_total,
                "bust_probability": 1 / 6,
                "bust_loss": turn_total,
            },
        },
    }


def _auction_values(adapter: GameAdapter, legal: List[str]) -> Dict[str, Any]:
    private_value = adapter.private_value() if adapter.supports("private_value") else None
    bids = {action: _parse_ints(action) for action in legal}
    numeric_bids = {action: nums[0] for action, nums in bids.items() if nums}
    if private_value is None:
        return {
            "private_valuation": unavailable("private valuation is missing"),
            "bid_space": numeric_bids,
            "zero_surplus_actions": unavailable("private valuation is required"),
            "positive_surplus_actions": unavailable("private valuation is required"),
            "objective_sensitive_bid_fields": unavailable("private valuation is required"),
            "win_probability_surplus_tradeoff": unavailable("private valuation is required"),
        }
    surplus = {action: float(private_value) - bid for action, bid in numeric_bids.items()}
    win_probs = adapter.win_probability_by_action() if adapter.supports("win_probability_by_action") else None
    return {
        "private_valuation": float(private_value),
        "bid_space": numeric_bids,
        "zero_surplus_actions": [action for action, value in surplus.items() if value == 0],
        "positive_surplus_actions": [action for action, value in surplus.items() if value > 0],
        "objective_sensitive_bid_fields": {
            "surplus_if_win_by_bid": surplus,
            "win_probability_available": win_probs is not None,
            "objective_mismatch_risk": "win-rate scoring can favor higher bids than expected-surplus scoring",
        },
        "win_probability_surplus_tradeoff": unavailable("win_probability_by_action or opponent bid distribution is missing") if not win_probs else {
            action: {
                "win_probability": win_probs.get(action, 0.0),
                "surplus_if_win": surplus.get(action),
                "expected_surplus": win_probs.get(action, 0.0) * surplus.get(action, 0.0),
            }
            for action in legal
            if action in surplus
        },
    }


def _prisoners_dilemma_values(obs: Mapping[str, Any]) -> Dict[str, Any]:
    opponent_history = str(obs.get("opponent_moves", ""))
    actions = [char for char in opponent_history if char.strip()]
    defections = sum(1 for action in actions if action in {"D", "1"})
    cooperations = sum(1 for action in actions if action in {"C", "0"})
    total = len(actions)
    if total == 0:
        pattern = "no_history"
    elif defections == total:
        pattern = "always_defect"
    elif cooperations == total:
        pattern = "always_cooperate"
    else:
        pattern = "mixed_or_noisy"
    return {
        "opponent_recent_actions": actions[-3:],
        "opponent_cooperation_rate": cooperations / total if total else 0,
        "opponent_defection_rate": defections / total if total else 0,
        "pattern_detection": {"pattern": pattern, "sample_size": total},
        "next_action_implications": {
            "<Silent>": {"stage_worst_case": 0, "requires_future_cooperation": True},
            "<Testify>": {"stage_worst_case": 1, "requires_future_cooperation": False},
        },
    }


def _required_values_for_game(adapter: GameAdapter, missing_field_ids: Iterable[str]) -> Dict[str, Any]:
    obs = adapter.state() if isinstance(adapter.state(), Mapping) else {}
    legal = [str(action) for action in adapter.legal_actions()]
    canonical = _canonical_game_id(adapter.game_id)
    if canonical == "negotiation":
        values = _negotiation_values(adapter, obs, legal)
    elif canonical == "connect4":
        values = _connect4_values(obs, legal)
    elif canonical == "kuhn_poker":
        values = _kuhn_values(obs, legal)
    elif canonical == "tictactoe":
        values = _tictactoe_values(obs, legal)
    elif canonical == "nim":
        values = _nim_values(legal)
    elif canonical == "pig":
        values = _pig_values(obs)
    elif canonical == "first_price_auction":
        values = _auction_values(adapter, legal)
    elif canonical == "iterated_prisoners_dilemma":
        values = _prisoners_dilemma_values(obs)
    else:
        values = {}
    return {field_id: values[field_id] for field_id in missing_field_ids if field_id in values}


def _required_decision_rules_for_game(
    canonical_game: str,
    existing_rule_ids: Iterable[str],
) -> List[DecisionRule]:
    existing = set(existing_rule_ids)
    rules: List[DecisionRule] = []
    if canonical_game == "connect4":
        candidate_rules = [
            DecisionRule(
                "connect4_win_now",
                1,
                "immediate_win_columns",
                "choose_if_nonempty",
                "select_from_field",
                "If any legal column wins immediately, choose from immediate_win_columns.",
            ),
            DecisionRule(
                "connect4_block_now",
                2,
                "immediate_block_columns",
                "choose_if_nonempty",
                "select_from_field",
                "If no immediate win exists, block an opponent immediate four-in-a-row.",
            ),
            DecisionRule(
                "connect4_filter_unsafe_enablers",
                3,
                "dangerous_moves_that_enable_opponent_win",
                "filter",
                "discard_field_actions",
                "Remove columns that allow the opponent an immediate winning reply.",
            ),
            DecisionRule(
                "connect4_prefer_center_after_tactics",
                6,
                "heuristic_tiebreak_center_distance_by_column",
                "minimize",
                "select_argmin",
                "If tactics and safety do not decide, prefer the remaining legal column closest to center.",
            ),
        ]
        rules.extend(rule for rule in candidate_rules if rule.rule_id not in existing)
    return rules


def add_required_game_fields(
    adapter: GameAdapter,
    fields: List[InteractionFieldSpec],
    rules: List[DecisionRule],
    checks: List[VerifierCheck],
) -> Tuple[List[InteractionFieldSpec], List[DecisionRule], List[VerifierCheck]]:
    schema = load_game_schema(adapter.game_id)
    required = schema.get("required_derived_fields") or {}
    if not required:
        return fields, rules, checks

    canonical = _canonical_game_id(adapter.game_id)
    alias_map = FIELD_ALIASES_BY_GAME.get(canonical, {})
    existing = {field.field_id for field in fields}
    aliased_existing = set(existing)
    for required_id, existing_id in alias_map.items():
        if existing_id in existing:
            aliased_existing.add(required_id)
    missing = [field_id for field_id in required if field_id not in aliased_existing]
    computed = _required_values_for_game(adapter, missing)
    added = []
    for field_id in missing:
        spec = required[field_id] or {}
        value = computed.get(field_id, unavailable(f"required field '{field_id}' has no deterministic computer yet"))
        output_type = "unavailable" if isinstance(value, dict) and value.get("status") == "unavailable" else spec.get("type")
        added.append(_field(adapter, field_id, spec, value, output_type=output_type))

    if added:
        checks = checks + [
            VerifierCheck(
                "required_game_fields_present",
                None,
                "all game schema required_derived_fields are present as computed or unavailable fields",
                True,
            )
        ]
    required_rules = _required_decision_rules_for_game(
        canonical,
        [rule.rule_id for rule in rules],
    )
    return fields + added, rules + required_rules, checks
