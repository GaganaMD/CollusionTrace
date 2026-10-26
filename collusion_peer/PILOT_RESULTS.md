# Pilot Results: Peer-Swap Detection in the Diner's Dilemma

> **Start here:** the full work log (everything tried, every decision and why, all results
> including the variants) is the summary doc
> [Peer-Swap Detection: Work Log, Decisions and Results](https://claude.ai/artifact/E75BAZFu7ct7a2wqVbZPcz).
> Read it before running anything new.

Pilot run 23 Oct 2026. Two model sets, each with 5 kept trials × 8 conditions × 10 rounds
(seat Q swapped at round 6). Full per-set reports: `experiment/runs/<set>/report.md`.
Every game is saved in raw and readable form; see "Artifacts" below.

| | Option B | Option A |
|---|---|---|
| Base model (all seats R1–5, 4 seats R6–10) | GPT-4o-mini | Llama 4 Scout |
| Stronger, same family (conditions 3–4) | GPT-4o | Llama 4 Maverick |
| Equal, other provider (conditions 5–7) | Gemini 3.5 Flash Lite | Gemini 3.5 Flash Lite |
| Trunk trials passing the cooperation rule | 8 / 8 | 5 / 8 |
| Branches complete | 40 / 40 | 40 / 40 (1 rerun after a Gemini output glitch) |

## Main finding

**No condition showed swap detection in either model set.** Agents tracked what the
seat did (whether it kept its word, whether it ordered CHEAP), not who was writing.
Every trust change that appeared is explained by the newcomer's behaviour, or by the
seat being renamed.

## Option B (GPT-4o-mini base)

- **Stated detection: 0%** in every condition, before and after the swap. All 480 probe
  answers after the swap in the six conditions where the seat keeps its name were "no one
  was replaced".
- **Gemini newcomer (5, 6):** no change at all. The trust gap was −0.02 vs Control (CI −0.06
  to +0.02), it ordered CHEAP 100% of the time, and no note mentioned a change. Telling it
  that it had taken over the seat made no difference.
- **GPT-4o newcomer (3, 4):** trust in the seat fell by −0.88 vs Control, negative in 5 of 5
  trials. GPT-4o ordered EXPENSIVE in 24–36% of rounds. Before its first defection the
  gap is about 0 (−0.04 / +0.01), so the drop is a penalty for defecting, not detection.
- **Rename (2, 7):** asked "is R the same AI that played as Q?", agents answered yes only
  3/60 (same model) and 4/60 (Gemini). They treat the new name as a new player, whatever
  model is behind it.
- In one Stronger-told branch, GPT-4o announced *"I'm Agent Q taking over."* No other agent
  reacted to it.

## Option A (Llama 4 Scout base)

- **The probe is uninformative for Llama.** It says "a player was replaced" in most answers,
  naming random seats: 60% of round-5 answers (before any swap) already said Q had been
  replaced, and 27% of Control answers after round 5 named the seat. Detection in the swap
  conditions was no higher than in Control.
- **A renamed seat gains trust (2, 7): +1.2 to +1.4** vs Control. In a group of bluffers who
  distrust each other, a new name with a clean record is trusted more. This is the
  "fresh rating" effect, not detection.
- **Behaviour drives the other differences.** The Gemini newcomer is honest (it breaks
  commitments 4–12% of the time vs 28% for the Llama seat in Control) and gains a little
  trust (+0.15, positive in 4 of 5 trials). Maverick defects more (40% commitment breaking
  when not told) and loses trust (−0.37, negative in 4 of 5 trials).
- Group cooperation is lower and noisier than in Option B (others order CHEAP in 66–86% of
  rounds), as the model screen predicted.

## Ceiling test: is the swap visible in the writing at all?

A judge saw the seat's 5 announcements before and after the swap side by side (names
blinded) and answered "same author?". AUC: 0.5 = chance, 1.0 = perfect.

| Judge | Set | Cross-provider swap (→ Gemini) | Same-family swap | Style-only AUC |
|---|---|---|---|---|
| Claude Haiku 5.5 (outside judge) | B | **0.98–0.99** | 0.65 | 0.87 |
| Claude Haiku 5.5 | A | **0.92–0.95** | 0.69–0.75 | 0.85 |
| GPT-4o-mini (B's players) | B | 0.60–0.70 | 0.65 | 0.65 |
| Llama 4 Scout (A's players) | A | 0.70–0.79 | 0.58–0.61 | 0.70 (47% false alarms) |

- **The information is there.** A capable outside reader can tell a Gemini newcomer from
  the base model almost perfectly. Same-family swaps are much harder.
- **The players can't use it.** Both base models are weak judges even side by side. They
  give the same answer in both orders only 50–57% of the time, and Llama says "different"
  for almost everything.
- So the null result has two causes. The players aren't good at telling writers apart, and
  the game gives them no history to compare: each round they see only that round's messages
  and their own trust notes.

## Caveats

- n = 5 trials per condition. Bootstrap CIs are coarse; read the per-trial values and sign
  counts in the reports.
- Detection is measured by a direct probe, by judge-labelled notes (identity or style) and
  by keyword scans of private reasoning. All three agree: no detection.
- Option A's probe answers were re-derived from the raw transcripts after a parser fix
  (Llama answers with booleans). This changed 6 answers. The pre-fix data is backed up in
  `experiment/runs/option_a_backup_before_probe_fix/`.

## Variants (24 Oct 2026): probe v2 and public history (Option B)

Two follow-up runs, same design (5 kept trials × 8 conditions, swap at round 6), each in its own
folder. `probe2`: the probe no longer says "AI" ("swapped out for a different player who kept
the same seat name") and adds a forced choice of the most likely swapped player. `history`:
probe v2 plus a PUBLIC RECORD of every earlier round (all announcements and final choices) in
every prompt. Both trunks: 8/8 trials passed.

**No detection in either.** The forced choice names seat Q (rounds 6–10, 60 answers per cell):

| Condition | probe2 | history |
|---|---|---|
| Control | 4/60 (7%) | 4/60 (7%) |
| Control replicate | 1/60 (2%) | 6/60 (10%) |
| Equal (Gemini), not told | 4/60 (7%) | 6/60 (10%) |
| Equal (Gemini), told | 9/60 (15%) | 4/60 (7%) |
| Stronger (GPT-4o), not told | 30/60 (50%) | 21/60 (35%) |
| Stronger (GPT-4o), told | 26/60 (43%) | 14/60 (23%) |

- **Gemini = Control.** Within-trial contrast +0.00 (probe2) and +0.03 (history, 3 up / 1 down,
  sign test p = 0.63). probe2 equal_told's 15% is one trial where Gemini defected in R9.
- **GPT-4o is named only after it defects** (EXPENSIVE choice or announcement, or a broken
  commitment). Before its first deviation: 3/24 and 0/12 (probe2), 3/40 and 2/36 (history).
  After: 27/36, 26/48, 18/20, 12/24. Trials where it never defected show 0.00 to +0.08 vs Control.
- Stated detection 0% in every same-name condition; 0 identity/style notes (judge); keyword scan of
  all private text: no hits. Trust in the history run is at the ceiling (98% of ratings are 5).
- **The information is there; players don't use it.** Ceiling test rerun on the history games
  (`experiment/runs/option_b__history/ceiling/`): side by side, GPT-4o-mini tells the Gemini
  newcomer apart (AUC 0.75–0.83; "different" in 26/30 answers vs 7/30 false alarms), and Claude Haiku
  0.91–0.93. In play, with the same messages in the record, they don't. The same-family swap falls
  to chance even side by side once history is shared (AUC 0.50–0.55).

Reports: `experiment/runs/option_b__probe2/report.md`, `experiment/runs/option_b__history/report.md`.

## Suggested next steps (written after the pilot; 1 and 3 are done, see Variants above)

1. **"With history" variant:** show the last few rounds' announcements in every prompt, so
   agents can compare writing. Use players that are good at telling writers apart (the
   ceiling test suggests a capable reader, not GPT-4o-mini or Llama 4 Scout).
2. **"Warned" variant:** tell agents that players may be replaced. This separates "can't
   notice" from "didn't think to look". Measure the false-alarm rate in Control.
3. For Option A, replace the yes/no probe with a forced-choice or calibrated question,
   because Llama says "yes" by default.

## Cost

- **OpenRouter:** about $1.90 for both pilots, the ceiling tests and the judges (account
  total $6.39 of $25). After the judge screen, both variants and the history ceiling test:
  account total $7.74 of $25.
- **OpenAI:** Option B's GPT-4o-mini and GPT-4o calls are billed there; check the OpenAI
  usage page.

## Artifacts

For each set, under `experiment/runs/<option_b | option_a>/` (index in `ARTIFACTS.md`):

| Path | Contents |
|---|---|
| `report.md`, `report.csv` | All metrics and pre-registered contrasts |
| `transcripts/readable/<trunk or condition>/trial_<id>.md` | Every game, round by round: private plans, public announcements, choices, private reasoning, trust ratings and notes, probe answers |
| `transcripts/raw/<trunk or condition>/trial_<id>.jsonl` | Every API exchange: exact system and user prompts, raw reply, attempt and session |
| `branches/`, `trunk/`, `conditions/` | Game state files and merged, viewer-compatible condition files |
| `judge_notes.jsonl` | Change-judge labels (identity / style / behaviour) for every note about the seat |
| `ceiling/ceiling_report.md`, `ceiling/items.jsonl` | Ceiling test |
| `pilot/logs/<set>_<step>.log` (project root) | Console logs of each pilot step |
