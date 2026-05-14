from gamingbench.prompts.field_schema_prompt_builder import build_field_usage_program_prompt
from gamingbench.prompts.regex_and_format import get_step_env_regex_and_format


def construct_step_prompt(observation):
    env_name = observation.get("env_name", "")
    legal_moves = observation.get("legal_moves", [])
    mapped_theories = observation.get("mapped_theories")

    prompt_data = build_field_usage_program_prompt(
        env_name,
        legal_moves,
        observation=observation,
        mapped_theories=mapped_theories,
        reasoning_mode="normal",
    )

    try:
        regex, _ = get_step_env_regex_and_format(env_name)
    except NotImplementedError:
        regex = "<.+>"

    return {
        "prompt": prompt_data["prompt"],
        "regex": regex,
    }
