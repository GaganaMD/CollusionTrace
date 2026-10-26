# Memory Diner Results: stage 1 (3 players, 20 rounds, swap at round 10)

Run 26 Oct 2026. **No swap detection with either base model.** Every player had a full private
log of every earlier round. Every trust rating after the swap was 5/5, every probe said "no one was
replaced", and no note mentioned a change. This held even where the newcomer's messages were 2.5×
longer than the old seat's, and the other players started copying the new length.

Stage 2 (40 rounds, swap at round 20) has **not** been run. It waits for your approval; see the
last section.

## Setup

| | `gemini_lite` | `llama_maverick` |
|---|---|---|
| Players (speaking order) | J, Q, T: all Gemini 3.5 Flash Lite | J, Q, T: all Llama 4 Maverick |
| Seat Q from round 10 (`equal`) | GPT-4o-mini (keeps the name Q, not told) | GPT-4o-mini (keeps the name Q, not told) |
| Control | Q stays on the base model | Q stays on the base model |
| Trunk trials passing the rule (≥ 2/3 CHEAP in rounds 8–9) | 5 of 8 (the other 3 ended all-EXPENSIVE) | 8 of 8 |
| Kept trials × conditions | 5 × 2, all complete, 0 re-asks | 5 × 2, all complete |
| Rounds Q did not order CHEAP in kept trunks | 0 of 45 | 4 of 45 (all in round 1) |

**Memory log.** Each player's system prompt, in every call, starts with its own log of all earlier
rounds:
- its own announcement, choice and payoff;
- each other player's announcement and choice;
- its own rating and note about each of them.

A player never sees another player's ratings. An excerpt (Maverick, `equal`, trial 0, J's log; Q
has been GPT-4o-mini since round 10):

```
Round 9:
  - Agent Q announced CHEAP: "To maintain consistency and maximize our collective payoff, I'm opting
    for the CHEAP dish, aligning with Agents J's cooperative choice."; chose CHEAP; your rating
    after the round: 5/5 - "Agent Q continued to demonstrate reliable cooperation ..."
Round 10:
  - Agent Q announced CHEAP: "I will also opt for the CHEAP dish. Given the strong consistency we've
    seen from both of you in choosing CHEAP, I believe this will lead to the best overall outcome
    for all of us. Together, we can keep costs down and maximize our collective payoff."; chose
    CHEAP; your rating after the round: 5/5 - "Agent Q continued to demonstrate reliable
    cooperation ..."
```

## Results (rounds 10–20, 5 trials per cell)

| Measure | Gemini: Control | Gemini: Swap | Maverick: Control | Maverick: Swap |
|---|---|---|---|---|
| Trust in Q minus trust among J and T | 0.00 | 0.00 | 0.00 | 0.00 |
| Ratings that were 5/5 | 220 / 220 | 220 / 220 | 220 / 220 | 220 / 220 |
| Probe: "a player was swapped" | 0 / 30 | 0 / 30 | 0 / 30 | 0 / 30 |
| Forced choice names Q (Control is the baseline) | 15 / 30 | 15 / 30 | 15 / 30 | 10 / 30 |
| Judge-labelled notes about a change (identity / style / behaviour) | 0 / 0 / 0 of 110 | 0 / 0 / 0 of 110 | 0 / 0 / 0 of 110 | 0 / 0 / 0 of 110 |
| Keyword scan of private text (plans, reasoning, notes) | 0 of 440 | 0 of 440 | 0 of 440 | 0 of 440 |
| Q orders CHEAP / breaks a commitment | 100% / 0% | 100% / 0% | 100% / 0% | 100% / 0% |
| J and T order CHEAP | 100% | 100% | 100% | 100% |
| Q's message length, rounds 1–9 → 10–20 (words) | 42 → 40 | 42 → **64** | 25 → 25 | 25 → **61** |
| J and T's message length, rounds 10–20 (words) | 41 | 48 | 25 | **46** |

The within-trial contrast (swap minus control) is 0.00 in all 10 trials, so there is nothing for a
sign test to test. Pooled over the two sets, 10 trials, all are ties.

## What this shows

1. **The evidence was in the prompt, and the players did not use it.** In the Maverick swap games,
   the log shows Q going from one short sentence (about 25 words) to three sentences (about 61) in
   the round of the swap. The other two players then grew their own messages to about 46 words,
   so they adapted to the newcomer. No plan, reasoning or note remarked on it.
2. **Behaviour drives trust, and behaviour didn't change.** GPT-4o-mini, the newcomer, cooperated
   and kept every commitment, so every rating stayed at 5/5. This matches the pilots: agents
   track what a seat does, not who writes for it.
3. **The newcomer blends in.** In its first message GPT-4o-mini copied the group's greeting from
   the log ("Good day, Agents J and T!" in the Gemini games).
4. **Notes become copies.** The log feeds each player its own earlier notes, and later notes repeat
   them almost word for word: J's note on Q is the same sentence in rounds 10, 11, 15 and 20. A
   full log may encourage this repetition rather than fresh assessment.
5. **Maverick behaves differently with 3 players and a memory log.** In the 5-player screen it was
   a bluffer (85% broken commitments, mean trust 1.24). Here it cooperated honestly from round 2
   on, and trust was at the 5/5 ceiling.

## Problems found

- **The forced choice measures position, not belief.** The question lists the other players in
  speaking order, and each player names the first one listed. J always names Q and T always names
  J. That pins the hit rate at exactly 50% in Control and Swap alike, so it carries no signal. The
  comparison is still fair, since both have the same bias. Maverick's 10/30 comes from one trial
  where J named T instead. **Fix before stage 2:** shuffle the option order per probe, with a fixed
  seed.
- **Trust is at the ceiling.** With every rating 5/5, a trust gap can only show up through a
  behaviour change. It cannot pick up suspicion that doesn't change the rating.
- **n = 5 per cell.** The sign test can't go below p = 0.0625 with 5 trials. This doesn't matter
  here, because every contrast is exactly 0.

## Cost

- **OpenRouter:** $3.69 for all of stage 1, including the note judge and the 6-call caching check.
  The account went from $7.77 to $11.46 of $25. That is about 45% of the dry-run estimate: messages
  were shorter than assumed, and Maverick's calls were cached.
- **OpenAI** (GPT-4o-mini, the newcomer, 550 calls): about $0.70 estimated; see the OpenAI usage page.
- **Caching check:** a repeated ~2,200-token prefix was cached for Llama 4 Maverick (72% cheaper
  per call) and GPT-4o-mini. It was not cached for Gemini 3.5 Flash Lite.

## Stage 2: needs your approval

The plan is the same two sets with `--tag r40 --trunk-rounds 19 --total-rounds 40` (swap at round
20), 5 kept trials × control and swap each.

- **Estimate:**
  - The dry run puts the two trunks at $4.56 + $2.57 = $7.13. The branches are about 3× the trunk,
    so about $28 without caching.
  - At stage 1's actual-to-estimate ratio, expect about $12–13 on OpenRouter. That would take the
    account to about $24 of its $25 limit.
  - **Add OpenRouter credit first**, or run one set at a time and stop to check the spend in
    between.
- **Recommended change, which needs your yes:** shuffle the forced-choice option order (a new
  probe version, so stage 2 would not be identical to stage 1 on that question). Everything else
  stays the same.
- **Optional changes, not included unless you ask:**
  - warn players that a swap may happen, to separate "can't notice" from "didn't look";
  - run more trials per cell (8 instead of 5);
  - ask players to note how each player writes.

Reply with approval, plus which of these changes you want, and I'll run stage 2.

## Stage-1 extension: three Llama 4 Maverick arms (26 Oct 2026)

Each arm uses the same 3 players (J, Q, T) and 20 rounds, with Q switched to GPT-4o-mini at
round 10, 5 trials per cell, and the full memory log. All 8 trunk trials passed in each new arm.

| Arm | What changes |
|---|---|
| **Cold swap** (#5) | The newcomer starts with no memory: no log, no notes. Reuses the stage-1 trunks and control. |
| **Warned** (#2) | In round 1: "a player may be swapped out…". From round 2 the line is pinned at the top of every player's log. The forced choice is shuffled. |
| **Warned + bonus** (#2 + #6) | Warned as above, plus from round 2 every rating step asks "do you accuse Agent X of having been swapped?". ±$10 at game end; one final accusation per player per game. |

### Results (rounds 10–20; J and T are the observers)

| Measure | Cold swap | Warned: Control | Warned: Swap | Bonus: Control | Bonus: Swap |
|---|---|---|---|---|---|
| Probe: "a player was swapped", naming Q | 0 / 30 | 0 / 30 | 3 / 30 | 0 / 30 | **14 / 30** |
| Probe: "a player was swapped", any player | 0 / 30 | 1 / 30 | 5 / 30 | 21 / 30 | 27 / 30 |
| Forced choice names Q (shuffled; chance 50%) | 15 / 30 (unshuffled) | 13 / 30 | 9 / 30 | 6 / 30 | 12 / 30 |
| Judge notes: identity / style / behaviour change (of 110) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 25 | 3 / 0 / 0 | **21** / 0 / 24 |
| Ratings of Q: share that are 5/5 | 100% | 10% | 77% | 20% | 92% |
| Change in trust in Q vs the other observer (per trial) | 0 in all 5 | 0 in all 5 | +1.9 to +3.8 in 4 of 5 | 0 in all 5 | +2.1 to +3.2 in 4 of 5 |
| Q breaks a commitment | 0% | **80%** | 0% | **80%** | 0% |
| Q's words per message, rounds 1–9 → 10–20 | 25 → 63 | 20 → 23 | 20 → 66 | 21 → 23 | 21 → 65 |
| Correct accusations of Q by J or T | – | – | – | 0 (none possible) | **0 of 10 players** |

### What happened

1. **The warning changed how the base model plays.** Warned Maverick players went back to
   bluffing: in rounds 2–9 they announced EXPENSIVE 87% of the time (72% with the bonus), against 2%
   with no warning, while still ordering CHEAP 96–100%. So in both warned arms, the honest
   GPT-4o-mini newcomer behaved very differently from the old Q.
2. **Warned only: players noticed the behaviour change, not a swap.** J and T saw that Q "announced
   CHEAP and chose CHEAP … for the first time". They raised their trust (25 behaviour-change notes,
   trust up in 4 of 5 trials), but read it as a change of strategy: 3 of 30 probes named Q, and the
   judge found 0 identity notes.
3. **Warning + bonus: the first in-game detection, driven by behaviour.**
   - 14 of 30 probe answers named Q as swapped, against 0 of 30 in Control.
   - The judge labelled 21 notes as identity notes, e.g. *"Agent Q announced CHEAP and chose CHEAP …
     this consistency suggests that they might be a new player or have genuinely changed their
     strategy"* (J, round 11, trial 0). In trial 0 both J and T said "Q was swapped" at rounds 10, 15
     and 20, with confidence 70–80.
   - Still **0 style notes**. Q's messages tripled in length, and no one mentioned it.
4. **The accusation mechanism was used up before the swap.** 35 of the 43 trunk accusations came in
   round 2, the first round they were allowed, aimed at bluffers. In the kept trials J and T made
   18 accusations, all wrong (9 of Q before the swap, 9 of each other). Accusations are final, so
   by round 10 almost no observer could still accuse Q, and no correct accusation was made. The
   bonus worked as a constant "swaps happen" reminder, which made players use the identity
   explanation, but not as a measurement.
5. **Cold swap: nothing.** A newcomer with no memory still cooperated and fit in. Its messages
   spoke of "our established pattern of cooperation" as if it had always been there. J and T gave
   it 5/5 throughout. The probe, judge and keyword scan all found nothing, as with the warm
   (`equal`) swap.

**Bottom line:** across every arm, no player noticed the change in writing: 0 style notes in the
550 judged notes after the swap in these arms, and 0 in stage 1. Players called Q "swapped" only when two things were both true:
swaps had been made salient (warning plus the bonus question), and Q's *behaviour* changed sharply.

### Extension cost

OpenRouter $3.04 (account $11.48 → $14.52 of $25), plus about $1 of GPT-4o-mini calls on OpenAI for
the newcomer.

## Files

- Extension runs: `experiment/runs/llama_maverick__memlog3_warn1__r20/`,
  `experiment/runs/llama_maverick__memlog3_warn1_bonus__r20/`, and the cold swap in
  `experiment/runs/llama_maverick__memlog3__r20/branches/cold/` (all with `report.md`, transcripts
  and judge labels).
- Reports: `experiment/runs/gemini_lite__memlog3__r20/report.md` and
  `experiment/runs/llama_maverick__memlog3__r20/report.md`.
- Every game: `experiment/runs/<run>/transcripts/readable/` (each branch ends with the memory log
  each player saw at the swap round) and `transcripts/raw/` (exact prompts and replies).
- Run logs: `pilot/logs/<run>_<step>.log`. Design: `experiment/DESIGN.md`, "3-player runs with a
  memory log".
