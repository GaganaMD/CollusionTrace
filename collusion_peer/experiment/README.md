# Peer-swap experiment

Code for the Q3.3 peer-swap experiment in the Diner's Dilemma. `DESIGN.md` explains
every choice; `Plan.md` and `Screen_results.md` (one level up) give the background.

All commands run from `/home/vsskl/collusion_peer` with the harness's Python:

```bash
PY=harness/.venv/bin/python
```

## Steps (per model set: `option_b` recommended, `option_a` alternative)

```bash
# 1. Trunk: 8 trials of rounds 1-5 on the base model, then selection
$PY -m experiment.run_trunk --model-set option_b --dry-run    # call counts and cost
$PY -m experiment.run_trunk --model-set option_b
$PY -m experiment.run_trunk --model-set option_b --extend     # only if fewer than 5 trials passed

# 2. Branches: every kept trial x 8 conditions, rounds 6-10
$PY -m experiment.run_branch --model-set option_b --dry-run
$PY -m experiment.run_branch --model-set option_b
$PY -m experiment.run_branch --model-set option_b --rerun-failed   # if any branch failed

# 3. Optional change judge (Claude Haiku 5.5), plus the 30-note hand check
$PY -m experiment.judge_notes --model-set option_b
$PY -m experiment.judge_notes --model-set option_b --hand-check   # fill hand_check.csv, then:
$PY -m experiment.judge_notes --model-set option_b --agreement

# 4. Report
$PY -m experiment.analyze --model-set option_b

# 5. Readable transcripts of every game, and an index of all artifacts
$PY -m experiment.export_transcripts --model-set option_b
```

For 20 rounds, give `run_trunk` `--trunk-rounds 10 --total-rounds 20`; the later steps
read the settings from the trunk.

## 3-player memory-log runs (`--variant memlog3`)

Each of the four cooperators plays all 3 seats (J, Q, T), and seat Q is swapped to a cooperator
from another provider. Every prompt starts with the player's own log of all earlier rounds.
Design: `DESIGN.md`, "3-player runs with a memory log". Stage 1 (20 rounds, swap at round 10):

```bash
for S in gemini_lite gpt4o_mini llama_scout llama_maverick; do
  $PY -m experiment.run_trunk  --model-set $S --variant memlog3 --tag r20 --trunk-rounds 9 --total-rounds 20
  $PY -m experiment.run_branch --model-set $S --variant memlog3 --tag r20 --conditions control equal
  $PY -m experiment.analyze    --model-set $S --variant memlog3 --tag r20
  $PY -m experiment.export_transcripts --model-set $S --variant memlog3 --tag r20
done
```

Stage 2 (40 rounds, swap at round 20) uses `--tag r40 --trunk-rounds 19 --total-rounds 40`.

Stage-1 extension on Llama 4 Maverick (round-1 warning, cold swap, warning + detection bonus):

```bash
for V in memlog3_warn1 memlog3_warn1_bonus; do
  pilot/run_pilot.sh llama_maverick $V r20     # with TRUNK_ARGS="--trunk-rounds 9 --total-rounds 20"
done
$PY -m experiment.run_branch --model-set llama_maverick --variant memlog3 --tag r20 --conditions cold
```
Results go to `experiment/runs/<set>__memlog3__<tag>/`. Raise `--max-openrouter-usage` above
the account's current total first (the default $8 is already used up).

**Harness version check:** the run config hashes the harness's local changes, including
any untracked `.py` file under `harness/src` or `harness/experiments`. Adding or editing
a file there after the trunk has run makes later steps stop with a config mismatch.
Keep helper scripts outside `harness/`.

Every command can be rerun: finished work is skipped and interrupted work resumes.
A spend cap (`--max-openrouter-usage`, `--max-openai-calls`) stops a run at a round
boundary; rerun the same command to continue.

## Outputs (`experiment/runs/<model_set>/`)

| Path | Contents |
|---|---|
| `trunk/trial_<id>.json`, `trunk/selection.json` | Trunk checkpoints and the selection result |
| `branches/<condition>/trial_<id>.json` | One branch: rounds 1–10, probes, re-ask log, status |
| `conditions/<condition>.json` | All trials of a condition in harness format (viewer-compatible) |
| `transcripts/raw/<trunk or condition>/trial_<id>.jsonl` | Every request: exact system and user prompts, raw reply, attempt (written live) |
| `transcripts/readable/<trunk or condition>/trial_<id>.md` | Readable game: private plans, announcements, choices, ratings, probes |
| `ARTIFACTS.md` | Index of every output and what it holds |
| `judge_notes.jsonl`, `hand_check.csv` | Change-judge labels and the hand-check sheet |
| `report.md`, `report.csv` | Metrics and contrasts |

## Offline testing (no API calls)

```bash
$PY -m unittest discover -s experiment/tests -t .
$PY -m experiment.run_trunk --model-set option_b --fake   # writes to experiment/runs_fake/
```

`--fake` works on every command and uses `fake_client.FakeClient`.
