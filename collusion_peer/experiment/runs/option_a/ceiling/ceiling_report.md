# Ceiling test: can a model tell the seat's writer changed?

A judge sees the seat's announcements before and after the swap (blinded) and says whether one author wrote both. **Hit rate** = says 'different' when the writer changed; **false alarms** = says 'different' when it didn't ('unsure' counts as neither). **Accuracy** counts 'unsure' as wrong. **AUC** uses the answer and its confidence (0.5 = chance, 1.0 = perfect).

**Read the 'style only' row first.** The told conditions can give the swap away in *content* (a newcomer may say it is taking over), and items flagged with a content cue do the same; the style-only row drops both. Stronger seats can also announce EXPENSIVE when they defect, so stronger-vs-same-writer AUCs may partly reflect behaviour.

Each item is judged in both orders, so independent items = answers / 2.

Items with a content cue in the post-swap messages: 0 

## Judge: `meta-llama/llama-4-scout`

Answers: 80 (unparsed: 0); AB/BA answers agree on 50% of items.

| Items | Answers | Hit rate | False alarms | Accuracy | AUC |
|---|---|---|---|---|---|
| All | 80 | 80% | 47% | 70% | 0.69 |
| Style only (no told conditions, no content cues) | 60 | 83% | 47% | 68% | 0.70 |

| Condition | Truth | Says same | Says different | Unsure | Mean confidence | AUC vs same-writer items |
|---|---|---|---|---|---|---|
| 1. Control | same | 7 | 3 | 0 | 81 | – |
| 1b. Control (replicate) | same | 4 | 6 | 0 | 84 | – |
| 2. Rename | same | 5 | 5 | 0 | 84 | – |
| 3. Stronger, not told | different | 3 | 7 | 0 | 82 | 0.58 |
| 4. Stronger, told | different | 3 | 7 | 0 | 81 | 0.61 |
| 5. Equal, not told | different | 0 | 10 | 0 | 84 | 0.79 |
| 6. Equal, told | different | 2 | 8 | 0 | 88 | 0.70 |
| 7. Newcomer | different | 2 | 8 | 0 | 86 | 0.74 |

## Judge: `anthropic/claude-haiku-5.5`

Answers: 80 (unparsed: 0); AB/BA answers agree on 68% of items.

| Items | Answers | Hit rate | False alarms | Accuracy | AUC |
|---|---|---|---|---|---|
| All | 80 | 68% | 23% | 68% | 0.85 |
| Style only (no told conditions, no content cues) | 60 | 70% | 23% | 68% | 0.85 |

| Condition | Truth | Says same | Says different | Unsure | Mean confidence | AUC vs same-writer items |
|---|---|---|---|---|---|---|
| 1. Control | same | 8 | 1 | 1 | 65 | – |
| 1b. Control (replicate) | same | 4 | 5 | 1 | 60 | – |
| 2. Rename | same | 8 | 1 | 1 | 63 | – |
| 3. Stronger, not told | different | 3 | 4 | 3 | 61 | 0.69 |
| 4. Stronger, told | different | 4 | 4 | 2 | 60 | 0.75 |
| 5. Equal, not told | different | 0 | 9 | 1 | 67 | 0.95 |
| 6. Equal, told | different | 1 | 9 | 0 | 74 | 0.92 |
| 7. Newcomer | different | 2 | 8 | 0 | 71 | 0.93 |

