#!/usr/bin/env bash
# Rerun models that ran before the retry/parse fix to the harness API clients
# (see harness/src/llm/providers/retry_utils.py). Waits for run_screen_v2.sh to finish.
# Old outputs are kept as *_endogenous_oldclient.json; the analysis uses the latest
# log entry per model.
set -u
cd "$(dirname "$0")/../harness"
set -a; . ./.env; set +a

MODELS=(
  google/gemini-3.8-flash
  deepseek/deepseek-v4.1-flash
  deepseek/deepseek-v4-pro
  anthropic/claude-sonnet-5.5
)
OUT=outputs/screen
DIR=$OUT/diners/5agents
LOG=../screen/screen_log.jsonl
MODEL_CAP=0.80
TOTAL_CAP=8.00

while pgrep -f "run_screen_v2.sh$" >/dev/null; do sleep 20; done

usage() { curl -s -m 15 https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq -r '.data.total_usage // "null"'; }
gt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a>b)}'; }

for m in "${MODELS[@]}"; do
  safe=${m//\//_}
  before=$(usage)
  if gt "$before" "$TOTAL_CAP"; then echo "total spend cap reached ($before)"; break; fi
  [ -f "$DIR/${safe}_endogenous.json" ] && mv "$DIR/${safe}_endogenous.json" "$DIR/${safe}_endogenous_oldclient.json"
  start=$(date +%s)
  timeout -k 30 1500 .venv/bin/python -u experiments/run_endogenous.py --game diners --agents 5 \
    --trials 2 --rounds 4 --model "$m" --use-queue --round-robin --output-dir "$OUT" \
    > "../screen/logs/${safe}_rerun.log" 2>&1 &
  pid=$!
  capped=0
  while kill -0 $pid 2>/dev/null; do
    sleep 30
    now=$(usage)
    if [ "$now" != "null" ] && gt "$(awk -v a="$now" -v b="$before" 'BEGIN{print a-b}')" "$MODEL_CAP"; then
      echo "spend cap hit for $m, stopping"; kill $pid; sleep 5; kill -9 $pid 2>/dev/null; capped=1
    fi
  done
  wait $pid; code=$?
  [ $capped -eq 1 ] && code=99
  after=$(usage); secs=$(( $(date +%s) - start ))
  echo "{\"model\": \"$m\", \"exit\": $code, \"seconds\": $secs, \"or_usage_before\": $before, \"or_usage_after\": $after, \"rerun\": \"fixed_client\"}" >> "$LOG"
  echo "done $m exit=$code ${secs}s"
done
echo "RERUN_DONE"
