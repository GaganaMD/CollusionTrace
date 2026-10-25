"""Minimal OpenAI-compatible chat client with a backend guard.

Only the Modal/vLLM endpoint (or an explicitly allowed host) may be called.
OpenRouter is refused unless ``allow_openrouter`` is set, so a misconfigured
run cannot silently fall back to it. Credentials are never logged.
"""
from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse

import requests


class ChatBackend(Protocol):
    label: str

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], tool_choice: str = "auto") -> dict[str, Any]:
        ...


def check_base_url(base_url: str, *, allow_openrouter: bool = False, allowed_suffixes: tuple[str, ...] = (".modal.run", ".modal.direct")) -> None:
    parsed = urlparse(base_url)
    host = parsed.hostname or ""
    if parsed.scheme != "https" or not parsed.path.rstrip("/").endswith("/v1"):
        raise ValueError("base_url must be an https URL ending in /v1")
    if "openrouter.ai" in host and not allow_openrouter:
        raise ValueError("OpenRouter is disabled for new experiments (set allow_openrouter only with explicit authorisation).")
    if "openrouter.ai" not in host and not any(host.endswith(s) for s in allowed_suffixes):
        raise ValueError(f"host {host!r} is not an allowed inference backend")


@dataclass
class OpenAICompatibleClient:
    base_url: str
    api_key: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 512
    timeout: int = 600
    max_retries: int = 2
    label: str = "modal-vllm"
    allow_openrouter: bool = False
    seed: int | None = None

    def __post_init__(self) -> None:
        check_base_url(self.base_url, allow_openrouter=self.allow_openrouter)
        if not self.api_key:
            raise ValueError("missing endpoint credential (set it via environment, never in config)")

    def __repr__(self) -> str:  # never expose the key
        return f"OpenAICompatibleClient(label={self.label!r}, model={self.model!r})"

    def models(self) -> list[str]:
        r = requests.get(self.base_url.rstrip("/") + "/models", headers={"Authorization": f"Bearer {self.api_key}"}, timeout=60)
        r.raise_for_status()
        return [m.get("id") for m in r.json().get("data", [])]

    def chat(self, messages, tools, tool_choice="auto"):
        body: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": self.temperature,
                                "max_tokens": self.max_tokens}
        if tools:
            body["tools"] = tools
            body["tool_choice"] = tool_choice
        if self.seed is not None:
            body["seed"] = self.seed
        last_err = None
        for attempt in range(self.max_retries + 1):
            t0 = time.time()
            try:
                r = requests.post(self.base_url.rstrip("/") + "/chat/completions", json=body,
                                  headers={"Authorization": f"Bearer {self.api_key}"}, timeout=self.timeout)
                if r.status_code >= 500 or r.status_code == 429:
                    raise RuntimeError(f"HTTP {r.status_code}")
                r.raise_for_status()
                data = r.json()
                msg = data["choices"][0]["message"]
                return {"message": msg, "usage": data.get("usage") or {}, "latency_s": round(time.time() - t0, 3),
                        "attempts": attempt + 1, "model": data.get("model")}
            except Exception as exc:  # noqa: BLE001 - recorded, retried, then raised
                last_err = f"{type(exc).__name__}: {exc}"
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"chat request failed after retries: {last_err}")


@dataclass
class ScriptedClient:
    """Deterministic offline policy for tests and dry runs (no network).

    ``policy(agent, phase, round, context) -> (tool_name, arguments) | None``.
    The agent name / phase / round are parsed from a machine-readable header the
    runner adds to every user prompt.
    """
    policy: Callable[[str, str, int, dict[str, Any]], tuple[str, dict[str, Any]] | None]
    label: str = "scripted"

    def chat(self, messages, tools, tool_choice="auto"):
        header = json.loads(messages[-1]["content"].split("\n", 1)[0].removeprefix("META "))
        decision = self.policy(header["agent"], header["phase"], header["round"], header)
        msg: dict[str, Any] = {"role": "assistant", "content": ""}
        if decision is not None:
            name, args = decision
            msg["tool_calls"] = [{"id": "call_0", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]
        return {"message": msg, "usage": {"prompt_tokens": 0, "completion_tokens": 0}, "latency_s": 0.0, "attempts": 1, "model": "scripted"}
