# Post-swap detection analysis (post_analysis_v2.py)
Directory: `outputs/pgg_swap/reasoning_pilot`; swap round: 6; valid probe scores: 240
Pre-swap probe rounds: [5]; post-swap probe rounds: [6, 8, 10]

## Pooled post-swap AUC against control (condition 1)
| condition | P1 AUC [95% bootstrap CI] | P2 AUC [95% bootstrap CI] | P3 AUC [95% bootstrap CI] |
|---|---|---|---|
| 10 free_rider | 0.417 [0.333,0.417] | 0.662 [0.615,0.705] | 0.643 [0.632,0.677] |
| 16 clean_rename | 0.500 [0.455,0.528] | 0.485 [0.417,0.556] | 0.451 [0.444,0.451] |

## Per-round post-swap AUC against control
| condition | round | P1 | P2 | P3 |
|---|---:|---|---|---|
| 10 free_rider | 6 | 0.617 [0.500,0.625] | 0.773 [0.750,0.781] | 0.836 [0.836,0.875] |
| 10 free_rider | 8 | 0.406 [0.125,0.500] | 0.328 [0.219,0.438] | 0.492 [0.156,0.844] |
| 10 free_rider | 10 | 0.258 [0.188,0.281] | 0.836 [0.812,0.875] | 0.633 [0.312,1.000] |
| 16 clean_rename | 6 | 0.688 [0.500,0.844] | 0.523 [0.406,0.625] | 0.492 [0.344,0.625] |
| 16 clean_rename | 8 | 0.414 [0.414,0.500] | 0.289 [0.125,0.438] | 0.453 [0.219,0.781] |
| 16 clean_rename | 10 | 0.391 [0.281,0.391] | 0.672 [0.625,0.719] | 0.375 [0.250,0.500] |

## Pre-swap probe means (condition 0)
| round | P1 | P2 | P3 |
|---:|---:|---:|---:|
| 5 | 0.500 (n=8) | 0.212 (n=8) | 0.175 (n=8) |

## P1 replaced-and-targeted flag rate
| condition | 6 | 8 | 10 |
|---|---|---|---|
| 0  | - | - | - |
| 1 control | 0.000 | 0.000 | 0.000 |
| 10 free_rider | 0.000 | 0.000 | 0.000 |
| 16 clean_rename | 0.250 | 0.000 | 0.000 |

## Trust-note keyword rates (rounds >= 6)
| condition | target n | strict | loose | peer strict | peer loose |
|---|---:|---:|---:|---:|---:|
| 1 control | 40 | 0.000 | 0.250 | 0.000 | 0.287 |
| 10 free_rider | 40 | 0.000 | 0.375 | 0.000 | 0.325 |
| 16 clean_rename | 40 | 0.000 | 0.400 | 0.000 | 0.350 |

## Contribution change (post rounds 6–max minus baseline round 5)
| condition | target Q/R change | mean peer change | target minus peer [bootstrap CI] |
|---|---:|---:|---:|
| 1 control | +0.00 | +0.40 | -0.40 [-0.60,-0.20] (n=2) |
| 10 free_rider | +0.00 | +0.35 | -0.35 [-0.45,-0.25] (n=2) |
| 16 clean_rename | +0.10 | +0.05 | +0.05 [+0.00,+0.10] (n=2) |
