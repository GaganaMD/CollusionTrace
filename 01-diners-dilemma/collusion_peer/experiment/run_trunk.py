"""Run the shared trunk (rounds before the swap) and select the trials to branch.

Usage (from /home/vsskl/collusion_peer):
    harness/.venv/bin/python -m experiment.run_trunk --model-set option_b --dry-run
    harness/.venv/bin/python -m experiment.run_trunk --model-set option_b
    harness/.venv/bin/python -m experiment.run_trunk --model-set option_b --extend

Trials already complete are skipped; trials stopped part-way resume at the next round.
"""
from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List

from experiment import cli_common
from experiment.clients import SpendCapReached
from experiment.config import (COOPERATIVE_ACTION, INITIAL_TRIALS, MAX_NOT_CHEAP_PER_ROUND, MAX_TRIALS,
                               TRIALS_TO_KEEP, RoundPlan)
from experiment.engine import run_branches
from experiment.roster import empty_memory
from experiment.state import (BranchState, ConfigMismatch, check_config, load_state, run_config_path,
                              save_json, save_state, selection_path, trunk_path)


def load_or_create(run: str, trial_id: int, config: Dict[str, Any]) -> BranchState:
    """The saved trunk for this trial (after a config check), or a fresh one."""
    path = trunk_path(run, trial_id)
    if path.exists():
        st = load_state(path)
        check_config(st.config, config, str(path))
        return st
    return BranchState(key=f"trunk.t{trial_id}", trial_id=trial_id, condition=None,
                       model_set=run, config=config, memory=empty_memory(config["agent_names"]))


def min_cheap(n_players: int) -> int:
    """CHEAP choices a selection round needs: all players but MAX_NOT_CHEAP_PER_ROUND."""
    return n_players - MAX_NOT_CHEAP_PER_ROUND


def selection_result(st: BranchState, plan: RoundPlan) -> Dict[str, Any]:
    """Apply the pre-registered rule: at most MAX_NOT_CHEAP_PER_ROUND players not CHEAP in both rounds.

    A choice that is anything but CHEAP (including unparsed) counts as not CHEAP.
    """
    if st.status != "complete":
        return {"status": st.status, "cheap": None, "passes": False, "failure": st.failure}
    cheap = {f"R{r + 1}": sum(c == COOPERATIVE_ACTION for c in st.rounds[r]["outcomes"]["choices"].values())
             for r in plan.selection_rounds}
    return {"status": "complete", "cheap": cheap,
            "passes": all(n >= min_cheap(len(st.config["agent_names"])) for n in cheap.values())}


def select(run: str, plan: RoundPlan, n_players: int) -> Dict[str, Any]:
    """Evaluate every saved trunk and keep the first TRIALS_TO_KEEP that pass, by trial id."""
    results = {tid: selection_result(load_state(trunk_path(run, tid)), plan)
               for tid in range(MAX_TRIALS) if trunk_path(run, tid).exists()}
    passing = [tid for tid, res in sorted(results.items()) if res["passes"]]
    kept = passing[:TRIALS_TO_KEEP]
    return {"rule": f">= {min_cheap(n_players)}/{n_players} CHEAP in rounds "
                    f"{', '.join(str(r + 1) for r in plan.selection_rounds)}; first {TRIALS_TO_KEEP} by id",
            "trials": {str(k): v for k, v in results.items()}, "kept": kept,
            "enough": len(kept) >= TRIALS_TO_KEEP}


def main(argv: List[str] = None) -> int:
    """Run (or resume) the trunk trials, then write selection.json. Returns an exit code."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    cli_common.add_common_args(parser)
    parser.add_argument("--trunk-rounds", type=int, default=None,
                        help="rounds before the swap (default 5; fixed by the first run)")
    parser.add_argument("--total-rounds", type=int, default=None,
                        help="rounds in total (default 10; fixed by the first run)")
    parser.add_argument("--extend", action="store_true",
                        help=f"run the extra trial ids {INITIAL_TRIALS}..{MAX_TRIALS - 1}")
    args = parser.parse_args(argv)
    run, var = cli_common.run_name(args), cli_common.variant(args)
    cli_common.setup_output(args.fake, run)

    models = cli_common.model_set(args)
    try:
        plan, config, saved = cli_common.resolve_run(models, var, run, args.trunk_rounds, args.total_rounds)
        ids = range(INITIAL_TRIALS, MAX_TRIALS) if args.extend else range(INITIAL_TRIALS)
        trunks = [load_or_create(run, tid, config) for tid in ids]
    except ConfigMismatch as err:
        print(f"ERROR: {err}")
        return 1

    calls, extra = cli_common.estimate_calls(trunks, plan, models, var)
    cli_common.print_estimate(calls, extra)
    if args.dry_run:
        return 0
    if not saved:
        save_json(run_config_path(run), config)

    clients = cli_common.build_clients(args, calls)
    try:
        run_branches(trunks, plan, models, clients,
                     save=lambda b: save_state(trunk_path(run, b.trial_id), b),
                     before_round=cli_common.spend_guard(args, [models.base]), variant=var)
    except SpendCapReached as stop:
        print(f"STOPPED: {stop}. Completed rounds are saved; rerun the same command to resume.")
        return 2

    selection = select(run, plan, len(config["agent_names"]))
    save_json(selection_path(run), selection)
    for tid, res in selection["trials"].items():
        print(f"trial {tid}: {res['status']}, CHEAP {res['cheap']}, passes={res['passes']}")
    print(f"kept: {selection['kept']}")
    if not selection["enough"]:
        hint = "run again with --extend" if not args.extend else "proceed with these and report it"
        print(f"Only {len(selection['kept'])} of {TRIALS_TO_KEEP} needed trials passed: {hint}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
