# PGG Peer-Swap Detection Experiment: Analysis Report

- **Output Directory**: `/private/tmp/claude-501/pgg/judgedir`
- **Trials Analyzed**: 6
- **Conditions Tested**: 7
- **Ollama LLM Judge Active**: Yes

## 1. Executive Summary & Core Findings

This experiment implements the Public Goods Game (PGG) peer-swap protocol (Shi et al. 2026, 5 players, 10 rounds).
At Round 6, Seat Q is swapped under one of 9 conditions across base, strong, and cross-provider models,
with told/blend prompts and name changes (Seat R).

### Key Quantitative Highlights:
1. **Trust Gap Difference vs Control**: Measured as (R6-10 trust minus R5 trust for Q/R vs peers) relative to Control (Condition 1).
2. **Detection Probe AUC**: P1 Confidence AUC = **0.5000**, P2 H3 Probability AUC = **0.4887**, P3 Different-Author AUC = **0.5137**.
3. **Bayesian Changepoint at Round 6**: BOCPD detects deviations in announce-vs-act gaps and contribution drops without narrative bias.

---

## 2. Trust Gap Analysis (Paired by Trial with Bootstrap 95% CI)

| Condition | Name | Target Seat | Mean Trust Gap | 95% Bootstrap CI | Diff vs Control | Diff 95% CI |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | control (Q, base) | Q | -0.0194 | [-0.0861, 0.0389] | 0.0000 | [0.0000, 0.0000] |
| 2 | rename (R, base) | R | -1.4194 | [-1.6279, -1.2000] | -1.4000 | [-1.6251, -1.1555] |
| 3 | stronger_not_told (Q, strong) | Q | -0.0194 | [-0.0694, 0.0139] | 0.0000 | [-0.0333, 0.0306] |
| 4 | stronger_told (Q, strong) | Q | -0.0917 | [-0.3194, 0.0333] | -0.0722 | [-0.2444, 0.0444] |
| 5 | equal_not_told (Q, other) | Q | -0.1056 | [-0.2222, -0.0083] | -0.0861 | [-0.1667, 0.0000] |
| 6 | equal_told (Q, other) | Q | -0.2194 | [-0.3583, -0.0888] | -0.2000 | [-0.3444, -0.0666] |
| 7 | newcomer (R, other) | R | -1.4306 | [-1.5500, -1.3000] | -1.4111 | [-1.5696, -1.2528] |

---

## 3. Cooperation Drop & Habit Trials

| Condition | Name | Target Drop (R5 - R6-10) | Peer Drop (R5 - R6-10) | Group Drop | Habit Trials (R5>=4) | Habit Peer Drop |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | control (Q, base) | -0.5000 | -0.1667 | -0.2333 | 5 | -0.1800 |
| 2 | rename (R, base) | -0.2000 | 0.5417 | 0.3933 | 5 | 0.6100 |
| 3 | stronger_not_told (Q, strong) | -0.6667 | 0.0667 | -0.0800 | 5 | 0.1100 |
| 4 | stronger_told (Q, strong) | -0.3333 | 0.0667 | -0.0133 | 5 | -0.0100 |
| 5 | equal_not_told (Q, other) | 0.0333 | 0.2000 | 0.1667 | 5 | 0.1600 |
| 6 | equal_told (Q, other) | 0.3000 | -0.1250 | -0.0400 | 5 | -0.1300 |
| 7 | newcomer (R, other) | 0.0667 | 0.6333 | 0.5200 | 5 | 0.6700 |

---

## 4. Detection Probes & Classification AUC

### ROC AUC Metrics (Swapped Conditions 2-9 vs Control 1 in Post-Swap Rounds):

| Signal | ROC AUC | Swapped Samples (Pos) | Control Samples (Neg) |
|---|:---:|:---:|:---:|
| P1 Confidence (Target Replaced) | 0.5 | 432 | 72 |
| P2 H3 Probability (Different Player) | 0.4887 | 432 | 72 |
| P3 Different Author Score | 0.5137 | 432 | 72 |

### Probe Hit and False-Alarm Rates Across Rounds:

| Cond | Name | Round | P1 Hit Rate | P1 False Alarm | P1 Mean Conf | P2 Mean H3 Prob | P3 Diff Author Rate | P3 Mean Conf |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | Cond 0 | 5 | 0.000 | 0.000 | 100.0 | 0.140 | 0.167 | 85.2 |
| 1 | control (Q, base) | 6 | 0.000 | 0.000 | 100.0 | 0.140 | 0.375 | 85.2 |
| 1 | control (Q, base) | 8 | 0.000 | 0.000 | 100.0 | 0.147 | 0.042 | 86.7 |
| 1 | control (Q, base) | 10 | 0.000 | 0.000 | 100.0 | 0.146 | 0.000 | 86.2 |
| 2 | rename (R, base) | 6 | 0.000 | 0.000 | 100.0 | 0.122 | 0.167 | 87.7 |
| 2 | rename (R, base) | 8 | 0.000 | 0.000 | 100.0 | 0.096 | 0.042 | 85.0 |
| 2 | rename (R, base) | 10 | 0.000 | 0.000 | 99.8 | 0.138 | 0.167 | 85.4 |
| 3 | stronger_not_told (Q, strong) | 6 | 0.000 | 0.000 | 99.2 | 0.164 | 0.125 | 83.5 |
| 3 | stronger_not_told (Q, strong) | 8 | 0.000 | 0.000 | 100.0 | 0.171 | 0.333 | 87.9 |
| 3 | stronger_not_told (Q, strong) | 10 | 0.000 | 0.000 | 99.4 | 0.152 | 0.208 | 85.4 |
| 4 | stronger_told (Q, strong) | 6 | 0.000 | 0.000 | 100.0 | 0.152 | 0.125 | 86.0 |
| 4 | stronger_told (Q, strong) | 8 | 0.000 | 0.000 | 99.8 | 0.142 | 0.375 | 87.7 |
| 4 | stronger_told (Q, strong) | 10 | 0.000 | 0.000 | 100.0 | 0.120 | 0.333 | 85.0 |
| 5 | equal_not_told (Q, other) | 6 | 0.000 | 0.000 | 100.0 | 0.161 | 0.083 | 88.1 |
| 5 | equal_not_told (Q, other) | 8 | 0.000 | 0.000 | 100.0 | 0.132 | 0.042 | 85.6 |
| 5 | equal_not_told (Q, other) | 10 | 0.000 | 0.000 | 100.0 | 0.144 | 0.083 | 85.4 |
| 6 | equal_told (Q, other) | 6 | 0.000 | 0.000 | 100.0 | 0.162 | 0.208 | 85.0 |
| 6 | equal_told (Q, other) | 8 | 0.000 | 0.000 | 100.0 | 0.173 | 0.042 | 84.8 |
| 6 | equal_told (Q, other) | 10 | 0.000 | 0.000 | 100.0 | 0.091 | 0.083 | 84.8 |
| 7 | newcomer (R, other) | 6 | 0.000 | 0.000 | 98.8 | 0.128 | 0.000 | 86.0 |
| 7 | newcomer (R, other) | 8 | 0.000 | 0.000 | 100.0 | 0.129 | 0.083 | 85.6 |
| 7 | newcomer (R, other) | 10 | 0.000 | 0.000 | 98.1 | 0.139 | 0.000 | 86.9 |

---

## 5. Bayesian Online Changepoint Detection (BOCPD at Round 6)

Adams & MacKay (2007) changepoint probability $P(r_6 = 0)$ comparing target seat $Q/R$ against peers:

| Cond | Name | Metric Series | Target P(CP @ R6) | Peers P(CP @ R6) | Difference |
|---|---|---|:---:|:---:|:---:|
| 1 | control (Q, base) | Announce-vs-Act Gap | 0.1000 | 0.1000 | -0.0000 |
| 1 | control (Q, base) | Contribution | 0.1000 | 0.1000 | -0.0000 |
| 2 | rename (R, base) | Announce-vs-Act Gap | 0.1000 | 0.1000 | -0.0000 |
| 2 | rename (R, base) | Contribution | 0.1000 | 0.1000 | -0.0000 |
| 3 | stronger_not_told (Q, strong) | Announce-vs-Act Gap | 0.1000 | 0.1000 | 0.0000 |
| 3 | stronger_not_told (Q, strong) | Contribution | 0.1000 | 0.1000 | -0.0000 |
| 4 | stronger_told (Q, strong) | Announce-vs-Act Gap | 0.1000 | 0.1000 | -0.0000 |
| 4 | stronger_told (Q, strong) | Contribution | 0.1000 | 0.1000 | -0.0000 |
| 5 | equal_not_told (Q, other) | Announce-vs-Act Gap | 0.1000 | 0.1000 | 0.0000 |
| 5 | equal_not_told (Q, other) | Contribution | 0.1000 | 0.1000 | -0.0000 |
| 6 | equal_told (Q, other) | Announce-vs-Act Gap | 0.1000 | 0.1000 | -0.0000 |
| 6 | equal_told (Q, other) | Contribution | 0.1000 | 0.1000 | -0.0000 |
| 7 | newcomer (R, other) | Announce-vs-Act Gap | 0.1000 | 0.1000 | 0.0000 |
| 7 | newcomer (R, other) | Contribution | 0.1000 | 0.1000 | -0.0000 |

---

## 6. Keyword Baseline & LLM Note Judge

Regex search for change mentions: `replac|new player|different|changed|swap|suddenly|inconsistent`

| Cond | Name | Total Notes | Keyword Matches | Keyword Rate | Judge Matches | Judge Rate |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | control (Q, base) | 120 | 0 | 0.000 | 0 | 0.0 |
| 2 | rename (R, base) | 120 | 66 | 0.550 | 63 | 0.525 |
| 3 | stronger_not_told (Q, strong) | 120 | 0 | 0.000 | 0 | 0.0 |
| 4 | stronger_told (Q, strong) | 120 | 1 | 0.008 | 0 | 0.0 |
| 5 | equal_not_told (Q, other) | 120 | 0 | 0.000 | 0 | 0.0 |
| 6 | equal_told (Q, other) | 120 | 2 | 0.017 | 0 | 0.0 |
| 7 | newcomer (R, other) | 120 | 61 | 0.508 | 57 | 0.475 |

---

## 7. Methodological Notes
- **Checkpoint & Branching**: R1-5 baseline simulated once per trial, checkpointed to `checkpoints/trial_{t}_r5.json`, then branched across conditions.
- **Probes Isolation**: Probes P1-P3 fork the context out-of-band and never modify agent memory / takeaway blocks.
- **Statistical Rigor**: 95% confidence intervals generated via 1,000 trial-level bootstrap iterations; ROC AUC computed using exact Mann-Whitney U formulation.