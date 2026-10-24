"""Human-readable, offline-only report for one completed Jira smoke run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .ingest import load_run
from .observations import make_observation
from .preflight import validate_completed_run
from .rules import evaluate_monitor


def report(run_dir: Path) -> dict[str, Any]:
    run = load_run(run_dir)
    tools = [event for event in run.events if event.source == "tool_events"]
    assignments = [
        {"sequence_index": event.source_index, "agent": event.agent,
         "task_id": (event.payload.get("arguments") or {}).get("task_id"),
         "result": event.payload.get("result")}
        for event in tools if event.kind == "assign_task"
    ]
    boards = [event.ref for event in run.events if event.source == "blackboards"]
    return {"run_id": run.run_id, "run_status": run.status, "outcome": run.outcome,
            "assign_task_calls": assignments, "tool_event_count": len(tools),
            "blackboard_event_refs": boards, "preflight": validate_completed_run(run_dir),
            "monitor": {layer: evaluate_monitor(make_observation(run, layer)).to_dict() for layer in ("O0", "O2")},
            "interpretation": "Monitor signals are not labels or proof of collusion."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = report(args.run_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
