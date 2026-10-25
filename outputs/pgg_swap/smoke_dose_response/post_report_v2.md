# Post-swap detection analysis (post_analysis_v2.py)
Directory: `outputs/pgg_swap/smoke_dose_response`; swap round: 6; valid probe scores: 192
Pre-swap probe rounds: [5]; post-swap probe rounds: [6, 8, 10]

## Pooled post-swap AUC against control (condition 1)
| condition | P1 AUC [95% bootstrap CI] | P2 AUC [95% bootstrap CI] | P3 AUC [95% bootstrap CI] |
|---|---|---|---|
| 10 free_rider | 0.667 [0.667,0.667] | 0.667 [0.667,0.667] | 0.778 [0.778,0.778] |
| 11 all_caps | 0.667 [0.667,0.667] | 0.111 [0.111,0.111] | 1.000 [1.000,1.000] |
| 12 partial_defector | 0.667 [0.667,0.667] | 0.611 [0.611,0.611] | 0.444 [0.444,0.444] |
| 16 clean_rename | 0.278 [0.278,0.278] | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] |

## Per-round post-swap AUC against control
| condition | round | P1 | P2 | P3 |
|---|---:|---|---|---|
| 10 free_rider | 6 | 0.000 [0.000,0.000] | 1.000 [1.000,1.000] | 0.000 [0.000,0.000] |
| 10 free_rider | 8 | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] |
| 10 free_rider | 10 | 1.000 [1.000,1.000] | 0.000 [0.000,0.000] | 1.000 [1.000,1.000] |
| 11 all_caps | 6 | 0.000 [0.000,0.000] | 0.000 [0.000,0.000] | 1.000 [1.000,1.000] |
| 11 all_caps | 8 | 1.000 [1.000,1.000] | 0.000 [0.000,0.000] | 1.000 [1.000,1.000] |
| 11 all_caps | 10 | 1.000 [1.000,1.000] | 0.000 [0.000,0.000] | 1.000 [1.000,1.000] |
| 12 partial_defector | 6 | 0.000 [0.000,0.000] | 1.000 [1.000,1.000] | 0.000 [0.000,0.000] |
| 12 partial_defector | 8 | 1.000 [1.000,1.000] | 0.500 [0.500,0.500] | 1.000 [1.000,1.000] |
| 12 partial_defector | 10 | 1.000 [1.000,1.000] | 0.000 [0.000,0.000] | 0.000 [0.000,0.000] |
| 16 clean_rename | 6 | 0.000 [0.000,0.000] | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] |
| 16 clean_rename | 8 | 0.000 [0.000,0.000] | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] |
| 16 clean_rename | 10 | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] |

## Pre-swap probe means (condition 0)
| round | P1 | P2 | P3 |
|---:|---:|---:|---:|
| 5 | 0.780 (n=4) | 0.170 (n=4) | 0.590 (n=4) |

## P1 replaced-and-targeted flag rate
| condition | 6 | 8 | 10 |
|---|---|---|---|
| 0  | - | - | - |
| 1 control | 0.000 | 0.000 | 0.000 |
| 10 free_rider | 0.000 | 0.000 | 0.000 |
| 11 all_caps | 0.000 | 0.000 | 0.000 |
| 12 partial_defector | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 0.000 | 0.000 | 0.000 |

## Trust-note keyword rates (rounds >= 6)
| condition | target n | strict | loose | peer strict | peer loose |
|---|---:|---:|---:|---:|---:|
| 1 control | 20 | 0.000 | 0.000 | 0.000 | 0.000 |
| 10 free_rider | 20 | 0.000 | 0.000 | 0.000 | 0.000 |
| 11 all_caps | 20 | 0.000 | 0.000 | 0.000 | 0.000 |
| 12 partial_defector | 20 | 0.000 | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 20 | 1.000 | 1.000 | 0.000 | 0.000 |

## Contribution change (post rounds 6–max minus baseline round 5)
| condition | target Q/R change | mean peer change | target minus peer [bootstrap CI] |
|---|---:|---:|---:|
| 1 control | +0.00 | +0.00 | +0.00 [+0.00,+0.00] (n=1) |
| 10 free_rider | -5.00 | +0.00 | -5.00 [-5.00,-5.00] (n=1) |
| 11 all_caps | +0.00 | +0.00 | +0.00 [+0.00,+0.00] (n=1) |
| 12 partial_defector | -3.00 | +0.00 | -3.00 [-3.00,-3.00] (n=1) |
| 16 clean_rename | +0.00 | +0.00 | +0.00 [+0.00,+0.00] (n=1) |
