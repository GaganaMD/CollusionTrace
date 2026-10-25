#!/usr/bin/env python3
"""Summarise outputs/pgg_swap/screen/*: Siva-style table (cooperative habit, commitment breaking, trust, parse rate).
Classes on the 0-5 contribution scale: Cooperative if mean contribution R3-4 >= 4.0 (80%), Selfish if <= 1.0 (20%).
"""
import csv, json, sys
from pathlib import Path
from statistics import mean

root = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs/pgg_swap/screen")
stated = lambda a: a["stated_action"] if isinstance(a, dict) else a
rows = []
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    st = json.loads((d / "status.json").read_text()) if (d / "status.json").exists() else {"phase": "?"}
    row = {"slug": d.name, "model": st.get("model", "?"), "gpu": st.get("gpu", "?"), "status": st.get("phase")}
    if (d / "rounds.jsonl").exists():
        R = [json.loads(l) for l in open(d / "rounds.jsonl")]
        R = [r for r in R if r["condition"] == 0 and r["round"] <= 5]
        if R:
            c34 = [a for r in R if r["round"] in (3, 4) for a in r["actions"].values()]
            call = [json.loads(l) for l in open(d / "calls.jsonl")]
            first = [c for c in call if c.get("attempt") == 0 and "parse_error" in c]
            by = {}
            for c in first:
                by.setdefault(c["stage"], []).append(not c["parse_error"])
            trust = []
            for r in R:
                for o, rat in r["trust_ratings"].items():
                    trust += [v["rating"] if isinstance(v, dict) else v for v in rat.values()]
            m = mean(c34)
            fb = json.loads((d / "run.json").read_text())["parse_failure_counts"]["fallbacks"] if (d / "run.json").exists() else "?"
            row.update(rounds=len(R), contrib_r34=round(m, 2), contrib_r15=round(mean(a for r in R for a in r["actions"].values()), 2),
                       cls="Cooperative" if m >= 4.0 else "Selfish" if m <= 1.0 else "In between",
                       broke=round(mean(abs(stated(r["announcements"][s]) - r["actions"][s]) >= 1 for r in R for s in r["actions"]), 2),
                       trust=round(mean(trust), 2), min_parse=round(min(mean(v) for v in by.values()), 2), fallbacks=fb)
    rows.append(row)
cols = ["slug", "gpu", "status", "contrib_r34", "cls", "contrib_r15", "broke", "trust", "min_parse", "fallbacks"]
rows.sort(key=lambda r: -(r.get("contrib_r34") or -1))
print("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols))
for r in rows:
    print("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
with open(root / "screen_summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r}))
    w.writeheader(); w.writerows(rows)
