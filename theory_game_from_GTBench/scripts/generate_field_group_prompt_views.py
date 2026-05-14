from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = REPO_ROOT / "analysis"
BANK_PATH = ANALYSIS_DIR / "high_reasoning_field_bank_all_games.md"
GROUP_PATH = ANALYSIS_DIR / "high_reasoning_field_groups_size6_random.md"
REASONING_OUT = ANALYSIS_DIR / "high_reasoning_field_groups_size6_prompt_ready.md"
DISTILL_OUT = ANALYSIS_DIR / "high_distill_field_groups_size6_prompt_ready.md"

GAME_TITLES = {
    "Tic-Tac-Toe",
    "Connect Four",
    "Breakthrough",
    "Nim",
    "Pig",
    "First-Sealed Auction",
    "Kuhn Poker",
    "Liar's Dice",
    "Negotiation",
    "Iterated Prisoner's Dilemma",
}


def parse_bank_descriptions(path: Path) -> dict[str, dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    game = None
    current_field = None
    current_desc = []
    result: dict[str, dict[str, str]] = {}

    def flush() -> None:
        nonlocal current_field, current_desc
        if game and current_field:
            result.setdefault(game, {})[current_field] = " ".join(
                part.strip() for part in current_desc if part.strip()
            ).strip()
        current_field = None
        current_desc = []

    for line in lines:
        if line.startswith("## "):
            flush()
            title = line[3:]
            game = title if title in GAME_TITLES else None
            if game:
                result.setdefault(game, {})
            continue
        if not game:
            continue
        if line.startswith("- `"):
            flush()
            match = re.match(r"- `([^`]+)`: ?(.*)", line)
            if not match:
                continue
            current_field = match.group(1)
            current_desc = [match.group(2)]
            continue
        if current_field and line.startswith("  "):
            current_desc.append(line.strip())
            continue
        if current_field and line.strip() == "":
            flush()
    flush()
    return result


def parse_groups(path: Path) -> dict[str, list[list[str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    game = None
    groups: dict[str, list[list[str]]] = {}
    current_group: list[str] | None = None

    for line in lines:
        if line.startswith("## "):
            title = line[3:]
            game = title if title in GAME_TITLES else None
            if game:
                groups.setdefault(game, [])
            current_group = None
            continue
        if not game:
            continue
        if line.startswith("### Group "):
            current_group = []
            groups[game].append(current_group)
            continue
        if current_group is not None and line.startswith("- `"):
            current_group.append(line.split("`")[1])
    return groups


def reasoning_template(game: str, group_idx: int, fields: list[str], descs: dict[str, str]) -> str:
    bullet_lines = "\n".join(
        f"- `{field}`: {descs[field]}" for field in fields
    )
    return f"""## {game}

### Group {group_idx}

Use only these computed fields:

{bullet_lines}

Suggested `high_reasoning` prompt block:

```text
You are executing a high_reasoning field program for {game}.

Current state and legal actions are already given.
Do not restate the whole game.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
{chr(10).join(f"- {field}: {descs[field]}" for field in fields)}

After computing them:
1. compare legal actions using only these fields,
2. explain the choice briefly through the computed field values,
3. choose one legal action,
4. return only the final action in the required output format.

Do not output long chain-of-thought.
Do not add a hand-written policy rule.
Use the fields as evidence, not as decorative text.
```
"""


def _positive_fields(fields: list[str]) -> list[str]:
    keys = (
        "immediate_win",
        "immediate_promotion",
        "double_threat",
        "draw_preserving",
        "stop_wins_now",
        "positive_surplus_actions",
        "conservative_raise_candidates",
        "expected_surplus_by_bid",
        "future_cooperation_value_proxy",
    )
    return [field for field in fields if any(key in field for key in keys)]


def _defense_fields(fields: list[str]) -> list[str]:
    keys = (
        "immediate_block",
        "opponent_immediate",
        "challenge_threshold",
        "repair_opportunity",
        "punishment_credibility",
        "stop_leaves_opponent_near_finish",
    )
    return [field for field in fields if any(key in field for key in keys)]


def _filter_fields(fields: list[str]) -> list[str]:
    keys = (
        "unsafe",
        "overbid",
        "terminal_take_last",
        "forced_loss",
        "aggressive_raise_candidates",
        "exploitation_risk",
    )
    return [field for field in fields if any(key in field for key in keys)]


def _score_fields(fields: list[str]) -> list[str]:
    keys = (
        "expected",
        "value",
        "payoff",
        "margin",
        "probability",
        "distance",
        "pressure",
        "risk",
        "parity",
        "count",
        "class",
        "position_value",
        "nim_sum",
        "surplus",
    )
    return [field for field in fields if any(key in field for key in keys)]


def distill_program_lines(fields: list[str]) -> list[str]:
    positive = _positive_fields(fields)
    defense = _defense_fields(fields)
    filtered = _filter_fields(fields)
    scored = [field for field in _score_fields(fields) if field not in filtered]

    lines = ["P0. Choose only from legal actions."]
    priority = 1
    if positive:
        joined = ", ".join(positive)
        lines.append(
            f"P{priority}. If any forcing or immediately favorable candidate set is exposed by [{joined}], prioritize actions supported by those fields."
        )
        priority += 1
    if defense:
        joined = ", ".join(defense)
        lines.append(
            f"P{priority}. If opponent threat or forced defense is exposed by [{joined}], keep only legal actions that answer that threat."
        )
        priority += 1
    if filtered:
        joined = ", ".join(filtered)
        lines.append(
            f"P{priority}. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [{joined}]."
        )
        priority += 1
    if scored:
        joined = ", ".join(scored)
        lines.append(
            f"P{priority}. Among remaining actions, rank them using the comparative evidence in [{joined}] and choose the strongest supported action."
        )
        priority += 1
    lines.append(
        f"P{priority}. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback."
    )
    return lines


def distill_template(game: str, group_idx: int, fields: list[str], descs: dict[str, str]) -> str:
    bullet_lines = "\n".join(
        f"- `{field}`: {descs[field]}" for field in fields
    )
    program = "\n".join(distill_program_lines(fields))
    return f"""## {game}

### Group {group_idx}

Use only these computed fields:

{bullet_lines}

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for {game}.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
{chr(10).join(f"- {field}: {descs[field]}" for field in fields)}

Decision program:
{program}

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```
"""


def build_reasoning_doc(groups: dict[str, list[list[str]]], descs: dict[str, dict[str, str]]) -> str:
    parts = [
        "# Prompt-Ready Size-6 Groups For High Reasoning",
        "",
        "## Purpose",
        "",
        "This file rewrites the sampled size-6 field groups into prompt-ready form",
        "for the `high_reasoning` setting.",
        "",
        "Mode interpretation:",
        "",
        "- use only the selected 6 fields,",
        "- compute those fields from the current state,",
        "- use them as evidence,",
        "- do not attach an explicit hand-written decision program.",
        "",
    ]
    for game, game_groups in groups.items():
        for idx, fields in enumerate(game_groups, start=1):
            parts.append(reasoning_template(game, idx, fields, descs[game]))
    return "\n".join(parts).rstrip() + "\n"


def build_distill_doc(groups: dict[str, list[list[str]]], descs: dict[str, dict[str, str]]) -> str:
    parts = [
        "# Prompt-Ready Size-6 Groups For High Distill",
        "",
        "## Purpose",
        "",
        "This file rewrites the sampled size-6 field groups into prompt-ready form",
        "for the `high_distill` setting.",
        "",
        "Mode interpretation:",
        "",
        "- use the same selected 6 fields,",
        "- compute them first,",
        "- then execute a compact decision program derived from those fields,",
        "- keep the final action aligned with the highest-priority applicable rule.",
        "",
    ]
    for game, game_groups in groups.items():
        for idx, fields in enumerate(game_groups, start=1):
            parts.append(distill_template(game, idx, fields, descs[game]))
    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    descriptions = parse_bank_descriptions(BANK_PATH)
    groups = parse_groups(GROUP_PATH)
    REASONING_OUT.write_text(build_reasoning_doc(groups, descriptions), encoding="utf-8")
    DISTILL_OUT.write_text(build_distill_doc(groups, descriptions), encoding="utf-8")


if __name__ == "__main__":
    main()
