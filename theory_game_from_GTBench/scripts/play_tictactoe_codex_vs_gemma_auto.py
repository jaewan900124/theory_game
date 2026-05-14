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
        max_tokens=2048,
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


def apply_move(board, move, mark):
    row, col = parse_move(move)
    board[row][col] = mark


def board_after(board, move, mark):
    new_board = copy.deepcopy(board)
    apply_move(new_board, move, mark)
    return new_board


def is_valid_move(board, move):
    parsed = parse_move(move)
    if parsed is None:
        return False
    row, col = parsed
    return board[row][col] is None


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


def minimax(board, current_mark, codex_mark, gemma_mark):
    winning_mark = winner(board)
    if winning_mark == codex_mark:
        return 1
    if winning_mark == gemma_mark:
        return -1
    moves = legal_moves(board)
    if not moves:
        return 0

    next_mark = gemma_mark if current_mark == codex_mark else codex_mark
    scores = [
        minimax(board_after(board, move, current_mark), next_mark, codex_mark, gemma_mark)
        for move in moves
    ]
    return max(scores) if current_mark == codex_mark else min(scores)


def find_immediate_move(board, mark):
    for move in legal_moves(board):
        if winner(board_after(board, move, mark)) == mark:
            return move
    return None


def choose_codex_move(board, codex_mark, gemma_mark):
    moves = legal_moves(board)
    immediate_win = find_immediate_move(board, codex_mark)
    immediate_block = find_immediate_move(board, gemma_mark)

    if immediate_win:
        chosen = immediate_win
        reason = "Codex has an immediate winning action and should take it."
    elif immediate_block:
        chosen = immediate_block
        reason = "Gemma has an immediate winning threat, so Codex must block it."
    else:
        scored = []
        for move in moves:
            score = minimax(board_after(board, move, codex_mark), gemma_mark, codex_mark, gemma_mark)
            scored.append((score, move))
        scored.sort(key=lambda item: (item[0], preference_rank(item[1])), reverse=True)
        chosen = scored[0][1]
        reason = "No immediate win or block exists, so Codex chooses the legal action with the best minimax continuation value."

    return chosen, {
        "selected_theory": "finite extensive-form game with perfect information",
        "immediate_win": immediate_win or "none",
        "immediate_block": immediate_block or "none",
        "continuation_rule": "backward-induction-style minimax over legal Tic-Tac-Toe continuations",
        "reason": reason,
        "action": chosen,
    }


def preference_rank(move):
    order = {
        "<C2R2>": 9,
        "<C1R1>": 8,
        "<C3R1>": 8,
        "<C1R3>": 8,
        "<C3R3>": 8,
        "<C2R1>": 7,
        "<C1R2>": 7,
        "<C3R2>": 7,
        "<C2R3>": 7,
    }
    return order.get(move, 0)


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


def query_repair_move(model, board, legal_actions):
    messages = [
        {
            "role": "system",
            "content": "You are playing Tic-Tac-Toe. Return exactly one legal action and no other text.",
        },
        {
            "role": "user",
            "content": (
                f"Current board:\n{render_board(board)}\n\n"
                f"Legal actions: {', '.join(legal_actions)}\n\n"
                "Choose exactly one action from the legal actions. "
                "Output format example: <C1R1>"
            ),
        },
    ]
    generations, completion_tokens, prompt_tokens = model.query(
        messages=messages,
        n=1,
        stop=None,
        prompt_type="move",
    )
    raw = generations[0] if generations else ""
    return normalize_move(raw) or raw, {
        "messages": messages,
        "raw_response": raw,
        "completion_tokens": completion_tokens,
        "prompt_tokens": prompt_tokens,
    }


def append_jsonl(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def run_game(args):
    if args.overwrite and args.output_dir.exists():
        for path in [args.output_dir / "turns.jsonl", args.output_dir / "match.json"]:
            if path.exists():
                path.unlink()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    utils.LLMBenchLogger(str(args.output_dir / "run.log"))

    gemma_agent = make_agent(args.llm_agent)
    gemma_model = make_model(args.model)
    gemma_agent.set_model(gemma_model)

    board = empty_board()
    turns = []
    move_memory = {0: [], 1: []}
    marks = {0: "X", 1: "O"}
    codex_player = args.codex_player
    gemma_player = 1 - codex_player
    status = "Normal"
    agents_at_fault = []
    turn_idx = 0

    while winner(board) is None and legal_moves(board):
        player_idx = turn_idx % 2
        state_before = render_board(board)
        observation = build_observation(board, move_memory, player_idx)
        queries = []
        codex_analysis = None

        if player_idx == codex_player:
            actor = "Codex"
            model = None
            move, codex_analysis = choose_codex_move(
                board,
                marks[codex_player],
                marks[gemma_player],
            )
            print(f"Codex move: {move}")
        else:
            actor = gemma_agent.agent_name
            model = gemma_model.nick_name
            repair_query = None
            repair_used = False
            if len(observation["legal_moves"]) == 1:
                move = observation["legal_moves"][0]
            else:
                move, queries = gemma_agent.step(copy.deepcopy(observation))
                move = normalize_move(move) or move
                if not is_valid_move(board, move):
                    repair_used = True
                    move, repair_query = query_repair_move(
                        gemma_model,
                        board,
                        observation["legal_moves"],
                    )
                if not is_valid_move(board, move):
                    move = observation["legal_moves"][0]
                    repair_query = repair_query or {}
                    repair_query["deterministic_fallback"] = (
                        "Gemma returned no parseable legal action after repair; "
                        "the first legal action was used to complete the automated pass."
                    )
            print(f"Gemma move: {move}")

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
            "codex_analysis": codex_analysis,
            "repair_used": repair_used if player_idx != codex_player else False,
            "repair_query": repair_query if player_idx != codex_player else None,
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
        returns = [0, 0]
    elif winning_mark == marks[codex_player]:
        winner_name = "Codex"
        returns = [1, -1] if codex_player == 0 else [-1, 1]
    else:
        winner_name = f"{gemma_agent.agent_name}_{gemma_model.nick_name}"
        returns = [-1, 1] if codex_player == 0 else [1, -1]

    match = {
        "game": "tictactoe",
        "status": status,
        "winner": winner_name if status == "Normal" else "",
        "returns": returns,
        "agents_at_fault": agents_at_fault,
        "codex_player": codex_player,
        "gemma_player": gemma_player,
        "gemma_agent": gemma_agent.agent_name,
        "gemma_model": gemma_model.nick_name,
        "final_board": render_board(board),
        "turns": turns,
    }
    write_json(args.output_dir / "match.json", match)
    print(json.dumps({
        "output_dir": str(args.output_dir),
        "status": status,
        "winner": match["winner"],
        "returns": returns,
        "num_turns": len(turns),
    }, indent=2, ensure_ascii=False))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gemma4:31b")
    parser.add_argument("--llm-agent", choices=["theory", "prompt"], default="theory")
    parser.add_argument("--codex-player", type=int, choices=[0, 1], default=0)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments/tictactoe_codex_vs_gemma4_31b_auto"),
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_game(parse_args())
