from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"
GAME_THEORY_MAPPING_PATH = CONFIG_DIR / "game_theory_mapping.json"


def load_existing_game_theory_mapping() -> Dict[str, Dict[str, Any]]:
    """Load the repository's existing game-to-theory mapping.

    This is the source of truth for selecting theory handlers. The compiler does
    not recreate a separate game->theory mapping.
    """

    with GAME_THEORY_MAPPING_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def mapping_for_game(game_id: str) -> Dict[str, Any]:
    mapping = load_existing_game_theory_mapping()
    if game_id in mapping:
        return mapping[game_id]
    aliases = {
        "tic_tac_toe": "tictactoe",
        "first_price_auction": "first_sealed_auction",
        "iterated_prisoners_dilemma": "prisoners_dilemma",
        "python_iterated_prisoners_dilemma": "prisoners_dilemma",
    }
    canonical = aliases.get(game_id, game_id)
    return mapping.get(canonical, {})
