"""Safe preparation and validation of Modal-backed collusion configurations."""

from __future__ import annotations

import copy
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yaml

_ENV = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-(.*?))?\}")
_SECRET_KEYS = {"api_key", "token", "authorization", "password", "secret"}


def _expand(value: Any, environ: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: _expand(item, environ) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand(item, environ) for item in value]
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        name, default = match.group(1), match.group(2)
        if name in environ:
            return environ[name]
        if default is not None:
            return default
        raise ValueError(f"Missing required environment variable: {name}")

    return _ENV.sub(replace, value)


def load_prepared_config(path: str | Path, *, environ: dict[str, str] | None = None) -> dict[str, Any]:
    """Load YAML and expand only explicit ``${NAME}`` placeholders."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Experiment configuration must be a YAML mapping.")
    return _expand(raw, dict(os.environ if environ is None else environ))


def redact_secrets(value: Any) -> Any:
    """Return a copy suitable for configuration snapshots and manifests."""
    if isinstance(value, dict):
        return {
            key: ("<redacted>" if key.lower() in _SECRET_KEYS else redact_secrets(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return copy.deepcopy(value)


def remote_vllm_spec(cfg: dict[str, Any]) -> dict[str, Any]:
    models = ((cfg.get("llm_models") or [{}])[0].get("llm") or {}).get("vllm", {}).get("models") or []
    if len(models) != 1:
        raise ValueError("This workflow requires exactly one llm.vllm.models entry.")
    return models[0]


def validate_modal_config(cfg: dict[str, Any]) -> None:
    spec = remote_vllm_spec(cfg)
    vllm = ((cfg.get("llm_models") or [{}])[0].get("llm") or {}).get("vllm", {})
    base_url = str(spec.get("base_url") or "")
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.netloc or not parsed.path.rstrip("/").endswith("/v1"):
        raise ValueError("vLLM models[0].base_url must be an HTTPS URL ending in /v1.")
    if vllm.get("auto_start_server") is not False:
        raise ValueError("Remote Modal configuration must set auto_start_server: false.")
    if not vllm.get("remote_authenticated"):
        raise ValueError("Remote Modal configuration must opt into remote_authenticated: true.")
    if not spec.get("api_key"):
        raise ValueError("Set the endpoint credential through MODAL_VLLM_API_KEY.")
    if not spec.get("served_model_name"):
        raise ValueError("Set served_model_name explicitly to match /v1/models.")
    params = vllm.get("params") or {}
    if "max_tokens" in params:
        raise ValueError("Terrarium vLLM client ignores params.max_tokens; use max_completion_tokens.")
    if params.get("temperature") != 0:
        raise ValueError(
            "Modal research configurations must set params.temperature: 0 for greedy decoding."
        )


def check_endpoint(cfg: dict[str, Any], *, timeout: float = 10.0) -> list[str]:
    """Authenticated, no-inference reachability check against ``/v1/models``."""
    validate_modal_config(cfg)
    spec = remote_vllm_spec(cfg)
    headers = {"Authorization": f"Bearer {spec['api_key']}"}
    response = requests.get(str(spec["base_url"]).rstrip("/") + "/models", headers=headers, timeout=timeout)
    response.raise_for_status()
    return [str(item["id"]) for item in response.json().get("data", []) if item.get("id")]
