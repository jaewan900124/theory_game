from gamingbench.agents.prompt_agent import PromptAgent
from gamingbench.prompts.step_prompts.theory_agent import construct_step_prompt


class TheoryAgent(PromptAgent):

    def __init__(self, config, **kwargs):
        super(TheoryAgent, self).__init__(config)

        self.step_prompt_constructor = construct_step_prompt
