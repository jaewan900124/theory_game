#!/usr/bin/env python
import argparse
import csv
import json
import re
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge selected GameBench prompt-result shards into one analyzable run."
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


def slug(value):
    return re.sub(r"[^a-zA-Z0-9]+", "_", str(value)).strip("_").lower()


def parse_include(spec):
    run_dir, games = spec.split("=", 1)
    return Path(run_dir), {game.strip() for game in games.split(",") if game.strip()}


def infer_agent_type_id(record):
    if record.get("agent_type_id"):
        return record["agent_type_id"]

    model = record.get("model") or record.get("model_name") or "unknown_model"
    backend = record.get("backend") or "unknown_backend"
    mode = record.get("mode")
    if mode:
        return f"theory_{slug(mode)}_{slug(backend)}_{slug(model)}"
    return f"unknown_{slug(backend)}_{slug(model)}"


def normalize_record(record, source_run_dir):
    out = dict(record)
    out["agent_type_id"] = infer_agent_type_id(out)
    out["source_run_dir"] = str(source_run_dir)
    return out


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
                normalized = normalize_record(record, run_dir)
                records.append(normalized)
                selected.append(normalized)

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


def win_value(record):
    agent_score = record.get("agent_score")
    opponent_score = record.get("opponent_score")
    if agent_score > opponent_score:
        return 1.0
    if agent_score == opponent_score:
        return 0.5
    return 0.0


def summarize(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[(record["agent_type_id"], record["game"])].append(record)

    by_agent_game = []
    for (agent, game), items in sorted(grouped.items()):
        ok_items = [item for item in items if item.get("status") == "ok"]
        scores = [float(item["agent_score"]) for item in ok_items]
        wins = [win_value(item) for item in ok_items]
        by_agent_game.append(
            {
                "agent": agent,
                "game": game,
                "matches": len(items),
                "ok": len(ok_items),
                "failed": len(items) - len(ok_items),
                "mean_score": mean(scores) if scores else None,
                "std_score": pstdev(scores) if len(scores) > 1 else 0.0 if scores else None,
                "win_rate": mean(wins) if wins else None,
            }
        )

    grouped_agents = defaultdict(list)
    for row in by_agent_game:
        if row["mean_score"] is not None:
            grouped_agents[row["agent"]].append(row)

    by_agent = []
    for agent, rows in sorted(grouped_agents.items()):
        by_agent.append(
            {
                "agent": agent,
                "games_with_scores": len(rows),
                "matches": sum(row["matches"] for row in rows),
                "ok": sum(row["ok"] for row in rows),
                "failed": sum(row["failed"] for row in rows),
                "macro_mean_score": mean(row["mean_score"] for row in rows),
                "macro_win_rate": mean(row["win_rate"] for row in rows),
            }
        )

    return {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "agent_type_ids": sorted({record["agent_type_id"] for record in records}),
        "total_records": len(records),
        "ok_records": sum(1 for record in records if record.get("status") == "ok"),
        "failed_records": sum(1 for record in records if record.get("status") != "ok"),
        "by_agent_game": by_agent_game,
        "by_agent": by_agent,
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
    write_json(output_dir / "source_manifest.json", manifest)
    write_csv(
        output_dir / "by_agent_game.csv",
        summary["by_agent_game"],
        ["agent", "game", "matches", "ok", "failed", "mean_score", "std_score", "win_rate"],
    )
    write_csv(
        output_dir / "by_agent.csv",
        summary["by_agent"],
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
    print(f"saved {len(records)} records to {output_dir}")


if __name__ == "__main__":
    main()
