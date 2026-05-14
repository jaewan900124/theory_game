from gamingbench.prompts.regex_and_format import get_step_env_regex_and_format
from gamingbench.prompts.theory_prompt_builder import build_theory_prompt


def construct_step_prompt(observation):
    env_name = observation.get("env_name", "")
    regex, format = get_step_env_regex_and_format(env_name)
    mapping_env_name = "prisoners_dilemma" if env_name == "python_iterated_prisoners_dilemma" else env_name
    legal_moves = observation.get("legal_moves", [])
    try:
        theory_package = build_theory_prompt(
            mapping_env_name,
            observation,
            legal_moves,
            {
                "env_name": env_name,
                "legal_moves": legal_moves,
                "previous_actions": observation.get("previous_actions", []),
            },
        )
        theory_guidance = theory_package["prompt"]
    except KeyError:
        theory_guidance = """Use the closest applicable Osborne/Rubinstein concept from strategic games, extensive games, Bayesian games, repeated games, bargaining, or mixed strategies.
Select and apply the solution concept that best matches the current information, timing, uncertainty, and payoff structure."""

    action_reminder = (
        f"Remember, you can only choose one move from the legal actions which is {legal_moves}"
        if len(legal_moves) <= 10
        else "Remember, you can only choose one move from the legal actions."
    )

    prompt = f"""Choose one legal action by applying the fixed theory-guided prompt structure below.

Theory-guided dynamic prompt:
{theory_guidance}

After the analysis, your final output must end with this format strictly:

Theory:
The selected theory concept.

Analysis:
Your concise analysis.

Candidate Check:
Briefly compare the most relevant candidate actions.

Action:
Your action wrapped by <>, i.e., {format}

{action_reminder}
"""
    return {
        "prompt": prompt,
        "regex": regex,
    }
