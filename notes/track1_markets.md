# Track 1: Markets and Collusion — Research Notes

## Core Focus & Theoretical Landscape
Markets serve as the earliest high-stakes proving ground for multi-agent collusion. In repeated Bertrand, Cournot, and double-auction markets, self-interested agents naturally explore pricing strategies that deviate from competitive Nash equilibria toward supracompetitive cartel outcomes.

## Key Sub-Questions & Literature Synthesis

### 1.1 Necessary Variables for Collusion
* **Fish et al. (2024)** demonstrated that LLMs reach supracompetitive prices in duopolies due to internalized "price-war concerns."
* **Dhanda (2026)** discovered that statutory price caps act as focal points, causing immediate convergence to the ceiling.
* **Lin et al. (2024)** showed that in multi-commodity Cournot competition, models divide markets into monopolies without explicit communication.
* **Conjeaud et al. (2026 - arXiv:2608.01406):** Proved that asynchronous price updating (Poisson clocks) significantly dampens algorithmic collusion relative to lock-step synchronous updating by breaking the symmetry of tit-for-tat retaliatory threats.
* **Ye (2025 - arXiv:2502.15084):** Proved that under observable macroeconomic demand shocks, agents autonomously learn procyclical pricing at high discount factors and countercyclical pricing at low discount factors while sustaining supracompetitive markups.
* **Key Levers:** Visible history length, prompt framing, plans-and-insights scratchpad persistence, update synchrony vs Poisson clocks, and agent naming.

### 1.2 Robustness to Peer Replacement & Meta-Games
* **Eschenbaum et al. (2022)** found that Q-learning cartels collapse when one agent is swapped because policies overfit rival actions.
* **Keppo et al. (2026)** showed that LLMs share universal economic representations; pairing asymmetric LLMs (32B vs 14B) sustains collusion, while pairing with Q-learning breaks it.
* **Carissimo et al. (2025 - arXiv:2508.14766):** Argued that algorithmic collusion is often "algorithm orchestration," requiring co-parametrization at the meta-game design level.
* **Luo et al. (2026 - arXiv:2602.17203):** Introduced test-time meta-game evaluations, showing that pre-trained LLM policies with dynamic adaptation rules coordinate on collusive equilibria without co-training.
* **Aharon et al. (2026):** Confirmed that models from similar foundation model families tacitly coordinate better on convention games.

### 1.3 Detection Calibration & Multi-Dimensional Pricing
* **Agrawal et al. (2025):** Benchmarked continuous double auctions with seller communication, showing that naive LLM judges struggle to distinguish shared pretraining priors from genuine coordination.
* **Xu, Yue, & Acemoglu (2026 - arXiv:2607.26385):** Proved that cartels can keep marginal primary prices competitive while colluding on ancillary dimensions (shipping fees, inventory throttling), blinding traditional single-price regressions by construction.
* **Tian & Ha (2026 - arXiv:2604.17774):** Used evolutionary prompt optimization to discover compact meta-prompts that trigger sustained monopoly markups without explicit cartel language.

### 1.4 Information-Theoretic Auditing
* **Bonjour et al. (UAI 2022):** Formulated Pairwise Net Influence (PNI), measuring directional mutual information transfer across action transitions. PNI isolates colluding pairs among 4 players without false accusations.
* **Bichler et al. (2025 - arXiv:2504.16592):** Analyzed equilibrium learning in retail platforms, identifying theoretical gaps in auditing online bandit and RL pricing algorithms.

### 1.5 Cost-Effective Restrictions
* **Collina et al. (2025):** Proved theoretically that introducing a single no-regret learning agent destabilizes collusive equilibria.
* **Agrawal et al. (2025):** Showed that throttling message length to short tokens significantly degrades coordination.
