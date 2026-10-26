#!/bin/bash
# Modal-served run: batches of 2 trials (7 conditions); no new batch after DEADLINE_EPOCH (containers hard-cap at 40 min).
cd "$(dirname "$0")/../.."
U=https://kaustubh73--pgg-swap-split
export PGG_BASE_URL=$U-base.us-east.modal.run/v1
export PGG_URLS="{\"Qwen/Qwen2.5-7B-Instruct\":\"$U-base.us-east.modal.run/v1\",\"ibm-granite/granite-3.3-8b-instruct\":\"$U-other.us-east.modal.run/v1\",\"Qwen/Qwen2.5-32B-Instruct-AWQ\":\"$U-strong.us-east.modal.run/v1\"}"
for k in 0 1 2 3 4; do
  [ "$(date +%s)" -ge "$DEADLINE_EPOCH" ] && break
  python3 experiments/pgg_swap/pgg_swap.py --trials 2 --conditions 1,2,3,4,5,6,7 --out outputs/pgg_swap/modal_main/b$k \
    --seed $((200+k)) --concurrency 64 --models experiments/pgg_swap/models.json
done
echo done > outputs/pgg_swap/modal_main/DONE
