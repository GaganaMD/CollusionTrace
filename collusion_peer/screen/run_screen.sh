#!/usr/bin/env bash
# Model screen: each model plays all 5 seats of the Diner's Dilemma, 2 trials x 4 rounds.
# Runs models one at a time so OpenRouter spend can be measured per model.
# Usage: screen/run_screen.sh            (from /home/vsskl/collusion_peer)
set -u
cd "$(dirname "$0")/../harness"
set -a; . ./.env; set +a

MODELS=(
  meta-llama/llama-4-scout
  meta-llama/llama-4-maverick
  mistralai/mistral-small-3.2-24b-instruct
  mistralai/mistral-large-4-0
  google/gemini-3.5-flash-lite
  google/gemini-3.8-flash
  anthropic/claude-haiku-5.5
  anthropic/claude-sonnet-5.5
  deepseek/deepseek-v4.1-flash
  deepseek/deepseek-v4-pro
  z-ai/glm-5.3-flash
  z-ai/glm-5.3
  google/gemma-4-26b-a4b-it
  meta-llama/llama-3.3-70b-instruct
  gpt-4o-mini
  gpt-4o
  gpt-5.2
)
OUT=outputs/screen
LOG=../screen/screen_log.jsonl
mkdir -p "$OUT" ../screen/logs

usage() { curl -s -m 15 https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq -r '.data.total_usage // "null"'; }
notify() { curl -s -m 10 -H "Title: Model screen" -d "$1" "https://ntfy.sh/$(cat ~/.claude2/hooks/ntfy-topic)" >/dev/null || true; }

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
  [ $code -ne 0 ] && notify "FAILED: $m (exit $code)"
done
notify "Screen finished: $(grep -c '"exit": 0' "$LOG") of ${#MODELS[@]} models OK"
