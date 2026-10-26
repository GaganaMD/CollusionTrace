#!/usr/bin/env bash
# Add gpt-4o (GPT-4o-mini's stronger same-family sibling) after run_screen_v4.sh finishes.
# Same settings as the screen; sends its own per-model notification when done.
set -u
cd "$(dirname "$0")/../harness"
set -a; . ./.env; set +a
LOG=../screen/screen_log.jsonl

while pgrep -f "[r]un_screen_v4.sh$" >/dev/null; do sleep 20; done

usage() { curl -s -m 15 https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq -r '.data.total_usage // "null"'; }
m=gpt-4o
before=$(usage); start=$(date +%s)
timeout -k 30 1500 .venv/bin/python -u experiments/run_endogenous.py --game diners --agents 5 \
  --trials 2 --rounds 4 --model "$m" --use-queue --round-robin --output-dir outputs/screen \
  > "../screen/logs/$m.log" 2>&1
code=$?
after=$(usage); secs=$(( $(date +%s) - start ))
echo "{\"model\": \"$m\", \"exit\": $code, \"seconds\": $secs, \"or_usage_before\": $before, \"or_usage_after\": $after}" >> "$LOG"
echo "done $m exit=$code ${secs}s"
cd ../screen && ../harness/.venv/bin/python -c "
import json, notify_models as n
from analyze_screen import LOG
lines = LOG.read_text().splitlines(); e = json.loads(lines[-1])
n.TOTAL = 16
n.send(*n.message(e, sum(1 for x in lines if '\"rerun\"' not in x), 0))
"
echo "GPT4O_DONE"
