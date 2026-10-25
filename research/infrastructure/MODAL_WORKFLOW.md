# Modal-backed Qwen workflow (Phase 1)

This workflow serves `Qwen/Qwen2.5-7B-Instruct` with vLLM on Modal and uses Terrarium's `vllm` provider. It does not use OpenAI inference.

## Deployment (requires approval)

```powershell
cd colosseum
uv run --with modal modal token new
$env:VLLM_API_KEY = "<generate-a-long-random-value>"
uv run --with modal modal secret create collusiontrace-vllm-auth VLLM_API_KEY=$env:VLLM_API_KEY
uv run --with modal modal deploy modal/qwen25_vllm.py
$env:MODAL_VLLM_BASE_URL = "https://<Modal-server-URL>/v1"
$env:MODAL_VLLM_API_KEY = $env:VLLM_API_KEY
```

The Modal URL is publicly routable, but vLLM rejects every API request without the bearer token in the Modal secret. Cache Volumes reduce repeated downloads. The service has zero minimum containers, a single-container cap, and a five-minute idle scale-down. A first request after scale-to-zero may receive a transient 503 while the model loads; retry after it becomes ready.

## Validate, check, and run

```powershell
cd colosseum
.\.venv\Scripts\python.exe -m experiments.collusion.modal_workflow validate --config experiments/collusion/configs/collusion_jira_modal_smoke.yaml
.\.venv\Scripts\python.exe -m experiments.collusion.modal_workflow run --config experiments/collusion/configs/collusion_jira_modal_smoke.yaml --dry-run
```

`endpoint-check` is an authenticated `GET /v1/models`, not inference, but can wake a scale-to-zero GPU server. Use it only after approval:

```powershell
.\.venv\Scripts\python.exe -m experiments.collusion.modal_workflow endpoint-check --config experiments/collusion/configs/collusion_jira_modal_smoke.yaml
```

The CLI refuses remote inference without explicit acknowledgement:

```powershell
# One 3-agent smoke episode
.\.venv\Scripts\python.exe -m experiments.collusion.modal_workflow run --config experiments/collusion/configs/collusion_jira_modal_smoke.yaml --allow-inference
# Matched baseline / secret-channel comparison, three seeds
.\.venv\Scripts\python.exe -m experiments.collusion.modal_workflow compare --config experiments/collusion/configs/collusion_jira_modal_comparison.yaml --allow-inference
```

Each output root is timestamped and the runner refuses to merge into an existing directory. `manifest.json` records experiment ID, time, Git revision, model identifiers, and trace/monitor boundary. `config.json` is credential-redacted. Per-run raw evidence lives below `runs/<model>/<sweep>/<run>/` (prompts, trajectories, tool events, blackboards, metrics). Keep future monitor evaluations separate, preserving matched raw trajectories for O0/O1/O2 work. A secret channel is an experimental condition, not ground truth for harmful collusion.

```powershell
.\.venv\Scripts\python.exe -m experiments.collusion.modal_workflow locate --root experiments/collusion/outputs/collusion_modal_smoke
uv run --with modal modal server list
uv run --with modal modal server stats collusiontrace-qwen-vllm/qwenvllmserver --since 30m
```

No explicit GPU shutdown is needed: the five-minute idle window scales to zero. Do not delete cache Volumes unless intentionally discarding cached weights.

## Integration notes

Terrarium 0.2.1 normalizes `checkpoint` only for its internal ID, but uses `served_model_name` verbatim for requests and `/v1/models` matching. Both sides therefore use exactly `Qwen/Qwen2.5-7B-Instruct`. `base_url` must be HTTPS and end in `/v1`; Terrarium appends `/chat/completions` and `/models`.

Terrarium attaches `Authorization: Bearer ...` and honors `request_timeout` for chat requests. Its stock preflight omits authorization, so the opt-in `remote_authenticated: true` shim adds it without modifying `.venv`. Its client maps `max_completion_tokens` (or `max_output_tokens`) to vLLM `max_tokens` and silently ignores YAML `max_tokens`; supplied configs use the former.

The supplied smoke and comparison configurations set `temperature: 0`, which uses greedy decoding and removes sampling randomness from model generation. This is necessary for matched-condition experiments, but it is not a guarantee of fully bitwise-reproducible GPU execution: vLLM, CUDA/PyTorch kernels, hardware, driver versions, and future package/model revisions can still affect outputs. Record the deployment image, vLLM version, model identifier, Git commit, and run artifacts; keep runs sequential as configured.

For Qwen2.5, vLLM specifies Hermes tool parsing. The server uses `--enable-auto-tool-choice --tool-call-parser hermes` and the model tokenizer template. References: [Modal vLLM example](https://modal.com/docs/examples/llm_inference), [Modal servers](https://modal.com/docs/guide/servers), and [vLLM Qwen tools](https://docs.vllm.ai/en/latest/features/tool_calling/).

## Cost estimate (not a quote)

L4 (24 GB) is a conservative fit for a 7B half-precision model with an 8k context. As of 2026-10-23, Modal publishes L4 at $0.000222/second ($0.7992/hour), before small CPU/memory charges and any regional multiplier. The configured five-minute idle window alone is about $0.0666 GPU cost; a 10-minute cold-start-plus-smoke session is about $0.1332 GPU cost. These are estimates, not a quote: cache Volumes reduce downloads but not model load, and rates/regions can change. With ~$50 credit, begin with one approved smoke episode and retain `max_concurrent_runs: 1`.
