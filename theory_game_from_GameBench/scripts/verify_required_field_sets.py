#!/usr/bin/env python
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prompts.theory_fields import (  # noqa: E402
    GAMEBENCH_ACTIVE_CONTEXTS,
    REQUIRED_FIELD_SETS_BY_GAME_CONTEXT,
)


DOC_GAME_TO_ID = {
    "Air, Land, and Sea": "air_land_sea",
    "Arctic Scavengers": "arctic_scavengers",
    "Are You the Traitor?": "are_you_the_traitor",
    "Codenames": "codenames",
    "Hive": "hive",
    "Pit": "pit",
    "Santorini": "santorini",
    "Sea Battle": "sea_battle",
    "Two Rooms and a Boom": "two_rooms_and_a_boom",
    "Tic-Tac-Toe": "tic_tac_toe",
}


def parse_required_field_doc(path: Path):
    text = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"^(##|###)\s+(.+)$", text, re.M))
    required_sets = {}
    current_game = None

    for index, heading in enumerate(headings):
        level = heading.group(1)
        title = heading.group(2).strip()
        body_start = heading.end()
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[body_start:body_end]

        if level == "##":
            if title not in DOC_GAME_TO_ID:
                raise ValueError(f"Unknown game heading in doc: {title}")
            current_game = DOC_GAME_TO_ID[title]
            required_sets.setdefault(current_game, {})
            continue

        if level != "###":
            continue
        if not current_game:
            raise ValueError(f"Context heading appears before a game heading: {title}")

        required_match = re.search(r"Required:\n((?:- .+\n)+)", body)
        if not required_match:
            raise ValueError(f"{current_game}/{title} is missing a Required block")
        required_sets[current_game][title] = [
            line[2:].strip() for line in required_match.group(1).splitlines()
        ]

    return required_sets


def main():
    doc_path = ROOT / "docs" / "required_field_sets.md"
    doc_sets = parse_required_field_doc(doc_path)
    errors = []

    active_contexts = {
        game: set(spec.get("contexts", {}))
        for game, spec in GAMEBENCH_ACTIVE_CONTEXTS.items()
    }
    doc_contexts = {
        game: set(contexts)
        for game, contexts in doc_sets.items()
    }
    code_contexts = {
        game: set(contexts)
        for game, contexts in REQUIRED_FIELD_SETS_BY_GAME_CONTEXT.items()
    }

    if set(doc_sets) != set(GAMEBENCH_ACTIVE_CONTEXTS):
        errors.append(
            "Doc games differ from active-context games: "
            f"doc={sorted(doc_sets)} active={sorted(GAMEBENCH_ACTIVE_CONTEXTS)}"
        )
    if set(REQUIRED_FIELD_SETS_BY_GAME_CONTEXT) != set(GAMEBENCH_ACTIVE_CONTEXTS):
        errors.append(
            "Code required-field games differ from active-context games: "
            f"code={sorted(REQUIRED_FIELD_SETS_BY_GAME_CONTEXT)} "
            f"active={sorted(GAMEBENCH_ACTIVE_CONTEXTS)}"
        )

    for game, active in active_contexts.items():
        if doc_contexts.get(game) != active:
            errors.append(
                f"{game}: doc contexts differ from active contexts: "
                f"doc={sorted(doc_contexts.get(game, []))} active={sorted(active)}"
            )
        if code_contexts.get(game) != active:
            errors.append(
                f"{game}: code contexts differ from active contexts: "
                f"code={sorted(code_contexts.get(game, []))} active={sorted(active)}"
            )

    for game, spec in GAMEBENCH_ACTIVE_CONTEXTS.items():
        for context, context_spec in spec.get("contexts", {}).items():
            active_fields = set(context_spec.get("fields", []))
            doc_fields = doc_sets.get(game, {}).get(context)
            code_fields = REQUIRED_FIELD_SETS_BY_GAME_CONTEXT.get(game, {}).get(context)
            if doc_fields != code_fields:
                errors.append(
                    f"{game}/{context}: doc/code required fields differ: "
                    f"doc={doc_fields} code={code_fields}"
                )
            if code_fields is None:
                continue
            duplicates = sorted({field for field in code_fields if code_fields.count(field) > 1})
            if duplicates:
                errors.append(f"{game}/{context}: duplicate required fields: {duplicates}")
            missing = [field for field in code_fields if field not in active_fields]
            if missing:
                errors.append(
                    f"{game}/{context}: required fields are not active fields: {missing}"
                )

    if errors:
        print("FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    context_count = sum(len(spec.get("contexts", {})) for spec in GAMEBENCH_ACTIVE_CONTEXTS.values())
    field_count = sum(
        len(fields)
        for contexts in REQUIRED_FIELD_SETS_BY_GAME_CONTEXT.values()
        for fields in contexts.values()
    )
    print(
        f"OK: {len(GAMEBENCH_ACTIVE_CONTEXTS)} games, "
        f"{context_count} contexts, {field_count} required field entries verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
