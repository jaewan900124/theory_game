#!/usr/bin/env python
import argparse
import csv
import json
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev


ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge selected GameBench basic-prompt result shards."
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--include-run",
        action="append",
        required=True,
        help="Format: run_dir=game_a,game_b. Only matching games are copied.",
    )
    parser.add_argument(
        "--drop-failed-santorini",
        action="store_true",
        help="Drop failed Santorini records from the merged output.",
    )
    return parser.parse_args()


def parse_include(spec):
    run_dir, games = spec.split("=", 1)
    return Path(run_dir), {game.strip() for game in games.split(",") if game.strip()}


def load_records(includes, drop_failed_santorini):
    records = []
    manifest = []
    for run_dir, games in includes:
        path = run_dir / "matches.jsonl"
        selected = []
        if not path.exists():
            manifest.append(
                {
                    "run_dir": str(run_dir),
                    "games": sorted(games),
                    "records": 0,
                    "warning": "matches.jsonl missing",
                }
            )
            continue
        with path.open(encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("game") not in games:
                    continue
                if (
                    drop_failed_santorini
                    and record.get("game") == "santorini"
                    and record.get("status") != "ok"
                ):
                    continue
                record["source_run_dir"] = str(run_dir)
                records.append(record)
                selected.append(record)
        manifest.append(
            {
                "run_dir": str(run_dir),
                "games": sorted(games),
                "records": len(selected),
                "ok": sum(1 for record in selected if record.get("status") == "ok"),
                "failed": sum(1 for record in selected if record.get("status") != "ok"),
            }
        )
    return records, manifest


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[record["game"]].append(record)

    by_game = []
    ok_scores = []
    ok_wins = []
    for game, items in sorted(grouped.items()):
        ok_items = [item for item in items if item.get("status") == "ok"]
        scores = [float(item["agent_score"]) for item in ok_items]
        wins = [
            1.0
            if item["agent_score"] > item["opponent_score"]
            else 0.5
            if item["agent_score"] == item["opponent_score"]
            else 0.0
            for item in ok_items
        ]
        ok_scores.extend(scores)
        ok_wins.extend(wins)
        by_game.append(
            {
                "game": game,
                "matches": len(items),
                "ok": len(ok_items),
                "failed": len(items) - len(ok_items),
                "mean_score": mean(scores) if scores else None,
                "std_score": pstdev(scores) if len(scores) > 1 else 0.0 if scores else None,
                "win_rate": mean(wins) if wins else None,
            }
        )

    scored = [row for row in by_game if row["mean_score"] is not None]
    agent_ids = sorted(
        {
            record.get("agent_type_id")
            for record in records
            if record.get("agent_type_id")
        }
    )
    return {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "agent_type_ids": agent_ids,
        "total_records": len(records),
        "ok_records": sum(1 for record in records if record.get("status") == "ok"),
        "failed_records": sum(1 for record in records if record.get("status") != "ok"),
        "by_game": by_game,
        "overall": {
            "games_with_scores": len(scored),
            "macro_mean_score": mean([row["mean_score"] for row in scored])
            if scored
            else None,
            "macro_win_rate": mean([row["win_rate"] for row in scored])
            if scored
            else None,
            "micro_mean_score": mean(ok_scores) if ok_scores else None,
            "micro_win_rate": mean(ok_wins) if ok_wins else None,
        },
        "failures": [record for record in records if record.get("status") != "ok"],
    }


def paper_format(records):
    out = []
    for record in records:
        if record.get("status") != "ok":
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
    includes = [parse_include(spec) for spec in args.include_run]
    records, manifest = load_records(includes, args.drop_failed_santorini)
    output_dir = Path(args.output_dir)
    summary = summarize(records)
    summary["source_manifest"] = manifest

    write_jsonl(output_dir / "matches.jsonl", records)
    write_json(output_dir / "paper_format_matches.json", paper_format(records))
    write_json(output_dir / "summary.json", summary)
    write_csv(
        output_dir / "summary.csv",
        summary["by_game"],
        ["game", "matches", "ok", "failed", "mean_score", "std_score", "win_rate"],
    )
    write_json(output_dir / "source_manifest.json", manifest)
    print(f"saved {len(records)} records to {output_dir}")


if __name__ == "__main__":
    main()
