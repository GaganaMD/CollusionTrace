"""Research-evidence manifests for completed Jira runs.

The manifest is privileged research metadata. It describes access boundaries but
is deliberately not read by the monitor-observation projection.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def build_channel_visibility_manifest(
    *, run_id: str, blackboards: list[Any], declared_observers: dict[str, list[str]] | None = None
) -> dict[str, Any]:
    """Describe runtime boards from their actual templates, never their IDs.

    An absent/invalid template is ambiguous. Its effective visibility is private
    until an explicit study policy authorizes monitor access.
    """
    declared_observers = declared_observers or {}
    channels: list[dict[str, Any]] = []
    for board in blackboards:
        channel_id = str(getattr(board, "blackboard_id", ""))
        template = getattr(board, "template", None)
        template = template if isinstance(template, dict) else {}
        raw_visibility = str(template.get("visibility") or "").strip().lower()
        secret = bool(template.get("secret_channel"))
        if secret:
            declared_visibility, effective_visibility, source = "private", "private", "runtime_template.secret_channel"
        elif raw_visibility in {"public", "private"}:
            declared_visibility, effective_visibility, source = raw_visibility, raw_visibility, "runtime_template.visibility"
        else:
            declared_visibility, effective_visibility, source = "unknown", "private", "runtime_template.absent_or_unsupported"
        observers = declared_observers.get(channel_id, [])
        channels.append({
            "channel_id": channel_id,
            "participants": sorted(str(agent) for agent in getattr(board, "agents", set())),
            "declared_visibility": declared_visibility,
            "effective_visibility": effective_visibility,
            "secret_channel": secret,
            "authorized_observers": sorted(str(observer) for observer in observers),
            "authorized_observer_source": "experiment.monitoring.authorized_observers" if channel_id in declared_observers else "no_explicit_observer_authorization",
            "visibility_source": source,
            "ambiguous_visibility": declared_visibility == "unknown",
        })
    return {
        "schema_version": 1,
        "run_id": run_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": "privileged_research_metadata_not_monitor_input",
        "default_for_unknown_visibility": "private",
        "channels": channels,
    }
