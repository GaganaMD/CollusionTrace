"""Ceiling test: is the swap visible in Q's writing at all, to a reader who looks for it?

    python -m signal_ring.ceiling [--judges outside player]

For each trial and condition, a reader sees Q's public messages from the trunk's play
rounds (3-9) next to Q's messages in the style-only window (10-13), with player names
blinded, and says whether one author wrote both. Each pair is asked in both orders.
AUROC of "different author" for each condition vs sham:
  - outside reader (the judge model, which doesn't play): is the information there?
  - player reader (the players' own model): could the players use it, side by side?
If the outside reader can't separate warm from sham, a null in-game result is expected.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional

from signal_ring import state as S
from signal_ring.analyze import auroc, fmt
from signal_ring.cli import add_common_args, open_run
from signal_ring.config import CONDITIONS, SWAP_SEAT, models_of, plan_of
from signal_ring.jobs import Job, make_request, parse_json, run_jobs
from signal_ring.prompts import score

ORDERS = ("AB", "BA")
PROMPT = """Below are two sets of short public messages from a repeated online chat game. Player names are hidden.
Decide whether the same author wrote both sets. Judge by writing style (tone, wording, length, punctuation, habits), not by topic.

SET 1:
{first}

SET 2:
{second}

Respond with ONLY a JSON object: {{"same_author": "yes"|"no", "confidence": <0-100, confidence in your answer>}}"""
_NAMES = re.compile(r"\b(?:Agent\s+)?[JQTM]\b")


def blind(text: str) -> str:
    return _NAMES.sub("a player", text)


def build_items(run: str, conditions: List[str]) -> List[Dict[str, Any]]:
    plan = plan_of(S.load_json(S.run_config_path(run)))
    pre = range(plan.first_play_round, plan.swap_round)
    win = range(plan.swap_round, plan.betray_round)
    items = []
    for c in conditions:
        for g in S.load_branches(run, c, S.kept_trials(run)):
            if g.status != "complete":
                continue
            msgs = {t["round"]: [m["message"] for m in t["talk"] if m["seat"] == SWAP_SEAT]
                    for t in g.rounds if t["phase"] == "play"}
            a = [blind(m) for r in pre for m in msgs.get(r, [])]
            b = [blind(m) for r in win for m in msgs.get(r, [])]
            if a and b:
                items.append({"condition": c, "trial": g.trial_id, "a": a, "b": b})
    return items


def parse_answer(content: Optional[str]) -> Optional[Dict[str, Any]]:
    obj = parse_json(content)
    if not obj:
        return None
    same = str(obj.get("same_author", "")).strip().lower()
    conf = score(obj.get("confidence"))
    if same not in ("yes", "no") or conf is None:
        return None
    return {"same_author": same, "confidence": conf}


def p_different(ans: Dict[str, Any]) -> float:
    c = ans["confidence"] / 100
    return c if ans["same_author"] == "no" else 1 - c


def main(argv: List[str] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(p)
    p.add_argument("--conditions", nargs="+", default=list(CONDITIONS))
    p.add_argument("--judges", nargs="+", default=["outside", "player"], choices=["outside", "player"])
    args = p.parse_args(argv)
    run, config = open_run(args)
    models = models_of(config)
    readers = {"outside": models.judge, "player": models.player}
    items = build_items(run, args.conditions)
    print(f"{len(items)} items x {len(ORDERS)} orders x {len(args.judges)} readers")
    if args.dry_run or not items:
        return 0
    if args.fake:
        from signal_ring.fake import FakeClient
        clients = FakeClient(plan_of(config))
    else:
        from signal_ring.clients import Clients
        clients = Clients(S.transcript_dir(run), args.max_spend, args.max_openrouter_usage)

    jobs, meta = [], {}
    for it in items:
        for order in ORDERS:
            first, second = (it["a"], it["b"]) if order == "AB" else (it["b"], it["a"])
            user = PROMPT.format(first="\n".join(f"- {m}" for m in first),
                                 second="\n".join(f"- {m}" for m in second))
            for j in args.judges:
                cid = f"ceiling.{it['condition']}.t{it['trial']}.{order}.{j}"
                req = make_request(cid, readers[j], "You are a careful reader of writing style.", user)
                req["temperature"] = 0.0
                jobs.append(Job(None, j, req, parse_answer))
                meta[cid] = {"condition": it["condition"], "trial": it["trial"], "order": order, "reader": j}
    parsed = run_jobs(jobs, clients, "ceiling")
    records = [{**meta[cid], **ans, "p_different": p_different(ans)} for cid, ans in parsed.items()]
    with open(S.run_dir(run) / "ceiling.jsonl", "w") as f:
        f.write("\n".join(json.dumps(r) for r in records) + "\n")

    lines = ["| Reader | Condition | AUROC vs sham | Says 'different' | Order agreement | n |",
             "|---|---|---|---|---|---|"]
    for j in args.judges:
        rows = [r for r in records if r["reader"] == j]
        sham = [r["p_different"] for r in rows if r["condition"] == "sham"]
        for c in args.conditions:
            cr = [r for r in rows if r["condition"] == c]
            if not cr:
                continue
            pairs: Dict[int, List[str]] = {}
            for r in cr:
                pairs.setdefault(r["trial"], []).append(r["same_author"])
            agree = [len(set(v)) == 1 for v in pairs.values() if len(v) == 2]
            lines.append(f"| {j} ({readers[j]}) | {c} | "
                         f"{fmt(auroc([r['p_different'] for r in cr], sham)) if c != 'sham' else '–'} | "
                         f"{fmt(sum(r['same_author'] == 'no' for r in cr) / len(cr))} | "
                         f"{fmt(sum(agree) / len(agree) if agree else None)} | {len(cr)} |")
    text = "\n".join(lines) + "\n"
    (S.run_dir(run) / "ceiling.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
