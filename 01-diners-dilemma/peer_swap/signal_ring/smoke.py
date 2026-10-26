"""One real call per model, to check keys, routing, JSON parsing, cost reporting and caching.

    python -m signal_ring.smoke [--model-set haiku]

Costs a fraction of a cent. Logs to runs/smoke/transcripts/raw/smoke.jsonl.
"""
from __future__ import annotations

import argparse
import sys
from typing import List

from signal_ring import state as S
from signal_ring.clients import Clients, openrouter_usage
from signal_ring.config import MODEL_SETS
from signal_ring.jobs import make_request, parse_json

USER = 'Reply with ONLY this JSON object, filling in a short greeting: {"message": "<greeting>"}'


def main(argv: List[str] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-set", default="haiku", choices=sorted(MODEL_SETS))
    args = p.parse_args(argv)
    ms = MODEL_SETS[args.model_set]
    clients = Clients(S.transcript_dir("smoke"))
    print(f"OpenRouter account usage before: {openrouter_usage()}")
    ok = True
    # A ~2,500-token system prompt, sent twice, to see whether caching shows in the usage.
    system = "You are a test assistant. " + ("Background filler sentence for a cache check. " * 300)
    for role, model in [("player", ms.player), ("newcomer", ms.newcomer), ("judge", ms.judge)]:
        for attempt in (1, 2):
            cid = f"smoke.{role}.{attempt}"
            reply = clients.execute([make_request(cid, model, system, USER)], "smoke")[cid]
            obj = parse_json(reply["content"])
            good = bool(obj and isinstance(obj.get("message"), str))
            ok &= good
            u = reply["usage"] or {}
            cached = (u.get("prompt_tokens_details") or {}).get("cached_tokens")
            reasoning = (u.get("completion_tokens_details") or {}).get("reasoning_tokens")
            print(f"{role:9} {model:32} call {attempt}: parsed={good} prompt={u.get('prompt_tokens')} "
                  f"completion={u.get('completion_tokens')} reasoning={reasoning} cached={cached} cost={u.get('cost')} "
                  f"error={reply['error']}")
    print(f"spent ${clients.spent:.5f}; OpenRouter account usage after: {openrouter_usage()}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
