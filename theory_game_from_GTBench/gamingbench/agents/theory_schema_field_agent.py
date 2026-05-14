from gamingbench.agents.prompt_agent import PromptAgent
from gamingbench.prompts.step_prompts.theory_schema_field_agent import construct_step_prompt


class TheorySchemaFieldAgent(PromptAgent):

    def __init__(self, config, **kwargs):
        super(TheorySchemaFieldAgent, self).__init__(config)
        self.step_prompt_constructor = construct_step_prompt
