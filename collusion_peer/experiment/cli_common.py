"""Pieces shared by the command-line tools: options, clients, spend guard, cost estimate."""
from __future__ import annotations

import argparse
import math
from collections import Counter
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from experiment import state
from experiment.clients import Clients, SpendCapReached, make_clients, openrouter_usage
from experiment.config import (EST_HISTORY_TOKENS_PER_ROUND, EST_LOG_TOKENS_OWN_ROUND,
                               EST_LOG_TOKENS_PER_PEER_ROUND, EST_TOKENS_PER_CALL, MODEL_SETS, PRICES, RUNS_DIR, VARIANTS, ModelSet,
                               RoundPlan, Variant, run_config)
from experiment.config import run_name as _run_name
from experiment.engine import calls_for_round
from experiment.fake_client import FakeClient
from experiment.state import (BranchState, ConfigMismatch, check_config, load_json, run_config_path,
                              run_dir)
from src.llm.client_factory import is_openai_model

FAKE_RUNS_DIR = RUNS_DIR.parent / "runs_fake"


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Options every runner takes."""
    parser.add_argument("--model-set", required=True, choices=sorted(MODEL_SETS))
    add_variant_arg(parser)
    parser.add_argument("--dry-run", action="store_true", help="print call counts and cost; send nothing")
    parser.add_argument("--fake", action="store_true",
                        help="offline fake client; writes to experiment/runs_fake/")
    parser.add_argument("--max-openrouter-usage", type=float, default=8.0,
                        help="stop if the OpenRouter ACCOUNT's total usage in USD (all-time, not just "
                             "this run) exceeds this; it was $4.52 after the model screen")
    parser.add_argument("--max-openai-calls", type=int, default=None,
                        help="OpenAI call cap (default: 2x the estimate, to allow re-asks)")


def add_variant_arg(parser: argparse.ArgumentParser) -> None:
    """The --variant option (baseline = the pilot as first run), and the run-folder --tag."""
    parser.add_argument("--variant", choices=list(VARIANTS), default="baseline",
                        help="probe2: new probe only; history: + public record of earlier rounds; "
                             "history_warned: + players told a swap may happen; memlog3: 3 players, "
                             "each with a private log of every earlier round")
    parser.add_argument("--tag", default=None,
                        help="suffix for the run folder (e.g. r20), so runs with different round "
                             "plans don't share one folder")


def run_name(args: argparse.Namespace) -> str:
    """Folder name of this run under runs/: the model set, the variant unless baseline, the tag."""
    return _run_name(args.model_set, args.variant, getattr(args, "tag", None))


def variant(args: argparse.Namespace) -> Variant:
    """The Variant named by --variant."""
    return VARIANTS[args.variant]


def setup_output(fake: bool, run: str) -> None:
    """Choose the output root (runs_fake/ for offline runs) and the API error log location."""
    if fake:
        state.set_runs_root(FAKE_RUNS_DIR)
    from src.llm.providers import retry_utils
    retry_utils.ERROR_LOG = str(run_dir(run) / "api_errors.jsonl")


def resolve_run(models: ModelSet, var: Variant, run: str, trunk_rounds: Optional[int] = None,
                total_rounds: Optional[int] = None) -> Tuple[RoundPlan, Dict[str, Any], bool]:
    """The round plan and config for this run: (plan, config, already_saved).

    The first trunk run fixes the settings in trunk/run_config.json. After that the
    saved settings are used; flags that conflict with them, or a code change that
    alters the config, raise ConfigMismatch.
    """
    path = run_config_path(run)
    if path.exists():
        saved = load_json(path)
        plan = RoundPlan(**saved["rounds"])
        if trunk_rounds not in (None, plan.trunk_rounds) or total_rounds not in (None, plan.total_rounds):
            raise ConfigMismatch(f"{path} fixes trunk {plan.trunk_rounds} / total {plan.total_rounds} "
                                 "rounds; drop the conflicting --trunk-rounds / --total-rounds")
        check_config(saved, run_config(models, plan, var), str(path))
        return plan, saved, True
    plan = RoundPlan(trunk_rounds or RoundPlan().trunk_rounds, total_rounds or RoundPlan().total_rounds)
    return plan, run_config(models, plan, var), False


def estimate_calls(branches: Iterable[BranchState], plan: RoundPlan, models: ModelSet,
                   var: Variant = VARIANTS["baseline"]) -> Tuple[Counter, Counter]:
    """Calls per model needed to finish these branches (no re-asks), and the extra input
    tokens per model that the public history and the memory log add."""
    calls: Counter = Counter()
    extra: Counter = Counter()
    for b in branches:
        if b.status != "running":
            continue
        end = plan.swap if b.condition is None else plan.total_rounds
        for r in range(b.next_round, end):
            per_model = calls_for_round(b, r, plan, models, var.agent_names)
            calls.update(per_model)
            if var.history:
                extra.update({m: n * EST_HISTORY_TOKENS_PER_ROUND * r for m, n in per_model.items()})
            if var.memory_log:
                per_call = (EST_LOG_TOKENS_PER_PEER_ROUND * (len(var.agent_names) - 1)
                            + EST_LOG_TOKENS_OWN_ROUND) * r
                extra.update({m: n * per_call for m, n in per_model.items()})
    return calls, extra


def print_estimate(calls: Counter, extra_input: Optional[Counter] = None) -> None:
    """Call counts and a rough cost per model (including any history tokens)."""
    tin, tout = EST_TOKENS_PER_CALL
    extra_input = extra_input or Counter()
    total = 0.0
    print(f"{'model':40s} {'calls':>7s} {'est. USD':>9s}")
    for model, n in sorted(calls.items()):
        pin, pout = PRICES.get(model, (0.0, 0.0))
        cost = (n * tin + extra_input[model]) * pin / 1e6 + n * tout * pout / 1e6
        total += cost
        print(f"{model:40s} {n:7d} {cost:9.2f}")
    print(f"{'total':40s} {sum(calls.values()):7d} {total:9.2f}  (no re-asks or prompt caching; "
          "rough token estimate)")


def build_clients(args: argparse.Namespace, calls: Counter) -> Clients:
    """Fake or real clients that log raw transcripts to transcripts/raw/.

    The OpenAI cap defaults to twice the estimated OpenAI calls.
    """
    transcripts = run_dir(run_name(args)) / "transcripts" / "raw"
    if args.fake:
        fake = FakeClient()
        return Clients(fake, fake, transcript_dir=transcripts)
    openai_estimate = sum(n for m, n in calls.items() if is_openai_model(m))
    cap = args.max_openai_calls if args.max_openai_calls is not None else math.ceil(2 * openai_estimate)
    return make_clients(list(calls), max_openai_calls=cap, transcript_dir=transcripts)


def spend_guard(args: argparse.Namespace, models: List[str]) -> Callable[[int], None]:
    """Before-round check that stops the run if OpenRouter usage passes the cap."""
    uses_openrouter = any(not is_openai_model(m) for m in models)

    def check(round_idx: int) -> None:
        if args.fake or not uses_openrouter:
            return
        usage = openrouter_usage()
        if usage is None:
            print(f"WARNING: could not read OpenRouter usage before round {round_idx + 1}; "
                  "the OpenRouter cap is not being enforced for this round.")
        elif usage > args.max_openrouter_usage:
            raise SpendCapReached(f"OpenRouter usage ${usage:.2f} is over the "
                                  f"${args.max_openrouter_usage:.2f} cap (before round {round_idx + 1})")
    return check


def model_set(args: argparse.Namespace) -> ModelSet:
    """The ModelSet named by --model-set."""
    return MODEL_SETS[args.model_set]
