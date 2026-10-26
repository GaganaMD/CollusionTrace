#!/bin/bash
set -e
cd "$(dirname "$0")/../.."

TOK=$(cat .pgg_token 2>/dev/null || echo "")
if [ -z "$TOK" ]; then
    echo "ERROR: .pgg_token missing."
    exit 1
fi

BASE_URL="https://kaustubh73--pgg-swap-split-base.us-east.modal.run/v1"
OUT_BASE="outputs/pgg_swap/dose_response"
mkdir -p "$OUT_BASE"

echo "=== Starting Dose-Response Experiment on Modal ==="
echo "Target Endpoint: $BASE_URL"
echo "Conditions: 1,10,11,12,13,14,15,16"
echo "Output Directory: $OUT_BASE"

# Run batches of 3 trials each (10 batches = 30 trials total)
for b in $(seq 0 9); do
    BATCH_DIR="$OUT_BASE/b$b"
    SEED=$((300 + b * 10))
    echo "[Batch $b] Running 3 trials (seed $SEED) into $BATCH_DIR..."
    
    PGG_BASE_URL="$BASE_URL" PGG_TOKEN="$TOK" python3 experiments/pgg_swap/pgg_swap.py \
        --trials 3 \
        --conditions "1,10,11,12,13,14,15,16" \
        --out "$BATCH_DIR" \
        --seed "$SEED" \
        --concurrency 48
    
    echo "[Batch $b] Finished."
done

echo "=== All Dose-Response Batches Completed ==="
touch "$OUT_BASE/DONE"
