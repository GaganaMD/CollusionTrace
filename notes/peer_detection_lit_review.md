# Peer-Shift Detection in Multi-Agent LLMs: Literature Review & Framework

**Context**: Apart Research AI Collusion Sprint (Oct 23–25, 2026)  
**Target Problem**: In repeated games (repeated Bertrand duopolies, steered/fine-tuned collusive agents), can an LLM agent detect whether its **peer has shifted** (swapped model family, steered via activation vectors, fine-tuned, persona-prompted, or switched between competitive and collusive regimes)? Zero-shot frontier models fail to recognize these peer shifts.  
**Scope (Lane A)**: (1) Model identification, self-recognition, and stylometric fingerprinting; (2) Theory of Mind (ToM) and opponent modeling; (3) Counterpart swapping and change detection in repeated games.

---

## 1. Verified Literature Review

### A.1 Model Identification, Self-Recognition & Stylometric Fingerprinting

#### 1. Panickssery, Bowman, & Feng (2024)
* **Citation**: Arjun Panickssery, Samuel R. Bowman, Shi Feng. *LLM Evaluators Recognize and Favor Their Own Generations*. arXiv:[2404.13076](https://arxiv.org/abs/2404.13076).
* **Finding**: Frontier LLMs distinguish their own outputs from other models above chance, with self-recognition correlating linearly with self-preference evaluation bias.
* **Relevance**: Confirms models implicitly identify architectural signatures, but this signal is entangled with quality bias rather than explicit counterpart tracking.

#### 2. Davidson et al. (2024)
* **Citation**: Tim R. Davidson et al. *Self-Recognition in Language Models*. EMNLP Findings, arXiv:[2407.06946](https://arxiv.org/abs/2407.06946).
* **Finding**: Tested with model-generated security questions across 10 LLMs, models fail to exhibit robust self-recognition, consistently picking whichever response matches shared quality priors.
* **Relevance**: Explains zero-shot peer-shift blindness: LLMs evaluate counterpart actions against generic quality priors rather than validating peer identity.

#### 3. Dietrich (2026)
* **Citation**: Juergen Dietrich. *Can Multi-Agent LLMs Identify Their Peers? Stylometric Fingerprinting in Role-Constrained Political Analysis*. arXiv:[2606.09854](https://arxiv.org/abs/2606.09854).
* **Finding**: Model family stylometric fingerprints survive prompt anonymization in multi-agent tasks, yielding 0.991 F1 with fine-tuned classifiers while frozen zero-shot LLMs fail.
* **Relevance**: Shows peer identity signals physically exist in outputs, but extracting them requires explicit feature-learning heads rather than passive in-context attention.

#### 4. Ko et al. (2026)
* **Citation**: Minseok Ko et al. *Who's Behind the Text? Robust Model Authorship Attribution*. arXiv:[2610.19583](https://arxiv.org/abs/2610.19583).
* **Finding**: Introduces ATLAS, using likelihood-based generative attribution with token clipping to achieve 74.3% accuracy under joint domain/model-version shifts where classifiers fail.
* **Relevance**: Demonstrates that peer detection requires evaluating token-level conditional likelihood ratios under candidate model profiles rather than unstructured prompting.

---

### A.2 Theory of Mind & Opponent Modeling in LLMs

#### 5. Ullman (2023)
* **Citation**: Tomer D. Ullman. *Large Language Models Fail on Trivial Alterations to Theory-of-Mind Tasks*. arXiv:[2302.08399](https://arxiv.org/abs/2302.08399).
* **Finding**: Apparent Theory of Mind capabilities in LLMs fail catastrophically under minor, semantics-preserving perturbations to physical or communicative context.
* **Relevance**: Demonstrates that LLM beliefs about counterpart intentionality rely on surface template matching, breaking down when a peer's policy shifts subtly.

#### 6. Akata et al. (2023)
* **Citation**: Elif Akata et al. *Playing repeated games with Large Language Models*. arXiv:[2305.16867](https://arxiv.org/abs/2305.16867).
* **Finding**: In repeated games (Prisoner's Dilemma, Battle of the Sexes), LLMs play rigid, uncooperative strategies, coordinating only when augmented with "Social Chain-of-Thought" (SCoT).
* **Relevance**: Shows unassisted LLMs treat counterpart moves as disconnected events; explicit opponent-modeling scratchpads are needed to track opponent policies.

#### 7. Park, Liu, Ozdaglar, & Zhang (2024)
* **Citation**: Chanwoo Park, Xiangyu Liu, Asuman Ozdaglar, Kaiqing Zhang. *Do LLM Agents Have Regret? A Case Study in Online Learning and Games*. arXiv:[2403.16843](https://arxiv.org/abs/2403.16843).
* **Finding**: Frontier LLMs fail to achieve no-regret in repeated games and non-stochastic online learning without inductive loss corrections, failing to adapt against non-stationary opponents.
* **Relevance**: Proves mathematically that frozen LLMs cannot adapt to non-stationary opponent distributions, explaining why pricing agents miss counterpart shifts.

#### 8. Cao et al. (2026)
* **Citation**: Shiyue Cao et al. *SOM: Structured Opponent Modeling for LLM-based Agents via Structural Causal Model*. arXiv:[2605.07301](https://arxiv.org/abs/2605.07301).
* **Finding**: Decouples opponent model construction from action prediction using a Structural Causal Model (SCM), proving unassisted LLMs conflate prediction with modeling.
* **Relevance**: Confirms peer tracking requires maintaining an explicit, decoupled causal representation of the opponent rather than feeding raw round histories into a single prompt.

---

### A.3 Counterpart Swapping, Algorithmic Collusion & Non-Stationary Shift

#### 9. Eschenbaum, Mellgren, & Zahn (2022)
* **Citation**: Nicolas Eschenbaum, Filip Mellgren, Philipp Zahn. *Robust Algorithmic Collusion*. OpenReview:[BztUFukcBry](https://openreview.net/pdf?id=BztUFukcBry).
* **Finding**: Algorithmic pricing cartels collapse upon counterpart replacement because policies overfit partner-specific action trajectories rather than learning generalized collusion.
* **Relevance**: Benchmark demonstration of partner-swap fragility: multi-agent policies are tightly co-adapted to historical traces and shatter when the peer changes.

#### 10. Fish, Gonczarowski, & Shorrer (2024)
* **Citation**: Sara Fish, Yannai A. Gonczarowski, Ran I. Shorrer. *Algorithmic Collusion by Large Language Models*. arXiv:[2404.00806](https://arxiv.org/abs/2404.00806).
* **Finding**: LLMs acting as pricing agents in repeated oligopolies autonomously sustain supracompetitive prices driven by internalized "price-war concerns," but pricing is hyper-sensitive to prompt phrasing.
* **Relevance**: In repeated Bertrand duopolies, LLMs interpret an undercut as a tactical defection in an ongoing price war rather than suspecting the peer model was swapped or steered.

#### 11. Keppo, Li, Tsoukalas, & Yuan (2026)
* **Citation**: Jussi Keppo, Yuze Li, Gerry Tsoukalas, Nuo Yuan. *On the Fragility of AI Agent Collusion*. arXiv:[2603.20281](https://arxiv.org/abs/2603.20281).
* **Finding**: Model-size asymmetry (32B vs 14B) sustains tacit collusion via emergent leader-follower conventions, but cross-algorithm swapping (LLM vs Q-learner) or patience mismatch shatters collusion.
* **Relevance**: Swapping a peer to a different model family or size often preserves leader-follower dynamics, blinding the agent to the identity swap.

#### 12. Gao et al. (2026)
* **Citation**: Jianxin Gao et al. *Testing Interchangeability in LLM Agent Teams*. arXiv:[2609.05279](https://arxiv.org/abs/2609.05279).
* **Finding**: Swapping role-matched agents across teams increases communication overhead by 16% to 63% due to convention interference, with the staying agent bearing most overhead without realizing the swap occurred.
* **Relevance**: Empirically proves staying agents do not identify counterpart swaps; they experience unexplained conversational thrashing and convention misalignment.

---

## 2. Why Current Models Fail at Peer-Shift Detection

1. **Stateless Attention vs. Latent Filtering**: LLMs compute self-attention across raw token histories $h_t = \{(p_{A,1}, p_{B,1}), \dots, (p_{A,t}, p_{B,t})\}$. They lack an explicit latent probability distribution over opponent parameters $\mathbf{b}_t(\theta) = P(\theta_{peer} \mid h_t)$. Without recursive Bayesian updates, an agent cannot compute change-point likelihood ratios.
2. **Scalar Information Bottleneck**: In repeated Bertrand games, the observable signal is purely numeric ($p_{B,t} \in \mathbb{R}^+$). Stylometric fingerprints (Dietrich 2026, Ko et al. 2026) exist only in dense text. In pure pricing markets, linguistic markers vanish, reducing detection to numerical changepoint detection where raw LLM attention struggles.
3. **Projection & Common-Prior Bias**: LLMs default to symmetric self-projection (Davidson et al. 2024, Akata et al. 2023), assuming opponents share their own reasoning framework. If an opponent drops price from $\$10$ to $\$6$, the agent interprets it as an aggressive competitive undercut within the existing relationship, rather than hypothesizing the counterpart was replaced or steered.
4. **Conflating Variance with Regime Shifts**: Stochastic exploration, temperature sampling, and mixed strategies produce price variance. Without sequential statistical tests (e.g., CUSUM, Page-Hinkley), LLMs cannot distinguish stochastic noise from a structural distribution shift.
5. **Absence of Active Epistemic Probing**: Identifying whether an opponent is activation-steered requires active probing: submitting an off-equilibrium price blip to measure retaliatory elasticity. Out-of-the-box LLMs are greedy reward-maximizers and never sacrifice instantaneous payoff to run diagnostic probes.
6. **Intent-Capability Gap**: As proven by Jiralerspong et al. (2026, arXiv:[2603.16928](https://arxiv.org/abs/2603.16928)), even if an LLM notes a behavioral anomaly in its scratchpad, it fails to maintain persistent suspicion across rounds, rapidly reverting to default in-context heuristics.

---

## 3. Critical Research Gaps

1. **Action-Space Stylometry**: While text stylometry is established (Dietrich 2026, Ko et al. 2026), no work benchmarks *action-space stylometry*—identifying model families or steering states purely from numerical decision sequences in repeated games.
2. **Sequential Changepoint Scaffolding for Agents**: Integrating Bayesian Online Changepoint Detection (BOCPD) or sequential probability ratio tests into LLM agent memory remains unexplored in algorithmic collusion.
3. **Detecting Steering Vectors in Multi-Agent Play**: No literature evaluates whether multi-agent LLMs can detect when a peer has been steered via activation addition (CAA/RepE) versus prompt-instructed or fine-tuned.

---

## 4. Five Concrete Experiment Blueprints for Siva's Sprint

### E1: Sequential Likelihood-Ratio (CUSUM) Memory Scaffold
* **Hypothesis**: Augmenting the LLM with an external Sequential Probability Ratio Test (CUSUM) over observed prices reduces peer-swap detection delay from $>50$ rounds (zero-shot) to $<5$ rounds.
* **Setup**: 100-round repeated Bertrand duopoly. At round 40, Peer B is swapped from `Llama-3.1-70B` to `GPT-4o` (or collusive steered model).
* **Protocol**: A background scaffold computes $S_t = \max(0, S_{t-1} + \ln \frac{P(p_{B,t} \mid \mathcal{M}_{alt})}{P(p_{B,t} \mid \mathcal{M}_{null})})$. When $S_t > \tau$, inject a prompt alert: `[ALERT: Statistical shift detected in Peer B policy distribution]`.
* **Metric**: Detection delay (rounds post-swap), False Alarm Rate, post-swap profit recovery.

### E2: Active Epistemic Probing (Impulse-Response Elasticity)
* **Hypothesis**: Deliberately injecting a 1-round price discount ($\Delta p = -2$) classifies an activation-steered collusive peer versus a base competitive peer with AUROC $> 0.85$.
* **Setup**: Steered collusive models exhibit rigid collusion basins (activation clamping); base models exhibit elastic price retaliations.
* **Protocol**: At round 25, Agent A executes a diagnostic probe $p_{A,25} = p_{collusive} - 2$. Agent A's scratchpad evaluates the response: if Peer B undercuts in round 26, classify as *Competitive*; if Peer B maintains supracompetitive pricing, classify as *Steered Collusive*.
* **Metric**: Classification AUROC across 50 independent duopoly trials.

### E3: Two-Track CoT (Decoupled Opponent State Filter)
* **Hypothesis**: Decoupling the scratchpad into explicit (1) Opponent State Estimation and (2) Action Optimization (following Cao et al. 2026 SOM) increases zero-shot shift detection from $\approx 0\%$ to $>60\%$.
* **Setup**: At round 30, Peer B switches persona from cooperative to predatory.
* **Protocol**: Require Agent A to output structured JSON before bidding:
  ```json
  {"opponent_regime": "stationary | shifted", "surprise_metric": "price delta vs expected", "shift_confidence": 0.0-1.0, "price_bid": float}
  ```
* **Metric**: Correlation between `shift_confidence` and true swap round; time to optimal counter-pricing.

### E4: Action-Distribution Stylometry (ATLAS for Economic Games)
* **Hypothesis**: Distinct LLM model families exhibit unique numerical pricing fingerprints (rounding biases, price endings, retaliation slopes) detectable by a likelihood classifier without text messages.
* **Setup**: Gather 1,000 rounds of pricing data across 4 model families (`Claude-3.5-Sonnet`, `GPT-4o`, `Llama-3.1-70B`, `Qwen-2.5-72B`).
* **Protocol**: Fit a Gaussian Process or adapter over transitions $(p_{t-2}, p_{t-1}) \to p_t$. Test whether an observer or agent can identify the model family sitting in the counterpart seat.
* **Metric**: Top-1 attribution accuracy across the 4 model families from numerical histories alone.

### E5: The Interchangeability Shock Benchmark in LLM Cartels
* **Hypothesis**: Swapping a peer with an identical model instance from a parallel market creates a "convention shock" (price volatility spike) distinguishing an instance swap from genuine continuity.
* **Setup**: Run two parallel Bertrand markets with identical `Llama-3.1-8B-Instruct` agents until stable collusion ($t=30$). At $t=31$, swap Peer B between markets.
* **Protocol**: Measure coordination breakdown across: (a) unswapped control, (b) swapped identical-model peer, (c) swapped cross-model peer. Query Agent A each round: `Has your partner been swapped? (Yes/No + Confidence)`.
* **Metric**: True positive detection rate vs. convention friction (excess price variance and payoff drop).
