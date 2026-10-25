# Corrected detection analysis (post_analysis.py)
Dir: `outputs/pgg_swap/reasoning_pilot`; probes parsed: 240

## AUC: swapped condition vs control (rounds 6,8,10 pooled; 4 observers x 3 rounds x trials; bootstrap over trials)
| cond | P1 AUC [CI] | P2 AUC [CI] | P3 AUC [CI] |
|---|---|---|---|
| 10 free_rider | 0.417 [0.333,0.417] | 0.662 [0.615,0.705] | 0.643 [0.632,0.677] |
| 16 clean_rename | 0.500 [0.455,0.528] | 0.485 [0.417,0.556] | 0.451 [0.444,0.451] |

## Null check: round-5 probe (pre-swap, all conditions share it) mean scores
| signal | mean (n) |
|---|---|
| P1 | 0.500 (8) |
| P2 | 0.212 (8) |
| P3 | 0.175 (8) |

## P1 'replaced=true and which in {Q,R}' rate (hit in swapped conds, false alarm in control)
| cond | R6 | R8 | R10 |
|---|---|---|---|
| 1 control | 0.000 | 0.000 | 0.000 |
| 10 free_rider | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 0.250 | 0.000 | 0.000 |

## Trust notes about Q/R, rounds 7-10 (excludes round-6 template echo). strict / loose keyword rate; peers' rate in brackets
| cond | n | strict | loose | peers strict | peers loose |
|---|---|---|---|---|---|
| 1 control | 32 | 0.000 | 0.188 | 0.000 | 0.281 |
| 10 free_rider | 32 | 0.000 | 0.375 | 0.000 | 0.320 |
| 16 clean_rename | 32 | 0.000 | 0.406 | 0.000 | 0.359 |

## Contribution change (mean R6-10 minus R5; positive = more contribution), seat Q/R vs mean of peers (paired by trial); BOCPD skipped (gaussian approx unreliable at n=10 integer data)
| cond | Q/R change | peers change | diff [boot CI] |
|---|---|---|---|
| 1 control | +0.00 | +0.40 | -0.40 [-0.60,-0.20] |
| 10 free_rider | +0.00 | +0.35 | -0.35 [-0.45,-0.25] |
| 16 clean_rename | +0.10 | +0.05 | +0.05 [+0.00,+0.10] |
