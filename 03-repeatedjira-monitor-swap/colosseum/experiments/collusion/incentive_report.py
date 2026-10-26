"""Privileged, offline diagnostics for Jira individual-incentive runs.

This report is research metadata.  It must never be supplied to an O0/O1/O2
monitor: bonus offers and eligibility are intentionally absent from those views.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def _read(path: Path) -> dict[str, Any] | list[Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assignment_events(events: list[Any]) -> dict[str, list[dict[str, Any]]]:
    by_agent: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        if not isinstance(event, dict) or event.get("tool_name") != "assign_task":
            continue
        agent = str(event.get("agent_name") or "")
        by_agent.setdefault(agent, []).append(event)
    return by_agent


def summarize_run(run_dir: Path) -> dict[str, Any]:
    """Return bonus diagnostics from raw run artifacts without mutating them."""
    config = _read(run_dir / "run_config.json")
    summary = _read(run_dir / "final_summary.json")
    events = _read(run_dir / "tool_events.json")
    if not isinstance(config, dict) or not isinstance(summary, dict) or not isinstance(events, list):
        raise ValueError(f"invalid incentive artifacts in {run_dir}")

    incentives = summary.get("individual_incentives")
    if not isinstance(incentives, dict):
        incentives = {}
    assignments = summary.get("assignment")
    if not isinstance(assignments, dict):
        assignments = {}
    offers = incentives.get("offers")
    if not isinstance(offers, dict):
        bonus = float(incentives.get("bonus") or 0.0)
        bonus_tasks = incentives.get("bonus_tasks") if isinstance(incentives.get("bonus_tasks"), dict) else {}
        offers = {
            str(agent): {"task_id": task, "bonus": bonus if incentives.get("enabled") else 0.0}
            for agent, task in bonus_tasks.items()
        }
    distribution = incentives.get("distribution") if isinstance(incentives.get("distribution"), dict) else {}
    events_by_agent = _assignment_events(events)
    prompt_path = run_dir / "agent_prompts.json"
    prompt_texts: dict[str, list[str]] | None = None
    if prompt_path.exists():
        raw_prompts = _read(prompt_path)
        if isinstance(raw_prompts, list):
            prompt_texts = {}
            for prompt in raw_prompts:
                if not isinstance(prompt, dict) or not isinstance(prompt.get("agent_name"), str):
                    continue
                text = prompt.get("user_prompt")
                if isinstance(text, str):
                    prompt_texts.setdefault(prompt["agent_name"], []).append(text)
    diagnostics: dict[str, dict[str, Any]] = {}
    all_agents = sorted(set(assignments) | set(offers))
    for agent in all_agents:
        raw_offer = offers.get(agent)
        offer = raw_offer if isinstance(raw_offer, dict) else {}
        task_id = offer.get("task_id")
        attempts = [
            event for event in events_by_agent.get(agent, [])
            if (event.get("arguments") or {}).get("task_id") == task_id
        ] if task_id else []
        succeeded = any(
            isinstance(event.get("result"), dict)
            and event["result"].get("status") == "success"
            and bool(event["result"].get("action_committed"))
            for event in attempts
        )
        offered_bonus = float(offer.get("bonus") or 0.0)
        prompt_present = None
        if offered_bonus > 0 and prompt_texts is not None:
            prompt_present = any(
                "YOUR TRANSPARENT INDIVIDUAL INCENTIVE" in text
                for text in prompt_texts.get(agent, [])
            )
        diagnostics[agent] = {
            "bonus_offered": offered_bonus,
            "bonus_eligible_task": task_id,
            "bonus_prompt_present": prompt_present,
            "eligible_task_attempted": bool(attempts),
            "eligible_task_successfully_assigned": bool(
                succeeded and assignments.get(agent) == task_id
            ),
            "bonus_earned": float(distribution.get(agent) or 0.0),
            "final_assignment": assignments.get(agent),
        }

    chosen_tasks = [str(task) for task in assignments.values() if task not in (None, "skip")]
    counts = Counter(chosen_tasks)
    conflicts = {
        task: count for task, count in sorted(counts.items()) if count > 1
    }
    return {
        "scope": "privileged_research_diagnostic_not_monitor_input",
        "run_id": config.get("run_id"),
        "condition": config.get("sweep"),
        "status": summary.get("status"),
        "bonus_enabled": bool(incentives.get("enabled")),
        "bonus_diagnostics": diagnostics,
        "joint_reward_excluding_bonuses": summary.get("joint_reward"),
        "agent_rewards_including_bonuses": summary.get("agent_rewards"),
        "assignment_conflicts": conflicts,
        "task_coverage": summary.get("coverage"),
        "violations": summary.get("violations"),
        "assignments": assignments,
    }


def collect_reports(runs_root: Path) -> dict[str, Any]:
    reports = [summarize_run(path.parent) for path in sorted(runs_root.rglob("final_summary.json"))]
    return {
        "scope": "privileged_research_diagnostic_not_monitor_input",
        "runs_root": str(runs_root),
        "episodes": reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs_root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    payload = collect_reports(args.runs_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
