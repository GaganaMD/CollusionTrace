"""Branch every kept trunk into the swap conditions and play rounds 10-20.

    python -m signal_ring.run_branch [--conditions sham warm infiltrator] [--limit N] [--dry-run]
    python -m signal_ring.run_branch --conditions cold --limit 15
    python -m signal_ring.run_branch --rerun-failed
    python -m signal_ring.run_branch --conditions warm infiltrator --newcomer openai/gpt-6-luna --label luna

--newcomer plays seat Q with another model than the run's model set; the branches go to
branches/<condition>-<label>/ and are reported under that name, next to the run's own sham.

Every branch of a trial starts from an identical copy of its trunk (same history, same
targets), so conditions are compared within trial.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from typing import List, Optional

from signal_ring import state as S
from signal_ring.cli import add_common_args, estimate, make_clients, print_estimate, setup
from signal_ring.config import CONDITIONS, DEFAULT_CONDITIONS
from signal_ring.engine import Ctx, run_games
from signal_ring.state import GameState


def load_or_branch(run: str, condition: str, trial_id: int, rerun_failed: bool,
                   label: Optional[str] = None, newcomer: Optional[str] = None) -> GameState:
    folder = f"{condition}-{label}" if label else condition
    path = S.branch_path(run, folder, trial_id)
    if path.exists():
        g = S.load_state(path)
        if g.newcomer != newcomer:
            raise S.ConfigMismatch(f"{path} was played with newcomer {g.newcomer}, not {newcomer}")
        if g.status != "failed" or not rerun_failed:
            return g
        history = g.history + [{"failure": g.failure, "reasks": g.reasks}]
    else:
        history = []
    trunk = S.load_state(S.trunk_path(run, trial_id))
    g = trunk.branch_from(condition)
    g.key, g.newcomer = f"{folder}.t{trial_id}", newcomer
    g.history = history
    return g


def main(argv: List[str] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(p)
    p.add_argument("--conditions", nargs="+", default=list(DEFAULT_CONDITIONS), choices=sorted(CONDITIONS))
    p.add_argument("--limit", type=int, default=None, help="only the first N kept trials")
    p.add_argument("--trials", type=int, nargs="+", default=None, help="only these kept trials")
    p.add_argument("--rerun-failed", action="store_true")
    p.add_argument("--newcomer", default=None, help="play seat Q with this model instead of the model set's")
    p.add_argument("--label", default=None, help="folder suffix for --newcomer branches (required with it)")
    args = p.parse_args(argv)

    if bool(args.newcomer) != bool(args.label):
        p.error("--newcomer and --label go together")
    run, config, plan, arm, models = setup(args)
    if args.newcomer:
        models = replace(models, newcomer=args.newcomer)
    kept = S.kept_trials(run)
    if args.trials:
        bad = sorted(set(args.trials) - set(kept))
        if bad:
            p.error(f"trials {bad} were not kept by selection")
        kept = [t for t in kept if t in args.trials]
    if args.limit is not None:
        kept = kept[:args.limit]
    games = [load_or_branch(run, c, t, args.rerun_failed, args.label, args.newcomer)
             for c in args.conditions for t in kept]
    for g in games:
        S.check_config(g.config, config, g.key)
    todo = [g for g in games if g.status == "running"]
    ctx = Ctx(plan, arm, models, clients=None)
    print(f"{run}: {len(todo)} branches to play ({len(games) - len(todo)} already done or failed), "
          f"conditions {args.conditions}, trials {kept}")
    if args.dry_run:
        print_estimate(estimate(todo, plan.total_rounds, ctx))
        return 0

    ctx.clients = make_clients(args, run, plan)
    from signal_ring.clients import SpendCapReached
    try:
        run_games(todo, plan.total_rounds, ctx,
                  lambda g: S.save_state(S.branch_path(run, g.folder, g.trial_id), g))
    except SpendCapReached as err:
        print(f"STOPPED: {err}. Rerun the same command to resume.")
        return 2
    failed = [g.key for g in todo if g.status == "failed"]
    print(f"done. failed: {failed or 'none'}. spent this command: ${getattr(ctx.clients, 'spent', 0.0):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
