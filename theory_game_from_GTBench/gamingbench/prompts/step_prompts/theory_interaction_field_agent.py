from gamingbench.interaction_fields import compile_from_observation
from gamingbench.prompts.regex_and_format import get_step_env_regex_and_format


def construct_step_prompt(
    observation,
    engineering_profile=None,
    engineering_profile_mode="reasoning",
    strict=False,
):
    env_name = observation.get("env_name", "")
    prompt_data = compile_from_observation(
        env_name,
        observation,
        engineering_profile=engineering_profile,
        engineering_profile_mode=engineering_profile_mode,
        strict=strict,
    )

    try:
        regex, _ = get_step_env_regex_and_format(env_name)
    except NotImplementedError:
        regex = "<.+>"

    return {
        "prompt": prompt_data.small_model_prompt,
        "regex": regex,
    }
