import argparse
import csv
import json
import re
from pathlib import Path

from dataset.utils import get_Nash_equilibrium


MATRIX_ROW_RE = re.compile(
    r"^\|[^|]*A(?P<row>[12])[^|]*\|\s*(?P<a11>\d+)\s*\\\s*(?P<b11>\d+)\s*\|\s*(?P<a12>\d+)\s*\\\s*(?P<b12>\d+)\s*\|"
)
ANY_MATRIX_ROW_RE = re.compile(
    r"^\|[^|]*\|\s*(?P<a11>\d+)\s*\\\s*(?P<b11>\d+)\s*\|\s*(?P<a12>\d+)\s*\\\s*(?P<b12>\d+)\s*\|"
)
PROMPTINGS = (
    "theory_refotom",
    "theory_resotom",
    "theory_fotom",
    "theory_sotom",
    "theory_cot",
    "resotom",
    "refotom",
    "sotom",
    "fotom",
    "theory",
    "direct",
    "cot",
)


def parse_payoff_matrix(path):
    pA = [[None, None], [None, None]]
    pB = [[None, None], [None, None]]

    next_unlabeled_row = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = MATRIX_ROW_RE.match(line)
        if match:
            row = int(match.group("row")) - 1
        else:
            match = ANY_MATRIX_ROW_RE.match(line)
            if not match:
                continue
            row = next_unlabeled_row
            next_unlabeled_row += 1
            if row > 1:
                continue
        pA[row][0] = int(match.group("a11"))
        pB[row][0] = int(match.group("b11"))
        pA[row][1] = int(match.group("a12"))
        pB[row][1] = int(match.group("b12"))

    if any(value is None for row in pA + pB for value in row):
        raise ValueError(f"Could not parse payoff matrix from {path}")

    return pA, pB


def normalize_choice_set(response):
    return sorted((str(a), str(b)) for a, b in response)


def parse_result_filename(path):
    family, variation, rest = path.stem.split("_", 2)
    for prompting in PROMPTINGS:
        suffix = f"_{prompting}"
        if rest.endswith(suffix):
            return family, variation, rest[: -len(suffix)], prompting
    raise ValueError(f"Could not parse result filename: {path.name}")


def evaluate_file(result_path, dataset_dir):
    family, variation, model, prompting = parse_result_filename(result_path)
    pA, pB = parse_payoff_matrix(dataset_dir / f"{family}_{variation}.txt")
    expected, _ = get_Nash_equilibrium(pA, pB)
    expected = normalize_choice_set(expected)

    data = json.loads(result_path.read_text())
    responses = data.get("responses", [])
    correct = 0
    valid = 0

    for response in responses:
        try:
            predicted = normalize_choice_set(response)
        except Exception:
            continue

        valid += 1
        if predicted == expected:
            correct += 1

    tries = data.get("tries", len(responses))
    return {
        "family": family,
        "variation": variation,
        "model": model,
        "prompting": prompting,
        "tries": tries,
        "valid": valid,
        "correct": correct,
        "accuracy": correct / valid if valid else 0.0,
        "expected": expected,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="results/story-based")
    parser.add_argument("--dataset_dir", default="dataset/story-based")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    dataset_dir = Path(args.dataset_dir)
    rows = [
        evaluate_file(path, dataset_dir)
        for path in sorted(results_dir.glob("*.json"))
    ]

    summary = {}
    for row in rows:
        key = (row["model"], row["prompting"])
        current = summary.setdefault(key, {"files": 0, "valid": 0, "correct": 0})
        current["files"] += 1
        current["valid"] += row["valid"]
        current["correct"] += row["correct"]

    print("model,prompting,files,valid,correct,accuracy")
    for (model, prompting), values in sorted(summary.items()):
        accuracy = values["correct"] / values["valid"] if values["valid"] else 0.0
        print(
            f"{model},{prompting},{values['files']},{values['valid']},"
            f"{values['correct']},{accuracy:.4f}"
        )

    if args.output:
        with open(args.output, "w", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "family",
                    "variation",
                    "model",
                    "prompting",
                    "tries",
                    "valid",
                    "correct",
                    "accuracy",
                    "expected",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    main()
