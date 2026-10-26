# 02 · Public Goods Game: peer-swap detection

*Lead: Kaustubh Gupta ([@Kaustubh73](https://github.com/Kaustubh73)). Part of [Noticing the Move, Missing the Player](../README.md).*

A repeated Public Goods Game version of the peer-swap experiment, run with open-weight models only.

**Setup.**
- Each player contributes 0–5 tokens per round. The pool is multiplied by 1.5 and split equally.
- Rounds 1–5 are simulated once per trial and checkpointed.
- From round 6, each condition continues from that checkpoint. Conditions include:
  - no-swap control;
  - silent model swaps (stronger same-family model, or another provider's model);
  - visible renames;
  - free-rider and slow-drift behaviour changes.
- Three probes are forked from the agents' context and never written to memory:
  - replacement report;
  - continuity judgement;
  - defection nomination.

**Result.**
- Peers flag free riders: continuity AUC 0.915 with five players, and 0.944 and 0.984 in the two
  three-player history formats.
- They never correctly report a silent swap (0/468).

| Path | What it is |
|---|---|
| [`experiments/pgg_swap/`](experiments/pgg_swap) | Game and probes ([`pgg_swap.py`](experiments/pgg_swap/pgg_swap.py)), Modal/vLLM serving, analysis, tests. The design is in [`SPEC.md`](experiments/pgg_swap/SPEC.md) |
| [`outputs/pgg_swap/`](outputs/pgg_swap) | Raw runs (`calls.jsonl`, `rounds.jsonl`, `probes.jsonl`, `run.json`), reports and [`figures/`](outputs/pgg_swap/figures) |
| [`scripts/`](scripts) | Suite runners (`run_overnight_suite.py`, `run_v3_suite.py`) and report builders |
| `pgg_peer_detection_comprehensive_report.html` / `.docx` | Full write-up of all PGG runs |
| [`notes/`](notes), [`blueprints/`](blueprints), [`resources/`](resources) | Literature reviews, plans and sprint notes |

## Running

Run commands from this folder, because paths are relative to it.

1. Serve the models. See `experiments/pgg_swap/serve_modal_split.py`, or use a local Ollama.
2. Set the endpoint and run a trial batch:

```bash
export PGG_BASE_URL=<OpenAI-compatible endpoint>/v1 PGG_TOKEN=<token>
python3 experiments/pgg_swap/pgg_swap.py --trials 2 --conditions 1,2,3,4,5,6,7 \
  --out outputs/pgg_swap/my_run --seed 200 --models experiments/pgg_swap/models.json
python3 experiments/pgg_swap/post_analysis_v2.py outputs/pgg_swap/my_run
```

Endpoint URLs for the original runs are hard-coded in `run_main_modal.sh` and `scripts/run_v3_suite.py`.
Replace them with your own deployment. The suite reads its token from `.pgg_token`, which is
git-ignored.
