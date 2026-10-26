"""API client: concurrent batches, retries, transcripts, cost tracking and spend guards.

Every model goes through OpenRouter's OpenAI-compatible API, unless OPENAI_DIRECT=1 is set,
in which case `openai/...` models go straight to OpenAI. The FakeClient in fake.py has the
same `execute(requests, label)` interface for offline runs.

A request is {"custom_id", "model", "system", "user", "temperature", "max_tokens"}; a reply
is {"content": str or None, "reasoning": str or None, "usage": {...}, "error": str or None}.
"reasoning" is the model's hidden reasoning text where the provider returns it (OpenRouter
does for Claude); it is logged in the raw transcripts but never shown to any player.
"""
from __future__ import annotations

import json
import os
import random
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

from signal_ring.config import PRICES, PROJECT_DIR

OPENROUTER_URL = "https://openrouter.ai/api/v1"
MAX_ATTEMPTS = 6
MAX_WORKERS = 16
TIMEOUT = 120


class SpendCapReached(RuntimeError):
    """A spend guard stopped the run at a round boundary; rerun the same command to resume."""


def load_env() -> None:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_DIR / ".env")


def transcript_file(root: Path, request_id: str) -> Path:
    """Where a request is logged: 'r5.warm.t3.talk.J' -> root/warm/trial_3.jsonl.

    Ids outside a game ('judge.…', 'ceiling.…', 'smoke.…') go to root/<prefix>.jsonl.
    """
    parts = request_id.split(".")
    if not parts[0].startswith("r") or len(parts) < 3:
        return root / f"{parts[0]}.jsonl"
    return root / parts[1] / f"trial_{parts[2].lstrip('t')}.jsonl"


def cost_of(model: str, usage: Dict[str, Any]) -> float:
    """USD for one reply: the provider's figure if given, else the price table."""
    if usage.get("cost") is not None:
        return float(usage["cost"])
    pin, pout = PRICES.get(model, (0.0, 0.0))
    return (usage.get("prompt_tokens", 0) * pin + usage.get("completion_tokens", 0) * pout) / 1e6


class Clients:
    """Sends batches concurrently, logs every exchange and tracks spend."""

    def __init__(self, transcript_dir: Optional[Path] = None, max_spend: Optional[float] = None,
                 max_openrouter_usage: Optional[float] = None, anthropic_cache: bool = True):
        load_env()
        from openai import OpenAI
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY is not set in .env")
        self.openrouter = OpenAI(base_url=OPENROUTER_URL, api_key=key, timeout=TIMEOUT, max_retries=0)
        self.openai = None
        if os.getenv("OPENAI_DIRECT") == "1":
            if not os.getenv("OPENAI_API_KEY"):
                raise RuntimeError("OPENAI_DIRECT=1 needs OPENAI_API_KEY in .env")
            self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=TIMEOUT, max_retries=0)
        self.max_spend = max_spend
        self.max_openrouter_usage = max_openrouter_usage
        self.anthropic_cache = anthropic_cache
        self.spent = 0.0
        self.calls = 0
        self.transcript_dir = Path(transcript_dir) if transcript_dir else None
        if self.transcript_dir is not None:
            self.transcript_dir.mkdir(parents=True, exist_ok=True)   # fail before any spend
        self.session = time.strftime("%Y%m%dT%H%M%S")
        self._sends: Dict[str, int] = {}

    # -- spend guards ------------------------------------------------------
    def check_budget(self) -> None:
        """Raise SpendCapReached if a cap is reached. Called between rounds."""
        if self.max_spend is not None and self.spent >= self.max_spend:
            raise SpendCapReached(f"this run spent ${self.spent:.2f} of its ${self.max_spend:.2f} cap")
        if self.max_openrouter_usage is not None:
            usage = openrouter_usage()
            if usage is None:
                raise SpendCapReached("could not read OpenRouter usage to check the cap")
            if usage >= self.max_openrouter_usage:
                raise SpendCapReached(f"OpenRouter account usage ${usage:.2f} reached the "
                                      f"${self.max_openrouter_usage:.2f} cap")

    # -- one call ------------------------------------------------------------
    def _messages(self, req: Dict[str, Any]) -> List[Dict[str, Any]]:
        system: Any = req["system"]
        if self.anthropic_cache and req["model"].startswith("anthropic/"):
            # Anthropic caches only marked prefixes; the system prompt starts with the
            # append-only memory log, so a player's calls within a round share it.
            system = [{"type": "text", "text": req["system"], "cache_control": {"type": "ephemeral"}}]
        return [{"role": "system", "content": system}, {"role": "user", "content": req["user"]}]

    def _call(self, req: Dict[str, Any]) -> Dict[str, Any]:
        model = req["model"]
        direct = self.openai is not None and model.startswith("openai/")
        client = self.openai if direct else self.openrouter
        kwargs: Dict[str, Any] = dict(model=model.split("/", 1)[1] if direct else model,
                                      messages=self._messages(req),
                                      temperature=req.get("temperature", 1.0),
                                      max_tokens=req.get("max_tokens", 4000))
        if not direct:
            kwargs["extra_body"] = {"usage": {"include": True}}
            if req.get("reasoning_max_tokens"):
                kwargs["extra_body"]["reasoning"] = {"max_tokens": req["reasoning_max_tokens"]}
        last_error = ""
        for attempt in range(MAX_ATTEMPTS):
            try:
                resp = client.chat.completions.create(**kwargs)
                msg = resp.choices[0].message if resp.choices else None
                content = msg.content if msg else None
                reasoning = getattr(msg, "reasoning", None) if msg else None
                usage = resp.usage.model_dump() if resp.usage else {}
                finish = resp.choices[0].finish_reason if resp.choices else None
                if content and content.strip():
                    return {"content": content, "reasoning": reasoning, "usage": usage,
                            "finish_reason": finish, "error": None}
                last_error = f"empty reply (finish_reason={finish})"
            except Exception as err:   # network, rate limit, provider error: all retried
                last_error = f"{type(err).__name__}: {err}"[:500]
            time.sleep(min(60.0, 2.0 ** attempt) + random.random())
        return {"content": None, "reasoning": None, "usage": {}, "error": last_error}

    # -- batches -------------------------------------------------------------
    def execute(self, requests: List[Dict[str, Any]], label: str) -> Dict[str, Dict[str, Any]]:
        """Send a batch concurrently and return {request id: reply}."""
        if not requests:
            return {}
        with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(requests))) as pool:
            replies = dict(zip([r["custom_id"] for r in requests], pool.map(self._call, requests)))
        for req in requests:
            self.calls += 1
            self.spent += cost_of(req["model"], replies[req["custom_id"]]["usage"])
        try:
            self._log(requests, replies, label)
        except (OSError, TypeError, ValueError) as err:
            print(f"WARNING: could not write transcripts for batch '{label}': {err!r}")
        return replies

    def _log(self, requests: List[Dict[str, Any]], replies: Dict[str, Any], label: str) -> None:
        if self.transcript_dir is None:
            return
        lines: Dict[Path, List[str]] = {}
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        for req in requests:
            cid = req["custom_id"]
            self._sends[cid] = self._sends.get(cid, 0) + 1
            reply = replies.get(cid, {})
            record = {"time": stamp, "session": self.session, "batch": label, "request_id": cid,
                      "attempt": self._sends[cid], "model": req["model"],
                      "system_prompt": req["system"], "user_prompt": req["user"],
                      "reply": reply.get("content"), "reasoning": reply.get("reasoning"),
                      "finish_reason": reply.get("finish_reason"),
                      "error": reply.get("error"),
                      "usage": reply.get("usage")}
            lines.setdefault(transcript_file(self.transcript_dir, cid), []).append(
                json.dumps(record, default=str))
        for path, entries in lines.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a") as f:
                f.write("\n".join(entries) + "\n")


def openrouter_usage() -> Optional[float]:
    """Total OpenRouter usage in USD for the account, or None if it can't be read."""
    load_env()
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return None
    req = urllib.request.Request(f"{OPENROUTER_URL}/credits", headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return float(json.load(resp)["data"]["total_usage"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
