"""Shared command-line plumbing: arguments, run folders, config check, clients and the dry-run."""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import replace
from typing import Any, Dict, Iterable, List, Tuple

from signal_ring import state as S
from signal_ring.config import (ARMS, EST_INPUT_BASE, EST_INPUT_PER_ROUND, EST_OUTPUT, FAKE_RUNS_DIR,
                                MODEL_SETS, MONITOR, OBSERVERS, PRICES, RING, Arm, ModelSet, RoundPlan,
                                run_config)
from signal_ring.engine import Ctx, seat_model
from signal_ring.state import GameState


def add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--model-set", default="haiku", choices=sorted(MODEL_SETS))
    p.add_argument("--arm", default="naive", choices=sorted(ARMS))
    p.add_argument("--tag", default=None, help="suffix for a new run folder (a new design needs one)")
    p.add_argument("--monitor-window", type=int, default=None,
                   help="earlier rounds the monitor sees (calibration knob; default all)")
    p.add_argument("--private-reveal", action="store_true",
                   help="show picks and targets to the ring only (calibration knob)")
    p.add_argument("--fake", action="store_true", help="offline fake client, writes to runs_fake/")
    p.add_argument("--dry-run", action="store_true", help="print calls and estimated cost, then stop")
    p.add_argument("--max-spend", type=float, default=None, help="USD cap for this command")
    p.add_argument("--max-openrouter-usage", type=float, default=None,
                   help="stop when the OpenRouter account's all-time usage reaches this (USD)")


def run_name(args: argparse.Namespace) -> str:
    name = f"{args.model_set}__{args.arm}"
    return f"{name}__{args.tag}" if args.tag else name


def arm_from(args: argparse.Namespace) -> Arm:
    arm = ARMS[args.arm]
    if args.monitor_window is not None:
        arm = replace(arm, monitor_window=args.monitor_window)
    if args.private_reveal:
        arm = replace(arm, public_reveal=False)
    return arm


def setup(args: argparse.Namespace) -> Tuple[str, Dict[str, Any], RoundPlan, Arm, ModelSet]:
    """Point at the run folder and return (run, config, plan, arm, models).

    The first trunk or calibration run of a folder writes run_config.json; every later
    command must match it.
    """
    if args.fake:
        S.set_runs_root(FAKE_RUNS_DIR)
    run = run_name(args)
    models, plan, arm = MODEL_SETS[args.model_set], RoundPlan(), arm_from(args)
    config = run_config(models, plan, arm)
    path = S.run_config_path(run)
    if path.exists():
        S.check_config(S.load_json(path), config, str(path))
    return run, config, plan, arm, models


def open_run(args: argparse.Namespace) -> Tuple[str, Dict[str, Any]]:
    """For read-only steps (analysis, judge, ceiling, transcripts): the run and its saved config.

    Unlike setup(), this doesn't require the current code to match, so analysis code can
    change after the games were played.
    """
    if args.fake:
        S.set_runs_root(FAKE_RUNS_DIR)
    run = run_name(args)
    path = S.run_config_path(run)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found: run run_trunk first")
    return run, S.load_json(path)


def write_config(run: str, config: Dict[str, Any]) -> None:
    path = S.run_config_path(run)
    if not path.exists():
        S.save_json(path, config)


def make_clients(args: argparse.Namespace, run: str, plan: RoundPlan) -> Any:
    if args.fake:
        from signal_ring.fake import FakeClient
        return FakeClient(plan)
    from signal_ring.clients import Clients
    return Clients(S.transcript_dir(run), args.max_spend, args.max_openrouter_usage)


# ---------------------------------------------------------------------------
# Dry-run estimate
# ---------------------------------------------------------------------------
def calls_for_round(game: GameState, r: int, ctx: Ctx) -> List[str]:
    """Models of the calls a round makes (re-key exchanges and re-asks not counted)."""
    plan = ctx.plan
    m = {s: seat_model(game, s, r, ctx) for s in list(RING) + [MONITOR]}
    if r <= plan.setup_rounds:
        calls = [m[s] for s in RING]
        return calls + ([m[s] for s in RING] if r == plan.setup_rounds else [])
    calls = [m[s] for s in RING]                       # talk
    calls += [m[s] for s in RING][1:]                  # two receivers (whoever sends; same models)
    calls += [m[MONITOR]]                              # monitor
    calls += [m[s] for s in RING]                      # reflections
    if plan.is_probe_round(r):
        calls += [m[s] for s in OBSERVERS] + [m[MONITOR]]
    return calls


def estimate(games: Iterable[GameState], until: int, ctx: Ctx) -> Dict[str, List[float]]:
    """{model: [calls, input tokens, output tokens]} to play `games` up to round `until`."""
    out: Dict[str, List[float]] = defaultdict(lambda: [0, 0, 0])
    for g in games:
        for r in range(g.next_round, until + 1):
            for model in calls_for_round(g, r, ctx):
                row = out[model]
                row[0] += 1
                row[1] += EST_INPUT_BASE + EST_INPUT_PER_ROUND * (r - 1)
                row[2] += EST_OUTPUT
    return out


def print_estimate(est: Dict[str, List[float]]) -> float:
    total = 0.0
    print(f"{'model':34} {'calls':>7} {'input tok':>11} {'output tok':>11} {'USD':>8}")
    for model, (n, tin, tout) in sorted(est.items()):
        pin, pout = PRICES.get(model, (0.0, 0.0))
        usd = (tin * pin + tout * pout) / 1e6
        total += usd
        print(f"{model:34} {n:7.0f} {tin:11.0f} {tout:11.0f} {usd:8.2f}")
    print(f"{'total':34} {sum(v[0] for v in est.values()):7.0f} {'':11} {'':11} {total:8.2f}")
    print("(No prompt caching and no re-asks counted; Anthropic caching lowers the real figure.)")
    return total
