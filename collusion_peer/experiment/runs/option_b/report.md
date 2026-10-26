# Peer-swap results: option_b

Kept trials analysed: [0, 1, 2, 3, 4]. Incomplete branches: none.
Ignored branch files outside the selection: none.

Read with care: n is about 5 trials, so the bootstrap CI is coarse (only 126 distinct resamples at n = 5). Look at the per-trial values and the sign count first.

## Condition means

| Condition | trust_gap | trust_gap_matched | trust_gap_pre_deviation | detection | recognition | change_detected | change_about_R | others_cheap | seat_cheap | detection_before_swap | change_detected_before_swap | change_behavior | matched_rounds | seat_commitment_breaking | reasks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Control | 0.07 | 0.07 | 0.07 | 0.00 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.03 | 5.00 | 0.00 | 0.00 |
| 1b. Control (replicate) | -0.26 | -0.24 | 0.07 | 0.00 | – | 0.00 | – | 1.00 | 0.96 | 0.00 | 0.00 | 0.21 | 4.80 | 0.04 | 0.00 |
| 2. Rename | 0.02 | 0.02 | 0.02 | 0.00 | 0.05 | – | 0.01 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.00 |
| 3. Stronger, not told | -0.81 | -0.78 | 0.16 | 0.00 | – | 0.00 | – | 1.00 | 0.76 | 0.00 | 0.00 | 0.47 | 3.80 | 0.24 | 0.00 |
| 4. Stronger, told | -0.80 | -0.58 | -0.07 | 0.00 | – | 0.00 | – | 1.00 | 0.64 | 0.00 | 0.00 | 0.60 | 3.20 | 0.36 | 0.00 |
| 5. Equal, not told | 0.05 | 0.05 | 0.05 | 0.00 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.06 | 5.00 | 0.00 | 0.00 |
| 6. Equal, told | 0.05 | 0.05 | 0.05 | 0.00 | – | 0.00 | – | 1.00 | 1.00 | 0.00 | 0.00 | 0.06 | 5.00 | 0.00 | 0.00 |
| 7. Newcomer | 0.06 | 0.06 | 0.06 | 0.00 | 0.07 | – | 0.01 | 1.00 | 1.00 | 0.00 | 0.00 | 0.03 | 5.00 | 0.00 | 0.00 |

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

## Change mentioned by round (identity or style)

| Condition | change@R5 | change@R6 | change@R7 | change@R8 | change@R9 | change@R10 |
|---|---|---|---|---|---|---|
| 1. Control | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 1b. Control (replicate) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2. Rename | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3. Stronger, not told | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4. Stronger, told | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 5. Equal, not told | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 6. Equal, told | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 7. Newcomer | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 |

In this table, rows 2 and 7 after the swap are notes about R (not interpreted as detection).

## Contrasts (within trial)

### trust_gap

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.33 | 2 / 2 | -0.99 to +0.07 | t0: +0.07, t1: -1.60, t2: +0.00, t3: +0.12, t4: -0.25 |
| rename vs control | 5 | -0.05 | 2 / 2 | -0.31 to +0.14 | t0: +0.12, t1: +0.00, t2: -0.55, t3: -0.03, t4: +0.20 |
| stronger vs control | 5 | -0.88 | 0 / 5 | -1.51 to -0.26 | t0: -0.22, t1: -1.65, t2: -0.03, t3: -1.72, t4: -0.80 |
| stronger_told vs control | 5 | -0.87 | 0 / 5 | -1.26 to -0.57 | t0: -0.75, t1: -0.85, t2: -0.42, t3: -1.62, t4: -0.70 |
| equal vs control | 5 | -0.02 | 1 / 2 | -0.06 to +0.02 | t0: -0.02, t1: +0.00, t2: +0.00, t3: +0.03, t4: -0.10 |
| equal_told vs control | 5 | -0.02 | 1 / 3 | -0.06 to +0.02 | t0: -0.05, t1: +0.00, t2: -0.02, t3: -0.08, t4: +0.05 |
| newcomer vs control | 5 | -0.01 | 1 / 3 | -0.11 to +0.11 | t0: -0.07, t1: +0.00, t2: -0.18, t3: -0.02, t4: +0.20 |
| newcomer vs rename (model change given a new name) | 5 | +0.04 | 2 / 1 | -0.11 to +0.22 | t0: -0.18, t1: +0.00, t2: +0.37, t3: +0.02, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.06 | 2 / 2 | -0.08 to +0.22 | t0: -0.17, t1: +0.00, t2: +0.37, t3: -0.02, t4: +0.10 |
| stronger vs equal (capability; also changes provider) | 5 | -0.87 | 0 / 5 | -1.50 to -0.23 | t0: -0.20, t1: -1.65, t2: -0.03, t3: -1.75, t4: -0.70 |
| told effect, stronger (4 - 3) | 5 | +0.02 | 3 / 2 | -0.35 to +0.42 | t0: -0.53, t1: +0.80, t2: -0.38, t3: +0.10, t4: +0.10 |
| told effect, equal (6 - 5) | 5 | -0.00 | 1 / 3 | -0.07 to +0.08 | t0: -0.03, t1: +0.00, t2: -0.02, t3: -0.12, t4: +0.15 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.02 | 2 / 3 | -0.36 to +0.45 | t0: -0.50, t1: +0.80, t2: -0.37, t3: +0.22, t4: -0.05 |

### trust_gap_matched

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.31 | 2 / 2 | -0.93 to +0.07 | t0: +0.07, t1: -1.50, t2: +0.00, t3: +0.12, t4: -0.25 |
| rename vs control | 5 | -0.05 | 2 / 2 | -0.31 to +0.14 | t0: +0.12, t1: +0.00, t2: -0.55, t3: -0.03, t4: +0.20 |
| stronger vs control | 5 | -0.85 | 0 / 5 | -1.49 to -0.21 | t0: -0.20, t1: -1.67, t2: -0.03, t3: -1.75, t4: -0.61 |
| stronger_told vs control | 5 | -0.64 | 0 / 5 | -1.05 to -0.28 | t0: -0.77, t1: -0.42, t2: -0.04, t3: -1.36, t4: -0.63 |
| equal vs control | 5 | -0.02 | 1 / 2 | -0.06 to +0.02 | t0: -0.02, t1: +0.00, t2: +0.00, t3: +0.03, t4: -0.10 |
| equal_told vs control | 5 | -0.02 | 1 / 3 | -0.06 to +0.02 | t0: -0.05, t1: +0.00, t2: -0.02, t3: -0.08, t4: +0.05 |
| newcomer vs control | 5 | -0.01 | 1 / 3 | -0.11 to +0.11 | t0: -0.07, t1: +0.00, t2: -0.18, t3: -0.02, t4: +0.20 |
| newcomer vs rename (model change given a new name) | 5 | +0.04 | 2 / 1 | -0.11 to +0.22 | t0: -0.18, t1: +0.00, t2: +0.37, t3: +0.02, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.06 | 2 / 2 | -0.08 to +0.22 | t0: -0.17, t1: +0.00, t2: +0.37, t3: -0.02, t4: +0.10 |
| stronger vs equal (capability; also changes provider) | 5 | -0.83 | 0 / 5 | -1.48 to -0.19 | t0: -0.18, t1: -1.67, t2: -0.03, t3: -1.78, t4: -0.51 |
| told effect, stronger (4 - 3) | 5 | +0.21 | 2 / 3 | -0.27 to +0.75 | t0: -0.58, t1: +1.25, t2: -0.01, t3: +0.39, t4: -0.02 |
| told effect, equal (6 - 5) | 5 | -0.00 | 1 / 3 | -0.07 to +0.08 | t0: -0.03, t1: +0.00, t2: -0.02, t3: -0.12, t4: +0.15 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.21 | 3 / 2 | -0.28 to +0.75 | t0: -0.54, t1: +1.25, t2: +0.01, t3: +0.51, t4: -0.17 |

### trust_gap_pre_deviation

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 4 | -0.02 | 2 / 1 | -0.17 to +0.09 | t0: +0.07, t2: +0.00, t3: +0.12, t4: -0.25 |
| rename vs control | 5 | -0.05 | 2 / 2 | -0.31 to +0.14 | t0: +0.12, t1: +0.00, t2: -0.55, t3: -0.03, t4: +0.20 |
| stronger vs control | 3 | -0.04 | 1 / 2 | -0.38 to +0.28 | t0: +0.28, t2: -0.03, t4: -0.38 |
| stronger_told vs control | 3 | +0.01 | 1 / 1 | -0.04 to +0.08 | t1: +0.00, t2: -0.04, t3: +0.08 |
| equal vs control | 5 | -0.02 | 1 / 2 | -0.06 to +0.02 | t0: -0.02, t1: +0.00, t2: +0.00, t3: +0.03, t4: -0.10 |
| equal_told vs control | 5 | -0.02 | 1 / 3 | -0.06 to +0.02 | t0: -0.05, t1: +0.00, t2: -0.02, t3: -0.08, t4: +0.05 |
| newcomer vs control | 5 | -0.01 | 1 / 3 | -0.11 to +0.11 | t0: -0.07, t1: +0.00, t2: -0.18, t3: -0.02, t4: +0.20 |
| newcomer vs rename (model change given a new name) | 5 | +0.04 | 2 / 1 | -0.11 to +0.22 | t0: -0.18, t1: +0.00, t2: +0.37, t3: +0.02, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.06 | 2 / 2 | -0.08 to +0.22 | t0: -0.17, t1: +0.00, t2: +0.37, t3: -0.02, t4: +0.10 |
| stronger vs equal (capability; also changes provider) | 3 | -0.01 | 1 / 2 | -0.28 to +0.30 | t0: +0.30, t2: -0.03, t4: -0.28 |
| told effect, stronger (4 - 3) | 1 | -0.01 | 0 / 1 | -0.01 to -0.01 | t2: -0.01 |
| told effect, equal (6 - 5) | 5 | -0.00 | 1 / 3 | -0.07 to +0.08 | t0: -0.03, t1: +0.00, t2: -0.02, t3: -0.12, t4: +0.15 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 1 | +0.01 | 1 / 0 | +0.01 to +0.01 | t2: +0.01 |

### detection

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger_told vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### recognition

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 0 | – | 0 / 0 | – |  |
| rename vs control | 0 | – | 0 / 0 | – |  |
| stronger vs control | 0 | – | 0 / 0 | – |  |
| stronger_told vs control | 0 | – | 0 / 0 | – |  |
| equal vs control | 0 | – | 0 / 0 | – |  |
| equal_told vs control | 0 | – | 0 / 0 | – |  |
| newcomer vs control | 0 | – | 0 / 0 | – |  |
| newcomer vs rename (model change given a new name) | 5 | +0.02 | 2 / 1 | -0.03 to +0.07 | t0: -0.08, t1: +0.08, t2: +0.08, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 0 | – | 0 / 0 | – |  |
| stronger vs equal (capability; also changes provider) | 0 | – | 0 / 0 | – |  |
| told effect, stronger (4 - 3) | 0 | – | 0 / 0 | – |  |
| told effect, equal (6 - 5) | 0 | – | 0 / 0 | – |  |
| capability x told interaction ((4 - 3) - (6 - 5)) | 0 | – | 0 / 0 | – |  |

### change_detected

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 0 | – | 0 / 0 | – |  |
| stronger vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger_told vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 0 | – | 0 / 0 | – |  |
| newcomer vs rename (model change given a new name) | 0 | – | 0 / 0 | – |  |
| name x model interaction ((7 - 5) - (2 - 1)) | 0 | – | 0 / 0 | – |  |
| stronger vs equal (capability; also changes provider) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### change_about_R

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 0 | – | 0 / 0 | – |  |
| rename vs control | 0 | – | 0 / 0 | – |  |
| stronger vs control | 0 | – | 0 / 0 | – |  |
| stronger_told vs control | 0 | – | 0 / 0 | – |  |
| equal vs control | 0 | – | 0 / 0 | – |  |
| equal_told vs control | 0 | – | 0 / 0 | – |  |
| newcomer vs control | 0 | – | 0 / 0 | – |  |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 0 | – | 0 / 0 | – |  |
| stronger vs equal (capability; also changes provider) | 0 | – | 0 / 0 | – |  |
| told effect, stronger (4 - 3) | 0 | – | 0 / 0 | – |  |
| told effect, equal (6 - 5) | 0 | – | 0 / 0 | – |  |
| capability x told interaction ((4 - 3) - (6 - 5)) | 0 | – | 0 / 0 | – |  |

### others_cheap

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger_told vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |

### seat_cheap

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.04 | 0 / 1 | -0.12 to +0.00 | t0: +0.00, t1: -0.20, t2: +0.00, t3: +0.00, t4: +0.00 |
| rename vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs control | 5 | -0.24 | 0 / 4 | -0.36 to -0.12 | t0: -0.20, t1: -0.40, t2: +0.00, t3: -0.40, t4: -0.20 |
| stronger_told vs control | 5 | -0.36 | 0 / 5 | -0.40 to -0.28 | t0: -0.40, t1: -0.40, t2: -0.20, t3: -0.40, t4: -0.40 |
| equal vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| equal_told vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs control | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | -0.24 | 0 / 4 | -0.36 to -0.12 | t0: -0.20, t1: -0.40, t2: +0.00, t3: -0.40, t4: -0.20 |
| told effect, stronger (4 - 3) | 5 | -0.12 | 0 / 3 | -0.20 to -0.04 | t0: -0.20, t1: +0.00, t2: -0.20, t3: +0.00, t4: -0.20 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t1: +0.00, t2: +0.00, t3: +0.00, t4: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | -0.12 | 0 / 3 | -0.20 to -0.04 | t0: -0.20, t1: +0.00, t2: -0.20, t3: +0.00, t4: -0.20 |

