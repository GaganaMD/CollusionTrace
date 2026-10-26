# Corrected detection analysis (post_analysis.py)
Dir: `outputs/pgg_swap/merged_local`; probes parsed: 1584

## AUC: swapped condition vs control (rounds 6,8,10 pooled; 4 observers x 3 rounds x trials; bootstrap over trials)
| cond | P1 AUC [CI] | P2 AUC [CI] | P3 AUC [CI] |
|---|---|---|---|
| 2 rename | 0.507 [0.500,0.521] | 0.454 [0.373,0.523] | 0.501 [0.421,0.595] |
| 3 strong_notold | 0.521 [0.500,0.549] | 0.563 [0.456,0.669] | 0.564 [0.434,0.709] |
| 4 strong_told | 0.507 [0.500,0.521] | 0.487 [0.410,0.570] | 0.555 [0.404,0.717] |
| 5 other_notold | 0.500 [0.500,0.500] | 0.485 [0.401,0.565] | 0.468 [0.357,0.593] |
| 6 other_told | 0.500 [0.500,0.500] | 0.466 [0.385,0.538] | 0.538 [0.461,0.609] |
| 7 newcomer | 0.535 [0.500,0.604] | 0.478 [0.380,0.586] | 0.456 [0.411,0.496] |

## Null check: round-5 probe (pre-swap, all conditions share it) mean scores
| signal | mean (n) |
|---|---|
| P1 | 0.000 (24) |
| P2 | 0.140 (24) |
| P3 | 0.260 (24) |

## P1 'replaced=true and which in {Q,R}' rate (hit in swapped conds, false alarm in control)
| cond | R6 | R8 | R10 |
|---|---|---|---|
| 1 control | 0.000 | 0.000 | 0.000 |
| 2 rename | 0.000 | 0.000 | 0.000 |
| 3 strong_notold | 0.000 | 0.000 | 0.000 |
| 4 strong_told | 0.000 | 0.000 | 0.000 |
| 5 other_notold | 0.000 | 0.000 | 0.000 |
| 6 other_told | 0.000 | 0.000 | 0.000 |
| 7 newcomer | 0.000 | 0.000 | 0.000 |

## Trust notes about Q/R, rounds 7-10 (excludes round-6 template echo). strict / loose keyword rate; peers' rate in brackets
| cond | n | strict | loose | peers strict | peers loose |
|---|---|---|---|---|---|
| 1 control | 96 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2 rename | 96 | 0.479 | 0.479 | 0.000 | 0.000 |
| 3 strong_notold | 96 | 0.000 | 0.000 | 0.000 | 0.003 |
| 4 strong_told | 96 | 0.000 | 0.010 | 0.000 | 0.003 |
| 5 other_notold | 96 | 0.000 | 0.000 | 0.000 | 0.005 |
| 6 other_told | 96 | 0.000 | 0.021 | 0.000 | 0.005 |
| 7 newcomer | 96 | 0.375 | 0.406 | 0.003 | 0.008 |

## Contribution change (mean R6-10 minus R5; positive = more contribution), seat Q/R vs mean of peers (paired by trial); BOCPD skipped (gaussian approx unreliable at n=10 integer data)
| cond | Q/R change | peers change | diff [boot CI] |
|---|---|---|---|
| 1 control | +0.50 | +0.17 | +0.33 [-0.39,+1.20] |
| 2 rename | +0.20 | -0.54 | +0.74 [+0.04,+1.52] |
| 3 strong_notold | +0.67 | -0.07 | +0.73 [-0.12,+1.70] |
| 4 strong_told | +0.33 | -0.07 | +0.40 [-0.49,+1.30] |
| 5 other_notold | -0.03 | -0.20 | +0.17 [-0.51,+0.80] |
| 6 other_told | -0.30 | +0.13 | -0.42 [-1.53,+0.83] |
| 7 newcomer | -0.07 | -0.63 | +0.57 [-0.47,+1.53] |
