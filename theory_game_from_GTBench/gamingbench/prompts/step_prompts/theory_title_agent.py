from gamingbench.prompts.regex_and_format import get_step_env_regex_and_format
from gamingbench.prompts.theory_prompt_builder import format_brief_theory_guidance


def construct_step_prompt(observation):
    env_name = observation.get("env_name", "")
    regex, format = get_step_env_regex_and_format(env_name)
    theory_guidance = format_brief_theory_guidance(
        env_name,
        max_steps=4,
        lead="Use the mapped game-theory concept as guidance:",
    )

    prompt = f"""You must choose an legal action to set up advantages.

{theory_guidance}
Before choosing, silently use these checks to compare legal actions.

Your output must be in the following format:

Action:
Your action wrapped with <>, {format}

Please return your answer without explanation!
"""
    return {
        "prompt": prompt,
        "regex": regex,
    }
