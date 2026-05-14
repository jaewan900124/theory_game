from gamingbench.agents.tot_agent import ToTAgent
from gamingbench.prompts.step_prompts.theory_tot_agent import (
    construct_step_prompt,
    construct_voting_prompt,
)


class TheoryToTAgent(ToTAgent):

    def __init__(self, config, **kwargs):
        super(TheoryToTAgent, self).__init__(config, **kwargs)
        self.step_prompt_constructor = construct_step_prompt
        self.voting_prompt_constructor = construct_voting_prompt
