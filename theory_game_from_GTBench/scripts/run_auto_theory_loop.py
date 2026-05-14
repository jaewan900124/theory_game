import argparse
import copy
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gamingbench.prompts.theory_prompt_builder import (
    build_analysis_output,
    build_theory_prompt,
    load_game_theory_mapping,
    load_theory_analysis_schema,
)


OUTPUT_DIR = Path("experiments/auto_theory_loop")
RECORDS_PATH = OUTPUT_DIR / "theory_records.jsonl"
STATUS_PATH = OUTPUT_DIR / "status.json"
SUMMARY_PATH = OUTPUT_DIR / "summary.md"
OPPONENT = "gemma4:31b"
RNG = random.Random(17)
GAME_THEORY_MAPPING = load_game_theory_mapping()
THEORY_SCHEMA = load_theory_analysis_schema()


THEORY = {
    "tictactoe": (
        "finite extensive-form game with perfect information; backward induction and maxmin defense",
        "Tic-Tac-Toe has a finite game tree, perfect observation of moves, and zero-sum outcomes, so lookahead can identify wins, blocks, and drawing defenses.",
    ),
    "connect4": (
        "finite extensive-form game with perfect information; backward-induction-style lookahead and maxmin defense",
        "Connect4 is a deterministic, alternating-move, perfect-information game where local threats and blocking moves approximate backward induction in the large game tree.",
    ),
    "breakthrough": (
        "finite extensive-form game with perfect information; backward-induction-style race and capture analysis",
        "Breakthrough exposes the full board and has deterministic legal moves, so advancement, captures, and promotion threats can be compared by lookahead.",
    ),
    "first_sealed_auction": (
        "Bayesian private-value strategic game; bid shading and expected payoff",
        "The bidder observes its own valuation but not the opponent's, so the optimal bid trades win probability against surplus.",
    ),
    "liars_dice": (
        "imperfect-information extensive-form game with chance; Bayesian belief updating and bluff detection",
        "Each player sees private dice and public claims, so decisions depend on posterior beliefs about hidden dice and incentives to bluff.",
    ),
    "negotiation": (
        "bargaining game with private preferences and strategic communication",
        "Players know their own utilities and observe offers, so proposals should trade low-value items for high-value items while preserving agreement incentives.",
    ),
    "nim": (
        "finite extensive-form game with perfect information; backward induction and combinatorial-game state analysis",
        "Nim has a compact deterministic state where the xor of pile sizes identifies losing and winning continuations under optimal play.",
    ),
    "pig": (
        "stochastic dynamic decision problem with chance nodes; expected value and stopping-risk analysis",
        "Pig alternates decisions with die-roll chance nodes, so rolling compares expected gain against bust risk and score-race pressure.",
    ),
    "kuhn_poker": (
        "imperfect-information extensive-form game; information sets, belief updating, and mixed bluff reasoning",
        "Kuhn poker combines private cards with public betting history, requiring beliefs over the opponent's hidden card and mixed incentives.",
    ),
    "prisoners_dilemma": (
        "repeated strategic game; history-dependent cooperation and retaliation reasoning",
        "The repeated Prisoner's Dilemma makes current incentives depend on the public action history, enabling cooperation, punishment, and forgiveness.",
    ),
}


RULES = {
    "tictactoe": "Players alternate marking a 3x3 board. Three in a row wins; a full board without a line is a draw.",
    "connect4": "Players drop discs into seven columns. Four connected discs horizontally, vertically, or diagonally wins.",
    "breakthrough": "Players move pawns forward or diagonally forward to capture. Reaching the far rank or eliminating all opposing pawns wins.",
    "first_sealed_auction": "Each bidder privately values the item and submits one sealed bid. Highest bid wins and pays its own bid.",
    "liars_dice": "Players have private dice and make increasing public claims about quantity and face value; a liar call checks the last claim.",
    "negotiation": "Players divide a fixed item pool while privately valuing item types. Agreement fixes the allocation; otherwise bargaining continues.",
    "nim": "Players remove one or more tokens from exactly one pile. The player taking the last token wins.",
    "pig": "On each turn, a player may roll to add to the turn total or hold to bank it. Rolling one loses the turn total.",
    "kuhn_poker": "Each player gets one private card from J,Q,K and chooses pass or bet in a one-card betting game.",
    "prisoners_dilemma": "Each round both players choose Silent or Testify. Repeated play rewards mutual cooperation but creates defection incentives.",
}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def append_jsonl(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")


def write_summary(completed, failed, game_dirs, next_action):
    lines = [
        "# Auto Theory Loop Summary",
        "",
        f"Updated: {now()}",
        "",
        "## Completed Games",
    ]
    lines.extend(f"- {game}: `{game_dirs[game]}`" for game in completed)
    lines.extend(["", "## Failed Games"])
    lines.extend([f"- {game}: {reason}" for game, reason in failed.items()] or ["- none"])
    lines.extend(["", "## Next Action", next_action])
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_status(status, loop, completed, failed, current_game=None, reason=""):
    write_json(
        STATUS_PATH,
        {
            "status": status,
            "loop": loop,
            "current_game": current_game,
            "completed_games": completed,
            "failed_games": failed,
            "reason": reason,
            "updated_at": now(),
        },
    )


def exact_legal_from_text(text, legal_actions):
    if not text:
        return None
    for action in legal_actions:
        if action in text:
            return action
    angle = re.findall(r"<[^>]+>", text)
    for candidate in angle:
        for action in legal_actions:
            if candidate.lower() == action.lower():
                return action
    return None


def query_gemma(prompt, legal_actions):
    base_url = os.environ.get("OLLAMA_BASE_URL")
    if not base_url:
        return legal_actions[0], f"fallback: OLLAMA_BASE_URL is not configured; used {legal_actions[0]}", True

    def post(user_prompt):
        endpoint = base_url.rstrip("/")
        if endpoint.endswith("/v1"):
            endpoint = endpoint[:-3]
        payload = {
            "model": OPPONENT,
            "messages": [
                {"role": "system", "content": "Choose exactly one legal game action. Return only the action."},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 32,
            },
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint + "/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["message"]["content"]

    try:
        first = post(prompt)
        parsed = exact_legal_from_text(first, legal_actions)
        if parsed:
            return parsed, first, False
        repair_prompt = f"Your previous answer was invalid: {first}\nOutput exactly one legal action from: {legal_actions}"
        second = post(repair_prompt)
        parsed = exact_legal_from_text(second, legal_actions)
        if parsed:
            return parsed, second, True
        return legal_actions[0], f"{first}\nREPAIR:{second}\nFALLBACK:{legal_actions[0]}", True
    except (urllib.error.URLError, KeyError, TimeoutError, json.JSONDecodeError) as exc:
        return legal_actions[0], f"fallback after query error: {exc}", True


def training_prompt(game, state, legal_actions, fields):
    return build_theory_prompt(
        game,
        state,
        legal_actions,
        fields,
        mapping=GAME_THEORY_MAPPING,
        schema_config=THEORY_SCHEMA,
    )


def make_record(game, turn, state, legal_actions, fields, analysis, action, extra=None):
    selected, applicability = THEORY[game]
    prompt_package = training_prompt(game, state, legal_actions, fields)
    theory_mapping = prompt_package["theory_mapping"]
    analysis_output = build_analysis_output(
        action=action,
        rationale=analysis,
        state_fields=fields,
        facts=[
            f"Game rule summary: {RULES[game]}",
            f"Legal actions available: {legal_actions}",
        ],
    )
    analysis_output["decision_problem"] = f"Choose one legal action for Codex in the current {theory_mapping['display_name']} state."
    analysis_output["strategic_objective"] = theory_mapping["output_focus"]
    completion = json.dumps(analysis_output, ensure_ascii=False)
    record = {
        "game": game,
        "match_index": 0,
        "turn_index": turn,
        "actor": "Codex",
        "opponent": OPPONENT,
        "state": copy.deepcopy(state),
        "legal_actions": copy.deepcopy(legal_actions),
        "game_rule_summary": RULES[game],
        "selected_theory": selected,
        "theory_applicability": applicability,
        "theory_mapping": copy.deepcopy(theory_mapping),
        "analysis_schema_key": prompt_package["schema_key"],
        "analysis_schema": copy.deepcopy(prompt_package["analysis_schema"]),
        "state_fields": copy.deepcopy(fields),
        "analysis": analysis,
        "chosen_action": action,
        "analysis_prompt": prompt_package["prompt"],
        "analysis_output": analysis_output,
        "training_prompt": prompt_package["prompt"],
        "training_completion": completion,
        "opponent_prompt": "",
        "opponent_response": "",
        "status": "ok",
    }
    if extra:
        record.update(copy.deepcopy(extra))
    append_jsonl(RECORDS_PATH, record)
    return record


def opponent_action(game, state, legal_actions):
    prompt = (
        f"Game: {game}\nRules: {RULES[game]}\nState: {json.dumps(state, ensure_ascii=False)}\n"
        f"Legal actions: {legal_actions}\nChoose exactly one legal action."
    )
    action, response, repaired = query_gemma(prompt, legal_actions)
    return action, prompt, response, repaired


def line_winner(board, mark):
    lines = board + [[board[r][c] for r in range(3)] for c in range(3)]
    lines += [[board[0][0], board[1][1], board[2][2]], [board[0][2], board[1][1], board[2][0]]]
    return any(line == [mark, mark, mark] for line in lines)


def run_tictactoe(game_dir):
    board = [["." for _ in range(3)] for _ in range(3)]
    records, history = [], []
    order = ["<C2R2>", "<C1R1>", "<C3R1>", "<C1R3>", "<C3R3>", "<C2R1>", "<C1R2>", "<C3R2>", "<C2R3>"]
    for turn in range(9):
        legal = [f"<C{c + 1}R{r + 1}>" for r in range(3) for c in range(3) if board[r][c] == "."]
        if turn % 2 == 0:
            chosen = next(a for a in order if a in legal)
            state = {"board": ["".join(row) for row in board], "history": history}
            fields = {"board": state["board"], "self_mark": "X", "opponent_mark": "O", "move_number": turn}
            analysis = "Take the highest-priority minimax opening or continuation square, preserving center/corner control and avoiding immediate tactical concessions."
            records.append(make_record("tictactoe", turn, state, legal, fields, analysis, chosen))
        else:
            chosen, prompt, response, repaired = opponent_action("tictactoe", {"board": ["".join(row) for row in board], "history": history}, legal)
            if records:
                records[-1]["opponent_prompt"] = prompt
                records[-1]["opponent_response"] = response
                records[-1]["status"] = "repaired" if repaired else "ok"
        c, r = int(chosen[2]) - 1, int(chosen[4]) - 1
        board[r][c] = "X" if turn % 2 == 0 else "O"
        history.append(chosen)
        if line_winner(board, "X") or line_winner(board, "O"):
            break
    write_json(game_dir / "match.json", {"game": "tictactoe", "history": history, "final_board": board, "records": records})


def c4_legal(board):
    return [f"<C{c + 1}>" for c in range(7) if board[0][c] == "."]


def c4_drop(board, action, mark):
    col = int(action[2]) - 1
    for row in range(5, -1, -1):
        if board[row][col] == ".":
            board[row][col] = mark
            return


def c4_win(board, mark):
    dirs = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for r in range(6):
        for c in range(7):
            if board[r][c] != mark:
                continue
            for dr, dc in dirs:
                if all(0 <= r + i * dr < 6 and 0 <= c + i * dc < 7 and board[r + i * dr][c + i * dc] == mark for i in range(4)):
                    return True
    return False


def run_connect4(game_dir):
    board = [["." for _ in range(7)] for _ in range(6)]
    records, history = [], []
    preference = ["<C4>", "<C3>", "<C5>", "<C2>", "<C6>", "<C1>", "<C7>"]
    for turn in range(42):
        legal = c4_legal(board)
        state = {"board": ["".join(row) for row in board], "history": history}
        if turn % 2 == 0:
            chosen = next(a for a in preference if a in legal)
            fields = {"center_control": "<C4>" in legal, "heights": [sum(board[r][c] != "." for r in range(6)) for c in range(7)]}
            analysis = "Prefer central columns because they participate in more four-in-a-row lines, while staying legal and maintaining maxmin defensive flexibility."
            records.append(make_record("connect4", turn, state, legal, fields, analysis, chosen))
        else:
            chosen, prompt, response, repaired = opponent_action("connect4", state, legal)
            if records:
                records[-1].update({"opponent_prompt": prompt, "opponent_response": response, "status": "repaired" if repaired else "ok"})
        c4_drop(board, chosen, "X" if turn % 2 == 0 else "O")
        history.append(chosen)
        if c4_win(board, "X") or c4_win(board, "O"):
            break
    write_json(game_dir / "match.json", {"game": "connect4", "history": history, "final_board": board, "records": records})


def run_nim(game_dir):
    piles = [1, 3, 5, 7]
    records, history, turn = [], [], 0
    while sum(piles) > 0:
        legal = [f"<pile:{i + 1}, take:{n}>" for i, p in enumerate(piles) for n in range(1, p + 1)]
        state = {"piles": piles[:], "history": history}
        if turn % 2 == 0:
            xor = 0
            for p in piles:
                xor ^= p
            chosen = legal[0]
            if xor:
                for i, p in enumerate(piles):
                    target = p ^ xor
                    if target < p:
                        chosen = f"<pile:{i + 1}, take:{p - target}>"
                        break
            fields = {"nim_sum": xor, "piles": piles[:], "winning_state": xor != 0}
            analysis = "Use the nim-sum. When it is nonzero, move to xor zero; otherwise choose a smallest legal reduction and preserve playability."
            records.append(make_record("nim", turn, state, legal, fields, analysis, chosen))
        else:
            chosen, prompt, response, repaired = opponent_action("nim", state, legal)
            if records:
                records[-1].update({"opponent_prompt": prompt, "opponent_response": response, "status": "repaired" if repaired else "ok"})
        nums = [int(x) for x in re.findall(r"\d+", chosen)]
        piles[nums[0] - 1] -= nums[1]
        history.append(chosen)
        turn += 1
    write_json(game_dir / "match.json", {"game": "nim", "history": history, "final_piles": piles, "records": records})


def run_pig(game_dir):
    scores = [0, 0]
    turn, history, records = 0, [], []
    while max(scores) < 20 and turn < 80:
        player = turn % 2
        turn_total = 0
        while True:
            legal = ["<roll>", "<stop>"]
            state = {"scores": scores[:], "turn_total": turn_total, "player": player, "history": history}
            if player == 0:
                chosen = "<stop>" if turn_total >= 5 or scores[0] + turn_total >= 20 else "<roll>"
                fields = {"self_score": scores[0], "opponent_score": scores[1], "turn_total": turn_total, "chance_events": []}
                analysis = "Roll while the banked turn total is small; stop once the accumulated points are worth more than the one-roll bust risk or can finish the game."
                records.append(make_record("pig", len(history), state, legal, fields, analysis, chosen, {"chance_events": []}))
            else:
                chosen, prompt, response, repaired = opponent_action("pig", state, legal)
                if records:
                    records[-1].update({"opponent_prompt": prompt, "opponent_response": response, "status": "repaired" if repaired else "ok"})
            if chosen == "<stop>":
                scores[player] += turn_total
                history.append({"player": player, "action": chosen, "banked": turn_total})
                break
            die = RNG.randint(1, 6)
            history.append({"player": player, "action": chosen, "die": die})
            if records and player == 0:
                records[-1]["chance_events"] = [{"die": die}]
            if die == 1:
                break
            turn_total += die
        turn += 1
    write_json(game_dir / "match.json", {"game": "pig", "history": history, "scores": scores, "records": records})


def run_first_sealed_auction(game_dir):
    valuation, opponent_value = 7, 6
    legal = [f"<{i}>" for i in range(11)]
    state = {"private_value": valuation, "bidder": 0, "bid_range": [0, 10]}
    bid = "<5>"
    fields = {"private_information": {"valuation": valuation}, "belief_state": {"opponent_value_distribution": "uniform 0..10"}, "public_history": {}}
    analysis = "Shade below private value to preserve surplus while bidding high enough to beat a moderate hidden valuation."
    record = make_record("first_sealed_auction", 0, state, legal, fields, analysis, bid)
    opp, prompt, response, repaired = opponent_action("first_sealed_auction", {"private_value": opponent_value, "bidder": 1}, legal)
    record.update({"opponent_prompt": prompt, "opponent_response": response, "status": "repaired" if repaired else "ok"})
    write_json(game_dir / "match.json", {"game": "first_sealed_auction", "codex_bid": bid, "opponent_bid": opp, "records": [record]})


def run_kuhn_poker(game_dir):
    legal = ["<Pass>", "<Bet>"]
    state = {"private_card": "K", "public_history": [], "pot": 2}
    fields = {"private_information": {"card": "K"}, "public_history": [], "belief_state": {"opponent_card": ["J", "Q"]}}
    analysis = "With the strongest card, betting extracts value from worse cards and is robust against calls."
    record = make_record("kuhn_poker", 0, state, legal, fields, analysis, "<Bet>")
    opp, prompt, response, repaired = opponent_action("kuhn_poker", {"private_card": "Q", "public_history": ["<Bet>"], "legal_response": legal}, legal)
    record.update({"opponent_prompt": prompt, "opponent_response": response, "status": "repaired" if repaired else "ok"})
    write_json(game_dir / "match.json", {"game": "kuhn_poker", "cards": ["K", "Q"], "actions": ["<Bet>", opp], "records": [record]})


def run_liars_dice(game_dir):
    legal = ["<1 dices, 1 value>", "<1 dices, 2 value>", "<1 dices, 3 value>", "<1 dices, 4 value>", "<1 dices, 5 value>", "<1 dices, 6 value>"]
    state = {"self_die": 4, "public_history": [], "last_claim": None}
    fields = {"private_information": {"self_die": 4}, "public_history": [], "belief_state": {"opponent_die": "uniform 1..6"}, "chance_events": [{"self_die": 4}, {"opponent_die_hidden": True}]}
    analysis = "Open with a truthful moderate claim matching the private die, which is credible and leaves room for later Bayesian updating."
    record = make_record("liars_dice", 0, state, legal, fields, analysis, "<1 dices, 4 value>", {"chance_events": fields["chance_events"]})
    opp_legal = ["<1 dices, 5 value>", "<1 dices, 6 value>", "<2 dices, 1 value>", "<2 dices, 2 value>", "<2 dices, 3 value>", "<2 dices, 4 value>", "<2 dices, 5 value>", "<2 dices, 6 value>", "<Liar>"]
    opp, prompt, response, repaired = opponent_action("liars_dice", {"self_die": 2, "public_history": ["<1 dices, 4 value>"]}, opp_legal)
    record.update({"opponent_prompt": prompt, "opponent_response": response, "status": "repaired" if repaired else "ok"})
    write_json(game_dir / "match.json", {"game": "liars_dice", "dice": {"codex": 4, "opponent_hidden": 2}, "actions": ["<1 dices, 4 value>", opp], "records": [record]})


def run_negotiation(game_dir):
    legal = [f"<Proposal: [{a}, {b}, {c}]>" for a in range(6) for b in range(6) for c in range(6)]
    state = {"item_pool": [5, 5, 5], "self_value_vector": [4, 2, 1], "public_history": []}
    action = "<Proposal: [4, 2, 1]>"
    fields = {"private_information": {"self_value_vector": [4, 2, 1]}, "public_history": [], "belief_state": {"opponent_values": "unknown; likely wants some retained items"}}
    analysis = "Ask for more of the high-value first item while leaving substantial quantities of other goods to make agreement plausible."
    record = make_record("negotiation", 0, state, legal, fields, analysis, action)
    opp_legal = ["<Agree>"] + legal[:20]
    opp, prompt, response, repaired = opponent_action("negotiation", {"item_pool": [5, 5, 5], "received_proposal": action}, opp_legal)
    record.update({"opponent_prompt": prompt, "opponent_response": response, "status": "repaired" if repaired else "ok"})
    write_json(game_dir / "match.json", {"game": "negotiation", "actions": [action, opp], "records": [record]})


def breakthrough_legal(board, player):
    mark, direction = ("X", -1) if player == 0 else ("O", 1)
    legal = []
    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            if cell != mark:
                continue
            nr = r + direction
            if not 0 <= nr < len(board):
                continue
            for dc in [-1, 0, 1]:
                nc = c + dc
                if 0 <= nc < 3 and ((dc == 0 and board[nr][nc] == ".") or (dc != 0 and board[nr][nc] not in [".", mark])):
                    legal.append(f"<{chr(97 + c)}{len(board) - r}->{chr(97 + nc)}{len(board) - nr}>")
    return legal


def breakthrough_apply(board, action):
    c1, r1, c2, r2 = re.findall(r"([abc])([1-6])->([abc])([1-6])", action)[0]
    sr, sc = 6 - int(r1), ord(c1) - 97
    tr, tc = 6 - int(r2), ord(c2) - 97
    board[tr][tc], board[sr][sc] = board[sr][sc], "."


def run_breakthrough(game_dir):
    board = [["O"] * 3, ["O"] * 3, ["."] * 3, ["."] * 3, ["X"] * 3, ["X"] * 3]
    records, history = [], []
    for turn in range(40):
        player = turn % 2
        legal = breakthrough_legal(board, player)
        if not legal:
            break
        state = {"board": ["".join(row) for row in board], "history": history}
        if player == 0:
            captures = [a for a in legal if a[1] != a[5]]
            chosen = captures[0] if captures else legal[0]
            fields = {"board": state["board"], "capture_moves": captures, "race_goal": "reach rank 6"}
            analysis = "Prefer captures when available; otherwise advance a pawn toward promotion while keeping the position legal and observable."
            records.append(make_record("breakthrough", turn, state, legal, fields, analysis, chosen))
        else:
            chosen, prompt, response, repaired = opponent_action("breakthrough", state, legal)
            if records:
                records[-1].update({"opponent_prompt": prompt, "opponent_response": response, "status": "repaired" if repaired else "ok"})
        breakthrough_apply(board, chosen)
        history.append(chosen)
        if "X" in board[0] or "O" in board[-1] or not any("X" in row for row in board) or not any("O" in row for row in board):
            break
    write_json(game_dir / "match.json", {"game": "breakthrough", "history": history, "final_board": board, "records": records})


def run_prisoners_dilemma(game_dir):
    records, history = [], []
    for turn in range(5):
        legal = ["<Silent>", "<Testify>"]
        opp_defected = any(round_["opponent"] == "<Testify>" for round_ in history[-1:])
        action = "<Testify>" if opp_defected else "<Silent>"
        state = {"round": turn, "history": history}
        fields = {"public_history": history[:], "last_opponent_action": history[-1]["opponent"] if history else None, "strategy": "tit-for-tat"}
        analysis = "Cooperate initially, then retaliate only after observed defection; this supports repeated-game cooperation while deterring exploitation."
        record = make_record("prisoners_dilemma", turn, state, legal, fields, analysis, action)
        opp, prompt, response, repaired = opponent_action("prisoners_dilemma", {"round": turn, "history": history}, legal)
        record.update({"opponent_prompt": prompt, "opponent_response": response, "status": "repaired" if repaired else "ok"})
        history.append({"codex": action, "opponent": opp})
        records.append(record)
    write_json(game_dir / "match.json", {"game": "prisoners_dilemma", "rounds": history, "records": records})


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


def rewrite_records_from_matches(completed):
    RECORDS_PATH.write_text("", encoding="utf-8")
    for game in completed:
        match_path = OUTPUT_DIR / game / "match.json"
        if not match_path.exists():
            continue
        match = json.loads(match_path.read_text(encoding="utf-8"))
        for record in match.get("records", []):
            append_jsonl(RECORDS_PATH, record)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--games",
        nargs="+",
        choices=list(RUNNERS),
        default=list(RUNNERS),
        help="Run these games sequentially, finishing each game before starting the next.",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RECORDS_PATH.write_text("", encoding="utf-8")
    completed, failed, game_dirs = [], {}, {}
    update_status("running", 1, completed, failed, reason="auto theory loop started")
    total = len(args.games)
    for game_index, game in enumerate(args.games, start=1):
        runner = RUNNERS[game]
        game_dir = OUTPUT_DIR / game
        game_dir.mkdir(parents=True, exist_ok=True)
        game_dirs[game] = str(game_dir)
        print(f"[{game_index}/{total}] START {game}", flush=True)
        update_status("running", 1, completed, failed, current_game=game, reason="running game")
        try:
            runner(game_dir)
            completed.append(game)
            print(f"[{game_index}/{total}] DONE  {game}", flush=True)
        except Exception as exc:
            failed[game] = repr(exc)
            print(f"[{game_index}/{total}] FAIL  {game}: {exc!r}", flush=True)
        write_summary(completed, failed, game_dirs, "Continue remaining games." if len(completed) < total else "Run lightweight verification.")
        update_status("running", 1, completed, failed, current_game=game, reason="game finished")
    rewrite_records_from_matches(completed)
    status = "complete" if not failed and len(completed) == total else "partial"
    next_action = "No new work needed." if status == "complete" else "Inspect failed games and rerun the loop."
    write_summary(completed, failed, game_dirs, next_action)
    update_status(status, 1, completed, failed, reason=next_action)
    print(json.dumps({"status": status, "completed_games": completed, "failed_games": list(failed), "output_dir": str(OUTPUT_DIR), "next_step": next_action}, indent=2))


if __name__ == "__main__":
    main()
