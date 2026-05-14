from gamingbench.agents.prompt_agent import PromptAgent
from gamingbench.prompts.step_prompts.theory_title_agent import construct_step_prompt


class TheoryDetailAgent(PromptAgent):

    def __init__(self, config, **kwargs):
        super(TheoryDetailAgent, self).__init__(config)

        self.step_prompt_constructor = construct_step_prompt
