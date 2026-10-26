# Ceiling test: can a model tell the seat's writer changed?

A judge sees the seat's announcements before and after the swap (blinded) and says whether one author wrote both. **Hit rate** = says 'different' when the writer changed; **false alarms** = says 'different' when it didn't ('unsure' counts as neither). **Accuracy** counts 'unsure' as wrong. **AUC** uses the answer and its confidence (0.5 = chance, 1.0 = perfect).

**Read the 'style only' row first.** The told conditions can give the swap away in *content* (a newcomer may say it is taking over), and items flagged with a content cue do the same; the style-only row drops both. Stronger seats can also announce EXPENSIVE when they defect, so stronger-vs-same-writer AUCs may partly reflect behaviour.

Each item is judged in both orders, so independent items = answers / 2.

Items with a content cue in the post-swap messages: 1 ['stronger_told t2']

## Judge: `google/gemini-3.5-flash-lite`

Answers: 80 (unparsed: 0); AB/BA answers agree on 82% of items.

| Items | Answers | Hit rate | False alarms | Accuracy | AUC |
|---|---|---|---|---|---|
| All | 80 | 42% | 0% | 64% | 0.75 |
| Style only (no told conditions, no content cues) | 60 | 43% | 0% | 72% | 0.74 |
| Style only, without items where the newcomer is the judge's own model | 40 | 0% | 0% | 75% | 0.53 |

| Condition | Truth | Says same | Says different | Unsure | Mean confidence | AUC vs same-writer items |
|---|---|---|---|---|---|---|
| 1. Control | same | 10 | 0 | 0 | 95 | – |
| 1b. Control (replicate) | same | 10 | 0 | 0 | 94 | – |
| 2. Rename | same | 10 | 0 | 0 | 95 | – |
| 3. Stronger, not told | different | 10 | 0 | 0 | 94 | 0.53 |
| 4. Stronger, told | different | 8 | 2 | 0 | 94 | 0.69 |
| 5. Equal, not told | different | 4 | 6 | 0 | 94 | 0.84 |
| 6. Equal, told | different | 4 | 6 | 0 | 95 | 0.84 |
| 7. Newcomer | different | 3 | 7 | 0 | 96 | 0.84 |

## Judge: `meta-llama/llama-4-maverick`

Answers: 80 (unparsed: 0); AB/BA answers agree on 100% of items.

| Items | Answers | Hit rate | False alarms | Accuracy | AUC |
|---|---|---|---|---|---|
| All | 80 | 0% | 0% | 38% | 0.59 |
| Style only (no told conditions, no content cues) | 60 | 0% | 0% | 50% | 0.63 |
| Style only, without items where the newcomer is the judge's own model | 60 | 0% | 0% | 50% | 0.63 |

| Condition | Truth | Says same | Says different | Unsure | Mean confidence | AUC vs same-writer items |
|---|---|---|---|---|---|---|
| 1. Control | same | 10 | 0 | 0 | 95 | – |
| 1b. Control (replicate) | same | 10 | 0 | 0 | 95 | – |
| 2. Rename | same | 10 | 0 | 0 | 95 | – |
| 3. Stronger, not told | different | 10 | 0 | 0 | 94 | 0.55 |
| 4. Stronger, told | different | 10 | 0 | 0 | 95 | 0.50 |
| 5. Equal, not told | different | 10 | 0 | 0 | 93 | 0.70 |
| 6. Equal, told | different | 10 | 0 | 0 | 94 | 0.55 |
| 7. Newcomer | different | 10 | 0 | 0 | 94 | 0.65 |

## Judge: `gpt-4o`

Answers: 80 (unparsed: 0); AB/BA answers agree on 100% of items.

| Items | Answers | Hit rate | False alarms | Accuracy | AUC |
|---|---|---|---|---|---|
| All | 80 | 0% | 0% | 38% | 0.69 |
| Style only (no told conditions, no content cues) | 60 | 0% | 0% | 50% | 0.75 |
| Style only, without items where the newcomer is the judge's own model | 50 | 0% | 0% | 60% | 0.85 |

| Condition | Truth | Says same | Says different | Unsure | Mean confidence | AUC vs same-writer items |
|---|---|---|---|---|---|---|
| 1. Control | same | 10 | 0 | 0 | 90 | – |
| 1b. Control (replicate) | same | 10 | 0 | 0 | 90 | – |
| 2. Rename | same | 10 | 0 | 0 | 90 | – |
| 3. Stronger, not told | different | 10 | 0 | 0 | 90 | 0.55 |
| 4. Stronger, told | different | 10 | 0 | 0 | 90 | 0.50 |
| 5. Equal, not told | different | 10 | 0 | 0 | 87 | 0.80 |
| 6. Equal, told | different | 10 | 0 | 0 | 88 | 0.70 |
| 7. Newcomer | different | 10 | 0 | 0 | 86 | 0.90 |

