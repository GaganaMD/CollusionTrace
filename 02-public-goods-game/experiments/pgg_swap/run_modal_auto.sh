#!/bin/bash
# wake 3 endpoints -> run harness -> hard stop + `modal app stop pgg-swap-split` (even if the run is unfinished)
cd "$(dirname "$0")/../.."
U=https://kaustubh73--pgg-swap-split
for i in $(seq 1 40); do ok=0; for n in base other strong; do
  c=$(curl -s -m 60 -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $PGG_TOKEN" $U-$n.us-east.modal.run/v1/models); [ "$c" = 200 ] && ok=$((ok+1)); done
  echo "$(date +%T) up=$ok/3"; [ $ok = 3 ] && break; sleep 20; done
[ $ok = 3 ] || { modal app stop pgg-swap-split; echo "never up; stopped"; exit 1; }
START=$(date +%s)
export PGG_BASE_URL=$U-base.us-east.modal.run/v1
export PGG_URLS="{\"Qwen/Qwen2.5-7B-Instruct\":\"$U-base.us-east.modal.run/v1\",\"ibm-granite/granite-3.3-8b-instruct\":\"$U-other.us-east.modal.run/v1\",\"Qwen/Qwen2.5-32B-Instruct-AWQ\":\"$U-strong.us-east.modal.run/v1\"}"
python3 experiments/pgg_swap/pgg_swap.py --trials 6 --conditions 1,2,3,4,5,6,7 --out outputs/pgg_swap/modal_main/m0 --seed 400 --concurrency 64 --models experiments/pgg_swap/models.json &
P=$!
while kill -0 $P 2>/dev/null && [ $(( $(date +%s) - START )) -lt $((19*60)) ]; do sleep 10; done
kill $P 2>/dev/null; echo "harness ended $(date +%T) after $(( $(date +%s) - START ))s"
modal app stop pgg-swap-split; echo "app stopped"
