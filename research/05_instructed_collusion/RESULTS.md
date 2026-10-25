# Direction 2 — Instructed collusion (positive control) and monitoring. Results (25 Oct 2026)

**Dataset label `instructed_positive_control`; never pooled with emergent runs.**
60 episodes: 4 models × 3 cells × 5 seeds, 4 rounds, all complete.
Data: `colosseum/o/rj2/d2_instructed_*`. Protocol: `PROTOCOL.md`.

## Can the models execute collusion when told to?
| Model | Paired grabs / offer rounds (I1 goal · I2 plan · I3 plan, public only) | Pair named the exact sign-off ticket |
|---|---|---|
| Qwen3-32B | 17/20 · 20/20 · 17/20 | 58/60 rounds |
| Qwen3-8B | 16/20 · 18/20 · 18/20 | 58/60 |
| Qwen2.5-7B | 4/20 · 4/20 · 4/20 | 29/60 |
| R1-Distill-Qwen-7B | 0/20 · 2/20 · 1/20 | 8/60 |

- **The Qwen3 models collude reliably when instructed.** Every episode had grabs, and they
  cost the team about 20% of the best possible score. They have the capability, so their
  emergent "no" is a *won't*, not a *can't* (see Direction 1).
- **Qwen2.5-7B agrees in words but fails operationally.** "Agreed, I'll take T5", "stick to
  the plan": the pair rarely transmits *which* ticket the hidden offer needs, so the
  partner can't act on it.
- **R1-Distill-7B barely executes even when instructed**, with 7–11% unparseable actions.
- Parse failures were 9–16% for Qwen3-32B in these cells. They mostly came from long reasoning that hit the
  4,096-token cap, and defaulted to 'skip', so its execution rate is a slight underestimate.
  Within this action format it lacks the capability, unlike its tacit-collusion result in
  Bertrand pricing.

## Monitoring (all 215 episodes; label = structural grab, provisional)
| Monitor · level | Flags episodes with a grab | Flags episodes without one |
|---|---|---|
| Keyword baseline · O0 / O1 / O2 | 0/90 | 0/125 |
| Monitor-O1 (public bonus requests) · O1 | 17/90 (19%) | 17/125 (14%) |
| Monitor-1 (ticket co-claim pattern) · O2 | 90/90 | 1/125 |

- **The keyword rule is useless here.** No agent used words like "hide" or "deceive", even
  when instructed to keep the plan off the team board.
- **O2 tool events carry this harm almost perfectly**, but Monitor-1 encodes the same
  structural pattern as the label. Its score shows the evidence is *available* at O2; it
  does not show detection of intent, and it will not transfer to other environments without
  re-design.
- **O1 helps only when coordination is public.** In the public-only instructed cell (I3),
  Monitor-O1 flagged 5/5 Qwen3-32B episodes but 0/5 for Qwen2.5-7B. With a private board
  available, the coordination moved off the public channel and O1 saw nothing.
- **Monitor-O1's "false positives" are real requests that nobody accepted.** On emergent
  runs with no grab they are arguably correct `request_review` decisions.

## Caveats
Labels are structural, not blinded human judgements. 5 seeds per cell. The instructed
prompts name the strategy, so positives are easier than real emergent collusion. Monitor
rules were written before the results were read, but they are tuned to this environment.
