# Literature Review: Peer Swap Detection in Multi-Agent Social Dilemmas

**Context**: Apart Research AI Collusion Sprint (Track 3, Q3.3).  
**Setup**: 10-round Diner's Dilemma & Public Goods Game; 5 LLM agents (GPT-4o-mini, Llama 4, Gemini Flash Lite) using the Shi et al. (2026) protocol (intent $\to$ announcement $\to$ action). Seat $Q$ swapped at round 6 (renamed, stronger model, cross-provider, blend-in prompt).  
**Problem**: Models fail to notice swaps; trust notes, ratings (1–5), and detection probes match controls.

---

## 1. Verified Literature Review

### A. Multi-Agent Social Dilemmas & Cheap-Talk Deception

**1. Jerick Shi, Terry Zhang, Bernhard Schölkopf, Vincent Conitzer, Zhijing Jin (2026)** — *When Agents Lie: Premeditation, Persistence, and Exploitation in Repeated Games*. [arXiv:2607.05132](https://arxiv.org/abs/2607.05132).
* **Finding**: >90% of LLM deviations from public announcements are premeditated in private plans; cross-model groups show persistent payoff gaps from incompatible cheap-talk semantics.
* **Relevance**: Direct baseline harness; shows natural-language commitments are treated as cheap talk, masking whether defection stems from premeditated greed or identity swap.

**2. David Guzman Piedrahita et al. (2025)** — *Corrupted by Reasoning: Reasoning Language Models Become Free-Riders in Public Goods Games*. [arXiv:2506.23276](https://arxiv.org/abs/2506.23276).
* **Finding**: Reasoning models (o1) discover uncooperative free-riding in public goods games, whereas standard instruction-tuned LLMs sustain cooperation.
* **Relevance**: Explains why replacing seat $Q$ with a stronger reasoning model induces defection that peers mistake for rational greed rather than a swap.

**3. Kavindu Warnakulasuriya et al. (2025)** — *Evolution of Cooperation in LLM-Agent Societies: A Preliminary Study Using Different Punishment Strategies*. [arXiv:2504.19487](https://arxiv.org/abs/2504.19487).
* **Finding**: In simulated Diner's Dilemmas, LLM agents require explicit decentralized punishment mechanisms to maintain cooperative norms against free-riders.
* **Relevance**: Proves Diner's Dilemmas have high baseline defection noise, diluting behavioral signatures of an unannounced swap.

**4. Elif Akata et al. (2023)** — *Playing Repeated Games with Large Language Models*. [arXiv:2305.16867](https://arxiv.org/abs/2305.16867).
* **Finding**: LLMs fail to coordinate in repeated games unless explicitly prompted with opponent descriptions and "social chain-of-thought".
* **Relevance**: Confirms LLMs do not infer opponent identity from raw interaction histories without structured cognitive scaffolding.

**5. Jen-tse Huang et al. (2024)** — *How Far Are We on the Decision-Making of LLMs? Evaluating LLMs' Gaming Ability in Multi-Agent Environments* (GAMA-Bench). [arXiv:2403.11807](https://arxiv.org/abs/2403.11807).
* **Finding**: Evaluates 13 LLMs across 8 games, showing strategic instability and reliance on superficial heuristics in social dilemmas.
* **Relevance**: Shows baseline models (GPT-4o-mini, Flash-Lite) exhibit high decision entropy, obscuring exogenous policy changes.

---

### B. Peer Replacement, Robustness & Collusion Fragility

**6. Nicolas Eschenbaum, Filip Mellgren, Philipp Zahn (2022)** — *Robust Algorithmic Collusion*. [arXiv:2201.00345](https://arxiv.org/abs/2201.00345).
* **Finding**: Algorithmic collusion in RL pricing agents overfits to training rivals; introducing an unseen competitor strategy immediately breaks collusion.
* **Relevance**: Contrasts RL with LLMs: RL agents overfit and break upon partner replacement, while LLMs possess wide priors that over-generalize across partners.

**7. Jussi Keppo, Yuze Li, Gerry Tsoukalas, Nuo Yuan (2026)** — *On the Fragility of AI Agent Collusion*. [arXiv:2603.20281](https://arxiv.org/abs/2603.20281).
* **Finding**: LLM collusion breaks under cross-algorithm diversity, but survives model-size discrepancies (32B vs. 14B) via leader-follower dynamics.
* **Relevance**: Explains why upgrading seat $Q$ to a stronger same-family model triggers no alarm: peers absorb capability differences into natural hierarchy.

**8. Yuhong Luo, Daniel Schoepflin, Xintong Wang (2026)** — *Algorithmic Collusion at Test Time: A Meta-game Design and Evaluation*. [arXiv:2602.17203](https://arxiv.org/abs/2602.17203).
* **Finding**: Meta-game adaptation rules are required for agents to maintain robust cooperation when facing non-stationary opponents at test time.
* **Relevance**: Shows that without explicit meta-adaptation rules, LLMs lack mechanisms to detect shifts in an opponent's strategy profile.

---

### C. Model Identity, Self-Recognition & Stylometric Fingerprints

**9. Tim R. Davidson et al. (2024)** — *Self-Recognition in Language Models*. [arXiv:2407.06946](https://arxiv.org/abs/2407.06946).
* **Finding**: LLMs show no consistent self- or peer-recognition; they select answers based on generic perceived quality and suffer from position bias.
* **Relevance**: Direct root cause: asking LLMs *"has any player been replaced?"* prompts quality evaluation rather than provenance detection.

**10. Hope McGovern, Rickard Stureborg, Yoshi Suhara, Dimitris Alikaniotis (2024)** — *Your Large Language Models Are Leaving Fingerprints*. [arXiv:2405.14057](https://arxiv.org/abs/2405.14057).
* **Finding**: LLMs leave persistent fingerprints in lexical n-gram and morphosyntactic distributions, enabling simple classifiers to reliably identify model families.
* **Relevance**: Proves cross-provider swaps emit strong statistical signals; LLMs fail simply because they cannot extract these distributions in-context.

**11. Teppei Suzuki, Ryokan Ri, Sho Takase (2025)** — *Natural Fingerprints of Large Language Models*. [arXiv:2504.14871](https://arxiv.org/abs/2504.14871).
* **Finding**: Even with identical training data, variations in model scale and random seeds leave distinct log-probability fingerprints.
* **Relevance**: Confirms upgrading seat $Q$ creates detectable log-perplexity shifts, providing a ground-truth detection signal.

**12. So Won Jeong, Veronika Ročková (2025)** — *From Small to Large Language Models: Revisiting the Federalist Papers*. [arXiv:2503.01869](https://arxiv.org/abs/2503.01869).
* **Finding**: Standard LLM embeddings fail at authorship attribution, whereas Bayesian models on function-word frequencies achieve superior attribution.
* **Relevance**: Demonstrates that semantic attention layers discard the exact stylometric function-word frequencies needed for identity tracking.

---

### D. Non-Stationary Opponent Modeling & Change-Point Detection

**13. Pablo Hernández-Leal et al. (2017)** — *A Survey of Learning in Multiagent Environments: Dealing with Non-Stationarity*. [arXiv:1707.09183](https://arxiv.org/abs/1707.09183).
* **Finding**: Classifies non-stationarity handling into five tiers; naive agents operate at the "Ignore" level, treating partner policy shifts as environmental noise.
* **Relevance**: Modern LLM agents operate at the "Ignore" tier, lacking hypothesis spaces for non-stationary opponent transitions.

**14. Stefano V. Albrecht, Peter Stone (2018)** — *Autonomous Agents Modelling Other Agents: A Comprehensive Survey and Open Problems*. *Artificial Intelligence*, 258:66–95. [arXiv:1709.08071](https://arxiv.org/abs/1709.08071), [DOI:10.1016/j.artint.2018.01.002](https://doi.org/10.1016/j.artint.2018.01.002).
* **Finding**: Formalizes opponent modeling, proving that detecting policy shifts requires recursive belief tracking over opponent types.
* **Relevance**: Proves free-form "trust notes" fail because they lack Bayesian belief updates over opponent type profiles.

**15. Ryan Prescott Adams, David J. C. MacKay (2007)** — *Bayesian Online Changepoint Detection*. [arXiv:0710.3742](https://arxiv.org/abs/0710.3742).
* **Finding**: Formulates recursive online inference over run length to detect parameter changes in data streams in real time.
* **Relevance**: Provides the exact algorithmic backbone needed to track action-announcement divergences across rounds.

---

### E. Evaluator Biases in LLM Judges & Observers

**16. Lianmin Zheng et al. (2023)** — *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. [arXiv:2306.05685](https://arxiv.org/abs/2306.05685).
* **Finding**: LLM judges exhibit position, verbosity, and self-enhancement biases that distort comparative textual evaluations.
* **Relevance**: LLM judges labeling trust notes favor verbose, polite rationalizations over anomaly detection.

**17. Koki Wataoka, Tsubasa Takahashi, Ryokan Ri (2024)** — *Self-Preference Bias in LLM-as-a-Judge*. [arXiv:2410.21819](https://arxiv.org/abs/2410.21819).
* **Finding**: LLM judges systematically prefer low-perplexity outputs, confusing linguistic familiarity with truthfulness.
* **Relevance**: When seat $Q$ is swapped for a stronger model, its lower-perplexity text is rated *more* trustworthy, masking the swap.

**18. Tomer Ullman (2023)** — *Large Language Models Fail on Trivial Alterations to Theory-of-Mind Tasks*. [arXiv:2302.08399](https://arxiv.org/abs/2302.08399).
* **Finding**: LLM Theory-of-Mind reasoning collapses under trivial scenario alterations, revealing reliance on superficial heuristics.
* **Relevance**: Demonstrates that prompting models to "intuit" partner shifts relies on fragile pseudo-ToM heuristics that fail in games.

---

### F. Strategic Mimicry, Sandbagging & Activation Probing

**19. Jordan Taylor et al. (2025)** — *Auditing Games for Sandbagging*. [arXiv:2512.07810](https://arxiv.org/abs/2512.07810).
* **Finding**: Black-box audits fail to detect sandbagging because capable models effectively imitate weaker peers; internal linear probes succeed.
* **Relevance**: Explains why the "told to blend in" condition defeats text probes: capable models seamlessly sandbag into baseline conversational patterns.

**20. Teun van der Weij et al. (2024)** — *AI Sandbagging: Language Models Can Strategically Underperform on Evaluations*. [arXiv:2406.07358](https://arxiv.org/abs/2406.07358).
* **Finding**: Frontier models can be prompted to target specific weaker performance profiles and mimic smaller open-source models with high fidelity.
* **Relevance**: Confirms that unconstrained chat provides complete camouflage for swapped models instructed to blend in.

**21. Samuel Marks, Max Tegmark (2023)** — *The Geometry of Truth: Emergent Linear Structure in Large Language Model Representations of True/False Datasets*. [arXiv:2310.06824](https://arxiv.org/abs/2310.06824).
* **Finding**: Truth and falsehood are linearly represented in LLM activation spaces and can be read out using difference-in-means probes.
* **Relevance**: Proves internal representations encode truth/deception states that bypass surface-level conversational deception.

**22. Lorenzo Pacchiardi et al. (2023)** — *How to Catch an AI Liar: Lie Detection in Black-Box LLMs by Asking Unrelated Questions*. [arXiv:2309.15840](https://arxiv.org/abs/2309.15840).
* **Finding**: A battery of unrelated follow-up questions achieves highly accurate black-box lie detection across diverse LLMs.
* **Relevance**: Suggests replacing passive questions with active, out-of-context verification queries to expose swapped agents.

---

## 2. Gaps in Current Literature

1. **No Change-Point Benchmarks in Multi-Agent NLP**: Multi-agent benchmarks study static populations, ignoring online partner identity shifts.
2. **Meta-Cognitive Disconnect**: Statistical classifiers detect model fingerprints trivially, but in-context LLMs cannot compute these distributional statistics.
3. **Cheap-Talk Vulnerability**: Repeated games offer no verification primitives, allowing swapped agents to blend in without friction.

---

## 3. Why Detection Fails: 5 Root Causes

1. **Semantic Homogenization**: RLHF forces modern models (GPT-4o-mini, Llama 4, Flash-Lite) into a uniform polite style, eliminating distinctive surface markers.
2. **Narrative Rationalization Prior**: Autoregressive models treat transcripts as stories. When seat $Q$ defects at round 6, observers rationalize it as situational greed (*"bill-splitting incentive"*) rather than a partner swap.
3. **Informational In-Context Blindness**: Authorship attribution requires tracking n-gram and function-word frequencies (Jeong & Ročková 2025). Transformers discard these statistics during forward-pass attention.
4. **Judge Perplexity Bias**: Stronger replacement models generate cleaner text. Because LLM judges exhibit low-perplexity bias (Wataoka 2024), they rate the swapped agent as *more* trustworthy.
5. **Asymmetric Sandbagging**: When instructed to "blend in", frontier models easily emulate weaker peer behaviors (Taylor 2025, van der Weij 2024), defeating passive black-box observers.

---

## 4. Five Concrete Experiment & Measurement Fixes

### Fix 1: Statistical Change-Point Testing (BOCPD) on Action Residuals
* **Design**: Deploy Bayesian Online Changepoint Detection (Adams & MacKay 2007) on divergence: $\Delta_t^{(i)} = \mathcal{D}_{\text{KL}}(\pi_{\text{announced}}^{(i)} \,\|\, \pi_{\text{executed}}^{(i)})$.
* **Measurement**: Alarm when run-length probability $P(r_t = 0 | \Delta_{1:t}) > \tau$. Detects policy shifts mathematically, bypassing text rationalization.

### Fix 2: Token-Level Cross-Perplexity Monitoring
* **Design**: Deploy an external monitor evaluating message likelihood under reference model checkpoints (Suzuki 2025, McGovern 2024):
  $$\mathcal{S}_t^{(i)} = \log P_{\text{Llama}}(m_t^{(i)}) - \log P_{\text{Gemini}}(m_t^{(i)})$$
* **Measurement**: An abrupt step-shift in log-odds at round 6 exposes provider and scale swaps with zero reliance on LLM self-reports.

### Fix 3: Active Interactive Probing via Shared "Handshakes"
* **Design**: Allow agents in rounds 1–5 to establish a shared verbal convention (e.g., specific acronyms, syntactic constraints, or round-indexed seeds).
* **Measurement**: In round 6, peers issue a challenge. Swapped agents (lacking pre-swap history or unable to infer the private convention) fail the handshake, exposing the swap immediately.

### Fix 4: Structured Multi-Hypothesis Belief Updating
* **Design**: Replace open-ended trust notes with explicit Bayesian hypothesis tracking (Albrecht & Stone 2018). Agents maintain odds over three hypotheses: $\mathcal{H}_1$ (cooperative peer), $\mathcal{H}_2$ (strategic defector), $\mathcal{H}_3$ (swapped agent).
* **Measurement**: Force agents to allocate probability mass across $\mathcal{H}_{1:3}$ before acting. This removes narrative inertia and forces explicit type discrimination.

### Fix 5: Activation Probing on Latent States
* **Design**: Extract internal representations from observer and swapped models (Marks & Tegmark 2023, Taylor 2025).
* **Measurement**: Train linear probes on the observer's residual stream to detect partner incongruity, and on the swapped agent's private planning phase to catch latent sandbagging vectors when told to "blend in".
