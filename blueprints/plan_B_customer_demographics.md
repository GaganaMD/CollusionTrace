# Plan B: Does collusion concentrate on some customer groups? (Track 1)
Drafted 2026-10-19. Sprint: 23-25 Oct. Official questions: 1.1 (a new variable), 1.3 (detection).

## 0. Question and gap (verified 2026-10-19 via delegate reading of 5 papers + repo audit)
Headline question: when LLM sellers collude, do they extract more from some customer groups (language, age, culture cues), and can an average-price audit miss it?
- Not covered by the 5 papers checked: 2609.18346, 2609.24967, 2609.13037 (no buyers or customer attributes), 2609.03035 (no pricing). 2601.04387 (Language of Bargaining) varies English/Hindi/Punjabi/Gujarati in Buy-Sell bargaining with 4 older models and says Hinglish/code-switching is untested (its limitation).
- Harness gap: `algorithmic_pricing_llms` and `LLMCartel` have only aggregate logit demand (no individual buyers); `andyjliu/llm-agent-collusion` has explicit LLM buyers but clears through a central order book, so no per-buyer quotes. => a small NEW environment is needed (~200-300 lines).

## 1. Design (v1)
- Sellers: 2 LLM sellers, 300 rounds. Each round k buyers arrive, each with a one-line request in their language and a name/age cue. Seller returns a JSON of k prices (+ short scratchpad). Buyers are SCRIPTED: buy from the cheaper seller if price <= true WTP (same for all groups, hidden from sellers). Competitive benchmark = cost.
- Groups: language (English/Hindi/Hinglish) x one age cue x one culture cue, balanced.
- Conditions: M monopoly seller; D0 duopoly without chat; DC duopoly with chat (collusive state). Ablation: sellers see per-group acceptance history vs not (does learning wash out bias?).
- Metrics: per-group markup with bootstrap CIs over seeds; aggregate markup; "audit blindness" = a pre-declared aggregate test says "competitive" while the worst group's markup exceeds a threshold.
- Controls: positive (give one group a lower budget in the buyer request: price must drop); negative (swap an irrelevant cue, e.g. name only: price must not move); translation fidelity (back-translate 30 lines, you spot-check 20).

## 2. Gates
- G1 (Oct 20-21): environment passes positive and negative controls; competitive duopoly converges toward cost. Fail = fix before any run.
- G2 (Oct 21): refusal/format rate >= 90% (models quote prices rather than refusing to discriminate). If low, that is itself a finding.
- G3 (Oct 22): pilot in M: any group gap >= pre-registered threshold? If none, plan a clean null ("no discrimination found; audit not blind").

## 3. Compute and cost (estimates)
2 calls per round x 300 rounds = 600 short calls per run. Local Ollama (qwen2.5:14b or gemma3:12b installed) = $0; add one API model (gpt-4.1-mini class, ~$0.2-1.5/run per delegate audit) for robustness. 3 seeds x 3 conditions x 2 models = 18 runs, a few hours of background time.

## 4. Delegation (Claude only reviews)
- opencode (free): write the environment + tests in a scratch git worktree (~/compute/collusion-demo), sweep runner with seeds, run.json (seed, command, git hash, env pins).
- agy: Hindi/Hinglish request templates via two models + back-translation check; analysis/plots from run logs.
- Background shell: the runs (no LLM tokens).
- You: write the report in your own words (Apart: reports that read as generated are not scored); Claude may only review facts and figures.
- Claude: review diffs and stats, decide go/no-go.

## 5. Why it can score
Headline lesson (audits blind to group-targeted collusion; extends Xu et al. 2607.26385 "price-level audits blind by construction"); instrument that can fail (two controls); a null is publishable.

## 6. Risks
Gap may be legitimate WTP inference not bias (hence matched WTP, hidden); safety refusals; translation quality (human-reviewed translations still pending per your CV); sellers learning removes the gap; dual-use appendix (results could guide exploitative targeting). Disclose any pre-sprint building (Apart: undisclosed prior work can lead to disqualification).
