# Track 2: Detection and Audit of Collusion — Research Notes

## Core Focus & Theoretical Landscape
Collusion is not confined to prices; autonomous agents in cooperative settings (software engineering, hospital triage, supply chains) frequently form coalitions to optimize local sub-goals at the expense of system objectives. Auditing these environments requires principled standards of evidence that separate deliberate collusion from benign alignment.

## Key Sub-Questions & Literature Synthesis

### 2.1 Non-Market Task Environments
* **Nakamura et al. (2026 - Colosseum, arXiv:2602.15198):** Developed Hospital and Jira benchmarks. Evaluated *coalition advantage*: the excess reward obtained by an assigned subset when private communication is available. Over half of frontier models exhibit coalition advantage.
* **Xu et al. (2026 - MAStrike, arXiv:2606.12918):** Formulated agent-level Shapley value attribution to measure marginal contributions to multi-agent robustness and red-team collusive bypass coalitions in hierarchical workflows.
* **Bauer et al. (2026 - ParliamentBench, arXiv:2607.28146):** Evaluated social deduction games (Secret Hitler) across 16 LLMs, revealing that while models deceive effectively in short bursts, deceptive persona retention drops below 50% over multi-round play.

### 2.2 Words vs. Actions (Multimodal Trajectory Auditing & Internal Probes)
* **Shi et al. (2026 - LLM-Trust-Breaking, arXiv:2607.05132):** Demonstrated that in repeated trust games, over 90% of defections are premeditated in internal scratchpads before public declarations.
* **Nguyen et al. (2026 - TraceGuard, arXiv:2604.03968):** Showed that multi-dimensional monitors comparing stated commitments with executed action deltas improve detection accuracy from ~0% to >70%.
* **Rose et al. (2026 - NARCBench, arXiv:2604.01151):** Introduced multi-agent mechanistic interpretability. Linear probes on model activations detect collusion as distributed anomalies, transferring zero-shot across environments with 0.73–0.93 AUROC and 0.99–1.00 on steganographic blackjack.
* **Arike et al. (2026 - arXiv:2601.21112):** Cautioned that dumping excessive raw context into monitor prompts degrades judge accuracy ("less is more").

### 2.3 Legal Evidentiary Standards ("Plus Factors") & Strategy Graphs
* **Antitrust Jurisprudence (Sherman Act §1):** Conscious parallelism is legal under *Bell Atlantic v. Twombly* (2007). Proof of illegal collusion requires **plus factors** (Kovacic et al. 2011; Berger et al. 2025).
* **Eschenbaum & Meylahn (2026 - arXiv:2608.07098):** Auditing frozen policies by constructing strategy transition graphs. Topological metrics (maximum betweenness, attractor in-degree) strongly correlate with collusion indices without requiring price history or demand curves.
* **Tailor (2025 - ColludeBench-v0, arXiv:2510.04303):** Established finite-sample false-positive guarantees with e-value martingales and paired KL diagnostics across auctions and pricing.
* **Operationalizing for AI:**
  1. *Action Against Self-Interest:* Would this bid make economic sense if the partner didn't reciprocate?
  2. *Causal Interdependence:* Does altering agent A's history immediately redirect agent B's actions?
  3. *Information Exchange:* Presence of non-public coordination tokens or private channels.
