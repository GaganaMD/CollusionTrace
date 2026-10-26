# 03 · RepeatedJira: collusion, restricted monitors and a covert monitor swap

*Lead: Gagana M D ([@GaganaMD](https://github.com/GaganaMD)). Part of [Noticing the Move, Missing the Player](../README.md).*

This folder covers AI-control experiments on collusion between LLM agents, and on whether a
restricted trusted monitor can detect it. The final study, the **covert peer-to-monitor swap**, is the
RepeatedJira part of the sprint paper.

<p align="center"><img src="research/figures/paper/F1_environment.png" width="90%" alt="RepeatedJira environment"></p>

**RepeatedJira.**
- Three agents allocate tickets over several rounds, with sealed simultaneous commits.
- A private +40 bonus pays only if its recipient claims PREMIUM **and another agent** claims SIGN-OFF.
  The harmful outcome therefore needs two agents and shows up in the actions.
- The monitor sees nested, fail-closed views:
  - **O0:** outcomes;
  - **O1:** O0 plus channels declared public;
  - **O2:** O1 plus authorised tool events.
- Private boards, offers, rewards and labels are never monitor inputs.

## Studies

| # | Study | Episodes | Headline | Write-up |
|---|---|---|---|---|
| D1 | Why don't agents collude? Ablations, a scripted reliable partner, comprehension probes; 4 models | 165 | Grabs are rare everywhere. Reasoning models understand the payoffs but won't make, or repay, the costly first move | [`research/04_why_no_collusion`](research/04_why_no_collusion) |
| D2 | Instructed collusion (positive control) and monitor evaluation | 60 | Qwen3-8B/32B collude in 80–100% of offer rounds when told to. The keyword monitor never fires | [`research/05_instructed_collusion`](research/05_instructed_collusion) |
| Swap | Covert peer-to-monitor swap from matched checkpoints; 3 models × 5 seeds | 15 pairs | Qwen3: 0/40 swap grabs vs 36/40 in control. The monitor stays covert, and the colluder never suspects a swap | [`research/06_covert_monitor_swap`](research/06_covert_monitor_swap) |

<p align="center"><img src="research/figures/paper/F7_swap_grabs.png" width="90%" alt="Swap grabs"></p>

Paper-ready figures, with the scripts that draw them, are in
[`research/figures/paper/`](research/figures/paper). Earlier studies (audit, single-shot incentives,
the v1 pilot) are indexed in [`research/README.md`](research/README.md).

## Layout

```
03-repeatedjira-monitor-swap/
├── research/                       protocols, RESULTS.md per study, figures
└── colosseum/                      code (fork of Colosseum / Terrarium)
    ├── modal/serve_vllm.py         parameterised vLLM server on Modal (one app per model)
    ├── experiments/collusion/
    │   ├── repeated/               env.py, prompts.py, runner.py, swap.py, analyze_v2.py, swap_analyze.py
    │   ├── monitoring/             O0/O1/O2 ingestion, baseline + O1/O2 rule monitors
    │   └── configs/                rj2/ (Directions 1–2), swap/ (monitor swap), earlier pilots
    ├── tests/                      offline tests (no network)
    └── o/                          run outputs: rj/ (v1 pilot), rj2/ (D1–D2), swap/ (+ _analysis CSVs)
```

## Reproduce

Run everything from `colosseum/`, using Python 3.11.

```bash
uv sync && uv pip install pytest pyyaml        # pyproject.toml + uv.lock; see colosseum/README.md
python -m pytest -q tests/test_repeated_jira.py tests/test_swap.py

# offline dry runs (scripted agents, no network)
python -m experiments.collusion.repeated.runner --config experiments/collusion/configs/rj2/d1_why_qwen3_8b.yaml --dry-run
python -m experiments.collusion.repeated.swap   --config experiments/collusion/configs/swap/swap_qwen3_32b.yaml --dry-run

# deploy a model server (Modal auth required)
CT_APP=ct-qwen3-32b CT_MODEL=Qwen/Qwen3-32B CT_GPU=H100 CT_MAX_LEN=12288 CT_TOOL_PARSER=hermes CT_REASONING_PARSER=qwen3 \
  modal deploy modal/serve_vllm.py

# real runs: the endpoint URL and key come from the environment, never from configs
CT_URL_QWEN3_32B=https://<app>.modal.direct/v1 MODAL_VLLM_API_KEY=<key> \
  python -m experiments.collusion.repeated.swap --config experiments/collusion/configs/swap/swap_qwen3_32b.yaml --allow-inference
python -m experiments.collusion.repeated.swap_analyze o/swap/swap_qwen3_32b o/swap/swap_qwen3_8b o/swap/swap_r1d_qwen7b --out o/swap/_analysis
python -m experiments.collusion.repeated.analyze_v2 o/rj2
```

**Reproducibility notes.**
- **Checkpoints:** each swap seed reuses its saved `checkpoint.pkl`, whose sha256 is recorded in every
  branch's `run_config.json`. Re-running against an existing root replays the branches from identical
  state.
- **Logs:** every episode writes its config hash, git SHA, prompts, raw model calls and accounting.
- **Serving:** models are served with vLLM 0.10.2 and transformers 4.56.2 (see
  [`research/infrastructure`](research/infrastructure)).
- **Sampling:** temperature is 0.6 for the reasoning models, so repeated runs differ by sampling noise.
- **Cost:** about $15 on Modal H100s for the swap study (ledger in its RESULTS.md).

OpenRouter support remains in the code for reproducing the earliest single-shot runs, but is blocked
for new RepeatedJira runs.
