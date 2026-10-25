"""
serve_modal_reasoning.py: Serve reasoning model (Qwen3-8B) on Modal with thinking ON vs OFF.
Enforces strict <think> token stripping in the router so thinking traces never leak
into game transcripts or observer memory.
"""

import os
import re
import subprocess
import sys
import modal

_TOKEN = os.environ.get("PGG_TOKEN")
if not _TOKEN and modal.is_local():
    raise SystemExit("set PGG_TOKEN")
_secret = modal.Secret.from_dict({"PGG_TOKEN": _TOKEN or "unused"})
_vol = modal.Volume.from_name("pgg-swap-hf", create_if_missing=True)

_image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "vllm==0.10.2",
    "transformers==4.56.2",
    "huggingface_hub",
    "fastapi",
    "httpx",
    "uvicorn",
)

app = modal.App("pgg-swap-reasoning")
KW = dict(
    image=_image,
    timeout=60 * 60,
    scaledown_window=180,
    max_containers=1,
    secrets=[_secret],
    volumes={"/root/.cache/huggingface": _vol},
)


def _start_vllm():
    """Start vLLM server on port 8001."""
    cmd = [
        sys.executable,
        "-m", "vllm.entrypoints.openai.api_server",
        "--model", "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "--host", "127.0.0.1",
        "--port", "8001",
        "--max-model-len", "8192",
        "--enable-prefix-caching",
        "--max-num-seqs", "64",
        "--gpu-memory-utilization", "0.90",
        "--api-key", os.environ["PGG_TOKEN"],
    ]
    subprocess.Popen(cmd)


@app.function(gpu="L40S", **KW)
@modal.concurrent(max_inputs=64)
@modal.web_server(8000, startup_timeout=1200)
def server():
    import json
    import httpx
    from fastapi import FastAPI, HTTPException, Request, Response

    _start_vllm()

    router = FastAPI()
    client_box = [None]

    @router.on_event("startup")
    async def startup():
        client_box[0] = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))

    @router.on_event("shutdown")
    async def shutdown():
        if client_box[0]:
            await client_box[0].aclose()

    @router.get("/health")
    async def health():
        if not client_box[0]:
            raise HTTPException(status_code=503, detail="router starting")
        try:
            r = await client_box[0].get("http://127.0.0.1:8001/health", timeout=3.0)
            if r.status_code == 200:
                return {"status": "ok"}
        except Exception:
            pass
        raise HTTPException(status_code=503, detail="vLLM backend initializing")

    @router.post("/v1/chat/completions")
    async def chat_completions(request: Request):
        tok = request.headers.get("authorization", "").replace("Bearer ", "").strip()
        if tok != os.environ["PGG_TOKEN"]:
            raise HTTPException(status_code=401, detail="Unauthorized")

        body = await request.json()
        model_req = body.get("model", "")

        # Handle thinking toggle:
        thinking_off = "nothink" in model_req.lower() or body.pop("thinking_off", False)
        if thinking_off:
            messages = body.get("messages", [])
            if messages and messages[0].get("role") == "system":
                messages[0]["content"] = "<think>\n</think>\n" + messages[0]["content"]

        # Forward to vLLM
        body["model"] = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
        r = await client_box[0].post(
            "http://127.0.0.1:8001/v1/chat/completions",
            json=body,
            headers={"Authorization": f"Bearer {os.environ['PGG_TOKEN']}"},
            timeout=180.0,
        )
        
        if r.status_code != 200:
            return Response(content=r.content, status_code=r.status_code, media_type="application/json")

        data = r.json()
        # STRIP <think>...</think> traces to prevent leakage into game transcripts
        for choice in data.get("choices", []):
            msg = choice.get("message", {})
            content = msg.get("content", "")
            if content:
                th_match = re.search(r"<think>([\s\S]*?)</think>", content)
                stripped = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()
                msg["content"] = stripped
                if th_match:
                    msg["thinking_chars"] = len(th_match.group(1))
                    msg["reasoning_content"] = th_match.group(1).strip()

        return Response(content=json.dumps(data), status_code=200, media_type="application/json")

    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8000, log_level="warning")
