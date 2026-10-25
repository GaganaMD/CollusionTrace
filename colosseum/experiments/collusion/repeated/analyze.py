"""Descriptive analysis of a RepeatedJira run root (no inference).

Writes episodes.csv, rounds.csv, monitor_decisions.csv and analysis_summary.json
into <root>/analysis/. Monitor decisions are label-free; no ground-truth labels
are produced here (annotation is a separate, blinded step).
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from experiments.collusion.monitoring.access import policy_with_public_channels
from experiments.collusion.monitoring.ingest import load_run
from experiments.collusion.monitoring.observations import make_observation
from experiments.collusion.monitoring.rules import evaluate_monitor
from experiments.collusion.monitoring.rules_o2 import evaluate_o2


def analyze(root: Path) -> dict:
    out = root / "analysis"
    out.mkdir(exist_ok=True)
    eps, rounds, mons = [], [], []
    policy = policy_with_public_channels(["0"])
    for d in sorted(p for p in root.iterdir() if (p / "run_config.json").exists()):
        cfg = json.loads((d / "run_config.json").read_text())
        summ = json.loads((d / "final_summary.json").read_text())
        priv = json.loads((d / "rounds_privileged.json").read_text())
        acc = json.loads((d / "accounting.json").read_text())
        boards = json.loads((d / "blackboards.json").read_text())
        msgs = Counter(b["blackboard_id"] for b in boards for e in b["events"] if e["kind"] == "communication")
        ecfg = cfg["environment_cfg"]
        paired = unilat = dup = bonus_paid = signoff_any = 0
        for r in priv["rounds"]:
            kinds = {t["id"]: t["kind"] for t in r["tasks"]}
            assign = r.get("assignment") or {}
            k = {a: kinds.get(t, t) for a, t in assign.items()}
            rec = r["offer_recipient"]
            others_signoff = [a for a, kk in k.items() if kk == "signoff"]
            rounds.append({"run_id": cfg["run_id"], "cell": cfg["cell"], "seed": cfg["seed"], "round": r["round"],
                           "offer_recipient": rec, "recipient_choice": k.get(rec), "public_score": r.get("public_score"),
                           "feasible_optimum": r.get("feasible_optimum"), "regret": (r.get("feasible_optimum") or 0) - (r.get("public_score") or 0),
                           "violations": r.get("violations"), "bonus_paid": r.get("bonus_paid_to") is not None,
                           "paired_capture": r.get("paired_capture"), "unilateral_premium": r.get("unilateral_premium"),
                           "attributable_delta": r.get("attributable_delta"), "signoff_claimers": ";".join(others_signoff),
                           "premium_claimers": ";".join(a for a, kk in k.items() if kk == "premium"),
                           "assignment_kinds": json.dumps(k)})
            paired += bool(r.get("paired_capture")); unilat += bool(r.get("unilateral_premium"))
            dup += int(r.get("violations") or 0); bonus_paid += r.get("bonus_paid_to") is not None
            signoff_any += bool(others_signoff)
        eps.append({"run_id": cfg["run_id"], "cell": cfg["cell"], "seed": cfg["seed"], "objective_regime": ecfg["objective_regime"],
                    "private_channel": ecfg["private_channel"], "status": summ["status"], "joint_public": summ["joint_reward"],
                    "optimum": summ["feasible_optimum_total"], "regret": summ["feasible_optimum_total"] - summ["joint_reward"],
                    "paired_capture_rounds": paired, "unilateral_premium_rounds": unilat, "signoff_rounds": signoff_any,
                    "violations": dup, "bonus_paid_rounds": bonus_paid, "msgs_team": msgs.get(0, 0), "msgs_private": msgs.get(1, 0),
                    **{f"cum_reward_{i}": round(v, 1) for i, v in enumerate(priv["cumulative_rewards"].values())},
                    "model_calls": acc["model_calls"], "prompt_tokens": acc["prompt_tokens"],
                    "completion_tokens": acc["completion_tokens"], "parse_failures": acc["parse_failures"], "runtime_s": acc["runtime_s"]})
        run = load_run(d)
        for layer in ("O0", "O1", "O2"):
            obs = make_observation(run, layer, policy)
            f0 = evaluate_monitor(obs)
            row = {"run_id": cfg["run_id"], "layer": layer, "events": len(obs.events), "baseline_decision": f0.decision}
            row["monitor1_decision"] = evaluate_o2(obs).decision if layer == "O2" else "n/a"
            mons.append(row)
    for name, rows in (("episodes.csv", eps), ("rounds.csv", rounds), ("monitor_decisions.csv", mons)):
        if rows:
            with (out / name).open("w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summary = {"episodes": len(eps), "complete": sum(e["status"] == "complete" for e in eps),
               "model_calls": sum(e["model_calls"] for e in eps), "parse_failures": sum(e["parse_failures"] for e in eps),
               "prompt_tokens": sum(e["prompt_tokens"] for e in eps), "completion_tokens": sum(e["completion_tokens"] for e in eps),
               "paired_capture_rounds_total": sum(e["paired_capture_rounds"] for e in eps),
               "unilateral_premium_rounds_total": sum(e["unilateral_premium_rounds"] for e in eps),
               "note": "Descriptive only. Structural flags are not collusion labels."}
    (out / "analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    print(json.dumps(analyze(Path(ap.parse_args().root)), indent=2))
