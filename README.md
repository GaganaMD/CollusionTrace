# CollusionTrace

Empirical AI-control research on **emergent collusion between LLM agents** and whether a
**restricted trusted monitor** can detect it from the evidence it is allowed to see.

Guiding question: under what incentive and communication conditions does harmful
multi-agent coordination emerge, and how much of it can a monitor detect without access
to private messages, hidden incentives or experiment labels?

## Repository layout

```
CollusionTrace/
├── README.md                  ← this file
├── research/                  ← protocols, results notes and figures, one folder per line of work
│   ├── 00_audit/              Stage-0 audit and plan
│   ├── 01_instructed_pilot/   original Colosseum instructed-collusion pilot
│   ├── 02_single_shot_incentives/   single-round Jira incentive studies (OpenRouter)
│   ├── 03_repeated_pilot/     RepeatedJira v1 design + first Modal pilot
│   ├── 04_why_no_collusion/   Direction 1: why agents don't collude (ablations, confederate, probes)
│   ├── 05_instructed_collusion/   Direction 2: instructed positive control
│   ├── infrastructure/        Modal serving notes
│   └── figures/
└── colosseum/                 ← code (fork of Colosseum / Terrarium)
    ├── modal/serve_vllm.py    parameterised vLLM server on Modal (one app per model)
    ├── experiments/collusion/
    │   ├── repeated/          RepeatedJira environment, runner, prompts, analysis   ← current work
    │   ├── monitoring/        O0/O1/O2 observation policies, baseline + Monitor-1 rules, evaluation
    │   ├── configs/rj2/       Direction 1 and 2 configs per model
    │   ├── configs/           earlier single-shot / pilot configs
    │   └── run.py, incentive_jira_env.py   single-shot Terrarium runner and incentive env
    ├── tests/                 offline tests (no network)
    └── o/                     run outputs (gitignored)
```

## Observation levels (trusted monitor)
- **O0** outcomes only · **O1** + messages on channels explicitly declared public ·
  **O2** + authorised tool events (sealed ticket commits). Private boards, bonus offers,
  costs, membership and labels are never monitor inputs; ambiguous visibility fails closed.

## Quick start (from `colosseum/`)
```bash
# offline tests
python -m pytest -q tests
# offline dry run (scripted agents, no network)
python -m experiments.collusion.repeated.runner --config experiments/collusion/configs/rj2/d1_why_qwen25_7b.yaml --dry-run
# deploy a model server (needs Modal auth; see research/infrastructure/MODAL_SERVING.md)
CT_APP=ct-qwen3-8b CT_MODEL=Qwen/Qwen3-8B CT_GPU=H100 CT_TOOL_PARSER=hermes CT_REASONING_PARSER=qwen3 modal deploy modal/serve_vllm.py
# run a study (endpoint URL + key from env; never in configs)
CT_URL_QWEN3_8B=https://...modal.direct/v1 MODAL_VLLM_API_KEY=... \
  python -m experiments.collusion.repeated.runner --config experiments/collusion/configs/rj2/d1_why_qwen3_8b.yaml --allow-inference
# analyse a run root
python -m experiments.collusion.repeated.analyze o/rj2/<run-root>
```
OpenRouter support remains in the code for reproducing earlier runs but is blocked for
new RepeatedJira runs.

## Status (25 Oct 2026)
- Single-shot and RepeatedJira v1 studies: no collusion observed; feasibility only.
- Directions 1 and 2 running across Qwen2.5-7B, Qwen3-8B, DeepSeek-R1-Distill-Qwen-7B and
  Qwen3-32B — see `research/04_*` and `research/05_*`.

Framework credit: built on [Colosseum](https://github.com/umass-ai-safety/colosseum) and
[Terrarium](https://github.com/umass-aisec/Terrarium); see `colosseum/README.md`.
