"""Smoke test for the PGG peer-swap Modal router.

    export PGG_BASE_URL=https://<workspace>--pgg-swap-vllm-serve.modal.run
    export PGG_TOKEN=<same secret used at deploy>
    python experiments/pgg_swap/smoke_test.py

Sends one chat completion to each of the three models in parallel and prints
model, latency, and the first 80 chars of the reply. The token is only ever
put into request headers, never printed.

Note: immediately after a cold deploy the first request triggers container
boot (a few minutes; longer on first-ever start while weights download). If a
request times out, wait and rerun.
"""

import asyncio
import os
import sys
import time

import httpx

MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-32B-Instruct-AWQ",
    "ibm-granite/granite-3.3-8b-instruct",
]


async def main() -> int:
    base = os.environ.get("PGG_BASE_URL", "").rstrip("/")
    token = os.environ.get("PGG_TOKEN", "")
    if not base or not token:
        print("set PGG_BASE_URL and PGG_TOKEN env vars", file=sys.stderr)
        return 1

    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0)) as client:
        try:
            health = await client.get(f"{base}/healthz")
            print(f"healthz -> {health.status_code} {health.json()}")
        except Exception as exc:
            print(f"healthz unreachable: {exc}")

        async def hit(model: str):
            t0 = time.perf_counter()
            try:
                r = await client.post(
                    f"{base}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "model": model,
                        "max_tokens": 8,
                        "messages": [{"role": "user", "content": "Reply with exactly: ok"}],
                    },
                )
                dt = time.perf_counter() - t0
                if r.status_code != 200:
                    return False, f"{model}: HTTP {r.status_code} after {dt:.1f}s :: {r.text[:80]}"
                content = r.json()["choices"][0]["message"]["content"]
                return True, f"{model}: {dt:.1f}s  {content[:80]!r}"
            except Exception as exc:
                return False, f"{model}: error after {time.perf_counter() - t0:.1f}s :: {type(exc).__name__}: {exc}"

        results = await asyncio.gather(*(hit(m) for m in MODELS))

    ok = True
    for good, line in results:
        print(line)
        ok = ok and good
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
