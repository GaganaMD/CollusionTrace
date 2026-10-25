"""PGG peer-swap: one vLLM engine per Modal container (multi-engine-per-GPU is not workable in vLLM 0.10.2).
App `pgg-swap-split`; three web endpoints, each OpenAI-compatible with `--api-key $PGG_TOKEN`.
  base   Qwen/Qwen2.5-7B-Instruct          L4
  other  ibm-granite/granite-3.3-8b-instruct  L4
  strong Qwen/Qwen2.5-32B-Instruct-AWQ     L40S
Hard cap 30 min per container (~$1.8 total worst case). Deploy: PGG_TOKEN=... modal deploy serve_modal_split.py
Stop: modal app stop pgg-swap-split.  Weights come from the `pgg-swap-hf` volume (see serve_modal.py::download)."""
import os, subprocess, sys
import modal

CAP = 30 * 60
_tok = os.environ.get("PGG_TOKEN")
if not _tok and modal.is_local():
    raise SystemExit("set PGG_TOKEN")
_secret = modal.Secret.from_dict({"PGG_TOKEN": _tok or "unused"})
_vol = modal.Volume.from_name("pgg-swap-hf", create_if_missing=True)
_image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "vllm==0.10.2", "transformers==4.56.2", "huggingface_hub")  # transformers 5.x breaks vllm 0.10.2
app = modal.App("pgg-swap-split")
KW = dict(image=_image, timeout=CAP, scaledown_window=120, max_containers=1, secrets=[_secret],
          volumes={"/root/.cache/huggingface": _vol})


def _vllm(model, *extra):
    subprocess.Popen([sys.executable, "-m", "vllm.entrypoints.openai.api_server", "--model", model, "--host", "0.0.0.0",
                      "--port", "8000", "--max-model-len", "8192", "--enable-prefix-caching", "--max-num-seqs", "64",
                      "--api-key", os.environ["PGG_TOKEN"], *extra])


@app.function(gpu="L40S", **KW)
@modal.concurrent(max_inputs=64)  # without this a web function serves ONE request at a time (queueing: median latency 50-100s)
@modal.web_server(8000, startup_timeout=1200)
def base(): _vllm("deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", "--gpu-memory-utilization", "0.92")


@app.function(gpu="L4", **KW)
@modal.concurrent(max_inputs=64)  # without this a web function serves ONE request at a time (queueing: median latency 50-100s)
@modal.web_server(8000, startup_timeout=1200)
def other(): _vllm("ibm-granite/granite-3.3-8b-instruct", "--gpu-memory-utilization", "0.92")


@app.function(gpu="L40S", **KW)
@modal.concurrent(max_inputs=64)  # without this a web function serves ONE request at a time (queueing: median latency 50-100s)
@modal.web_server(8000, startup_timeout=1200)
def strong(): _vllm("Qwen/Qwen2.5-32B-Instruct-AWQ", "--quantization", "awq_marlin", "--gpu-memory-utilization", "0.92")
