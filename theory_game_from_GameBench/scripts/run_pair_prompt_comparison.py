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
from agents.theory_prompt_agent import TheoryPromptAgent  # noqa: E402


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

PROMPT_CHOICES = ["base", "high_reasoning", "field_rationale", "field_program", "high_distill"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run head-to-head GameBench prompt-agent comparisons."
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-root", default="theory_results")
    parser.add_argument("--games", nargs="+", default=["all"], choices=["all", *GAME_PATHS])
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--left-agent", required=True, choices=PROMPT_CHOICES)
    parser.add_argument("--right-agent", required=True, choices=PROMPT_CHOICES)
    parser.add_argument("--num-matches", type=int, default=5)
    parser.add_argument("--model-name", default="gemma4:31b")
    parser.add_argument("--backend", default="ollama", choices=["ollama", "openai"])
    parser.add_argument("--base-url", default=os.environ.get("OLLAMA_BASE_URL"))
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--left-model-name", default=None)
    parser.add_argument("--right-model-name", default=None)
    parser.add_argument("--left-backend", default=None, choices=["ollama", "openai"])
    parser.add_argument("--right-backend", default=None, choices=["ollama", "openai"])
    parser.add_argument("--left-base-url", default=None)
    parser.add_argument("--right-base-url", default=None)
    parser.add_argument("--left-api-key", default=None)
    parser.add_argument("--right-api-key", default=None)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--response-retries", type=int, default=3)
    parser.add_argument(
        "--match-timeout-seconds",
        type=int,
        default=0,
        help=(
            "Optional wall-clock timeout per match. Use 0 to follow each "
            "game's rule-defined termination without an external match timer."
        ),
    )
    parser.add_argument("--show-state", action="store_true")
    parser.add_argument("--transparent-reasoning", action="store_true")
    parser.add_argument(
        "--prompt-output-mode",
        default="compact",
        choices=["compact", "compact_basis", "compact_field_analysis", "debug"],
        help=(
            "compact asks theory agents to return only selected_action and "
            "openended_response; compact_basis also asks for used_rule or "
            "used_fields; compact_field_analysis adds a short analysis for "
            "those selected rules/fields; debug also asks for computed_fields "
            "and decision traces."
        ),
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--seating",
        default="balanced",
        choices=["balanced", "random", "left_first"],
    )
    parser.add_argument("--dry-run", action="store_true")
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


def stable_seed(base_seed, game_key, comparison, match_index):
    text = f"{base_seed}:{game_key}:{comparison}:{match_index}"
    total = 0
    for char in text:
        total = (total * 131 + ord(char)) % 1_000_000_007
    return total


def agent_runtime_config(args, side):
    prefix = f"{side}_"
    return {
        "backend": getattr(args, f"{prefix}backend") or args.backend,
        "model_name": getattr(args, f"{prefix}model_name") or args.model_name,
        "base_url": getattr(args, f"{prefix}base_url") or args.base_url,
        "api_key": getattr(args, f"{prefix}api_key") or args.api_key,
    }


def build_agent(agent_kind, args, side=None):
    runtime = agent_runtime_config(args, side) if side else {
        "backend": args.backend,
        "model_name": args.model_name,
        "base_url": args.base_url,
        "api_key": args.api_key,
    }
    common = {
        "backend": runtime["backend"],
        "model_name": runtime["model_name"],
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "timeout": args.timeout,
        "response_retries": args.response_retries,
        "base_url": runtime["base_url"],
        "api_key": runtime["api_key"],
        "transparent_reasoning": args.transparent_reasoning,
    }
    if agent_kind == "base":
        return BasicPromptAgent, common
    return TheoryPromptAgent, {
        **common,
        "agent_mode": agent_kind,
        "prompt_output_mode": args.prompt_output_mode,
    }


def agent_type_id(agent_kind, args, side=None):
    agent_class, kwargs = build_agent(agent_kind, args, side)
    agent = agent_class(team_id=-1, agent_id=-1, **kwargs)
    return agent.agent_type_id


def choose_swapped(args, match_index):
    if args.seating == "left_first":
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


def score_key(args, side):
    agent = args.left_agent if side == "left" else args.right_agent
    if args.left_agent == args.right_agent:
        return f"{side}_{agent}_score"
    return f"{agent}_score"


def mean_score_key(args, side):
    return score_key(args, side).replace("_score", "_mean_score")


def mean_score_key_from_config(config, side):
    agent = config["left_agent"] if side == "left" else config["right_agent"]
    if config["left_agent"] == config["right_agent"]:
        return f"{side}_{agent}_mean_score"
    return f"{agent}_mean_score"


def run_match(args, game_key, match_index):
    match_seed = stable_seed(args.seed, game_key, args.comparison, match_index)
    seed_everything(match_seed)
    if args.seating == "random":
        random.seed(match_seed)
    swapped = choose_swapped(args, match_index)

    left_class, left_kwargs = build_agent(args.left_agent, args, "left")
    right_class, right_kwargs = build_agent(args.right_agent, args, "right")
    left_id = agent_type_id(args.left_agent, args, "left")
    right_id = agent_type_id(args.right_agent, args, "right")
    left_runtime = agent_runtime_config(args, "left")
    right_runtime = agent_runtime_config(args, "right")
    left_score_key = score_key(args, "left")
    right_score_key = score_key(args, "right")

    game = None
    record = {
        "game": game_key,
        "comparison": args.comparison,
        "model": args.model_name,
        "base_url": args.base_url,
        "left_model": left_runtime["model_name"],
        "right_model": right_runtime["model_name"],
        "left_backend": left_runtime["backend"],
        "right_backend": right_runtime["backend"],
        "left_base_url": left_runtime["base_url"],
        "right_base_url": right_runtime["base_url"],
        "match_index": match_index,
        "swapped_seating": swapped,
        "status": "started",
        left_score_key: None,
        right_score_key: None,
        "error": None,
        "left_agent_type_id": left_id,
        "right_agent_type_id": right_id,
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
                agent_1_kwargs=right_kwargs,
                agent_2_kwargs=left_kwargs,
            )
            game.init_game(right_class, left_class)
            right_score, left_score = game.play()
        else:
            game = game_class(
                show_state=args.show_state,
                agent_1_kwargs=left_kwargs,
                agent_2_kwargs=right_kwargs,
            )
            game.init_game(left_class, right_class)
            left_score, right_score = game.play()
        record.update(
            {
                "status": "ok",
                left_score_key: float(left_score),
                right_score_key: float(right_score),
            }
        )
    except MatchTimeout as exc:
        record.update(
            {
                "status": "failed",
                "error": f"MatchTimeout: {exc}",
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


def summarize(records, args, run_id):
    groups = {}
    left_key = score_key(args, "left")
    right_key = score_key(args, "right")
    left_mean_key = mean_score_key(args, "left")
    right_mean_key = mean_score_key(args, "right")
    for record in records:
        groups.setdefault(record["game"], []).append(record)

    by_game = []
    for game, items in sorted(groups.items()):
        ok_items = [item for item in items if item["status"] == "ok"]
        left_scores = [item[left_key] for item in ok_items]
        right_scores = [item[right_key] for item in ok_items]
        by_game.append(
            {
                "game": game,
                "comparison": args.comparison,
                "model_name": args.model_name,
                "left_model_name": agent_runtime_config(args, "left")["model_name"],
                "right_model_name": agent_runtime_config(args, "right")["model_name"],
                "left_backend": agent_runtime_config(args, "left")["backend"],
                "right_backend": agent_runtime_config(args, "right")["backend"],
                "matches": len(items),
                "ok": len(ok_items),
                "failed": len(items) - len(ok_items),
                left_mean_key: mean(left_scores) if left_scores else None,
                right_mean_key: mean(right_scores) if right_scores else None,
            }
        )

    ok_items = [item for item in records if item["status"] == "ok"]
    summary = {
        "run_id": run_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "config": {
            "games": selected_games(args.games),
            "comparison": args.comparison,
            "left_agent": args.left_agent,
            "right_agent": args.right_agent,
            "model_name": args.model_name,
            "base_url": args.base_url,
            "left_model_name": agent_runtime_config(args, "left")["model_name"],
            "right_model_name": agent_runtime_config(args, "right")["model_name"],
            "left_backend": agent_runtime_config(args, "left")["backend"],
            "right_backend": agent_runtime_config(args, "right")["backend"],
            "left_base_url": agent_runtime_config(args, "left")["base_url"],
            "right_base_url": agent_runtime_config(args, "right")["base_url"],
            "num_matches": args.num_matches,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "timeout": args.timeout,
            "response_retries": args.response_retries,
            "prompt_output_mode": args.prompt_output_mode,
            "match_timeout_seconds": args.match_timeout_seconds,
            "seed": args.seed,
            "seating": args.seating,
        },
        "matches": len(records),
        "ok": len(ok_items),
        "failed": len(records) - len(ok_items),
        "by_game": by_game,
        "failures": [record for record in records if record["status"] != "ok"],
    }
    if ok_items:
        summary[left_mean_key] = mean(item[left_key] for item in ok_items)
        summary[right_mean_key] = mean(item[right_key] for item in ok_items)
    else:
        summary[left_mean_key] = None
        summary[right_mean_key] = None
    return summary


def write_summary_csv(path, summary):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "game",
        "comparison",
        "model_name",
        "left_model_name",
        "right_model_name",
        "left_backend",
        "right_backend",
        "matches",
        "ok",
        "failed",
        mean_score_key_from_config(summary["config"], "left"),
        mean_score_key_from_config(summary["config"], "right"),
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary["by_game"]:
            writer.writerow(row)


def main():
    args = parse_args()
    games = selected_games(args.games)
    run_id = args.run_id or (
        f"{args.comparison}_{args.model_name.replace(':', '_')}_{time.strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir = Path(args.output_root) / run_id

    if args.dry_run:
        print(f"run_id={run_id}")
        print(f"output_dir={output_dir}")
        print(f"left_agent={args.left_agent} agent_id={agent_type_id(args.left_agent, args, 'left')}")
        print(f"right_agent={args.right_agent} agent_id={agent_type_id(args.right_agent, args, 'right')}")
        for game_key in games:
            try:
                util.import_class(GAME_PATHS[game_key])
                import_status = "ok"
            except Exception as exc:
                import_status = f"import_failed ({type(exc).__name__}: {exc})"
            print(f"game={game_key} matches={args.num_matches} import={import_status}")
        return

    records = []
    matches_path = output_dir / "matches.jsonl"
    transcript_root = output_dir / "transcripts"
    left_key = score_key(args, "left")
    right_key = score_key(args, "right")
    for game_key in games:
        for match_index in range(args.num_matches):
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {game_key} {args.comparison} match {match_index + 1}/{args.num_matches}")
            record = run_match(args, game_key, match_index)
            records.append({k: v for k, v in record.items() if k != "agent_traces"})
            append_jsonl(matches_path, {k: v for k, v in record.items() if k != "agent_traces"})
            append_jsonl(transcript_root / game_key / f"{args.comparison}.jsonl", record)
            summary = summarize(records, args, run_id)
            write_json(output_dir / "summary.json", summary)
            write_summary_csv(output_dir / "summary.csv", summary)
            print(f"  status={record['status']} {left_key}={record[left_key]} {right_key}={record[right_key]}")

    print(f"Saved matches: {matches_path}")
    print(f"Saved summary: {output_dir / 'summary.json'}")
    print(f"Saved summary CSV: {output_dir / 'summary.csv'}")


if __name__ == "__main__":
    main()
