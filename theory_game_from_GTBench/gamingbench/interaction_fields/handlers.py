from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from gamingbench.interaction_fields.adapters import GameAdapter, parse_numeric_action
from gamingbench.interaction_fields.schemas import (
    DecisionRule,
    InteractionFieldSpec,
    VerifierCheck,
    unavailable,
)


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    text = text.lower()
    return any(needle.lower() in text for needle in needles)


_KUHN_CARD_RANK = {"J": 0, "Q": 1, "K": 2}


def _normalize_kuhn_card(raw_card: Any) -> Optional[str]:
    if raw_card is None:
        return None
    value = str(raw_card)
    return {
        "0": "J",
        "1": "Q",
        "2": "K",
        "j": "J",
        "q": "Q",
        "k": "K",
        "J": "J",
        "Q": "Q",
        "K": "K",
    }.get(value, None)


def _kuhn_public_history(obs: Mapping[str, Any]) -> str:
    if obs.get("public_history") is not None:
        return str(obs.get("public_history") or "")
    if obs.get("history") is not None:
        return str(obs.get("history") or "")
    if obs.get("moves") is not None:
        return str(obs.get("moves") or "")
    self_moves = list(obs.get("self_moves") or [])
    opponent_moves = list(obs.get("opponent_moves") or [])
    return "".join(str(action) for action in self_moves + opponent_moves)


def _kuhn_possible_opponent_cards(card: Optional[str]) -> List[str]:
    deck = ["J", "Q", "K"]
    return [item for item in deck if item != card] if card in deck else deck


def _uniform_card_probabilities(cards: Sequence[str]) -> Mapping[str, float]:
    if not cards:
        return {}
    probability = 1.0 / len(cards)
    return {card: probability for card in cards}


def _kuhn_showdown_payoff(my_card: str, opponent_card: str, stake: float) -> float:
    return stake if _KUHN_CARD_RANK[my_card] > _KUHN_CARD_RANK[opponent_card] else -stake


def _kuhn_facing_bet_action_payoffs(
    my_card: Optional[str],
    legal: Sequence[str],
    opponent_cards: Sequence[str],
) -> Any:
    if my_card not in _KUHN_CARD_RANK:
        return unavailable("private card is missing or invalid")
    if not opponent_cards:
        return unavailable("opponent card support is empty")

    payoffs: Dict[str, Any] = {}
    if "<Pass>" in legal:
        payoffs["<Pass>"] = {opponent_card: -1.0 for opponent_card in opponent_cards}
    if "<Bet>" in legal:
        payoffs["<Bet>"] = {
            opponent_card: _kuhn_showdown_payoff(my_card, opponent_card, 2.0)
            for opponent_card in opponent_cards
        }
    return payoffs if payoffs else unavailable("no legal facing-bet actions were found")


def _kuhn_expected_action_values(
    action_payoffs: Any,
    structural_prior: Any,
) -> Any:
    if isinstance(action_payoffs, dict) and action_payoffs.get("status") == "unavailable":
        return action_payoffs
    if isinstance(structural_prior, dict) and structural_prior.get("status") == "unavailable":
        return structural_prior

    expected_values: Dict[str, float] = {}
    for action, payoff_by_card in action_payoffs.items():
        expected_values[action] = sum(
            float(structural_prior[opponent_card]) * float(payoff)
            for opponent_card, payoff in payoff_by_card.items()
        )
    return expected_values


class TheoryHandler(ABC):
    theory_id = "abstract"
    required_game_capabilities: List[str] = []

    def supports_mapping(self, mapping_entry: Mapping[str, Any]) -> bool:
        parts = [
            str(mapping_entry.get("display_name", "")),
            str(mapping_entry.get("game_type", "")),
            str(mapping_entry.get("solution_concept", "")),
            str(mapping_entry.get("why_fixed", "")),
            " ".join(mapping_entry.get("osborne_rubinstein_mapping", []) or []),
        ]
        return self.supports_text(" ".join(parts))

    @abstractmethod
    def supports_text(self, mapping_text: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def compile(self, adapter: GameAdapter, mapping_entry: Mapping[str, Any]) -> Tuple[List[InteractionFieldSpec], List[DecisionRule], List[VerifierCheck]]:
        raise NotImplementedError

    def field(
        self,
        adapter: GameAdapter,
        field_id: str,
        description: str,
        raw_inputs: List[str],
        requirements: List[str],
        method: str,
        steps: List[str],
        output_type: str,
        value: Any,
        decision_role: str,
        priority: Optional[int],
        operator: str,
        invariants: List[str],
        failure_mode: str,
        formula: Optional[str] = None,
        handler: Optional[str] = None,
    ) -> InteractionFieldSpec:
        calculation = {"method": method, "steps": steps}
        if formula:
            calculation["formula"] = formula
        if handler:
            calculation["handler"] = handler
        return InteractionFieldSpec(
            field_id=field_id,
            source_game_id=adapter.game_id,
            source_theory_id=self.theory_id,
            description=description,
            raw_inputs=raw_inputs,
            requirements=requirements,
            calculation=calculation,
            output_type=output_type,
            value=value,
            decision_role=decision_role,
            priority=priority,
            operator=operator,
            invariants=invariants,
            failure_mode_if_ignored=failure_mode,
        )


class PureNashMatrixHandler(TheoryHandler):
    theory_id = "pure_nash_equilibrium"
    required_game_capabilities = ["payoff_matrix", "legal_actions"]

    def supports_text(self, mapping_text: str) -> bool:
        return _contains_any(mapping_text, ["pure nash", "normal-form", "payoff matrix", "best response matrix"])

    def compile(self, adapter: GameAdapter, mapping_entry: Mapping[str, Any]):
        if not adapter.supports("payoff_matrix"):
            value = unavailable("adapter lacks payoff_matrix capability")
            fields = [self.field(
                adapter, "mutual_best_response_cells",
                "Cells that are best responses for every player.",
                ["payoff_matrix", "legal_actions"], self.required_game_capabilities,
                "scan_payoff_matrix",
                ["Read payoff matrix.", "Compute each player's best responses.", "Intersect best-response cells."],
                "unavailable", value, "priority_candidate", 1, "choose_if_nonempty",
                ["Do not treat best-response cycles as equilibria."],
                "Can report non-equilibrium action profiles.",
            )]
            return fields, [], [VerifierCheck("pure_ne_cells_are_mutual_best_responses", "mutual_best_response_cells", "all returned cells are mutual best responses", True)]

        payoff_matrix = adapter.payoff_matrix()
        row_actions = adapter.legal_actions(0)
        col_actions = adapter.legal_actions(1)
        row_best = {}
        col_best = {}
        for col in col_actions:
            payoffs = [(row, payoff_matrix[(row, col)][0]) for row in row_actions]
            max_payoff = max(v for _, v in payoffs)
            row_best[col] = [row for row, v in payoffs if v == max_payoff]
        for row in row_actions:
            payoffs = [(col, payoff_matrix[(row, col)][1]) for col in col_actions]
            max_payoff = max(v for _, v in payoffs)
            col_best[row] = [col for col, v in payoffs if v == max_payoff]
        mutual = [
            [row, col]
            for row in row_actions
            for col in col_actions
            if row in row_best[col] and col in col_best[row]
        ]
        fields = [
            self.field(
                adapter, "player_best_response_cells",
                "Best-response cells by opponent action for each player.",
                ["payoff_matrix", "legal_actions"], self.required_game_capabilities,
                "compute_best_response",
                [
                    "For each column action, find row actions maximizing player 0 payoff.",
                    "For each row action, find column actions maximizing player 1 payoff.",
                ],
                "map[player, map[opponent_action, list[action]]]",
                {"player_0": row_best, "player_1": col_best},
                "informational", None, "compare",
                ["Best responses compare individual, not total, payoffs."],
                "Can confuse high total payoff with equilibrium.",
            ),
            self.field(
                adapter, "mutual_best_response_cells",
                "Pure Nash cells where all players are best responding.",
                ["player_best_response_cells"], self.required_game_capabilities,
                "scan_payoff_matrix",
                ["Intersect player 0 and player 1 best-response cells."],
                "set[cell]", mutual,
                "solution_set_field", 1, "intersection",
                ["Every returned cell must be a best response for both players."],
                "Can return a profile that one player would deviate from.",
            ),
        ]
        rules = [DecisionRule("return_pure_nash_cells", 1, "mutual_best_response_cells", "return_all", "answer", "Return exactly all mutual best-response cells.")]
        checks = [VerifierCheck("pure_ne_complete", "mutual_best_response_cells", "answer equals the complete mutual_best_response_cells set", True)]
        return fields, rules, checks


class SequentialLookaheadHandler(TheoryHandler):
    theory_id = "sequential_lookahead"
    required_game_capabilities = ["legal_actions"]

    def supports_text(self, mapping_text: str) -> bool:
        text = mapping_text.lower()
        if "imperfect-information" in text or "imperfect information" in text:
            return _contains_any(text, ["backward", "subgame", "lookahead", "combinatorial"])
        return _contains_any(text, ["backward", "subgame", "lookahead", "perfect information", "combinatorial"])

    def compile(self, adapter: GameAdapter, mapping_entry: Mapping[str, Any]):
        if adapter.game_id in {"tictactoe", "tic_tac_toe"} and adapter.supports("tictactoe_board"):
            return self._compile_tictactoe(adapter)
        if adapter.game_id == "nim":
            return self._compile_nim(adapter)
        value = unavailable("no deterministic transition/search adapter is available for this sequential game")
        fields = [self.field(
            adapter, "minimax_value_by_action",
            "Depth-limited minimax values for legal actions.",
            ["state", "legal_actions", "transition", "utility"],
            ["legal_actions", "apply_action", "is_terminal", "utility"],
            "compute_minimax_value",
            ["Capability check failed before search.", "Return unavailable instead of claiming minimax."],
            "unavailable", value, "ranking_score", 10, "maximize",
            ["Do not claim complete minimax without transition and terminal utility capabilities."],
            "Can hallucinate forced wins or blocks.",
        )]
        checks = [VerifierCheck("legal_action_only", None, "selected action is in legal_actions", True)]
        return fields, [], checks

    def _compile_tictactoe(self, adapter: GameAdapter):
        board = adapter.tictactoe_board()
        legal = adapter.legal_actions()
        self_moves = set(board.get("self_moves") or [])
        opp_moves = set(board.get("opponent_moves") or [])
        lines = [
            ["<C1R1>", "<C2R1>", "<C3R1>"],
            ["<C1R2>", "<C2R2>", "<C3R2>"],
            ["<C1R3>", "<C2R3>", "<C3R3>"],
            ["<C1R1>", "<C1R2>", "<C1R3>"],
            ["<C2R1>", "<C2R2>", "<C2R3>"],
            ["<C3R1>", "<C3R2>", "<C3R3>"],
            ["<C1R1>", "<C2R2>", "<C3R3>"],
            ["<C3R1>", "<C2R2>", "<C1R3>"],
        ]

        def completing_actions(marks: set) -> List[str]:
            actions = []
            for line in lines:
                marked = [cell for cell in line if cell in marks]
                empty = [cell for cell in line if cell in legal]
                if len(marked) == 2 and len(empty) == 1:
                    actions.append(empty[0])
            return sorted(set(actions), key=legal.index)

        immediate_win = completing_actions(self_moves)
        opponent_wins = completing_actions(opp_moves)
        block = opponent_wins[:]
        fields = [
            self.field(
                adapter, "immediate_win_actions",
                "Legal actions that complete my terminal winning line.",
                ["self_moves", "legal_actions", "winning_lines"], ["tictactoe_board"],
                "custom_handler",
                ["Scan every winning line.", "If it has two self marks and one legal empty cell, add the empty action."],
                "set[action]", immediate_win,
                "tactical_set", 1, "choose_if_nonempty",
                ["Every action must be legal and complete a named line."],
                "Can miss an immediate win.",
                handler="_compile_tictactoe",
            ),
            self.field(
                adapter, "opponent_immediate_win_actions",
                "Opponent actions that would win immediately next turn.",
                ["opponent_moves", "legal_actions", "winning_lines"], ["tictactoe_board"],
                "custom_handler",
                ["Scan every winning line.", "If it has two opponent marks and one legal empty cell, add the empty action."],
                "set[action]", opponent_wins,
                "verifier_only", None, "verify",
                ["Every action must be legal and complete an opponent line."],
                "Can overlook forced loss next turn.",
                handler="_compile_tictactoe",
            ),
            self.field(
                adapter, "immediate_block_actions",
                "Legal actions that prevent every current opponent terminal threat.",
                ["opponent_immediate_win_actions"], ["tictactoe_board"],
                "custom_handler",
                ["Use opponent_immediate_win_actions as required block squares."],
                "set[action]", block,
                "tactical_set", 2, "choose_if_nonempty",
                ["Use only when immediate_win_actions is empty."],
                "Can choose a non-terminal plan while allowing immediate loss.",
                handler="_compile_tictactoe",
            ),
        ]
        rules = [
            DecisionRule("win_now", 1, "immediate_win_actions", "choose_if_nonempty", "select_from_field", "Immediate terminal win overrides all lower-priority rules."),
            DecisionRule("block_now", 2, "immediate_block_actions", "choose_if_nonempty", "select_from_field", "If no immediate win exists, block opponent terminal win."),
        ]
        checks = [
            VerifierCheck("legal_action_only", None, "selected action is in legal_actions", True),
            VerifierCheck("block_if_required", "immediate_block_actions", "if immediate_win_actions empty and immediate_block_actions nonempty, selected action is in immediate_block_actions", True),
        ]
        return fields, rules, checks

    def _parse_nim_action(self, action: Any) -> Optional[Tuple[int, int]]:
        import re
        match = re.search(r"pile:(\d+),\s*take:(\d+)", str(action))
        if not match:
            return None
        return int(match.group(1)), int(match.group(2))

    def _compile_nim(self, adapter: GameAdapter):
        legal = adapter.legal_actions()
        parsed = {action: self._parse_nim_action(action) for action in legal}
        valid = {action: item for action, item in parsed.items() if item is not None}
        pile_state = {}
        for _, (pile, take) in valid.items():
            pile_state[pile] = max(pile_state.get(pile, 0), take)

        def next_state_for(action):
            pile, take = valid[action]
            state = dict(pile_state)
            state[pile] = max(0, state[pile] - take)
            return {key: value for key, value in sorted(state.items()) if value > 0}

        effects = {action: next_state_for(action) for action in valid}
        nim_sum = {}
        phase = {}
        singleton_parity = {}
        total_matches_after_action = {}
        nonzero_pile_count_by_action = {}
        large_pile_count_by_action = {}
        singleton_count_by_action = {}
        zero_nim_sum_flag_by_action = {}
        all_singletons_flag_by_action = {}
        terminal_take_last_flag_by_action = {}
        endgame_parity_target_by_action = {}
        for action, state in effects.items():
            large = [value for value in state.values() if value > 1]
            singletons = [value for value in state.values() if value == 1]
            phase[action] = "normal_phase" if len(large) >= 2 else "misere_endgame_phase"
            xor_value = 0
            for value in state.values():
                xor_value ^= value
            nim_sum[action] = xor_value
            singleton_parity[action] = "odd" if len(singletons) % 2 else "even"
            total_matches_after_action[action] = sum(state.values())
            nonzero_pile_count_by_action[action] = len(state)
            large_pile_count_by_action[action] = len(large)
            singleton_count_by_action[action] = len(singletons)
            zero_nim_sum_flag_by_action[action] = xor_value == 0
            all_singletons_flag_by_action[action] = bool(state) and all(value == 1 for value in state.values())
            terminal_take_last_flag_by_action[action] = len(state) == 0
            endgame_parity_target_by_action[action] = (
                phase[action] == "misere_endgame_phase" and singleton_parity[action] == "odd"
            )

        normal_winning = [
            action for action in valid
            if phase[action] == "normal_phase" and nim_sum[action] == 0
        ]
        # Misere endgame: if a move leaves only singleton piles, hand the
        # opponent an odd number of singletons where possible.
        misere_winning = [
            action for action in valid
            if (
                phase[action] == "misere_endgame_phase"
                and all(value == 1 for value in effects[action].values())
                and singleton_parity[action] == "odd"
            )
        ]
        winning_moves = set(normal_winning or misere_winning)
        opponent_position_value = {
            action: "opponent_losing" if action in winning_moves else "opponent_not_proven_losing"
            for action in valid
        }
        opponent_losing_score = {
            action: 1 if action in winning_moves else 0
            for action in valid
        }
        forced_loss_indicator = not bool(winning_moves)
        state_equivalence = {}
        for action, state in effects.items():
            signature = tuple(sorted(state.items()))
            state_equivalence.setdefault(signature, []).append(action)
        action_equivalence_classes = {
            action: sorted(state_equivalence[tuple(sorted(state.items()))], key=legal.index)
            for action, state in effects.items()
        }
        fields = [
            self.field(
                adapter, "pile_state_from_legal_actions",
                "Current pile sizes inferred from the maximum legal take per pile.",
                ["legal_actions"], ["legal_actions"],
                "custom_handler",
                ["Parse <pile:i, take:k> actions.", "Infer pile size as max legal take per pile."],
                "map[pile, count]", pile_state,
                "informational", None, "compare",
                ["Inference is valid only for Nim action formats exposing all takes."],
                "Can apply nim-sum to the wrong pile state.",
                handler="_compile_nim",
            ),
            self.field(
                adapter, "legal_move_effects",
                "Next pile state after each legal action.",
                ["pile_state_from_legal_actions", "legal_actions"], ["legal_actions"],
                "enumerate_legal_actions",
                ["For each legal action, subtract take count from exactly one pile."],
                "map[action, pile_state]", effects,
                "informational", None, "compare",
                ["Each action must reduce exactly one pile."],
                "Can choose a move without knowing the successor state.",
            ),
            self.field(
                adapter, "total_matches_after_action",
                "Total remaining matches after each legal action.",
                ["legal_move_effects"], ["legal_actions"],
                "custom_handler",
                ["For each successor state, sum all remaining pile sizes."],
                "map[action, number]", total_matches_after_action,
                "informational", None, "compare",
                ["Each value must equal the total matches in the successor state."],
                "Can miss terminal proximity and parity-relevant endgames.",
            ),
            self.field(
                adapter, "nonzero_pile_count_by_action",
                "Number of nonempty piles in each successor state.",
                ["legal_move_effects"], ["legal_actions"],
                "custom_handler",
                ["For each successor state, count piles with positive size."],
                "map[action, number]", nonzero_pile_count_by_action,
                "informational", None, "compare",
                ["Count only strictly positive piles."],
                "Can reason about the wrong successor game shape.",
            ),
            self.field(
                adapter, "large_pile_count_by_action",
                "Number of piles larger than one in each successor state.",
                ["legal_move_effects"], ["legal_actions"],
                "custom_handler",
                ["For each successor state, count piles whose size is greater than one."],
                "map[action, number]", large_pile_count_by_action,
                "informational", None, "compare",
                ["Large piles determine whether normal-phase Nim logic still applies."],
                "Can misclassify normal-phase versus misere endgame states.",
            ),
            self.field(
                adapter, "singleton_count_by_action",
                "Number of singleton piles in each successor state.",
                ["legal_move_effects"], ["legal_actions"],
                "custom_handler",
                ["For each successor state, count piles of size exactly one."],
                "map[action, number]", singleton_count_by_action,
                "informational", None, "compare",
                ["Singleton counts are parity-relevant in misere endgames."],
                "Can miss the endgame parity structure.",
            ),
            self.field(
                adapter, "nim_sum_by_action",
                "Nim-sum of each successor state.",
                ["legal_move_effects"], ["legal_actions"],
                "custom_handler",
                ["XOR all nonzero pile sizes after each action."],
                "map[action, number]", nim_sum,
                "ranking_score", 4, "minimize",
                ["Normal-phase target is successor nim-sum 0."],
                "Can miss a forced losing state for the opponent.",
            ),
            self.field(
                adapter, "misere_phase_by_action",
                "Whether each successor state is normal or misere endgame.",
                ["legal_move_effects"], ["legal_actions"],
                "custom_handler",
                ["Count piles larger than 1 after each action.", "Use misere endgame when fewer than two large piles remain."],
                "map[action, string]", phase,
                "verifier_only", None, "verify",
                ["Misere endgames must not blindly use normal nim-sum."],
                "Can lose by applying normal-play Nim in the final singleton phase.",
            ),
            self.field(
                adapter, "phase_classification_by_action",
                "Whether each successor state is normal or misere endgame.",
                ["large_pile_count_by_action"], ["legal_actions"],
                "custom_handler",
                ["Reuse the same phase classification as misere_phase_by_action."],
                "map[action, string]", phase,
                "verifier_only", None, "verify",
                ["This field mirrors misere_phase_by_action for alternate field-group experiments."],
                "Can create profile mismatch across equivalent phase fields.",
            ),
            self.field(
                adapter, "zero_nim_sum_flag_by_action",
                "Whether the successor Nim state has nim-sum zero.",
                ["nim_sum_by_action"], ["legal_actions"],
                "custom_handler",
                ["Set True when the successor nim-sum is zero, else False."],
                "map[action, boolean]", zero_nim_sum_flag_by_action,
                "ranking_score", None, "compare",
                ["Normal-phase target states have nim-sum zero."],
                "Can hide the key normal-phase target condition.",
            ),
            self.field(
                adapter, "all_singletons_flag_by_action",
                "Whether every remaining pile in the successor state is a singleton.",
                ["legal_move_effects"], ["legal_actions"],
                "custom_handler",
                ["Check whether all positive piles in the successor state have size one."],
                "map[action, boolean]", all_singletons_flag_by_action,
                "informational", None, "compare",
                ["The empty state is terminal, not an all-singletons state."],
                "Can blur terminal states with singleton-only endgames.",
            ),
            self.field(
                adapter, "terminal_take_last_flag_by_action",
                "Whether the action removes the final remaining match.",
                ["total_matches_after_action"], ["legal_actions"],
                "custom_handler",
                ["Set True when the successor state contains zero remaining matches."],
                "map[action, boolean]", terminal_take_last_flag_by_action,
                "informational", None, "compare",
                ["In misere Nim, taking the last match loses."],
                "Can fail to identify immediate self-losing actions.",
            ),
            self.field(
                adapter, "endgame_parity_target_by_action",
                "Whether the successor misere endgame has the favorable odd-singleton target.",
                ["phase_classification_by_action", "singleton_parity_by_action"], ["legal_actions"],
                "custom_handler",
                ["In misere endgames, mark True when the successor gives the opponent an odd singleton count."],
                "map[action, boolean]", endgame_parity_target_by_action,
                "informational", None, "compare",
                ["Only apply this parity target inside misere endgame states."],
                "Can mix endgame parity logic into normal-phase positions.",
            ),
            self.field(
                adapter, "opponent_position_value_by_action",
                "Opponent position class after each legal action under the available Nim heuristic.",
                ["nim_sum_by_action", "misere_phase_by_action"], ["legal_actions"],
                "custom_handler",
                ["Classify each successor state.", "Normal-phase nim-sum 0 and selected misere singleton states are opponent_losing."],
                "map[action, string]", opponent_position_value,
                "informational", None, "compare",
                ["Every classified action must be legal."],
                "Can choose a losing move when a direct winning move exists.",
            ),
            self.field(
                adapter, "opponent_losing_score_by_action",
                "Numeric score for whether the action gives the opponent a losing state.",
                ["opponent_position_value_by_action"], ["legal_actions"],
                "custom_handler",
                ["Map opponent_losing to 1 and other classes to 0."],
                "map[action, number]", opponent_losing_score,
                "ranking_score", 1, "maximize",
                ["Score is a derived classifier, not a preselected action list."],
                "Can hide the losing-state comparison inside an action recommendation.",
            ),
            self.field(
                adapter, "forced_loss_indicator",
                "Whether every legal action fails to hand the opponent a provably losing state.",
                ["opponent_position_value_by_action"], ["legal_actions"],
                "custom_handler",
                ["Set True when no legal action is classified as opponent_losing."],
                "boolean", forced_loss_indicator,
                "informational", None, "compare",
                ["This is a state-level indicator, not an action recommendation."],
                "Can hide whether the current state is strategically losing.",
            ),
            self.field(
                adapter, "action_equivalence_classes_by_successor_state",
                "Actions grouped by identical successor state.",
                ["legal_move_effects"], ["legal_actions"],
                "custom_handler",
                ["For each action, list all legal actions that induce the same successor state."],
                "map[action, list[action]]", action_equivalence_classes,
                "informational", None, "compare",
                ["Equivalent actions must produce identical successor pile states."],
                "Can miss duplicate strategic options and unstable tie breaks.",
            ),
        ]
        rules = [
            DecisionRule("prefer_opponent_losing_position", 1, "opponent_losing_score_by_action", "maximize", "select_argmax", "Prefer actions whose successor state is classified as opponent_losing."),
            DecisionRule("minimize_successor_nim_sum", 4, "nim_sum_by_action", "minimize", "select_argmin", "If no winning move is identified, choose lowest successor nim-sum."),
        ]
        checks = [
            VerifierCheck("legal_action_only", None, "selected action is in legal_actions", True),
            VerifierCheck("opponent_losing_priority", "opponent_position_value_by_action", "if any action is opponent_losing, selected action should have opponent_losing class", True),
        ]
        return fields, rules, checks


class PrivateValueAuctionHandler(TheoryHandler):
    theory_id = "private_value_auction_expected_utility"
    required_game_capabilities = ["legal_actions", "private_value"]

    def supports_text(self, mapping_text: str) -> bool:
        return _contains_any(mapping_text, ["auction"])

    def compile(self, adapter: GameAdapter, mapping_entry: Mapping[str, Any]):
        legal = adapter.legal_actions()
        value = adapter.private_value() if adapter.supports("private_value") else None
        if value is None:
            unavailable_value = unavailable("private valuation is missing from the game observation")
            fields = [self.field(
                adapter, "expected_utility_by_bid",
                "Expected utility of each bid.",
                ["private_valuation", "legal_actions", "win_probability_by_bid"],
                ["private_value", "legal_actions"],
                "compute_expected_utility",
                ["Private value is required before surplus can be computed."],
                "unavailable", unavailable_value, "ranking_score", 5, "maximize",
                ["Do not fabricate private valuation."],
                "Can recommend bids with unknown payoff.",
            )]
            return fields, [], [VerifierCheck("legal_action_only", None, "selected action is in legal_actions", True)]

        bids = {action: parse_numeric_action(action) for action in legal}
        surplus = {
            action: None if bid is None else value - bid
            for action, bid in bids.items()
        }
        overbids = [action for action, s in surplus.items() if s is not None and s < 0]
        win_probs = adapter.win_probability_by_action() if adapter.supports("win_probability_by_action") else None
        if win_probs:
            expected_utility = {
                action: win_probs.get(action, 0.0) * surplus[action]
                for action in legal
                if surplus[action] is not None
            }
            eu_output_type = "map[action, number]"
        else:
            expected_utility = unavailable("win_probability_by_action or opponent bid distribution is missing")
            eu_output_type = "unavailable"
        fields = [
            self.field(
                adapter, "surplus_if_win_by_bid",
                "Payoff if the bid wins under first-price private-value payoff.",
                ["private_valuation", "legal_actions"], ["private_value", "legal_actions"],
                "custom_handler",
                ["Parse each legal action as a bid.", "Compute private_valuation - bid."],
                "map[action, number]", surplus,
                "informational", None, "compare",
                ["Surplus must use individual private value, not total welfare."],
                "Can choose bids with negative utility if they win.",
                formula="surplus_if_win(bid)=private_value-bid",
            ),
            self.field(
                adapter, "overbid_actions",
                "Bids with negative surplus if they win.",
                ["surplus_if_win_by_bid"], ["private_value", "legal_actions"],
                "custom_handler",
                ["Collect actions where surplus_if_win_by_bid < 0."],
                "set[action]", overbids,
                "hard_constraint", 1, "filter",
                ["Filtered actions must not be selected unless the payoff rule explicitly differs."],
                "Can win the auction while losing utility.",
            ),
            self.field(
                adapter, "expected_utility_by_bid",
                "Win-probability weighted utility for each bid.",
                ["surplus_if_win_by_bid", "win_probability_by_action"],
                ["private_value", "legal_actions", "win_probability_by_action"],
                "compute_expected_utility",
                ["Compute surplus_if_win.", "Multiply by win_probability_by_action if available.", "Return unavailable if probabilities are missing."],
                eu_output_type, expected_utility,
                "ranking_score", 5, "maximize",
                ["Do not fabricate win probabilities."],
                "Can confuse conditional surplus with expected utility.",
                formula="EU(bid)=Pr(win|bid)*(private_value-bid)",
            ),
        ]
        rules = [
            DecisionRule("filter_overbids", 1, "overbid_actions", "filter", "discard_field_actions", "Remove negative-surplus bids."),
            DecisionRule("maximize_expected_utility", 5, "expected_utility_by_bid", "maximize", "select_argmax", "If available, choose highest expected utility after filters."),
        ]
        checks = [
            VerifierCheck("legal_action_only", None, "selected action is in legal_actions", True),
            VerifierCheck("no_negative_surplus_overbid", "overbid_actions", "selected action is not in overbid_actions", True),
        ]
        return fields, rules, checks


class StochasticExpectedValueHandler(TheoryHandler):
    theory_id = "stochastic_expected_value"
    required_game_capabilities = ["legal_actions", "chance_outcomes"]

    def supports_text(self, mapping_text: str) -> bool:
        return _contains_any(mapping_text, ["stochastic", "chance", "expected-value", "expected value"])

    def compile(self, adapter: GameAdapter, mapping_entry: Mapping[str, Any]):
        if adapter.game_id == "pig" and adapter.supports("pig_scores"):
            scores = adapter.pig_scores()
            if scores is not None:
                return self._compile_pig(adapter, scores)

        fields = []
        legal = adapter.legal_actions()
        values = {}
        missing = []
        for action in legal:
            outcomes = adapter.chance_outcomes(action) if adapter.supports("chance_outcomes") else None
            if outcomes is None:
                missing.append(action)
            else:
                values[action] = outcomes
        value = unavailable("chance outcome probabilities are missing") if missing else values
        output_type = "unavailable" if missing else "map[action, list[outcome, probability]]"
        fields.append(self.field(
            adapter, "expected_value_by_action",
            "Expected value computed from enumerated chance outcomes.",
            ["legal_actions", "chance_outcomes"], ["legal_actions", "chance_outcomes"],
            "compute_expected_utility",
            ["Enumerate legal actions.", "For each action, enumerate chance outcomes.", "If probabilities are missing, return unavailable."],
            output_type, value, "ranking_score", 5, "maximize",
            ["Expected value requires explicit probabilities."],
            "Can fabricate chance probabilities.",
        ))
        rules = [DecisionRule("maximize_expected_value", 5, "expected_value_by_action", "maximize", "select_argmax", "Use only when field is available.")]
        checks = [VerifierCheck("no_fake_probabilities", "expected_value_by_action", "unavailable if chance probabilities are missing", True)]
        return fields, rules, checks

    def _compile_pig(self, adapter: GameAdapter, scores: Mapping[str, int]):
        legal = adapter.legal_actions()
        self_score = scores["self_score"]
        opponent_score = scores["opponent_score"]
        turn_total = scores["turn_total"]
        target = scores["target_score"]
        score_after_stop = self_score + turn_total
        stop_wins_now = score_after_stop >= target
        roll_has_no_bust_loss = turn_total == 0
        bust_loss = turn_total
        distances = {
            "self_distance": max(0, target - self_score),
            "opponent_distance": max(0, target - opponent_score),
            "score_after_stop_distance": max(0, target - score_after_stop),
        }
        safe_roll_expected_gain = sum(range(2, 7)) / 6.0
        one_roll_expected_turn_total = (5 / 6) * (turn_total + 4) + (1 / 6) * 0
        stop_or_roll = {
            "<stop>": score_after_stop,
            "<roll>": self_score + one_roll_expected_turn_total,
        }
        fields = [
            self.field(
                adapter, "score_after_stop",
                "Permanent score if stopping now.",
                ["self_current_score", "turn_total_score"], ["pig_scores"],
                "custom_handler",
                ["Add self_current_score and turn_total_score."],
                "number", score_after_stop,
                "informational", None, "compare",
                ["Must equal self_score + turn_total."],
                "Can falsely claim stopping wins.",
                formula="score_after_stop=self_score+turn_total",
            ),
            self.field(
                adapter, "stop_wins_now",
                "Whether stopping immediately reaches the target.",
                ["score_after_stop", "target_score"], ["pig_scores"],
                "custom_handler",
                ["Compare score_after_stop to target_score."],
                "boolean", stop_wins_now,
                "verifier_only", None, "verify",
                ["If true and <stop> legal, <stop> must be chosen."],
                "Can roll instead of taking a guaranteed win.",
            ),
            self.field(
                adapter, "roll_has_no_bust_loss",
                "Whether rolling risks no accumulated turn points.",
                ["turn_total_score"], ["pig_scores"],
                "custom_handler",
                ["Check whether turn_total_score is 0."],
                "boolean", roll_has_no_bust_loss,
                "verifier_only", None, "verify",
                ["If true and stop does not win, prefer <roll> over banking 0."],
                "Can stop for zero and waste the turn.",
            ),
            self.field(
                adapter, "bust_loss",
                "Turn points lost if a 1 is rolled.",
                ["turn_total_score"], ["pig_scores"],
                "custom_handler",
                ["Bust loss equals current turn_total_score."],
                "number", bust_loss,
                "informational", None, "compare",
                ["Bust does not remove permanent score."],
                "Can overstate the downside of rolling.",
            ),
            self.field(
                adapter, "score_race_pressure",
                "Distances to target for both players.",
                ["self_current_score", "opponent_current_score", "target_score"], ["pig_scores"],
                "custom_handler",
                ["Compute target_score minus each permanent score."],
                "map[string, number]", distances,
                "tie_breaker", 5, "compare",
                ["Distances must be non-negative."],
                "Can ignore urgent race pressure.",
            ),
            self.field(
                adapter, "one_roll_heuristic_value_by_action",
                "Approximate one-roll continuation value using fair die outcomes.",
                ["turn_total_score"], ["pig_scores"],
                "compute_expected_utility",
                ["Use probability 1/6 for bust and 5/6 for safe outcomes.", "Approximate safe gain by average of 2..6."],
                "map[action, number]", stop_or_roll,
                "action_value", 6, "maximize",
                ["This is one-roll, not full dynamic-programming value."],
                "Can treat a heuristic as exact optimal policy.",
            ),
        ]
        rules = [
            DecisionRule("stop_if_winning", 1, "stop_wins_now", "custom_handler", "select_stop_if_true", "If stop_wins_now is true and <stop> is legal, choose <stop>."),
            DecisionRule("roll_if_no_bust_loss", 2, "roll_has_no_bust_loss", "custom_handler", "select_roll_if_true", "If roll_has_no_bust_loss is true and stop_wins_now is false, choose <roll>."),
            DecisionRule("maximize_one_roll_heuristic_value", 6, "one_roll_heuristic_value_by_action", "maximize", "select_argmax", "If priorities do not decide, choose the higher one-roll heuristic value."),
        ]
        checks = [
            VerifierCheck("legal_action_only", None, "selected action is in legal_actions", True),
            VerifierCheck("roll_when_turn_total_zero", "roll_has_no_bust_loss", "if turn_total is 0 and stop_wins_now is false, selected action is <roll>", True),
            VerifierCheck("stop_when_winning", "stop_wins_now", "if stop_wins_now is true, selected action is <stop>", True),
        ]
        return fields, rules, checks


class RepeatedGameTriggerHandler(TheoryHandler):
    theory_id = "repeated_game_trigger_strategy"

    def supports_text(self, mapping_text: str) -> bool:
        return _contains_any(mapping_text, ["repeated", "retaliation", "forgiveness", "history-dependent"])

    def compile(self, adapter: GameAdapter, mapping_entry: Mapping[str, Any]):
        obs = adapter.state() if isinstance(adapter.state(), Mapping) else {}
        legal = adapter.legal_actions()
        self_history = str(obs.get("self_moves", ""))
        opponent_history = str(obs.get("opponent_moves", ""))

        def split_history(text: str) -> List[str]:
            if not text:
                return []
            if "," in text:
                return [item.strip() for item in text.split(",") if item.strip()]
            return [char for char in text if char.strip()]

        opponent_actions = split_history(opponent_history)
        recent = opponent_actions[-1:] if opponent_actions else []
        defections = sum(1 for action in opponent_actions if action in {"D", "1", "Testify", "<Testify>"})
        coop = sum(1 for action in opponent_actions if action in {"C", "0", "Silent", "<Silent>"})
        recent_defection = bool(recent and recent[-1] in {"D", "1", "Testify", "<Testify>"})
        trigger_state = "punish" if recent_defection else ("no_history" if not opponent_actions else "cooperation_possible")
        payoff_bounds = {
            "<Silent>": {"worst_case": 0, "best_case": 5, "if_opponent_silent": 5, "if_opponent_testify": 0},
            "<Testify>": {"worst_case": 1, "best_case": 10, "if_opponent_silent": 10, "if_opponent_testify": 1},
        }
        legal_payoff_bounds = {action: payoff_bounds[action] for action in legal if action in payoff_bounds}
        worst_case_payoff = {action: values["worst_case"] for action, values in legal_payoff_bounds.items()}
        strictly_dominant = []
        if {"<Silent>", "<Testify>"}.issubset(legal_payoff_bounds):
            testify = legal_payoff_bounds["<Testify>"]
            silent = legal_payoff_bounds["<Silent>"]
            if (
                testify["if_opponent_silent"] > silent["if_opponent_silent"]
                and testify["if_opponent_testify"] > silent["if_opponent_testify"]
            ):
                strictly_dominant = ["<Testify>"]
        fields = [
            self.field(
                adapter, "history_summary",
                "Public repeated-game action history.",
                ["self_moves", "opponent_moves"], ["legal_actions"],
                "custom_handler",
                ["Read self and opponent histories from observation."],
                "map[string, list[action]]",
                {"self": split_history(self_history), "opponent": opponent_actions},
                "informational", None, "compare",
                ["History must be public observation, not invented."],
                "Can punish or cooperate from a false history.",
            ),
            self.field(
                adapter, "opponent_defection_count",
                "Count of opponent defection/testify actions.",
                ["opponent_moves"], ["legal_actions"],
                "custom_handler",
                ["Count opponent Testify/D actions."],
                "number", defections,
                "informational", None, "compare",
                ["Only observed opponent actions count."],
                "Can overreact to nonexistent defection.",
            ),
            self.field(
                adapter, "opponent_cooperation_count",
                "Count of opponent cooperation/silent actions.",
                ["opponent_moves"], ["legal_actions"],
                "custom_handler",
                ["Count opponent Silent/C actions."],
                "number", coop,
                "informational", None, "compare",
                ["Only observed opponent actions count."],
                "Can miss stable cooperation.",
            ),
            self.field(
                adapter, "trigger_strategy_state",
                "History state for trigger-style repeated-game reasoning.",
                ["opponent_moves"], ["legal_actions"],
                "custom_handler",
                ["Set punish only after observed recent defection.", "Use no_history when there is no evidence of cooperation or defection."],
                "string", trigger_state,
                "informational", None, "compare",
                ["State must come from observed opponent history."],
                "Can treat absent history as evidence of cooperation.",
            ),
            self.field(
                adapter, "opponent_recent_defection",
                "Whether the opponent's most recent observed action was defection/testify.",
                ["opponent_moves"], ["legal_actions"],
                "custom_handler",
                ["Check only the latest observed opponent action.", "Return false when no opponent action has been observed."],
                "boolean", recent_defection,
                "verifier_only", None, "verify",
                ["Must not infer defection from missing history."],
                "Can punish without evidence or fail to punish observed defection.",
            ),
            self.field(
                adapter, "stage_game_payoff_bounds_by_action",
                "One-round environment payoff bounds by my action over possible opponent actions.",
                ["legal_actions"], ["legal_actions"],
                "custom_handler",
                ["Use Prisoner's Dilemma payoff rule.", "For each legal action, record worst and best payoff across opponent actions."],
                "map[action, map[string, number]]", legal_payoff_bounds,
                "informational", None, "compare",
                ["Bounds are stage-game payoffs, not full repeated-game values."],
                "Can ignore immediate exploitability in the first round.",
            ),
            self.field(
                adapter, "stage_game_worst_case_payoff_by_action",
                "Worst-case one-round payoff by my action.",
                ["stage_game_payoff_bounds_by_action"], ["legal_actions"],
                "custom_handler",
                ["Take the minimum payoff for each action across possible opponent actions."],
                "map[action, number]", worst_case_payoff,
                "ranking_score", 2, "maximize",
                ["Use only when future cooperation value is unavailable or not credible."],
                "Can choose an exploitable first-round cooperation by default.",
            ),
            self.field(
                adapter, "strictly_dominant_stage_actions",
                "Actions that strictly dominate alternatives in the one-shot stage game.",
                ["stage_game_payoff_bounds_by_action"], ["legal_actions"],
                "compute_dominance",
                ["Compare payoffs under each possible opponent action.", "Include an action only if it is strictly better in every case."],
                "set[action]", strictly_dominant,
                "informational", None, "compare",
                ["Stage dominance does not by itself prove repeated-game optimality."],
                "Can confuse one-shot dominance with repeated-game equilibrium.",
            ),
            self.field(
                adapter, "future_interaction_value",
                "Evidence that current cooperation can be repaid by future opponent cooperation.",
                ["round_index", "opponent_moves", "discount_or_horizon", "opponent_strategy_belief"], ["legal_actions"],
                "custom_handler",
                ["Require a horizon/discount or opponent cooperation model.", "If absent, mark unavailable instead of assuming cooperation."],
                "unavailable", unavailable("discount/horizon or opponent cooperation model is missing"),
                "informational", None, "verify",
                ["Do not assume future cooperation value from an empty history."],
                "Can cooperate in the first round without evidence that cooperation is enforceable.",
            ),
        ]
        rules = [
            DecisionRule("retaliate_after_observed_defection", 1, "opponent_recent_defection", "custom_handler", "select_testify_if_true", "If opponent_recent_defection is true and <Testify> is legal, select <Testify>."),
            DecisionRule("avoid_first_round_exploitation_without_future_value", 2, "stage_game_worst_case_payoff_by_action", "maximize", "select_argmax", "When future_interaction_value is unavailable, choose the legal action with the best worst-case stage payoff."),
        ]
        checks = [
            VerifierCheck("legal_action_only", None, "selected action is in legal_actions", True),
            VerifierCheck("retaliate_after_defection", "opponent_recent_defection", "if true, selected action should be <Testify>", True),
            VerifierCheck("no_assumed_future_cooperation", "future_interaction_value", "do not select <Silent> solely from empty history when future_interaction_value is unavailable", True),
        ]
        return fields, rules, checks


class ImperfectInformationBeliefHandler(TheoryHandler):
    theory_id = "belief_weighted_expected_utility"
    required_game_capabilities = ["legal_actions", "belief_state"]

    def supports_text(self, mapping_text: str) -> bool:
        return _contains_any(mapping_text, ["imperfect-information", "belief", "bayesian", "private preferences"])

    def compile(self, adapter: GameAdapter, mapping_entry: Mapping[str, Any]):
        if adapter.game_id == "kuhn_poker":
            obs = adapter.state() if isinstance(adapter.state(), Mapping) else {}
            legal = adapter.legal_actions()
            card = _normalize_kuhn_card(
                obs.get("private_card") or obs.get("card") or obs.get("my_card")
            )
            history = _kuhn_public_history(obs)
            facing_bet = history.lower().endswith("b")
            possible_cards = _kuhn_possible_opponent_cards(card)
            pot_size = 3 if facing_bet else 2
            structural_prior = (
                unavailable("private card is missing, so opponent card support is unknown")
                if card is None
                else _uniform_card_probabilities(possible_cards)
            )
            action_payoffs = (
                _kuhn_facing_bet_action_payoffs(card, legal, possible_cards)
                if facing_bet
                else unavailable("exact action EV is only computed when responding to a bet")
            )
            expected_values = _kuhn_expected_action_values(action_payoffs, structural_prior)
            showdown_result = (
                unavailable("private card is missing or invalid")
                if card not in _KUHN_CARD_RANK
                else {
                    opponent_card: (
                        "win" if _KUHN_CARD_RANK[card] > _KUHN_CARD_RANK[opponent_card] else "lose"
                    )
                    for opponent_card in possible_cards
                }
            )
            call_value = (
                action_payoffs.get("<Bet>", unavailable("call is not legal in this information set"))
                if isinstance(action_payoffs, dict)
                else unavailable("call value is unavailable outside immediate-resolution facing-bet states")
            )
            fold_value = (
                -1.0
                if facing_bet and "<Pass>" in legal
                else unavailable("fold_value is only defined when facing a bet and fold is legal")
            )
            if card is None:
                bluff_incentive = unavailable("private card is missing")
                value_bet_incentive = unavailable("private card is missing")
                bet_fold_equity = unavailable("private card is missing")
            else:
                if facing_bet:
                    bluff_incentive = {"status": "not_applicable", "reason": "current decision responds to an opponent bet"}
                    value_bet_incentive = {"status": "not_applicable", "reason": "current decision responds to an opponent bet"}
                    bet_fold_equity = {"status": "not_applicable", "reason": "bet/fold tradeoff applies when considering an opening bet"}
                else:
                    bluff_incentive = {
                        "J": "high_bluff_incentive",
                        "Q": "mixed_bluff_incentive",
                        "K": "low_bluff_incentive",
                    }[card]
                    value_bet_incentive = {
                        "J": "low_value_bet_incentive",
                        "Q": "medium_value_bet_incentive",
                        "K": "high_value_bet_incentive",
                    }[card]
                    bet_fold_equity = {
                        "J": "bet gains most from opponent fold with weak showdown value",
                        "Q": "bet has intermediate fold-equity value",
                        "K": "bet mainly gains from value extraction rather than fold equity",
                    }[card]
            opponent_response_if_i_bet = (
                {"possible_responses": ["fold", "call"], "status": "structural_only"}
                if not facing_bet and "<Bet>" in legal
                else {"status": "not_applicable", "reason": "current node is not an opening-bet decision"}
            )
            action_risk_profile = {}
            for action in legal:
                if facing_bet:
                    if action == "<Pass>":
                        action_risk_profile[action] = "defensive_fold"
                    elif action == "<Bet>":
                        if card == "K":
                            action_risk_profile[action] = "profitable_call_candidate"
                        elif card == "J":
                            action_risk_profile[action] = "high_variance_call"
                        else:
                            action_risk_profile[action] = "thin_call"
                    else:
                        action_risk_profile[action] = "other"
                else:
                    if action == "<Pass>":
                        action_risk_profile[action] = "safe_check"
                    elif action == "<Bet>":
                        if card == "J":
                            action_risk_profile[action] = "clear_bluff_candidate"
                        elif card == "K":
                            action_risk_profile[action] = "clear_value_bet_candidate"
                        else:
                            action_risk_profile[action] = "mixed_bet_candidate"
                    else:
                        action_risk_profile[action] = "other"
            information_set_class = (
                "facing_bet_response"
                if facing_bet
                else ("opening_action" if history == "" else "post_check_action")
            )

            fields = [
                self.field(
                    adapter,
                    "belief_state",
                    "Belief model over hidden information used for belief-weighted decisions.",
                    ["observation", "information_set"],
                    ["belief_state"],
                    "compute_expected_utility",
                    ["Read provided belief_state.", "If absent, return unavailable instead of inventing beliefs."],
                    "unavailable",
                    unavailable("strategy-conditioned belief_state is missing"),
                    "informational",
                    None,
                    "verify",
                    ["Beliefs must come from adapter input, not model imagination."],
                    "Can hallucinate hidden information.",
                ),
                self.field(
                    adapter,
                    "opponent_card_belief_probabilities",
                    "Structural prior over the opponent's remaining possible cards when no strategy-conditioned posterior is provided.",
                    ["private_card", "public_history"],
                    ["legal_actions"],
                    "custom_handler",
                    ["Normalize my private card.", "Enumerate remaining deck cards.", "Assign uniform probability over structurally possible opponent cards."],
                    "map[hidden_state, probability]" if card is not None else "unavailable",
                    structural_prior,
                    "informational",
                    None,
                    "compare",
                    ["Probabilities must sum to 1 over cards still possible after card exclusion."],
                    "Can overfit to nonexistent strategic tells in the betting history.",
                ),
                self.field(
                    adapter,
                    "action_payoff_by_opponent_card",
                    "Action payoff table by possible opponent card when the current information set resolves immediately.",
                    ["private_card", "public_history", "legal_actions"],
                    ["legal_actions"],
                    "custom_handler",
                    ["If facing a bet, fold loses 1 chip.", "If calling, evaluate showdown payoff of +2 or -2 against each possible opponent card.", "Otherwise mark unavailable because opponent response remains unresolved."],
                    "map[action, map[hidden_state, number]]"
                    if not isinstance(action_payoffs, dict) or "status" not in action_payoffs
                    else "unavailable",
                    action_payoffs,
                    "informational",
                    None,
                    "compare",
                    ["Only populate this field when the current action resolves the hand exactly."],
                    "Can pretend unresolved betting lines already have fixed payoffs.",
                ),
                self.field(
                    adapter,
                    "expected_value_by_action",
                    "Structural-prior expected payoff for each legal action when the hand resolves immediately from this information set.",
                    ["action_payoff_by_opponent_card", "opponent_card_belief_probabilities"],
                    ["legal_actions"],
                    "compute_expected_utility",
                    ["Use action_payoff_by_opponent_card.", "Average by opponent_card_belief_probabilities.", "If either ingredient is unavailable, return unavailable."],
                    "map[action, number]"
                    if not isinstance(expected_values, dict) or "status" not in expected_values
                    else "unavailable",
                    expected_values,
                    "ranking_score",
                    5,
                    "maximize",
                    ["Only compare actions using exact immediate-resolution values under the structural prior."],
                    "Can maximize a fabricated EV in unresolved betting states.",
                    formula="expected_value(action)=sum_card P(card)*payoff(action,card)",
                ),
                self.field(
                    adapter,
                    "information_set_class",
                    "Coarse Kuhn information-set type for the current decision.",
                    ["public_history", "legal_actions"],
                    ["legal_actions"],
                    "custom_handler",
                    ["If facing a bet, classify as facing_bet_response.", "If history is empty, classify as opening_action.", "Otherwise classify as post_check_action."],
                    "string",
                    information_set_class,
                    "informational",
                    None,
                    "compare",
                    ["Classification must follow the observed public history only."],
                    "Can use the wrong tactical template for the current Kuhn node.",
                ),
                self.field(
                    adapter,
                    "possible_opponent_cards",
                    "Opponent cards still possible after excluding my private card.",
                    ["private_card"],
                    ["legal_actions"],
                    "custom_handler",
                    ["Normalize my private card.", "List the remaining cards in the Kuhn deck."],
                    "list[hidden_state]" if card is not None else "unavailable",
                    possible_cards if card is not None else unavailable("private card is missing"),
                    "informational",
                    None,
                    "compare",
                    ["Possible opponent cards must exclude my own card."],
                    "Can reason over an impossible opponent card support.",
                ),
                self.field(
                    adapter,
                    "posterior_over_opponent_cards",
                    "Posterior belief over opponent cards under the current structural prior.",
                    ["possible_opponent_cards", "public_history"],
                    ["legal_actions"],
                    "custom_handler",
                    ["Use the structural prior over possible opponent cards when no richer posterior model is available."],
                    "map[hidden_state, probability]" if card is not None else "unavailable",
                    structural_prior,
                    "informational",
                    None,
                    "compare",
                    ["Belief weights must sum to 1 over structurally possible opponent cards."],
                    "Can hide uncertainty over the opponent card.",
                ),
                self.field(
                    adapter,
                    "pot_size",
                    "Current pot size before taking the action.",
                    ["public_history"],
                    ["legal_actions"],
                    "custom_handler",
                    ["Use Kuhn ante pot of 2.", "If facing a bet, pot before response is 3.", "Otherwise pot is 2."],
                    "number",
                    pot_size,
                    "informational",
                    None,
                    "compare",
                    ["Pot size must match the observed betting history."],
                    "Can misvalue call or bet incentives.",
                ),
                self.field(
                    adapter,
                    "showdown_result_by_opponent_card",
                    "Showdown outcome against each possible opponent card.",
                    ["private_card", "possible_opponent_cards"],
                    ["legal_actions"],
                    "custom_handler",
                    ["Compare my card rank against each possible opponent card.", "Mark each as win or lose at showdown."],
                    "map[hidden_state, string]" if card is not None else "unavailable",
                    showdown_result,
                    "informational",
                    None,
                    "compare",
                    ["Showdown outcome depends only on card ranks, not imagined betting behavior."],
                    "Can misread hand strength against the opponent support.",
                ),
                self.field(
                    adapter,
                    "call_value_by_opponent_card",
                    "Payoff by opponent card when the current <Bet> action functions as a call.",
                    ["action_payoff_by_opponent_card", "legal_action_context"],
                    ["legal_actions"],
                    "custom_handler",
                    ["If facing a bet and <Bet> is legal, reuse the exact call payoff by opponent card.", "Otherwise return unavailable."],
                    "map[hidden_state, number]" if not isinstance(call_value, dict) or "status" not in call_value else "unavailable",
                    call_value,
                    "informational",
                    None,
                    "compare",
                    ["Only populate exact call values in immediate-resolution response states."],
                    "Can fabricate call payoffs in unresolved betting nodes.",
                ),
                self.field(
                    adapter,
                    "fold_value",
                    "Guaranteed payoff of folding when currently facing a bet.",
                    ["public_history", "legal_actions"],
                    ["legal_actions"],
                    "custom_handler",
                    ["If facing a bet and <Pass> is legal, fold value is -1.", "Otherwise return unavailable."],
                    "number" if not isinstance(fold_value, dict) else "unavailable",
                    fold_value,
                    "informational",
                    None,
                    "compare",
                    ["Fold value is only defined when <Pass> is the fold action."],
                    "Can confuse check with fold and distort the action baseline.",
                ),
                self.field(
                    adapter,
                    "bet_fold_equity",
                    "Coarse value of how much an opening bet can benefit from opponent folds.",
                    ["private_card", "public_history"],
                    ["legal_actions"],
                    "custom_handler",
                    ["If not facing a bet, summarize the fold-equity role of betting from my current card class.", "If facing a bet, mark not_applicable."],
                    "string_or_status",
                    bet_fold_equity,
                    "informational",
                    None,
                    "compare",
                    ["This is a structural heuristic, not an exact opponent response model."],
                    "Can overstate precise fold probabilities.",
                ),
                self.field(
                    adapter,
                    "bluff_incentive",
                    "Coarse incentive to bet with weak showdown value.",
                    ["private_card", "public_history"],
                    ["legal_actions"],
                    "custom_handler",
                    ["If not facing a bet, classify bluff incentive from my card rank.", "If facing a bet, mark not_applicable."],
                    "string_or_status",
                    bluff_incentive,
                    "informational",
                    None,
                    "compare",
                    ["Bluff incentive is strongest when showdown value is weak and betting may induce folds."],
                    "Can blur bluff logic with value-bet logic.",
                ),
                self.field(
                    adapter,
                    "value_bet_incentive",
                    "Coarse incentive to bet for value from current card strength.",
                    ["private_card", "public_history"],
                    ["legal_actions"],
                    "custom_handler",
                    ["If not facing a bet, classify value-bet incentive from my card rank.", "If facing a bet, mark not_applicable."],
                    "string_or_status",
                    value_bet_incentive,
                    "informational",
                    None,
                    "compare",
                    ["Value-bet incentive rises with stronger showdown value."],
                    "Can confuse strong-card extraction with weak-card bluffing.",
                ),
                self.field(
                    adapter,
                    "opponent_response_if_i_bet",
                    "Structural opponent response classes if I make an opening bet.",
                    ["public_history", "legal_actions"],
                    ["legal_actions"],
                    "custom_handler",
                    ["If current node is an opening-bet decision, list structural responses fold and call.", "Otherwise mark not_applicable."],
                    "map_or_status",
                    opponent_response_if_i_bet,
                    "informational",
                    None,
                    "compare",
                    ["This field exposes response classes, not a precise opponent strategy."],
                    "Can pretend exact response probabilities are known.",
                ),
                self.field(
                    adapter,
                    "action_risk_profile",
                    "Coarse risk label for each legal action in the current information set.",
                    ["private_card", "public_history", "legal_actions"],
                    ["legal_actions"],
                    "custom_handler",
                    ["Assign each legal action a compact structural risk label based on card strength and betting context."],
                    "map[action, string]",
                    action_risk_profile,
                    "informational",
                    None,
                    "compare",
                    ["Risk labels summarize structure; they do not directly choose the action."],
                    "Can collapse qualitatively different actions into an uninformative bucket.",
                ),
            ]
            rules = [
                DecisionRule(
                    "maximize_expected_value",
                    5,
                    "expected_value_by_action",
                    "maximize",
                    "select_argmax",
                    "If expected_value_by_action is available, choose the legal action with the highest structural-prior expected payoff.",
                )
            ]
            checks = [
                VerifierCheck(
                    "no_hallucinated_hidden_state",
                    "belief_state",
                    "belief-dependent fields unavailable when no strategy-conditioned belief model exists",
                    True,
                ),
                VerifierCheck(
                    "structural_card_prior_is_explicit",
                    "opponent_card_belief_probabilities",
                    "opponent_card_belief_probabilities is explicit rather than guessed from hidden information",
                    True,
                ),
                VerifierCheck(
                    "exact_ev_only_when_resolved",
                    "expected_value_by_action",
                    "expected_value_by_action is unavailable unless the current Kuhn information set resolves immediately after my action",
                    True,
                ),
            ]
            return fields, rules, checks

        belief = adapter.belief_state() if adapter.supports("belief_state") else None
        value = unavailable("belief_state/probability model is missing") if belief is None else belief
        output_type = "unavailable" if belief is None else "map[hidden_state, probability]"
        fields = [self.field(
            adapter, "belief_state",
            "Probability model over hidden information used for belief-weighted decisions.",
            ["observation", "information_set"], ["belief_state"],
            "compute_expected_utility",
            ["Read provided belief_state.", "If absent, return unavailable instead of inventing beliefs."],
            output_type, value, "informational", None, "verify",
            ["Beliefs must come from adapter input, not model imagination."],
            "Can hallucinate hidden information.",
        )]
        checks = [VerifierCheck("no_hallucinated_hidden_state", "belief_state", "belief-dependent fields unavailable when no belief model exists", True)]
        return fields, [], checks


DEFAULT_HANDLERS: List[TheoryHandler] = [
    PureNashMatrixHandler(),
    SequentialLookaheadHandler(),
    PrivateValueAuctionHandler(),
    StochasticExpectedValueHandler(),
    RepeatedGameTriggerHandler(),
    ImperfectInformationBeliefHandler(),
]


def handlers_for_mapping(mapping_entry: Mapping[str, Any], handlers: Optional[Sequence[TheoryHandler]] = None) -> List[TheoryHandler]:
    pool = list(handlers or DEFAULT_HANDLERS)
    matched = [handler for handler in pool if handler.supports_mapping(mapping_entry)]
    return matched or [UnsupportedTheoryHandler()]


class UnsupportedTheoryHandler(TheoryHandler):
    theory_id = "unsupported_theory"

    def supports_text(self, mapping_text: str) -> bool:
        return True

    def compile(self, adapter: GameAdapter, mapping_entry: Mapping[str, Any]):
        concept = mapping_entry.get("solution_concept", "unknown")
        fields = [self.field(
            adapter, "unsupported_interaction_fields",
            "No deterministic handler is available for this mapped theory/game interaction.",
            ["mapping.solution_concept"], [],
            "custom_handler",
            ["Read existing mapping.", "Return unavailable because no handler matched."],
            "unavailable", unavailable(f"no handler for solution_concept={concept!r}"),
            "informational", None, "verify",
            ["Compiler must fail explicitly instead of hallucinating fields."],
            "Can produce generic descriptive fields.",
        )]
        return fields, [], [VerifierCheck("unavailable_is_explicit", "unsupported_interaction_fields", "field value is unavailable with reason", True)]
