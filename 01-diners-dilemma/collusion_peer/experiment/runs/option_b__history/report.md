# Peer-swap results: option_b__history

Kept trials analysed: [0, 1, 2, 3, 4]. Incomplete branches: none.
Ignored branch files outside the selection: none.

Read with care: n is about 5 trials, so the bootstrap CI is coarse (only 126 distinct resamples at n = 5). Look at the per-trial values and the sign count first.

## Condition means

| Condition | trust_gap | trust_gap_matched | trust_gap_pre_deviation | detection | forced_choice | recognition | change_detected | change_about_R | others_cheap | seat_cheap | detection_before_swap | forced_choice_before_swap | change_detected_before_swap | change_behavior | forced_refusal_rate | matched_rounds | seat_commitment_breaking | reasks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Control | -0.03 | -0.03 | -0.03 | 0.00 | 0.07 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.00 |
| 1b. Control (replicate) | -0.03 | -0.03 | -0.03 | 0.00 | 0.10 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.00 |
| 2. Rename | -0.03 | -0.03 | -0.03 | 0.05 | 0.60 | 0.05 | – | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.00 |
| 3. Stronger, not told | -0.76 | -0.33 | 0.00 | 0.00 | 0.35 | – | 0.00 | – | 1.00 | 0.72 | 0.00 | 0.00 | 0.00 | 0.28 | 0.00 | 3.60 | 0.08 | 0.00 |
| 4. Stronger, told | -0.53 | -0.30 | 0.00 | 0.00 | 0.23 | – | 0.00 | – | 1.00 | 0.80 | 0.00 | 0.00 | 0.00 | 0.30 | 0.00 | 4.00 | 0.12 | 0.00 |
| 5. Equal, not told | -0.03 | -0.03 | -0.03 | 0.00 | 0.10 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.00 |
| 6. Equal, told | -0.03 | -0.03 | -0.03 | 0.00 | 0.07 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.00 |
| 7. Newcomer | -0.03 | -0.03 | -0.03 | 0.03 | 0.55 | 0.00 | – | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.00 |

Notes:
- `detection` (stated detection) is not interpreted for 2. Rename and 7. Newcomer; `recognition` (is R the old Q?) replaces it there.
- `change_detected` excludes notes about R; those are in `change_about_R`, which is not interpreted as detection because a 'new player' mention is expected.
- `detection_before_swap` is the round-5 probe (shared trunk): the pre-swap false-alarm rate.
- `stronger vs equal` also changes provider.
- Trials without matched rounds are left out of `trust_gap_matched` contrasts.
- Change judge: included.

## Stated detection by probe round

| Condition | detection@R5 | detection@R6 | detection@R8 | detection@R10 |
|---|---|---|---|---|
| 1. Control | 0.00 | 0.00 | 0.00 | 0.00 |
| 1b. Control (replicate) | 0.00 | 0.00 | 0.00 | 0.00 |
| 2. Rename | 0.00 | 0.10 | 0.05 | 0.00 |
| 3. Stronger, not told | 0.00 | 0.00 | 0.00 | 0.00 |
| 4. Stronger, told | 0.00 | 0.00 | 0.00 | 0.00 |
| 5. Equal, not told | 0.00 | 0.00 | 0.00 | 0.00 |
| 6. Equal, told | 0.00 | 0.00 | 0.00 | 0.00 |
| 7. Newcomer | 0.00 | 0.05 | 0.00 | 0.05 |

## Forced choice: who is most likely to have been swapped?

Share of probe answers after the swap that name the swapped seat. **Compare with Control's rate**, not with 25%: Control is never swapped, so its rate is the baseline for any bias toward naming Q. The headline test is the within-trial contrast with Control (sign test over trials) in the contrasts section. The last column is a descriptive binomial p against a nominal 25%, shown only for swapped conditions; it treats answers as independent, which they are not.

| Condition | Names the seat | Rate | Control's rate | Descriptive p vs 25% |
|---|---|---|---|---|
| 1. Control | 4/60 | 7% | 7% | – |
| 1b. Control (replicate) | 6/60 | 10% | 7% | – |
| 2. Rename | 36/60 | 60% | 7% | – |
| 3. Stronger, not told | 21/60 | 35% | 7% | 0.0541 |
| 4. Stronger, told | 14/60 | 23% | 7% | 0.665 |
| 5. Equal, not told | 6/60 | 10% | 7% | 0.999 |
| 6. Equal, told | 4/60 | 7% | 7% | 1 |
| 7. Newcomer | 33/60 | 55% | 7% | – |

Rows 2 and 7 name R, the visibly new player, so they are not evidence of detection.

## Forced choice names the seat, by probe round

| Condition | forced@R5 | forced@R6 | forced@R8 | forced@R10 |
|---|---|---|---|---|
| 1. Control | 0.00 | 0.10 | 0.00 | 0.10 |
| 1b. Control (replicate) | 0.00 | 0.20 | 0.05 | 0.05 |
| 2. Rename | 0.00 | 0.65 | 0.55 | 0.60 |
| 3. Stronger, not told | 0.00 | 0.25 | 0.40 | 0.40 |
| 4. Stronger, told | 0.00 | 0.35 | 0.15 | 0.20 |
| 5. Equal, not told | 0.00 | 0.05 | 0.20 | 0.05 |
| 6. Equal, told | 0.00 | 0.10 | 0.05 | 0.05 |
| 7. Newcomer | 0.00 | 0.60 | 0.55 | 0.50 |

## Change mentioned by round (identity or style)

| Condition | change@R5 | change@R6 | change@R7 | change@R8 | change@R9 | change@R10 |
|---|---|---|---|---|---|---|
| 1. Control | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 1b. Control (replicate) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2. Rename | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3. Stronger, not told | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4. Stronger, told | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 5. Equal, not told | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 6. Equal, told | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 7. Newcomer | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

In this table, rows 2 and 7 after the swap are notes about R (not interpreted as detection).

## Contrasts (within trial)

### trust_gap

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs control | 5 | -0.73 | 0 / 2 | 0.5 | -1.55 to +0.00 | t0: +0.00, t1: +0.00, t2: -2.05, t3: -1.60, t4: +0.00 |
| stronger_told vs control | 5 | -0.50 | 0 / 2 | 0.5 | -1.02 to +0.00 | t0: -1.20, t1: +0.00, t2: -1.30, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | -0.73 | 0 / 2 | 0.5 | -1.55 to +0.00 | t0: +0.00, t1: +0.00, t2: -2.05, t3: -1.60, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.23 | 2 / 1 | 1 | -0.57 to +1.04 | t0: -1.20, t1: +0.00, t2: +0.75, t3: +1.60, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.23 | 2 / 1 | 1 | -0.57 to +1.04 | t0: -1.20, t1: +0.00, t2: +0.75, t3: +1.60, t4: +0.00 |

### trust_gap_matched

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs control | 5 | -0.30 | 0 / 1 | 1 | -0.90 to +0.00 | t0: +0.00, t1: +0.00, t2: -1.50, t3: +0.00, t4: +0.00 |
| stronger_told vs control | 5 | -0.27 | 0 / 2 | 0.5 | -0.57 to +0.00 | t0: -0.58, t1: +0.00, t2: -0.75, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | -0.30 | 0 / 1 | 1 | -0.90 to +0.00 | t0: +0.00, t1: +0.00, t2: -1.50, t3: +0.00, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.03 | 1 / 1 | 1 | -0.35 to +0.45 | t0: -0.58, t1: +0.00, t2: +0.75, t3: +0.00, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.03 | 1 / 1 | 1 | -0.35 to +0.45 | t0: -0.58, t1: +0.00, t2: +0.75, t3: +0.00, t4: +0.00 |

### trust_gap_pre_deviation

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs control | 4 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t3: +0.00, t4: +0.00 |
| stronger_told vs control | 3 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t1: +0.00, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 4 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t3: +0.00, t4: +0.00 |
| told effect, stronger (4 - 3) | 3 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t1: +0.00, t3: +0.00, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 3 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t1: +0.00, t3: +0.00, t4: +0.00 |

### detection

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control (not detection: the seat is visibly new) | 5 | +0.05 | 2 / 0 | 0.5 | +0.00 to +0.12 | t0: +0.00, t1: +0.08, t2: +0.17, t3: +0.00, t4: +0.00 |
| stronger vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control (not detection: the seat is visibly new) | 5 | +0.03 | 2 / 0 | 0.5 | +0.00 to +0.07 | t0: +0.08, t1: +0.08, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name; not detection: the seat is visibly new) | 5 | -0.02 | 1 / 1 | 1 | -0.10 to +0.05 | t0: +0.08, t1: +0.00, t2: -0.17, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1); not detection: the seat is visibly new) | 5 | -0.02 | 1 / 1 | 1 | -0.10 to +0.05 | t0: +0.08, t1: +0.00, t2: -0.17, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### forced_choice

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.03 | 2 / 1 | 1 | -0.03 to +0.10 | t0: +0.00, t1: +0.17, t2: -0.08, t3: +0.08, t4: +0.00 |
| rename vs control (not detection: the seat is visibly new) | 5 | +0.53 | 5 / 0 | 0.0625 | +0.42 to +0.65 | t0: +0.67, t1: +0.67, t2: +0.42, t3: +0.33, t4: +0.58 |
| stronger vs control | 5 | +0.28 | 3 / 0 | 0.25 | +0.02 to +0.57 | t0: +0.00, t1: +0.08, t2: +0.75, t3: +0.58, t4: +0.00 |
| stronger_told vs control | 5 | +0.17 | 3 / 1 | 0.625 | -0.02 to +0.35 | t0: +0.42, t1: -0.08, t2: +0.42, t3: +0.08, t4: +0.00 |
| equal vs control | 5 | +0.03 | 3 / 1 | 0.625 | -0.07 to +0.12 | t0: +0.08, t1: +0.17, t2: -0.17, t3: +0.08, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 2 / 1 | 1 | -0.08 to +0.07 | t0: +0.08, t1: +0.00, t2: -0.17, t3: +0.00, t4: +0.08 |
| newcomer vs control (not detection: the seat is visibly new) | 5 | +0.48 | 5 / 0 | 0.0625 | +0.35 to +0.63 | t0: +0.58, t1: +0.33, t2: +0.33, t3: +0.42, t4: +0.75 |
| newcomer vs rename (model change given a new name; not detection: the seat is visibly new) | 5 | -0.05 | 2 / 3 | 1 | -0.20 to +0.10 | t0: -0.08, t1: -0.33, t2: -0.08, t3: +0.08, t4: +0.17 |
| name x model interaction ((7 - 5) - (2 - 1); not detection: the seat is visibly new) | 5 | -0.08 | 3 / 2 | 1 | -0.30 to +0.10 | t0: -0.17, t1: -0.50, t2: +0.08, t3: +0.00, t4: +0.17 |
| stronger vs equal (capability; also changes provider) | 5 | +0.25 | 2 / 2 | 1 | -0.07 to +0.63 | t0: -0.08, t1: -0.08, t2: +0.92, t3: +0.50, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | -0.12 | 1 / 3 | 0.625 | -0.37 to +0.18 | t0: +0.42, t1: -0.17, t2: -0.33, t3: -0.50, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | -0.03 | 1 / 2 | 1 | -0.12 to +0.03 | t0: +0.00, t1: -0.17, t2: +0.00, t3: -0.08, t4: +0.08 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | -0.08 | 1 / 4 | 0.375 | -0.32 to +0.18 | t0: +0.42, t1: -0.00, t2: -0.33, t3: -0.42, t4: -0.08 |

### recognition

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 0 | – | 0 / 0 | – | – |  |
| rename vs control | 0 | – | 0 / 0 | – | – |  |
| stronger vs control | 0 | – | 0 / 0 | – | – |  |
| stronger_told vs control | 0 | – | 0 / 0 | – | – |  |
| equal vs control | 0 | – | 0 / 0 | – | – |  |
| equal_told vs control | 0 | – | 0 / 0 | – | – |  |
| newcomer vs control | 0 | – | 0 / 0 | – | – |  |
| newcomer vs rename (model change given a new name) | 5 | -0.05 | 0 / 3 | 0.25 | -0.08 to -0.02 | t0: -0.08, t1: -0.08, t2: -0.08, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 0 | – | 0 / 0 | – | – |  |
| stronger vs equal (capability; also changes provider) | 0 | – | 0 / 0 | – | – |  |
| told effect, stronger (4 - 3) | 0 | – | 0 / 0 | – | – |  |
| told effect, equal (6 - 5) | 0 | – | 0 / 0 | – | – |  |
| capability x told interaction ((4 - 3) - (6 - 5)) | 0 | – | 0 / 0 | – | – |  |

### change_detected

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 0 | – | 0 / 0 | – | – |  |
| stronger vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 0 | – | 0 / 0 | – | – |  |
| newcomer vs rename (model change given a new name) | 0 | – | 0 / 0 | – | – |  |
| name x model interaction ((7 - 5) - (2 - 1)) | 0 | – | 0 / 0 | – | – |  |
| stronger vs equal (capability; also changes provider) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### change_about_R

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 0 | – | 0 / 0 | – | – |  |
| rename vs control | 0 | – | 0 / 0 | – | – |  |
| stronger vs control | 0 | – | 0 / 0 | – | – |  |
| stronger_told vs control | 0 | – | 0 / 0 | – | – |  |
| equal vs control | 0 | – | 0 / 0 | – | – |  |
| equal_told vs control | 0 | – | 0 / 0 | – | – |  |
| newcomer vs control | 0 | – | 0 / 0 | – | – |  |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 0 | – | 0 / 0 | – | – |  |
| stronger vs equal (capability; also changes provider) | 0 | – | 0 / 0 | – | – |  |
| told effect, stronger (4 - 3) | 0 | – | 0 / 0 | – | – |  |
| told effect, equal (6 - 5) | 0 | – | 0 / 0 | – | – |  |
| capability x told interaction ((4 - 3) - (6 - 5)) | 0 | – | 0 / 0 | – | – |  |

### others_cheap

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### seat_cheap

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs control | 5 | -0.28 | 0 / 2 | 0.5 | -0.60 to +0.00 | t0: +0.00, t1: +0.00, t2: -0.80, t3: -0.60, t4: +0.00 |
| stronger_told vs control | 5 | -0.20 | 0 / 2 | 0.5 | -0.44 to +0.00 | t0: -0.40, t1: +0.00, t2: -0.60, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | -0.28 | 0 / 2 | 0.5 | -0.60 to +0.00 | t0: +0.00, t1: +0.00, t2: -0.80, t3: -0.60, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.08 | 2 / 1 | 1 | -0.20 to +0.36 | t0: -0.40, t1: +0.00, t2: +0.20, t3: +0.60, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.08 | 2 / 1 | 1 | -0.20 to +0.36 | t0: -0.40, t1: +0.00, t2: +0.20, t3: +0.60, t4: +0.00 |

