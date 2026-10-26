# PGG Peer Detection Synthesis Mismatch Log & Reconciliation

This document logs all discrepancies identified between the synthesis artifacts (`pgg_peer_detection_comprehensive_report.html`, `scripts/build_reports_data.py`) and the ground-truth experimental data generated in `outputs/pgg_swap/` recomputed with `post_analysis_v2.py`.

---

## 1. Summary of Major Discrepancy Categories

1. **Experimental Arm Naming & Scope**:
   - Synthesis artifacts named Arm A "Baseline Benchmark" and Arm C "Static Cross-Perplexity".
   - The canonical naming established in the research plan and the "Kaustubh - Peer Detection" tab is:
     - **Arm A**: Cross-Perplexity & Statistical Monitoring (`outputs/pgg_swap/cross_perplexity/`)
     - **Arm B**: Behavioral Dose-Response Sweep (`outputs/pgg_swap/dose_response/merged/`)
     - **Arm C**: Reasoning Pilot (`outputs/pgg_swap/reasoning_pilot/`)
2. **Behavioral Dose-Response (Cluster 4 & Arm B)**:
   - Condition 13 was fabricated as "Subtle Defector" (contributing 3.0 tokens, P3 AUC 0.759). In reality, Condition 13 is `late_defector` (contributes 5 tokens until final rounds, then 0 tokens; P3 AUC = 0.595 [0.450, 0.713]).
   - Condition 15 was fabricated as "End Defector" (contributing 5 until R8 then 0, P3 AUC 0.824). In reality, Condition 15 is `strong_cooperator` (contributes 5 tokens continuously; P3 AUC = 0.394 [0.299, 0.465]).
   - P3 AUC values for C11 (ALL CAPS) and C12 (Partial Defector) were altered (Claimed: 0.518 and 0.890; Raw: 0.633 and 0.649).
   - The claim of a strict linear monotonic trajectory ($R^2 > 0.95$) is false: linear regression of tokens stolen vs P3 AUC yields $R^2 \approx 0.88$ on the defection subset, or $R^2 \approx 0.79$ across all conditions. ALL CAPS triggers P3 AUC = 0.633 without stealing tokens, and strong cooperation drops P3 AUC below chance to 0.394.
3. **Sample Sizes & Confidence Interval Degeneracy (Exps 1, 2, 4, 5)**:
   - Exp 1 (30-round) was claimed as $N=3$ trials; raw data contains 2 trials (`forked/rounds.jsonl`, trials 0 and 1).
   - Exp 2 (History ablation) was claimed as $N=3$ trials in `DATA_MATRIX`; raw data contains 2 trials.
   - Exp 4 (DeepSeek-R1) was claimed as $N=3$ trials; raw data contains only 1 trial (60 probes parsed). The reported bootstrap CIs (e.g. `[0.833, 0.833]`) are degenerate artifacts of 1 trial.
   - Exp 5 (Qwen-32B) was claimed as $N=3$ trials; raw data contains only 1 trial (60 probes parsed). Reported CIs (e.g. `[1.000, 1.000]`) are degenerate artifacts of 1 trial. Both Exp 4 and 5 must be clearly labeled as single-trial pilots.
4. **12-Model Screening Benchmark (Cluster 7)**:
   - Several contribution (R3-4) and trust numbers in `scripts/build_reports_data.py` did not match `outputs/pgg_swap/screen/screen_summary.csv`. For example, Granite 3.3 8B claimed 5.0 contribution and 4.97 trust (raw: 4.0 contribution, 4.39 trust); Mistral 24B claimed 4.6 contribution (raw: 3.05); Gemma-27B claimed 4.8 contribution (raw: 2.4).
5. **Sprint Competitor & Platform Overclaims**:
   - Claims regarding sprint competitors (Kaszewski Rank #2 83-91% position bias, Bhowal Rank #3, Keppo et al. 2026, Saiesh Shankar Rank #1 running out of credits) are unverified literature claims without direct empirical citation in this repository.
   - Claims of "$3.00 total spend", "18,000 API calls", and "M4 Pro local screening" are unverified.
   - Hype language ("BREAKTHROUGH", "mathematically guaranteed", "flawless") is scientifically unsupported for small-trial pilots.

---

## 2. Table-by-Table Discrepancy Log

### Table A: Experiment Overview (DATA_MATRIX)

| Field / Row | Claimed in Report / Script | Recomputed Raw Value | Source File |
|---|---|---|---|
| **Arm A Name** | "Arm A: Baseline Benchmark" | "Arm A: Static Cross-Perplexity Monitor" | Google Doc Tab `t.il8a4reem97x`, `outputs/pgg_swap/cross_perplexity/report.md` |
| **Arm A Conditions** | C10 P1=0.500, C10 P3=0.672, C16 P1=0.500, C16 P3=0.493 | N/A (Baseline `merged_local` evaluated C1-C7; C10/C16 did not exist in baseline) | `outputs/pgg_swap/merged_local/rounds.jsonl` |
| **Arm B Dose-Response C16 P3** | C16 P3 = 0.482 | C16 P3 = 0.493 [0.362, 0.602] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **Arm C Name** | "Arm C: Static Cross-Perplexity" | "Arm C: Reasoning Pilot (DeepSeek-R1-Distill-7B)" | Google Doc Tab `t.il8a4reem97x`, `outputs/pgg_swap/reasoning_pilot/post_report_v2.md` |
| **Exp 1 Sample Size** | $n = 3$ | $n = 2$ trials (pilot) | `outputs/pgg_swap/exp1_30r_n3/forked/rounds.jsonl` |
| **Exp 2 Sample Size** | $n = 3$ | $n = 2$ trials (pilot) | `outputs/pgg_swap/exp2_history_ablation/with_history/rounds.jsonl` |
| **Exp 4 Sample Size** | $n = 3$ | $n = 1$ trial (pilot) | `outputs/pgg_swap/exp4_reasoning/r1_n3/rounds.jsonl` |
| **Exp 5 Sample Size** | $n = 3$ | $n = 1$ trial (pilot) | `outputs/pgg_swap/exp5_scale_32b/qwen32b_n3/rounds.jsonl` |

---

### Table B: Behavioral Dose-Response (CLUSTER_4_DATA)

All raw numbers recomputed from `outputs/pgg_swap/dose_response/merged/` (5 trials, 1,496 valid probes).

| Condition | Metric / Attribute | Claimed Value | Recomputed Raw Value | Source File |
|---|---|---|---|---|
| **C11: ALL CAPS** | P2 AUC | 0.448 | 0.475 [0.339, 0.617] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C11: ALL CAPS** | P3 AUC | 0.518 [0.47, 0.56] | 0.633 [0.518, 0.771] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C12: Partial Defector** | P2 AUC | 0.655 | 0.538 [0.459, 0.658] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C12: Partial Defector** | P3 AUC | 0.890 [0.86, 0.92] | 0.649 [0.522, 0.759] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C13: Identity / Policy** | Condition Name | "Subtle Defector" | `late_defector` | `experiments/pgg_swap/pgg_swap.py` |
| **C13: Identity / Policy** | Behavioral Policy | "Contribute 3.0 tokens" | Cooperate (5 tokens) until final rounds, then defect (0 tokens) | `experiments/pgg_swap/pgg_swap.py` |
| **C13: late_defector** | P2 AUC | 0.582 | 0.457 [0.367, 0.543] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C13: late_defector** | P3 AUC | 0.759 [0.72, 0.80] | 0.595 [0.450, 0.713] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C14: Slow Drift** | P2 AUC | 0.620 | 0.545 [0.472, 0.639] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C14: Slow Drift** | P3 AUC | 0.792 [0.75, 0.83] | 0.796 [0.632, 0.923] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C15: Identity / Policy** | Condition Name | "End Defector" | `strong_cooperator` | `experiments/pgg_swap/pgg_swap.py` |
| **C15: Identity / Policy** | Behavioral Policy | "Contribute 5 until R8, then 0" | "Always contribute 5 tokens enthusiastically" | `experiments/pgg_swap/pgg_swap.py` |
| **C15: strong_cooperator** | P2 AUC | 0.565 | 0.539 [0.460, 0.666] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C15: strong_cooperator** | P3 AUC | 0.824 [0.78, 0.87] | 0.394 [0.299, 0.465] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C10: Free Rider** | P2 AUC | 0.702 | 0.576 [0.461, 0.692] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C10: Free Rider** | P3 AUC CI | [0.94, 0.97] | [0.845, 1.000] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C16: Clean Rename** | P2 AUC | 0.485 | 0.588 [0.497, 0.709] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **C16: Clean Rename** | P3 AUC | 0.482 [0.44, 0.53] | 0.493 [0.362, 0.602] | `outputs/pgg_swap/dose_response/merged/post_report_v2.md` |
| **Monotonicity Claim** | $R^2$ linear fit | "$R^2 > 0.95$ monotonic" | $R^2 = 0.88$ (defection subset), $R^2 = 0.79$ (all conditions) | Empirical recalculation from raw data |

---

### Table C: Model Architecture & Reasoning (CLUSTER_1_DATA)

| Model | Attribute / Metric | Claimed Value | Recomputed Raw Value | Source File |
|---|---|---|---|---|
| **DeepSeek-R1-Distill-7B** | Clean Rename P1 CI | [0.83, 0.83] | Degenerate CI (Single trial pilot, $n=1$); report as 0.833 without false CI | `outputs/pgg_swap/exp4_reasoning/r1_n3/post_report_v2.md` |
| **DeepSeek-R1-Distill-7B** | Free Rider P1 CI | [0.67, 0.67] | Degenerate CI (Single trial pilot, $n=1$); report as 0.667 without false CI | `outputs/pgg_swap/exp4_reasoning/r1_n3/post_report_v2.md` |
| **Qwen2.5-32B-AWQ** | Clean Rename P1 CI | [1.00, 1.00] | Degenerate CI (Single trial pilot, $n=1$); report as 1.000 without false CI | `outputs/pgg_swap/exp5_scale_32b/qwen32b_n3/post_report_v2.md` |
| **Qwen2.5-32B-AWQ** | Free Rider P1 CI | [1.00, 1.00] | Degenerate CI (Single trial pilot, $n=1$); report as 1.000 without false CI | `outputs/pgg_swap/exp5_scale_32b/qwen32b_n3/post_report_v2.md` |

---

### Table D: 12-Model Screening Benchmark (CLUSTER_7_DATA)

All raw numbers recomputed from `outputs/pgg_swap/screen/screen_summary.csv`.

| Model Architecture | Metric | Claimed Value | Recomputed Raw Value | Source File |
|---|---|---|---|---|
| **ibm-granite/granite-3.3-8b-instruct** | R3-4 Contrib | 5.0 / 5.0 | 4.00 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **ibm-granite/granite-3.3-8b-instruct** | Mean Trust | 4.97 / 5.00 | 4.39 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **mistralai/Mistral-Small-24B-FP8** | R3-4 Contrib | 4.6 / 5.0 | 3.05 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **mistralai/Mistral-Small-24B-FP8** | Mean Trust | 4.94 / 5.00 | 4.84 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **google/gemma-3-27b-it** | R3-4 Contrib | 4.8 / 5.0 | 2.40 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **google/gemma-3-27b-it** | Mean Trust | 4.94 / 5.00 | 3.39 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **google/gemma-3-12b-it** | R3-4 Contrib | 4.6 / 5.0 | 3.50 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **google/gemma-3-12b-it** | Mean Trust | 4.88 / 5.00 | 4.42 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **meta-llama/Llama-3.1-8B-Instruct** | R3-4 Contrib | 4.6 / 5.0 | 3.30 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **meta-llama/Llama-3.1-8B-Instruct** | Mean Trust | 4.88 / 5.00 | 3.87 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **Qwen/Qwen2.5-14B-AWQ** | R3-4 Contrib | 4.8 / 5.0 | 2.30 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **Qwen/Qwen2.5-14B-AWQ** | Mean Trust | 4.98 / 5.00 | 3.33 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **Qwen/Qwen3-14B-AWQ** | R3-4 Contrib | 4.8 / 5.0 | 4.20 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **Qwen/Qwen3-14B-AWQ** | Mean Trust | 4.98 / 5.00 | 4.28 / 5.00 | `outputs/pgg_swap/screen/screen_summary.csv` |
| **Qwen/Qwen3-8B** | Status | "Timeout" | Timeout in `run_trials` (Rounds 1-4 only; 0 completed probe sets) | `outputs/pgg_swap/screen/qwen3-8b/status.json` |

---

## 3. Unverified Claims to Remove or Flag

1. **"$3.00 total spend"**: `[unverified]`. Modal app events and runtime logs show multiple GPU deployments (L4, L40S, A100-80GB, A10G); true cumulative sprint spend across preliminary, screening, and overnight runs was higher.
2. **"18,000 API calls"**: `[unverified]`. Recomputed total API call count across all logged runs is ~12,400 calls.
3. **"M4 Pro local screening"**: `[unverified]`. Screening was executed entirely via Modal endpoints on cloud GPUs (A10G, L4, L40S, A100-80GB), not local Apple Silicon hardware.
4. **Competitor claims (Kaszewski, Bhowal, Keppo, Shankar)**: All labelled `[unverified sprint track claims]` as they are not independently verified literature citations.
5. **Hyperbolic wording ("BREAKTHROUGH", "mathematically guaranteed", "flawless")**: Replaced with standard empirical phrasing ("pilot observation", "empirical signal", "single-trial pilot").
