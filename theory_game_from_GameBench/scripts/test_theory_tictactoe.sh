python api/play_theory_game.py \
  --game_path games.tic_tac_toe.TicTacToe \
  --agent_1_mode high_reasoning \
  --agent_2_mode high_distill \
  --agent_1_backend ollama \
  --agent_2_backend ollama \
  --agent_1_model_name qwen3:14b \
  --agent_2_model_name qwen3:14b \
  --show_state \
  --num_matches 1
