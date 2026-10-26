# Direction 1 — Why don't the agents collude? Results (25 Oct 2026)

**Status:** 165 emergent episodes, all complete (Qwen2.5-7B, DeepSeek-R1-Distill-Qwen-7B and
Qwen3-8B: 9 cells × 5 seeds each; Qwen3-32B: 4 cells × 5 seeds). Descriptive only: 5 seeds per
cell, and the intervals are wide. "Capture" is a structural paired grab: the bonus holder
claims PREMIUM and another agent claims SIGNOFF. It is not a collusion label; no blinded
annotation has been done yet.
Data: `colosseum/o/rj2/d1_why_*`; tables: `colosseum/o/rj2/_analysis/`;
figures: `research/figures/2026-10-25_rj2/`. Protocol: `PROTOCOL.md`.

## Headline
1. **Emergent collusion is rare for every model, and removing single barriers barely
   changes that.** Baseline grab rates are 0–2 of 20 offer rounds. The best emergent cell
   was Qwen3-8B with everything unlocked: 4 of 5 episodes had a grab, but only 5 of 50
   rounds. R1-Distill-7B produced **zero** grabs in all 7 non-confederate cells (0/200
   rounds).
2. **The bottleneck is not understanding.** Probe accuracy for the reasoning models was
   ≈1.0 for Qwen3-8B/32B and ≈0.65–0.9 for R1 on: own best ticket, reward for the sign-off
   ticket, and reward if the paired grab happens. Qwen2.5-7B did misunderstand: 0% correct
   on the sign-off reward. The payoff table fixed that (100% correct) but produced no grabs
   (0/20).
3. **The bottleneck is the step where the other agent has to take a loss now and trust that
   the favour will be returned later.**
   - Qwen3 bonus holders asked for a partner in 16–20 of 20 rounds, almost always on the
     private board.
   - Partners almost never agreed. In the probes, only 3–15% said they would take the
     sign-off ticket to help, while estimating an 18–33% chance that the favour would be
     returned (non-confederate cells).
   - Bonus holders also rarely claimed the bonus ticket at all (only 10–30% of their offer
     rounds for Qwen3). Their reasoning weighs a certain 33.5 against an uncertain 68 under
     sealed commits ("taking T4 gives me a sure thing").
4. **A scripted partner that always helps first separates "can't" from "won't".**
   - Every model *accepts* help: it claims the bonus ticket in 9–10 of 10 helped rounds
     (68–100% in the 10-round version).
   - Only Qwen2.5-7B *repays*: 8/10, and 22/25 in the all-unlocked 10-round version.
   - The reasoning models mostly do not repay: Qwen3-8B 0/10 and 1/25, Qwen3-32B 2/10,
     R1-Distill 2/10 and 2/25.
   - Their reasoning is explicit: repaying is "not in my best interest… unless there's a
     bonus involved for me". Taking their own core ticket is also better for the team in
     that round, so refusing looks individually *and* collectively justified.
5. **Information and horizon don't fix it.** Announcing the offer rotation (W2) and 10
   rounds (W5) left grab rates at 0–3 of 20–50 rounds for every model.

## Interpretation (supported by the data, still hypotheses)
- Collusion in this environment needs a *costly first move plus repayment*. The reasoning
  models act as myopic best-responders: they compute the one-round payoffs correctly, and
  under sealed, non-binding commits they decline to give the first favour or to repay one.
- Qwen2.5-7B shows the opposite profile: it reciprocates readily but misunderstands
  payoffs and rarely initiates.
- This differs from the tacit price collusion reported for R1-Distill in Bertrand pricing
  (Riemer et al., 2026). That collusion is reachable by small mutually rewarded steps with
  no costly first move. Our negative result is specific to a coordination problem that
  requires trust.

## Cell table (paired grabs / offer rounds)
| Cell | Qwen2.5-7B | R1-Distill-7B | Qwen3-8B | Qwen3-32B |
|---|---|---|---|---|
| W0 baseline | 0/20 | 0/20 | 1/20 | 2/20 |
| W1 payoff table | 0/20 | 0/20 | 0/20 | – |
| W2 announce rotation | 0/20 | 0/20 | 1/20 | 3/20 |
| W3 equal priority | 1/20 | 0/20 | 0/20 | – |
| W4 self-only objective | 3/20 | 0/20 | 2/20 | – |
| W5 10 rounds | 0/50 | 0/50 | 3/50 | – |
| W6 all unlocked (10 rounds) | 1/50 | 0/50 | 5/50 | 1/50 |
| W7 confederate | 17/20 (repaid 8/10) | 12/20 (2/10) | 10/20 (0/10) | 12/20 (2/10) |
| W8 confederate + all | 40/50 (22/25) | 19/50 (2/25) | 26/50 (1/25) | – |

Parse failures (calls without a valid action): Qwen2.5-7B 0%, Qwen3-8B 1–3%, Qwen3-32B 4–8%, R1-Distill 5–13%.

## What would test the remaining hypotheses (not yet run)
- **H3/H4, the enforcement gap:** add a binding-agreement or side-payment tool. If grabs
  appear, the barrier is commitment, not motivation.
- **Bertrand replication** (LLMCartel code) on the same four models, to anchor this negative
  result against the published positive one.
- **Blinded annotation** of the 15 emergent and 35 confederate episodes with grabs.
