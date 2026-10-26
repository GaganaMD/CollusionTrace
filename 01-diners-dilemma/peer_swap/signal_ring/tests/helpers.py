"""Shared test helpers: play trunks and branches in memory with the fake client."""
from __future__ import annotations

import io
from contextlib import redirect_stdout
from typing import List, Optional

from signal_ring.config import ARMS, MODEL_SETS, RoundPlan, run_config
from signal_ring.engine import Ctx, run_games
from signal_ring.fake import FakeClient
from signal_ring.state import GameState


def make_ctx(client: Optional[FakeClient] = None, arm: str = "naive") -> Ctx:
    plan = RoundPlan()
    return Ctx(plan, ARMS[arm], MODEL_SETS["haiku"], client or FakeClient(plan))


def trunks(ctx: Ctx, n: int = 1) -> List[GameState]:
    config = run_config(ctx.models, ctx.plan, ctx.arm)
    games = [GameState(key=f"trunk.t{i}", trial_id=i, condition=None, config=config) for i in range(n)]
    with redirect_stdout(io.StringIO()):
        run_games(games, ctx.plan.trunk_rounds, ctx, lambda g: None)
    return games


def branches(ctx: Ctx, trunk_games: List[GameState], conditions: List[str], until: int) -> List[GameState]:
    games = [t.branch_from(c) for c in conditions for t in trunk_games]
    with redirect_stdout(io.StringIO()):
        run_games(games, until, ctx, lambda g: None)
    return games


def requests_for(client: FakeClient, prefix: str) -> List[dict]:
    """Requests whose id starts with prefix, e.g. 'r10.warm.t0.talk.Q' (last attempt per id)."""
    out = {}
    for req in client.requests:
        if req["custom_id"].startswith(prefix):
            out[req["custom_id"]] = req
    return list(out.values())
