"""Send the harness's own reflection requests for one saved round and print raw replies.

Usage (from harness/): .venv/bin/python ../screen/probe_parse.py <model> <saved output json>
Rebuilds trial 0, round 0 reflection prompts exactly as trial_runner does, sends them
through QueuedOpenRouterClient, and reports how each reply parses.
"""
import json
import sys
from collections import Counter
from types import SimpleNamespace

sys.path.insert(0, ".")
from src.config import settings  # noqa: E402
from src.endogenous.core.prompt_builders import build_single_agent_reflection_prompt  # noqa: E402
from src.endogenous.core.trial_runner import _build_request, _compute_outcomes, _parse_response  # noqa: E402
from src.llm.providers.queued_openrouter import QueuedOpenRouterClient  # noqa: E402

model, path = sys.argv[1], sys.argv[2]
t = json.load(open(path))["rounds"][0]["trials"][0]
names = sorted(t["agents"])
stage2 = {a: t["agents"][a]["stage2"] for a in names}
choices = {a: t["agents"][a]["stage3"].get("choice") or "CHEAP" for a in names}
outcomes = _compute_outcomes("diners", names, {}, choices)

reqs = []
for a in names:
    for b in names:
        if a == b:
            continue
        sys_p, usr_p, schema = build_single_agent_reflection_prompt(
            game_type="diners", agent_name=a, target_agent=b, agent_names=names, game_params={},
            stage2_results=stage2, outcomes=outcomes, current_takeaways={}, round_idx=0,
            supports_structured=False)
        reqs.append(_build_request(f"{a}_about_{b}", model, sys_p, usr_p, schema, 1.0, False,
                                   SimpleNamespace(temperature=1.0)))

client = QueuedOpenRouterClient(api_key=settings.OPENROUTER_API_KEY, max_workers=25, timeout=120, max_retries=5)
raw = client.execute_all(reqs)
kinds = Counter()
for cid, r in sorted(raw.items()):
    p = _parse_response(r, ["score", "assessment"])
    ok = p.get("score") is not None and bool(p.get("assessment"))
    kind = "ok" if ok else ("error: " + str(r.get("error"))[:120] if r.get("status") == "error" else "unparsed")
    kinds[kind.split(":")[0] if ok else kind[:60]] += 1
    if not ok:
        print(f"--- {cid}: {kind}\n{json.dumps(r)[:700]}\n")
print("SUMMARY", model, dict(kinds))
