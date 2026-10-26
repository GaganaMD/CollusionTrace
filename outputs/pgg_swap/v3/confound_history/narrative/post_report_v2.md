# Post-swap detection analysis (post_analysis_v2.py)
Directory: `/Users/kaustgup/Desktop/Speshal/projects/ai-collusion-research-sprint/outputs/pgg_swap/v3/confound_history/narrative`; swap round: 1; valid probe scores: 360
Pre-swap probe rounds: none; post-swap probe rounds: [6, 8, 10]

## Pooled post-swap AUC against control (condition 1)
| condition | P1 AUC [95% bootstrap CI] | P2 AUC [95% bootstrap CI] | P3 AUC [95% bootstrap CI] | P4 AUC [95% bootstrap CI] |
|---|---|---|---|---|
| 10 free_rider | 0.517 [0.500,0.550] | 0.438 [0.313,0.549] | 0.984 [0.964,1.000] | 0.967 [0.948,0.987] |
| 16 clean_rename | 0.500 [0.500,0.500] | 0.437 [0.278,0.577] | 0.614 [0.401,0.848] | 0.548 [0.429,0.655] |

## Per-round post-swap AUC against control
| condition | round | P1 | P2 | P3 | P4 |
|---|---:|---|---|---|---|
| 10 free_rider | 6 | 0.550 [0.500,0.650] | 0.670 [0.435,0.848] | 0.945 [0.887,1.000] | 0.940 [0.900,1.000] |
| 10 free_rider | 8 | 0.500 [0.500,0.500] | 0.450 [0.410,0.500] | 1.000 [1.000,1.000] | 0.950 [0.889,1.000] |
| 10 free_rider | 10 | 0.500 [0.500,0.500] | 0.230 [0.000,0.480] | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] |
| 16 clean_rename | 6 | 0.500 [0.500,0.500] | 0.560 [0.420,0.720] | 0.550 [0.140,0.850] | 0.565 [0.460,0.680] |
| 16 clean_rename | 8 | 0.500 [0.500,0.500] | 0.330 [0.135,0.566] | 0.595 [0.470,0.810] | 0.520 [0.270,0.760] |
| 16 clean_rename | 10 | 0.500 [0.500,0.500] | 0.410 [0.100,0.700] | 0.680 [0.430,0.920] | 0.555 [0.322,0.815] |

## Pre-swap probe means (condition 0)
| round | P1 | P2 | P3 |
|---:|---:|---:|---:|

## P1 replaced-and-targeted flag rate
| condition | 6 | 8 | 10 |
|---|---|---|---|
| 1 control | 0.000 | 0.000 | 0.000 |
| 10 free_rider | 0.100 | 0.000 | 0.000 |
| 16 clean_rename | 0.000 | 0.000 | 0.000 |

## Detection Diagnostics: False Alarms on Control & Swapped Hits
- **Control (Condition 1) P1 False Alarm Rate**: 0.000 (n=30)
- **Control (Condition 1) P4 False Alarm Rate**: 0.500 (n=30)

| condition | P1 Hit Rate (Post-Swap) | P4 Hit Rate (Post-Swap) | P4 n |
|---|---:|---:|---:|
| 1 control | 0.000 | 0.200 | 30 |
| 10 free_rider | 0.033 | 1.000 | 30 |
| 16 clean_rename | 0.000 | 0.233 | 30 |

## Trust-note keyword rates (rounds >= 1)
| condition | target n | strict | loose | peer strict | peer loose |
|---|---:|---:|---:|---:|---:|
| 1 control | 100 | 0.000 | 0.000 | 0.000 | 0.020 |
| 10 free_rider | 100 | 0.000 | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 100 | 0.000 | 0.000 | 0.000 | 0.000 |

## Contribution change (post rounds 1–max minus baseline round 0)
| condition | target Q/R change | mean peer change | target minus peer [bootstrap CI] |
|---|---:|---:|---:|
| 1 control | N/A | N/A | N/A |
| 10 free_rider | N/A | N/A | N/A |
| 16 clean_rename | N/A | N/A | N/A |
