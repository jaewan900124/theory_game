from gamingbench.prompts.regex_and_format import get_step_env_regex_and_format
from gamingbench.prompts.theory_prompt_builder import format_brief_theory_guidance


def construct_step_prompt(observation):
    env_name = observation.get("env_name", "")
    regex, format = get_step_env_regex_and_format(env_name)
    legal_moves = observation.get("legal_moves", [])
    theory_guidance = format_brief_theory_guidance(
        env_name,
        max_steps=4,
        lead="Use the mapped game-theory concept while reasoning:",
    )

    if len(legal_moves) <= 10:
        action_reminder = (
            "Remember, you can only choose one move from the legal actions "
            f"which is {legal_moves}"
        )
    else:
        action_reminder = "Remember, you can only choose one move from the legal actions."

    prompt = f"""First think about your current situation, then choose one legal action to set up advantages.

{theory_guidance}
Use the checks above in your thought, then commit to one valid action.

Your output must be in the following format strictly:

Thought:
Your concise game-theory-guided thought.

Action:
Your action wrapped by <>, i.e., {format}

{action_reminder}
"""
    return {
        "prompt": prompt,
        "regex": regex,
    }
