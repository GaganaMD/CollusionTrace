"""Change judge: label the trust notes written about the swapped seat (optional step).

Usage (from /home/vsskl/collusion_peer):
    harness/.venv/bin/python -m experiment.judge_notes --model-set option_b --dry-run
    harness/.venv/bin/python -m experiment.judge_notes --model-set option_b
    harness/.venv/bin/python -m experiment.judge_notes --model-set option_b --hand-check
    harness/.venv/bin/python -m experiment.judge_notes --model-set option_b --agreement

Scope: every note about the seat (Q, or R after a rename) from the last trunk round to
the final round, in every condition. The judge sees only the note and the target's
letter (blinded), uses the frozen rubric in config.py at temperature 0, and each
distinct note text is judged once.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional

from experiment import cli_common
from experiment.clients import SpendCapReached
from experiment.config import (CONDITIONS, JUDGE_MODEL, JUDGE_RUBRIC, JUDGE_RUBRIC_SHA256,
                               JUDGE_TEMPERATURE, NEW_NAME, RoundPlan)
from experiment.engine import Job, make_request, run_jobs
from experiment.probe import normalize_answer
from experiment.state import kept_trials, load_branches, run_dir, stray_branch_files
from src.endogenous.core.trial_runner import _parse_response

LABELS = ("identity", "style", "behavior")
HAND_CHECK_SIZE = 30
JUDGE_SCHEMA = {"name": "note_labels", "strict": True,
                "schema": {"type": "object",
                           "properties": {k: {"type": "string", "enum": ["yes", "no"]} for k in LABELS},
                           "required": list(LABELS), "additionalProperties": False}}


def collect_notes(model_set: str) -> List[Dict[str, Any]]:
    """Every note about the seat, from the last trunk round on, in the kept trials' complete branches."""
    kept = kept_trials(model_set)
    notes = []
    for cond in CONDITIONS:
        stray = stray_branch_files(model_set, cond, kept)
        if stray:
            print(f"WARNING: ignoring branch files outside the selection: {[str(p) for p in stray]}")
        for b in load_branches(model_set, cond, kept):
            if b.status != "complete":
                continue
            plan = RoundPlan(**b.config["rounds"])
            for trial in b.rounds[plan.swap - 1:]:
                seat = trial["seat"]
                for rater, data in trial["agents"].items():
                    note = (data.get("reflection") or {}).get("takeaways", {}).get(seat)
                    if rater != seat and note:
                        text = note["assessment"]
                        notes.append({
                            "trial_id": b.trial_id, "condition": cond, "round_id": trial["round_id"],
                            "rater": rater, "target": seat, "about_new_name": seat == NEW_NAME,
                            "note": text,
                            "note_sha256": hashlib.sha256(f"{seat}|{text}".encode()).hexdigest()})
    return notes


def parse_labels(raw: Any) -> Optional[Dict[str, bool]]:
    """Three yes/no labels, or None if any is missing."""
    p = _parse_response(raw, list(LABELS))
    vals = {k: normalize_answer(p.get(k)) for k in LABELS}   # booleans count as yes / no
    if not all(v in ("yes", "no") for v in vals.values()):
        return None
    return {k: v == "yes" for k, v in vals.items()}


def judge(notes: List[Dict[str, Any]], clients) -> Dict[str, Dict[str, bool]]:
    """Labels per distinct (target, note) hash."""
    unique = {n["note_sha256"]: n for n in notes}
    jobs = [Job(None, h, make_request(f"judge.{h[:16]}", JUDGE_MODEL,
                                      (JUDGE_RUBRIC, f"TARGET: Agent {n['target']}\nNOTE: \"{n['note']}\"",
                                       JUDGE_SCHEMA), told=False, temperature=JUDGE_TEMPERATURE),
                parse_labels) for h, n in unique.items()]
    parsed = run_jobs(jobs, clients, "change judge", reask_log=[])
    return {h: parsed[f"judge.{h[:16]}"] for h in unique if f"judge.{h[:16]}" in parsed}


def write_hand_check(model_set: str, records: List[Dict[str, Any]], seed: int = 0) -> None:
    """Export 30 distinct notes, stratified by condition and detection label, without the labels.

    Refuses to overwrite an existing sheet, which may already hold human labels.
    """
    out = run_dir(model_set)
    if (out / "hand_check.csv").exists():
        print(f"{out / 'hand_check.csv'} already exists; move it away first if you really want a new sample.")
        return
    strata, seen = defaultdict(list), set()
    for rec in records:
        if rec["labels"] and rec["note_sha256"] not in seen:   # each distinct note once
            seen.add(rec["note_sha256"])
            strata[(rec["condition"], rec["labels"]["identity"] or rec["labels"]["style"])].append(rec)
    rng = random.Random(seed)
    for group in strata.values():
        rng.shuffle(group)
    sample, keys = [], sorted(strata)
    while len(sample) < HAND_CHECK_SIZE and any(strata.values()):
        for k in keys:
            if strata[k] and len(sample) < HAND_CHECK_SIZE:
                sample.append(strata[k].pop())
    rng.shuffle(sample)
    with open(out / "hand_check.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "target", "note", *[f"human_{k}" for k in LABELS]])
        for i, rec in enumerate(sample):
            w.writerow([i, rec["target"], rec["note"], "", "", ""])
    (out / "hand_check_key.json").write_text(json.dumps(
        [{"item": i, "note_sha256": rec["note_sha256"], "condition": rec["condition"],
          "labels": rec["labels"]} for i, rec in enumerate(sample)], indent=1))
    print(f"wrote {out / 'hand_check.csv'} ({len(sample)} notes): "
          "fill human_* with yes/no, then run --agreement")


def cohen_kappa(pairs: List[tuple]) -> Optional[float]:
    """Cohen's kappa for two raters' yes/no labels; None if chance agreement is 1."""
    n = len(pairs)
    observed = sum(a == b for a, b in pairs) / n
    p_a, p_b = sum(a for a, _ in pairs) / n, sum(b for _, b in pairs) / n
    chance = p_a * p_b + (1 - p_a) * (1 - p_b)
    return None if chance == 1 else (observed - chance) / (1 - chance)


def agreement(model_set: str) -> None:
    """Print agreement and Cohen's kappa between the filled hand-check sheet and the judge."""
    out = run_dir(model_set)
    key = {k["item"]: k for k in json.loads((out / "hand_check_key.json").read_text())}
    with open(out / "hand_check.csv") as f:
        rows = [r for r in csv.DictReader(f) if all(r[f"human_{k}"].strip() for k in LABELS)]
    for label in LABELS:
        pairs = [(r[f"human_{label}"].strip().lower() == "yes", key[int(r["item"])]["labels"][label])
                 for r in rows]
        if pairs:
            agree = sum(h == j for h, j in pairs) / len(pairs)
            kappa = cohen_kappa(pairs)
            print(f"{label:9s} n={len(pairs)} agreement={agree:.0%} "
                  f"kappa={'n/a' if kappa is None else f'{kappa:.2f}'}")


def main(argv: List[str] = None) -> int:
    """Judge the notes (or export / score the hand check). Returns an exit code."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    cli_common.add_common_args(parser)
    parser.add_argument("--hand-check", action="store_true", help="export the 30-note sample")
    parser.add_argument("--agreement", action="store_true", help="score the filled hand-check sheet")
    args = parser.parse_args(argv)
    run = cli_common.run_name(args)
    cli_common.setup_output(args.fake, run)
    path = run_dir(run) / "judge_notes.jsonl"

    if args.agreement:
        agreement(run)
        return 0
    if args.hand_check:
        if not path.exists():
            print("No judge labels yet: run the judge first (without --hand-check).")
            return 1
        write_hand_check(run, [json.loads(l) for l in path.read_text().splitlines()])
        return 0

    notes = collect_notes(run)
    n_unique = len({n["note_sha256"] for n in notes})
    print(f"{len(notes)} notes, {n_unique} distinct texts to judge")
    calls = cli_common.Counter({JUDGE_MODEL: n_unique})
    cli_common.print_estimate(calls)
    if args.dry_run or not notes:
        return 0
    clients = cli_common.build_clients(args, calls)
    try:
        cli_common.spend_guard(args, [JUDGE_MODEL])(0)
        labels = judge(notes, clients)
    except SpendCapReached as stop:
        print(f"STOPPED: {stop}")
        return 2
    records = [{**n, "labels": labels.get(n["note_sha256"]), "judge_model": JUDGE_MODEL,
                "temperature": JUDGE_TEMPERATURE, "rubric_sha256": JUDGE_RUBRIC_SHA256} for n in notes]
    tmp = path.with_suffix(".jsonl.tmp")
    tmp.write_text("".join(json.dumps(r) + "\n" for r in records))
    tmp.replace(path)
    print(f"wrote {path}: {sum(r['labels'] is not None for r in records)} of {len(records)} notes labelled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
