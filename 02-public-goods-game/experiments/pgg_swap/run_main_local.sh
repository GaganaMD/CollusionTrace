#!/bin/bash
# Sequential single-trial batches on local Ollama (port 11435); stops starting new trials after DEADLINE (UTC epoch).
cd "$(dirname "$0")/../.."
export PGG_BASE_URL=http://127.0.0.1:11435/v1 PGG_TOKEN=local
DEADLINE=$(( $(date +%s) + 8*3600 ))  # stop starting new trials 8h after launch
for k in $(seq 0 11); do
  [ "$(date -u +%s)" -ge "$DEADLINE" ] && break
  python3 experiments/pgg_swap/pgg_swap.py --trials 1 --conditions 1,2,3,4,5,6,7 \
    --out outputs/pgg_swap/main_local/t$k --seed $((100+k)) --concurrency 6 \
    --models experiments/pgg_swap/models.local.json
done
echo done > outputs/pgg_swap/main_local/DONE
