"""Branch every kept trunk trial into the swap conditions and play to the last round.

Usage (from /home/vsskl/collusion_peer):
    harness/.venv/bin/python -m experiment.run_branch --model-set option_b --dry-run
    harness/.venv/bin/python -m experiment.run_branch --model-set option_b
    harness/.venv/bin/python -m experiment.run_branch --model-set option_b --conditions control equal
    harness/.venv/bin/python -m experiment.run_branch --model-set option_b --rerun-failed

Complete branches are skipped, interrupted ones resume, and failed ones are kept
unless --rerun-failed restarts them from the trunk. After running, every condition
with complete branches is merged into conditions/<condition>.json (harness format).
"""
from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List

from experiment import cli_common
from experiment.clients import SpendCapReached
from experiment.config import (CONDITIONS, DEFAULT_CONDITIONS, GAME_TYPE, NEW_NAME, SELF_REFERENCE,
                               SWAP_SEAT, ModelSet, RoundPlan)
from experiment.engine import run_branches
from experiment.roster import seat_models
from experiment.state import (BranchState, ConfigMismatch, branch_path, check_config, condition_path,
                              kept_trials, load_branches, load_state, run_config_path, save_json,
                              save_state, trunk_path)
from src.endogenous.analysis.endogenous_analyzer import analyze_all_rounds


def load_trunk(run: str, trial_id: int, run_cfg: Dict[str, Any]) -> BranchState:
    """A complete trunk made with exactly the run-level config."""
    trunk = load_state(trunk_path(run, trial_id))
    if trunk.status != "complete":
        raise RuntimeError(f"trunk trial {trial_id} is {trunk.status}; rerun experiment.run_trunk")
    check_config(trunk.config, run_cfg, f"trunk trial {trial_id}")
    return trunk


def load_or_branch(trunk: BranchState, condition: str, rerun_failed: bool) -> BranchState:
    """The saved branch (resumed as is), or a fresh one from the trunk.

    With rerun_failed, a failed branch restarts from the trunk; its failure and
    re-ask log are kept in `history`.
    """
    path = branch_path(trunk.model_set, condition, trunk.trial_id)
    if not path.exists():
        return trunk.branch_from(condition)
    st = load_state(path)
    check_config(st.config, trunk.config, str(path))
    if st.status == "failed" and rerun_failed:
        fresh = trunk.branch_from(condition)
        fresh.history = st.history + [{"failure": st.failure, "reasks": st.reasks}]
        return fresh
    return st


def merge_condition(models: ModelSet, condition: str, plan: RoundPlan,
                    branches: List[BranchState], names: List[str]) -> Dict[str, Any]:
    """All complete branches of one condition as one harness-format file.

    `branches` should be every saved branch of the kept trials, not just those run in
    this call, so a partial run never shrinks the merged file.
    """
    done = sorted((b for b in branches if b.status == "complete"), key=lambda b: b.trial_id)
    cond = CONDITIONS[condition]
    rounds = [{"round_id": r, "trials": [b.rounds[r] for b in done]} for r in range(plan.total_rounds)]
    analysis = analyze_all_rounds(rounds, GAME_TYPE, models.base, len(names),
                                  SELF_REFERENCE, plan.total_rounds)
    metadata = {
        **analysis["metadata"],
        "protocol": "peer_swap_endogenous",
        "model_set": models.name,
        "variant": done[0].config.get("variant", {"name": "baseline"})["name"] if done else None,
        "condition": condition,
        "condition_label": f"{cond.number}. {cond.label}",
        "trial_ids": [b.trial_id for b in done],
        "harness_judge": "not run",
        "swap": {"seat": SWAP_SEAT, "round_id": plan.swap,
                 "new_name": NEW_NAME if cond.rename else SWAP_SEAT,
                 "new_model": models.model_for(cond.seat_role), "told": cond.told},
        "agent_models": {"trunk": seat_models(None, 0, plan, models, names),
                         "branch": seat_models(cond, plan.swap, plan, models, names)},
        "config": done[0].config if done else None,
    }
    probes = [{"trial_id": b.trial_id, **p} for b in done for p in b.probes]
    reasks = {b.trial_id: len(b.reasks) for b in done}
    earlier_failures = {b.trial_id: b.history for b in done if b.history}
    return {"metadata": metadata, "per_round": analysis["per_round"], "rounds": rounds,
            "probes": probes, "reasks": reasks, "earlier_failures": earlier_failures}


def main(argv: List[str] = None) -> int:
    """Run (or resume) the branches, then rebuild the merged condition files. Returns an exit code."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    cli_common.add_common_args(parser)
    parser.add_argument("--conditions", nargs="+", choices=list(CONDITIONS), default=None,
                        help="default: the set's planned conditions (DEFAULT_CONDITIONS), else every "
                             "condition it has models for except cold")
    parser.add_argument("--trials", nargs="+", type=int,
                        help="run only these kept trial ids (default: all kept trials)")
    parser.add_argument("--rerun-failed", action="store_true", help="restart failed branches from the trunk")
    args = parser.parse_args(argv)
    run, var = cli_common.run_name(args), cli_common.variant(args)
    cli_common.setup_output(args.fake, run)

    models = cli_common.model_set(args)
    kept = kept_trials(run)
    if not run_config_path(run).exists() or not kept:
        print(f"No selected trunk trials for {run}; run experiment.run_trunk first.")
        return 1
    not_kept = sorted(set(args.trials or []) - set(kept))
    if not_kept:
        print(f"ERROR: trials {not_kept} were not kept by the selection rule (kept: {kept}).")
        return 1
    trial_ids = args.trials or kept
    runnable = [c for c in CONDITIONS if models.model_for(CONDITIONS[c].seat_role) is not None]
    fallback = [c for c in runnable if not CONDITIONS[c].cold]   # cold is added on request only
    args.conditions = args.conditions or list(DEFAULT_CONDITIONS.get(models.name, fallback))
    missing = [c for c in args.conditions if c not in runnable]
    if missing:
        print(f"ERROR: model set {models.name} has no model for conditions {missing}; "
              f"pass --conditions from: {' '.join(runnable)}")
        return 1
    try:
        plan, run_cfg, _ = cli_common.resolve_run(models, var, run)
        trunks = {tid: load_trunk(run, tid, run_cfg) for tid in trial_ids}
        branches = [load_or_branch(trunks[tid], c, args.rerun_failed)
                    for tid in trial_ids for c in args.conditions]
    except ConfigMismatch as err:
        print(f"ERROR: {err}")
        return 1

    calls, extra = cli_common.estimate_calls(branches, plan, models, var)
    cli_common.print_estimate(calls, extra)
    if args.dry_run:
        return 0

    clients = cli_common.build_clients(args, calls)
    stopped = None
    try:
        run_branches(branches, plan, models, clients,
                     save=lambda b: save_state(branch_path(run, b.condition, b.trial_id), b),
                     before_round=cli_common.spend_guard(args, list(calls)), variant=var)
    except SpendCapReached as stop:
        stopped = stop

    for c in args.conditions:
        on_disk = load_branches(run, c, kept)
        if any(b.status == "complete" for b in on_disk):
            save_json(condition_path(run, c),
                      merge_condition(models, c, plan, on_disk, run_cfg["agent_names"]))
    for b in branches:
        if b.status == "failed":
            print(f"FAILED {b.key}: {b.failure}")
    print(f"complete {sum(b.status == 'complete' for b in branches)} / {len(branches)} branches run")
    if stopped:
        print(f"STOPPED: {stopped}. Completed rounds are saved; rerun the same command to resume.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
