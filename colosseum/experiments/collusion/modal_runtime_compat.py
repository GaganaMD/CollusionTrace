"""Compatibility for authenticated, remote vLLM endpoints.

Terrarium 0.2.1 correctly puts the configured API key on chat-completion
requests, but its vLLM server-manager probes ``/v1/models`` without headers.
That makes an otherwise correctly protected remote vLLM server look offline.

This module deliberately patches only the in-process Terrarium class and only
when a configuration explicitly opts in via ``remote_authenticated: true``.
It does not edit the installed Terrarium package.
"""

from __future__ import annotations

from typing import Any


def enable_authenticated_remote_vllm_preflight() -> None:
    """Add bearer authentication to Terrarium's remote-server preflight once."""
    from terrarium.llm.vllm.runtime import VLLMServerManager

    if getattr(VLLMServerManager, "_collusiontrace_auth_patch", False):
        return

    def ensure_server(self: Any, spec: Any) -> None:
        # Remote only: never launch a local process.  This is intentionally a
        # strict reachability + model-identity check before spending inference.
        if self.config.auto_start_server:
            raise ValueError(
                "remote_authenticated vLLM requires auto_start_server: false."
            )
        import requests

        api_key = spec.api_key or self.config.api_key or "EMPTY"
        headers = {"Authorization": f"Bearer {api_key}"}
        health_url = self._health_url(spec, self.config)
        try:
            health = requests.get(health_url, headers=headers, timeout=5.0)
            health.raise_for_status()
            models = requests.get(
                spec.api_base().rstrip("/") + "/models",
                headers=headers,
                timeout=5.0,
            )
            models.raise_for_status()
            payload = models.json()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Authenticated remote vLLM endpoint is unreachable at {health_url}."
            ) from exc

        available = [
            str(entry.get("id"))
            for entry in (payload.get("data") or [])
            if isinstance(entry, dict) and entry.get("id")
        ]
        expected = spec.served_name()
        if expected not in available:
            raise RuntimeError(
                "Authenticated remote vLLM endpoint does not expose the expected "
                f"model. Expected: {expected}; available: {available or 'unknown'}"
            )

    VLLMServerManager.ensure_server = ensure_server
    VLLMServerManager._collusiontrace_auth_patch = True
