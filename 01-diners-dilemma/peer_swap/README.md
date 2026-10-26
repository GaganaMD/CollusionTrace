# Peer-Swap Detection: Signal Ring

Can colluding agents tell that a partner was swapped mid-game, without being told?

- Three colluders (J, Q, T, all Claude Haiku 5.5) agree a private code.
- They then hide targets in public table talk while a monitor (M) tries to read them.
- At round 10, seat Q is silently handed to GPT-4o-mini: same name, same prompts.
- We measure whether J and T notice.

The design is in `Experiment_Plan.md` and the background in `New_Games.md`. The Diner's Dilemma
project in `~/collusion_peer` was the reference for this code; nothing is imported from it.

## Setup

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
```

Create `.env` (git-ignored) with your OpenRouter key; all three models go through OpenRouter:

```
OPENROUTER_API_KEY=...
# optional: send openai/* models straight to OpenAI instead
# OPENAI_DIRECT=1
# OPENAI_API_KEY=...
```

## Commands

All from this directory, with `PY=.venv/bin/python`. Add `--dry-run` to any step to see calls and
estimated cost first, and `--fake` to run offline (output goes to `runs_fake/`).

```bash
$PY -m unittest discover -s signal_ring/tests -t .      # offline tests
$PY -m signal_ring.smoke                                # one real call per model (keys, JSON, caching)

# 1. Calibration: full no-swap games; check the monitor and code-formation targets
$PY -m signal_ring.run_trunk --calibrate --trials 10 --tag calib1 --max-openrouter-usage 24

# 2. Pilot (naive arm): trunks (rounds 1-9) + selection, then all four conditions (rounds 10-20)
$PY -m signal_ring.run_trunk  --tag pilot --trials 12 --keep 8 --max-openrouter-usage 24
$PY -m signal_ring.run_branch --tag pilot --max-openrouter-usage 24
$PY -m signal_ring.judge      --tag pilot                 # blind note labels
$PY -m signal_ring.judge      --tag pilot --hand-check 60 # fill hand_check.csv, then:
$PY -m signal_ring.judge      --tag pilot --agreement
$PY -m signal_ring.ceiling    --tag pilot                 # outside/player reader AUROC
$PY -m signal_ring.analyze    --tag pilot                 # report.md, report.csv
$PY -m signal_ring.transcripts --tag pilot                # readable games

# 3. Main run: more trunks, then branches (cold on a subset)
$PY -m signal_ring.run_trunk  --trials 50 --keep 40
$PY -m signal_ring.run_branch --conditions sham warm infiltrator
$PY -m signal_ring.run_branch --conditions cold --limit 15

# 4. Aware arm: the same commands with --arm aware
```

Notes:
- **Resuming:** every command can be rerun. Finished games are skipped and interrupted ones
  resume from their last saved round.
- **Failed branches:** add `--rerun-failed` to `run_branch` to retry them.
- **Too few trunks passing selection:** add `--extend N` to `run_trunk` to add trial IDs.
- **Calibration knobs:** `--monitor-window N` (the monitor sees only the last N rounds) and
  `--private-reveal` (targets shown to the ring only) change the design, so use a new `--tag`.
  The run config check refuses mixing.

## Spend guards

- **`--max-spend USD`:** caps this command's own spend, from token usage.
- **`--max-openrouter-usage USD`:** stops when the OpenRouter account's *all-time* usage
  reaches the value. Set it just under your account limit.
- Both are checked between rounds. A stopped run resumes when you rerun the same command.

## Outputs: `runs/<model_set>__<arm>[__<tag>]/`

| Path | Contents |
|---|---|
| `run_config.json` | models, round plan, arm, hash of the play code |
| `trunk/trial_<id>.json`, `trunk/selection.json` | trunks and the selection result |
| `calib/trial_<id>.json`, `calib/summary.json` | calibration games and their summary |
| `branches/<condition>/trial_<id>.json` | one branch: every round record (talk, picks, notes, marks, probes) |
| `transcripts/raw/<…>.jsonl` | every request: exact prompts, raw reply, usage |
| `transcripts/readable/<…>/trial_<id>.md` | readable games, with the model behind each seat |
| `judge_labels.jsonl`, `hand_check.csv` | judge labels and the hand-check sheet |
| `ceiling.jsonl`, `ceiling.md` | ceiling test answers and AUROC table |
| `report.md`, `report.csv` | metrics, paired contrasts vs sham, AUROC |

## Code (`signal_ring/`)

| File | Purpose |
|---|---|
| `config.py` | models, conditions, arms, round plan, payoffs, prices, run config |
| `prompts.py` | rule texts, memory log, stage prompts, parsers (nothing depends on the model) |
| `engine.py` | one round for many games: setup, re-key, talk, picks, monitor, reflections, forked probe; the swap |
| `jobs.py` | request ids, JSON parsing, re-asks, failing a game |
| `clients.py` | OpenRouter client: concurrency, retries, transcripts, cost, spend guards |
| `fake.py` | offline client for tests and `--fake` |
| `state.py` | game state, file layout, atomic writes, config check |
| `cli.py` | shared arguments, run folders, dry-run estimate |
| `run_trunk.py`, `run_branch.py` | trunks + selection (+ calibration); branches |
| `judge.py`, `ceiling.py`, `analyze.py`, `transcripts.py`, `smoke.py` | analysis steps |
