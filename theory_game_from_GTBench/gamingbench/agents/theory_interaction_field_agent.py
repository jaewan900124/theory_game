from gamingbench.agents.prompt_agent import PromptAgent
from gamingbench.prompts.step_prompts.theory_interaction_field_agent import construct_step_prompt


class TheoryInteractionFieldAgent(PromptAgent):

    def __init__(self, config, **kwargs):
        super(TheoryInteractionFieldAgent, self).__init__(config)
        self.engineering_profile = getattr(config, "engineering_profile", None)
        self.engineering_profile_mode = getattr(
            config, "engineering_profile_mode", "reasoning"
        )
        self.engineering_profile_strict = bool(
            getattr(config, "engineering_profile_strict", False)
        )
        self.step_prompt_constructor = lambda observation: construct_step_prompt(
            observation,
            engineering_profile=self.engineering_profile,
            engineering_profile_mode=self.engineering_profile_mode,
            strict=self.engineering_profile_strict,
        )
