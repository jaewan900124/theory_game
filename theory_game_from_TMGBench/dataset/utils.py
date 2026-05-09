import json

def get_Nash_equilibrium(pA, pB, ban=None, banp=None):
    # pA: player A's payoff matrix
    # pB: player B's payoff matrix
    # ban: the restricted situation
    # banp: the restricted player
    Nash_equilibrium_choice, Nash_equilibrium_result = [], []
    for row in range(2):
        for column in range(2):
            alter_row, alter_column = 1 - row, 1 - column
            if ban is not None and (row + 1, column + 1) == ban: continue
            if (banp == "A" and (alter_row + 1, column + 1) == ban or pA[row][column] >= pA[alter_row][column]) \
            and (banp == "B" and (row + 1, alter_column + 1) == ban or pB[row][column] >= pB[row][alter_column]):
                Nash_equilibrium_choice.append((f"A{row + 1}", f"B{column + 1}"))
                Nash_equilibrium_result.append((pA[row][column], pB[row][column]))
    return Nash_equilibrium_choice, Nash_equilibrium_result
