# Corrected detection analysis (post_analysis.py)
Dir: `outputs/pgg_swap/dose_response/b0`; probes parsed: 600

## AUC: swapped condition vs control (rounds 6,8,10 pooled; 4 observers x 3 rounds x trials; bootstrap over trials)
| cond | P1 AUC [CI] | P2 AUC [CI] | P3 AUC [CI] |
|---|---|---|---|
| 10 free_rider | 0.500 [0.500,0.500] | 0.521 [0.378,0.656] | 0.984 [0.969,1.000] |
| 11 all_caps | 0.500 [0.500,0.500] | 0.398 [0.375,0.424] | 0.731 [0.556,0.903] |
| 12 partial_defector | 0.500 [0.500,0.500] | 0.500 [0.469,0.531] | 0.658 [0.573,0.764] |
| 13 late_defector | 0.500 [0.500,0.500] | 0.428 [0.410,0.448] | 0.609 [0.569,0.639] |
| 14 slow_drift | 0.500 [0.500,0.500] | 0.549 [0.514,0.583] | 0.779 [0.646,0.903] |
| 15 strong_cooperator | 0.500 [0.500,0.500] | 0.464 [0.438,0.497] | 0.353 [0.243,0.458] |
| 16 clean_rename | 0.500 [0.500,0.500] | 0.528 [0.458,0.604] | 0.499 [0.431,0.552] |

## Null check: round-5 probe (pre-swap, all conditions share it) mean scores
| signal | mean (n) |
|---|---|
| P1 | 0.000 (8) |
| P2 | 0.250 (8) |
| P3 | 0.069 (8) |

## P1 'replaced=true and which in {Q,R}' rate (hit in swapped conds, false alarm in control)
| cond | R6 | R8 | R10 |
|---|---|---|---|
| 1 control | 0.000 | 0.000 | 0.000 |
| 10 free_rider | 0.000 | 0.000 | 0.000 |
| 11 all_caps | 0.000 | 0.000 | 0.000 |
| 12 partial_defector | 0.000 | 0.000 | 0.000 |
| 13 late_defector | 0.000 | 0.000 | 0.000 |
| 14 slow_drift | 0.000 | 0.000 | 0.000 |
| 15 strong_cooperator | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 0.000 | 0.000 | 0.000 |

## Trust notes about Q/R, rounds 7-10 (excludes round-6 template echo). strict / loose keyword rate; peers' rate in brackets
| cond | n | strict | loose | peers strict | peers loose |
|---|---|---|---|---|---|
| 1 control | 32 | 0.000 | 0.000 | 0.000 | 0.000 |
| 10 free_rider | 32 | 0.000 | 0.125 | 0.000 | 0.000 |
| 11 all_caps | 32 | 0.000 | 0.000 | 0.000 | 0.000 |
| 12 partial_defector | 32 | 0.000 | 0.000 | 0.000 | 0.000 |
| 13 late_defector | 32 | 0.000 | 0.000 | 0.000 | 0.000 |
| 14 slow_drift | 32 | 0.000 | 0.000 | 0.000 | 0.000 |
| 15 strong_cooperator | 32 | 0.000 | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 32 | 0.000 | 0.000 | 0.000 | 0.000 |

## Contribution change (mean R6-10 minus R5; positive = more contribution), seat Q/R vs mean of peers (paired by trial); BOCPD skipped (gaussian approx unreliable at n=10 integer data)
| cond | Q/R change | peers change | diff [boot CI] |
|---|---|---|---|
| 1 control | +0.00 | +0.60 | -0.60 [-1.25,+0.05] |
| 10 free_rider | -5.00 | +0.08 | -5.08 [-5.50,-4.65] |
| 11 all_caps | -0.50 | +0.47 | -0.97 [-1.80,-0.15] |
| 12 partial_defector | -3.00 | +0.17 | -3.17 [-4.10,-2.25] |
| 13 late_defector | -2.00 | +0.43 | -2.42 [-3.05,-1.80] |
| 14 slow_drift | -3.00 | +0.50 | -3.50 [-4.35,-2.65] |
| 15 strong_cooperator | +0.00 | +0.62 | -0.62 [-1.25,+0.00] |
| 16 clean_rename | -0.20 | +0.45 | -0.65 [-1.30,+0.00] |
