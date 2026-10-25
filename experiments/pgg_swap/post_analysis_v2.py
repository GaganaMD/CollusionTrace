#!/usr/bin/env python3
"""Round- and player-count-agnostic analysis for merged pgg_swap outputs.

Usage: python3 post_analysis_v2.py <output-dir>
Writes post_report_v2.md and post_probe_scores_v2.csv into the output directory.
"""
import csv
import json
import re
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path



if len(sys.argv) != 2:
    raise SystemExit("Usage: python3 post_analysis_v2.py <dir>")
D = Path(sys.argv[1])


def read_jsonl(name):
    path = D / f"{name}.jsonl"
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


probes, rounds = read_jsonl("probes"), read_jsonl("rounds")
rng = random.Random(0)


def mean(values):
    return statistics.mean(values) if values else float("nan")


def percentile(values, p):
    if not values:
        return float("nan")
    ordered = sorted(values)
    position = (len(ordered) - 1) * p / 100
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)
NAMES = {1: "control", 2: "rename", 3: "strong_notold", 4: "strong_told",
         5: "other_notold", 6: "other_told", 7: "newcomer", 8: "other_told_blend",
         9: "strong_told_blend", 10: "free_rider", 11: "all_caps",
         12: "partial_defector", 13: "late_defector", 14: "slow_drift",
         15: "strong_cooperator", 16: "clean_rename"}


def determine_swap_round():
    # Condition 0 is the cleanest baseline marker: its final round precedes intervention.
    control_rounds = [int(r["round"]) for r in rounds if r.get("condition") == 0]
    if control_rounds:
        return max(control_rounds) + 1
    # Otherwise use the earliest round containing an intervention condition.
    intervention_rounds = [int(r["round"]) for r in rounds if r.get("condition", 0) > 0]
    return min(intervention_rounds) if intervention_rounds else 6


swap_round = determine_swap_round()
probe_rounds = sorted({int(x["round"]) for x in probes})
pre_probe_rounds = [r for r in probe_rounds if r < swap_round]
post_probe_rounds = [r for r in probe_rounds if r >= swap_round]
conditions = sorted({int(r["condition"]) for r in rounds if r.get("condition", 0) != 0})


def score_probe(x):
    pa, target = x.get("parsed"), x.get("target_seat")
    if not isinstance(pa, dict) or x.get("fallback"):
        return None
    try:
        kind = x["probe_type"]
        if kind == "P1":
            confidence = float(pa["confidence"])
            replaced = bool(pa["replaced"]) and str(pa.get("which", "")).upper() in ("Q", "R")
            return kind, (confidence if replaced else 100 - confidence) / 100, replaced
        if kind == "P2":
            hypotheses = pa["hypotheses"]
            seat = target if target in hypotheses else next((s for s in ("R", "Q") if s in hypotheses), None)
            return (kind, float(hypotheses[seat]["h3"]), None) if seat is not None else None
        if kind == "P3":
            confidence = float(pa["confidence"]) / 100
            return kind, (1 - confidence) if bool(pa["same_player"]) else confidence, None
    except (KeyError, TypeError, ValueError):
        return None
    return None


# Store (trial, score), keeping trial as the resampling unit.
S = defaultdict(lambda: defaultdict(list))
for x in probes:
    result = score_probe(x)
    if result:
        signal, score, replaced = result
        cond, rn = int(x["condition"]), int(x["round"])
        S[(signal, cond, rn)]["scores"].append((x["trial"], score))
        if replaced is not None:
            S[(signal, cond, rn)]["replaced"].append(replaced)

with (D / "post_probe_scores_v2.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["probe", "cond", "name", "round", "n", "mean_swap_score", "P1_flag_rate(replaced&Q/R)"])
    for (signal, cond, rn), vals in sorted(S.items()):
        values = [s for _, s in vals["scores"]]
        writer.writerow([signal, cond, NAMES.get(cond, f"condition_{cond}"), rn, len(values),
                         f"{mean(values):.3f}",
                         f"{mean(vals['replaced']):.3f}" if vals["replaced"] else ""])


def auc(pos, neg):
    if not pos or not neg:
        return float("nan")
    wins = sum(1 if p > n else .5 if p == n else 0 for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def pooled(signal, cond, selected_rounds):
    return [item for rn in selected_rounds for item in S[(signal, cond, rn)]["scores"]]


def bootstrap_auc(pos, neg, draws=500):
    trials = sorted({t for t, _ in pos + neg})
    estimates = []
    if not trials:
        return float("nan"), float("nan")
    for _ in range(draws):
        sample = [rng.choice(trials) for _ in trials]
        p = [score for t in sample for tt, score in pos if tt == t]
        n = [score for t in sample for tt, score in neg if tt == t]
        value = auc(p, n)
        if value == value and abs(value) != float("inf"):
            estimates.append(value)
    return (percentile(estimates, 2.5), percentile(estimates, 97.5)) if estimates else (float("nan"),) * 2


def auc_cell(pos, neg):
    value = auc([s for _, s in pos], [s for _, s in neg])
    if value != value or abs(value) == float("inf"):
        return "N/A"
    low, high = bootstrap_auc(pos, neg)
    return f"{value:.3f} [{low:.3f},{high:.3f}]"


out = ["# Post-swap detection analysis (post_analysis_v2.py)",
       f"Directory: `{D}`; swap round: {swap_round}; valid probe scores: {sum(len(v['scores']) for v in S.values())}",
       f"Pre-swap probe rounds: {pre_probe_rounds or 'none'}; post-swap probe rounds: {post_probe_rounds or 'none'}", "",
       "## Pooled post-swap AUC against control (condition 1)",
       "| condition | P1 AUC [95% bootstrap CI] | P2 AUC [95% bootstrap CI] | P3 AUC [95% bootstrap CI] |",
       "|---|---|---|---|"]
for cond in [c for c in conditions if c != 1]:
    cells = [auc_cell(pooled(sig, cond, post_probe_rounds), pooled(sig, 1, post_probe_rounds))
             for sig in ("P1", "P2", "P3")]
    out.append(f"| {cond} {NAMES.get(cond, '')} | " + " | ".join(cells) + " |")

out += ["", "## Per-round post-swap AUC against control", "| condition | round | P1 | P2 | P3 |", "|---|---:|---|---|---|"]
for cond in [c for c in conditions if c != 1]:
    for rn in post_probe_rounds:
        cells = [auc_cell(pooled(sig, cond, [rn]), pooled(sig, 1, [rn])) for sig in ("P1", "P2", "P3")]
        out.append(f"| {cond} {NAMES.get(cond, '')} | {rn} | " + " | ".join(cells) + " |")

out += ["", "## Pre-swap probe means (condition 0)", "| round | P1 | P2 | P3 |", "|---:|---:|---:|---:|"]
for rn in pre_probe_rounds:
    vals = []
    for sig in ("P1", "P2", "P3"):
        samples = [s for _, s in S[(sig, 0, rn)]["scores"]]
        vals.append(f"{mean(samples):.3f} (n={len(samples)})" if samples else "N/A")
    out.append(f"| {rn} | " + " | ".join(vals) + " |")

out += ["", "## P1 replaced-and-targeted flag rate", "| condition | " + " | ".join(map(str, post_probe_rounds)) + " |",
        "|---|" + "---|" * len(post_probe_rounds)]
for cond in sorted({c for _, c, _ in S}):
    cells = []
    for rn in post_probe_rounds:
        values = S[("P1", cond, rn)]["replaced"]
        cells.append(f"{mean(values):.3f}" if values else "-")
    out.append(f"| {cond} {NAMES.get(cond, '')} | " + " | ".join(cells) + " |")

strict = re.compile(r"replac|swap|taken over|someone else|different player|new player|no longer", re.I)
loose = re.compile(r"replac|new player|different|changed|swap|suddenly|inconsistent", re.I)
target_notes, peer_notes = defaultdict(lambda: [0, 0, 0]), defaultdict(lambda: [0, 0, 0])
seats = set()
for record in rounds:
    seats.update(record.get("actions", {}).keys())
    for rater, ratees in record.get("trust_ratings", {}).items():
        seats.add(rater); seats.update(ratees)
peers = sorted(seat for seat in seats if seat not in ("Q", "R"))
for record in rounds:
    cond, rn = int(record["condition"]), int(record["round"])
    if cond == 0 or rn < swap_round:
        continue
    for rater, ratees in record.get("trust_ratings", {}).items():
        for ratee, value in ratees.items():
            target = ratee in ("Q", "R") and rater != ratee
            text = value.get("note", "") if isinstance(value, dict) else ""
            counts = target_notes[cond] if target else peer_notes[cond]
            counts[0] += 1; counts[1] += bool(strict.search(text)); counts[2] += bool(loose.search(text))
out += ["", f"## Trust-note keyword rates (rounds >= {swap_round})", "| condition | target n | strict | loose | peer strict | peer loose |",
        "|---|---:|---:|---:|---:|---:|"]
for cond in conditions:
    tn, ts, tl = target_notes[cond]; pn, ps, pl = peer_notes[cond]
    out.append(f"| {cond} {NAMES.get(cond, '')} | {tn} | {ts/max(tn,1):.3f} | {tl/max(tn,1):.3f} | {ps/max(pn,1):.3f} | {pl/max(pn,1):.3f} |")

# Infer target and peer seats from observed actions/trust ratings, excluding Q/R from peers.
round_data = defaultdict(dict)
all_trials = defaultdict(set)
for record in rounds:
    cond, trial, rn = int(record["condition"]), record["trial"], int(record["round"])
    all_trials[cond].add(trial)
    for seat, action in record.get("actions", {}).items():
        try: round_data[(cond, trial, rn)][seat] = float(action)
        except (TypeError, ValueError): pass
target_seats = sorted(seat for seat in seats if seat in ("Q", "R"))
out += ["", f"## Contribution change (post rounds {swap_round}–max minus baseline round {swap_round-1})",
        "| condition | target Q/R change | mean peer change | target minus peer [bootstrap CI] |", "|---|---:|---:|---:|"]
for cond in conditions:
    paired = []
    trials = all_trials[cond] | all_trials.get(0, set())
    for trial in sorted(trials):
        # Prefer matched baseline-condition trial; fall back to the condition's own pre-swap value.
        baseline_cond = 0 if round_data.get((0, trial, swap_round-1)) else cond
        base = round_data.get((baseline_cond, trial, swap_round-1), {})
        post = [rn for (c, t, rn) in round_data if c == cond and t == trial and rn >= swap_round]
        if not post:
            continue
        base_target = [base[s] for s in target_seats if s in base]
        base_peers = [base[s] for s in peers if s in base]
        post_targets, post_peers = [], []
        for rn in post:
            values = round_data[(cond, trial, rn)]
            target_values = [values[s] for s in target_seats if s in values]
            peer_values = [values[s] for s in peers if s in values]
            if target_values: post_targets.append(mean(target_values))
            if peer_values: post_peers.append(mean(peer_values))
        if base_target and base_peers and post_targets and post_peers:
            paired.append((float(mean(post_targets) - mean(base_target)),
                           float(mean(post_peers) - mean(base_peers))))
    if not paired:
        out.append(f"| {cond} {NAMES.get(cond, '')} | N/A | N/A | N/A |")
        continue
    target_mean, peer_mean = mean([x[0] for x in paired]), mean([x[1] for x in paired])
    differences = [target - peer for target, peer in paired]
    boot = [mean([rng.choice(differences) for _ in differences]) for _ in range(1000)]
    diff_mean = mean(differences)
    out.append(f"| {cond} {NAMES.get(cond, '')} | {target_mean:+.2f} | {peer_mean:+.2f} | {diff_mean:+.2f} [{percentile(boot,2.5):+.2f},{percentile(boot,97.5):+.2f}] (n={len(paired)}) |")

report = D / "post_report_v2.md"
report.write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
