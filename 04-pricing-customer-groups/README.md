# 04 · Customer-group pricing pilot (supplementary)

*Kaustubh Gupta ([@Kaustubh73](https://github.com/Kaustubh73)). Pre-sprint feasibility work. It is
**not part of the sprint submission** and is kept for transparency.*

**Question.** Do LLM pricing agents quote different markups depending on a customer's stated
language, culture, gender or age? And does that change when two sellers can collude?

**Setup.**
- Pre-registered in [`PREREG.md`](pilot_customer_groups/PREREG.md) before any run.
- Uses the agent, prompt and storage layers of
  [algorithmic_pricing_llms](https://github.com/luciasauer/algorithmic_pricing_llms) (MIT, vendored in
  [`third_party/`](third_party)).
- Model: `qwen2.5:14b-instruct` served with Ollama.

**Outcome.**
- The pre-registered collusion check failed: the duopoly-with-chat markup was not above the duopoly
  without chat.
- The pilot was therefore dropped in favour of the peer-swap direction.
- See [`REPORT.md`](pilot_customer_groups/REPORT.md) and the figures in
  [`pilot_customer_groups/figures/`](pilot_customer_groups/figures).
- The non-English request text is machine-generated and has not been reviewed.

```bash
cd pilot_customer_groups
pip install -r requirements.txt
python group_sim.py --help        # simulation (Ollama backend)
python analyze.py --help          # analysis
python make_figures.py            # figures
```
