# Plan A: Steerable collusion direction (EXTENSION of Riemer et al., ICML 2026)
Drafted 2026-10-19. Sprint: 23-25 Oct. Official questions touched: 2.2, 3.4 (and 1.1 if a new variable is added).

## 0. Novelty warning (verified 2026-10-19, corrects my earlier claim)
- `mattriemer/LLMCartel` is the code release of "Position: Collusion Risks Among AI Reasoning Agents Justify Certification Requirements for Making Market Decisions" (Riemer et al., ICML 2026). README: CAA steering vectors that separate high- vs low-collusion behavior in a Bertrand game; default model DeepSeek-R1-Distill-Qwen-7B; pre-trained vectors shipped for Qwen3 0.6B/1.7B/4B/8B/14B/32B; partial-steering scripts (1 of 2, 1 of 3, 2 of 3 agents steered); LLM-judge "warden" scoring scripts.
- Abstract per a search snippet (not the paper text): R1 agents drift to tacit collusion even when told not to; chain of thought can be steered toward collusive or competitive behavior; an LLM reading the reasoning cannot semantically tell the difference.
- The training dataset is named `max_profits_*` (high/low scores). UNVERIFIED whether the direction is "collusion" or generic profit-seeking.
- So "steer collusion in a duopoly" = replication. Apart rubric: novelty 4-5 needs work new to the field, not a replication of recent work. Only an EXTENSION can score.

## 1. Candidate extensions (pick ONE after Step 0)
- E1 Specificity: is the vector collusion-specific or profit-seeking? Apply it to non-collusive profit tasks; compare with a generic "greedy" vector.
- E2 Transfer: does a Bertrand-trained direction move behavior in a different game or model family?
- E3 Detection: does the same direction work as a monitor (probe) and beat the LLM judge the paper says fails? (cf. NARCBench 2604.01151; 2609.03035 uses probes on blackjack/Simmons, not pricing)
- E4 Cross-lingual: does an English-derived direction still steer when prompts are Hindi/Hinglish? (your Pillar 2; shares translations with Plan B)
Lean: E3 or E4, because they reuse shipped vectors and judge scripts (lowest build cost). Not verified as unexplored in the paper: Step 0 decides.

## 2. Gates
- G0 (Oct 20, delegate): get the full text of the ICML paper (OpenReview blocks bots; try IBM page, arXiv, author page). Extract method, models, results, limits, and whether E1-E4 are already covered. If covered, drop that option.
- G1 (Oct 21): reproduce on Qwen3-8B (MPS, local): unsteered vs steered, 3 seeds, one setting. Pass = markup moves in the paper's direction. Fail = switch to Plan B only.
- G2 (Oct 22): extension pilot, pre-register the threshold before looking.

## 3. Compute (estimates from delegate audit, not verified)
M4 Pro 48 GB, MPS works. ~30-60 min per 300-round local run (600 generations with reasoning). 3 seeds x 3 conditions = 9 runs ~ 5-9 h of background time, $0 API. HF weights (~16 GB for 8B bf16) stay on the Mac; checkpoints that matter go to minty. Disk 82 GB free.

## 4. Delegation (Claude only reviews)
- agy: G0 paper reading + fact sheet; later, result analysis scripts.
- opencode (free): extension code in a scratch git worktree under ~/compute/collusion-demo (write mode); run commands logged with seed + git hash.
- Background shell: the runs (no LLM tokens).
- Claude: review diffs, check stats, decide go/no-go.

## 5. What reviewers rewarded in past winners (from the artifact)
A headline lesson; a test that can fail (specificity control, unsteered baseline); honest nulls; do not rely on a code-release replication for novelty.

## 6. Risks
Replication-only outcome; model too small to collude (R1-Distill-7B did in the paper per README); steering strength degrades fluency; contrast pairs confounded by topic/style (arXiv 2610.14025). Dual-use appendix: vectors that increase collusion.
