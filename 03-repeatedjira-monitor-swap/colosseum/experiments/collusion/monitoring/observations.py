"""Explicit observability policies for offline monitors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .access import EvidenceAccessPolicy, INITIAL_PUBLIC_OBSERVER
from .ingest import Event, LoadedRun

Layer = Literal["O0", "O1", "O2"]


@dataclass(frozen=True)
class Observation:
    run_id: str
    layer: Layer
    run_status: str
    outcome: dict[str, Any]
    events: tuple[dict[str, Any], ...]
    issues: tuple[str, ...]
    chronology: str = "source_local_only"


def _event_dict(event: Event) -> dict[str, Any]:
    return {"ref": event.ref, "source": event.source, "source_index": event.source_index, "timestamp": event.timestamp, "kind": event.kind, "agent": event.agent, "channel_id": event.channel_id, "payload": event.payload}


def _public_event(event: Event, policy: EvidenceAccessPolicy) -> dict[str, Any] | None:
    if event.source == "blackboards" and policy.can_observe_channel(event.channel_id):
        # Context and communications are what an authorized participant can see.
        if event.kind in {"communication", "context"} or (event.kind == "action_executed" and policy.allow_public_board_actions):
            return _event_dict(event)
    return None


def _tool_event(event: Event, policy: EvidenceAccessPolicy) -> dict[str, Any] | None:
    if event.source != "tool_events" or not policy.allow_audit_tool_events or event.visibility == "private":
        return None
    # A channel-less Jira assign_task event is auditable; a private message is not.
    if event.kind == "post_message" and not policy.can_observe_channel(event.channel_id):
        return None
    return _event_dict(event)


def make_observation(run: LoadedRun, layer: Layer, policy: EvidenceAccessPolicy = INITIAL_PUBLIC_OBSERVER) -> Observation:
    """Project a loaded run into the exact evidence admissible to a monitor."""
    if layer not in {"O0", "O1", "O2"}:
        raise ValueError(f"unknown observation layer: {layer}")
    events: list[dict[str, Any]] = []
    if layer in {"O1", "O2"}:
        events.extend(item for event in run.events if (item := _public_event(event, policy)) is not None)
    if layer == "O2":
        events.extend(item for event in run.events if (item := _tool_event(event, policy)) is not None)
    # Event refs retain each artifact's ordering. Sorting by source would alter it.
    return Observation(
        run_id=run.run_id, layer=layer, run_status=run.status, outcome=dict(run.outcome),
        events=tuple(events), issues=tuple(issue.code for issue in run.issues),
    )
