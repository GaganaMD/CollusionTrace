# Peer-swap results: llama_maverick__memlog3_warn1_bonus__r20

Kept trials analysed: [0, 1, 2, 3, 4]. Incomplete branches: none.
Ignored branch files outside the selection: none.

Read with care: n is about 5 trials, so the bootstrap CI is coarse (only 126 distinct resamples at n = 5). Look at the per-trial values and the sign count first.

## Condition means

| Condition | trust_gap | trust_gap_matched | trust_gap_pre_deviation | detection | forced_choice | recognition | change_detected | change_about_R | others_cheap | seat_cheap | detection_before_swap | forced_choice_before_swap | change_detected_before_swap | change_behavior | forced_refusal_rate | matched_rounds | seat_commitment_breaking | reasks | accused_seat | false_accusations | first_accusation_round | seat_accusations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Control | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | – | 0.03 | – | 1.00 | 1.00 | 0.00 | 0.30 | 0.10 | 0.00 | 0.00 | 2.20 | 0.80 | 0.00 | 0.00 | 3.60 | – | 2.00 |
| 5. Equal, not told | 2.21 | 2.21 | 2.21 | 0.47 | 0.40 | – | 0.19 | – | 1.00 | 1.00 | 0.00 | 0.30 | 0.10 | 0.22 | 0.00 | 11.00 | 0.00 | 0.00 | 0.00 | 3.60 | – | 2.00 |

Notes:
- `detection` (stated detection) is not interpreted for 2. Rename and 7. Newcomer; `recognition` (is R the old Q?) replaces it there.
- `change_detected` excludes notes about R; those are in `change_about_R`, which is not interpreted as detection because a 'new player' mention is expected.
- `detection_before_swap` is the round-9 probe (shared trunk): the pre-swap false-alarm rate.
- `stronger vs equal` also changes provider.
- Trials without matched rounds are left out of `trust_gap_matched` contrasts.
- Change judge: included.
- Accusations (detection bonus) count J and T only; the seat's own are in `seat_accusations`. `first_accusation_round` is the first round in which J or T accused the seat; in Control every such accusation is wrong.

## Stated detection by probe round

| Condition | detection@R9 | detection@R10 | detection@R15 | detection@R20 |
|---|---|---|---|---|
| 1. Control | 0.00 | 0.00 | 0.00 | 0.00 |
| 5. Equal, not told | 0.00 | 0.50 | 0.40 | 0.50 |

## Forced choice: who is most likely to have been swapped?

Share of probe answers after the swap that name the swapped seat. **Compare with Control's rate**, not with 50%: Control is never swapped, so its rate is the baseline for any bias toward naming Q. The headline test is the within-trial contrast with Control (sign test over trials) in the contrasts section. The last column is a descriptive binomial p against a nominal 50%, shown only for swapped conditions; it treats answers as independent, which they are not.

| Condition | Names the seat | Rate | Control's rate | Descriptive p vs 50% |
|---|---|---|---|---|
| 1. Control | 6/30 | 20% | 20% | – |
| 5. Equal, not told | 12/30 | 40% | 20% | 0.9 |

Rows 2 and 7 name R, the visibly new player, so they are not evidence of detection.

## Forced choice names the seat, by probe round

| Condition | forced@R9 | forced@R10 | forced@R15 | forced@R20 |
|---|---|---|---|---|
| 1. Control | 0.30 | 0.20 | 0.20 | 0.20 |
| 5. Equal, not told | 0.30 | 0.60 | 0.30 | 0.30 |

## Change mentioned by round (identity or style)

| Condition | change@R9 | change@R10 | change@R11 | change@R12 | change@R13 | change@R14 | change@R15 | change@R16 | change@R17 | change@R18 | change@R19 | change@R20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Control | 0.10 | 0.10 | 0.10 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 5. Equal, not told | 0.10 | 0.60 | 0.50 | 0.50 | 0.40 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

In this table, rows 2 and 7 after the swap are notes about R (not interpreted as detection).

## Contrasts (within trial)

### trust_gap

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +2.21 | 4 / 0 | 0.125 | +1.06 to +3.03 | t0: +2.77, t1: +2.09, t2: +3.23, t3: +0.00, t4: +2.95 |

### trust_gap_matched

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 1 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t3: +0.00 |

### trust_gap_pre_deviation

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 1 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t3: +0.00 |

### detection

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +0.47 | 4 / 0 | 0.125 | +0.10 to +0.83 | t0: +1.00, t1: +0.00, t2: +1.00, t3: +0.17, t4: +0.17 |

### forced_choice

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +0.20 | 3 / 1 | 0.625 | -0.03 to +0.47 | t0: +0.33, t1: -0.17, t2: +0.67, t3: +0.00, t4: +0.17 |

### recognition

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 0 | – | 0 / 0 | – | – |  |

### change_detected

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +0.16 | 4 / 0 | 0.125 | +0.03 to +0.30 | t0: +0.36, t1: +0.05, t2: +0.36, t3: +0.00, t4: +0.05 |

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

### accused_seat

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### false_accusations

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

