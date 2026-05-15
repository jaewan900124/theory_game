#!/usr/bin/env python
import argparse
import csv
import json
import re
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean


ARCHIVE_PREFIXES = ("archive_",)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Merge completed theory_results shards into visibility-first "
            "experiment folders."
        )
    )
    parser.add_argument(
        "--input-root",
        default="/home/user/ktlim/theory_game/theory_game_from_GameBench/theory_results",
    )
    parser.add_argument(
        "--output-root",
        default="/home/user/ktlim/theory_game/theory_game_from_GameBench/theory_results_merged",
    )
    return parser.parse_args()


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


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


def score_key_from_config(config, side):
    agent = config[f"{side}_agent"]
    if config["left_agent"] == config["right_agent"]:
        return f"{side}_{agent}_score"
    return f"{agent}_score"


def mean_score_key_from_config(config, side):
    agent = config[f"{side}_agent"]
    if config["left_agent"] == config["right_agent"]:
        return f"{side}_{agent}_mean_score"
    return f"{agent}_mean_score"


def load_run(run_dir):
    summary_path = run_dir / "summary.json"
    matches_path = run_dir / "matches.jsonl"
    if not summary_path.exists() or not matches_path.exists():
        return None

    summary = json.loads(summary_path.read_text())
    config = dict(summary.get("config", {}))
    records = []
    counts = defaultdict(int)
    ok_counts = defaultdict(int)
    for line in matches_path.open(encoding="utf-8"):
        if not line.strip():
            continue
        record = json.loads(line)
        records.append(record)
        game = record.get("game")
        counts[game] += 1
        if record.get("status") == "ok":
            ok_counts[game] += 1

    expected_games = list(config.get("games", []))
    num_matches = int(config.get("num_matches", 0) or 0)
    extra_games = sorted(set(counts) - set(expected_games))
    missing_games = sorted(game for game in expected_games if counts.get(game, 0) != num_matches)
    failed_games = sorted(game for game in expected_games if ok_counts.get(game, 0) != num_matches)
    is_complete = (
        bool(expected_games)
        and not extra_games
        and not missing_games
        and not failed_games
    )
    if extra_games:
        complete_reason = f"unexpected_games:{','.join(extra_games)}"
    elif missing_games:
        complete_reason = f"incomplete_games:{','.join(missing_games)}"
    elif failed_games:
        complete_reason = f"failed_games:{','.join(failed_games)}"
    else:
        complete_reason = "complete"

    return {
        "run_id": run_dir.name,
        "run_dir": run_dir,
        "summary": summary,
        "config": config,
        "records": records,
        "counts": dict(counts),
        "ok_counts": dict(ok_counts),
        "expected_games": expected_games,
        "num_matches": num_matches,
        "is_complete": is_complete,
        "complete_reason": complete_reason,
    }


def normalized_group_key(config):
    return (
        config.get("comparison"),
        config.get("left_agent"),
        config.get("right_agent"),
        config.get("left_model_name"),
        config.get("right_model_name"),
        config.get("left_backend"),
        config.get("right_backend"),
        config.get("prompt_output_mode"),
        config.get("temperature"),
        config.get("max_tokens"),
        config.get("timeout"),
        config.get("response_retries"),
        config.get("match_timeout_seconds"),
        config.get("seating"),
        config.get("seed"),
    )


def duplicate_signature(run):
    return normalized_group_key(run["config"]) + (tuple(sorted(run["expected_games"])),)


def preference_score(run_id):
    score = 0
    if "fixed2" in run_id:
        score += 300
    elif "fixed" in run_id:
        score += 200
    if re.search(r"_set\d+$", run_id):
        score += 50
    if re.search(r"_s\d+$", run_id):
        score += 40
    if re.search(r"_g\d+$", run_id):
        score += 30
    if "_all" in run_id:
        score -= 100
    return score


def strip_run_suffix(run_id):
    return re.sub(r"(_s\d+|_g\d+|_set\d+|_all)$", "", run_id)


def merged_run_name(group_runs):
    base_names = [strip_run_suffix(run["run_id"]) for run in group_runs]
    unique = sorted(set(base_names))
    if len(unique) == 1:
        return unique[0]
    return unique[0]


def group_label_from_key(key):
    (
        comparison,
        left_agent,
        right_agent,
        left_model,
        right_model,
        left_backend,
        right_backend,
        prompt_output_mode,
        temperature,
        max_tokens,
        timeout,
        response_retries,
        match_timeout_seconds,
        seating,
        seed,
    ) = key
    return {
        "comparison": comparison,
        "left_agent": left_agent,
        "right_agent": right_agent,
        "left_model_name": left_model,
        "right_model_name": right_model,
        "left_backend": left_backend,
        "right_backend": right_backend,
        "prompt_output_mode": prompt_output_mode,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": timeout,
        "response_retries": response_retries,
        "match_timeout_seconds": match_timeout_seconds,
        "seating": seating,
        "seed": seed,
    }


def summarize_merged(records, config, run_id, source_runs_by_game):
    left_key = score_key_from_config(config, "left")
    right_key = score_key_from_config(config, "right")
    left_mean_key = mean_score_key_from_config(config, "left")
    right_mean_key = mean_score_key_from_config(config, "right")

    by_game = []
    grouped = defaultdict(list)
    for record in records:
        grouped[record["game"]].append(record)

    for game in sorted(grouped):
        items = grouped[game]
        ok_items = [item for item in items if item.get("status") == "ok"]
        left_scores = [float(item[left_key]) for item in ok_items]
        right_scores = [float(item[right_key]) for item in ok_items]
        by_game.append(
            {
                "game": game,
                "comparison": config["comparison"],
                "model_name": config.get("model_name"),
                "left_model_name": config.get("left_model_name"),
                "right_model_name": config.get("right_model_name"),
                "left_backend": config.get("left_backend"),
                "right_backend": config.get("right_backend"),
                "matches": len(items),
                "ok": len(ok_items),
                "failed": len(items) - len(ok_items),
                left_mean_key: mean(left_scores) if left_scores else None,
                right_mean_key: mean(right_scores) if right_scores else None,
                "source_runs": ",".join(sorted(source_runs_by_game.get(game, set()))),
            }
        )

    ok_items = [item for item in records if item.get("status") == "ok"]
    summary = {
        "run_id": run_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "config": config,
        "matches": len(records),
        "ok": len(ok_items),
        "failed": len(records) - len(ok_items),
        "by_game": by_game,
        "failures": [item for item in records if item.get("status") != "ok"],
    }
    if ok_items:
        summary[left_mean_key] = mean(float(item[left_key]) for item in ok_items)
        summary[right_mean_key] = mean(float(item[right_key]) for item in ok_items)
    else:
        summary[left_mean_key] = None
        summary[right_mean_key] = None
    return summary


def write_summary_csv(path, summary):
    left_mean_key = mean_score_key_from_config(summary["config"], "left")
    right_mean_key = mean_score_key_from_config(summary["config"], "right")
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
        left_mean_key,
        right_mean_key,
        "source_runs",
    ]
    write_csv(path, summary["by_game"], fieldnames)


def build_merge_notes(merged_name, group_info, included_runs, missing_games, status):
    notes = [
        f"merged_name={merged_name}",
        f"status={status}",
        f"comparison={group_info['comparison']}",
        f"prompt_output_mode={group_info['prompt_output_mode']}",
        f"left={group_info['left_agent']}:{group_info['left_model_name']}",
        f"right={group_info['right_agent']}:{group_info['right_model_name']}",
        f"included_runs={','.join(run['run_id'] for run in included_runs)}",
    ]
    if missing_games:
        notes.append(f"missing_games={','.join(missing_games)}")
    return {"notes": notes}


def main():
    args = parse_args()
    input_root = Path(args.input_root)
    output_root = Path(args.output_root)
    by_experiment_root = output_root / "by_experiment"

    all_runs = []
    for run_dir in sorted(input_root.iterdir()):
        if not run_dir.is_dir():
            continue
        if run_dir.name.startswith(ARCHIVE_PREFIXES):
            continue
        loaded = load_run(run_dir)
        if loaded is not None:
            all_runs.append(loaded)

    duplicate_groups = defaultdict(list)
    for run in all_runs:
        if run["is_complete"]:
            duplicate_groups[duplicate_signature(run)].append(run)

    preferred_run_ids = set()
    duplicate_exclusions = {}
    for runs in duplicate_groups.values():
        ranked = sorted(
            runs,
            key=lambda run: (-preference_score(run["run_id"]), run["run_id"]),
        )
        preferred = ranked[0]
        preferred_run_ids.add(preferred["run_id"])
        for run in ranked[1:]:
            duplicate_exclusions[run["run_id"]] = (
                f"duplicate_completed_run_prefer:{preferred['run_id']}"
            )

    grouped_runs = defaultdict(list)
    for run in all_runs:
        grouped_runs[normalized_group_key(run["config"])].append(run)

    merged_index_rows = []
    excluded_rows = []
    for group_key, group_runs in sorted(grouped_runs.items(), key=lambda item: str(item[0])):
        group_info = group_label_from_key(group_key)
        expected_games = sorted(
            {game for run in group_runs for game in run["expected_games"]}
        )
        included_runs = []
        manifest = []

        for run in sorted(group_runs, key=lambda item: item["run_id"]):
            if not run["is_complete"]:
                reason = run["complete_reason"]
                included = False
            elif run["run_id"] not in preferred_run_ids:
                reason = duplicate_exclusions.get(run["run_id"], "duplicate_completed_run")
                included = False
            else:
                reason = "included"
                included = True
                included_runs.append(run)

            manifest.append(
                {
                    "run_id": run["run_id"],
                    "run_dir": str(run["run_dir"]),
                    "expected_games": run["expected_games"],
                    "num_matches": run["num_matches"],
                    "counts": run["counts"],
                    "ok_counts": run["ok_counts"],
                    "is_complete": run["is_complete"],
                    "decision": reason,
                    "included": included,
                }
            )

            if not included:
                excluded_rows.append(
                    {
                        "run_id": run["run_id"],
                        "comparison": run["config"].get("comparison"),
                        "prompt_output_mode": run["config"].get("prompt_output_mode"),
                        "left_agent": run["config"].get("left_agent"),
                        "right_agent": run["config"].get("right_agent"),
                        "left_model_name": run["config"].get("left_model_name"),
                        "right_model_name": run["config"].get("right_model_name"),
                        "games": ",".join(run["expected_games"]),
                        "reason": reason,
                    }
                )

        if not included_runs:
            continue

        merged_name = merged_run_name(included_runs)
        merged_dir = by_experiment_root / merged_name
        records = []
        source_runs_by_game = defaultdict(set)
        for run in included_runs:
            for record in run["records"]:
                merged_record = dict(record)
                merged_record["source_run_id"] = run["run_id"]
                merged_record["source_run_dir"] = str(run["run_dir"])
                records.append(merged_record)
                source_runs_by_game[record["game"]].add(run["run_id"])

        merged_config = dict(included_runs[0]["config"])
        merged_config["games"] = sorted({record["game"] for record in records})
        merged_config["source_runs"] = [run["run_id"] for run in included_runs]

        included_games = sorted({record["game"] for record in records})
        missing_games = sorted(set(expected_games) - set(included_games))
        status = "complete_group" if not missing_games else "partial_group_missing_shards"

        summary = summarize_merged(records, merged_config, merged_name, source_runs_by_game)
        summary["merge_status"] = status
        summary["expected_group_games"] = expected_games
        summary["missing_group_games"] = missing_games
        summary["source_runs"] = [run["run_id"] for run in included_runs]

        write_jsonl(merged_dir / "matches.jsonl", records)
        write_json(merged_dir / "summary.json", summary)
        write_summary_csv(merged_dir / "summary.csv", summary)
        write_json(merged_dir / "source_manifest.json", manifest)
        write_json(
            merged_dir / "merge_notes.json",
            build_merge_notes(merged_name, group_info, included_runs, missing_games, status),
        )

        merged_index_rows.append(
            {
                "merged_run_name": merged_name,
                "status": status,
                "comparison": group_info["comparison"],
                "prompt_output_mode": group_info["prompt_output_mode"],
                "left_agent": group_info["left_agent"],
                "right_agent": group_info["right_agent"],
                "left_model_name": group_info["left_model_name"],
                "right_model_name": group_info["right_model_name"],
                "games": ",".join(included_games),
                "missing_games": ",".join(missing_games),
                "num_source_runs": len(included_runs),
                "num_records": len(records),
                "output_dir": str(merged_dir),
            }
        )

    write_csv(
        output_root / "index.csv",
        sorted(merged_index_rows, key=lambda row: row["merged_run_name"]),
        [
            "merged_run_name",
            "status",
            "comparison",
            "prompt_output_mode",
            "left_agent",
            "right_agent",
            "left_model_name",
            "right_model_name",
            "games",
            "missing_games",
            "num_source_runs",
            "num_records",
            "output_dir",
        ],
    )
    write_csv(
        output_root / "excluded_runs.csv",
        sorted(excluded_rows, key=lambda row: row["run_id"]),
        [
            "run_id",
            "comparison",
            "prompt_output_mode",
            "left_agent",
            "right_agent",
            "left_model_name",
            "right_model_name",
            "games",
            "reason",
        ],
    )
    write_json(
        output_root / "merge_overview.json",
        {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "input_root": str(input_root),
            "output_root": str(output_root),
            "merged_runs": len(merged_index_rows),
            "excluded_runs": len(excluded_rows),
        },
    )
    print(f"saved merged results to {output_root}")


if __name__ == "__main__":
    main()
