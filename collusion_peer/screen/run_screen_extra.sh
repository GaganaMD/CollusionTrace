#!/usr/bin/env bash
# Extra models for the screen (added after the first 17 started).
# Waits for screen/run_screen.sh to finish, then runs these the same way:
# all 5 seats one model, 2 trials x 4 rounds, one model at a time.
set -u
cd "$(dirname "$0")/../harness"
set -a; . ./.env; set +a

MODELS=(
  google/gemma-4-31b-it
  qwen/qwen3.6-35b-a3b
  gpt-5-mini
)
OUT=outputs/screen
LOG=../screen/screen_log.jsonl

while pgrep -f "screen/run_screen.sh$" >/dev/null; do sleep 20; done

usage() { curl -s -m 15 https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq -r '.data.total_usage // "null"'; }

for m in "${MODELS[@]}"; do
  safe=${m//\//_}
  if grep -q "\"model\": \"$m\", \"exit\": 0" "$LOG" 2>/dev/null; then echo "skip $m (done)"; continue; fi
  before=$(usage); start=$(date +%s)
  timeout 1800 .venv/bin/python experiments/run_endogenous.py --game diners --agents 5 \
    --trials 2 --rounds 4 --model "$m" --use-queue --round-robin --output-dir "$OUT" \
    > "../screen/logs/$safe.log" 2>&1
  code=$?
  after=$(usage); secs=$(( $(date +%s) - start ))
  echo "{\"model\": \"$m\", \"exit\": $code, \"seconds\": $secs, \"or_usage_before\": $before, \"or_usage_after\": $after}" >> "$LOG"
  echo "done $m exit=$code ${secs}s"
done
