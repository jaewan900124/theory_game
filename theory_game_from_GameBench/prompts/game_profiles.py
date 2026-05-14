GAME_PROFILES = {
    "tic_tac_toe": {
        "style": "board_tactics",
        "predefined_examples": ["(0,0)", "(1,1)"],
    },
    "sea_battle": {
        "style": "simultaneous_tactics",
    },
    "santorini": {
        "style": "board_tactics",
    },
    "pit": {
        "style": "trading",
    },
    "air_land_sea": {
        "style": "card_battle",
    },
    "codenames": {
        "style": "word_association",
        "openended_response_defaults": {
            "submit_clue": "bridge,1",
        },
        "openended_examples": {
            "submit_clue": "bridge,1",
        },
    },
    "arctic_scavengers": {
        "style": "resource_cards",
        "openended_response_defaults": {
            "DIG": "['DIG', ['Refugee']]",
            "DRAW": "['DRAW', ['Refugee']]",
            "HUNT": "['HUNT', ['Refugee']]",
            "TRASH": "['TRASH', ['Refugee']]",
            "HIRE": "['HIRE', ['Medicine'], 'Brawler']",
            "SNIPER": "['SNIPER', 'Refugee']",
            "SABOTEUR": "['SABOTEUR', 'Refugee']",
        },
    },
    "are_you_the_traitor": {
        "style": "social_deduction",
        "openended_response_defaults": {
            "openended": "What is your role?",
        },
    },
    "two_rooms_and_a_boom": {
        "style": "social_deduction",
        "openended_response_defaults": {
            "openended": "What team are you on?",
        },
    },
}


GAME_PROFILE_ALIASES = {
    "air_land_and_sea": "air_land_sea",
}


def canonical_game_id(game_id: str):
    normalized = (game_id or "").strip().lower()
    return GAME_PROFILE_ALIASES.get(normalized, normalized)


def profile_for_game(game_id: str):
    return GAME_PROFILES.get(canonical_game_id(game_id), {})
