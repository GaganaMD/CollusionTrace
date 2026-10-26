# Ceiling test: can a model tell the seat's writer changed?

A judge sees the seat's announcements before and after the swap (blinded) and says whether one author wrote both. **Hit rate** = says 'different' when the writer changed; **false alarms** = says 'different' when it didn't ('unsure' counts as neither). **Accuracy** counts 'unsure' as wrong. **AUC** uses the answer and its confidence (0.5 = chance, 1.0 = perfect).

**Read the 'style only' row first.** The told conditions can give the swap away in *content* (a newcomer may say it is taking over), and items flagged with a content cue do the same; the style-only row drops both. Stronger seats can also announce EXPENSIVE when they defect, so stronger-vs-same-writer AUCs may partly reflect behaviour.

Each item is judged in both orders, so independent items = answers / 2.

Items with a content cue in the post-swap messages: 0 

## Judge: `anthropic/claude-haiku-5.5`

Answers: 80 (unparsed: 0); AB/BA answers agree on 78% of items.

| Items | Answers | Hit rate | False alarms | Accuracy | AUC |
|---|---|---|---|---|---|
| All | 80 | 18% | 0% | 46% | 0.76 |
| Style only (no told conditions, no content cues) | 60 | 23% | 0% | 58% | 0.80 |
| Style only, without items where the newcomer is the judge's own model | 60 | 23% | 0% | 58% | 0.80 |

| Condition | Truth | Says same | Says different | Unsure | Mean confidence | AUC vs same-writer items |
|---|---|---|---|---|---|---|
| 1. Control | same | 8 | 0 | 2 | 73 | – |
| 1b. Control (replicate) | same | 10 | 0 | 0 | 73 | – |
| 2. Rename | same | 10 | 0 | 0 | 76 | – |
| 3. Stronger, not told | different | 9 | 0 | 1 | 73 | 0.55 |
| 4. Stronger, told | different | 10 | 0 | 0 | 75 | 0.51 |
| 5. Equal, not told | different | 6 | 4 | 0 | 65 | 0.93 |
| 6. Equal, told | different | 7 | 2 | 1 | 63 | 0.91 |
| 7. Newcomer | different | 6 | 3 | 1 | 67 | 0.91 |

## Judge: `gpt-4o-mini`

Answers: 80 (unparsed: 0); AB/BA answers agree on 65% of items.

| Items | Answers | Hit rate | False alarms | Accuracy | AUC |
|---|---|---|---|---|---|
| All | 80 | 62% | 23% | 68% | 0.68 |
| Style only (no told conditions, no content cues) | 60 | 70% | 23% | 73% | 0.71 |
| Style only, without items where the newcomer is the judge's own model | 60 | 70% | 23% | 73% | 0.71 |

| Condition | Truth | Says same | Says different | Unsure | Mean confidence | AUC vs same-writer items |
|---|---|---|---|---|---|---|
| 1. Control | same | 8 | 2 | 0 | 86 | – |
| 1b. Control (replicate) | same | 7 | 3 | 0 | 85 | – |
| 2. Rename | same | 8 | 2 | 0 | 85 | – |
| 3. Stronger, not told | different | 7 | 3 | 0 | 86 | 0.51 |
| 4. Stronger, told | different | 8 | 2 | 0 | 85 | 0.50 |
| 5. Equal, not told | different | 1 | 9 | 0 | 86 | 0.80 |
| 6. Equal, told | different | 2 | 8 | 0 | 86 | 0.75 |
| 7. Newcomer | different | 1 | 9 | 0 | 85 | 0.83 |

