#!/usr/bin/env python
import argparse
import csv
import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze basic-prompt GameBench runs in a paper-style summary."
    )
    parser.add_argument("run_dirs", nargs="+", help="Result directories containing matches.jsonl.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def load_records(run_dirs):
    records = []
    for run_dir in run_dirs:
        path = Path(run_dir) / "matches.jsonl"
        if not path.exists():
            raise FileNotFoundError(f"Missing matches file: {path}")
        with path.open(encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    record = json.loads(line)
                    record["source_run_dir"] = str(run_dir)
                    records.append(record)
    return records


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def game_rows(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[(record["agent_type_id"], record["game"])].append(record)

    rows = []
    for (agent, game), items in sorted(grouped.items()):
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
        rows.append(
            {
                "agent": agent,
                "game": game,
                "matches": len(items),
                "ok": len(ok_items),
                "failed": len(items) - len(ok_items),
                "mean_score": mean(scores) if scores else None,
                "win_rate": mean(wins) if wins else None,
            }
        )
    return rows


def agent_rows(rows):
    grouped = defaultdict(list)
    for row in rows:
        if row["mean_score"] is not None:
            grouped[row["agent"]].append(row)

    out = []
    for agent, items in sorted(grouped.items()):
        out.append(
            {
                "agent": agent,
                "games_with_scores": len(items),
                "matches": sum(row["matches"] for row in items),
                "ok": sum(row["ok"] for row in items),
                "failed": sum(row["failed"] for row in items),
                "macro_mean_score": mean(row["mean_score"] for row in items),
                "macro_win_rate": mean(row["win_rate"] for row in items),
            }
        )
    return out


def _bt_params(records, players, alpha=0.001):
    import choix
    import numpy as np

    data = []
    player_index = {player: idx for idx, player in enumerate(players)}
    for record in records:
        if record["status"] != "ok":
            continue
        agent_score = float(record["agent_score"])
        random_score = float(record["opponent_score"])
        if agent_score == random_score:
            continue
        data.append(
            (
                player_index[record["agent_type_id"]],
                player_index["random"],
                agent_score,
                random_score,
            )
        )
    if not data:
        return None

    def lsr_pairwise(n_items, pair_data, initial_params=None):
        weights, chain = choix.lsr._init_lsr(n_items, alpha, initial_params)
        for p1, p2, p1_score, p2_score in pair_data:
            chain[p1, p2] += float(p2_score) / (weights[p1] + weights[p2])
            chain[p2, p1] += float(p1_score) / (weights[p1] + weights[p2])
        chain -= np.diag(chain.sum(axis=1))
        return choix.utils.log_transform(choix.utils.statdist(chain))

    params = None
    for _ in range(100):
        new_params = lsr_pairwise(len(players), data, params)
        if params is not None and np.max(np.abs(new_params - params)) < 1e-8:
            params = new_params
            break
        params = new_params
    return params


def bt_summary(records, bootstrap_samples, seed):
    import choix
    import numpy as np

    ok_records = [record for record in records if record["status"] == "ok"]
    players = sorted({record["agent_type_id"] for record in ok_records} | {"random"})
    if len(players) < 2:
        return None

    params = _bt_params(ok_records, players)
    if params is None:
        return None

    random.seed(seed)
    game_counts = Counter(record["game"] for record in ok_records)
    sample_weights = [1 / game_counts[record["game"]] for record in ok_records]
    bootstraps = []
    for _ in range(bootstrap_samples):
        sample = random.choices(ok_records, k=len(ok_records), weights=sample_weights)
        sample_params = _bt_params(sample, players)
        if sample_params is not None:
            bootstraps.append(sample_params)

    matrix = []
    for left_idx, left in enumerate(players):
        for right_idx, right in enumerate(players):
            if left == right:
                probability = None
            else:
                probability = float(choix.probabilities([left_idx, right_idx], params)[0])
            matrix.append(
                {
                    "agent": left,
                    "opponent": right,
                    "win_probability": probability,
                }
            )

    rating_rows = []
    bootstrap_array = np.array(bootstraps) if bootstraps else None
    for idx, player in enumerate(players):
        row = {
            "agent": player,
            "bt_rating": float(params[idx]),
            "proportional_rating": float(np.exp(params[idx]) / np.max(np.exp(params))),
        }
        if bootstrap_array is not None and len(bootstrap_array):
            row["bt_rating_p05"] = float(np.percentile(bootstrap_array[:, idx], 5))
            row["bt_rating_p95"] = float(np.percentile(bootstrap_array[:, idx], 95))
        else:
            row["bt_rating_p05"] = None
            row["bt_rating_p95"] = None
        rating_rows.append(row)

    return {
        "players": players,
        "ratings": sorted(rating_rows, key=lambda row: row["bt_rating"], reverse=True),
        "pairwise_probabilities": matrix,
        "bootstrap_samples_requested": bootstrap_samples,
        "bootstrap_samples_used": len(bootstraps),
    }


def paper_format_matches(records):
    out = []
    for record in records:
        if record["status"] != "ok":
            continue
        out.append(
            {
                "game": record["game"],
                record["agent_type_id"]: record["agent_score"],
                "random": record["opponent_score"],
            }
        )
    return out


def main():
    args = parse_args()
    records = load_records(args.run_dirs)
    rows = game_rows(records)
    agents = agent_rows(rows)
    try:
        bt = bt_summary(records, args.bootstrap_samples, args.seed)
        bt_error = None
    except Exception as exc:
        bt = None
        bt_error = f"{type(exc).__name__}: {exc}"

    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else ROOT / "basic_results" / f"analysis_{time.strftime('%Y%m%d_%H%M%S')}"
    )
    summary = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "run_dirs": args.run_dirs,
        "total_records": len(records),
        "ok_records": sum(1 for record in records if record["status"] == "ok"),
        "failed_records": sum(1 for record in records if record["status"] != "ok"),
        "by_game": rows,
        "by_agent": agents,
        "bradley_terry": bt,
        "bradley_terry_error": bt_error,
        "failures": [record for record in records if record["status"] != "ok"],
    }

    write_json(output_dir / "analysis.json", summary)
    write_json(output_dir / "paper_format_matches.json", paper_format_matches(records))
    write_csv(
        output_dir / "by_game.csv",
        rows,
        ["agent", "game", "matches", "ok", "failed", "mean_score", "win_rate"],
    )
    write_csv(
        output_dir / "by_agent.csv",
        agents,
        [
            "agent",
            "games_with_scores",
            "matches",
            "ok",
            "failed",
            "macro_mean_score",
            "macro_win_rate",
        ],
    )
    if bt is not None:
        write_csv(
            output_dir / "bt_ratings.csv",
            bt["ratings"],
            [
                "agent",
                "bt_rating",
                "bt_rating_p05",
                "bt_rating_p95",
                "proportional_rating",
            ],
        )
        write_csv(
            output_dir / "bt_pairwise_probabilities.csv",
            bt["pairwise_probabilities"],
            ["agent", "opponent", "win_probability"],
        )

    print(f"Saved analysis: {output_dir / 'analysis.json'}")
    print(f"Saved by-game CSV: {output_dir / 'by_game.csv'}")
    print(f"Saved by-agent CSV: {output_dir / 'by_agent.csv'}")
    if bt_error:
        print(f"Bradley-Terry skipped: {bt_error}")


if __name__ == "__main__":
    main()
