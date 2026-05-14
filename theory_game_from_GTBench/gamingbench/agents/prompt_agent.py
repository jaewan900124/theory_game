
import json
import re

from gamingbench.agents.base_agent import BaseAgent
from gamingbench.prompts.step_prompts.prompt_agent import construct_step_prompt
from gamingbench.prompts.observation_prompts import construct_observation_prompt
from gamingbench.prompts.system_prompts import construct_system_prompt


class PromptAgent(BaseAgent):

    def __init__(self, config, **kwargs):
        super(PromptAgent, self).__init__(config)

        self.step_prompt_constructor = construct_step_prompt

    @staticmethod
    def _legal_move_match(move, legal_moves):
        if not move or not legal_moves:
            return None
        move = move.strip()
        move_with_brackets = move if move.startswith("<") else f"<{move}>"
        for legal_move in legal_moves:
            if move == legal_move or move_with_brackets == legal_move:
                return legal_move
            if move.lower() == "agree" and legal_move.lower() == "<agree>":
                return legal_move
            if move.startswith("[") and move in legal_move:
                return legal_move
        return None

    @staticmethod
    def _extract_json_object(text):
        if not text:
            return None
        text = text.strip()
        candidates = [text]
        fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced_match:
            candidates.insert(0, fenced_match.group(1))
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            candidates.append(text[first_brace:last_brace + 1])

        for candidate in candidates:
            try:
                value = json.loads(candidate)
            except (TypeError, json.JSONDecodeError):
                continue
            if isinstance(value, dict):
                return value
        return None

    @staticmethod
    def _selected_action_from_json(response, legal_moves):
        parsed = PromptAgent._extract_json_object(response)
        if not parsed:
            return None

        final_decision = parsed.get("final_decision")
        if isinstance(final_decision, dict):
            legal_match = PromptAgent._legal_move_match(
                final_decision.get("selected_action"), legal_moves)
            if legal_match:
                return legal_match

        decision = parsed.get("decision")
        if isinstance(decision, dict):
            legal_match = PromptAgent._legal_move_match(
                decision.get("selected_action"), legal_moves)
            if legal_match:
                return legal_match

        for key in ("selected_action", "chosen_action", "action"):
            legal_match = PromptAgent._legal_move_match(parsed.get(key), legal_moves)
            if legal_match:
                return legal_match
        return None

    @staticmethod
    def _legal_move_from_response_text(responses, legal_moves):
        if not responses or not legal_moves:
            return None

        for response in responses:
            legal_from_json = PromptAgent._selected_action_from_json(
                response, legal_moves)
            if legal_from_json:
                return legal_from_json

        action_markers = ("Final Action:", "Action:")
        for response in responses:
            if not response:
                continue

            action_text = None
            for marker in action_markers:
                marker_index = response.rfind(marker)
                if marker_index != -1:
                    action_text = response[marker_index + len(marker):]
                    break

            if action_text is not None:
                for legal_move in legal_moves:
                    if legal_move in action_text:
                        return legal_move
                if action_text.strip().lower() == "agree":
                    for legal_move in legal_moves:
                        if legal_move.lower() == "<agree>":
                            return legal_move

        for response in responses:
            if not response:
                continue
            for legal_move in legal_moves:
                if legal_move in response:
                    return legal_move
            if response.strip().lower() == "agree":
                for legal_move in legal_moves:
                    if legal_move.lower() == "<agree>":
                        return legal_move
        return None

    @staticmethod
    def _construct_repair_prompt(responses, legal_moves, observations):
        if observations.get("env_name") == "negotiation":
            turn_type = observations.get("turn_type")
            if turn_type == "Proposal":
                valid_format = (
                    "Return exactly one valid action and nothing else.\n"
                    "Use <Agree> or <Proposal: [a, b, c]>.\n"
                    "For <Proposal: [a, b, c]>, each number must be an integer from 0 to 5."
                )
            elif turn_type == "Utterance":
                valid_format = (
                    "Return exactly one valid action and nothing else.\n"
                    "Use <Utterance: [a, b, c]>.\n"
                    "Each number must be an integer from 0 to 4."
                )
            else:
                valid_format = (
                    "Return exactly one valid negotiation action and nothing else.\n"
                    "Use <Agree>, <Proposal: [a, b, c]>, or <Utterance: [a, b, c]>."
                )
            return f"""The previous answer was invalid or empty:
{responses}

{valid_format}
"""

        return f"""The previous answer was invalid or empty:
{responses}

Return exactly one legal action from this list and nothing else:
{legal_moves}
"""

    def _repair_or_fallback_move(self, responses, regex, legal_moves, query_list, observations):
        if not legal_moves:
            return ""

        repair_prompt = self._construct_repair_prompt(
            responses, legal_moves, observations)
        msgs = self.construct_init_messages(
            "Return exactly one legal action and nothing else.",
            repair_prompt)
        repair_responses, repair_query = self.llm_query(
            msgs, n=1, stop=None, prompt_type='move')
        query_list.append(repair_query)
        self.logger.info(f'Repair Prompt: {repair_prompt}')
        self.logger.info(f'Repair Response: {repair_responses}')

        legal_from_text = self._legal_move_from_response_text(
            repair_responses, legal_moves)
        if legal_from_text:
            return legal_from_text

        repaired_moves = self.parse_with_regex(repair_responses, regex)
        if len(repaired_moves) != 0:
            repaired_move = self.post_processing(repaired_moves, majority_vote=False)
            legal_match = self._legal_move_match(repaired_move, legal_moves)
            if legal_match:
                return legal_match

        fallback_move = legal_moves[0]
        self.logger.info(f'Falling back to first legal move: {fallback_move}')
        return fallback_move

    def step(self, observations):
        """

        :param observations:
        :return:
        """

        self.logger.info('-' * 20 + f'{self.agent_name} Begin' + '-' * 20)
        query_list = []

        env_name = observations['env_name']
        system_prompt = construct_system_prompt(env_name)
        observation_prompt = construct_observation_prompt(
            observations, env_name)
        step_instruct = self.step_prompt_constructor(observations)
        step_prompt = step_instruct['prompt']
        observation_prompt = observation_prompt + '\n' + step_prompt
        regex = step_instruct['regex']

        msgs = self.construct_init_messages(
            system_prompt, observation_prompt)

        responses, query = self.llm_query(
            msgs, n=self.num_generations, stop=None, prompt_type='move')
        query_list.append(query)

        self.logger.info(f'Prompt: {observation_prompt}')
        self.logger.info(f'Response: {responses}')

        legal_moves = observations.get("legal_moves", [])
        move = self._legal_move_from_response_text(responses, legal_moves)
        if not move:
            moves = self.parse_with_regex(responses, regex)
            if len(moves) != 0:
                move = self.post_processing(moves, majority_vote=False)
            else:
                move = ""

        if legal_moves:
            legal_match = self._legal_move_match(move, legal_moves)
            if legal_match:
                move = legal_match
            else:
                move = self._repair_or_fallback_move(
                    responses, regex, legal_moves, query_list, observations)

        self.logger.info('-' * 20 + f'{self.agent_name} End' + '-' * 20)
        return move, query_list
