
def _construct_head_prompt():
    return 'Kuhn poker is a simple model zero-sum two-player imperfect-information game, amenable to a complete game-theoretic analysis. In Kuhn poker, the deck includes only three playing cards: a King (K), a Queen (Q), and a Jack (J).\n' \
           'Each player antes 1 chip, one card is dealt to each player, and the third card is put aside unseen. There is exactly one betting round and no further raises are allowed.\n' \
           'The available actions are always labeled <Pass> and <Bet>. If no bet has been made yet, <Pass> means check and <Bet> means bet. If the opponent has already bet, <Pass> means fold and <Bet> means call.\n' \
           'If both players check, the hand goes to showdown and the higher-ranking card wins the pot. If a player bets and the opponent folds, the bettor wins immediately. If a player bets and the opponent calls, the hand goes to showdown and the higher-ranking card wins the pot. The card rankings are as follows: King (K) > Queen (Q) > Jack (J).\n' \
           'Your objective is to maximize expected chip payoff over repeated hands, not merely to maximize the count of hands won. Folding loses the ante already committed, winning after checks is a smaller payoff than winning a called bet, and calling a losing bet is costlier than folding.\n' \
           '\n' \
           'You are playing Kuhn poker with the opponent. The actions are denoted by <Bet> and <Pass>.' \



def construct_observation_prompt(observations):

    card_mapping = {
        '0': 'Jack (J)',
        '1': 'Queen (Q)',
        '2': 'King (K)'
    }

    card = card_mapping[observations['card']]
    moves = observations['moves']
    player_idx = observations['player_idx']
    recent_match_history = observations.get('recent_match_history', [])

    move_prompt = ''
    if moves is not None:
        move_prompt = 'Here are the past moves in this match:\n'

        for idx, m in enumerate(moves):
            if (player_idx + 1) % (idx + 1) == 0:
                role = 'you'
            else:
                role = 'the opponent'

            if m == 'b':
                move = '<Bet>'
            elif m == 'p':
                move = '<Pass>'
            else:
                raise ValueError

            if idx == 0:
                move_prompt += f'In the {idx + 1}st round, {role} choose to {move};\n'
            elif idx == 1:
                move_prompt += f'In the {idx + 1}nd round, {role} choose to {move};\n'
            elif idx == 2:
                move_prompt += f'In the {idx + 1}rd round, {role} choose to {move};\n'
            else:
                raise ValueError

    recent_history_prompt = ''
    if recent_match_history:
        recent_history_prompt = (
            'Here are the previous completed games against this opponent '
            '(oldest to newest, up to the last 10 games):\n'
        )
        for idx, summary in enumerate(recent_match_history, 1):
            recent_history_prompt += f'{idx}. {summary}\n'

    prompt = f'In this match, your card is {card}.\n' \
             f'{move_prompt}\n' \
             f'{recent_history_prompt}\n' \
             f'Your legal moves are: <Pass>, <Bet>.'

    return _construct_head_prompt() + '\n' + prompt


if __name__ == '__main__':
    prompt = _construct_head_prompt()
    obs_prompt = construct_observation_prompt(
        {'card': 0, 'moves': 'pb', 'player_idx': 0})
    prompt += '\n' + obs_prompt
    print(prompt)
