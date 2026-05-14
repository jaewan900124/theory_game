from gamingbench.agents.prompt_agent import PromptAgent
from gamingbench.prompts.step_prompts.theory_detail_cot_agent import construct_step_prompt


class TheoryDetailCoTAgent(PromptAgent):

    def __init__(self, config, **kwargs):
        super(TheoryDetailCoTAgent, self).__init__(config)

        self.step_prompt_constructor = construct_step_prompt
