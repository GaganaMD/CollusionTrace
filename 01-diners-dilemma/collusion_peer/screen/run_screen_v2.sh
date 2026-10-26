#!/usr/bin/env bash
# Model screen, v2: all 5 seats one model, 2 trials x 4 rounds, one model at a time.
# Changes from v1 (which hung when the laptop suspended mid-run):
#  - wrapped in systemd-inhibit by the caller so the machine doesn't sleep
#  - python -u so logs are written live
#  - per-model OpenRouter spend guard ($0.80) and total guard ($8.00)
#  - timeout sends KILL 30 s after TERM
# Skips models that already finished (exit 0) in screen_log.jsonl.
set -u
cd "$(dirname "$0")/../harness"
set -a; . ./.env; set +a

MODELS=(
  meta-llama/llama-4-scout
  meta-llama/llama-4-maverick
  mistralai/mistral-small-3.2-24b-instruct
  google/gemini-3.5-flash-lite
  google/gemini-3.8-flash
  anthropic/claude-haiku-5.5
  anthropic/claude-sonnet-5.5
  deepseek/deepseek-v4.1-flash
  deepseek/deepseek-v4-pro
  z-ai/glm-5.3-flash
  z-ai/glm-5.3
  google/gemma-4-26b-a4b-it
  google/gemma-4-31b-it
  meta-llama/llama-3.3-70b-instruct
  qwen/qwen3.6-35b-a3b
  gpt-4o-mini
  gpt-4o
  gpt-5-mini
  gpt-5.2
  mistralai/mistral-large-4-0
)
OUT=outputs/screen
LOG=../screen/screen_log.jsonl
MODEL_CAP=0.80
TOTAL_CAP=8.00
mkdir -p "$OUT" ../screen/logs

usage() { curl -s -m 15 https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq -r '.data.total_usage // "null"'; }
gt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a>b)}'; }

for m in "${MODELS[@]}"; do
  safe=${m//\//_}
  if grep -q "\"model\": \"$m\", \"exit\": 0" "$LOG" 2>/dev/null; then echo "skip $m (done)"; continue; fi
  before=$(usage)
  if gt "$before" "$TOTAL_CAP"; then echo "total spend cap reached ($before)"; break; fi
  start=$(date +%s)
  timeout -k 30 1500 .venv/bin/python -u experiments/run_endogenous.py --game diners --agents 5 \
    --trials 2 --rounds 4 --model "$m" --use-queue --round-robin --output-dir "$OUT" \
    > "../screen/logs/$safe.log" 2>&1 &
  pid=$!
  capped=0
  while kill -0 $pid 2>/dev/null; do
    sleep 30
    case "$m" in gpt-*) continue ;; esac
    now=$(usage)
    if [ "$now" != "null" ] && gt "$(awk -v a="$now" -v b="$before" 'BEGIN{print a-b}')" "$MODEL_CAP"; then
      echo "spend cap hit for $m, stopping"; kill $pid; sleep 5; kill -9 $pid 2>/dev/null; capped=1
    fi
  done
  wait $pid; code=$?
  [ $capped -eq 1 ] && code=99
  after=$(usage); secs=$(( $(date +%s) - start ))
  echo "{\"model\": \"$m\", \"exit\": $code, \"seconds\": $secs, \"or_usage_before\": $before, \"or_usage_after\": $after}" >> "$LOG"
  echo "done $m exit=$code ${secs}s"
done
echo "SCREEN_DONE"
