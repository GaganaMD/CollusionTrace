"""Read Colosseum Jira artifacts without mutating them.

The runner writes its artifacts independently rather than as one transaction.
Accordingly, this loader reports incomplete or malformed evidence as issues;
it never turns absent evidence into an assertion about agent behaviour.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REQUIRED_COMPLETE = (
    "run_config.json",
    "final_summary.json",
    "agent_turns.json",
    "tool_events.json",
    "blackboards.json",
)
OUTCOME_FIELDS = (
    "status", "joint_reward", "joint_reward_ratio", "tasks_done", "priority_sum",
    "total_cost", "violations", "coverage", "cost_gap", "normalized_score",
    "tasks_available", "total_agents", "random_fallback_fills", "notes",
    "decisions_made",
)


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    detail: str


@dataclass(frozen=True)
class Event:
    """A source-preserving event; cross-artifact chronology may be unavailable."""

    ref: str
    source: str
    source_index: int
    kind: str
    agent: str | None
    channel_id: str | None
    visibility: str  # public, private, or unknown
    timestamp: float | None
    payload: dict[str, Any]


@dataclass
class LoadedRun:
    path: Path
    run_id: str
    status: str  # complete, incomplete, malformed
    outcome: dict[str, Any]
    events: list[Event]
    issues: list[Issue] = field(default_factory=list)
    # This is restricted metadata, intentionally not copied into observations.
    restricted: dict[str, Any] = field(default_factory=dict, repr=False)


def _read_json(path: Path, issues: list[Issue]) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        issues.append(Issue("missing_file", path.name, "artifact was not written"))
    except json.JSONDecodeError as exc:
        issues.append(Issue("invalid_json", path.name, str(exc)))
    except OSError as exc:
        issues.append(Issue("unreadable_file", path.name, str(exc)))
    return None


def _dict(value: Any, name: str, issues: list[Issue]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    issues.append(Issue("invalid_shape", name, "expected JSON object"))
    return {}


def _list(value: Any, name: str, issues: list[Issue]) -> list[Any]:
    if isinstance(value, list):
        return value
    issues.append(Issue("invalid_shape", name, "expected JSON array"))
    return []


def _timestamp(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def _require_fields(value: dict[str, Any], fields: tuple[str, ...], name: str, issues: list[Issue]) -> None:
    for required_name in fields:
        if required_name not in value:
            issues.append(Issue("missing_field", name, f"required field {required_name!r} is absent"))


def load_run(run_dir: str | Path) -> LoadedRun:
    """Load one saved run and retain source-local event order.

    Blackboard entries have timestamps; tool events and agent turns do not.  We
    therefore do not claim a fabricated global ordering across those artifacts.
    """
    path = Path(run_dir)
    issues: list[Issue] = []
    raw = {name: _read_json(path / name, issues) for name in REQUIRED_COMPLETE}
    config = _dict(raw["run_config.json"], "run_config.json", issues)
    summary = _dict(raw["final_summary.json"], "final_summary.json", issues)
    turns = _list(raw["agent_turns.json"], "agent_turns.json", issues)
    tools = _list(raw["tool_events.json"], "tool_events.json", issues)
    boards = _list(raw["blackboards.json"], "blackboards.json", issues)
    _require_fields(config, ("run_id",), "run_config.json", issues)
    _require_fields(summary, ("status",), "final_summary.json", issues)

    run_id = str(config.get("run_id") or path.name)
    secret_id = config.get("secret_blackboard_id")
    secret_key = str(secret_id) if secret_id is not None else None
    events: list[Event] = []

    for board_index, board in enumerate(boards):
        if not isinstance(board, dict):
            issues.append(Issue("invalid_event", "blackboards.json", f"board {board_index} is not an object"))
            continue
        _require_fields(board, ("blackboard_id", "participants", "events"), "blackboards.json", issues)
        channel = str(board.get("blackboard_id")) if board.get("blackboard_id") is not None else None
        visibility = "private" if channel is not None and channel == secret_key else "unknown"
        # A non-secret board is an ordinary shared channel in this runner.  If
        # run_config is absent, conservatively leave its visibility unknown.
        if channel is not None and secret_key is not None and visibility != "private":
            visibility = "public"
        for event_index, raw_event in enumerate(_list(board.get("events"), "blackboards.events", issues)):
            if not isinstance(raw_event, dict):
                issues.append(Issue("invalid_event", "blackboards.json", f"event {board_index}:{event_index} is not an object"))
                continue
            _require_fields(raw_event, ("id", "ts", "agent", "kind", "payload"), "blackboards.json", issues)
            payload = raw_event.get("payload")
            if not isinstance(payload, dict):
                payload = {"raw_payload": payload}
            event_channel = raw_event.get("blackboard_id", channel)
            event_channel = str(event_channel) if event_channel is not None else channel
            event_visibility = "private" if event_channel == secret_key and secret_key is not None else visibility
            events.append(Event(
                ref=f"blackboards:{channel}:{event_index}", source="blackboards", source_index=event_index,
                kind=str(raw_event.get("kind") or "unknown"), agent=(str(raw_event["agent"]) if raw_event.get("agent") is not None else None),
                channel_id=event_channel, visibility=event_visibility, timestamp=_timestamp(raw_event.get("ts")), payload=payload,
            ))

    for index, raw_event in enumerate(tools):
        if not isinstance(raw_event, dict):
            issues.append(Issue("invalid_event", "tool_events.json", f"event {index} is not an object"))
            continue
        _require_fields(raw_event, ("tool_name", "agent_name", "arguments", "result"), "tool_events.json", issues)
        arguments = raw_event.get("arguments") if isinstance(raw_event.get("arguments"), dict) else {}
        channel = arguments.get("blackboard_id")
        channel = str(channel) if channel is not None else None
        visibility = "private" if channel == secret_key and secret_key is not None else "unknown"
        events.append(Event(
            ref=f"tool_events:{index}", source="tool_events", source_index=index,
            kind=str(raw_event.get("tool_name") or "unknown"), agent=(str(raw_event["agent_name"]) if raw_event.get("agent_name") is not None else None),
            channel_id=channel, visibility=visibility, timestamp=None,
            payload={"arguments": arguments, "result": raw_event.get("result"), "phase": raw_event.get("phase"), "iteration": raw_event.get("iteration"), "planning_round": raw_event.get("planning_round")},
        ))

    # Turns are retained only as provenance for auditing completeness.  Their
    # response and role are not placed in observation payloads.
    for index, turn in enumerate(turns):
        if not isinstance(turn, dict):
            issues.append(Issue("invalid_event", "agent_turns.json", f"turn {index} is not an object"))
            continue
        _require_fields(turn, ("phase", "agent"), "agent_turns.json", issues)
        events.append(Event(
            ref=f"agent_turns:{index}", source="agent_turns", source_index=index,
            kind="agent_turn", agent=(str(turn["agent"]) if turn.get("agent") is not None else None),
            channel_id=None, visibility="unknown", timestamp=None,
            payload={"phase": turn.get("phase"), "planning_round": turn.get("planning_round"), "has_response": "response" in turn, "has_tools": bool(turn.get("tools_executed"))},
        ))

    outcome = {field: summary[field] for field in OUTCOME_FIELDS if field in summary}
    if not summary:
        status = "malformed" if any(i.code == "invalid_json" for i in issues) else "incomplete"
    elif summary.get("status") != "complete" or any(i.code == "missing_file" for i in issues):
        status = "incomplete"
    else:
        status = "complete"
    restricted = {key: config.get(key) for key in ("colluders", "roles", "secret_blackboard_id", "secret_channel_enabled", "seed", "environment_cfg") if key in config}
    return LoadedRun(path, run_id, status, outcome, events, issues, restricted)
