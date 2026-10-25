"""Parameterised Modal deployment of a protected vLLM OpenAI-compatible server.

Configure with environment variables at deploy time (they are baked into the
image env so the container sees the same values):
  CT_APP, CT_MODEL, CT_GPU, CT_MAX_LEN, CT_TOOL_PARSER (or ''), CT_REASONING_PARSER (or ''),
  CT_CONCURRENCY, CT_GPU_UTIL
Example:
  CT_APP=ct-qwen3-8b CT_MODEL=Qwen/Qwen3-8B CT_GPU=L4 CT_TOOL_PARSER=hermes \
  CT_REASONING_PARSER=qwen3 modal deploy modal/serve_vllm.py
Requests must carry the bearer key from the Modal secret `collusiontrace-vllm-auth`.
"""
from __future__ import annotations

import os
import subprocess

import modal

KEYS = ("CT_APP", "CT_MODEL", "CT_GPU", "CT_MAX_LEN", "CT_TOOL_PARSER", "CT_REASONING_PARSER", "CT_CONCURRENCY", "CT_GPU_UTIL",
        "CT_MAX_CONTAINERS")
CFG = {k: os.environ.get(k, "") for k in KEYS}
CFG["CT_APP"] = CFG["CT_APP"] or "collusiontrace-qwen-vllm"
CFG["CT_MODEL"] = CFG["CT_MODEL"] or "Qwen/Qwen2.5-7B-Instruct"
CFG["CT_GPU"] = CFG["CT_GPU"] or "L4"
CFG["CT_MAX_LEN"] = CFG["CT_MAX_LEN"] or "8192"
CFG["CT_CONCURRENCY"] = CFG["CT_CONCURRENCY"] or "24"
CFG["CT_GPU_UTIL"] = CFG["CT_GPU_UTIL"] or "0.90"
CFG["CT_MAX_CONTAINERS"] = CFG["CT_MAX_CONTAINERS"] or "1"
PORT = 8000

app = modal.App(CFG["CT_APP"])
hf_cache = modal.Volume.from_name("collusiontrace-huggingface-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("collusiontrace-vllm-cache", create_if_missing=True)
auth = modal.Secret.from_name("collusiontrace-vllm-auth", required_keys=["VLLM_API_KEY"])
image = (
    modal.Image.from_registry("nvidia/cuda:12.4.0-devel-ubuntu22.04", add_python="3.11")
    .uv_pip_install("vllm==0.10.2", "transformers==4.56.2")
    .env({k: v for k, v in CFG.items()})
)


@app.server(
    image=image, gpu=CFG["CT_GPU"], port=PORT, min_containers=0, max_containers=int(CFG["CT_MAX_CONTAINERS"]),
    scaledown_window=5 * 60, startup_timeout=25 * 60, target_concurrency=int(CFG["CT_CONCURRENCY"]),
    unauthenticated=True, secrets=[auth],
    volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache},
)
class VLLMServer:
    @modal.enter()
    def start(self) -> None:
        cmd = ["vllm", "serve", CFG["CT_MODEL"], "--host", "0.0.0.0", "--port", str(PORT),
               "--served-model-name", CFG["CT_MODEL"], "--api-key", os.environ["VLLM_API_KEY"],
               "--dtype", "bfloat16" if CFG["CT_GPU"] in {"H100", "A100-80GB", "H200", "L40S"} else "half",
               "--max-model-len", CFG["CT_MAX_LEN"], "--gpu-memory-utilization", CFG["CT_GPU_UTIL"],
               "--max-num-seqs", CFG["CT_CONCURRENCY"]]
        if CFG["CT_TOOL_PARSER"]:
            cmd += ["--enable-auto-tool-choice", "--tool-call-parser", CFG["CT_TOOL_PARSER"]]
        if CFG["CT_REASONING_PARSER"]:
            cmd += ["--reasoning-parser", CFG["CT_REASONING_PARSER"]]
        self.process = subprocess.Popen(cmd)

    @modal.exit()
    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=30)
