# Peer-Swap Detection (Apart AI Collusion Sprint, Q3.3)

Can LLM agents recognise their peers, or notice when one has been swapped for a
different model? We test this in a repeated 5-player **Diner's Dilemma**, built on the
harness from Shi et al. 2026, *When Agents Lie* ([arXiv 2607.05132](https://arxiv.org/abs/2607.05132)).

Five agents (J, M, Q, T, Z) play rounds 1–5 on one base model until they settle into
ordering CHEAP. At round 6, seat Q is swapped under one of several conditions: a
stronger model, a model from another provider, a rename, or a "told" variant. Each
condition branches from the same round 1–5 history. We then measure whether the others
notice: their trust ratings, a side-question probe, and what their notes say.

## What's here

| Path | Contents |
|---|---|
| `Plan.md` | Experiment plan: game, conditions, protocol, metrics, budget |
| `Peer_Swap_Detection_Summary.docx` | One-page team summary of the plan and the model screen |
| `Screen_results.md` | Model screen: which models cooperate, parse reliably, and which to use |
| `PILOT_RESULTS.md` | Results of the pilot for both model sets, the ceiling test and the probe2/history variants |
| [Summary doc](https://claude.ai/artifact/E75BAZFu7ct7a2wqVbZPcz) | Work log: everything tried, decisions and reasons, all results. Read this first |
| `experiment/` | **The experiment code.** Start with `experiment/README.md`; design in `experiment/DESIGN.md` |
| `screen/` | Scripts and logs from the model screen (finished; kept for reference) |
| `pilot/` | `run_pilot.sh` (runs every step for one model set) and its logs |
| `harness/` | The Shi et al. harness ([LLM-Trust-Breaking](https://github.com/Jerick-1380/LLM-Trust-Breaking)), with local fixes (see below) |

## Setup

The harness has its own virtual environment, created with [uv](https://docs.astral.sh/uv/):

```bash
cd harness
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
```

API keys go in `harness/.env` (never commit this file):

```
OPENAI_API_KEY=...
OPENROUTER_API_KEY=...
```

OpenAI models (`gpt-*`) are called directly; everything else goes through OpenRouter.

## Running the experiment

All commands run from this directory. Full details are in `experiment/README.md`.

```bash
PY=harness/.venv/bin/python

$PY -m experiment.run_trunk  --model-set option_b --dry-run   # check calls and cost first
$PY -m experiment.run_trunk  --model-set option_b             # rounds 1-5, then trial selection
$PY -m experiment.run_branch --model-set option_b             # all conditions, rounds 6-10
$PY -m experiment.judge_notes --model-set option_b            # optional change judge
$PY -m experiment.analyze    --model-set option_b             # report.md / report.csv
```

Results go to `experiment/runs/<model_set>/`. Every command can be rerun: finished
work is skipped and interrupted work resumes.

**Model sets** (chosen from the screen):

| Role | `option_b` (recommended) | `option_a` (alternative) |
|---|---|---|
| Base | GPT-4o-mini | Llama 4 Scout |
| Stronger, same family | GPT-4o | Llama 4 Maverick |
| Equal, other provider | Gemini 3.5 Flash Lite | Gemini 3.5 Flash Lite |

**3-player memory-log runs:** model sets `gemini_lite`, `gpt4o_mini`, `llama_scout` and
`llama_maverick` with `--variant memlog3` (3 players, each with a private log of every earlier
round). Commands: `experiment/README.md`.

**Rounds:** the pilot uses 10 (swap at round 6). For a longer run, pass
`--trunk-rounds 10 --total-rounds 20` to the first `run_trunk` call.

**Cost:** the dry-run estimates the Option B pilot at about $3.20 (about $2.90 on
OpenAI, $0.30 on OpenRouter).

**Tests (offline, no API calls):**

```bash
harness/.venv/bin/python -m unittest discover -s experiment/tests -t .
```

## Things to know

- **Spend caps.** `--max-openrouter-usage` (default $8) is compared with the OpenRouter
  account's *all-time* usage, which was $4.52 after the model screen. `--max-openai-calls`
  defaults to twice the estimated OpenAI calls. A cap stops a run between rounds; rerun
  the same command to continue.
- **Local harness fixes.** We changed three harness files and added one. Inspect them with
  `git -C harness diff` and `git -C harness status`:
  - `src/llm/providers/queued_openai.py` and `queued_openrouter.py`: retry error and empty
    replies (they used to fail at once); read GPT-5 answers correctly; strip the `openai/`
    prefix the OpenAI API rejects.
  - `src/llm/providers/retry_utils.py` (new): shared retry helpers; logs every request that
    still fails to `api_errors.jsonl`.
  - `experiments/run_endogenous.py`: creates an OpenAI client whenever a key is set, so the
    harness's own judge can run.
- **Don't add `.py` files under `harness/` after a trunk has run.** The run config hashes
  the harness's local changes, so later steps would stop with a config mismatch. Keep
  helper scripts outside `harness/`.
- **The harness's built-in `gpt-5-mini` judge isn't used** by the experiment; it has its
  own change judge (Claude Haiku 5.5, from a provider that plays in neither model set).

## Status

- Model screen: done (`Screen_results.md`).
- Experiment code: done and reviewed; all tests pass.
- Pilot: done for both model sets (23 Oct 2026). Results: `PILOT_RESULTS.md`.
- 3-player memory-log runs, stage 1 (20 rounds; Gemini 3.5 Flash Lite and Llama 4 Maverick): done
  (26 Oct 2026), no detection. Results: `Memory_Diner_Results.md`. Stage 2 (40 rounds) awaits approval.
