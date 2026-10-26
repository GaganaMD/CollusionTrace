"""API clients with spend guards.

Real runs use the harness's queued OpenAI / OpenRouter clients (patched with retries).
Tests pass a FakeClient instead. Both expose `execute_all(requests) -> {id: reply}`.
"""
from __future__ import annotations

import json
import time
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.endogenous.core.trial_runner import _execute_requests_split_by_provider
from src.llm.client_factory import is_openai_model


class SpendCapReached(RuntimeError):
    """A spend guard stopped the run (at a batch boundary, so it can be resumed)."""


def transcript_file(root: Path, request_id: str) -> Path:
    """Where a request's raw exchange is logged, from its id.

    'r5.equal.t3.s1.J' -> root/equal/trial_3.jsonl, 'r2.trunk.t0.refl.J>M' ->
    root/trunk/trial_0.jsonl, change-judge ids 'judge.<hash>' -> root/judge/notes.jsonl,
    and ceiling-test ids 'ceiling.<...>' -> root/ceiling/items.jsonl.
    """
    parts = request_id.split(".")
    if parts[0] == "judge":
        return root / "judge" / "notes.jsonl"
    if parts[0] == "ceiling":
        return root / "ceiling" / "items.jsonl"
    condition, trial = parts[1], parts[2]
    return root / condition / f"trial_{trial.lstrip('t')}.jsonl"


class Clients:
    """Routes requests to the right provider, enforces the OpenAI call cap, and logs
    every exchange (prompts and raw reply) when `transcript_dir` is set."""

    def __init__(self, openai: Any, openrouter: Any, max_openai_calls: Optional[int] = None,
                 transcript_dir: Optional[Path] = None):
        self.openai = openai
        self.openrouter = openrouter
        self.max_openai_calls = max_openai_calls
        self.openai_calls = 0
        self.transcript_dir = Path(transcript_dir) if transcript_dir else None
        if self.transcript_dir is not None:
            # Fail before any spend if transcripts can't be written.
            self.transcript_dir.mkdir(parents=True, exist_ok=True)
            probe = self.transcript_dir / ".write_test"
            probe.write_text("ok")
            probe.unlink()
        # Marks transcript lines from this process; a resumed run starts a new session.
        self.session = time.strftime("%Y%m%dT%H%M%S")
        self._sends: Counter = Counter()   # times each request id has been sent this session (re-asks > 1)

    def _log(self, requests: List[Dict[str, Any]], replies: Dict[str, Any], label: str) -> None:
        """Append one JSON line per request: id, model, prompts, raw reply, attempt number."""
        if self.transcript_dir is None:
            return
        lines: Dict[Path, List[str]] = {}
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        for req in requests:
            cid = req["custom_id"]
            self._sends[cid] += 1
            messages = {m["role"]: m["content"] for m in req.get("messages", [])}
            record = {"time": stamp, "session": self.session, "batch": label, "request_id": cid,
                      "attempt": self._sends[cid],
                      "model": req["model"], "system_prompt": messages.get("system"),
                      "user_prompt": messages.get("user"), "raw_reply": replies.get(cid)}
            lines.setdefault(transcript_file(self.transcript_dir, cid), []).append(
                json.dumps(record, default=str))
        for path, entries in lines.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a") as f:
                f.write("\n".join(entries) + "\n")

    def check_room(self, n_openai: int) -> None:
        """Raise SpendCapReached if `n_openai` more calls would exceed the cap.

        Called before each round with that round's expected calls, so a run stops at a
        round boundary rather than paying for a half-played round.
        """
        if self.max_openai_calls is not None and self.openai_calls + n_openai > self.max_openai_calls:
            raise SpendCapReached(f"OpenAI call cap {self.max_openai_calls} reached "
                                  f"({self.openai_calls} used, next round needs about {n_openai})")

    def execute(self, requests: List[Dict[str, Any]], label: str) -> Dict[str, Any]:
        """Send a batch and return {request id: reply}.

        Raises SpendCapReached *before* sending if the batch would exceed the OpenAI
        call cap.
        """
        if not requests:
            return {}
        n_openai = sum(is_openai_model(r["model"]) for r in requests)
        if self.max_openai_calls is not None and self.openai_calls + n_openai > self.max_openai_calls:
            raise SpendCapReached(f"OpenAI call cap {self.max_openai_calls} reached "
                                  f"({self.openai_calls} used, batch needs {n_openai})")
        self.openai_calls += n_openai
        replies = _execute_requests_split_by_provider(requests, self.openai, self.openrouter, label)
        try:
            self._log(requests, replies, label)
        except (OSError, TypeError, ValueError) as err:
            # The batch is already paid for: never lose it to a logging problem.
            print(f"WARNING: could not write transcripts for batch '{label}': {err!r}")
        return replies


def make_clients(models: List[str], max_openai_calls: Optional[int],
                 transcript_dir: Optional[Path] = None) -> Clients:
    """Build real clients for the providers these models need (reads API keys)."""
    from src.config import settings
    from src.llm.providers.queued_openai import QueuedOpenAIClient
    from src.llm.providers.queued_openrouter import QueuedOpenRouterClient

    need_openai = any(is_openai_model(m) for m in models)
    need_openrouter = any(not is_openai_model(m) for m in models)
    if need_openai and not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in harness/.env")
    if need_openrouter and not settings.OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set in harness/.env")
    openai = (QueuedOpenAIClient(api_key=settings.OPENAI_API_KEY, max_workers=25, timeout=120,
                                 max_retries=5) if need_openai else None)
    openrouter = (QueuedOpenRouterClient(api_key=settings.OPENROUTER_API_KEY, max_workers=25,
                                         timeout=120, max_retries=5) if need_openrouter else None)
    return Clients(openai, openrouter, max_openai_calls, transcript_dir)


def openrouter_usage() -> Optional[float]:
    """Total OpenRouter usage in USD for the account, or None if it can't be read."""
    from src.config import settings
    if not settings.OPENROUTER_API_KEY:
        return None
    req = urllib.request.Request("https://openrouter.ai/api/v1/credits",
                                 headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return float(json.load(resp)["data"]["total_usage"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
