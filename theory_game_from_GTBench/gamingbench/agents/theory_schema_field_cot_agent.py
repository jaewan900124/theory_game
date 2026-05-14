from gamingbench.agents.prompt_agent import PromptAgent
from gamingbench.prompts.step_prompts.theory_schema_field_cot_agent import construct_step_prompt


class TheorySchemaFieldCoTAgent(PromptAgent):

    def __init__(self, config, **kwargs):
        super(TheorySchemaFieldCoTAgent, self).__init__(config)
        self.step_prompt_constructor = construct_step_prompt
