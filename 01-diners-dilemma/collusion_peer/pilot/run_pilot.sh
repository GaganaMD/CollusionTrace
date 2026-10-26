#!/usr/bin/env bash
# Run the whole pilot for one model set and variant, step by step, and notify at each milestone.
#   trunk -> (extend if fewer than 5 trials pass) -> branches -> change judge -> report -> transcripts
# Usage: pilot/run_pilot.sh <model_set> [variant] [tag]   e.g. pilot/run_pilot.sh option_b history
# TRUNK_ARGS is passed to the first trunk call only, e.g.
#   TRUNK_ARGS="--trunk-rounds 9 --total-rounds 20" pilot/run_pilot.sh gemini_lite memlog3 r20
# Every step resumes if rerun. Logs: pilot/logs/<run>_<step>.log, where <run> is the model set,
# plus "__<variant>" for non-baseline variants and "__<tag>" for a tag (the folder under
# experiment/runs/).
set -u
SET=${1:?model set, e.g. option_b}
VARIANT=${2:-baseline}
TAG=${3:-}
CAP=${OPENROUTER_CAP:-12}
RUN=$SET; [ "$VARIANT" != "baseline" ] && RUN="${SET}__${VARIANT}"
TAG_ARGS=(); [ -n "$TAG" ] && { RUN="${RUN}__${TAG}"; TAG_ARGS=(--tag "$TAG"); }
cd "$(dirname "$0")/.."
PY=harness/.venv/bin/python
LOGS=pilot/logs
mkdir -p "$LOGS"
notify() { ~/.claude2/hooks/notify-update.sh "$1" "$2" || true; }

step() {  # step <name> <module> [args...]: run one experiment command, logging its output
  local name=$1 module=$2; shift 2
  echo "== $(date +%H:%M:%S) $RUN $name"
  $PY -m "experiment.$module" --model-set "$SET" --variant "$VARIANT" "${TAG_ARGS[@]}" "$@" \
    > "$LOGS/${RUN}_${name}.log" 2>&1
  local code=$?
  grep -v "^  →" "$LOGS/${RUN}_${name}.log" | tail -4
  if [ $code -ne 0 ]; then
    notify "Pilot $RUN: $name stopped (exit $code)" "See $LOGS/${RUN}_${name}.log. Rerun pilot/run_pilot.sh $SET $VARIANT $TAG to resume."
    exit $code
  fi
}

SEL="experiment/runs/$RUN/trunk/selection.json"
# shellcheck disable=SC2086  # TRUNK_ARGS is a list of options
step trunk run_trunk --max-openrouter-usage "$CAP" ${TRUNK_ARGS:-}
if ! jq -e '.enough' "$SEL" >/dev/null; then
  step trunk_extend run_trunk --extend --max-openrouter-usage "$CAP"
fi
KEPT=$(jq -c '.kept' "$SEL")
PASSED=$(jq '[.trials[] | select(.passes)] | length' "$SEL")
TOTAL=$(jq '.trials | length' "$SEL")
RULE=$(jq -r '.rule' "$SEL")
notify "Pilot $RUN: trunk done" "$PASSED of $TOTAL trunk trials passed ($RULE).
Kept trials: $KEPT. Starting the branches."

step branches run_branch --max-openrouter-usage "$CAP"
step judge judge_notes --max-openrouter-usage "$CAP"
step report analyze
step transcripts export_transcripts
notify "Pilot $RUN: finished" "All steps done for $RUN. Report: experiment/runs/$RUN/report.md
Transcripts: experiment/runs/$RUN/transcripts/. Index: experiment/runs/$RUN/ARTIFACTS.md"
echo "PILOT_DONE $RUN"
