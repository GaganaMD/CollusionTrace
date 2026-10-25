# Corrected detection analysis (post_analysis.py)
Dir: `outputs/pgg_swap/dose_response/merged`; probes parsed: 1496

## AUC: swapped condition vs control (rounds 6,8,10 pooled; 4 observers x 3 rounds x trials; bootstrap over trials)
| cond | P1 AUC [CI] | P2 AUC [CI] | P3 AUC [CI] |
|---|---|---|---|
| 10 free_rider | 0.500 [0.500,0.500] | 0.576 [0.448,0.692] | 0.955 [0.844,1.000] |
| 11 all_caps | 0.500 [0.500,0.500] | 0.475 [0.339,0.615] | 0.633 [0.530,0.771] |
| 12 partial_defector | 0.500 [0.500,0.500] | 0.538 [0.457,0.672] | 0.649 [0.538,0.759] |
| 13 late_defector | 0.500 [0.500,0.500] | 0.457 [0.363,0.543] | 0.595 [0.450,0.709] |
| 14 slow_drift | 0.500 [0.500,0.500] | 0.545 [0.470,0.625] | 0.796 [0.657,0.923] |
| 15 strong_cooperator | 0.500 [0.500,0.500] | 0.539 [0.459,0.666] | 0.394 [0.297,0.466] |
| 16 clean_rename | 0.500 [0.500,0.500] | 0.588 [0.492,0.688] | 0.493 [0.373,0.597] |

## Null check: round-5 probe (pre-swap, all conditions share it) mean scores
| signal | mean (n) |
|---|---|
| P1 | 0.000 (20) |
| P2 | 0.172 (20) |
| P3 | 0.211 (19) |

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
| 1 control | 80 | 0.000 | 0.000 | 0.000 | 0.013 |
| 10 free_rider | 80 | 0.000 | 0.050 | 0.000 | 0.009 |
| 11 all_caps | 80 | 0.000 | 0.000 | 0.000 | 0.000 |
| 12 partial_defector | 80 | 0.000 | 0.037 | 0.000 | 0.000 |
| 13 late_defector | 80 | 0.000 | 0.000 | 0.000 | 0.000 |
| 14 slow_drift | 80 | 0.000 | 0.000 | 0.000 | 0.000 |
| 15 strong_cooperator | 80 | 0.000 | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 80 | 0.000 | 0.000 | 0.000 | 0.000 |

## Contribution change (mean R6-10 minus R5; positive = more contribution), seat Q/R vs mean of peers (paired by trial); BOCPD skipped (gaussian approx unreliable at n=10 integer data)
| cond | Q/R change | peers change | diff [boot CI] |
|---|---|---|---|
| 1 control | -0.08 | +0.19 | -0.27 [-0.78,+0.07] |
| 10 free_rider | -5.00 | -0.06 | -4.94 [-5.26,-4.67] |
| 11 all_caps | -0.56 | +0.14 | -0.70 [-1.27,-0.31] |
| 12 partial_defector | -3.00 | +0.02 | -3.02 [-3.63,-2.55] |
| 13 late_defector | -2.00 | +0.14 | -2.14 [-2.63,-1.81] |
| 14 slow_drift | -3.00 | +0.10 | -3.10 [-3.74,-2.69] |
| 15 strong_cooperator | +0.00 | +0.22 | -0.22 [-0.75,+0.09] |
| 16 clean_rename | -0.20 | +0.18 | -0.38 [-0.91,+0.08] |
