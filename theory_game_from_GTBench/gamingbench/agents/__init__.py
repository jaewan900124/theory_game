
from gamingbench.agents.prompt_agent import PromptAgent
from gamingbench.agents.cot_agent import CoTAgent
from gamingbench.agents.sc_cot_agent import SCCoTAgent
from gamingbench.agents.tot_agent import ToTAgent
from gamingbench.agents.theory_agent import TheoryAgent
from gamingbench.agents.theory_title_agent import TheoryTitleAgent
from gamingbench.agents.theory_detail_agent import TheoryDetailAgent
from gamingbench.agents.theory_detail_cot_agent import TheoryDetailCoTAgent
from gamingbench.agents.theory_field_cot_agent import TheoryFieldCoTAgent
from gamingbench.agents.theory_field_program_agent import TheoryFieldProgramAgent
from gamingbench.agents.theory_interaction_field_agent import TheoryInteractionFieldAgent
from gamingbench.agents.theory_schema_field_agent import TheorySchemaFieldAgent
from gamingbench.agents.theory_schema_field_cot_agent import TheorySchemaFieldCoTAgent
from gamingbench.agents.theory_tot_agent import TheoryToTAgent
from gamingbench.agents.random_agent import RandomAgent
from gamingbench.agents.titfortat_agent import TitForTatAgent

try:
    from gamingbench.agents.mcts_agent import MCTSAgent
except ModuleNotFoundError:
    MCTSAgent = None
