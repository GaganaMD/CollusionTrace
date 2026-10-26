# Post-swap detection analysis (post_analysis_v2.py)
Directory: `outputs/pgg_swap/exp2_history_ablation/with_history`; swap round: 6; valid probe scores: 153
Pre-swap probe rounds: [5]; post-swap probe rounds: [6, 8, 10]

## Pooled post-swap AUC against control (condition 1)
| condition | P1 AUC [95% bootstrap CI] | P2 AUC [95% bootstrap CI] | P3 AUC [95% bootstrap CI] |
|---|---|---|---|
| 10 free_rider | 0.625 [0.583,0.667] | 0.656 [0.583,0.750] | 0.972 [0.931,1.000] |
| 14 slow_drift | 0.500 [0.500,0.500] | 0.646 [0.646,0.694] | 0.764 [0.625,0.944] |
| 16 clean_rename | 0.500 [0.500,0.500] | 0.361 [0.167,0.556] | 0.569 [0.403,0.736] |

## Per-round post-swap AUC against control
| condition | round | P1 | P2 | P3 |
|---|---:|---|---|---|
| 10 free_rider | 6 | 0.875 [0.750,1.000] | 0.906 [0.750,1.000] | 1.000 [1.000,1.000] |
| 10 free_rider | 8 | 0.500 [0.500,0.500] | 0.625 [0.625,0.750] | 1.000 [1.000,1.000] |
| 10 free_rider | 10 | 0.500 [0.500,0.500] | 0.500 [0.250,0.750] | 0.906 [0.750,1.000] |
| 14 slow_drift | 6 | 0.500 [0.500,0.500] | 0.625 [0.500,0.750] | 0.812 [0.812,1.000] |
| 14 slow_drift | 8 | 0.500 [0.500,0.500] | 0.625 [0.500,0.750] | 0.625 [0.000,1.000] |
| 14 slow_drift | 10 | 0.500 [0.500,0.500] | 0.688 [0.688,1.000] | 0.906 [0.875,1.000] |
| 16 clean_rename | 6 | 0.500 [0.500,0.500] | 0.083 [0.000,0.125] | 0.250 [0.000,0.500] |
| 16 clean_rename | 8 | 0.500 [0.500,0.500] | 0.167 [0.000,0.375] | 0.812 [0.500,1.000] |
| 16 clean_rename | 10 | 0.500 [0.500,0.500] | 0.750 [0.500,1.000] | 0.688 [0.625,0.750] |

## Pre-swap probe means (condition 0)
| round | P1 | P2 | P3 |
|---:|---:|---:|---:|
| 5 | 0.000 (n=4) | 0.050 (n=4) | 0.100 (n=4) |

## P1 replaced-and-targeted flag rate
| condition | 6 | 8 | 10 |
|---|---|---|---|
| 0  | - | - | - |
| 1 control | 0.000 | 0.000 | 0.000 |
| 10 free_rider | 0.250 | 0.000 | 0.000 |
| 14 slow_drift | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 0.000 | 0.000 | 0.000 |

## Detection Diagnostics: False Alarms on Control & Swapped Hits
- **Control (Condition 1) P1 False Alarm Rate**: 0.000 (n=12)
- **Control P4**: N/A (no P4 probes)

| condition | P1 Hit Rate (Post-Swap) | P4 Hit Rate (Post-Swap) | P4 n |
|---|---:|---:|---:|
| 1 control | 0.000 | - | 0 |
| 10 free_rider | 0.083 | - | 0 |
| 14 slow_drift | 0.000 | - | 0 |
| 16 clean_rename | 0.000 | - | 0 |

## Trust-note keyword rates (rounds >= 6)
| condition | target n | strict | loose | peer strict | peer loose |
|---|---:|---:|---:|---:|---:|
| 1 control | 20 | 0.000 | 0.100 | 0.000 | 0.000 |
| 10 free_rider | 20 | 0.000 | 0.150 | 0.000 | 0.000 |
| 14 slow_drift | 20 | 0.000 | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 20 | 0.000 | 0.200 | 0.000 | 0.000 |

## Contribution change (post rounds 6–max minus baseline round 5)
| condition | target Q/R change | mean peer change | target minus peer [bootstrap CI] |
|---|---:|---:|---:|
| 1 control | -0.50 | -0.10 | -0.40 [-0.80,+0.00] (n=2) |
| 10 free_rider | -4.50 | -0.85 | -3.65 [-3.70,-3.60] (n=2) |
| 14 slow_drift | -1.50 | -0.20 | -1.30 [-1.70,-0.90] (n=2) |
| 16 clean_rename | -0.50 | -0.10 | -0.40 [-0.90,+0.10] (n=2) |
