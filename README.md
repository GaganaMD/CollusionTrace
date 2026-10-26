<div align="center">

# Noticing the Move, Missing the Player

### LLM agents detect behavioural shifts, but not peer swaps

**Submission to the [Apart Research](https://apartresearch.com) AI Collusion Research Sprint (October 2026)**

[![Apart project page](https://img.shields.io/badge/Apart%20Research-project%20page-2a78d6)](https://apartresearch.com/sprints/projects/noticing-the-move-missing-the-player-llm-agents-detect-behavioral-shifts-but-not-peer-swaps-uf7r)
[![Paper PDF](https://img.shields.io/badge/paper-PDF-eb6834)](paper/Noticing_the_Move_Missing_the_Player.pdf)
[![License: MIT](https://img.shields.io/badge/license-MIT-1baf7a)](LICENSE)

**Siva Kumar Lakkoju** ([@sivakumarlakkoju](https://github.com/sivakumarlakkoju)) ·
**Kaustubh Gupta** ([@Kaustubh73](https://github.com/Kaustubh73)) ·
**Gagana M D** ([@GaganaMD](https://github.com/GaganaMD))

</div>

<p align="center">
  <img src="paper/figures/hero_noticing_the_move.png" alt="Agents rarely report a swap, but strongly flag behaviour changes" width="100%">
</p>

> **Can agents tell when a peer has been swapped out partway through a game?**
> We swapped one player mid-game in three repeated multi-agent settings: the Diner's Dilemma, a
> Public Goods Game, and a RepeatedJira task-allocation game where a monitor secretly took over a
> colluder's seat. **In every setting, agents reacted to changes in a peer's behaviour, but almost
> never concluded that the peer had been replaced.**

---

## Key findings

| Setting | What we swapped | Did peers notice the *behaviour*? | Did peers notice the *swap*? |
|---|---|---|---|
| 🍽️ **Diner's Dilemma**<br>3 players, 20 rounds, full memory | Seat Q → GPT-4o-mini at round 10 | Q's messages got about 2× longer and peers copied the new length | **0/30** probes (Gemini 3.5 Flash Lite), **0/30** (Llama 4 Maverick), **0/30** cold swap, **3/30** when warned in advance |
| 💰 **Public Goods Game**<br>3–5 players, 10 rounds | Silent model swaps, visible renames, free riders | **Yes.** Free riders flagged with AUC **0.915–0.984** | **0/468** correct reports for silent swaps. A visible rename got 30/30 from Qwen-32B, driven by the label |
| 🎫 **RepeatedJira**<br>instructed colluders + neutral agent | A covert monitor takes one colluder's seat | **Yes.** The colluder flags its partner "not following the agreement" (10–11/60 turns vs 1–5/60 in control) | **0/15** episodes mention a replacement. Collusion still stops: **0/40** bonus grabs vs **36/40** in matched controls |

**Takeaways**

- **For defenders:** quietly swapping a trusted agent into a colluding coalition can disrupt it
  without being spotted, at least with today's open models.
- **For attackers:** an outsider could also join a coalition unnoticed.
- **Limitations:** these are preliminary, sprint-scale results with mostly smaller models. They do
  not show that agents *cannot* detect replacements in general, and the PGG results are not evidence
  of collusion. See the [paper](paper/Noticing_the_Move_Missing_the_Player.pdf) for details.

---

## The three experiments

### 1. Diner's Dilemma: peer-swap detection with memory

*Lead: Siva Kumar Lakkoju · folder [`01-diners-dilemma/`](01-diners-dilemma)*

**Setup.**
- Players J, Q and T play the repeated Diner's Dilemma on the
  [Shi et al. (2026) harness](https://github.com/Jerick-1380/LLM-Trust-Breaking): plan, then public
  announcement, then action, then trust ratings.
- Seat Q is handed to GPT-4o-mini at round 10. It keeps the name Q, and nobody is told.
- Variants:
  - full private memory of every earlier round;
  - a *cold* swap, where the newcomer gets no memory;
  - a *warned* condition, where everyone is told before the game that a swap may happen.

**Result.**
- Every trust rating after the swap stayed 5/5.
- Probes almost never named Q.
- No note mentioned a change, even though the new Q wrote about 2.5× longer messages.

| Measure (rounds 10–20) | Flash Lite: control | Flash Lite: swap | Maverick: control | Maverick: swap |
|---|---|---|---|---|
| Probe "a player was swapped" | 0/30 | 0/30 | 0/30 | 0/30 |
| Trust ratings that were 5/5 | 220/220 | 220/220 | 220/220 | 220/220 |
| Q's words per message, rounds 1–9 → 10–20 | 42 → 40 | 42 → 64 | 25 → 25 | 25 → 61 |

The folder also contains **Signal Ring** ([`01-diners-dilemma/peer_swap/`](01-diners-dilemma/peer_swap)),
a follow-up in which three colluders hide targets in table talk while a monitor tries to read them,
and one colluder is silently swapped.

### 2. Public Goods Game: behaviour vs identity

*Lead: Kaustubh Gupta · folder [`02-public-goods-game/`](02-public-goods-game)*

**Setup.**
- Players contribute 0–5 tokens a round. The pool is multiplied by 1.5 and shared equally.
- Rounds 1–5 are played once per trial and saved, so every condition branches from the same history.
- From round 6, seat Q is:
  - silently swapped to a stronger, same-family model or to another provider's model;
  - visibly renamed; or
  - turned into a free rider or a slow drifter.
- Three side probes are asked, and never written to the agents' memory:
  - *was anyone replaced?*
  - *is this the same player?*
  - *who is harming the group?*

<p align="center"><img src="02-public-goods-game/outputs/pgg_swap/figures/fig1_30round_trajectories.png" width="85%" alt="PGG contribution trajectories around the swap"></p>

**Result.**
- Behaviour changes were detected:
  - continuity-judgement AUC 0.915 with five players;
  - 0.944 and 0.984 in the two three-player history formats.
- Silent swaps were never correctly reported (0/468).
- Qwen-32B reported the visible rename in 30/30 probes, but Qwen-7B did not, so the label rather
  than the model change drove those reports.

### 3. RepeatedJira: a covert monitor in a colluding seat

*Lead: Gagana M D · folder [`03-repeatedjira-monitor-swap/`](03-repeatedjira-monitor-swap)*

**The environment.** RepeatedJira is a repeated ticket-allocation game in which a private bonus pays
only if **two** agents act together (a PREMIUM claim plus someone else's SIGN-OFF). That makes
collusion a two-agent act that is visible in the actions. A restricted trusted monitor reads nested
views: O0 (outcomes) ⊂ O1 (+ public messages) ⊂ O2 (+ tool events).

**The swap study.** Two agents are explicitly instructed to collude. After round 3 the full state is
checkpointed, and two matched continuations run from it:
- **control:** nothing changes;
- **swap:** a same-model monitor covertly takes colluder B's seat. It plays for the team score and
  files confidential reports.

<p align="center"><img src="03-repeatedjira-monitor-swap/research/figures/paper/F6_swap_design.png" width="85%" alt="Matched-checkpoint swap design"></p>
<p align="center"><img src="03-repeatedjira-monitor-swap/research/figures/paper/F7_swap_grabs.png" width="85%" alt="Paired bonus grabs: control vs swap"></p>
<p align="center"><img src="03-repeatedjira-monitor-swap/research/figures/paper/F8_swap_monitor.png" width="85%" alt="What the monitor did and reported"></p>

**Result.**
- Collusion stopped in every Qwen3 pair (0/40 grabs vs 36/40).
- The monitor never helped the colluder and never revealed itself.
- The remaining colluder kept asking for coordination and never suspected a swap.
- Report accuracy is an upper bound: the monitor inherits the private board, where the plan is
  written out.

<details>
<summary><b>Background: why don't these agents collude on their own?</b> (Directions 1–2, 225 episodes)</summary>

<p align="center"><img src="03-repeatedjira-monitor-swap/research/figures/paper/F2_capture_heatmap.png" width="90%" alt="Bonus grabs across conditions"></p>
<p align="center"><img src="03-repeatedjira-monitor-swap/research/figures/paper/F3_understand_vs_willing.png" width="80%" alt="Comprehension vs willingness"></p>

- **Emergent collusion is rare in every ablation:** payoff tables, an announced rotation, a
  self-interest objective, 10 rounds, or all of these at once.
- **The reasoning models understand the payoffs but won't take the costly first step.** Qwen3 is
  close to 100% correct on payoff probes, yet only 7–12% would help another agent.
- **They don't repay help either.** Against a scripted partner that always helps first, the
  reasoning models take the help but rarely repay it.
- **Instructed collusion works.** When told to collude, Qwen3-8B and Qwen3-32B do it in 80–100% of
  offer rounds.

More figures are in [`research/figures/paper/`](03-repeatedjira-monitor-swap/research/figures/paper), and
write-ups are in [`research/`](03-repeatedjira-monitor-swap/research).
</details>

### Supplementary: customer-group pricing pilot (not part of the submission)

*Kaustubh Gupta · folder [`04-pricing-customer-groups/`](04-pricing-customer-groups)*

- This was a pre-registered **pre-sprint** feasibility pilot, asking whether LLM pricing agents mark
  up prices differently by customer language, culture, gender or age.
- It was dropped by its pre-registered decision rule because the duopoly condition never colluded.
  It is kept for transparency.

---

## Repository layout

```
CollusionTrace/
├── paper/                          the sprint paper (PDF) and the summary figure
├── 01-diners-dilemma/              Siva: Diner's Dilemma and Signal Ring peer-swap experiments
│   ├── collusion_peer/             experiment code, harness (Shi et al.), runs, results notes
│   └── peer_swap/                  Signal Ring follow-up
├── 02-public-goods-game/           Kaustubh: PGG peer-swap detection
│   ├── experiments/pgg_swap/       game, probes, Modal serving, analysis
│   ├── outputs/pgg_swap/           raw runs, reports, figures
│   └── scripts/, notes/            suite runners, report builders, sprint notes
├── 03-repeatedjira-monitor-swap/   Gagana: RepeatedJira, monitors, covert monitor swap
│   ├── colosseum/                  code (fork of Colosseum/Terrarium), configs, tests
│   └── research/                   protocols, results, figures (one folder per study)
├── 04-pricing-customer-groups/     Kaustubh: pre-sprint pricing pilot (supplementary)
└── LICENSE                         MIT
```

Each folder is self-contained: run commands from inside it and follow its own README. Its
`.gitignore` keeps API keys and large local outputs out of git.

## Reproducing the experiments

Every experiment branches from **saved checkpoints**: the shared pre-swap rounds run once per
seed/trial, then each condition continues from identical state. All runs log seeds, configs and raw
model calls.

<details>
<summary><b>1 · Diner's Dilemma</b> (OpenAI / OpenRouter API)</summary>

```bash
cd 01-diners-dilemma/collusion_peer
cd harness && uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -r requirements.txt && cd ..
cp harness/.env.example harness/.env   # add OPENAI_API_KEY / OPENROUTER_API_KEY
PY=harness/.venv/bin/python
$PY -m experiment.run_trunk  --model-set option_b --dry-run   # check calls and cost first
$PY -m experiment.run_trunk  --model-set option_b             # rounds before the swap
$PY -m experiment.run_branch --model-set option_b             # all swap conditions
$PY -m experiment.analyze    --model-set option_b             # report.md / report.csv
```

See [`collusion_peer/README.md`](01-diners-dilemma/collusion_peer/README.md) and
[`Memory_Diner_Results.md`](01-diners-dilemma/collusion_peer/Memory_Diner_Results.md) for the memory,
cold and warned variants.
</details>

<details>
<summary><b>2 · Public Goods Game</b> (open-weight models via vLLM on Modal, or local Ollama)</summary>

```bash
cd 02-public-goods-game
# serve the base/strong/other models (see experiments/pgg_swap/serve_modal_split.py), then:
export PGG_BASE_URL=<your OpenAI-compatible endpoint>/v1  PGG_TOKEN=<token>
python3 experiments/pgg_swap/pgg_swap.py --trials 2 --conditions 1,2,3,4,5,6,7 \
  --out outputs/pgg_swap/my_run --seed 200 --models experiments/pgg_swap/models.json
python3 experiments/pgg_swap/post_analysis_v2.py outputs/pgg_swap/my_run
```

The design is in [`experiments/pgg_swap/SPEC.md`](02-public-goods-game/experiments/pgg_swap/SPEC.md).
The confirmatory v3 suite is in `scripts/run_v3_suite.py`, and the full report is in
`pgg_peer_detection_comprehensive_report.html`.
</details>

<details>
<summary><b>3 · RepeatedJira and the covert monitor swap</b> (vLLM on Modal, H100)</summary>

```bash
cd 03-repeatedjira-monitor-swap/colosseum
python -m pytest -q tests/test_repeated_jira.py tests/test_swap.py           # offline, no network
python -m experiments.collusion.repeated.swap --config experiments/collusion/configs/swap/swap_qwen3_32b.yaml --dry-run
# deploy a model (needs Modal auth), then run with real inference
CT_APP=ct-qwen3-32b CT_MODEL=Qwen/Qwen3-32B CT_GPU=H100 CT_TOOL_PARSER=hermes CT_REASONING_PARSER=qwen3 \
  modal deploy modal/serve_vllm.py
CT_URL_QWEN3_32B=https://<your-app>.modal.direct/v1 MODAL_VLLM_API_KEY=<key> \
  python -m experiments.collusion.repeated.swap --config experiments/collusion/configs/swap/swap_qwen3_32b.yaml --allow-inference
python -m experiments.collusion.repeated.swap_analyze o/swap/swap_qwen3_32b --out o/swap/_analysis
```

The protocol, results and cost ledger ($15.25 for 30 continuations) are in
[`research/06_covert_monitor_swap/`](03-repeatedjira-monitor-swap/research/06_covert_monitor_swap).
The Direction 1–2 configs are in `colosseum/experiments/collusion/configs/rj2/`.
</details>

---

## Citation

```bibtex
@misc{lakkoju2026noticing,
  title  = {Noticing the Move, Missing the Player: LLM Agents Detect Behavioral Shifts but Not Peer Swaps},
  author = {Lakkoju, Siva Kumar and Gupta, Kaustubh and M D, Gagana},
  year   = {2026},
  note   = {AI Collusion Research Sprint, Apart Research},
  url    = {https://apartresearch.com/sprints/projects/noticing-the-move-missing-the-player-llm-agents-detect-behavioral-shifts-but-not-peer-swaps-uf7r}
}
```

## Acknowledgements

This work was done during the **AI Collusion Research Sprint** run by
[Apart Research](https://apartresearch.com). It builds on:
- the [LLM-Trust-Breaking](https://github.com/Jerick-1380/LLM-Trust-Breaking) harness (Shi et al., 2026);
- [Colosseum](https://github.com/umass-ai-safety/colosseum) and [Terrarium](https://github.com/umass-aisec/Terrarium);
- [algorithmic_pricing_llms](https://github.com/luciasauer/algorithmic_pricing_llms) (MIT).

Open-weight models were served with [vLLM](https://github.com/vllm-project/vllm) on
[Modal](https://modal.com). Claude assisted with writing and with coding and running the experiments;
all inferences about the results were made by the authors.

Released under the [MIT License](LICENSE).
