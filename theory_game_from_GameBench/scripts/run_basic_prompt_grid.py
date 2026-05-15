#!/usr/bin/env python
import argparse
import csv
import json
import os
import random
import signal
import sys
import time
import traceback
from pathlib import Path
from statistics import mean, pstdev


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", "/tmp/gamebench-mpl")

import api.util as util  # noqa: E402
from agents.basic_prompt_agent import BasicPromptAgent  # noqa: E402
from agents.random_agent import RandomAgent  # noqa: E402


class MatchTimeout(Exception):
    pass


def _handle_match_timeout(signum, frame):
    raise MatchTimeout("match timeout exceeded")


GAME_PATHS = {
    "air_land_sea": "games.air_land_sea.game.AirLandSea",
    "arctic_scavengers": "games.arctic_scavengers.arctic_scavengers.ArcticScavengers",
    "are_you_the_traitor": "games.are_you_the_traitor.aytt.AreYouTheTraitor",
    "codenames": "games.codenames.game.CodenamesGame",
    "hive": "games.hive.game.HiveGame",
    "pit": "games.pit.pit.PitGame",
    "santorini": "games.santorini.santorini.Santorini",
    "sea_battle": "games.sea_battle.SeaBattle",
    "two_rooms_and_a_boom": "games.two_rooms_and_a_boom.two_rooms.TwoRoomsAndaBoom",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run a GameBench-style basic prompt LLM agent against RandomAgent."
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-root", default="basic_results")
    parser.add_argument("--games", nargs="+", default=["all"], choices=["all", *GAME_PATHS])
    parser.add_argument(
        "--match-plan",
        default="fixed",
        choices=["fixed", "paper_gpt4_random"],
        help=(
            "fixed uses --num-matches for every game. paper_gpt4_random reuses "
            "the per-game match counts found in matches.json for gpt-4 vs random."
        ),
    )
    parser.add_argument("--num-matches", type=int, default=5)
    parser.add_argument("--model-name", default="qwen3:8b")
    parser.add_argument("--backend", default="ollama", choices=["ollama", "openai"])
    parser.add_argument("--base-url", default=os.environ.get("OLLAMA_BASE_URL"))
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument(
        "--match-timeout-seconds",
        type=int,
        default=0,
        help=(
            "Optional wall-clock timeout per match. Use 0 to follow each "
            "game's rule-defined termination without an external match timer."
        ),
    )
    parser.add_argument("--response-retries", type=int, default=3)
    parser.add_argument("--show-state", action="store_true")
    parser.add_argument("--transparent-reasoning", action="store_true")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--seating",
        default="random",
        choices=["random", "balanced", "basic_first"],
        help="How to assign BasicPromptAgent to player/team slots across matches.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned jobs and import game classes, but do not run matches.",
    )
    return parser.parse_args()


def selected_games(game_args):
    if "all" in game_args:
        return list(GAME_PATHS)
    return game_args


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def seed_everything(seed):
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except Exception:
        pass


def stable_seed(base_seed, game_key, match_index):
    text = f"{base_seed}:{game_key}:basic_prompt:{match_index}"
    total = 0
    for char in text:
        total = (total * 131 + ord(char)) % 1_000_000_007
    return total


def basic_kwargs(args):
    return {
        "backend": args.backend,
        "model_name": args.model_name,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "timeout": args.timeout,
        "response_retries": args.response_retries,
        "base_url": args.base_url,
        "api_key": args.api_key,
        "transparent_reasoning": args.transparent_reasoning,
    }


def basic_agent_id(args):
    agent = BasicPromptAgent(team_id=-1, agent_id=-1, **basic_kwargs(args))
    return agent.agent_type_id


def paper_gpt4_random_counts():
    counts = {game: 0 for game in GAME_PATHS}
    matches_path = ROOT / "matches.json"
    if not matches_path.exists():
        return counts
    for match in util.load_json(str(matches_path)):
        if match.get("game") not in counts:
            continue
        agent_keys = {key for key in match if key != "game"}
        if agent_keys == {"gpt-4", "random"}:
            counts[match["game"]] += 1
    return counts


def planned_match_counts(args, games):
    if args.match_plan == "fixed":
        return {game: args.num_matches for game in games}
    counts = paper_gpt4_random_counts()
    return {game: counts.get(game, 0) for game in games}


def choose_swapped(args, match_index):
    if args.seating == "basic_first":
        return False
    if args.seating == "balanced":
        return bool(match_index % 2)
    return bool(random.choice([0, 1]))


def collect_traces(game):
    def add_agent(agent, source):
        if agent is None or not hasattr(agent, "take_action"):
            return
        agent_key = id(agent)
        if agent_key in seen:
            return
        seen.add(agent_key)
        traces.append(
            {
                "trace_source": source,
                "agent_type_id": getattr(agent, "agent_type_id", None),
                "team_id": getattr(agent, "team_id", None),
                "agent_id": getattr(agent, "agent_id", None),
                "traces": getattr(agent, "traces", []),
            }
        )

    def add_value(value, source):
        if value is None:
            return
        if isinstance(value, dict):
            for key, item in value.items():
                add_value(item, f"{source}.{key}")
            return
        if isinstance(value, (list, tuple, set)):
            for index, item in enumerate(value):
                add_value(item, f"{source}[{index}]")
            return
        if hasattr(value, "agent"):
            add_agent(getattr(value, "agent"), f"{source}.agent")
            return
        add_agent(value, source)

    traces = []
    seen = set()
    for attr in (
        "agents",
        "players",
        "_players",
        "spymaster_list",
        "operative_list",
        "red_team_list",
        "blue_team_list",
        "list_all_players",
        "rooms",
    ):
        add_value(getattr(game, attr, None), attr)
    for attr in ("spymaster_1", "spymaster_2", "operative_1", "operative_2", "player1", "player2"):
        add_value(getattr(game, attr, None), attr)
    return traces


def run_match(args, game_key, match_index):
    match_seed = stable_seed(args.seed, game_key, match_index)
    seed_everything(match_seed)
    swapped = choose_swapped(args, match_index)
    kwargs = basic_kwargs(args)
    opponent_kwargs = {}
    agent_id = basic_agent_id(args)
    game = None

    record = {
        "game": game_key,
        "agent_type_id": agent_id,
        "model": args.model_name,
        "backend": args.backend,
        "opponent": "random",
        "match_index": match_index,
        "seed": match_seed,
        "swapped_seating": swapped,
        "status": "started",
        "agent_score": None,
        "opponent_score": None,
        "error": None,
    }
    try:
        old_handler = None
        if args.match_timeout_seconds > 0:
            old_handler = signal.signal(signal.SIGALRM, _handle_match_timeout)
            signal.alarm(args.match_timeout_seconds)
        game_class = util.import_class(GAME_PATHS[game_key])
        if swapped:
            game = game_class(
                show_state=args.show_state,
                agent_1_kwargs=opponent_kwargs,
                agent_2_kwargs=kwargs,
            )
            game.init_game(RandomAgent, BasicPromptAgent)
            opponent_score, agent_score = game.play()
        else:
            game = game_class(
                show_state=args.show_state,
                agent_1_kwargs=kwargs,
                agent_2_kwargs=opponent_kwargs,
            )
            game.init_game(BasicPromptAgent, RandomAgent)
            agent_score, opponent_score = game.play()
        record.update(
            {
                "status": "ok",
                "agent_score": float(agent_score),
                "opponent_score": float(opponent_score),
            }
        )
    except MatchTimeout as exc:
        record.update(
            {
                "status": "failed",
                "error": f"TimeoutError: {exc}",
                "traceback": traceback.format_exc(),
            }
        )
    except Exception as exc:
        record.update(
            {
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }
        )
    finally:
        if args.match_timeout_seconds > 0:
            signal.alarm(0)
            if old_handler is not None:
                signal.signal(signal.SIGALRM, old_handler)
        record["agent_traces"] = collect_traces(game) if game is not None else []
    return record


def summarize(records, args, run_id, match_counts):
    groups = {}
    for record in records:
        groups.setdefault(record["game"], []).append(record)

    by_game = []
    all_scores = []
    all_wins = []
    for game in selected_games(args.games):
        items = groups.get(game, [])
        ok_items = [item for item in items if item["status"] == "ok"]
        scores = [item["agent_score"] for item in ok_items]
        wins = [
            1.0
            if item["agent_score"] > item["opponent_score"]
            else 0.5
            if item["agent_score"] == item["opponent_score"]
            else 0.0
            for item in ok_items
        ]
        all_scores.extend(scores)
        all_wins.extend(wins)
        by_game.append(
            {
                "game": game,
                "planned_matches": match_counts.get(game, 0),
                "matches": len(items),
                "ok": len(ok_items),
                "failed": len(items) - len(ok_items),
                "mean_score": mean(scores) if scores else None,
                "std_score": pstdev(scores) if len(scores) > 1 else 0.0 if scores else None,
                "win_rate": mean(wins) if wins else None,
            }
        )

    scored_games = [row for row in by_game if row["mean_score"] is not None]
    summary = {
        "run_id": run_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "config": {
            "games": selected_games(args.games),
            "match_plan": args.match_plan,
            "match_counts": match_counts,
            "model_name": args.model_name,
            "backend": args.backend,
            "base_url": args.base_url,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "timeout": args.timeout,
            "match_timeout_seconds": args.match_timeout_seconds,
            "response_retries": args.response_retries,
            "seed": args.seed,
            "seating": args.seating,
            "opponent": "random",
            "agent_type_id": basic_agent_id(args),
        },
        "by_game": by_game,
        "overall": {
            "planned_matches": sum(match_counts.values()),
            "matches": len(records),
            "ok": sum(1 for record in records if record["status"] == "ok"),
            "failed": sum(1 for record in records if record["status"] != "ok"),
            "games_with_scores": len(scored_games),
            "macro_mean_score": mean([row["mean_score"] for row in scored_games])
            if scored_games
            else None,
            "macro_win_rate": mean([row["win_rate"] for row in scored_games])
            if scored_games
            else None,
            "micro_mean_score": mean(all_scores) if all_scores else None,
            "micro_win_rate": mean(all_wins) if all_wins else None,
        },
        "failures": [record for record in records if record["status"] != "ok"],
    }
    return summary


def write_summary_csv(path, summary):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "game",
        "planned_matches",
        "matches",
        "ok",
        "failed",
        "mean_score",
        "std_score",
        "win_rate",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary["by_game"]:
            writer.writerow(row)


def paper_format_record(record):
    return {
        "game": record["game"],
        record["agent_type_id"]: record["agent_score"],
        "random": record["opponent_score"],
    }


def main():
    args = parse_args()
    games = selected_games(args.games)
    match_counts = planned_match_counts(args, games)
    run_id = args.run_id or f"basic_prompt_{args.model_name.replace(':', '_')}_{time.strftime('%Y%m%d_%H%M%S')}"
    output_dir = Path(args.output_root) / run_id

    if args.dry_run:
        print(f"run_id={run_id}")
        print(f"output_dir={output_dir}")
        print(f"agent_id={basic_agent_id(args)}")
        for game_key in games:
            try:
                util.import_class(GAME_PATHS[game_key])
                import_status = "ok"
            except Exception as exc:
                import_status = f"import_failed ({type(exc).__name__}: {exc})"
            print(
                f"game={game_key} matches={match_counts.get(game_key, 0)} "
                f"import={import_status}"
            )
        return

    records = []
    paper_records = []
    matches_path = output_dir / "matches.jsonl"
    paper_matches_path = output_dir / "paper_format_matches.json"
    for game_key in games:
        for match_index in range(match_counts.get(game_key, 0)):
            print(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"{game_key} basic_prompt match "
                f"{match_index + 1}/{match_counts.get(game_key, 0)}"
            )
            record = run_match(args, game_key, match_index)
            records.append({k: v for k, v in record.items() if k != "agent_traces"})
            append_jsonl(matches_path, {k: v for k, v in record.items() if k != "agent_traces"})
            append_jsonl(
                output_dir / "transcripts" / game_key / "basic_prompt_vs_random.jsonl",
                record,
            )
            if record["status"] == "ok":
                paper_records.append(paper_format_record(record))
                write_json(paper_matches_path, paper_records)
            summary = summarize(records, args, run_id, match_counts)
            write_json(output_dir / "summary.json", summary)
            write_summary_csv(output_dir / "summary.csv", summary)
            print(
                f"  status={record['status']} agent_score={record['agent_score']} "
                f"opponent_score={record['opponent_score']}"
            )

    print(f"Saved matches: {matches_path}")
    print(f"Saved paper-format matches: {paper_matches_path}")
    print(f"Saved summary: {output_dir / 'summary.json'}")
    print(f"Saved summary CSV: {output_dir / 'summary.csv'}")


if __name__ == "__main__":
    main()
