import argparse
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from gamingbench.prompts.theory_prompt_builder import build_theory_prompt
from run_auto_theory_loop import (
    RULES,
    breakthrough_apply,
    breakthrough_legal,
    c4_drop,
    c4_legal,
    c4_win,
    exact_legal_from_text,
    line_winner,
    write_json,
)


MODEL = "gemma4:31b"
RNG = random.Random(23)
OUTPUT_DIR = Path("experiments/gemma4_31b_prompt_ablation")
RECORDS_PATH = OUTPUT_DIR / "matches.jsonl"
SUMMARY_PATH = OUTPUT_DIR / "summary.md"


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ollama_chat(prompt, legal_actions, style):
    base_url = os.environ.get("OLLAMA_BASE_URL")
    if not base_url:
        return legal_actions[0], "fallback: OLLAMA_BASE_URL is not configured", True

    endpoint = base_url.rstrip("/")
    if endpoint.endswith("/v1"):
        endpoint = endpoint[:-3]

    system_prompt = (
        "You are playing a game. You may analyze concisely, but your final answer must contain exactly one legal action label."
        if style == "theory"
        else "You are playing a game. Choose exactly one legal action. Return only the action label."
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 768 if style == "theory" else 64,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint + "/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        response = body["message"]["content"]
        action = exact_legal_from_text(response, legal_actions)
        if action:
            return action, response, False
        repair_prompt = f"Invalid answer:\n{response}\n\nReturn exactly one legal action from this list: {legal_actions}"
        payload["messages"] = [
            {"role": "system", "content": "Return exactly one legal action label and nothing else."},
            {"role": "user", "content": repair_prompt},
        ]
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(endpoint + "/api/chat", data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        repaired_response = body["message"]["content"]
        repaired_action = exact_legal_from_text(repaired_response, legal_actions)
        if repaired_action:
            return repaired_action, response + "\nREPAIR:\n" + repaired_response, True
        return legal_actions[0], response + "\nFALLBACK:" + legal_actions[0], True
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
        return legal_actions[0], f"fallback after query error: {exc}", True


def theory_prompt(game, state, legal_actions, fields):
    pkg = build_theory_prompt(game, state, legal_actions, fields)
    mapping = pkg["theory_mapping"]
    schema = pkg["analysis_schema"]
    return f"""Game: {mapping['display_name']} ({game})
Rules: {RULES[game]}
State: {json.dumps(state, ensure_ascii=False)}
Legal actions: {json.dumps(legal_actions, ensure_ascii=False)}

Use this fixed theory mapping:
- Game type: {mapping['game_type']}
- Solution concept: {mapping['solution_concept']}
- Osborne/Rubinstein mapping: {json.dumps(mapping['osborne_rubinstein_mapping'], ensure_ascii=False)}
- Why fixed: {mapping['why_fixed']}

Analyze the current state using these fields when available:
{json.dumps(schema['analysis_fields'], ensure_ascii=False)}

Compare the strongest legal candidates using:
{json.dumps(schema['candidate_action_fields'], ensure_ascii=False)}

Choose exactly one legal action. End your answer with:
Action: <legal_action>
"""


def baseline_prompt(game, state, legal_actions):
    return f"""Game: {game}
Rules: {RULES[game]}
State: {json.dumps(state, ensure_ascii=False)}
Legal actions: {json.dumps(legal_actions, ensure_ascii=False)}

You must choose a legal action to set up advantages.
Return only your action wrapped with <>.
"""


def choose(game, state, legal_actions, player_style, fields=None):
    if player_style == "theory":
        prompt = theory_prompt(game, state, legal_actions, fields or {})
    else:
        prompt = baseline_prompt(game, state, legal_actions)
    action, response, repaired = ollama_chat(prompt, legal_actions, player_style)
    return {
        "style": player_style,
        "model": MODEL,
        "prompt": prompt,
        "raw_response": response,
        "action": action,
        "repaired": repaired,
    }


def append_match(match):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with RECORDS_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(match, ensure_ascii=False) + "\n")


def run_tictactoe():
    board = [["." for _ in range(3)] for _ in range(3)]
    turns = []
    for turn in range(9):
        legal = [f"<C{c + 1}R{r + 1}>" for r in range(3) for c in range(3) if board[r][c] == "."]
        style = "theory" if turn % 2 == 0 else "baseline"
        state = {"board": ["".join(row) for row in board], "history": [t["action"] for t in turns], "mark_to_play": "X" if style == "theory" else "O"}
        fields = {"board": state["board"], "self_mark": state["mark_to_play"], "legal_actions": legal}
        decision = choose("tictactoe", state, legal, style, fields)
        c, r = int(decision["action"][2]) - 1, int(decision["action"][4]) - 1
        board[r][c] = "X" if style == "theory" else "O"
        turns.append(decision)
        if line_winner(board, "X") or line_winner(board, "O"):
            break
    winner = "theory" if line_winner(board, "X") else "baseline" if line_winner(board, "O") else "draw"
    return {"game": "tictactoe", "winner": winner, "turns": turns, "final_state": {"board": ["".join(row) for row in board]}}


def run_connect4():
    board = [["." for _ in range(7)] for _ in range(6)]
    turns = []
    for turn in range(42):
        legal = c4_legal(board)
        style = "theory" if turn % 2 == 0 else "baseline"
        state = {"board": ["".join(row) for row in board], "history": [t["action"] for t in turns], "disc_to_play": "X" if style == "theory" else "O"}
        fields = {"board": state["board"], "column_heights": [sum(board[r][c] != "." for r in range(6)) for c in range(7)], "legal_actions": legal}
        decision = choose("connect4", state, legal, style, fields)
        c4_drop(board, decision["action"], "X" if style == "theory" else "O")
        turns.append(decision)
        if c4_win(board, "X") or c4_win(board, "O"):
            break
    winner = "theory" if c4_win(board, "X") else "baseline" if c4_win(board, "O") else "draw"
    return {"game": "connect4", "winner": winner, "turns": turns, "final_state": {"board": ["".join(row) for row in board]}}


def run_breakthrough():
    board = [["O"] * 3, ["O"] * 3, ["."] * 3, ["."] * 3, ["X"] * 3, ["X"] * 3]
    turns = []
    for turn in range(40):
        player = turn % 2
        style = "theory" if player == 0 else "baseline"
        legal = breakthrough_legal(board, player)
        if not legal:
            break
        state = {"board": ["".join(row) for row in board], "history": [t["action"] for t in turns], "piece_to_play": "X" if player == 0 else "O"}
        fields = {"board": state["board"], "legal_actions": legal, "capture_moves": [a for a in legal if a[1] != a[5]]}
        decision = choose("breakthrough", state, legal, style, fields)
        breakthrough_apply(board, decision["action"])
        turns.append(decision)
        if "X" in board[0] or "O" in board[-1] or not any("X" in row for row in board) or not any("O" in row for row in board):
            break
    winner = "theory" if "X" in board[0] or not any("O" in row for row in board) else "baseline" if "O" in board[-1] or not any("X" in row for row in board) else "draw"
    return {"game": "breakthrough", "winner": winner, "turns": turns, "final_state": {"board": ["".join(row) for row in board]}}


def run_nim():
    piles = [1, 3, 5, 7]
    turns = []
    turn = 0
    while sum(piles) > 0:
        style = "theory" if turn % 2 == 0 else "baseline"
        legal = [f"<pile:{i + 1}, take:{n}>" for i, p in enumerate(piles) for n in range(1, p + 1)]
        xor = 0
        for p in piles:
            xor ^= p
        state = {"piles": piles[:], "history": [t["action"] for t in turns]}
        decision = choose("nim", state, legal, style, {"pile_sizes": piles[:], "nim_sum": xor, "legal_actions": legal})
        nums = [int(x) for x in re.findall(r"\d+", decision["action"])]
        piles[nums[0] - 1] -= nums[1]
        turns.append(decision)
        turn += 1
    winner = turns[-1]["style"] if turns else "none"
    return {"game": "nim", "winner": winner, "turns": turns, "final_state": {"piles": piles}}


def run_pig():
    scores = [0, 0]
    turns = []
    round_index = 0
    while max(scores) < 20 and round_index < 40:
        player = round_index % 2
        style = "theory" if player == 0 else "baseline"
        turn_total = 0
        while True:
            legal = ["<roll>", "<stop>"]
            state = {"scores": scores[:], "turn_total": turn_total, "player": style, "history": [t["action"] for t in turns]}
            decision = choose("pig", state, legal, style, {"self_score": scores[player], "opponent_score": scores[1 - player], "turn_total": turn_total})
            if decision["action"] == "<stop>":
                scores[player] += turn_total
                decision["banked"] = turn_total
                turns.append(decision)
                break
            die = RNG.randint(1, 6)
            decision["die"] = die
            turns.append(decision)
            if die == 1:
                break
            turn_total += die
        round_index += 1
    winner = "theory" if scores[0] > scores[1] else "baseline" if scores[1] > scores[0] else "draw"
    return {"game": "pig", "winner": winner, "turns": turns, "final_state": {"scores": scores}}


def run_first_sealed_auction():
    legal = [f"<{i}>" for i in range(11)]
    theory = choose("first_sealed_auction", {"private_value": 7, "bidder": "theory", "bid_range": [0, 10]}, legal, "theory", {"private_valuation": 7, "bid_range": [0, 10]})
    baseline = choose("first_sealed_auction", {"private_value": 6, "bidder": "baseline", "bid_range": [0, 10]}, legal, "baseline")
    tbid, bbid = int(re.findall(r"\d+", theory["action"])[0]), int(re.findall(r"\d+", baseline["action"])[0])
    winner = "theory" if tbid > bbid else "baseline" if bbid > tbid else "draw"
    return {"game": "first_sealed_auction", "winner": winner, "turns": [theory, baseline], "final_state": {"theory_bid": tbid, "baseline_bid": bbid}}


def run_kuhn_poker():
    theory = choose("kuhn_poker", {"private_card": "K", "public_history": [], "pot": 2}, ["<Pass>", "<Bet>"], "theory", {"private_card": "K", "pot_size": 2})
    baseline = choose("kuhn_poker", {"private_card": "Q", "public_history": [theory["action"]], "pot": 2}, ["<Pass>", "<Bet>"], "baseline")
    return {"game": "kuhn_poker", "winner": "not_scored", "turns": [theory, baseline], "final_state": {"cards": {"theory": "K", "baseline": "Q"}}}


def run_liars_dice():
    legal = ["<1 dices, 1 value>", "<1 dices, 2 value>", "<1 dices, 3 value>", "<1 dices, 4 value>", "<1 dices, 5 value>", "<1 dices, 6 value>"]
    theory = choose("liars_dice", {"self_die": 4, "public_history": []}, legal, "theory", {"self_dice": [4], "public_bid_history": []})
    response_legal = ["<1 dices, 5 value>", "<1 dices, 6 value>", "<2 dices, 1 value>", "<2 dices, 2 value>", "<2 dices, 3 value>", "<2 dices, 4 value>", "<2 dices, 5 value>", "<2 dices, 6 value>", "<Liar>"]
    baseline = choose("liars_dice", {"self_die": 2, "public_history": [theory["action"]]}, response_legal, "baseline")
    return {"game": "liars_dice", "winner": "not_scored", "turns": [theory, baseline], "final_state": {"dice": {"theory": 4, "baseline": 2}}}


def run_negotiation():
    legal = [f"<Proposal: [{a}, {b}, {c}]>" for a in range(6) for b in range(6) for c in range(6)]
    theory = choose("negotiation", {"item_pool": [5, 5, 5], "self_value_vector": [4, 2, 1], "public_history": []}, legal, "theory", {"item_pool": [5, 5, 5], "self_value_vector": [4, 2, 1]})
    baseline = choose("negotiation", {"item_pool": [5, 5, 5], "received_proposal": theory["action"]}, ["<Agree>"] + legal[:20], "baseline")
    return {"game": "negotiation", "winner": "agreement" if baseline["action"] == "<Agree>" else "not_scored", "turns": [theory, baseline], "final_state": {"proposal": theory["action"], "response": baseline["action"]}}


def run_prisoners_dilemma():
    history = []
    turns = []
    for round_index in range(5):
        legal = ["<Silent>", "<Testify>"]
        theory = choose("prisoners_dilemma", {"round": round_index, "history": history, "player": "theory"}, legal, "theory", {"round_index": round_index, "public_action_history": history})
        baseline = choose("prisoners_dilemma", {"round": round_index, "history": history, "player": "baseline"}, legal, "baseline")
        history.append({"theory": theory["action"], "baseline": baseline["action"]})
        turns.extend([theory, baseline])
    return {"game": "prisoners_dilemma", "winner": "not_scored", "turns": turns, "final_state": {"rounds": history}}


RUNNERS = {
    "tictactoe": run_tictactoe,
    "connect4": run_connect4,
    "breakthrough": run_breakthrough,
    "first_sealed_auction": run_first_sealed_auction,
    "liars_dice": run_liars_dice,
    "negotiation": run_negotiation,
    "nim": run_nim,
    "pig": run_pig,
    "kuhn_poker": run_kuhn_poker,
    "prisoners_dilemma": run_prisoners_dilemma,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", nargs="+", choices=list(RUNNERS), default=list(RUNNERS))
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RECORDS_PATH.write_text("", encoding="utf-8")
    completed, failed = [], {}
    for idx, game in enumerate(args.games, 1):
        print(f"[{idx}/{len(args.games)}] START {game}", flush=True)
        try:
            match = RUNNERS[game]()
            match["updated_at"] = now()
            append_match(match)
            write_json(OUTPUT_DIR / game / "match.json", match)
            completed.append(game)
            print(f"[{idx}/{len(args.games)}] DONE  {game} winner={match['winner']}", flush=True)
        except Exception as exc:
            failed[game] = repr(exc)
            print(f"[{idx}/{len(args.games)}] FAIL  {game}: {exc!r}", flush=True)
    SUMMARY_PATH.write_text(
        "# Gemma4 31B Prompt Ablation\n\n"
        f"Updated: {now()}\n\n"
        "Players:\n"
        "- theory: gemma4:31b with fixed theory-guided dynamic prompt\n"
        "- baseline: gemma4:31b with baseline action-only prompt\n\n"
        f"Completed: {completed}\n\n"
        f"Failed: {failed or 'none'}\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "complete" if not failed else "partial", "completed": completed, "failed": failed, "output_dir": str(OUTPUT_DIR)}, indent=2))


if __name__ == "__main__":
    main()
