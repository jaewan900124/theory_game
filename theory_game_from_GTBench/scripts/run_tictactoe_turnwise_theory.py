import argparse
import copy
import json
import re
from pathlib import Path
from types import SimpleNamespace

from gamingbench.agents.prompt_agent import PromptAgent
from gamingbench.agents.theory_agent import TheoryAgent
from gamingbench.models.llm_model import LLMModel
from gamingbench.utils import utils


def make_agent(agent_cls, name):
    return agent_cls(SimpleNamespace(
        agent_name=name,
        num_generations=1,
        majority_vote=False,
    ))


def make_gpt4o_mini_model():
    return LLMModel(SimpleNamespace(
        llm_model_path="gpt-4o-mini",
        max_tokens=1024,
        timeout=120,
        temperature=0.2,
        nick_name="gpt-4o-mini",
    ))


def query_to_dict(query):
    return query.to_dict() if hasattr(query, "to_dict") else query


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def append_jsonl(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")


def empty_board():
    return [[None for _ in range(3)] for _ in range(3)]


def render_board(board):
    rows = []
    for row in board:
        rows.append(" ".join(cell or "." for cell in row))
    return "\n".join(rows)


def legal_moves(board):
    moves = []
    for row_idx in range(3):
        for col_idx in range(3):
            if board[row_idx][col_idx] is None:
                moves.append(f"<C{col_idx + 1}R{row_idx + 1}>")
    return moves


def parse_move(move):
    match = re.search(r"C([1-3])R([1-3])", move or "")
    if not match:
        return None
    col = int(match.group(1)) - 1
    row = int(match.group(2)) - 1
    return row, col


def is_valid_move(board, move):
    parsed = parse_move(move)
    if parsed is None:
        return False
    row, col = parsed
    return board[row][col] is None


def apply_move(board, move, mark):
    row, col = parse_move(move)
    board[row][col] = mark


def winner(board):
    lines = []
    lines.extend(board)
    lines.extend([[board[0][c], board[1][c], board[2][c]] for c in range(3)])
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])
    for line in lines:
        if line[0] is not None and line[0] == line[1] == line[2]:
            return line[0]
    return None


def build_observation(board, move_memory, player_idx):
    opponent_idx = 1 - player_idx
    valid_action = legal_moves(board)
    observation_dict = {
        "opponent_moves": copy.deepcopy(move_memory[opponent_idx]),
        "self_moves": copy.deepcopy(move_memory[player_idx]),
    }
    observation_dict["openspiel_legal_actions"] = list(range(len(valid_action)))
    observation_dict["legal_moves"] = valid_action
    observation_dict["env_name"] = "tictactoe"
    return observation_dict, valid_action


def run_match(args):
    if args.overwrite and args.output_dir.exists():
        for path in [args.output_dir / "turns.jsonl", args.output_dir / "match.json"]:
            if path.exists():
                path.unlink()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    utils.LLMBenchLogger(str(args.output_dir / "run.log"))

    agents = [None, None]
    agents[args.theory_player] = make_agent(TheoryAgent, "TheoryAgent")
    agents[1 - args.theory_player] = make_agent(PromptAgent, "PromptAgent")

    models = [make_gpt4o_mini_model(), make_gpt4o_mini_model()]
    for agent, model in zip(agents, models):
        agent.set_model(model)

    turns = []
    turn_idx = 0
    status = "Normal"
    agents_at_fault = []
    board = empty_board()
    move_memory = {0: [], 1: []}
    marks = {0: "X", 1: "O"}
    while winner(board) is None and legal_moves(board):
        player_idx = turn_idx % 2
        agent = agents[player_idx]
        state_before = render_board(board)
        observation_dict, valid_actions = build_observation(board, move_memory, player_idx)

        if len(valid_actions) == 1:
            move = valid_actions[0]
            query_list = []
        else:
            move, query_list = agent.step(copy.deepcopy(observation_dict))

        turn_record = {
            "turn_index": turn_idx,
            "player_index": player_idx,
            "agent": agent.agent_name,
            "model": models[player_idx].nick_name,
            "state_before": state_before,
            "observation": observation_dict,
            "legal_actions": valid_actions,
            "move": move,
            "queries": [query_to_dict(q) for q in query_list],
        }

        if not is_valid_move(board, move):
            status = "Abnormal"
            agents_at_fault.append(agent.agent_name)
            turn_record["status_after_turn"] = status
            turn_record["state_after"] = render_board(board)
            turns.append(turn_record)
            append_jsonl(args.output_dir / "turns.jsonl", turn_record)
            break

        apply_move(board, move, marks[player_idx])
        move_memory[player_idx].append(move)

        turn_record["status_after_turn"] = "Normal"
        turn_record["state_after"] = render_board(board)
        turns.append(turn_record)
        append_jsonl(args.output_dir / "turns.jsonl", turn_record)
        turn_idx += 1

    winning_mark = winner(board)
    if winning_mark == marks[0]:
        returns = [1, -1]
    elif winning_mark == marks[1]:
        returns = [-1, 1]
    elif status == "Normal":
        returns = [0, 0]
    else:
        returns = [0, 0]
    if status == "Normal":
        if returns[0] > returns[1]:
            winner_name = f"{agents[0].agent_name}_{models[0].nick_name}"
        elif returns[1] > returns[0]:
            winner_name = f"{agents[1].agent_name}_{models[1].nick_name}"
        else:
            winner_name = ""
    else:
        winner_name = ""

    match = {
        "game": "tictactoe",
        "status": status,
        "agents_at_fault": agents_at_fault,
        "winner": winner_name,
        "returns": returns,
        "theory_player": args.theory_player,
        "agents": [
            {"player_index": 0, "agent": agents[0].agent_name, "model": models[0].nick_name},
            {"player_index": 1, "agent": agents[1].agent_name, "model": models[1].nick_name},
        ],
        "turns": turns,
    }
    write_json(args.output_dir / "match.json", match)
    print(json.dumps({
        "output_dir": str(args.output_dir),
        "status": status,
        "winner": winner_name,
        "returns": returns,
        "num_turns": len(turns),
    }, indent=2))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments/tictactoe_turnwise_theory_gpt4omini"),
    )
    parser.add_argument("--theory-player", type=int, choices=[0, 1], default=0)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_match(parse_args())
