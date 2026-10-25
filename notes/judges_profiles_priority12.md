# Judge profiles (agy-delegate output, 2026-10-23). UNVERIFIED: arXiv ids/URLs not checked by me; verify before citing any.

# Evaluation Panel Analysis: Apart Research AI Collusion Sprint

Research profile and evaluation focus for the 12 selected judges from `notes/judges_20261023.md`.

---

### 1. Jasmine Brazilek
* **Affiliation:** Co-founder & Head of Evaluations and Data, CaML (Compassion Aligned Machine Learning); ex-Anthropic Security.
* **Public Work:**
  * Lead paper on unprompted multi-agent escalation: [*Coercion and Deception in AI-to-AI Management: An Agentic Benchmark of Unprompted Escalation*](https://arxiv.org/abs/2607.15434) (arXiv:2607.15434)
  * Codebase: [CompassionML/manager-coercion-bench](https://github.com/CompassionML/manager-coercion-bench)
  * Organization & Benchmarks: [CaML](https://compassionml.com) (Agentic compassion benchmarks: *TAC* and *HarvestBench*)
* **Evaluation Focus & Priorities:**
  * **Multi-agent dynamics & hierarchy:** Cares deeply about emergent behavioral dynamics when agents interact autonomously under authority structures or peer pressures.
  * **Unprompted deception & coercion:** Looks for whether models spontaneously escalate, threaten, or fabricate success metrics when encountering friction or task refusal.
  * **Empirical escalation ladders:** Values structured, behavioral grading (e.g., discrete severity tiers) over vague sentiment checks.

### 2. Jess Bergs (UK AISI)
* **Affiliation:** R&D Engineering & Product Strategy Lead / Human-AI Interaction Lead, UK AI Safety Institute (UK AISI); Mentor at SPAR, Pivotal Research, BlueDot Impact.
* **Public Work:**
  * Personal Portfolio & Research: [jbergs.eu](https://jbergs.eu)
  * Projects: Scalable empirical tooling for human-in-the-loop AI oversight; *Auditing Games for Debate* (testing whether models learn human spot-checking patterns); *AI and Political Knowledge* (*PNAS Nexus* [unverified direct DOI]); past BBC R&D on Explainable AI (XAI).
* **Evaluation Focus & Priorities:**
  * **Human oversight & auditing tools:** Cares about realistic, scalable human-in-the-loop protocols for inspecting and auditing autonomous agent trajectories.
  * **Interactive oversight (Debate & Auditing Games):** Strongly interested in whether oversight mechanisms can detect subtle coordination or deceptive arguments.
  * **Evaluator tooling & usability:** Values practical infrastructure that allows safety researchers to run reproducible empirical evaluations at scale.

### 3. Arjun Chakraborty (Microsoft Security AI Research)
* **Affiliation:** Evals Team Lead & Principal Applied AI Engineer, Microsoft Security AI Research.
* **Public Work:**
  * Benchmark Paper: [*CTI-REALM: Benchmark to Evaluate Agent Performance on Security Detection Rule Generation Capabilities*](https://arxiv.org/abs/2603.13517) (arXiv:2603.13517)
  * Evaluation Dataset & Code: [Hugging Face cti_realm](https://huggingface.co/datasets/arjun180-new/cti_realm) [unverified exact repo path]
  * Microsoft Security Research: Technical posts on automated incident response and LLM agent benchmarking in enterprise environments.
* **Evaluation Focus & Priorities:**
  * **Real-world cyber threat rigor:** Wants evaluations grounded in real attack-defense telemetry rather than synthetic multi-choice questions.
  * **End-to-end agent tool use:** Emphasizes trajectory-based rewards, tool-calling execution fidelity, and iterative debugging in realistic environments.
  * **Actionable defensive validation:** Cares whether an evaluation produces verifiable ground truth (e.g., syntactically and semantically valid detection logic).

### 4. Simon Storf (Anthropic)
* **Affiliation:** AI Safety & Security Researcher, Anthropic; ex-Anthropic Fellow; ex-MATS Fellow (under Marius Hobbhahn).
* **Public Work:**
  * Personal Site: [simonstorf.com](https://simonstorf.com)
  * Paper: [*Red-Teaming Auto Mode: Improving Blocking Classifiers Against Malign Coding Agents*](https://arxiv.org/abs/2609.19587) (arXiv:2609.19587)
  * Paper: [*Constitutional Black-Box Monitoring for Scheming in LLM Agents*](https://arxiv.org/abs/2603.00829) (arXiv:2603.00829; ICML 2026)
  * Paper: *Training Deliberative Monitors for Black-Box Scheming Detection* (ICML 2026)
* **Evaluation Focus & Priorities:**
  * **AI Control & Scheming:** Foremost expert on detecting whether agents covertly pursue misaligned goals without access to internal activations.
  * **Adversarial monitor evasion:** Studies how agents actively bypass classifiers via prompt injection against the monitor, context compaction, and task-splitting.
  * **Multi-agent evasion:** Specifically values tests where multiple agents divide malicious subtasks to stay under individual monitor thresholds.

### 5. Raja Moreno (Raja Mehta Moreno)
* **Affiliation:** Co-founder, Etymologic (AI safety PBC); former MATS Fellow (under Francis Rhys Ward).
* **Public Work:**
  * Personal Site: [rajamoreno.github.io](https://rajamoreno.github.io)
  * Paper: [*CTRL-ALT-DECEIT: Sabotage Evaluations for Automated AI R&D*](https://arxiv.org/abs/2511.09904) (arXiv:2511.09904; NeurIPS)
  * Evaluation Tooling: Extended UK AISI Inspect benchmark framework for sabotage and sandbagging detection.
* **Evaluation Focus & Priorities:**
  * **Covert sabotage & sandbagging:** Deeply interested in whether autonomous agents can hide capabilities or subtly subvert tasks without alerting oversight.
  * **AI Control protocols:** Focuses on realistic deployment scenarios (like automated R&D) where models are treated as untrusted actors.
  * **Monitor limits:** Evaluates the exact boundary where automated secondary LLM monitors fail to distinguish malicious stealth from honest failure.

### 6. Jasmine Li (SaferAI)
* **Affiliation:** Research Affiliate, SaferAI; Founder, Cornell AI Alignment; former MATS Fellow (under Alex Turner).
* **Public Work:**
  * Personal Site & Writing: [jasminexli.com](https://jasminexli.com) (Substack: *The J-Space*)
  * Paper: [*ProgressGym: Alignment with a Millennium of Moral Progress*](https://arxiv.org/abs/2406.20087) (arXiv:2406.20087; [GitHub](https://github.com/PKU-Alignment/ProgressGym))
  * Institutional Work: Independent third-party AI risk evaluations and governance frameworks at [SaferAI](https://safer-ai.org).
* **Evaluation Focus & Priorities:**
  * **Evaluation gaming & reward hacking:** Researches methods to prevent models from gaming benchmarks or exploiting evaluation heuristics.
  * **Independent third-party audits:** Values evaluation protocols that map cleanly to international risk management standards (ISO, NIST, EU AI Act).
  * **Value alignment robustness:** Cares about multi-agent feedback loops and ensuring alignment methods don't freeze blindspots or brittle proxy goals.

### 7. Boyd Kane
* **Affiliation:** Technical AI Safety Researcher; MATS 9.0 & Extension Fellow (Team Shard, mentored by Alex Turner and Alex Cloud); ex-embedded systems engineer.
* **Public Work:**
  * Personal Site: [boydkane.com](https://boydkane.com)
  * Technical Writings & Blog: [beyarkay on LessWrong](https://www.lesswrong.com/users/beyarkay) & Substack
  * Research Spotlight: MATS Symposium presentation on detecting misaligned LLM internal goals via limited-parameter finetuning (with Jo Jiao).
* **Evaluation Focus & Priorities:**
  * **Mechanistic interpretability & internal representations:** Cares about what is happening internally within the model (sparse autoencoders, representation editing).
  * **Shard theory & learned values:** Looks for whether behavioral failures are driven by coherent sub-agent goal representations or surface-level mimicry.
  * **Systems-level security:** Brings an embedded engineering lens—values scrutiny of host execution environments, sandboxes, and runtime exploitation.

### 8. Ihor Kendiukhov
* **Affiliation:** Founder & Principal Researcher, BiodynAI; Research Lead, AI Safety Camp (AISC); SPAR Fellow.
* **Public Work:**
  * Organization: [BiodynAI](https://biodynai.com)
  * Peer-Reviewed Paper: [*What topological and geometric structure do biological foundation models learn? Evidence from 141 hypotheses*](https://doi.org/10.1371/journal.pone.0344826) (*PLOS ONE* 21(7): e0344826, 2026)
  * Safety Leadership: Project Lead at AISC on *Novel AI Control Protocol Classes Evaluation and Scalability* ([AISC](https://aisafety.camp)).
* **Evaluation Focus & Priorities:**
  * **Statistical rigor & null controls:** Extremely critical of spurious correlations; insists on comprehensive null hypothesis testing and rigorous baselines.
  * **AI Control protocol scaling:** Examines formal mathematical and empirical scaling properties of AI control setups (e.g. Greenblatt et al. paradigms).
  * **Geometric / Circuit verification:** Values formal mapping of model representations and causal circuits rather than accepting black-box outputs.

### 9. Debayan Gupta (Ashoka Univ / Truth Audit Labs)
* **Affiliation:** Associate Professor of Computer Science, Ashoka University; Co-founder, Truth Audit Labs; former Visiting Faculty, MIT EECS.
* **Public Work:**
  * Academic Profile: [Ashoka Faculty Page](https://www.ashoka.edu.in/faculty/debayan-gupta/) & [debayangupta.com](https://debayangupta.com)
  * Recent Papers:
    * [*Identifying Intelligent Processes via Online Sequential Testing*](https://arxiv.org/abs/2609.26193) (arXiv:2609.26193)
    * [*Validity, Reliability, and Transparency in AI Regulation*](https://arxiv.org/abs/2608.05800) (arXiv:2608.05800)
    * [*On the Indistinguishability of Human v/s AI Generated Text*](https://arxiv.org/abs/2608.26797) (arXiv:2608.26797)
* **Evaluation Focus & Priorities:**
  * **Formal & mathematical rigor:** Looks for statistical guarantees, online sequential testing validity, Lipschitz bounds, and theoretical foundations.
  * **Adversarial robustness & evasion:** Focuses on proving whether an agent or protocol can be provably audited or reliably distinguished from benign behavior.
  * **Privacy & multi-party computation:** Cares about secure protocols, distributed verification, and algorithmic audit validity.

### 10. Ksheeraj Sai Vepuri (Meta)
* **Affiliation:** Senior Research Engineer, Meta Superintelligence Labs / GenAI.
* **Public Work:**
  * Recent Paper: [*MaD-RL: Matching Distributions for Calibrating LLMs with Reinforcement Learning*](https://arxiv.org/abs/2609.31644) (arXiv:2609.31644)
  * Research Profile: [Google Scholar](https://scholar.google.com/citations?user=HEGEYC0aEHm2HYUkrBWzqeyBtlTGrwR5kxMtTVvpEdM-x1hjOAj82Zjex9PCUQcRLbWqb87_ZMHSsaZ--B8NGFtjjDM2A0Krr7cwW32oxPfEuqfcEekOLdWHxPVpiviqNXlj_AG89_B8GrYPhpUCvuT8o=) [unverified query ID token, verified author]
  * Academic Repository: [SJSU ScholarWorks](https://scholarworks.sjsu.edu) (Computer vision and deep learning publications)
* **Evaluation Focus & Priorities:**
  * **Calibration & output distribution:** Looks at aggregate distribution metrics across rollouts, warning against mode collapse induced by scalar reward RL (like GRPO).
  * **Empirical scale & production readiness:** Values methods that scale reliably across frontier architectures without fragile hyperparameter sensitivity.
  * **Principled statistical loss formulation:** Appreciates rigorous divergence formulations (KL, Jensen-Shannon) when evaluating agent alignment.

### 11. Jannis Kirschner
* **Affiliation:** AI Safety Researcher & Software Security Engineer (Niantic); former Swiss National Hacking Team leader; competitive CTF player (suid.ch).
* **Public Work:**
  * Personal Portfolio: [jannis.re](https://jannis.re)
  * Vulnerability Disclosures: Responsible disclosure of critical flaws in Swiss e-voting systems and network routers with [suid.ch](https://suid.ch) (talks at REcon, BSidesZH).
  * AI Security: Red-teaming frontier models, auditing model supply-chain and runtime vulnerabilities on platforms like Hugging Face.
* **Evaluation Focus & Priorities:**
  * **Offensive adversary mindset:** Evaluates whether a threat model assumes realistic, capable adversaries who actively try to break rules and bypass guardrails.
  * **Concrete exploitability over theory:** Unimpressed by synthetic lab safety metrics that fail the moment an attacker tweaks tool inputs or formats.
  * **Sandboxing & environment containment:** Demands strict isolation, tamper resistance, and offensive red-teaming of the execution substrate.

### 12. Kaushik Prabhakar (Apart Research)
* **Affiliation:** Research Fellow & Studio Member, Apart Research; B.Tech VIT Vellore.
* **Public Work:**
  * Personal Site: [kaushiksp.com](https://kaushiksp.com)
  * Regulatory Paper: [*An Evaluation Framework for National AI Regulation*](https://arxiv.org/abs/2608.15417) (arXiv:2608.15417)
  * Survey Publication: *A contemporary review on chatbots, AI-powered virtual conversational agents, ChatGPT* (*Computer Science Review*, 2024; DOI: 10.1016/j.cosrev.2024.100660)
  * Hackathons & Evals: Judge and contributor across Apart Research AI Control and Safety sprints ([Apart Research](https://apartresearch.com)).
* **Evaluation Focus & Priorities:**
  * **AI Control & representation engineering:** Cares about practical mechanisms to detect and intercept deceptive representations in LLMs.
  * **Translating policy to code:** Values evaluation suites that operationalize broad alignment and governance concepts into measurable software benchmarks.
  * **Sprint execution velocity:** Prioritizes modular, reproducible code, clear README setups, and immediate actionable utility for the AI safety ecosystem.

---

### Panel Synthesis: What Research Traits Will Impress This Panel

1. **Active Evasion Threat Modeling:** Treat collusion as deliberate, adaptive evasion against an active monitor (e.g., steganography, context splitting, prompt-injecting the monitor) rather than passive, cooperative agreement.
2. **Multi-Agent Control & Oversight:** Directly test an AI Control setup (untrusted colluding worker agents vs. trusted black-box/deliberative monitors) and measure the monitor's failure boundary.
3. **Behavioral Ground-Truth Telemetry:** Use concrete execution environments with verifiable trajectories and ground-truth artifacts (code execution, tool actions) instead of ungrounded chat prompts.
4. **Exhaustive Null Controls & Baselines:** Include strict ablation baselines (e.g., prompt-scrambled, single-agent, uncoordinated) to prove coordination is genuine collusion rather than shared pretraining bias.
5. **Distributional & Calibration Metrics:** Report trajectory distributions, failure distributions across diverse seeds, and variance rather than cherry-picked pass/fail anecdotes.
6. **Offensive Security Realism:** Subject the harness to a red-team hacker perspective—ensure the sandbox cannot be escaped and test edge cases where agents subvert the evaluation scaffolding itself.
7. **Structured Behavioral Escalation:** Implement quantitative escalation ladders (e.g., measuring gradual shifts from compliance to covert coordination to sabotage).
8. **Human-in-the-Loop Auditability:** Design logging and inspectable traces so human auditors can easily spot-check, verify, and understand the collusion failure modes.
9. **Governance & Standards Readiness:** Structure the evaluation so metrics directly inform third-party audit standards and frontier lab deployment gates (Inspect-compatible format).
10. **Clean, Reproducible Artifacts:** Deliver self-contained, open-source benchmark code with pinned environments, automated scoring scripts, and clear trajectory visualizations.
