from __future__ import annotations

import copy
import re
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


class GameAdapter(ABC):
    """Capability-oriented game interface for deterministic field compilation.

    Adapters are intentionally partial: unsupported capabilities return False from
    supports(...) and the compiler emits unavailable fields instead of guessing.
    """

    game_id: str

    def supports(self, capability: str) -> bool:
        return callable(getattr(self, capability, None))

    def state(self) -> Any:
        raise NotImplementedError

    def players(self) -> List[Any]:
        return []

    def current_player(self) -> Optional[Any]:
        return None

    def legal_actions(self, player: Optional[Any] = None) -> List[Any]:
        raise NotImplementedError

    def is_legal_action(self, player: Optional[Any], action: Any) -> bool:
        return action in self.legal_actions(player)


class ObservationGameAdapter(GameAdapter):
    """Adapter over the observation dicts already passed to GamingBench agents."""

    def __init__(self, game_id: str, observation: Optional[Mapping[str, Any]] = None):
        self.game_id = game_id
        self.observation = dict(observation or {})

    def state(self) -> Dict[str, Any]:
        return self.observation

    def current_player(self) -> Optional[Any]:
        return self.observation.get("current_player")

    def legal_actions(self, player: Optional[Any] = None) -> List[str]:
        return list(self.observation.get("legal_moves") or self.observation.get("legal_actions") or [])

    def private_value(self) -> Optional[float]:
        value = self.observation.get("valuation")
        if value is None:
            value = self.observation.get("private_valuation")
        return float(value) if value is not None else None

    def win_probability_by_action(self) -> Optional[Dict[str, float]]:
        value = self.observation.get("win_probability_by_action")
        return dict(value) if isinstance(value, Mapping) else None

    def belief_state(self) -> Optional[Dict[str, Any]]:
        value = self.observation.get("belief_state") or self.observation.get("opponent_value_belief")
        return dict(value) if isinstance(value, Mapping) else None

    def chance_outcomes(self, action: Optional[Any] = None) -> Optional[List[Tuple[Any, float]]]:
        value = self.observation.get("chance_outcomes")
        if isinstance(value, Mapping) and action in value:
            return list(value[action])
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return list(value)
        return None

    def payoff_matrix(self) -> Optional[Dict[str, Any]]:
        value = self.observation.get("payoff_matrix")
        return dict(value) if isinstance(value, Mapping) else None

    def tictactoe_board(self) -> Optional[Dict[str, Any]]:
        if self.game_id not in {"tictactoe", "tic_tac_toe"}:
            return None
        legal = self.legal_actions()
        self_moves = list(self.observation.get("self_moves") or [])
        opponent_moves = list(self.observation.get("opponent_moves") or [])
        state = self.observation.get("state")
        return {
            "self_moves": self_moves,
            "opponent_moves": opponent_moves,
            "legal_actions": legal,
            "state": str(state) if state is not None else None,
        }

    def pig_scores(self) -> Optional[Dict[str, int]]:
        keys = ("self_current_score", "opponent_current_score", "turn_total_score")
        if not all(key in self.observation for key in keys):
            return None
        return {
            "self_score": int(self.observation["self_current_score"]),
            "opponent_score": int(self.observation["opponent_current_score"]),
            "turn_total": int(self.observation["turn_total_score"]),
            "target_score": int(self.observation.get("target_score", 30)),
        }


class MatrixGameAdapter(GameAdapter):
    """Small normal-form adapter used by the compiler and regression tests."""

    def __init__(
        self,
        payoff_matrix: Mapping[Tuple[Any, Any], Tuple[float, float]],
        row_actions: Iterable[Any],
        col_actions: Iterable[Any],
        game_id: str = "matrix_game",
    ):
        self.game_id = game_id
        self._payoff_matrix = dict(payoff_matrix)
        self.row_actions = list(row_actions)
        self.col_actions = list(col_actions)

    def state(self) -> Dict[str, Any]:
        return {"payoff_matrix": copy.deepcopy(self._payoff_matrix)}

    def players(self) -> List[int]:
        return [0, 1]

    def legal_actions(self, player: Optional[Any] = None) -> List[Any]:
        if player == 1:
            return list(self.col_actions)
        return list(self.row_actions)

    def payoff_matrix(self) -> Dict[Tuple[Any, Any], Tuple[float, float]]:
        return copy.deepcopy(self._payoff_matrix)


def parse_numeric_action(action: Any) -> Optional[float]:
    if isinstance(action, (int, float)):
        return float(action)
    match = re.search(r"-?\d+(?:\.\d+)?", str(action))
    if not match:
        return None
    return float(match.group(0))
