import json
from pathlib import Path


CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"
MAPPING_PATH = CONFIG_DIR / "game_theory_mapping.json"
SCHEMA_PATH = CONFIG_DIR / "theory_analysis_schema.json"


SCHEMA_BY_GAME = {
    "tictactoe": "perfect_information_extensive_game",
    "connect4": "perfect_information_extensive_game",
    "breakthrough": "perfect_information_extensive_game",
    "nim": "combinatorial_perfect_information_game",
    "pig": "stochastic_dynamic_game",
    "first_sealed_auction": "bayesian_private_value_game",
    "kuhn_poker": "imperfect_information_extensive_game",
    "liars_dice": "imperfect_information_chance_game",
    "negotiation": "bargaining_private_preferences",
    "prisoners_dilemma": "repeated_strategic_game",
}


def load_game_theory_mapping(path=MAPPING_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_theory_analysis_schema(path=SCHEMA_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def mapping_game_name(env_name):
    if env_name == "python_iterated_prisoners_dilemma":
        return "prisoners_dilemma"
    return env_name


def mapped_theory_guidance(env_name, max_steps=None):
    mapping = load_game_theory_mapping()
    game_name = mapping_game_name(env_name)
    game_mapping = mapping.get(game_name, {})
    steps = game_mapping.get("analysis_steps", [])
    if max_steps is not None:
        steps = steps[:max_steps]
    return {
        "concept": game_mapping.get("solution_concept", "General strategic reasoning"),
        "why": game_mapping.get("why_fixed", "Use the relevant strategic structure of the game state."),
        "steps": steps,
        "prompt_state_fields": game_mapping.get("prompt_state_fields", []),
    }


def format_brief_theory_guidance(env_name, max_steps=3, lead="Use this game-theory guide:"):
    guidance = mapped_theory_guidance(env_name, max_steps=max_steps)
    steps = "\n".join(f"- {step}" for step in guidance["steps"])
    fields = "\n".join(f"- {field}" for field in guidance["prompt_state_fields"])
    field_section = f"\nDecision fields to track:\n{fields}\n" if fields else ""
    return f"""{lead}
Theory: {guidance["concept"]}
Why it fits: {guidance["why"]}
{field_section}
Key checks:
{steps}
"""


def schema_key_for_game(game):
    try:
        return SCHEMA_BY_GAME[game]
    except KeyError as exc:
        raise KeyError(f"No theory analysis schema is mapped for game: {game}") from exc


def build_analysis_output(action, rationale, state_fields=None, facts=None, candidate_actions=None):
    """Build the supervised target shape used by theory-guided training records."""
    return {
        "decision_problem": "",
        "strategic_objective": "",
        "critical_facts": facts or [],
        "theory_specific_analysis": state_fields or {},
        "candidate_actions": candidate_actions
        or [
            {
                "action": action,
                "reason": rationale,
                "risk": "",
                "expected_continuation": "",
            }
        ],
        "chosen_action": action,
        "chosen_action_rationale": rationale,
    }


def build_theory_prompt(game, state, legal_actions, state_fields=None, mapping=None, schema_config=None):
    mapping = mapping or load_game_theory_mapping()
    schema_config = schema_config or load_theory_analysis_schema()
    if game not in mapping:
        raise KeyError(f"No game theory mapping exists for game: {game}")

    game_mapping = mapping[game]
    schema_key = schema_key_for_game(game)
    schema = schema_config["schemas"][schema_key]
    output_schema = schema_config["common_output_schema"]

    prompt = f"""You are generating a theory-guided game decision record for training data.

Use the fixed theory mapping below. Do not choose a different theory.

Game: {game_mapping["display_name"]} ({game})
Game type: {game_mapping["game_type"]}
Solution concept: {game_mapping["solution_concept"]}
Osborne/Rubinstein mapping: {json.dumps(game_mapping["osborne_rubinstein_mapping"], ensure_ascii=False)}
Why this mapping is fixed: {game_mapping["why_fixed"]}

Game rule/state summary:
- Required state fields for analysis: {json.dumps(game_mapping["required_state_fields"], ensure_ascii=False)}
- Theory analysis steps: {json.dumps(game_mapping["analysis_steps"], ensure_ascii=False)}
- Output focus: {game_mapping["output_focus"]}

Theory-specific schema:
- Schema key: {schema_key}
- Field purpose: {schema["field_purpose"]}
- Analysis fields to populate when available: {json.dumps(schema["analysis_fields"], ensure_ascii=False)}
- Candidate action fields to consider: {json.dumps(schema["candidate_action_fields"], ensure_ascii=False)}

Current decision input:
- State: {json.dumps(state, ensure_ascii=False)}
- Legal actions: {json.dumps(legal_actions, ensure_ascii=False)}
- Extracted state fields: {json.dumps(state_fields or {}, ensure_ascii=False)}

Return JSON only. The JSON must follow this schema:
{json.dumps(output_schema, indent=2, ensure_ascii=False)}

Rules for the JSON:
- chosen_action must be copied exactly from legal_actions.
- candidate_actions[].action must be copied exactly from legal_actions.
- theory_specific_analysis should use the theory-specific fields above when the current state provides enough information.
- Keep the analysis concise but visible; do not hide the reasoning.
"""

    return {
        "prompt": prompt,
        "game": game,
        "theory_mapping": game_mapping,
        "schema_key": schema_key,
        "analysis_schema": schema,
        "output_schema": output_schema,
    }
