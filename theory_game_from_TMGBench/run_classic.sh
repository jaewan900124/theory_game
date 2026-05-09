source config.env

python -m scripts.eval_classic \
  -s GPT4 \
  -v gpt-4o-mini \
  -k "$KEY" \
  -l "$URL" \
  -p direct \
  -d 0.1
