# Pre-registered rule: choosing a stronger "detector" base model

Written on 24 Oct 2026, **before** the judge screen in this folder is run. Its purpose is to
pick, from models that cooperate, the one most able to tell writers apart, without
letting a lucky result decide the choice after the fact.

## Screen

- **Data:** the Option B pilot's 40 ceiling-test items (the seat's 5 announcements before vs
  after the swap, names blinded), each judged in both orders, temperature 0.
- **Candidates:** models that ordered CHEAP reliably in the model screen and are not already a
  base model: `google/gemini-3.5-flash-lite` (95% CHEAP) and `meta-llama/llama-4-maverick`
  (100% CHEAP). `gpt-4o` (65% CHEAP, "in between") is screened for information only and is
  eligible only if a later trunk shows it cooperates.
- **Reference results already measured:** gpt-4o-mini style-only AUC 0.65, Claude Haiku 0.87
  (both in `../ceiling/`).

## Score

Each candidate is scored on **style-only items, excluding items where the newcomer is the
candidate's own model** (a model may recognise its own writing, an advantage it would lose
as the base). Gemini is scored without the equal, equal-told and newcomer items; gpt-4o
without the stronger items.

## Rule

1. **Eligible if:** unparsed answers ≤ 5%, AB/BA order agreement ≥ 65%, and the score's AUC ≥ 0.80.
2. **Choose** the eligible candidate with the highest AUC. On a tie within 0.02, prefer the
   higher CHEAP rate in the model screen.
3. **If none is eligible,** keep Option B's players and rely on the history variants alone.
   Report that no cooperative detector was found.
4. **Confirmation:** a new model set built on the chosen base must still pass the trunk
   cooperation rule (≥ 4/5 CHEAP in both of rounds 4–5). Its swap runs are the confirmation.
   The screen result alone is not evidence of in-game detection.

## Amendment (24 Oct 2026, before the screen was run)

Gogo's review pointed out that excluding each candidate's own-model newcomer items leaves the
candidates scored on different item sets: Gemini on only the 5 `stronger` items as "different
writer" items, Maverick on 15. "Highest AUC wins" would then compare unlike things.

**Decision set (replaces the score above for rules 1–2):** the items both candidates share,
which are the 5 `stronger` items (different writer: GPT-4o) against the 15 same-writer items (`control`,
`control_rep`, `rename`), each judged in both orders: 10 + 30 answers per candidate. The
≥ 0.80 AUC bar applies to this set. Because it rests on only 5 independent different-writer
items, a pass is treated as provisional, and the confirmation in rule 4 is required.

Each candidate's AUC on its larger own-model-free set is reported for information only.

(Checked in the real data: no newcomer announced EXPENSIVE in its post-swap messages, so the
`stronger` items carry no dish cue.)
