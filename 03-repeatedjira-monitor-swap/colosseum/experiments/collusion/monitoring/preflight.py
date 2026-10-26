"""Offline preflight validation for a completed Jira run."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .ingest import REQUIRED_COMPLETE, load_run


@dataclass(frozen=True)
class PreflightIssue:
    severity: str  # error, warning, info
    code: str
    detail: str


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def validate_completed_run(run_dir: Path) -> dict[str, Any]:
    """Check trace completeness without drawing a behavioral conclusion."""
    run = load_run(run_dir)
    issues: list[PreflightIssue] = [PreflightIssue("error", issue.code, f"{issue.path}: {issue.detail}") for issue in run.issues]
    manifest_path = run_dir / "channel_visibility_manifest.json"
    manifest = _read(manifest_path)
    if not manifest_path.exists():
        issues.append(PreflightIssue("error", "missing_visibility_manifest", "future research runs require channel_visibility_manifest.json"))
    elif not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        issues.append(PreflightIssue("error", "invalid_visibility_manifest", "manifest must be a schema_version 1 object"))
    else:
        channels = manifest.get("channels")
        if not isinstance(channels, list):
            issues.append(PreflightIssue("error", "invalid_visibility_manifest", "channels must be an array"))
        else:
            board_ids = {event.channel_id for event in run.events if event.source == "blackboards" and event.channel_id is not None}
            manifest_ids = set()
            for channel in channels:
                if not isinstance(channel, dict) or not isinstance(channel.get("channel_id"), str):
                    issues.append(PreflightIssue("error", "invalid_manifest_channel", "each channel requires a string channel_id"))
                    continue
                channel_id = channel["channel_id"]
                if channel_id in manifest_ids:
                    issues.append(PreflightIssue("error", "duplicate_manifest_channel", channel_id))
                manifest_ids.add(channel_id)
                if channel.get("declared_visibility") not in {"public", "private", "unknown"}:
                    issues.append(PreflightIssue("error", "invalid_channel_visibility", channel_id))
                if channel.get("declared_visibility") == "unknown":
                    issues.append(PreflightIssue("warning", "ambiguous_visibility", f"{channel_id} defaults to private"))
            for board_id in sorted(board_ids - manifest_ids):
                issues.append(PreflightIssue("error", "unmanifested_channel", board_id))
    raw_tools = _read(run_dir / "tool_events.json")
    if isinstance(raw_tools, list):
        for index, event in enumerate(raw_tools):
            if not isinstance(event, dict) or not isinstance(event.get("arguments"), dict) or "result" not in event:
                issues.append(PreflightIssue("error", "incomplete_tool_event", f"tool_events[{index}] lacks structured arguments or result"))
            elif event.get("sequence_index") != index:
                issues.append(PreflightIssue("error", "invalid_tool_event_order", f"tool_events[{index}] must preserve sequence_index {index}"))
    if run.status != "complete":
        issues.append(PreflightIssue("warning", "run_incomplete", "This is trace incompleteness, not evidence of benign or suspicious behavior."))
    issues.append(PreflightIssue("info", "chronology_scope", "Blackboard order is local; tool and turn artifacts have no global timestamp."))
    errors = [issue for issue in issues if issue.severity == "error"]
    return {
        "run_id": run.run_id,
        "run_path": str(run_dir),
        "run_status": run.status,
        "monitoring_ready": run.status == "complete" and not errors,
        "behavioral_conclusion": "none",
        "required_artifacts": list(REQUIRED_COMPLETE) + ["channel_visibility_manifest.json"],
        "issues": [asdict(issue) for issue in issues],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a saved Jira run for offline monitoring; no model or network calls.")
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate_completed_run(args.run_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
