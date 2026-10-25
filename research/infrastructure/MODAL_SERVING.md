# Modal serving (current)

`colosseum/modal/serve_vllm.py` deploys one protected vLLM OpenAI-compatible server per
model; settings come from `CT_*` env vars at deploy time (baked into the image env).

| App | Model | GPU | Tool parser | Reasoning parser |
|---|---|---|---|---|
| ct-qwen25-7b | Qwen/Qwen2.5-7B-Instruct | L4 | hermes | — |
| ct-qwen3-8b | Qwen/Qwen3-8B | H100 | hermes | qwen3 |
| ct-r1d-qwen7b | deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | H100 | — (text ACTION lines) | deepseek_r1 |
| ct-qwen3-32b | Qwen/Qwen3-32B | H100 | hermes | qwen3 |

Pins: vllm 0.10.2 + transformers 4.56.2 (newer transformers breaks vLLM 0.10.2
startup); modal client ≥ 1.6 (`@app.server`). URLs are `https://<workspace>--<app>-vllmserver.<region>.modal.direct/v1`.
Auth: bearer key in Modal secret `collusiontrace-vllm-auth`; local copy in gitignored
`colosseum/.env.modal.local`. Servers scale to zero 5 min after the last request; the
runner waits for readiness and retries cold-start 503s. Stop explicitly with
`modal app stop <app>` after a study.
L4 was ~15 tok/s per stream for 8B reasoning models — use H100 for reasoning models.
