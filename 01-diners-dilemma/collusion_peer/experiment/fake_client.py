"""Offline stand-in for the API clients, for tests and --fake runs. No network use.

Replies are valid JSON for every stage, shaped like real OpenRouter replies
({"content": "<json>"}). Behavior can differ by model, and failures can be injected.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict, List, Optional

from experiment.config import PROBE2_MOST_LIKELY, PROBE2_SAME_AS_Q, PROBE_SAME_AS_Q


def split_request_id(cid: str) -> Dict[str, str]:
    """Parse 'r{round}.{condition}.t{trial}.{stage}.{who}' into its parts."""
    parts = cid.split(".")
    return {"round": parts[0][1:], "branch": ".".join(parts[1:-2]), "stage": parts[-2], "who": parts[-1]}


class FakeClient:
    """Answers every request locally.

    policy: {model: {"plan": A, "announce": A, "choice": A}} with A = CHEAP or EXPENSIVE
            (default: honest CHEAP everywhere).
    fail:   {request-id substring: number of times to reply with unparseable text}.
    probe:  the answer every probe gets.
    accuse: {"rater>target": round index}: in detection-bonus runs, that rater answers "yes" to
            the accusation question about that target from that round on (everyone else "no").
    """

    def __init__(self, policy: Optional[Dict[str, Dict[str, str]]] = None,
                 fail: Optional[Dict[str, int]] = None,
                 probe: Optional[Dict[str, Any]] = None,
                 accuse: Optional[Dict[str, int]] = None):
        self.policy = policy or {}
        self.fail = dict(fail or {})
        self.probe = probe or {"replaced": "no", "which": "none", "confidence": 60}
        self.accuse = accuse or {}
        self.requests: List[Dict[str, Any]] = []   # every request received, in order
        self.batches: List[List[str]] = []         # request ids per execute_all call
        self.calls_by_model: Counter = Counter()

    def _actions(self, model: str) -> Dict[str, str]:
        return {"plan": "CHEAP", "announce": "CHEAP", "choice": "CHEAP", **self.policy.get(model, {})}

    def _reply(self, request: Dict[str, Any]) -> Dict[str, Any]:
        cid = request["custom_id"]
        for pattern, remaining in self.fail.items():
            if pattern in cid and remaining > 0:
                self.fail[pattern] = remaining - 1
                return {"content": "Sorry, I can't answer in JSON right now."}
        if cid.startswith("ceiling."):
            return {"content": json.dumps({"same_author": "yes", "confidence": 60})}
        part = split_request_id(cid)
        act = self._actions(request["model"])
        stage = part["stage"]
        if stage == "s1":
            body = {"intended_action": act["plan"], "reasoning": f"Plan {act['plan']}."}
        elif stage == "s2":
            body = {"stated_action": act["announce"], "message": f"I will order {act['announce']}."}
        elif stage == "s3":
            body = {"choice": act["choice"], "reasoning": f"Ordering {act['choice']}."}
        elif stage == "refl":
            body = {"score": 4, "assessment": f"Agent {part['who'].split('>')[1]} kept their word."}
            if "Accusation: do you accuse" in request["messages"][-1]["content"]:
                start = self.accuse.get(part["who"])
                body["accuse"] = "yes" if start is not None and int(part["round"]) >= start else "no"
        elif stage == "probe":
            body = dict(self.probe)
            user = request["messages"][-1]["content"]
            if PROBE_SAME_AS_Q in user or PROBE2_SAME_AS_Q in user:
                body.update(same_as_q="unsure", same_confidence=50)
            if PROBE2_MOST_LIKELY in user:   # probe v2: 'swapped' key plus a forced choice
                body.setdefault("swapped", body.get("replaced", "no"))
                # never the asker or the seat; valid with 5 players (J M Q T Z) and 3 (J Q T)
                body.setdefault("most_likely", "J" if part["who"] == "T" else "T")
        elif stage == "judge":
            body = {"identity": "no", "style": "no", "behavior": "no"}
        else:
            raise ValueError(f"unknown stage in request id {cid}")
        return {"content": json.dumps(body)}

    def execute_all(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Same interface as the harness's queued clients."""
        self.batches.append([r["custom_id"] for r in requests])
        out = {}
        for request in requests:
            self.requests.append(request)
            self.calls_by_model[request["model"]] += 1
            out[request["custom_id"]] = self._reply(request)
        return out
