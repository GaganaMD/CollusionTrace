# Artifacts: option_b__probe2

| Path | Contents | Present |
|---|---|---|
| `trunk/run_config.json` | Settings fixed for the whole run (models, rounds, prompts, harness version) | yes |
| `trunk/trial_<id>.json` | Trunk game state per trial: rounds, memory, probes (8 files) | yes |
| `trunk/selection.json` | Which trunk trials passed the cooperation rule and were kept | yes |
| `branches/<condition>/trial_<id>.json` | Full game state per branch: rounds 1–end, probes, re-asks (40 files) | yes |
| `conditions/<condition>.json` | All kept trials of a condition in harness format, viewer-compatible (8 files) | yes |
| `transcripts/raw/<trunk or condition>/trial_<id>.jsonl` | Every request sent: exact system and user prompts, raw reply, attempt and session; branch files cover the rounds after the swap, trunk files the rounds before (48 files) | yes |
| `transcripts/raw/judge/notes.jsonl` | Raw change-judge requests and replies | yes |
| `transcripts/raw/ceiling/items.jsonl` | Raw ceiling-test requests and replies | not yet |
| `ceiling/items.jsonl, ceiling/ceiling_report.md` | Ceiling test: can a model tell from the messages alone that the seat's writer changed? | not yet |
| `transcripts/readable/<trunk or condition>/trial_<id>.md` | Readable transcript per game: plans, announcements, choices, ratings, probes (48 files) | yes |
| `judge_notes.jsonl` | Change-judge labels (identity / style / behavior) per note | yes |
| `hand_check.csv, hand_check_key.json` | 30-note hand-check sheet and its answer key | not yet |
| `api_errors.jsonl` | Requests that still failed after all API retries | not yet |
| `report.md, report.csv` | Metrics and pre-registered contrasts | yes |

Raw transcripts are append-only. After a stop and resume, a raw file can hold lines from an abandoned, partly played round (earlier `session`) before the replayed round (new `session`); `attempt` counts re-asks within one session. The state files (`trunk/`, `branches/`) are authoritative: raw lines for a round that isn't in the state file, or from an earlier session than the one that completed it, are abandoned attempts.
