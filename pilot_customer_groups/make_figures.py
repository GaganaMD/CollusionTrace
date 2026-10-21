"""Figures from analysis/results*.json and the raw rounds. Run: python make_figures.py -> figures/*.png"""
import glob, json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

H = Path(__file__).parent
R = {k: json.load(open(H / f"analysis/results{v}.json")) for k, v in (("starter", ""), ("goal", "_goal"))}
(H / "figures").mkdir(exist_ok=True)
sns.set_theme(style="whitegrid", context="talk")

# 1. aggregate markup by condition
d = pd.DataFrame([(c, p, R[p]["aggregate_markup"][c]["est"]) for p in R for c in ("M", "D0", "DC")], columns=["cond", "prompt", "markup"])
d = d[~((d.prompt == "goal") & (d.cond == "M"))]  # goal prompt has no M run
sns.barplot(d, x="cond", y="markup", hue="prompt")
plt.ylabel("aggregate markup"); plt.tight_layout(); plt.savefig(H / "figures/fig1_markup_by_condition.png", dpi=150); plt.close()

# 2. mean quote per 10-round block
rows = []
for p, suf in (("starter", ""), ("goal", "_goal")):
    for c in ("D0", "DC"):
        for r in map(json.loads, open(glob.glob(str(H / f"outputs/*_agents/*_main_{c}_s1{suf}/rounds.jsonl"))[0])):
            rows.append((p, c, (r["round"] - 1) // 10, np.mean([x for q in r["quotes"].values() for x in q])))
d = pd.DataFrame(rows, columns=["prompt", "cond", "block", "quote"]).groupby(["prompt", "cond", "block"]).quote.mean().reset_index()
d["block"] = d.block * 10 + 5
sns.lineplot(d, x="block", y="quote", hue="prompt", style="cond", marker="o")
plt.axhline(10, color="gray", ls=":"); plt.xlabel("round (block mid)"); plt.ylabel("mean quote ($)"); plt.tight_layout()
plt.savefig(H / "figures/fig2_price_trajectory.png", dpi=150); plt.close()

# 3. group gaps vs reference level, M (starter) vs DC (goal)
d = pd.DataFrame([(k, c, v["est"], v["lo"], v["hi"]) for c, g in (("M", R["starter"]["gaps"]["M"]), ("DC", R["goal"]["gaps"]["DC"])) for k, v in g.items()],
                 columns=["contrast", "cond", "est", "lo", "hi"])
fig, ax = plt.subplots(figsize=(9, 7))
for i, (c, off) in enumerate((("M", -.15), ("DC", .15))):
    s = d[d.cond == c].reset_index(drop=True); y = np.arange(len(s)) + off
    ax.errorbar(s.est, y, xerr=[s.est - s.lo, s.hi - s.est], fmt="o", color=sns.color_palette()[i], label={"M": "M (starter)", "DC": "DC (goal)"}[c], capsize=3)
ax.axvspan(-.1, .1, color="gray", alpha=.15); ax.set_yticks(range(9)); ax.set_yticklabels(s.contrast); ax.invert_yaxis()
ax.set_xlabel("markup gap vs reference (95% CI), band = threshold"); ax.legend(); plt.tight_layout()
plt.savefig(H / "figures/fig3_group_gaps.png", dpi=150); plt.close()

# 4. markup by age level, monopoly
m = R["starter"]["gaps"]["M"]["age:child10-adult45"]["level_means"]
sns.barplot(x=["adult 45", "child 10", "young 24", "senior 68"], y=m, color=sns.color_palette()[0])
plt.ylabel("markup (M)"); plt.tight_layout(); plt.savefig(H / "figures/fig4_age_markup_monopoly.png", dpi=150); plt.close()
