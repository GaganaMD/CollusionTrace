# Open-Source Starter Repositories Catalog

The organizers designed every starter route to run on a standard 16 GB laptop with **no GPU required**, using API-based inference or lightweight CPU execution.

| Repository | Organization / Author | Primary Track / RQ | Description & Setup Notes | GitHub URL |
| :--- | :--- | :--- | :--- | :--- |
| **`colosseum`** | UMass AI Safety (`umass-ai-safety`) | Track 2 (RQ 2.1), Track 3 (RQ 3.1) | Realistic multi-agent workplace environments (Hospital triage and Jira software engineering). Tests *coalition advantage* and private vs public communication. Preflight Terrarium dependencies. | [umass-ai-safety/colosseum](https://github.com/umass-ai-safety/colosseum) |
| **`LLM-Agent-collusion`** | `AgentSafety2025` (Voluntary Collusion codebase, as mapped on the sprint page) | Track 3 (RQ 3.2) | Liar's Bar and Cleanup games with baseline, secret-channel and secret-hint conditions. Local HuggingFace open-weight models (7B+), designed for H100; no API path, so an adapter is needed for a 16 GB laptop. | [AgentSafety2025/LLM-Agent-collusion](https://github.com/AgentSafety2025/LLM-Agent-collusion) |
| **`LLMCartel`** | Matt Riemer (`mattriemer`) | Track 1 (RQ 1.1, 1.2) | Repeated pricing games with customizable prompt prefixes, temperature sweeps, and round monitoring. Ideal for variable ablations and checkpoint branching. | [mattriemer/LLMCartel](https://github.com/mattriemer/LLMCartel) |
| **`algorithmic_pricing_llms`** | Lucia Sauer (`luciasauer`) | Track 1 (RQ 1.1) | Clean, standalone 2-seller Bertrand duopoly implementation (`experiments_synthetic/duopoly.py`). 300-round histories with explicit economic demand functions. | [luciasauer/algorithmic_pricing_llms](https://github.com/luciasauer/algorithmic_pricing_llms) |
| **`LLM-Trust-Breaking`** | Jerick Shi (`Jerick-1380`) | Track 2 (RQ 2.2), Track 3 (RQ 3.3) | Harness for repeated social dilemmas (trust games, prisoner's dilemmas). Formats and records private plans, public speech, and actions. Compatible with OpenAI and OpenRouter APIs. | [Jerick-1380/LLM-Trust-Breaking](https://github.com/Jerick-1380/LLM-Trust-Breaking) |
| **`TraceGuard`** | Linh Kid (`linhkid`) | Track 2 (RQ 2.2) | Action-trace consistency monitor. Compares agent stated intentions against executed tool traces to catch discrepancies. Easily adapted as a judge module. | [linhkid/TraceGuard](https://github.com/linhkid/TraceGuard) |
| **`focal-points`** | Emanuele LM (`EmanueleLM`) | Track 1 (RQ 1.2), Track 3 (RQ 3.3) | Benchmarks for benign Schelling focal point convergence in repeated matrix coordination games. Low compute baseline. | [EmanueleLM/focal-points](https://github.com/EmanueleLM/focal-points) |
| **`Steganographic_Collusion`** | Om Tailor (`Ostailor`), ColludeBench for "Audit the Whisper" | Track 2 (RQ 2.3) | Pricing, first-price auction, peer-review and double-auction scenarios with covert-channel colluders and a statistical audit pipeline (FPR 1e-3 calibration). Text channels only; has tests. Preflight, not ready-made data. Not Motwani's NeurIPS 2024 code. | [Ostailor/Steganographic_Collusion](https://github.com/Ostailor/Steganographic_Collusion) |
| **`collusive-llm-agents`** | Ryan Lin / Siddhartha Ojha (`smojha`) | Track 1 (RQ 1.1), Track 3 (RQ 3.1) | Cournot multi-commodity competition notebooks demonstrating market division and anti-competitive practices. | [smojha/collusive-llm-agents](https://github.com/smojha/collusive-llm-agents) |
| **`llm-agent-collusion`** | `andyjliu`, Agrawal et al. (arXiv 2507.01413) | Track 1 (RQ 1.3, 1.5), Track 3 (RQ 3.4) | Continuous double-auction harness: 5 sellers and 6 buyers by default, seller chat, message caps, oversight notices, temperature sweeps. API-based (OpenAI/Anthropic/OpenRouter); several pinned model IDs are reported retired (unverified). | [andyjliu/llm-agent-collusion](https://github.com/andyjliu/llm-agent-collusion) |

---

## Recommended Local Environment Setup

```bash
# Recommended Python virtual environment
cd ~/Desktop/Speshal/projects/ai-collusion-research-sprint
python3 -m venv .venv
source .venv/bin/activate

# Core dependencies for API harnesses and statistics
pip install numpy scipy pandas matplotlib seaborn httpx openai anthropic tenacity
```
