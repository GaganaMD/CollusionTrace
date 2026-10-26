"""Requests, JSON parsing and re-asks.

An unparsed reply is re-sent up to MAX_REASKS times before anyone else could see it. A
game whose request still fails is stopped (status 'failed'), so a model-specific
failure never becomes a cue for the other players.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from signal_ring.config import MAX_REASKS, MAX_TOKENS, REASONING_MAX_TOKENS, TEMPERATURE
from signal_ring.state import GameState

Parser = Callable[[Optional[str]], Optional[Dict[str, Any]]]


@dataclass
class Job:
    """One request plus how to parse its reply."""
    game: Optional[GameState]    # None for jobs outside a game (judge, ceiling)
    who: str
    request: Dict[str, Any]
    parse: Parser


def request_id(r: int, game: GameState, stage: str, who: str) -> str:
    """Unique id: r{round}.{game key}.{stage}.{who}, e.g. 'r12.warm.t3.talk.Q'."""
    return f"r{r}.{game.key}.{stage}.{who}"


def make_request(cid: str, model: str, system: str, user: str) -> Dict[str, Any]:
    return {"custom_id": cid, "model": model, "system": system, "user": user,
            "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
            "reasoning_max_tokens": REASONING_MAX_TOKENS}


_FENCE = re.compile(r"```(?:json)?", re.IGNORECASE)


def parse_json(content: Optional[str]) -> Optional[Dict[str, Any]]:
    """The first JSON object in a reply (code fences and surrounding prose are ignored)."""
    if not content:
        return None
    text = _FENCE.sub("", content)
    decoder = json.JSONDecoder()
    start = text.find("{")
    while start != -1:
        try:
            obj, _ = decoder.raw_decode(text, start)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
        start = text.find("{", start + 1)
    return None


def run_jobs(jobs: List[Job], clients: Any, label: str,
             reask_log: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
    """Send jobs, re-asking unparsed ones; return {request id: parsed answer} for those that parsed."""
    pending = {j.request["custom_id"]: j for j in jobs}
    assert len(pending) == len(jobs), f"{label}: duplicate request ids in one batch"
    parsed: Dict[str, Dict[str, Any]] = {}
    for attempt in range(MAX_REASKS + 1):
        replies = clients.execute([j.request for j in pending.values()], label)
        for cid in list(pending):
            reply = replies.get(cid, {})
            answer = pending[cid].parse(reply.get("content"))
            if answer is not None:
                parsed[cid] = answer
                del pending[cid]
            elif attempt < MAX_REASKS:
                entry = {"request": cid, "attempt": attempt + 1,
                         "reply": str(reply.get("content") or reply.get("error"))[:300]}
                game = pending[cid].game
                (game.reasks if game is not None else (reask_log if reask_log is not None else [])).append(entry)
        if not pending:
            break
    return parsed


def fail_games(active: Dict[str, GameState], jobs: List[Job], parsed: Dict[str, Any],
               stage: str, r: int) -> None:
    """Stop every game with a job that never parsed, and drop it from `active`."""
    for job in jobs:
        key = job.game.key
        if job.request["custom_id"] not in parsed and key in active:
            job.game.status = "failed"
            job.game.failure = {"round": r, "stage": stage, "who": job.who,
                                "request": job.request["custom_id"]}
            del active[key]
