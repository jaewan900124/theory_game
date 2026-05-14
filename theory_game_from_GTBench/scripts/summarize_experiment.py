import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def iter_jsonl(path):
    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid json") from exc


def summarize_file(path):
    game_name = path.parent.name
    run_name = path.stem
    total_matches = 0
    normal_matches = 0
    abnormal_matches = 0
    draws = 0
    wins = Counter()
    faults = Counter()
    total_payoff = defaultdict(float)
    payoff_matches = Counter()
    total_tokens = 0
    total_steps = 0

    for record in iter_jsonl(path):
        for match in record.get("matches", []):
            total_matches += 1
            status = match.get("status", "Normal")
            if status == "Normal":
                normal_matches += 1
            else:
                abnormal_matches += 1

            winner = match.get("winner", "")
            if winner:
                wins[winner] += 1
            elif status == "Normal":
                draws += 1

            for agent_name in match.get("agents_at_fault", []):
                faults[agent_name] += 1

            if status == "Normal":
                scores = match.get("scores") or {}
                if scores:
                    for agent_name, score in scores.items():
                        total_payoff[agent_name] += score
                        payoff_matches[agent_name] += 1
                else:
                    participants = [
                        f"{agent}_{model}"
                        for agent, model in zip(
                            match.get("agent_order", []),
                            match.get("model_order", []),
                        )
                    ]
                    for agent_name in participants:
                        if not winner:
                            score = 0.0
                        elif agent_name == winner:
                            score = match.get("winner_score", 0.0)
                        else:
                            score = match.get("loser_score", 0.0)
                        total_payoff[agent_name] += score
                        payoff_matches[agent_name] += 1

            total_tokens += match.get("token_size", 0)
            total_steps += len(match.get("steps", []))

    normal_denominator = normal_matches if normal_matches else 1
    win_rates = {
        agent: count / normal_denominator
        for agent, count in sorted(wins.items())
    }
    return {
        "game": game_name,
        "run": run_name,
        "matches": total_matches,
        "normal": normal_matches,
        "abnormal": abnormal_matches,
        "draws": draws,
        "wins": dict(sorted(wins.items())),
        "win_rates": win_rates,
        "average_payoff": {
            agent: total_payoff[agent] / payoff_matches[agent]
            for agent in sorted(total_payoff)
            if payoff_matches[agent]
        },
        "faults": dict(sorted(faults.items())),
        "avg_tokens": total_tokens / total_matches if total_matches else 0,
        "avg_steps": total_steps / total_matches if total_matches else 0,
    }


def format_rate(value):
    return f"{100 * value:.1f}%"


def print_markdown(rows):
    print("| game | run | matches | normal | abnormal | draws | win rates | avg payoff | faults | avg tokens | avg steps |")
    print("|---|---|---:|---:|---:|---:|---|---|---|---:|---:|")
    for row in rows:
        win_rates = ", ".join(
            f"{agent}: {format_rate(rate)}"
            for agent, rate in row["win_rates"].items()
        ) or "-"
        average_payoff = ", ".join(
            f"{agent}: {payoff:.3f}"
            for agent, payoff in row["average_payoff"].items()
        ) or "-"
        faults = ", ".join(
            f"{agent}: {count}"
            for agent, count in row["faults"].items()
        ) or "-"
        print(
            f"| {row['game']} | {row['run']} | {row['matches']} | "
            f"{row['normal']} | {row['abnormal']} | {row['draws']} | "
            f"{win_rates} | {average_payoff} | {faults} | {row['avg_tokens']:.1f} | "
            f"{row['avg_steps']:.1f} |"
        )


def print_json(rows):
    print(json.dumps(rows, indent=2, ensure_ascii=False))


def grouped_summary(rows):
    grouped = defaultdict(lambda: {
        "matches": 0,
        "normal": 0,
        "abnormal": 0,
        "draws": 0,
        "wins": Counter(),
        "faults": Counter(),
        "total_payoff": defaultdict(float),
        "payoff_matches": Counter(),
        "total_tokens": 0.0,
        "total_steps": 0.0,
    })
    for row in rows:
        bucket = grouped[row["game"]]
        bucket["matches"] += row["matches"]
        bucket["normal"] += row["normal"]
        bucket["abnormal"] += row["abnormal"]
        bucket["draws"] += row["draws"]
        bucket["wins"].update(row["wins"])
        bucket["faults"].update(row["faults"])
        for agent, payoff in row["average_payoff"].items():
            matches = row["normal"]
            bucket["total_payoff"][agent] += payoff * matches
            bucket["payoff_matches"][agent] += matches
        bucket["total_tokens"] += row["avg_tokens"] * row["matches"]
        bucket["total_steps"] += row["avg_steps"] * row["matches"]

    summary_rows = []
    for game, bucket in sorted(grouped.items()):
        normal_denominator = bucket["normal"] if bucket["normal"] else 1
        match_denominator = bucket["matches"] if bucket["matches"] else 1
        summary_rows.append({
            "game": game,
            "run": "ALL",
            "matches": bucket["matches"],
            "normal": bucket["normal"],
            "abnormal": bucket["abnormal"],
            "draws": bucket["draws"],
            "wins": dict(sorted(bucket["wins"].items())),
            "win_rates": {
                agent: count / normal_denominator
                for agent, count in sorted(bucket["wins"].items())
            },
            "average_payoff": {
                agent: bucket["total_payoff"][agent] / bucket["payoff_matches"][agent]
                for agent in sorted(bucket["total_payoff"])
                if bucket["payoff_matches"][agent]
            },
            "faults": dict(sorted(bucket["faults"].items())),
            "avg_tokens": bucket["total_tokens"] / match_denominator,
            "avg_steps": bucket["total_steps"] / match_denominator,
        })
    return summary_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("exp_root", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--group-by-game", action="store_true")
    args = parser.parse_args()

    files = sorted(args.exp_root.glob("*/*.jsonl"))
    files = [path for path in files if path.name != "errors.jsonl"]
    rows = [summarize_file(path) for path in files]
    if args.group_by_game:
        rows = grouped_summary(rows)

    if args.json:
        print_json(rows)
    else:
        print_markdown(rows)


if __name__ == "__main__":
    main()
