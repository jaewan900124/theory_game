# Theory Game

This repository combines two theory-of-mind and game-theoretic reasoning benchmark projects:

- `theory_game_from_TMGBench/`: TMGBench-based 2x2 strategic game evaluation with direct, theory-guided, and CoT-style prompts.
- `theory_game_from_GTBench/`: GTBench-derived game reasoning project.

## Usage

Run each project from its own subdirectory because scripts use project-local relative paths.

```bash
cd theory_game_from_TMGBench
python -m scripts.eval_classic -h
python -m scripts.eval_story_based -h
```

```bash
cd theory_game_from_GTBench
python -m scripts --help
```

## Notes

- Local secrets such as `.env` and `config.env` are intentionally excluded.
- Generated outputs under `results/` are excluded by default.
- Large or license-sensitive references under `theory_game_from_TMGBench/ref/` are excluded by default.
