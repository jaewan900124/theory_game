from gamingbench.prompts.regex_and_format import get_step_env_regex_and_format
from gamingbench.prompts.theory_prompt_builder import format_brief_theory_guidance


def _get_stop_signs(env_name):
    return ["Action:", None]


def _guidance_text(env_name):
    return format_brief_theory_guidance(
        env_name,
        max_steps=4,
        lead="Use this mapped game-theory guide while building the thought tree:",
    )


def construct_step_prompt(observation):
    env_name = observation.get("env_name", "")
    regex, format = get_step_env_regex_and_format(env_name)
    stop_signs = _get_stop_signs(env_name)
    guidance = _guidance_text(env_name)

    prompt = f"""First think about your current situation, then choose one legal action to set up advantages.

{guidance}
When thinking, compare candidate legal actions using the concept above and reject actions with weak continuation value.

Your output should be of the following format:

Thought:
Your concise game-theory-guided thought.

Action:
Your action wrapped with <>, e.g., {format}
"""

    return {
        "prompt": prompt,
        "regex": regex,
        "stop_signs": stop_signs,
    }


def construct_voting_prompt(observation):
    env_name = observation.get("env_name", "")
    guidance = _guidance_text(env_name)
    prompt = f"""Given an instruction and several choices, decide which choice is most promising.

{guidance}
Analyze each choice by whether it follows the mapped theory and leads to the strongest strategic position. Conclude in the last line "The best choice is {{s}}", where s is the integer id of the choice."""
    return {
        "prompt": prompt,
        "regex": ".*best choice is .*(\\d+).*",
    }
