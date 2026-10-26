"""PGG peer-swap experiment: serve the three models on Modal behind one router.

Backends (vLLM 0.10.2, ONE A100-80GB container):
    port 8001  Qwen/Qwen2.5-7B-Instruct             (BASE)   gpu_mem 0.22
    port 8002  Qwen/Qwen2.5-32B-Instruct-AWQ        (STRONG) gpu_mem 0.42
    port 8003  ibm-granite/granite-3.3-8b-instruct  (OTHER)  gpu_mem 0.24

An OpenAI-compatible FastAPI router on port 8000 (exposed with
@modal.web_server) requires `Authorization: Bearer $PGG_TOKEN` and dispatches
by the JSON `model` field to the matching backend port.

Deploy (token is read from the shell, embedded at deploy time, never printed):
    export PGG_TOKEN=<random-secret>
    modal deploy experiments/pgg_swap/serve_modal.py

Find the URL: the deploy output prints the .modal.run URL:
    https://<workspace>--pgg-swap-vllm-serve.modal.run
(verify with: modal app list / modal app logs pgg-swap-vllm -f)

Smoke test (from repo root, see smoke_test.py):
    PGG_BASE_URL=<url> PGG_TOKEN=$PGG_TOKEN python experiments/pgg_swap/smoke_test.py

Stop:    modal app stop pgg-swap-vllm
Logs:    modal app logs pgg-swap-vllm -f  (vLLM backend output goes here too)

Notes:
- HF weights (~50 GB across the three models) are cached in the "pgg-swap-hf"
  Volume at /root/.cache/huggingface; Modal volume storage is effectively
  free, and the cache makes warm starts a few minutes instead of ~20.
- The FIRST cold start must download all weights and may exceed the 1500 s
  web startup timeout: if the first request errors, wait a few minutes and
  retry; subsequent activations load from the volume.
- Budget/safety: max_containers=1, timeout=4h, and an in-process reaper that
  kills all backends at the 4h mark; scaledown_window=300s releases the GPU
  after 5 minutes without web traffic.
"""

import os
import subprocess
import sys
import time
from urllib.request import urlopen

import modal

SERVER_PORT = 8000
WEB_STARTUP_TIMEOUT = 1500
READY_BUDGET = 18 * 60      # wait for backend /health (≤) then start router anyway
HARD_CAP = 60 * 60          # 60 min cap (~$2.5 at A100-80GB): workspace spend was $10 of $15
STAGGER_S = 75              # sleep between backend launches

BACKENDS = {
    # OpenAI `model` name (HF id): (port, gpu_memory_utilization, extra flags)
    "Qwen/Qwen2.5-7B-Instruct": (8001, 0.28, []),
    "Qwen/Qwen2.5-32B-Instruct-AWQ": (8002, 0.40, ["--quantization", "awq_marlin"]),
    "ibm-granite/granite-3.3-8b-instruct": (8003, 0.28, []),
}
MODEL_PORT = {m: p for m, (p, _, _) in BACKENDS.items()}

# Fail fast at deploy time; the plaintext token is never printed anywhere.
_TOKEN = os.environ.get("PGG_TOKEN")
if not _TOKEN and modal.is_local():
    raise SystemExit(
        "PGG_TOKEN is not set. Deploy with: "
        "PGG_TOKEN=<secret> modal deploy experiments/pgg_swap/serve_modal.py"
    )
_pgg_secret = modal.Secret.from_dict({"PGG_TOKEN": _TOKEN or "unused"})

# Modal volume storage is effectively free; keeps the ~50 GB of weights warm.
_hf_volume = modal.Volume.from_name("pgg-swap-hf", create_if_missing=True)

_image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "vllm==0.10.2",
    "transformers==4.56.2",  # transformers 5.x breaks vllm 0.10.2 (all_special_tokens_extended)
    "huggingface_hub",
    "fastapi",
    "httpx",
    "uvicorn",
)

app = modal.App("pgg-swap-vllm")


def _back_ok(port: int) -> bool:
    try:
        with urlopen(f"http://127.0.0.1:{port}/health", timeout=5.0) as resp:
            return resp.status == 200
    except Exception:
        return False


def _make_router(token: str, hard_exit_at: float):
    """Build the FastAPI router.

    Heavy deps are imported lazily so that `modal deploy` on the local machine
    only needs the modal client, not fastapi/httpx.
    """
    import asyncio
    import hmac
    import signal
    from contextlib import asynccontextmanager

    import httpx
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import Response

    client_box: list = [None]  # shared AsyncClient, set in lifespan

    async def _hard_cap_reaper(when: float) -> None:
        await asyncio.sleep(max(0.0, when - time.monotonic()))
        print("[reaper] 4h hard cap reached: shutting down all backends", flush=True)
        try:
            os.killpg(os.getpgid(0), signal.SIGTERM)  # vLLM children share our group
        except Exception:
            pass
        await asyncio.sleep(5)
        os._exit(0)

    @asynccontextmanager
    async def lifespan(_app):
        client_box[0] = httpx.AsyncClient(
            timeout=httpx.Timeout(1200.0, connect=30.0),
            limits=httpx.Limits(max_connections=200, max_keepalive_connections=128),
        )
        reapers = [asyncio.get_running_loop().create_task(_hard_cap_reaper(hard_exit_at))]
        yield
        reapers[0].cancel()
        await client_box[0].aclose()

    router = FastAPI(title="pgg-swap router", lifespan=lifespan)

    def _auth_ok(request: Request) -> bool:
        got = request.headers.get("authorization", "")
        return hmac.compare_digest(got.encode(), f"Bearer {token}".encode())

    async def _backend_up(port: int) -> bool:
        if client_box[0] is None:
            return False
        try:
            r = await client_box[0].get(f"http://127.0.0.1:{port}/health", timeout=5.0)
            return r.status_code == 200
        except Exception:
            return False

    @router.get("/healthz")
    async def healthz():
        # No auth: reveals only per-backend up/down state.
        if client_box[0] is None:
            return {"backends": {}, "all_up": False}
        states = {m: await _backend_up(p) for m, p in MODEL_PORT.items()}
        return {"backends": states, "all_up": all(states.values())}

    async def _forward(request: Request, path: str):
        if not _auth_ok(request):
            raise HTTPException(status_code=401, detail="bad or missing bearer token")
        if client_box[0] is None:
            raise HTTPException(status_code=503, detail="router initialising")
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="request body must be JSON")
        if body.get("stream"):
            raise HTTPException(status_code=400, detail="streaming is not supported by this router")
        model = body.get("model")
        port = MODEL_PORT.get(model)
        if port is None:
            raise HTTPException(
                status_code=400,
                detail=f"unknown or missing model {model!r}; expected one of {sorted(MODEL_PORT)}",
            )
        try:
            backend = await client_box[0].post(f"http://127.0.0.1:{port}{path}", json=body)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"backend {model!r} unreachable: {exc!r}")
        return Response(
            content=backend.content,
            status_code=backend.status_code,
            media_type=backend.headers.get("content-type", "application/json"),
        )

    @router.post("/v1/chat/completions")
    async def chat_completions(request: Request):
        return await _forward(request, "/v1/chat/completions")

    @router.post("/v1/completions")
    async def completions(request: Request):
        return await _forward(request, "/v1/completions")

    @router.get("/v1/models")
    async def models(request: Request):
        if not _auth_ok(request):
            raise HTTPException(status_code=401, detail="bad or missing bearer token")
        if client_box[0] is None:
            raise HTTPException(status_code=503, detail="router initialising")
        data = []
        for model_id, port in MODEL_PORT.items():
            try:
                r = await client_box[0].get(f"http://127.0.0.1:{port}/v1/models", timeout=10.0)
                r.raise_for_status()
                data.extend(r.json().get("data", []))
            except Exception:
                pass  # backend down: leave it out
        if not data:
            data = [{"id": m, "object": "model"} for m in MODEL_PORT]  # still loading
        return {"object": "list", "data": data}

    return router


@app.function(
    image=_image,
    gpu="A100-80GB",
    timeout=HARD_CAP,
    scaledown_window=300,
    max_containers=1,
    secrets=[_pgg_secret],
    volumes={"/root/.cache/huggingface": _hf_volume},
)
@modal.web_server(SERVER_PORT, startup_timeout=WEB_STARTUP_TIMEOUT)
def serve():
    """Launch the three vLLM backends (staggered), wait for /health, then run the router."""
    t0 = time.monotonic()

    def log(msg: str) -> None:
        print(f"[{time.monotonic() - t0:6.0f}s] {msg}", flush=True)

    token = os.environ.get("PGG_TOKEN", "")
    if not token:
        raise RuntimeError("PGG_TOKEN missing in container env (check modal.Secret)")

    import threading

    import uvicorn

    router = _make_router(token, hard_exit_at=t0 + HARD_CAP)
    threading.Thread(
        target=lambda: uvicorn.run(router, host="0.0.0.0", port=SERVER_PORT, log_level="warning", access_log=False),
        daemon=True,
    ).start()
    log(f"router up on :{SERVER_PORT} (poll /healthz for backend readiness)")

    for i, (model_id, (port, gpu_frac, extra)) in enumerate(BACKENDS.items()):
        if i:
            time.sleep(STAGGER_S)  # stagger to avoid simultaneous CUDA memory profiling
        subprocess.Popen(
            env={**os.environ, "VLLM_HOST_IP": "127.0.0.1", "GLOO_SOCKET_IFNAME": "lo"},
            args=[
                sys.executable, "-m", "vllm.entrypoints.openai.api_server",
                "--model", model_id,
                "--host", "127.0.0.1",
                "--port", str(port),
                "--max-model-len", "8192",
                "--gpu-memory-utilization", str(gpu_frac),
                "--enable-prefix-caching",
                "--max-num-seqs", "96",
                *extra,
            ]
        )  # stdout/stderr inherit -> visible via `modal app logs`
        log(f"launched {model_id} on :{port}")


@app.function(
    image=_image,
    timeout=3 * 3600,
    volumes={"/root/.cache/huggingface": _hf_volume},
)
def download():
    """CPU-only: pre-fetch all weights into the volume so GPU time is not spent on downloads.
    Run: modal run experiments/pgg_swap/serve_modal.py::download"""
    from huggingface_hub import snapshot_download

    for m in BACKENDS:
        snapshot_download(m)
        print("downloaded", m, flush=True)
    _hf_volume.commit()
