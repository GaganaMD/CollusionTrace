"""Hero figure for the README: agents notice the move, miss the player (numbers from the sprint paper)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.3), gridspec_kw={"width_ratios": [1.25, 1]})
fig.subplots_adjust(left=0.245, right=0.965, top=0.78, bottom=0.2, wspace=0.62)

# Left: direct swap detection
rows = [("Diner's Dilemma · Gemini 3.5 Flash Lite", 0, 30, C[0]), ("Diner's Dilemma · Llama 4 Maverick", 0, 30, C[0]),
        ("Diner's Dilemma · cold swap (no memory)", 0, 30, C[0]), ("Diner's Dilemma · warned before the game", 3, 30, C[0]),
        ("Public Goods Game · silent model swaps", 0, 468, C[2]), ("RepeatedJira · covert monitor (episodes)", 0, 15, C[1])]
y = np.arange(len(rows))
for i, (lab, k, n, col) in enumerate(rows):
    a1.barh(i, max(k / n, 0.004), height=0.62, color=col)
    a1.text(k / n + 0.01, i, f"{k}/{n}", va="center", fontsize=9, color=INK)
a1.set_yticks(y); a1.set_yticklabels([r[0] for r in rows], fontsize=9); a1.invert_yaxis(); a1.set_xlim(0, 1)
a1.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); a1.grid(axis="x", color=GRID); a1.set_axisbelow(True); a1.tick_params(length=0)
a1.set_title("Missing the player: peers that report a swap", fontsize=10.5, color=INK, loc="right", weight="bold")

# Right: behaviour change detection (PGG continuity AUC)
pts = [("Free rider · 5 players", 0.915, 0.838, 0.974), ("Free rider · 3 players, table", 0.944, 0.880, 0.992),
       ("Free rider · 3 players, narrative", 0.984, 0.964, 1.0), ("Clean rename, same play · table", 0.637, 0.492, 0.739)]
for i, (lab, v, lo, hi) in enumerate(pts):
    col = C[2] if i < 3 else "#9a9893"
    a2.plot([lo, hi], [i, i], color=col, lw=2.2, solid_capstyle="round")
    a2.scatter([v], [i], s=70, color=col, zorder=3, edgecolor="white", linewidth=1.5)
    a2.text(hi + 0.012, i, f"{v:.3f}", va="center", fontsize=9, color=INK)
a2.axvline(0.5, color=INK2, ls="--", lw=1); a2.text(0.505, 3.55, "chance", fontsize=8, color=INK2)
a2.set_yticks(range(len(pts))); a2.set_yticklabels([p[0] for p in pts], fontsize=9); a2.invert_yaxis(); a2.set_xlim(0.4, 1.08)
a2.set_ylim(3.75, -0.5); a2.grid(axis="x", color=GRID); a2.set_axisbelow(True); a2.tick_params(length=0)
a2.set_xlabel("continuity-judgement AUC vs control (95% CI)")
a2.set_title("Noticing the move: free riders are flagged (PGG)", fontsize=10.5, color=INK, loc="right", weight="bold")

fig.text(0.01, 0.975, "Noticing the Move, Missing the Player", fontsize=15, weight="bold", color=INK, va="top")
fig.text(0.01, 0.915, "Across three games, LLM agents react to a peer's behaviour change but almost never conclude the peer was replaced.",
         fontsize=10, color=INK2, va="top")
fig.text(0.01, 0.025, "Left: Diner's Dilemma = probe answers naming a swap · PGG = correct direct replacement reports · RepeatedJira = swap episodes in which any agent mentioned a replacement.\n"
         "In RepeatedJira the remaining colluder did notice its partner stop cooperating (10–11 of 60 turns vs 1–5 in control), but blamed strategy, not a swap.",
         fontsize=8, color=INK2)
fig.savefig("hero_noticing_the_move.png", dpi=170)
print("ok")
