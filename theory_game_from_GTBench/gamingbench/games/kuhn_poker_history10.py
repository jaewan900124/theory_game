from gamingbench.games.kuhn_poker import KuhnPoker


CARD_LABELS = {
    '0': 'Jack (J)',
    '1': 'Queen (Q)',
    '2': 'King (K)',
}

SHOWDOWN_ACTION_SEQUENCES = {
    ('<Pass>', '<Pass>'),
    ('<Bet>', '<Bet>'),
    ('<Pass>', '<Bet>', '<Bet>'),
}


class KuhnPokerHistory10(KuhnPoker):

    def __init__(self) -> None:
        super().__init__()
        self.recent_match_history_by_player = {0: [], 1: []}

    def set_recent_match_history_by_player(self, history_by_player):
        self.recent_match_history_by_player = {
            0: list(history_by_player.get(0, [])),
            1: list(history_by_player.get(1, [])),
        }

    def openspiel_observation_to_dict(self, current_player_idx, openspiel_obs):
        observations = super().openspiel_observation_to_dict(
            current_player_idx, openspiel_obs)
        observations['recent_match_history'] = list(
            self.recent_match_history_by_player.get(current_player_idx, []))
        return observations

    @staticmethod
    def _player_cards_by_index(match):
        player_cards = {}
        for step in match.steps:
            player_idx = step.observation.get('player_idx')
            card = step.observation.get('card')
            if player_idx not in player_cards and card is not None:
                player_cards[player_idx] = card
        return player_cards

    @staticmethod
    def _public_action_history(match):
        return [step.move for step in match.steps]

    @staticmethod
    def _result_for_player(match, player_idx):
        if not match.winner:
            return 'the game was a draw'

        winner_key = f"{match.agent_order[player_idx]}_{match.model_order[player_idx]}"
        if match.winner == winner_key:
            return 'you won'
        return 'you lost'

    @staticmethod
    def _payoff_for_player(match, player_idx):
        player_key = f"{match.agent_order[player_idx]}_{match.model_order[player_idx]}"
        if getattr(match, 'scores', None) and player_key in match.scores:
            return match.scores[player_key]
        if not match.winner:
            return 0
        if match.winner == player_key:
            return match.winner_score
        return match.loser_score

    def summarize_completed_match_for_players(self, match):
        public_actions = self._public_action_history(match)
        public_action_text = ' -> '.join(public_actions) if public_actions else 'no public actions'
        showdown = tuple(public_actions) in SHOWDOWN_ACTION_SEQUENCES
        player_cards = self._player_cards_by_index(match)
        summaries = {}

        for player_idx in range(2):
            own_card = CARD_LABELS.get(player_cards.get(player_idx, '?'), player_cards.get(player_idx, '?'))
            role_text = 'You acted first' if player_idx == 0 else 'You acted second'
            result_text = self._result_for_player(match, player_idx)

            parts = [
                role_text,
                f"your private card was {own_card}",
                f"public action history was {public_action_text}",
                f"result: {result_text}",
                f"chip payoff: {self._payoff_for_player(match, player_idx):+g}",
            ]

            if showdown:
                opponent_idx = 1 - player_idx
                opponent_card = CARD_LABELS.get(
                    player_cards.get(opponent_idx, '?'),
                    player_cards.get(opponent_idx, '?'),
                )
                parts.append(f"opponent card at showdown was {opponent_card}")

            summaries[player_idx] = '; '.join(parts) + '.'

        return summaries
