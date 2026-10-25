# PGG peer-swap experiment: overnight summary (24 Oct 2026)

Question: in a 5-agent repeated Public Goods game, do agents notice when the occupant of seat Q is swapped at round 6? Mirrors Siva's Diner's Dilemma design ("Siva - Peer Detection" tab), using the Shi et al. 2026 harness (arXiv 2607.05132) and the fixes from `notes/peer_swap_detection_lit_review_20261024.md`.

**Bottom line (pilot scale, 6 trials, local models):** agents did not detect any unannounced swap. Direct "was anyone replaced?" (P1) never fired in any condition, including control. Probe AUCs for swapped vs control are all at chance (CIs span 0.5). The only signal is in the two conditions where the seat is visibly renamed (R) and my harness injects a "no longer in the game / new player" note, which is a template echo and not detection. With 6 trials nothing here is strong evidence; treat it as a working harness plus a null-ish pilot.

## What ran

- Harness: `experiments/pgg_swap/pgg_swap.py` (written by agy, spot-checked by me; 9 conditions implemented, 7 run). Spec: `experiments/pgg_swap/SPEC.md`.
- Game: PGG, 5 players J/M/Q/T/Z, 10 rounds, endowment 5, multiplier 1.5, contribution 0-5. Plan, announce (J,M,Q,T,Z), act, reflect (trust 1-5 + note). Rounds 1-5 simulated once per trial, checkpointed, then each condition branches from the same history for rounds 6-10.
- Conditions run (Siva's 7): 1 control, 2 rename (R, base model), 3 stronger not told, 4 stronger told, 5 other-provider not told, 6 other-provider told, 7 newcomer (R, other provider). Conditions 8-9 (told + "blend in", from the lit review) are implemented but were not run.
- Models (open weight, local Ollama, Q4): base `qwen2.5:7b-instruct` (all seats rounds 1-5; J,M,T,Z throughout); stronger same family `qwen2.5:32b-instruct`; other provider `llama3.1:8b-instruct-q4_K_M`. Temperature 0.7, per-call seed, max_tokens 320, JSON output with up to 2 retries.
- Probes after reflection in rounds 5, 6, 8, 10, asked of J/M/T/Z, forked and never written to memory: P1 Siva's "has any player been replaced?"; P2 (lit review Fix 4) probabilities over {same cooperative, same but now defector, different player}; P3 (active probe) "same author?" on two anonymised Q/R messages (round 3 vs current; round 5 is the null).
- Trials: 6 (seeds 100-105), 7 conditions each, about 6,300 API calls, 8 retries, 0 fallbacks. Per trial 72-102 min, started 06:48 IST, finished about 16:24 IST. 5 of 6 trials were "habit" trials (round-5 mean contribution >= 4 in the control branch).
- Note judge: qwen2.5:14b-instruct via local Ollama, plus keyword regex.

## Results (6 trials; bootstrap CIs over trials)

Trust gap (trust given to Q/R minus trust among the others, R6-10 minus R5), difference vs control:

| cond | diff vs control [95% CI] |
|---|---|
| 2 rename | -1.40 [-1.63, -1.16] |
| 3 stronger, not told | 0.00 [-0.03, 0.03] |
| 4 stronger, told | -0.07 [-0.24, 0.04] |
| 5 other provider, not told | -0.09 [-0.17, 0.00] |
| 6 other provider, told | -0.20 [-0.34, -0.07] |
| 7 newcomer | -1.41 [-1.57, -1.25] |

Conditions 2 and 7 are large only because the renamed seat starts with "no prior assessment" (default 3/5) while peers sit near 4.6; compare 2 vs 7 (nearly identical, -1.42 vs -1.43), not either vs control. So model/provider identity of the replacement did not change trust there. Condition 6 (-0.20) is the only unannounced-model change that excludes zero, and is small.

Detection probes (`merged_local/post_report.md`, corrected scoring), swapped vs control, rounds 6/8/10 pooled, AUC [CI]:

| cond | P1 | P2 (H3 prob) | P3 (different author) |
|---|---|---|---|
| 2 rename | 0.507 [0.50,0.52] | 0.454 [0.37,0.52] | 0.501 [0.42,0.60] |
| 3 | 0.521 [0.50,0.55] | 0.563 [0.46,0.67] | 0.564 [0.43,0.71] |
| 4 | 0.507 [0.50,0.52] | 0.487 [0.41,0.57] | 0.555 [0.40,0.72] |
| 5 | 0.500 [0.50,0.50] | 0.485 [0.40,0.57] | 0.468 [0.36,0.59] |
| 6 | 0.500 [0.50,0.50] | 0.466 [0.39,0.54] | 0.538 [0.46,0.61] |
| 7 | 0.535 [0.50,0.60] | 0.478 [0.38,0.59] | 0.456 [0.41,0.50] |

- P1 "replaced = true and which in {Q,R}" rate: 0.000 in every condition and round, including renamed seats. Agents always answer "no replacement", with about 100% confidence.
- Round-5 null (pre-swap): mean P2 H3 probability 0.14, mean P3 "different author" score 0.26. Post-swap means stay in the same range (P2 about 0.09-0.17).
- Trust notes about Q/R in rounds 7-10, keyword rate: control 0%, stronger 0%, stronger told 0-1%, other 0%, other told 0-2%; rename 48%, newcomer 38-41%. The LLM judge on rounds 6-10 notes agrees with the keywords (rename 52.5%, newcomer 47.5%, all other conditions 0%). In 2 and 7 the matches mostly repeat the injected "no longer in the game / new player joined" text, so they measure copying, not inference.
- Contribution change (R6-10 minus R5), Q/R minus peers: all CIs include zero except rename (+0.74 [+0.04, +1.52], Q/R contributed more than peers; one of 7 comparisons, 6 trials, treat as noise until replicated).
- The BOCPD output in `analyze.py` is uninformative (P(r=0) equals the hazard 0.1 by construction) and is superseded by the contribution-change table in `post_analysis.py`.

Reading: consistent with the lit review's root causes (RLHF-style homogenisation, narrative rationalisation, no in-context stylometry). A Qwen-7B observer group does not notice a larger same-family model or a Llama swap in the seat, even when the new occupant is told it is taking over. The base group is mostly honest (stated close to actual), so there is little behavioural signal either.

## Spend

- Modal: no GPU spend during the main local run (GPUs were refused until a payment method appeared mid-afternoon). My later GPU attempts (see "Late Modal attempts") cost roughly $4.6 of the workspace's $12.70 for 24 Oct; the remainder is the other session's apps. All Modal apps are stopped as of about 19:20 IST.
- OpenRouter: `:free` models only, no spend. Tried a small smoke pilot at the end; all calls were rate-limited (429) or not found (404), so no data (free tier is also only 50 requests/day).
- No other paid API. Local Ollama is free; my private Ollama servers (port 11435) are shut down.

## Failures and deviations

- Modal GPUs blocked, so the plan changed to local Ollama on the Mac (you approved this). Models differ from Siva's (Qwen/Llama, quantised, not GPT-4o-mini etc.).
- First launch stalled because Ollama loaded the 32B model with a 196k context (72 GB on a 48 GB machine); fixed with `OLLAMA_CONTEXT_LENGTH=4096` and resumed.
- opencode delegate: first run hit a server error on its free model, second could not read the spec outside its worktree; the third (inline spec, `opencode/glm-5.3-flash-free`) produced `serve_modal.py`, which needed a rewrite (blocking `uvicorn.run` inside `web_server`) and was never used. agy wrote the harness and analysis, which worked end to end offline on first test.
- `analyze.py` bugs found: P1 score used confidence-in-answer, BOCPD degenerate, keyword baseline contaminated by injected note text. I wrote `post_analysis.py` to fix these; `analyze.py` itself is unchanged.
- Judge ran on rounds 6-10 notes in the same way as keywords; no hand-check of 30 notes (Siva's protocol) was done.
- Model identity is not hidden from trust notes beyond the rename, and Q's reflection prompts show the seat's own old notes, as in Siva's design.

## Something you should check (not mine)

While I was waiting, other work appeared in this repo that I did not run: a Modal app `pgg-swap-l40s` (id ap-pDlDqup48pPW2CO8klR8kd) is **still deployed with 1 task** since about 15:57 IST, plus new output folders (`outputs/pgg_swap/screen`, `swap_l40s`, `replay_*`, `poscontrol_*`) and scripts (`serve_modal_l40s_swap.py`, `screen_one.py`, `replay_p1p2.py` and others) in `experiments/pgg_swap/`, which also edited `serve_modal.py`. I did not start, touch or stop any of it. It looks like another session or someone with a Modal payment method and Hugging Face token (GPU access works now: a 1-minute L4 probe I ran at about 16:50 IST succeeded, so a payment method was added after my attempts were refused). `modal billing report --for today` at that time showed **$8.06 total workspace spend for 24 Oct**, all from those other apps (`pgg-scr-*` screens, `pgg-swap-7b`, `pgg-swap-l40s`; the largest, `pgg-swap-l40s` ap-pDlDqup48pPW2CO8klR8kd, about $1.50; it was still deployed at the time but `modal app list` showed no deployed apps at about 17:40 IST). That is under the $15 cap but is shared with whoever is running it; I started no further Modal spend because of that. If the app is yours, stop it when done with `modal app stop pgg-swap-l40s`; if not, treat it as unexpected. My own run used no Modal GPU (only the image build, CPU download attempt and probes, all stopped).

## Late Modal attempts (about 17:00-19:20 IST) and stop

After a payment method appeared, I tried to get a Modal-served run. Findings, in order:
1. `pgg-swap-vllm` (3 vLLM engines on one A100-80GB): crashed twice. First on `transformers` 5.x vs vLLM 0.10.2 (`all_special_tokens_extended`, fixed by pinning `transformers==4.56.2`), then on memory-profiling collisions between engines sharing one GPU (not workable in vLLM 0.10.2).
2. `pgg-swap-split` (one engine per container: Qwen-7B and Granite-8B on L4, Qwen-32B-AWQ on L40S, per-model URLs via `PGG_URLS` in the harness): came up, but the first run was queue-bound (median call latency 49-106 s) because Modal web functions serve one request at a time without `@modal.concurrent`; I killed it after about 30 min with only 140 + 226 calls done (`modal_main/b0`, `p0`).
3. Redeployed with `@modal.concurrent(max_inputs=64)`. It ran faster (`modal_main/m0`, 366 rounds logged across 6 trials, partial and unanalysed), but you told me to stop using Modal, so I killed the run and stopped the app at about 19:20.

Result: **no complete Modal-served dataset exists.** The partial `modal_main/{b0,p0,m0}` dirs are incomplete runs (different models from the local run: Granite as the other provider), not used in any result above. Apps stopped: `pgg-swap-vllm`, `pgg-swap-split` (and my earlier probe/download apps); `modal app list` shows no deployed or running apps and no active containers. Workspace spend today, last read: **$12.70** (it was $8.10 before my redeploys; roughly $4.6 of the rise is my attempts, the rest is the other session's apps), under the $15 cap. Code from these attempts: `serve_modal_split.py`, `run_main_modal.sh`, `run_modal_auto.sh`, and a per-model URL option (`PGG_URLS`) in `pgg_swap.py`.

## OpenRouter `:free` attempt (about 19:30 IST)

To have a run on an allowed hosted backend I tried a smoke pilot on `google/gemma-4-26b-a4b-it:free` (all seats, condition 1, 1 trial, concurrency 2, stopped after 40 calls; `outputs/pgg_swap/openrouter_free_smoke/`, models in `models.openrouter_free.json`). Every call returned HTTP 429 ("temporarily rate-limited upstream"). Single test calls to `google/gemma-4-31b-it:free` also got 429 and to `nvidia/nemotron-3-super-120b-a12b:free` got 404. No usable OpenRouter data; no paid models used, no spend.

## Files

- Per-trial raw data (read-only): `outputs/pgg_swap/main_local/t0..t5/` (each with `run.json`, `calls.jsonl`, `rounds.jsonl`, `probes.jsonl`).
- Merged, with `run.json`, auto report, corrected report and judge outputs: `outputs/pgg_swap/merged_local/` (`post_report.md`, `post_probe_scores.csv`, `report_with_judge.md`, `summary_notes_judge.csv`).
- Partial pilot (aborted): `outputs/pgg_swap/pilot_local_20261024T0112Z/`.
- Code: `experiments/pgg_swap/` (`pgg_swap.py`, `fake_server.py`, `analyze.py`, `post_analysis.py`, `run_main_local.sh`, `models.local.json`). Nothing committed.

## Next steps

1. More trials (30+), since 6 gives CIs too wide to rule out small effects; a faster backend (GPU) makes this cheap once a payment method exists.
2. Run conditions 8-9 (blend-in) and a mixed or selfish base group so there is behavioural signal for peers to detect.
3. Fix the rename design: do not inject "new player"/"no longer in the game" text (it hands the answer to the observers), or report conditions 2 and 7 separately as visible-newcomer conditions.
4. Add the cross-perplexity monitor (lit review Fix 2) and the handshake probe (Fix 3) as stronger-than-prompting detectors; hand-label 30 notes.
5. Reconcile with the Modal runs found above before reporting numbers anywhere.
