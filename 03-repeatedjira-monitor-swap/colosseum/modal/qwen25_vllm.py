"""Modal deployment definition for a protected Qwen2.5-7B vLLM server.

This file is inert until `modal deploy` is run explicitly.  It serves vLLM's
native OpenAI-compatible API, including `/v1/models` and
`/v1/chat/completions`.  vLLM enforces a bearer token from the Modal Secret.
"""

from __future__ import annotations

import os
import subprocess

import modal

APP_NAME = "collusiontrace-qwen-vllm"
MODEL = "Qwen/Qwen2.5-7B-Instruct"
PORT = 8000
MINUTES = 60

app = modal.App(APP_NAME)
hf_cache = modal.Volume.from_name("collusiontrace-huggingface-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("collusiontrace-vllm-cache", create_if_missing=True)
auth = modal.Secret.from_name("collusiontrace-vllm-auth", required_keys=["VLLM_API_KEY"])

# Pinning this image makes future reproducibility easier; update deliberately
# after validating tool calling again. L4 (24 GB) comfortably accommodates
# Qwen2.5-7B with this conservative context and memory fraction.
image = (
    modal.Image.from_registry("nvidia/cuda:12.4.0-devel-ubuntu22.04", add_python="3.11")
    .uv_pip_install("vllm==0.10.2", "transformers==4.56.2")
)


@app.server(
    image=image,
    gpu="L4",
    port=PORT,
    min_containers=0,
    max_containers=1,
    scaledown_window=5 * MINUTES,
    startup_timeout=15 * MINUTES,
    target_concurrency=1,
    # The URL is public at Modal's routing layer, but vLLM rejects every API
    # request without VLLM_API_KEY. Do not remove --api-key below.
    unauthenticated=True,
    secrets=[auth],
    volumes={
        "/root/.cache/huggingface": hf_cache,
        "/root/.cache/vllm": vllm_cache,
    },
)
class QwenVLLMServer:
    @modal.enter()
    def start(self) -> None:
        api_key = os.environ["VLLM_API_KEY"]
        self.process = subprocess.Popen(
            [
                "vllm", "serve", MODEL,
                "--host", "0.0.0.0", "--port", str(PORT),
                "--served-model-name", MODEL,
                "--api-key", api_key,
                "--dtype", "half",
                "--max-model-len", "8192",
                "--gpu-memory-utilization", "0.85",
                "--enable-auto-tool-choice",
                "--tool-call-parser", "hermes",
            ]
        )

    @modal.exit()
    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=30)
