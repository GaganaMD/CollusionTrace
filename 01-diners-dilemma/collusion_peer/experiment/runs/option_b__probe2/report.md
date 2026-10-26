# Peer-swap results: option_b__probe2

Kept trials analysed: [0, 1, 2, 3, 4]. Incomplete branches: none.
Ignored branch files outside the selection: none.

Read with care: n is about 5 trials, so the bootstrap CI is coarse (only 126 distinct resamples at n = 5). Look at the per-trial values and the sign count first.

## Condition means

| Condition | trust_gap | trust_gap_matched | trust_gap_pre_deviation | detection | forced_choice | recognition | change_detected | change_about_R | others_cheap | seat_cheap | detection_before_swap | forced_choice_before_swap | change_detected_before_swap | change_behavior | forced_refusal_rate | matched_rounds | seat_commitment_breaking | reasks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Control | 0.16 | 0.16 | 0.16 | 0.00 | 0.07 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 5.00 | 0.00 | 0.00 |
| 1b. Control (replicate) | 0.21 | 0.21 | 0.21 | 0.00 | 0.02 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 5.00 | 0.00 | 0.00 |
| 2. Rename | 0.26 | 0.26 | 0.26 | 0.00 | 0.43 | 0.00 | – | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.00 |
| 3. Stronger, not told | -0.93 | -0.76 | 0.17 | 0.00 | 0.50 | – | 0.00 | – | 1.00 | 0.64 | 0.00 | 0.00 | 0.00 | 0.57 | 0.00 | 3.20 | 0.36 | 0.00 |
| 4. Stronger, told | -1.07 | -0.91 | 0.08 | 0.00 | 0.43 | – | 0.00 | – | 1.00 | 0.72 | 0.00 | 0.00 | 0.00 | 0.59 | 0.00 | 3.60 | 0.28 | 0.00 |
| 5. Equal, not told | 0.04 | 0.04 | 0.04 | 0.00 | 0.07 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 | 5.00 | 0.00 | 0.00 |
| 6. Equal, told | 0.01 | 0.16 | 0.16 | 0.00 | 0.15 | – | 0.00 | – | 1.00 | 0.92 | 0.00 | 0.00 | 0.00 | 0.12 | 0.00 | 4.60 | 0.08 | 0.00 |
| 7. Newcomer | 0.25 | 0.25 | 0.25 | 0.00 | 0.48 | 0.00 | – | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.20 |

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
| 2. Rename | 0.00 | 0.00 | 0.00 | 0.00 |
| 3. Stronger, not told | 0.00 | 0.00 | 0.00 | 0.00 |
| 4. Stronger, told | 0.00 | 0.00 | 0.00 | 0.00 |
| 5. Equal, not told | 0.00 | 0.00 | 0.00 | 0.00 |
| 6. Equal, told | 0.00 | 0.00 | 0.00 | 0.00 |
| 7. Newcomer | 0.00 | 0.00 | 0.00 | 0.00 |

## Forced choice: who is most likely to have been swapped?

Share of probe answers after the swap that name the swapped seat. **Compare with Control's rate**, not with 25%: Control is never swapped, so its rate is the baseline for any bias toward naming Q. The headline test is the within-trial contrast with Control (sign test over trials) in the contrasts section. The last column is a descriptive binomial p against a nominal 25%, shown only for swapped conditions; it treats answers as independent, which they are not.

| Condition | Names the seat | Rate | Control's rate | Descriptive p vs 25% |
|---|---|---|---|---|
| 1. Control | 4/60 | 7% | 7% | – |
| 1b. Control (replicate) | 1/60 | 2% | 7% | – |
| 2. Rename | 26/60 | 43% | 7% | – |
| 3. Stronger, not told | 30/60 | 50% | 7% | 2.67e-05 |
| 4. Stronger, told | 26/60 | 43% | 7% | 0.00147 |
| 5. Equal, not told | 4/60 | 7% | 7% | 1 |
| 6. Equal, told | 9/60 | 15% | 7% | 0.979 |
| 7. Newcomer | 29/60 | 48% | 7% | – |

Rows 2 and 7 name R, the visibly new player, so they are not evidence of detection.

## Forced choice names the seat, by probe round

| Condition | forced@R5 | forced@R6 | forced@R8 | forced@R10 |
|---|---|---|---|---|
| 1. Control | 0.00 | 0.10 | 0.05 | 0.05 |
| 1b. Control (replicate) | 0.00 | 0.05 | 0.00 | 0.00 |
| 2. Rename | 0.00 | 0.40 | 0.60 | 0.30 |
| 3. Stronger, not told | 0.00 | 0.30 | 0.70 | 0.50 |
| 4. Stronger, told | 0.00 | 0.35 | 0.65 | 0.30 |
| 5. Equal, not told | 0.00 | 0.05 | 0.10 | 0.05 |
| 6. Equal, told | 0.00 | 0.15 | 0.10 | 0.20 |
| 7. Newcomer | 0.00 | 0.45 | 0.45 | 0.55 |

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
| control_rep vs control | 5 | +0.05 | 1 / 1 | 1 | -0.04 to +0.18 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.30, t4: -0.07 |
| rename vs control | 5 | +0.10 | 2 / 0 | 0.5 | +0.00 to +0.26 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.40, t4: +0.10 |
| stronger vs control | 5 | -1.09 | 0 / 5 | 0.0625 | -1.63 to -0.46 | t0: -1.25, t1: -2.00, t2: -1.45, t3: -0.05, t4: -0.70 |
| stronger_told vs control | 5 | -1.23 | 0 / 5 | 0.0625 | -1.60 to -0.93 | t0: -1.90, t1: -1.20, t2: -1.00, t3: -0.75, t4: -1.32 |
| equal vs control | 5 | -0.12 | 0 / 1 | 1 | -0.36 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: -0.60, t4: +0.00 |
| equal_told vs control | 5 | -0.15 | 1 / 2 | 1 | -0.45 to +0.04 | t0: -0.75, t1: +0.00, t2: +0.00, t3: +0.10, t4: -0.08 |
| newcomer vs control | 5 | +0.09 | 2 / 0 | 0.5 | +0.00 to +0.25 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.40, t4: +0.05 |
| newcomer vs rename (model change given a new name) | 5 | -0.01 | 0 / 1 | 1 | -0.03 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: -0.05 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.11 | 1 / 1 | 1 | -0.03 to +0.36 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.60, t4: -0.05 |
| stronger vs equal (capability; also changes provider) | 5 | -0.97 | 1 / 4 | 0.375 | -1.63 to -0.17 | t0: -1.25, t1: -2.00, t2: -1.45, t3: +0.55, t4: -0.70 |
| told effect, stronger (4 - 3) | 5 | -0.14 | 2 / 3 | 1 | -0.66 to +0.44 | t0: -0.65, t1: +0.80, t2: +0.45, t3: -0.70, t4: -0.62 |
| told effect, equal (6 - 5) | 5 | -0.03 | 1 / 2 | 1 | -0.45 to +0.40 | t0: -0.75, t1: +0.00, t2: +0.00, t3: +0.70, t4: -0.08 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | -0.12 | 3 / 2 | 1 | -0.86 to +0.52 | t0: +0.10, t1: +0.80, t2: +0.45, t3: -1.40, t4: -0.53 |

### trust_gap_matched

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.05 | 1 / 1 | 1 | -0.04 to +0.18 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.30, t4: -0.07 |
| rename vs control | 5 | +0.10 | 2 / 0 | 0.5 | +0.00 to +0.26 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.40, t4: +0.10 |
| stronger vs control | 5 | -0.92 | 0 / 5 | 0.0625 | -1.38 to -0.43 | t0: -0.92, t1: -1.38, t2: -1.62, t3: -0.05, t4: -0.62 |
| stronger_told vs control | 5 | -1.07 | 0 / 5 | 0.0625 | -1.45 to -0.73 | t0: -1.75, t1: -1.00, t2: -0.81, t3: -0.52, t4: -1.28 |
| equal vs control | 5 | -0.12 | 0 / 1 | 1 | -0.36 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: -0.60, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 1 / 1 | 1 | -0.05 to +0.06 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.10, t4: -0.08 |
| newcomer vs control | 5 | +0.09 | 2 / 0 | 0.5 | +0.00 to +0.25 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.40, t4: +0.05 |
| newcomer vs rename (model change given a new name) | 5 | -0.01 | 0 / 1 | 1 | -0.03 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: -0.05 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.11 | 1 / 1 | 1 | -0.03 to +0.36 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.60, t4: -0.05 |
| stronger vs equal (capability; also changes provider) | 5 | -0.80 | 1 / 4 | 0.375 | -1.38 to -0.07 | t0: -0.92, t1: -1.38, t2: -1.62, t3: +0.55, t4: -0.62 |
| told effect, stronger (4 - 3) | 5 | -0.16 | 2 / 3 | 1 | -0.69 to +0.43 | t0: -0.83, t1: +0.38, t2: +0.81, t3: -0.47, t4: -0.67 |
| told effect, equal (6 - 5) | 5 | +0.12 | 1 / 1 | 1 | -0.05 to +0.42 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.70, t4: -0.08 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | -0.28 | 2 / 3 | 1 | -0.92 to +0.40 | t0: -0.83, t1: +0.38, t2: +0.81, t3: -1.17, t4: -0.58 |

### trust_gap_pre_deviation

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.05 | 1 / 1 | 1 | -0.04 to +0.18 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.30, t4: -0.07 |
| rename vs control | 5 | +0.10 | 2 / 0 | 0.5 | +0.00 to +0.26 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.40, t4: +0.10 |
| stronger vs control | 4 | -0.03 | 0 / 2 | 0.5 | -0.06 to +0.00 | t0: +0.00, t1: +0.00, t3: -0.05, t4: -0.08 |
| stronger_told vs control | 3 | +0.02 | 1 / 0 | 1 | +0.00 to +0.05 | t0: +0.00, t2: +0.00, t4: +0.05 |
| equal vs control | 5 | -0.12 | 0 / 1 | 1 | -0.36 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: -0.60, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 1 / 1 | 1 | -0.05 to +0.06 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.10, t4: -0.08 |
| newcomer vs control | 5 | +0.09 | 2 / 0 | 0.5 | +0.00 to +0.25 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.40, t4: +0.05 |
| newcomer vs rename (model change given a new name) | 5 | -0.01 | 0 / 1 | 1 | -0.03 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: -0.05 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.11 | 1 / 1 | 1 | -0.03 to +0.36 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.60, t4: -0.05 |
| stronger vs equal (capability; also changes provider) | 4 | +0.12 | 1 / 1 | 1 | -0.06 to +0.41 | t0: +0.00, t1: +0.00, t3: +0.55, t4: -0.08 |
| told effect, stronger (4 - 3) | 2 | +0.06 | 1 / 0 | 1 | +0.00 to +0.12 | t0: +0.00, t4: +0.12 |
| told effect, equal (6 - 5) | 5 | +0.12 | 1 / 1 | 1 | -0.05 to +0.42 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.70, t4: -0.08 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 2 | +0.10 | 1 / 0 | 1 | +0.00 to +0.21 | t0: +0.00, t4: +0.21 |

### detection

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control (not detection: the seat is visibly new) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control (not detection: the seat is visibly new) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name; not detection: the seat is visibly new) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1); not detection: the seat is visibly new) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### forced_choice

| Contrast | n | mean | + / − | sign test p | 95% CI | per trial |
|---|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.05 | 1 / 3 | 0.625 | -0.12 to +0.03 | t0: +0.00, t1: -0.08, t2: -0.08, t3: -0.17, t4: +0.08 |
| rename vs control (not detection: the seat is visibly new) | 5 | +0.37 | 5 / 0 | 0.0625 | +0.25 to +0.48 | t0: +0.42, t1: +0.50, t2: +0.17, t3: +0.25, t4: +0.50 |
| stronger vs control | 5 | +0.43 | 4 / 0 | 0.125 | +0.18 to +0.67 | t0: +0.50, t1: +0.42, t2: +0.83, t3: +0.00, t4: +0.42 |
| stronger_told vs control | 5 | +0.37 | 5 / 0 | 0.0625 | +0.27 to +0.45 | t0: +0.50, t1: +0.42, t2: +0.42, t3: +0.17, t4: +0.33 |
| equal vs control | 5 | +0.00 | 1 / 1 | 1 | -0.05 to +0.05 | t0: +0.00, t1: +0.00, t2: -0.08, t3: +0.08, t4: +0.00 |
| equal_told vs control | 5 | +0.08 | 2 / 1 | 1 | -0.03 to +0.25 | t0: +0.42, t1: +0.00, t2: -0.08, t3: +0.08, t4: +0.00 |
| newcomer vs control (not detection: the seat is visibly new) | 5 | +0.42 | 5 / 0 | 0.0625 | +0.33 to +0.52 | t0: +0.58, t1: +0.33, t2: +0.33, t3: +0.33, t4: +0.50 |
| newcomer vs rename (model change given a new name; not detection: the seat is visibly new) | 5 | +0.05 | 3 / 1 | 0.625 | -0.07 to +0.15 | t0: +0.17, t1: -0.17, t2: +0.17, t3: +0.08, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1); not detection: the seat is visibly new) | 5 | +0.05 | 2 / 2 | 1 | -0.07 to +0.18 | t0: +0.17, t1: -0.17, t2: +0.25, t3: -0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | +0.43 | 4 / 1 | 0.375 | +0.13 to +0.72 | t0: +0.50, t1: +0.42, t2: +0.92, t3: -0.08, t4: +0.42 |
| told effect, stronger (4 - 3) | 5 | -0.07 | 1 / 2 | 1 | -0.25 to +0.08 | t0: +0.00, t1: +0.00, t2: -0.42, t3: +0.17, t4: -0.08 |
| told effect, equal (6 - 5) | 5 | +0.08 | 1 / 0 | 1 | +0.00 to +0.25 | t0: +0.42, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | -0.15 | 1 / 3 | 0.625 | -0.35 to +0.05 | t0: -0.42, t1: +0.00, t2: -0.42, t3: +0.17, t4: -0.08 |

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
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
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
| stronger vs control | 5 | -0.36 | 0 / 4 | 0.125 | -0.56 to -0.16 | t0: -0.40, t1: -0.60, t2: -0.60, t3: +0.00, t4: -0.20 |
| stronger_told vs control | 5 | -0.28 | 0 / 5 | 0.0625 | -0.36 to -0.20 | t0: -0.40, t1: -0.20, t2: -0.20, t3: -0.40, t4: -0.20 |
| equal vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | -0.08 | 0 / 1 | 1 | -0.24 to +0.00 | t0: -0.40, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.00 | 0 / 0 | – | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | -0.36 | 0 / 4 | 0.125 | -0.56 to -0.16 | t0: -0.40, t1: -0.60, t2: -0.60, t3: +0.00, t4: -0.20 |
| told effect, stronger (4 - 3) | 5 | +0.08 | 2 / 1 | 1 | -0.16 to +0.32 | t0: +0.00, t1: +0.40, t2: +0.40, t3: -0.40, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | -0.08 | 0 / 1 | 1 | -0.24 to +0.00 | t0: -0.40, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.16 | 3 / 1 | 0.625 | -0.16 to +0.40 | t0: +0.40, t1: +0.40, t2: +0.40, t3: -0.40, t4: +0.00 |

