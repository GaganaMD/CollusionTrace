# Ceiling test: can a model tell the seat's writer changed?

A judge sees the seat's announcements before and after the swap (blinded) and says whether one author wrote both. **Hit rate** = says 'different' when the writer changed; **false alarms** = says 'different' when it didn't ('unsure' counts as neither). **Accuracy** counts 'unsure' as wrong. **AUC** uses the answer and its confidence (0.5 = chance, 1.0 = perfect).

**Read the 'style only' row first.** The told conditions can give the swap away in *content* (a newcomer may say it is taking over), and items flagged with a content cue do the same; the style-only row drops both. Stronger seats can also announce EXPENSIVE when they defect, so stronger-vs-same-writer AUCs may partly reflect behaviour.

Each item is judged in both orders, so independent items = answers / 2.

Items with a content cue in the post-swap messages: 1 ['stronger_told t2']

## Judge: `gpt-4o-mini`

Answers: 80 (unparsed: 0); AB/BA answers agree on 57% of items.

| Items | Answers | Hit rate | False alarms | Accuracy | AUC |
|---|---|---|---|---|---|
| All | 80 | 50% | 20% | 61% | 0.65 |
| Style only (no told conditions, no content cues) | 60 | 50% | 20% | 65% | 0.65 |

| Condition | Truth | Says same | Says different | Unsure | Mean confidence | AUC vs same-writer items |
|---|---|---|---|---|---|---|
| 1. Control | same | 8 | 2 | 0 | 85 | – |
| 1b. Control (replicate) | same | 8 | 2 | 0 | 85 | – |
| 2. Rename | same | 8 | 2 | 0 | 85 | – |
| 3. Stronger, not told | different | 5 | 5 | 0 | 85 | 0.65 |
| 4. Stronger, told | different | 5 | 5 | 0 | 85 | 0.65 |
| 5. Equal, not told | different | 4 | 6 | 0 | 85 | 0.70 |
| 6. Equal, told | different | 5 | 5 | 0 | 85 | 0.65 |
| 7. Newcomer | different | 6 | 4 | 0 | 85 | 0.60 |

## Judge: `anthropic/claude-haiku-5.5`

Answers: 80 (unparsed: 0); AB/BA answers agree on 70% of items.

| Items | Answers | Hit rate | False alarms | Accuracy | AUC |
|---|---|---|---|---|---|
| All | 80 | 32% | 0% | 57% | 0.85 |
| Style only (no told conditions, no content cues) | 60 | 40% | 0% | 70% | 0.87 |

| Condition | Truth | Says same | Says different | Unsure | Mean confidence | AUC vs same-writer items |
|---|---|---|---|---|---|---|
| 1. Control | same | 10 | 0 | 0 | 74 | – |
| 1b. Control (replicate) | same | 10 | 0 | 0 | 73 | – |
| 2. Rename | same | 10 | 0 | 0 | 74 | – |
| 3. Stronger, not told | different | 9 | 0 | 1 | 71 | 0.65 |
| 4. Stronger, told | different | 8 | 1 | 1 | 71 | 0.65 |
| 5. Equal, not told | different | 4 | 6 | 0 | 64 | 0.98 |
| 6. Equal, told | different | 4 | 3 | 3 | 60 | 0.98 |
| 7. Newcomer | different | 3 | 6 | 1 | 62 | 0.99 |

