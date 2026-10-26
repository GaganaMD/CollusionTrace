# Peer-swap results: llama_maverick__memlog3_warn1__r20

Kept trials analysed: [0, 1, 2, 3, 4]. Incomplete branches: none.
Ignored branch files outside the selection: none.

Read with care: n is about 5 trials, so the bootstrap CI is coarse (only 126 distinct resamples at n = 5). Look at the per-trial values and the sign count first.

## Condition means

| Condition | trust_gap | trust_gap_matched | trust_gap_pre_deviation | detection | forced_choice | recognition | change_detected | change_about_R | others_cheap | seat_cheap | detection_before_swap | forced_choice_before_swap | change_detected_before_swap | change_behavior | forced_refusal_rate | matched_rounds | seat_commitment_breaking | reasks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Control | 0.00 | 0.00 | 0.00 | 0.00 | 0.43 | – | 0.00 | – | 0.90 | 1.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 2.20 | 0.80 | 0.00 |
| 5. Equal, not told | 2.17 | 2.17 | 2.17 | 0.10 | 0.30 | – | 0.00 | – | 0.90 | 1.00 | 0.00 | 0.50 | 0.00 | 0.23 | 0.00 | 11.00 | 0.00 | 0.00 |

Notes:
- `detection` (stated detection) is not interpreted for 2. Rename and 7. Newcomer; `recognition` (is R the old Q?) replaces it there.
- `change_detected` excludes notes about R; those are in `change_about_R`, which is not interpreted as detection because a 'new player' mention is expected.
- `detection_before_swap` is the round-9 probe (shared trunk): the pre-swap false-alarm rate.
- `stronger vs equal` also changes provider.
- Trials without matched rounds are left out of `trust_gap_matched` contrasts.
- Change judge: included.

## Stated detection by probe round

| Condition | detection@R9 | detection@R10 | detection@R15 | detection@R20 |
|---|---|---|---|---|
| 1. Control | 0.00 | 0.00 | 0.00 | 0.00 |
| 5. Equal, not told | 0.00 | 0.30 | 0.00 | 0.00 |

## Forced choice: who is most likely to have been swapped?

Share of probe answers after the swap that name the swapped seat. **Compare with Control's rate**, not with 50%: Control is never swapped, so its rate is the baseline for any bias toward naming Q. The headline test is the within-trial contrast with Control (sign test over trials) in the contrasts section. The last column is a descriptive binomial p against a nominal 50%, shown only for swapped conditions; it treats answers as independent, which they are not.

| Condition | Names the seat | Rate | Control's rate | Descriptive p vs 50% |
|---|---|---|---|---|
| 1. Control | 13/30 | 43% | 43% | – |
| 5. Equal, not told | 9/30 | 30% | 43% | 0.992 |

Rows 2 and 7 name R, the visibly new player, so they are not evidence of detection.

## Forced choice names the seat, by probe round

| Condition | forced@R9 | forced@R10 | forced@R15 | forced@R20 |
|---|---|---|---|---|
| 1. Control | 0.50 | 0.40 | 0.40 | 0.50 |
| 5. Equal, not told | 0.50 | 0.70 | 0.10 | 0.10 |

## Change mentioned by round (identity or style)

| Condition | change@R9 | change@R10 | change@R11 | change@R12 | change@R13 | change@R14 | change@R15 | change@R16 | change@R17 | change@R18 | change@R19 | change@R20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Control | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 5. Equal, not told | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

In this table, rows 2 and 7 after the swap are notes about R (not interpreted as detection).

## Contrasts (within trial)

### trust_gap

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +2.17 | 4 / 0 | 0.125 | +1.04 to +3.26 | t0: +0.00, t1: +3.00, t2: +3.82, t3: +2.18, t4: +1.86 |

### trust_gap_matched

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 1 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00 |

### trust_gap_pre_deviation

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 1 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00 |

### detection

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +0.10 | 3 / 0 | 0.25 | +0.03 to +0.17 | t0: +0.00, t1: +0.00, t2: +0.17, t3: +0.17, t4: +0.17 |

### forced_choice

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | -0.13 | 1 / 3 | 0.625 | -0.30 to +0.03 | t0: +0.00, t1: -0.33, t2: +0.17, t3: -0.33, t4: -0.17 |

### recognition

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 0 | – | 0 / 0 | – | – |  |

### change_detected

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### change_about_R

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 0 | – | 0 / 0 | – | – |  |

### others_cheap

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### seat_cheap

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

