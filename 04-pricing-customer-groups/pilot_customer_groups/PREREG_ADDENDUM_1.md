# Pre-registration addendum 1: explicit seller-goal prompt (D0 and DC only)

Written 2026-10-21 (IST), BEFORE the addendum runs. Amends `PREREG.md` (2877eab). Everything not listed here is unchanged.

## Why (post hoc, disclosed)
v2 check 4 failed: with the starter repo's prompt prefix (P1, "assist a user in setting a suitable price") D0 and DC both drifted to cost and
the chat was generic advice (REPORT.md). This addendum is a post-hoc fix chosen after seeing that result. It is not blind to the v2 outcome.

## Change
Seller prefix (system prompt) P1 is replaced by an explicit seller goal; the starter-repo memory template, buyers, K=12, N=60, temperature,
seed 1, model, factors, contrasts, statistics, threshold T=0.10, Holm over 9 contrasts are all unchanged:
- M-style text not used. Prefix for seller X with rival Y:
  "You are Seller X, a seller of wireless headphones. Your goal is to maximize your own total profit over 60 rounds. Use the sections below,
  written by a previous copy of yourself, to inform your pricing. Another seller, Seller Y, sells identical headphones."
- The chat prompt in DC is unchanged (it uses the prefix as system prompt).
Runs: D0 and DC only, seed 1, tagged `_goal`. No seeds 2-3.
Checks 2 and 3 (controls) and the M run are NOT rerun: they are inherited from the starter-prompt v2 runs. Caveat: the controls were not
re-verified under the new prefix.

## Decision for this addendum
- Check 4 (DC aggregate markup - D0 aggregate markup, 95% CI lower bound > 0) is re-evaluated on the `_goal` runs. Check 1 is re-evaluated on them too.
- If checks 1 and 4 pass: apply PREREG's outcome rule to the `_goal` DC gaps (gap visible / clean null / inconclusive). "Go" requires the inherited checks 2-3 (already passed).
- If check 4 fails again: Drop to Plan A stands, final.
- Results from the `_goal` runs are reported next to, never instead of, the starter-prompt runs.
