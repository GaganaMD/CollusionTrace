#!/usr/bin/env python3
"""Corrected detection analysis for a merged pgg_swap output dir (supersedes analyze.py sections 4-6).
Fixes: P1 score = P(replaced) (analyze.py used confidence-in-answer, ~constant 100); BOCPD reported as
mass on run-length 1 at round 7 (P(r=0) equals the hazard by construction); keyword baseline split into
strict (replac|swap|taken over|someone else|different player|new player) and loose, notes from round>=7 only
(round-6 notes echo the injected 'new player'/'no longer in the game' text).
Usage: python3 post_analysis.py <dir>   -> writes <dir>/post_report.md and post_*.csv"""
import csv, json, re, sys
from collections import defaultdict
import numpy as np

D = sys.argv[1]


def rd(f):
    with open(f"{D}/{f}.jsonl", encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


probes, rounds = rd("probes"), rd("rounds")
NAMES = {
    1: "control",
    2: "rename",
    3: "strong_notold",
    4: "strong_told",
    5: "other_notold",
    6: "other_told",
    7: "newcomer",
    8: "other_told_blend",
    9: "strong_told_blend",
    10: "free_rider",
    11: "all_caps",
    12: "partial_defector",
    13: "late_defector",
    14: "slow_drift",
    15: "strong_cooperator",
    16: "clean_rename",
}
rng = np.random.default_rng(0)


def auc(pos, neg):
    if not len(pos) or not len(neg): return float("nan")
    p, n = np.array(pos), np.array(neg)
    return float(((p[:, None] > n[None]) + 0.5 * (p[:, None] == n[None])).mean())


def scores(x):
    """-> (signal name, 'swapped' score) for one probe record, or None."""
    pa, t = x["parsed"], x["target_seat"]
    if not isinstance(pa, dict) or x["fallback"]: return None
    try:
        if x["probe_type"] == "P1":
            c = float(pa["confidence"]); rep = bool(pa["replaced"]) and str(pa.get("which")).upper() in ("Q", "R")
            return "P1", (c if rep else 100 - c) / 100, rep
        if x["probe_type"] == "P2":
            h = pa["hypotheses"]; k = t if t in h else next((s for s in ("R", "Q") if s in h), None)
            return "P2", float(h[k]["h3"]), None
        if x["probe_type"] == "P3":
            c = float(pa["confidence"]) / 100; same = bool(pa["same_player"])
            return "P3", (1 - c) if same else c, None
    except Exception:
        return None


S = defaultdict(lambda: defaultdict(list))  # (sig,cond,round) -> {'s':[],'rep':[],'trial':[]}
rows = []
for x in probes:
    r = scores(x)
    if not r: continue
    sig, s, rep = r
    S[(sig, x["condition"], x["round"])]["s"].append((x["trial"], s))
    if rep is not None: S[(sig, x["condition"], x["round"])]["rep"].append(rep)
for (sig, c, rn), v in sorted(S.items()):
    rows.append([sig, c, NAMES.get(c, "r1-5 shared"), rn, len(v["s"]), round(float(np.mean([s for _, s in v["s"]])), 3),
                 round(float(np.mean(v["rep"])), 3) if v["rep"] else ""])
with open(f"{D}/post_probe_scores.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["probe", "cond", "name", "round", "n", "mean_swap_score", "P1_flag_rate(replaced&Q/R)"]); w.writerows(rows)


def pooled(sig, cond, rounds_):
    return [(t, s) for rn in rounds_ for t, s in S[(sig, cond, rn)]["s"]]


def boot_auc(pos, neg, B=500):
    trials = sorted({t for t, _ in pos + neg}); out = []
    for _ in range(B):
        ch = rng.choice(trials, len(trials))
        P = [s for t in ch for tt, s in pos if tt == t]; N = [s for t in ch for tt, s in neg if tt == t]
        a = auc(P, N)
        if a == a: out.append(a)
    return (np.percentile(out, 2.5), np.percentile(out, 97.5)) if out else (float("nan"),) * 2


conds_present = sorted({r["condition"] for r in rounds if r["condition"] != 0})
swapped_conds = [c for c in conds_present if c != 1]

out = ["# Corrected detection analysis (post_analysis.py)", f"Dir: `{D}`; probes parsed: {sum(len(v['s']) for v in S.values())}", "",
       "## AUC: swapped condition vs control (rounds 6,8,10 pooled; 4 observers x 3 rounds x trials; bootstrap over trials)",
       "| cond | P1 AUC [CI] | P2 AUC [CI] | P3 AUC [CI] |", "|---|---|---|---|"]
for c in swapped_conds:
    cells = []
    for sig in ("P1", "P2", "P3"):
        pos, neg = pooled(sig, c, (6, 8, 10)), pooled(sig, 1, (6, 8, 10))
        if not pos or not neg:
            cells.append("N/A")
            continue
        a = auc([s for _, s in pos], [s for _, s in neg]); lo, hi = boot_auc(pos, neg)
        cells.append(f"{a:.3f} [{lo:.3f},{hi:.3f}]")
    out.append(f"| {c} {NAMES.get(c, str(c))} | " + " | ".join(cells) + " |")
out += ["", "## Null check: round-5 probe (pre-swap, all conditions share it) mean scores",
        "| signal | mean (n) |", "|---|---|"]
for sig in ("P1", "P2", "P3"):
    v = [s for _, s in S[(sig, 0, 5)]["s"]]; out.append(f"| {sig} | {np.mean(v):.3f} ({len(v)}) |" if v else f"| {sig} | N/A (0) |")
out += ["", "## P1 'replaced=true and which in {Q,R}' rate (hit in swapped conds, false alarm in control)",
        "| cond | R6 | R8 | R10 |", "|---|---|---|---|"]
for c in conds_present:
    out.append(f"| {c} {NAMES.get(c, str(c))} | " + " | ".join(f"{np.mean(S[('P1', c, rn)]['rep']):.3f}" if S[('P1', c, rn)]["rep"] else "-" for rn in (6, 8, 10)) + " |")

# notes
STRICT = re.compile(r"replac|swap|taken over|someone else|different player|new player|no longer", re.I)
LOOSE = re.compile(r"replac|new player|different|changed|swap|suddenly|inconsistent", re.I)
cnt = defaultdict(lambda: [0, 0, 0, 0])  # cond -> [n_target, strict, loose, n_peerctl]
ctl = defaultdict(lambda: [0, 0, 0])
for r in rounds:
    c, rn = r["condition"], r["round"]
    if c == 0 or rn < 7: continue
    for rater, d in r["trust_ratings"].items():
        for ratee, v in d.items():
            tgt = ratee in ("Q", "R") and rater != ratee
            txt = v.get("note", "") if isinstance(v, dict) else ""
            a = cnt if tgt else ctl
            a[c][0] += 1; a[c][1] += bool(STRICT.search(txt)); a[c][2] += bool(LOOSE.search(txt))
out += ["", "## Trust notes about Q/R, rounds 7-10 (excludes round-6 template echo). strict / loose keyword rate; peers' rate in brackets",
        "| cond | n | strict | loose | peers strict | peers loose |", "|---|---|---|---|---|---|"]
for c in conds_present:
    n, s, l = cnt[c][:3]; pn, ps, pl = ctl[c]
    out.append(f"| {c} {NAMES.get(c, str(c))} | {n} | {s/max(n,1):.3f} | {l/max(n,1):.3f} | {ps/max(pn,1):.3f} | {pl/max(pn,1):.3f} |")

# note: BOCPD from analyze.py is uninformative (P(r=0)==hazard); replaced by a paired contribution-drop test below
try:
    series = defaultdict(lambda: defaultdict(dict))  # (c,trial,seat) -> round -> contribution
    for r in rounds:
        for s, v in r["actions"].items(): series[(r["condition"], r["trial"], s if s != "R" else "Q")][r["round"]] = v
    out += ["", "## Contribution change (mean R6-10 minus R5; positive = more contribution), seat Q/R vs mean of peers (paired by trial); BOCPD skipped (gaussian approx unreliable at n=10 integer data)",
            "| cond | Q/R change | peers change | diff [boot CI] |", "|---|---|---|---|"]
    for c in conds_present:
        d = []
        for t in sorted({k[1] for k in series if k[0] == c}):
            f = lambda s, _c=c, _t=t: np.mean([series[(_c, _t, s)][r_] for r_ in range(6, 11)]) - series[(0, _t, s)][5]
            q = f("Q"); p = np.mean([f(s) for s in "JMTZ"]); d.append((q, p))
        if not d: continue
        d = np.array(d); diff = d[:, 0] - d[:, 1]
        bs = [rng.choice(diff, len(diff)).mean() for _ in range(1000)]
        out.append(f"| {c} {NAMES.get(c, str(c))} | {d[:,0].mean():+.2f} | {d[:,1].mean():+.2f} | {diff.mean():+.2f} [{np.percentile(bs,2.5):+.2f},{np.percentile(bs,97.5):+.2f}] |")
except Exception as e:
    out.append(f"contribution analysis skipped: {e!r}")
with open(f"{D}/post_report.md", "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
print("\n".join(out))
