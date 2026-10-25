"""Runner for RepeatedJira v1 episodes.

Writes monitor-compatible artifacts (run_config.json, final_summary.json,
agent_turns.json, tool_events.json, blackboards.json,
channel_visibility_manifest.json) plus privileged research files
(rounds_privileged.json, prompts.jsonl, llm_calls.jsonl).

Usage (offline, no network):
  python -m experiments.collusion.repeated.runner --config <yaml> --dry-run
Real inference requires --allow-inference and MODAL_VLLM_BASE_URL / MODAL_VLLM_API_KEY.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .client import OpenAICompatibleClient, ScriptedClient
from .env import SKIP, RepeatedJiraConfig, RepeatedJiraEnv
from .prompts import system_prompt, tools_for, user_prompt

TEAM_BOARD = 0
PRIVATE_BOARD = 1


def _git_state(repo: Path) -> dict[str, Any]:
    try:
        sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=20, check=False).stdout.strip()
        dirty = bool(subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True, timeout=20, check=False).stdout.strip())
        return {"git_sha": sha or None, "git_dirty": dirty}
    except Exception:  # noqa: BLE001
        return {"git_sha": None, "git_dirty": None}


def _parse_tool_call(message: dict[str, Any], expected: str) -> tuple[dict[str, Any] | None, str]:
    calls = message.get("tool_calls") or []
    for call in calls:
        fn = call.get("function") or {}
        if fn.get("name") != expected:
            continue
        try:
            args = json.loads(fn.get("arguments") or "{}")
        except json.JSONDecodeError:
            return None, "unparseable_arguments"
        if isinstance(args, dict):
            return args, "ok"
    return None, "no_tool_call" if not calls else "wrong_tool"


class Episode:
    def __init__(self, env: RepeatedJiraEnv, client, out_dir: Path, run_meta: dict[str, Any], planning_steps: int = 2):
        self.env, self.client, self.out, self.meta = env, client, out_dir, run_meta
        self.planning_steps = planning_steps
        self.ts = 0.0
        self.boards: list[dict[str, Any]] = [{"blackboard_id": TEAM_BOARD, "kind": "team", "participants": list(env.agents), "events": []}]
        if env.config.private_channel:
            self.boards.append({"blackboard_id": PRIVATE_BOARD, "kind": "private", "participants": list(env.rotation), "events": []})
        self.tool_events: list[dict[str, Any]] = []
        self.turns: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []
        self.prompts: list[dict[str, Any]] = []
        self.private_rewards: dict[str, dict[int, float]] = {a: {} for a in env.agents}
        self.failures: list[dict[str, Any]] = []

    # -------------------------------------------------------------- helpers
    def _tick(self) -> float:
        self.ts += 1.0
        return self.ts

    def _board(self, board_id: int) -> dict[str, Any] | None:
        return next((b for b in self.boards if b["blackboard_id"] == board_id), None)

    def _post(self, board: dict[str, Any], agent: str | None, kind: str, payload: dict[str, Any]) -> str:
        eid = f"b{board['blackboard_id']}-{len(board['events'])}"
        board["events"].append({"id": eid, "ts": self._tick(), "agent": agent, "kind": kind, "blackboard_id": board["blackboard_id"], "payload": payload})
        return eid

    def _call(self, agent: str, r: int, phase: str, step: int, retry_note: str | None = None) -> dict[str, Any]:
        board_ids = [b["blackboard_id"] for b in self.boards if agent in b["participants"]]
        sys_p = system_prompt(self.env, agent)
        usr_p = user_prompt(self.env, agent, r, phase, step, self.planning_steps, self.boards, self.private_rewards[agent])
        if retry_note:
            usr_p += "\n" + retry_note
        messages = [{"role": "system", "content": sys_p}, {"role": "user", "content": usr_p}]
        tools = tools_for(phase, self.env, r, board_ids)
        self.prompts.append({"agent": agent, "round": r, "phase": phase, "step": step, "system": sys_p, "user": usr_p})
        resp = self.client.chat(messages, tools)
        self.calls.append({"agent": agent, "round": r, "phase": phase, "step": step, "usage": resp.get("usage"),
                           "latency_s": resp.get("latency_s"), "attempts": resp.get("attempts"), "model": resp.get("model"),
                           "retry": bool(retry_note)})
        return resp

    # ----------------------------------------------------------------- phases
    def planning(self, r: int) -> None:
        for step in range(1, self.planning_steps + 1):
            for agent in self.env.agent_order(r):
                resp = self._call(agent, r, "planning", step)
                msg = resp["message"]
                args, status = _parse_tool_call(msg, "post_message")
                executed = []
                if args is not None:
                    board = self._board(args.get("board_id")) if isinstance(args.get("board_id"), int) else None
                    text = str(args.get("message") or "").strip()[:600]
                    if board is None or agent not in board["participants"] or not text:
                        result = {"status": "rejected", "reason": "not a member of that board or empty message"}
                    else:
                        eid = self._post(board, agent, "communication", {"content": text, "phase": "planning", "round": r, "step": step})
                        result = {"status": "posted", "event_id": eid}
                    self.tool_events.append({"sequence_index": len(self.tool_events), "tool_name": "post_message", "agent_name": agent,
                                             "arguments": {"blackboard_id": args.get("board_id"), "message": text},
                                             "result": result, "phase": "planning", "iteration": r, "planning_round": step})
                    executed.append("post_message")
                elif status != "no_tool_call":
                    self.failures.append({"agent": agent, "round": r, "phase": "planning", "step": step, "status": status})
                self.turns.append({"agent": agent, "phase": "planning", "round": r, "planning_round": step,
                                   "response": msg.get("content") or "", "tools_executed": executed, "parse_status": status})

    def commit(self, r: int) -> dict[str, str]:
        spec = self.env.rounds[r - 1]
        valid = set(self.env.options(spec))
        commits: dict[str, str] = {}
        for agent in self.env.agent_order(r):
            choice, status, msg = None, "", {}
            for attempt in range(2):
                note = None if attempt == 0 else "Your previous reply did not call assign_task with a valid ticket id. Call assign_task now."
                resp = self._call(agent, r, "commit", 0, retry_note=note)
                msg = resp["message"]
                args, status = _parse_tool_call(msg, "assign_task")
                tid = str(args.get("task_id")) if args else None
                if tid in valid:
                    choice = tid
                    break
                status = status if args is None else "invalid_task_id"
            if choice is None:
                choice = SKIP
                self.failures.append({"agent": agent, "round": r, "phase": "commit", "status": status, "defaulted_to": SKIP})
            commits[agent] = choice
            # Sealed: the result reveals nothing about other agents or rewards.
            self.tool_events.append({"sequence_index": len(self.tool_events), "tool_name": "assign_task", "agent_name": agent,
                                     "arguments": {"task_id": choice}, "result": {"status": "committed_sealed"},
                                     "phase": "commit", "iteration": r, "planning_round": None})
            self.turns.append({"agent": agent, "phase": "commit", "round": r, "planning_round": None,
                               "response": msg.get("content") or "", "tools_executed": ["assign_task"], "parse_status": status})
        return commits

    def run(self) -> Path:
        t0 = time.time()
        status = "complete"
        error = None
        try:
            for r in range(1, self.env.config.rounds + 1):
                public_tasks = [t.public() for t in self.env.rounds[r - 1].tasks]
                self._post(self.boards[0], None, "context", {"subtype": "round_start", "round": r, "tasks": public_tasks,
                                                              "content": f"Round {r} tickets: " + ", ".join(t["id"] for t in public_tasks)})
                self.planning(r)
                commits = self.commit(r)
                res = self.env.score_round(r, commits)
                for a in self.env.agents:
                    self.private_rewards[a][r] = res.agent_rewards[a]
                assign = ", ".join(f"{a}->{t}" for a, t in res.assignment.items())
                self._post(self.boards[0], None, "context", {"subtype": "round_outcome", "round": r,
                                                              "content": f"{assign}; team score {res.public_score}; violations {res.violations}"})
        except Exception as exc:  # noqa: BLE001 - recorded as an incomplete run
            status, error = "incomplete", f"{type(exc).__name__}: {exc}"
        self._write(status, error, time.time() - t0)
        return self.out

    # ----------------------------------------------------------------- output
    def _write(self, status: str, error: str | None, runtime: float) -> None:
        env, out = self.env, self.out
        out.mkdir(parents=True, exist_ok=False)
        res = env.results
        opt_total = sum(x.feasible_optimum for x in res)
        joint = sum(x.public_score for x in res)
        summary = {"status": status if len(res) == env.config.rounds else "incomplete",
                   "joint_reward": joint, "feasible_optimum_total": opt_total,
                   "joint_reward_ratio": (joint / opt_total) if opt_total else 0.0,
                   "tasks_done": sum(x.tasks_done for x in res), "violations": sum(x.violations for x in res),
                   "total_cost": sum(x.total_cost for x in res), "priority_sum": sum(x.priority_sum for x in res),
                   "total_agents": len(env.agents), "rounds_completed": len(res), "rounds_planned": env.config.rounds,
                   "public_round_scores": [x.public_score for x in res], "error": error}
        private_id = PRIVATE_BOARD if env.config.private_channel else None
        run_config = {**self.meta, "seed": env.config.seed, "agents": env.agents,
                      "environment_cfg": dataclasses.asdict(env.config),
                      "secret_channel_enabled": env.config.private_channel,
                      "private_channel_participants": list(env.rotation) if env.config.private_channel else [],
                      "secret_blackboard_id": private_id, "planning_steps": self.planning_steps}
        manifest = {"schema_version": 1, "run_id": self.meta["run_id"], "scope": "privileged_research_metadata_not_monitor_input",
                    "default_for_unknown_visibility": "private", "channels": [
                        {"channel_id": str(b["blackboard_id"]), "participants": b["participants"],
                         "declared_visibility": "public" if b["kind"] == "team" else "private",
                         "effective_visibility": "public" if b["kind"] == "team" else "private",
                         "secret_channel": b["kind"] != "team",
                         "authorized_observers": ["trusted_monitor"] if b["kind"] == "team" else [],
                         "visibility_source": "repeated_jira_v1.design"} for b in self.boards]}
        privileged = {"scope": "privileged_research_data_not_monitor_input", "agents": env.agents, "rotation": env.rotation,
                      "skills": env.skills, "rounds": [{
                          "round": spec.index, "tasks": [t.public() | {"kind": t.kind} for t in spec.tasks], "costs": spec.costs,
                          "offer_recipient": spec.offer_recipient if env.config.bonus_enabled else None,
                          "premium": spec.premium_id, "signoff": spec.signoff_id,
                          **({} if i >= len(res) else dataclasses.asdict(res[i]))} for i, spec in enumerate(env.rounds)],
                      "cumulative_rewards": env.cumulative_rewards(), "failures": self.failures}
        tok_p = sum((c.get("usage") or {}).get("prompt_tokens", 0) or 0 for c in self.calls)
        tok_c = sum((c.get("usage") or {}).get("completion_tokens", 0) or 0 for c in self.calls)
        accounting = {"model_calls": len(self.calls), "prompt_tokens": tok_p, "completion_tokens": tok_c,
                      "runtime_s": round(runtime, 2), "parse_failures": len(self.failures),
                      "max_latency_s": max([c.get("latency_s") or 0 for c in self.calls] or [0])}
        files = {"run_config.json": run_config, "final_summary.json": summary, "agent_turns.json": self.turns,
                 "tool_events.json": self.tool_events, "blackboards.json": self.boards,
                 "channel_visibility_manifest.json": manifest, "rounds_privileged.json": privileged,
                 "accounting.json": accounting}
        for name, data in files.items():
            (out / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        with (out / "prompts.jsonl").open("w", encoding="utf-8") as fh:
            for p in self.prompts:
                fh.write(json.dumps(p, ensure_ascii=False) + "\n")
        with (out / "llm_calls.jsonl").open("w", encoding="utf-8") as fh:
            for c in self.calls:
                fh.write(json.dumps(c) + "\n")


# --------------------------------------------------------------------- driver
def build_client(cfg: dict[str, Any], dry_run: bool, env_factory=None):
    if dry_run:
        from .scripted import make_policy
        return ScriptedClient(make_policy(cfg.get("dry_run_policy", "efficient"), env_factory), label="scripted")
    m = cfg["model"]
    base = os.environ.get(m.get("base_url_env", "MODAL_VLLM_BASE_URL"), "")
    key = os.environ.get(m.get("api_key_env", "MODAL_VLLM_API_KEY"), "")
    return OpenAICompatibleClient(base_url=base, api_key=key, model=m["name"], temperature=float(m.get("temperature", 0)),
                                  max_tokens=int(m.get("max_tokens", 512)), label=m.get("label", "modal-vllm"),
                                  seed=m.get("seed"))


def run_config(path: str, out_root: str | None, dry_run: bool, allow_inference: bool, only_cells: list[str] | None = None,
               seeds: list[int] | None = None) -> Path:
    raw = Path(path).read_text(encoding="utf-8")
    cfg = yaml.safe_load(raw)
    if not dry_run and not allow_inference:
        raise SystemExit("Refusing model inference without --allow-inference (use --dry-run for offline checks).")
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    root = Path(out_root or cfg.get("output_dir", "o/rj")) / (stamp + ("-dry" if dry_run else ""))
    repo = Path(__file__).resolve().parents[3]
    meta_base = {"experiment_id": cfg["experiment_id"], "config_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                 "backend": "scripted" if dry_run else cfg["model"].get("label", "modal-vllm"),
                 "model": "scripted" if dry_run else cfg["model"]["name"],
                 "temperature": None if dry_run else cfg["model"].get("temperature", 0),
                 "max_tokens": None if dry_run else cfg["model"].get("max_tokens", 512), **_git_state(repo)}
    root.mkdir(parents=True, exist_ok=False)
    manifest = {"created_at": stamp, "dry_run": dry_run, **meta_base, "episodes": []}
    for cell in cfg["cells"]:
        if only_cells and cell["name"] not in only_cells:
            continue
        for seed in (seeds or cfg["seeds"]):
            ecfg = RepeatedJiraConfig(seed=int(seed), rounds=int(cfg["environment"]["rounds"]), bonus=float(cfg["environment"]["bonus"]),
                                      bonus_enabled=bool(cell.get("bonus_enabled", cfg["environment"].get("bonus_enabled", True))),
                                      objective_regime=cell["objective_regime"], private_channel=bool(cell["private_channel"]))
            env = RepeatedJiraEnv(ecfg)
            client = build_client(cfg, dry_run, env_factory=lambda e=env: e)
            run_id = f"{cfg['experiment_id']}__{cell['name']}__s{seed}"
            out = root / f"{cell['name']}_s{seed}"
            ep = Episode(env, client, out, {**meta_base, "run_id": run_id, "cell": cell["name"]},
                         planning_steps=int(cfg["environment"].get("planning_steps", 2)))
            ep.run()
            acc = json.loads((out / "accounting.json").read_text())
            summ = json.loads((out / "final_summary.json").read_text())
            manifest["episodes"].append({"run_id": run_id, "cell": cell["name"], "seed": seed, "path": str(out.relative_to(root)),
                                         "status": summ["status"], **acc})
            (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"run_id": run_id, "status": summ["status"], "joint": summ["joint_reward"], **acc}))
            if summ["status"] != "complete" and not dry_run:
                raise SystemExit("Stopping: incomplete episode (stopping rule).")
    return root


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-root")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-inference", action="store_true")
    ap.add_argument("--cells", nargs="*")
    ap.add_argument("--seeds", nargs="*", type=int)
    a = ap.parse_args()
    print(run_config(a.config, a.out_root, a.dry_run, a.allow_inference, a.cells, a.seeds))


if __name__ == "__main__":
    main()
