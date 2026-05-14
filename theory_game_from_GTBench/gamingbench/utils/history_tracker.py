import json
from collections import defaultdict


class Query:
    def __init__(self, messages: list, prompt_type: str, llm_output: list, token_size: int = 0) -> None:

        assert prompt_type in ['move', 'plan', 'vote']
        self.messages = messages
        self.prompt_type = prompt_type
        self.llm_output = llm_output
        self.token_size = token_size
        pass

    def set_token_size(self, num):
        self.token_size = num

    def to_dict(self):
        return {"messages": self.messages,
                "prompt_type": self.prompt_type,
                "llm_output": self.llm_output,
                "token_size": self.token_size}

    def append_llm_output(self, output: str):
        self.llm_output.append(output)

    def __json__(self):
        return self.to_dict()


class Step:
    def __init__(self, agent: str, observation: str = "", move: str = "") -> None:
        self.agent = agent                       # agents name
        self.observation = observation           # observation
        self.move = move
        self.queries = []                          # should be list of str

    def set_observation(self, observation):
        self.observation = observation

    def set_model_name(self, name):
        self.model_name = name

    def set_move(self, move):
        self.move = move

    def add_query(self, query):
        self.queries.append(query)
        pass

    def get_token_size(self):
        self.token_size = sum([q.token_size for q in self.queries])
        return self.token_size

    def to_dict(self):
        return {"agent": self.agent,
                "observation": self.observation,
                "move": self.move,
                "queries": [q.to_dict() for q in self.queries],
                "token_size": self.get_token_size(),
                "model_name": self.model_name
                }

    def __json__(self):
        return self.to_dict()


class GameMatch:

    def __init__(self) -> None:
        self.winner = ""   # the name of the agent
        self.steps = []
        self.status = "Normal"
        self.agents_at_fault = []
        self.agents = set()
        self.agent_order = []
        self.model_order = []
        self.winner_score = 0
        self.loser_score = 0
        self.scores = {}
        pass

    def set_winner(self, winner):
        self.winner = winner

    def set_player_order(self, agent_order, model_order):
        self.agent_order = list(agent_order)
        self.model_order = list(model_order)

    def set_scores(self, scores):
        self.scores = dict(scores)

    def reset(self):
        '''
        This function will clear all steps and agents
        '''
        self.steps.clear()
        self.winner = ""

    def add_step(self, step):
        self.steps.append(step)
        self.agents.add(step.agent)

    def get_steps_by_agent(self, agent_name):
        steps = [step for step in self.steps if step.agent == agent_name]
        return steps
        pass

    def get_token_size(self):
        self.token_size = sum([s.get_token_size() for s in self.steps])
        return self.token_size

    def get_moves_by_agent(self, agent_name):
        steps = self.get_steps_by_agent(agent_name)
        return [s.move for s in steps]

    def to_dict(self):
        return {"winner": self.winner,
                "agents": list(self.agents),
                "agent_order": self.agent_order,
                "model_order": self.model_order,
                "starting_agent": self.steps[0].agent if self.steps else "",
                "steps": [s.to_dict() for s in self.steps],
                "status": self.status,
                "agents_at_fault": self.agents_at_fault,
                "scores": self.scores,
                "winner_score": self.winner_score,
                "loser_score": self.loser_score,
                "token_size": self.get_token_size()}

    def __json__(self):
        return self.to_dict()


class HistoryTracker:
    def __init__(self) -> None:
        self.game_config = {}
        self.matches = []
        self.agents = set()
        self.agents_config = []
        self.models_config = []
        pass

    def get_win_rate(self):

        valid_match_num = 0
        agents_win_match = defaultdict(lambda: 0)

        for m in self.matches:
            if m.status == "Normal":
                valid_match_num += 1
                if m.winner != "":
                    agents_win_match[m.winner] += 1
        if valid_match_num != 0:
            for key, val in agents_win_match.items():
                agents_win_match[key] = val/valid_match_num
        else:
            for key, val in agents_win_match.items():
                agents_win_match[key] = 0

        return dict(agents_win_match)

    def get_payoff_summary(self):
        summary = defaultdict(lambda: {
            "total_payoff": 0.0,
            "matches": 0,
        })

        for match in self.matches:
            if match.status != "Normal":
                continue

            scores = getattr(match, "scores", None)
            if scores:
                for agent, score in scores.items():
                    summary[agent]["total_payoff"] += score
                    summary[agent]["matches"] += 1
                continue

            if len(match.agent_order) != len(match.model_order):
                continue

            participants = [
                f"{agent}_{model}"
                for agent, model in zip(match.agent_order, match.model_order)
            ]
            for participant in participants:
                if match.winner == "":
                    score = 0.0
                elif participant == match.winner:
                    score = match.winner_score
                else:
                    score = match.loser_score
                summary[participant]["total_payoff"] += score
                summary[participant]["matches"] += 1

        output = {}
        for agent, values in sorted(summary.items()):
            matches = values["matches"]
            output[agent] = {
                "total_payoff": values["total_payoff"],
                "average_payoff": values["total_payoff"] / matches if matches else 0.0,
                "matches": matches,
            }
        return output

    def get_average_payoff(self):
        return {
            agent: values["average_payoff"]
            for agent, values in self.get_payoff_summary().items()
        }

    def get_all_matches(self):
        return self.matches

    def set_game_config(self, config):
        self.game_config = config

    def add_agents_config(self, config):
        self.agents_config.append(config)

    def add_models_config(self, config):
        self.models_config.append(config)

    def add_match(self, match):
        self.matches.append(match)
        for agent in match.agents:
            self.agents.add(agent)

    def get_token_size(self):
        self.token_size = sum([s.get_token_size() for s in self.matches])
        return self.token_size

    def to_dict(self):
        return {
            "game_config": self.game_config,
            "agents_config": self.agents_config,
            "models_config": self.models_config,
            "win_rate": self.get_win_rate(),
            "average_payoff": self.get_average_payoff(),
            "payoff_summary": self.get_payoff_summary(),
            "matches": [m.to_dict() for m in self.matches],
            "token_size": self.get_token_size()}

    def __json__(self):
        return self.to_dict()

    def clear(self):
        '''
        This function will clear all steps and agents
        '''
        self.matches.clear()
        self.agents.clear()

    def save_as_json(self, path):
        '''
        outout a json file containing agents' name and steps
        '''
        data = self.to_dict()
        json_data = json.dumps(data, indent=2)
        # Save JSON to a file
        with open(path, 'w') as json_file:
            json_file.write(json_data)
        pass
