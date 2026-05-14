import argparse
import json
import os
from pathlib import Path
import random
import sys

try:
    import fire
except ModuleNotFoundError:
    fire = None

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import api.util as util


def _instantiate_agent(agent_class, kwargs):
    return agent_class(team_id=-1, agent_id=-1, **kwargs)


def _agent_type_id(agent_class, kwargs):
    return _instantiate_agent(agent_class, kwargs).agent_type_id


def _default_transcript_path(game_id, agent_1_id, agent_2_id):
    safe_name = f"{agent_1_id}__vs__{agent_2_id}".replace("/", "_")
    return os.path.join("theory_transcripts", game_id, safe_name + ".jsonl")


def _save_transcript_line(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def play_game(
    game_path,
    num_matches=1,
    show_state=False,
    save_results=True,
    save_transcript=True,
    transcript_path=None,
    agent_1_path="agents.theory_prompt_agent.TheoryPromptAgent",
    agent_2_path="agents.theory_prompt_agent.TheoryPromptAgent",
    agent_1_mode="high_reasoning",
    agent_2_mode="high_distill",
    agent_1_backend="ollama",
    agent_2_backend="ollama",
    agent_1_model_name="qwen3:14b",
    agent_2_model_name="qwen3:14b",
    agent_1_kwargs=None,
    agent_2_kwargs=None,
):
    agent_1_kwargs = dict(agent_1_kwargs or {})
    agent_2_kwargs = dict(agent_2_kwargs or {})
    agent_1_kwargs.setdefault("agent_mode", agent_1_mode)
    agent_1_kwargs.setdefault("backend", agent_1_backend)
    agent_1_kwargs.setdefault("model_name", agent_1_model_name)
    agent_2_kwargs.setdefault("agent_mode", agent_2_mode)
    agent_2_kwargs.setdefault("backend", agent_2_backend)
    agent_2_kwargs.setdefault("model_name", agent_2_model_name)

    agent_1_class = util.import_class(agent_1_path)
    agent_2_class = util.import_class(agent_2_path)
    agent_1_id = _agent_type_id(agent_1_class, agent_1_kwargs)
    agent_2_id = _agent_type_id(agent_2_class, agent_2_kwargs)

    if agent_1_id == agent_2_id:
        print("Both configured agents resolve to the same agent_type_id. Match results will not be saved.")
        save_results = False

    game_class = util.import_class(game_path)
    player_1_total = 0.0
    player_2_total = 0.0

    try:
        matches = util.load_json("matches.json")
    except ValueError:
        matches = []

    historical_total = 0.0
    historical_matches = 0
    for match in matches:
        if match.get("game") == game_class.id and agent_1_id in match and agent_2_id in match:
            historical_total += match[agent_1_id]
            historical_matches += 1

    if historical_matches > 0:
        print(f"Historical average scores across {historical_matches} matches:")
        print(f"{agent_1_id} avg score: {historical_total / historical_matches}")
        print(f"{agent_2_id} avg score: {1 - (historical_total / historical_matches)}")

    transcript_path = transcript_path or _default_transcript_path(game_class.id, agent_1_id, agent_2_id)

    for match_index in range(num_matches):
        swapped = bool(random.choice([0, 1]))
        if swapped:
            game = game_class(
                show_state=show_state,
                agent_1_kwargs=agent_2_kwargs,
                agent_2_kwargs=agent_1_kwargs,
            )
            game.init_game(agent_2_class, agent_1_class)
            player_2_score, player_1_score = game.play()
        else:
            game = game_class(
                show_state=show_state,
                agent_1_kwargs=agent_1_kwargs,
                agent_2_kwargs=agent_2_kwargs,
            )
            game.init_game(agent_1_class, agent_2_class)
            player_1_score, player_2_score = game.play()

        print(f"{agent_1_id} score: {player_1_score}")
        print(f"{agent_2_id} score: {player_2_score}")

        player_1_total += player_1_score
        player_2_total += player_2_score

        if save_results:
            matches = util.load_json("matches.json")
            matches.append(
                {
                    "game": game_class.id,
                    agent_1_id: player_1_score,
                    agent_2_id: player_2_score,
                }
            )
            util.save_json(matches, "matches.json")
            print("Saved match information")

        if save_transcript:
            traces = []
            for agent in getattr(game, "agents", []) or []:
                traces.append(
                    {
                        "agent_type_id": agent.agent_type_id,
                        "team_id": agent.team_id,
                        "agent_id": agent.agent_id,
                        "traces": getattr(agent, "traces", []),
                    }
                )
            _save_transcript_line(
                transcript_path,
                {
                    "match_index": match_index,
                    "game": game_class.id,
                    "swapped_seating": swapped,
                    "agent_1_id": agent_1_id,
                    "agent_2_id": agent_2_id,
                    "agent_1_score": player_1_score,
                    "agent_2_score": player_2_score,
                    "agent_1_kwargs": agent_1_kwargs,
                    "agent_2_kwargs": agent_2_kwargs,
                    "agent_traces": traces,
                },
            )

    print("")
    print(f"Agent 1 ({agent_1_id}) average score: {player_1_total / num_matches}")
    print(f"Agent 2 ({agent_2_id}) average score: {player_2_total / num_matches}")


def _parse_kwargs_arg(value):
    if not value:
        return {}
    return json.loads(value)


def _main_with_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_path", required=True)
    parser.add_argument("--num_matches", type=int, default=1)
    parser.add_argument("--show_state", action="store_true")
    parser.add_argument("--save_results", action="store_true")
    parser.add_argument("--save_transcript", action="store_true")
    parser.add_argument("--transcript_path")
    parser.add_argument("--agent_1_path", default="agents.theory_prompt_agent.TheoryPromptAgent")
    parser.add_argument("--agent_2_path", default="agents.theory_prompt_agent.TheoryPromptAgent")
    parser.add_argument("--agent_1_mode", default="high_reasoning")
    parser.add_argument("--agent_2_mode", default="high_distill")
    parser.add_argument("--agent_1_backend", default="ollama")
    parser.add_argument("--agent_2_backend", default="ollama")
    parser.add_argument("--agent_1_model_name", default="qwen3:14b")
    parser.add_argument("--agent_2_model_name", default="qwen3:14b")
    parser.add_argument("--agent_1_kwargs", default="")
    parser.add_argument("--agent_2_kwargs", default="")
    args = parser.parse_args()
    play_game(
        game_path=args.game_path,
        num_matches=args.num_matches,
        show_state=args.show_state,
        save_results=args.save_results,
        save_transcript=args.save_transcript,
        transcript_path=args.transcript_path,
        agent_1_path=args.agent_1_path,
        agent_2_path=args.agent_2_path,
        agent_1_mode=args.agent_1_mode,
        agent_2_mode=args.agent_2_mode,
        agent_1_backend=args.agent_1_backend,
        agent_2_backend=args.agent_2_backend,
        agent_1_model_name=args.agent_1_model_name,
        agent_2_model_name=args.agent_2_model_name,
        agent_1_kwargs=_parse_kwargs_arg(args.agent_1_kwargs),
        agent_2_kwargs=_parse_kwargs_arg(args.agent_2_kwargs),
    )


if __name__ == "__main__":
    if fire is None:
        _main_with_argparse()
    else:
        fire.Fire(play_game)
