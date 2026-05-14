import argparse
import copy
import json
import re
from pathlib import Path
from types import SimpleNamespace

from gamingbench.agents.prompt_agent import PromptAgent
from gamingbench.agents.theory_agent import TheoryAgent
from gamingbench.models.llm_model import LLMModel
from gamingbench.prompts.observation_prompts import construct_observation_prompt
from gamingbench.prompts.system_prompts import construct_system_prompt
from gamingbench.utils import utils


def make_agent(agent_type):
    agent_cls = TheoryAgent if agent_type == "theory" else PromptAgent
    name = "TheoryAgent" if agent_type == "theory" else "PromptAgent"
    return agent_cls(SimpleNamespace(
        agent_name=name,
        num_generations=1,
        majority_vote=False,
    ))


def make_model(model_name):
    return LLMModel(SimpleNamespace(
        llm_model_path=model_name,
        max_tokens=1024,
        timeout=120,
        temperature=0.2,
        nick_name=model_name,
    ))


def empty_board():
    return [[None for _ in range(3)] for _ in range(3)]


def render_board(board):
    header = "     C1  C2  C3"
    rows = [header]
    for row_idx, row in enumerate(board):
        cells = "  ".join(cell or "." for cell in row)
        rows.append(f"R{row_idx + 1}   {cells}")
    return "\n".join(rows)


def legal_moves(board):
    moves = []
    for row_idx in range(3):
        for col_idx in range(3):
            if board[row_idx][col_idx] is None:
                moves.append(f"<C{col_idx + 1}R{row_idx + 1}>")
    return moves


def normalize_move(text):
    match = re.search(r"<?\s*C([1-3])\s*R([1-3])\s*>?", text.strip(), re.IGNORECASE)
    if not match:
        return None
    return f"<C{match.group(1)}R{match.group(2)}>"


def parse_move(move):
    normalized = normalize_move(move or "")
    if normalized is None:
        return None
    match = re.search(r"C([1-3])R([1-3])", normalized)
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
    current_legal_moves = legal_moves(board)
    return {
        "board": render_board(board),
        "opponent_moves": copy.deepcopy(move_memory[opponent_idx]),
        "self_moves": copy.deepcopy(move_memory[player_idx]),
        "openspiel_legal_actions": list(range(len(current_legal_moves))),
        "legal_moves": current_legal_moves,
        "env_name": "tictactoe",
    }


def query_to_dict(query):
    return query.to_dict() if hasattr(query, "to_dict") else query


def append_jsonl(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def read_human_move(board):
    legal = legal_moves(board)
    while True:
        raw = input(f"Your move {legal}: ").strip()
        if raw.lower() in {"q", "quit", "exit"}:
            return None
        move = normalize_move(raw)
        if move in legal:
            return move
        print("Invalid move. Use a legal move like C2R2 or <C2R2>.")


def display_player_prompt(observation, step_prompt):
    system_prompt = construct_system_prompt(observation["env_name"])
    observation_prompt = construct_observation_prompt(
        observation, observation["env_name"])
    full_prompt = observation_prompt + "\n" + step_prompt
    print("\n" + "=" * 24 + " SYSTEM PROMPT " + "=" * 24)
    print(system_prompt)
    print("=" * 24 + " USER PROMPT " + "=" * 26)
    print(full_prompt)
    print("=" * 64)


def run_game(args):
    if args.overwrite and args.output_dir.exists():
        for path in [args.output_dir / "turns.jsonl", args.output_dir / "match.json"]:
            if path.exists():
                path.unlink()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    utils.LLMBenchLogger(str(args.output_dir / "run.log"))

    llm_agent = make_agent(args.llm_agent)
    llm_model = make_model(args.model)
    llm_agent.set_model(llm_model)

    board = empty_board()
    turns = []
    move_memory = {0: [], 1: []}
    marks = {0: "X", 1: "O"}
    human_player = args.human_player
    llm_player = 1 - human_player
    status = "Normal"
    agents_at_fault = []
    turn_idx = 0

    print(render_board(board))
    print("Enter moves as C2R2 or <C2R2>. Type q to stop.")

    while winner(board) is None and legal_moves(board):
        player_idx = turn_idx % 2
        state_before = render_board(board)
        observation = build_observation(board, move_memory, player_idx)

        if player_idx == human_player:
            actor = "Human"
            model = None
            display_player_prompt(
                observation,
                """You are the human player. Choose one legal action from the legal actions.

Input your action in the same format:
Action:
<CxRy>
""",
            )
            move = read_human_move(board)
            queries = []
            if move is None:
                status = "Stopped"
                break
        else:
            actor = llm_agent.agent_name
            model = llm_model.nick_name
            if len(observation["legal_moves"]) == 1:
                move = observation["legal_moves"][0]
                queries = []
            else:
                move, queries = llm_agent.step(copy.deepcopy(observation))
                move = normalize_move(move) or move
            print(f"LLM move: {move}")

        turn_record = {
            "turn_index": turn_idx,
            "player_index": player_idx,
            "actor": actor,
            "model": model,
            "mark": marks[player_idx],
            "state_before": state_before,
            "observation": observation,
            "legal_actions": observation["legal_moves"],
            "move": move,
            "queries": [query_to_dict(q) for q in queries],
        }

        if not is_valid_move(board, move):
            status = "Abnormal"
            agents_at_fault.append(actor)
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

        print(render_board(board))
        turn_idx += 1

    winning_mark = winner(board)
    if winning_mark is None:
        winner_name = ""
    elif winning_mark == marks[human_player]:
        winner_name = "Human"
    else:
        winner_name = f"{llm_agent.agent_name}_{llm_model.nick_name}"

    match = {
        "game": "tictactoe",
        "status": status,
        "winner": winner_name,
        "agents_at_fault": agents_at_fault,
        "human_player": human_player,
        "llm_player": llm_player,
        "llm_agent": llm_agent.agent_name,
        "llm_model": llm_model.nick_name,
        "final_board": render_board(board),
        "turns": turns,
    }
    write_json(args.output_dir / "match.json", match)
    print(json.dumps({
        "output_dir": str(args.output_dir),
        "status": status,
        "winner": winner_name,
        "num_turns": len(turns),
    }, indent=2))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--llm-agent", choices=["theory", "prompt"], default="theory")
    parser.add_argument("--human-player", type=int, choices=[0, 1], default=0)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments/tictactoe_human_vs_llm"),
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_game(parse_args())
