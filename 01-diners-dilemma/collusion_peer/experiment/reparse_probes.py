"""Re-derive probe answers from the raw transcripts with the current probe parser.

Usage (from /home/vsskl/collusion_peer):
    harness/.venv/bin/python -m experiment.reparse_probes --model-set option_a --dry-run
    harness/.venv/bin/python -m experiment.reparse_probes --model-set option_a

Why: the first parser rejected boolean answers ("replaced": true), so such probes were
re-asked, and some ended up invalid. Probes are never shown to other agents or kept in
memory, so they can be re-scored from the saved raw replies without replaying any game.

For every probe in every trunk and branch state file, this takes the request's
attempts from the raw transcript (latest session only, in order) and keeps the FIRST
attempt that parses. The state file's probe entry is replaced, with the previous entry
kept under "before_reparse". Afterwards rerun run_branch (to rebuild the merged
condition files), analyze and export_transcripts.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from experiment import cli_common
from experiment.config import CONDITIONS, MAX_TRIALS, SWAP_SEAT, RoundPlan, variant_of
from experiment.probe import allowed_which, forced_options, parse_probe
from experiment.state import (BranchState, branch_path, load_state, run_dir, save_state,
                              trunk_path)


def raw_attempts(path: Path) -> Dict[str, List[Any]]:
    """Raw replies per request id from one raw transcript file, latest session only."""
    if not path.exists():
        return {}
    lines = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    latest: Dict[str, str] = {}
    for rec in lines:
        latest[rec["request_id"]] = max(latest.get(rec["request_id"], ""), rec.get("session", ""))
    out: Dict[str, List[Any]] = {}
    for rec in lines:
        if rec.get("session", "") == latest[rec["request_id"]]:
            out.setdefault(rec["request_id"], []).append(rec["raw_reply"])
    return out


def first_parse(replies: List[Any], allowed: List[str], ask_same: bool, version: int = 1,
                forced: Optional[List[str]] = None) -> Tuple[Optional[dict], int]:
    """The first reply that parses, and its 1-based attempt number (0 if none parses)."""
    for i, reply in enumerate(replies):
        answer = parse_probe(reply, allowed, ask_same, version, forced)
        if answer is not None:
            return answer, i + 1
    if replies:   # as in the live run: keep the rest of the last reply if only the forced choice failed
        answer = parse_probe(replies[-1], allowed, ask_same, version, forced, allow_refusal=True)
        if answer is not None:
            return answer, len(replies)
    return None, 0


def reparse(b: BranchState, model_set: str) -> int:
    """Re-score every probe of one state in place; return how many entries changed."""
    plan = RoundPlan(**b.config["rounds"])
    version = variant_of(b.config).probe_version
    raw_root = run_dir(model_set) / "transcripts" / "raw"
    sources = {"trunk": raw_attempts(raw_root / "trunk" / f"trial_{b.trial_id}.jsonl")}
    if b.condition:
        sources[b.condition] = raw_attempts(raw_root / b.condition / f"trial_{b.trial_id}.jsonl")
    changed = 0
    for i, p in enumerate(b.probes):
        r = p["round_id"]
        part = "trunk" if r < plan.swap else b.condition
        cid = f"r{r}.{part}.t{b.trial_id}.probe.{p['agent']}"
        replies = sources[part].get(cid)
        if not replies:
            continue   # no raw transcript for this probe; keep the stored answer
        names = b.rounds[r]["announcement_order"]
        renamed = b.rounds[r]["seat"] != SWAP_SEAT
        allowed = allowed_which(names, SWAP_SEAT if renamed else None)
        answer, attempt = first_parse(replies, allowed, renamed, version, forced_options(names, p["agent"]))
        new = {"round_id": r, "agent": p["agent"], "parse_ok": answer is not None, **(answer or {}),
               "parsed_from_attempt": attempt}
        old = {k: v for k, v in p.items() if k != "before_reparse"}
        if {k: v for k, v in new.items() if k != "parsed_from_attempt"} != \
           {k: v for k, v in old.items() if k != "parsed_from_attempt"}:
            changed += 1
        b.probes[i] = {**new, "before_reparse": p.get("before_reparse", old)}
    return changed


def main(argv: List[str] = None) -> int:
    """Re-score the probes of every trunk and branch of one model set. Returns an exit code."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model-set", required=True, choices=sorted(cli_common.MODEL_SETS))
    cli_common.add_variant_arg(parser)
    parser.add_argument("--fake", action="store_true", help="work on experiment/runs_fake/")
    parser.add_argument("--dry-run", action="store_true", help="report changes; write nothing")
    args = parser.parse_args(argv)
    run = cli_common.run_name(args)
    cli_common.setup_output(args.fake, run)
    paths = [trunk_path(run, t) for t in range(MAX_TRIALS)]
    paths += [branch_path(run, c, t) for c in CONDITIONS for t in range(MAX_TRIALS)]
    total = 0
    for path in (p for p in paths if p.exists()):
        b = load_state(path)
        changed = reparse(b, run)
        if changed:
            print(f"{b.key}: {changed} probe answer(s) changed")
            total += changed
            if not args.dry_run:
                save_state(path, b)
    print(f"{total} probe answers changed{' (dry run; nothing written)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
