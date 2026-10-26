"""Shared retry helpers for the queued API clients.

Added for the peer-swap sprint: the original clients gave up immediately on
error bodies returned with HTTP 200 and on empty replies, which wiped out whole
stages during brief provider hiccups.
"""
from __future__ import annotations
import json
import os
import random
import time
from typing import Any, Dict

MIN_ATTEMPTS = 8
ERROR_LOG = os.getenv("API_ERROR_LOG", "outputs/api_errors.jsonl")


class EmptyOrErrorResponse(Exception):
    """Reply arrived but held an error body or no usable content; worth retrying."""


def backoff_seconds(attempt: int) -> float:
    """Exponential backoff capped at 60 s, with jitter."""
    return min(60.0, 2.0 ** attempt) + random.random()


def log_failures(provider: str, requests_list, results: Dict[str, Any]) -> None:
    """Append every request that still failed after all retries to ERROR_LOG."""
    models = {r.get("custom_id"): r.get("model") for r in requests_list}
    failed = [(cid, r) for cid, r in results.items() if isinstance(r, dict) and r.get("status") == "error"]
    if not failed:
        return
    os.makedirs(os.path.dirname(ERROR_LOG) or ".", exist_ok=True)
    with open(ERROR_LOG, "a") as f:
        for cid, r in failed:
            f.write(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "provider": provider,
                                "model": models.get(cid), "custom_id": cid, "error": str(r.get("error"))[:500]}) + "\n")
