#!/usr/bin/env bash
# Model screen, v4 (small models only, per user request):
# Model screen, v3: resumes after the harness fixes (API retries, GPT-5 reply
# parsing, judge routing). Runs the models not yet done, then reruns the models
# whose results came from the old client with poor parse rates.
# Each model: all 5 seats one model, 2 trials x 4 rounds, one model at a time.
# Run under systemd-inhibit so the machine doesn't sleep.
set -u
cd "$(dirname "$0")/../harness"
set -a; . ./.env; set +a

NEW=(
  google/gemma-4-26b-a4b-it
  google/gemma-4-31b-it
  qwen/qwen3.6-35b-a3b
  gpt-4o-mini
  gpt-5-mini
)
RERUN=(
  google/gemini-3.8-flash
  deepseek/deepseek-v4.1-flash
)
OUT=outputs/screen
DIR=$OUT/diners/5agents
LOG=../screen/screen_log.jsonl
MODEL_CAP=0.80
TOTAL_CAP=8.00

usage() { curl -s -m 15 https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq -r '.data.total_usage // "null"'; }
gt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a>b)}'; }

run_model() {  # $1 = model, $2 = "rerun" or ""
  local m=$1 tag=$2 safe=${1//\//_} before after start secs pid code capped now suffix=""
  before=$(usage)
  if gt "$before" "$TOTAL_CAP"; then echo "total spend cap reached ($before)"; return 1; fi
  if [ -n "$tag" ]; then
    suffix="_rerun"
    [ -f "$DIR/${safe}_endogenous.json" ] && mv "$DIR/${safe}_endogenous.json" "$DIR/${safe}_endogenous_oldclient.json"
  fi
  start=$(date +%s)
  timeout -k 30 1500 .venv/bin/python -u experiments/run_endogenous.py --game diners --agents 5 \
    --trials 2 --rounds 4 --model "$m" --use-queue --round-robin --output-dir "$OUT" \
    > "../screen/logs/${safe}${suffix}.log" 2>&1 &
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
  if [ -n "$tag" ]; then
    echo "{\"model\": \"$m\", \"exit\": $code, \"seconds\": $secs, \"or_usage_before\": $before, \"or_usage_after\": $after, \"rerun\": \"fixed_client\"}" >> "$LOG"
  else
    echo "{\"model\": \"$m\", \"exit\": $code, \"seconds\": $secs, \"or_usage_before\": $before, \"or_usage_after\": $after}" >> "$LOG"
  fi
  echo "done $m exit=$code ${secs}s"
}

for m in "${NEW[@]}"; do
  grep -q "\"model\": \"$m\", \"exit\": 0" "$LOG" && { echo "skip $m (done)"; continue; }
  run_model "$m" "" || break
done
for m in "${RERUN[@]}"; do
  grep -q "\"model\": \"$m\", \"exit\": 0, .*\"rerun\"" "$LOG" && { echo "skip rerun $m (done)"; continue; }
  run_model "$m" "rerun" || break
done
echo "SCREEN_DONE"
