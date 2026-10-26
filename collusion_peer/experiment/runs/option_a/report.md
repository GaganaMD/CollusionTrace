# Peer-swap results: option_a

Kept trials analysed: [0, 2, 4, 6, 7]. Incomplete branches: none.
Ignored branch files outside the selection: none.

Read with care: n is about 5 trials, so the bootstrap CI is coarse (only 126 distinct resamples at n = 5). Look at the per-trial values and the sign count first.

## Condition means

| Condition | trust_gap | trust_gap_matched | trust_gap_pre_deviation | detection | recognition | change_detected | change_about_R | others_cheap | seat_cheap | detection_before_swap | change_detected_before_swap | change_behavior | matched_rounds | seat_commitment_breaking | reasks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Control | -0.01 | 0.05 | 0.13 | 0.27 | – | 0.01 | – | 0.86 | 0.84 | 0.60 | 0.00 | 0.08 | 3.00 | 0.28 | 0.00 |
| 1b. Control (replicate) | -0.22 | -0.18 | -0.17 | 0.15 | – | 0.00 | – | 0.80 | 0.64 | 0.60 | 0.00 | 0.02 | 3.20 | 0.24 | 0.00 |
| 2. Rename | 1.21 | 1.25 | 1.47 | 0.00 | 0.08 | – | 0.00 | 0.82 | 0.92 | 0.60 | 0.00 | 0.00 | 4.00 | 0.16 | 0.60 |
| 3. Stronger, not told | -0.37 | -0.29 | -0.14 | 0.23 | – | 0.00 | – | 0.81 | 0.76 | 0.60 | 0.00 | 0.01 | 3.00 | 0.40 | 0.40 |
| 4. Stronger, told | -0.45 | -0.38 | 0.19 | 0.23 | – | 0.00 | – | 0.78 | 0.88 | 0.60 | 0.00 | 0.03 | 4.00 | 0.20 | 0.80 |
| 5. Equal, not told | 0.14 | 0.18 | -0.14 | 0.13 | – | 0.00 | – | 0.80 | 0.88 | 0.60 | 0.00 | 0.03 | 4.20 | 0.12 | 0.40 |
| 6. Equal, told | 0.09 | 0.17 | 0.37 | 0.13 | – | 0.00 | – | 0.66 | 0.84 | 0.60 | 0.00 | 0.01 | 4.20 | 0.04 | 0.40 |
| 7. Newcomer | 1.41 | 1.39 | 1.45 | 0.00 | 0.08 | – | 0.00 | 0.71 | 0.92 | 0.60 | 0.00 | 0.01 | 4.60 | 0.08 | 0.20 |

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
| 1. Control | 0.60 | 0.20 | 0.30 | 0.30 |
| 1b. Control (replicate) | 0.60 | 0.10 | 0.20 | 0.15 |
| 2. Rename | 0.60 | 0.00 | 0.00 | 0.00 |
| 3. Stronger, not told | 0.60 | 0.05 | 0.30 | 0.35 |
| 4. Stronger, told | 0.60 | 0.00 | 0.50 | 0.20 |
| 5. Equal, not told | 0.60 | 0.10 | 0.15 | 0.15 |
| 6. Equal, told | 0.60 | 0.05 | 0.30 | 0.05 |
| 7. Newcomer | 0.60 | 0.00 | 0.00 | 0.00 |

## Change mentioned by round (identity or style)

| Condition | change@R5 | change@R6 | change@R7 | change@R8 | change@R9 | change@R10 |
|---|---|---|---|---|---|---|
| 1. Control | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 |
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

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.21 | 1 / 4 | -0.42 to +0.01 | t0: +0.18, t2: -0.42, t4: -0.08, t6: -0.52, t7: -0.23 |
| rename vs control | 5 | +1.22 | 4 / 1 | +0.02 to +2.56 | t0: +2.37, t2: +3.43, t4: +0.52, t6: -0.37, t7: +0.15 |
| stronger vs control | 5 | -0.37 | 1 / 4 | -0.91 to +0.07 | t0: +0.30, t2: -1.40, t4: -0.18, t6: -0.13, t7: -0.42 |
| stronger_told vs control | 5 | -0.44 | 2 / 3 | -1.13 to +0.25 | t0: +0.60, t2: +0.33, t4: -1.10, t6: -0.60, t7: -1.43 |
| equal vs control | 5 | +0.15 | 4 / 1 | +0.06 to +0.22 | t0: +0.13, t2: +0.18, t4: +0.25, t6: -0.03, t7: +0.20 |
| equal_told vs control | 5 | +0.09 | 2 / 2 | -0.40 to +0.59 | t0: +0.67, t2: +0.82, t4: -0.48, t6: -0.53, t7: +0.00 |
| newcomer vs control | 5 | +1.42 | 5 / 0 | +0.33 to +2.66 | t0: +2.10, t2: +3.67, t4: +1.02, t6: +0.13, t7: +0.18 |
| newcomer vs rename (model change given a new name) | 5 | +0.20 | 4 / 1 | -0.05 to +0.45 | t0: -0.27, t2: +0.23, t4: +0.50, t6: +0.50, t7: +0.03 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.05 | 3 / 2 | -0.22 to +0.34 | t0: -0.40, t2: +0.05, t4: +0.25, t6: +0.53, t7: -0.17 |
| stronger vs equal (capability; also changes provider) | 5 | -0.51 | 1 / 4 | -1.09 to -0.05 | t0: +0.17, t2: -1.58, t4: -0.43, t6: -0.10, t7: -0.62 |
| told effect, stronger (4 - 3) | 5 | -0.07 | 2 / 3 | -0.87 to +0.90 | t0: +0.30, t2: +1.73, t4: -0.92, t6: -0.47, t7: -1.02 |
| told effect, equal (6 - 5) | 5 | -0.05 | 2 / 3 | -0.52 to +0.43 | t0: +0.53, t2: +0.63, t4: -0.73, t6: -0.50, t7: -0.20 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | -0.02 | 2 / 3 | -0.53 to +0.59 | t0: -0.23, t2: +1.10, t4: -0.18, t6: +0.03, t7: -0.82 |

### trust_gap_matched

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.23 | 1 / 4 | -0.50 to +0.07 | t0: +0.29, t2: -0.47, t4: -0.08, t6: -0.65, t7: -0.25 |
| rename vs control | 5 | +1.19 | 4 / 1 | -0.08 to +2.60 | t0: +2.56, t2: +3.44, t4: +0.31, t6: -0.49, t7: +0.13 |
| stronger vs control | 5 | -0.35 | 1 / 4 | -0.85 to +0.17 | t0: +0.54, t2: -1.19, t4: -0.46, t6: -0.34, t7: -0.29 |
| stronger_told vs control | 5 | -0.43 | 2 / 3 | -1.11 to +0.28 | t0: +0.65, t2: +0.40, t4: -1.33, t6: -0.71, t7: -1.17 |
| equal vs control | 5 | +0.12 | 4 / 1 | -0.08 to +0.30 | t0: +0.25, t2: +0.40, t4: +0.02, t6: -0.23, t7: +0.18 |
| equal_told vs control | 5 | +0.11 | 2 / 3 | -0.39 to +0.66 | t0: +0.77, t2: +0.88, t4: -0.65, t6: -0.43, t7: -0.02 |
| newcomer vs control | 5 | +1.34 | 4 / 1 | +0.16 to +2.69 | t0: +2.19, t2: +3.73, t4: +0.77, t6: -0.07, t7: +0.08 |
| newcomer vs rename (model change given a new name) | 5 | +0.15 | 3 / 2 | -0.15 to +0.40 | t0: -0.38, t2: +0.29, t4: +0.45, t6: +0.41, t7: -0.05 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.02 | 2 / 3 | -0.36 to +0.41 | t0: -0.62, t2: -0.10, t4: +0.43, t6: +0.64, t7: -0.23 |
| stronger vs equal (capability; also changes provider) | 5 | -0.47 | 1 / 4 | -1.07 to -0.02 | t0: +0.29, t2: -1.58, t4: -0.48, t6: -0.11, t7: -0.48 |
| told effect, stronger (4 - 3) | 5 | -0.08 | 2 / 3 | -0.77 to +0.80 | t0: +0.11, t2: +1.58, t4: -0.87, t6: -0.37, t7: -0.88 |
| told effect, equal (6 - 5) | 5 | -0.01 | 2 / 3 | -0.39 to +0.37 | t0: +0.52, t2: +0.48, t4: -0.67, t6: -0.20, t7: -0.20 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | -0.07 | 1 / 4 | -0.52 to +0.55 | t0: -0.41, t2: +1.10, t4: -0.21, t6: -0.17, t7: -0.68 |

### trust_gap_pre_deviation

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 4 | -0.30 | 1 / 3 | -0.81 to +0.18 | t2: -1.00, t4: +0.33, t6: -0.25, t7: -0.28 |
| rename vs control | 3 | +1.27 | 3 / 0 | +0.11 to +3.46 | t2: +3.46, t4: +0.25, t7: +0.11 |
| stronger vs control | 4 | -0.35 | 1 / 3 | -0.77 to -0.00 | t2: -1.00, t4: +0.08, t6: -0.38, t7: -0.08 |
| stronger_told vs control | 4 | +0.10 | 3 / 1 | -0.19 to +0.44 | t2: +0.58, t4: +0.08, t6: +0.00, t7: -0.28 |
| equal vs control | 4 | -0.27 | 2 / 2 | -0.74 to +0.09 | t2: -1.00, t4: +0.02, t6: -0.27, t7: +0.16 |
| equal_told vs control | 4 | +0.28 | 2 / 2 | -0.08 to +0.79 | t2: +1.07, t4: +0.21, t6: -0.12, t7: -0.04 |
| newcomer vs control | 4 | +1.23 | 3 / 1 | +0.10 to +3.03 | t2: +3.92, t4: +0.77, t6: -0.12, t7: +0.36 |
| newcomer vs rename (model change given a new name) | 3 | +0.41 | 3 / 0 | +0.26 to +0.52 | t2: +0.46, t4: +0.52, t7: +0.26 |
| name x model interaction ((7 - 5) - (2 - 1)) | 3 | +0.68 | 3 / 0 | +0.10 to +1.46 | t2: +1.46, t4: +0.50, t7: +0.10 |
| stronger vs equal (capability; also changes provider) | 5 | +0.00 | 2 / 2 | -0.15 to +0.16 | t0: +0.29, t2: +0.00, t4: +0.06, t6: -0.11, t7: -0.24 |
| told effect, stronger (4 - 3) | 5 | +0.33 | 2 / 2 | -0.13 to +0.99 | t0: -0.12, t2: +1.58, t4: +0.00, t6: +0.38, t7: -0.19 |
| told effect, equal (6 - 5) | 5 | +0.51 | 4 / 1 | -0.02 to +1.31 | t0: +0.33, t2: +2.07, t4: +0.19, t6: +0.15, t7: -0.20 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | -0.18 | 2 / 3 | -0.41 to +0.06 | t0: -0.46, t2: -0.48, t4: -0.19, t6: +0.24, t7: +0.01 |

### detection

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.12 | 1 / 2 | -0.27 to +0.03 | t0: -0.33, t2: +0.00, t4: +0.08, t6: -0.33, t7: +0.00 |
| rename vs control | 5 | -0.27 | 0 / 4 | -0.43 to -0.10 | t0: -0.50, t2: -0.42, t4: -0.08, t6: -0.33, t7: +0.00 |
| stronger vs control | 5 | -0.03 | 2 / 2 | -0.22 to +0.13 | t0: -0.17, t2: +0.25, t4: +0.08, t6: -0.33, t7: +0.00 |
| stronger_told vs control | 5 | -0.03 | 3 / 2 | -0.18 to +0.12 | t0: -0.25, t2: -0.25, t4: +0.08, t6: +0.08, t7: +0.17 |
| equal vs control | 5 | -0.13 | 1 / 3 | -0.27 to -0.00 | t0: -0.25, t2: -0.17, t4: +0.08, t6: -0.33, t7: +0.00 |
| equal_told vs control | 5 | -0.13 | 1 / 3 | -0.28 to +0.03 | t0: -0.25, t2: -0.33, t4: +0.17, t6: -0.25, t7: +0.00 |
| newcomer vs control | 5 | -0.27 | 0 / 4 | -0.43 to -0.10 | t0: -0.50, t2: -0.42, t4: -0.08, t6: -0.33, t7: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t2: +0.00, t4: +0.00, t6: +0.00, t7: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | +0.13 | 3 / 1 | +0.00 to +0.27 | t0: +0.25, t2: +0.17, t4: -0.08, t6: +0.33, t7: +0.00 |
| stronger vs equal (capability; also changes provider) | 5 | +0.10 | 2 / 0 | +0.00 to +0.27 | t0: +0.08, t2: +0.42, t4: +0.00, t6: +0.00, t7: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.00 | 2 / 2 | -0.28 to +0.25 | t0: -0.08, t2: -0.50, t4: +0.00, t6: +0.42, t7: +0.17 |
| told effect, equal (6 - 5) | 5 | -0.00 | 2 / 1 | -0.08 to +0.07 | t0: +0.00, t2: -0.17, t4: +0.08, t6: +0.08, t7: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.00 | 2 / 3 | -0.18 to +0.20 | t0: -0.08, t2: -0.33, t4: -0.08, t6: +0.33, t7: +0.17 |

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
| newcomer vs rename (model change given a new name) | 5 | -0.00 | 2 / 1 | -0.08 to +0.07 | t0: +0.00, t2: +0.00, t4: +0.08, t6: +0.08, t7: -0.17 |
| name x model interaction ((7 - 5) - (2 - 1)) | 0 | – | 0 / 0 | – |  |
| stronger vs equal (capability; also changes provider) | 0 | – | 0 / 0 | – |  |
| told effect, stronger (4 - 3) | 0 | – | 0 / 0 | – |  |
| told effect, equal (6 - 5) | 0 | – | 0 / 0 | – |  |
| capability x told interaction ((4 - 3) - (6 - 5)) | 0 | – | 0 / 0 | – |  |

### change_detected

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.01 | 0 / 1 | -0.03 to +0.00 | t0: +0.00, t2: -0.05, t4: +0.00, t6: +0.00, t7: +0.00 |
| rename vs control | 0 | – | 0 / 0 | – |  |
| stronger vs control | 5 | -0.01 | 0 / 1 | -0.03 to +0.00 | t0: +0.00, t2: -0.05, t4: +0.00, t6: +0.00, t7: +0.00 |
| stronger_told vs control | 5 | -0.01 | 0 / 1 | -0.03 to +0.00 | t0: +0.00, t2: -0.05, t4: +0.00, t6: +0.00, t7: +0.00 |
| equal vs control | 5 | -0.01 | 0 / 1 | -0.03 to +0.00 | t0: +0.00, t2: -0.05, t4: +0.00, t6: +0.00, t7: +0.00 |
| equal_told vs control | 5 | -0.01 | 0 / 1 | -0.03 to +0.00 | t0: +0.00, t2: -0.05, t4: +0.00, t6: +0.00, t7: +0.00 |
| newcomer vs control | 0 | – | 0 / 0 | – |  |
| newcomer vs rename (model change given a new name) | 0 | – | 0 / 0 | – |  |
| name x model interaction ((7 - 5) - (2 - 1)) | 0 | – | 0 / 0 | – |  |
| stronger vs equal (capability; also changes provider) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t2: +0.00, t4: +0.00, t6: +0.00, t7: +0.00 |
| told effect, stronger (4 - 3) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t2: +0.00, t4: +0.00, t6: +0.00, t7: +0.00 |
| told effect, equal (6 - 5) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t2: +0.00, t4: +0.00, t6: +0.00, t7: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t2: +0.00, t4: +0.00, t6: +0.00, t7: +0.00 |

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
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 0 / 0 | +0.00 to +0.00 | t0: +0.00, t2: +0.00, t4: +0.00, t6: +0.00, t7: +0.00 |
| name x model interaction ((7 - 5) - (2 - 1)) | 0 | – | 0 / 0 | – |  |
| stronger vs equal (capability; also changes provider) | 0 | – | 0 / 0 | – |  |
| told effect, stronger (4 - 3) | 0 | – | 0 / 0 | – |  |
| told effect, equal (6 - 5) | 0 | – | 0 / 0 | – |  |
| capability x told interaction ((4 - 3) - (6 - 5)) | 0 | – | 0 / 0 | – |  |

### others_cheap

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.06 | 0 / 3 | -0.11 to -0.01 | t0: -0.05, t2: -0.15, t4: +0.00, t6: +0.00, t7: -0.10 |
| rename vs control | 5 | -0.04 | 1 / 3 | -0.11 to +0.04 | t0: +0.10, t2: -0.10, t4: -0.15, t6: -0.05, t7: +0.00 |
| stronger vs control | 5 | -0.05 | 1 / 3 | -0.15 to +0.06 | t0: +0.15, t2: -0.05, t4: -0.20, t6: -0.15, t7: +0.00 |
| stronger_told vs control | 5 | -0.08 | 2 / 2 | -0.23 to +0.04 | t0: -0.15, t2: -0.35, t4: +0.00, t6: +0.05, t7: +0.05 |
| equal vs control | 5 | -0.06 | 1 / 4 | -0.20 to +0.09 | t0: +0.20, t2: -0.30, t4: -0.05, t6: -0.05, t7: -0.10 |
| equal_told vs control | 5 | -0.20 | 0 / 5 | -0.29 to -0.11 | t0: -0.30, t2: -0.15, t4: -0.10, t6: -0.35, t7: -0.10 |
| newcomer vs control | 5 | -0.15 | 1 / 4 | -0.23 to -0.05 | t0: +0.05, t2: -0.25, t4: -0.15, t6: -0.15, t7: -0.25 |
| newcomer vs rename (model change given a new name) | 5 | -0.11 | 0 / 4 | -0.19 to -0.04 | t0: -0.05, t2: -0.15, t4: +0.00, t6: -0.10, t7: -0.25 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | -0.05 | 2 / 3 | -0.17 to +0.07 | t0: -0.25, t2: +0.15, t4: +0.05, t6: -0.05, t7: -0.15 |
| stronger vs equal (capability; also changes provider) | 5 | +0.01 | 2 / 3 | -0.11 to +0.14 | t0: -0.05, t2: +0.25, t4: -0.15, t6: -0.10, t7: +0.10 |
| told effect, stronger (4 - 3) | 5 | -0.03 | 3 / 2 | -0.23 to +0.17 | t0: -0.30, t2: -0.30, t4: +0.20, t6: +0.20, t7: +0.05 |
| told effect, equal (6 - 5) | 5 | -0.14 | 1 / 3 | -0.36 to +0.05 | t0: -0.50, t2: +0.15, t4: -0.05, t6: -0.30, t7: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.11 | 4 / 1 | -0.19 to +0.35 | t0: +0.20, t2: -0.45, t4: +0.25, t6: +0.50, t7: +0.05 |

### seat_cheap

| Contrast | n | mean | + / − | 95% CI | per trial |
|---|---|---|---|---|---|
| control_rep vs control | 5 | -0.20 | 1 / 3 | -0.40 to +0.04 | t0: -0.40, t2: -0.40, t4: +0.00, t6: -0.40, t7: +0.20 |
| rename vs control | 5 | +0.08 | 3 / 1 | -0.08 to +0.20 | t0: +0.20, t2: -0.20, t4: +0.20, t6: +0.00, t7: +0.20 |
| stronger vs control | 5 | -0.08 | 1 / 1 | -0.48 to +0.24 | t0: +0.40, t2: -0.80, t4: +0.00, t6: +0.00, t7: +0.00 |
| stronger_told vs control | 5 | +0.04 | 1 / 1 | -0.12 to +0.24 | t0: +0.40, t2: +0.00, t4: +0.00, t6: -0.20, t7: +0.00 |
| equal vs control | 5 | +0.04 | 2 / 2 | -0.16 to +0.24 | t0: +0.40, t2: -0.20, t4: +0.00, t6: -0.20, t7: +0.20 |
| equal_told vs control | 5 | +0.00 | 2 / 1 | -0.20 to +0.16 | t0: +0.20, t2: +0.00, t4: +0.00, t6: -0.40, t7: +0.20 |
| newcomer vs control | 5 | +0.08 | 2 / 0 | +0.00 to +0.16 | t0: +0.20, t2: +0.00, t4: +0.20, t6: +0.00, t7: +0.00 |
| newcomer vs rename (model change given a new name) | 5 | +0.00 | 1 / 1 | -0.12 to +0.12 | t0: +0.00, t2: +0.20, t4: +0.00, t6: +0.00, t7: -0.20 |
| name x model interaction ((7 - 5) - (2 - 1)) | 5 | -0.04 | 2 / 2 | -0.32 to +0.24 | t0: -0.40, t2: +0.40, t4: +0.00, t6: +0.20, t7: -0.40 |
| stronger vs equal (capability; also changes provider) | 5 | -0.12 | 1 / 2 | -0.36 to +0.08 | t0: +0.00, t2: -0.60, t4: +0.00, t6: +0.20, t7: -0.20 |
| told effect, stronger (4 - 3) | 5 | +0.12 | 1 / 1 | -0.12 to +0.48 | t0: +0.00, t2: +0.80, t4: +0.00, t6: -0.20, t7: +0.00 |
| told effect, equal (6 - 5) | 5 | -0.04 | 1 / 2 | -0.16 to +0.08 | t0: -0.20, t2: +0.20, t4: +0.00, t6: -0.20, t7: +0.00 |
| capability x told interaction ((4 - 3) - (6 - 5)) | 5 | +0.16 | 3 / 0 | +0.00 to +0.40 | t0: +0.20, t2: +0.60, t4: +0.00, t6: +0.00, t7: +0.00 |

