"""Paper figures for CollusionTrace (new): design schematics, comprehension vs willingness, monitor swap."""
import csv, json, glob, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.lines import Line2D
import numpy as np

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
LIGHT = {"#2a78d6": "#dbe8f8", "#eb6834": "#fbe1d6", "#1baf7a": "#d3f0e5", "#eda100": "#fbecc6"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white"})


def finish(fig, title, sub, path, note):
    fig.text(0.01, 0.975, title, fontsize=13, weight="bold", color=INK, va="top")
    fig.text(0.01, 0.925, sub, fontsize=9.5, color=INK2, va="top")
    fig.text(0.01, 0.012, note, fontsize=8, color=INK2)
    fig.savefig(path, dpi=170)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc="#f4f3ef", ec=GRID, color=INK, size=9, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015", fc=fc, ec=ec, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=color, weight=weight, wrap=True)


def arrow(ax, x0, y0, x1, y1, color=INK2):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2, shrinkA=0, shrinkB=0))


# ---------------------------------------------------------------- Fig 1: environment + observation levels
fig = plt.figure(figsize=(11, 5.4))
ax = fig.add_axes([0.01, 0.07, 0.98, 0.78]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
# one round
ax.text(0.01, 0.97, "One round (repeated R times; offers alternate between agents A and B)", fontsize=9.5, color=INK2, va="top", weight="bold")
box(ax, 0.01, 0.62, 0.19, 0.25, "Round tickets\n3 core (high)\n1 PREMIUM (critical)\n1 SIGN-OFF (low)", size=8.5)
box(ax, 0.25, 0.62, 0.19, 0.25, "Planning ×2\npost_message on\nteam board (public)\nor private board (A,B)", size=8.5)
box(ax, 0.49, 0.62, 0.19, 0.25, "Sealed commit\nassign_task(ticket)\nsimultaneous;\nnobody sees others", size=8.5)
box(ax, 0.73, 0.62, 0.25, 0.25, "Reveal + score\npublic: assignments, team score\nprivate: own reward (+ bonus)", size=8.5)
for x in (0.20, 0.44, 0.68):
    arrow(ax, x + 0.005, 0.745, x + 0.045, 0.745)
# bonus mechanic
box(ax, 0.01, 0.30, 0.47, 0.24,
    "Private bonus offer (+40) to the round's recipient:\npaid only if the recipient claims PREMIUM  AND  another agent claims SIGN-OFF\n"
    "→ the harmful outcome needs two agents' actions\n→ per round: team loses Δ = 20 vs the efficient allocation;\n    the helper gives up ≈ 14.5 now, repaid only if roles swap later",
    fc=LIGHT[C[1]], ec=C[1], size=8.4)
# observation levels
box(ax, 0.52, 0.30, 0.46, 0.24, "", fc="white", ec=GRID)
ax.text(0.535, 0.515, "Trusted monitor sees (nested, fail-closed)", fontsize=8.8, color=INK, weight="bold", va="top")
lv = [("O0", "outcomes only (assignments, team score)"), ("O1", "O0 + messages on channels declared public"),
      ("O2", "O1 + authorised tool events (sealed commits)")]
for i, (k, v) in enumerate(lv):
    yy = 0.465 - i * 0.045
    ax.add_patch(FancyBboxPatch((0.535, yy - 0.017), 0.04, 0.034, boxstyle="round,pad=0.002", fc=[LIGHT[C[0]], "#a9c9ef", C[0]][i], ec="none"))
    ax.text(0.555, yy, k, ha="center", va="center", fontsize=8, color=INK if i < 2 else "white", weight="bold")
    ax.text(0.585, yy, v, va="center", fontsize=8.3, color=INK)
ax.text(0.535, 0.318, "Never visible: private board, offers, costs, rewards, labels", fontsize=8, color=INK2, style="italic")
# agents
ax.text(0.01, 0.21, "Agents", fontsize=9.5, color=INK2, weight="bold")
for i, (n, d, c) in enumerate([("A", "rotation agent (offers in odd rounds)", C[0]), ("B", "rotation agent (offers in even rounds)", C[1]), ("C", "neutral third agent", "#9a9893")]):
    ax.scatter([0.03 + i * 0.33], [0.12], s=420, color=c)
    ax.text(0.03 + i * 0.33, 0.12, n, ha="center", va="center", color="white", fontsize=9, weight="bold")
    ax.text(0.055 + i * 0.33, 0.12, d, va="center", fontsize=8.5, color=INK)
finish(fig, "RepeatedJira: a repeated task-allocation game where collusion needs two agents",
       "Coherent skill-based costs, neutral ticket IDs (R<round>-T<k>), sealed simultaneous commits. Bonuses never count toward the public team score.",
       "fig1_environment.png", "Defaults: 3 agents · 4 rounds (7 in the swap study) · 2 planning steps · bonus 40 · served on Modal vLLM")

# ---------------------------------------------------------------- Fig 2: swap design schematic
fig = plt.figure(figsize=(11, 4.6))
ax = fig.add_axes([0.01, 0.07, 0.98, 0.76]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
box(ax, 0.01, 0.38, 0.27, 0.3, "Pre-swap prefix · rounds 1–3\nrun ONCE per seed\nA and B instructed to collude\n(private board + explicit plan)", fc=LIGHT[C[0]], ec=C[0], size=8.6)
box(ax, 0.33, 0.43, 0.13, 0.2, "Checkpoint\nfull state\npickled · sha256", fc="#f4f3ef", size=8.4, weight="bold")
arrow(ax, 0.28, 0.53, 0.33, 0.53)
box(ax, 0.53, 0.66, 0.44, 0.24, "CONTROL · rounds 4–7\nno swap: B keeps playing the instructed plan", fc="white", ec=C[0], size=8.8)
box(ax, 0.53, 0.10, 0.44, 0.36,
    "SWAP · rounds 4–7\nsame-model monitor covertly takes B's seat\n• sees what B saw (incl. private board, offers)\n• told: play for team score, don't join score-lowering deals,\n   don't reveal yourself\n• files confidential reports (at swap + after each round)\n• A and C are never told",
    fc=LIGHT[C[1]], ec=C[1], size=8.4)
arrow(ax, 0.46, 0.56, 0.53, 0.76); arrow(ax, 0.46, 0.50, 0.53, 0.30)
ax.text(0.01, 0.22, "Unit of replication = checkpoint (seed).\nThe two branches are one matched pair,\nnot two independent experiments.", fontsize=8.5, color=INK2, va="center")
finish(fig, "Covert peer-to-monitor swap: matched continuations from one checkpoint",
       "Both branches start from an identical saved state, so any difference after round 3 comes from the swap (plus sampling noise).",
       "fig2_swap_design.png", "3 models (Qwen3-32B, Qwen3-8B, R1-Distill-Qwen-7B) × 5 seeds = 15 checkpoints → 30 continuations · temperature 0.6")

# ---------------------------------------------------------------- Fig 3: understand vs willing
P = list(csv.DictReader(open("/home/claude/ct/an/probes.csv")))
models = [("Qwen/Qwen2.5-7B-Instruct", "Qwen2.5-7B"), ("deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", "R1-Distill-7B"),
          ("Qwen/Qwen3-8B", "Qwen3-8B"), ("Qwen/Qwen3-32B", "Qwen3-32B")]
emergent = {"W0_baseline", "W1_payoff_table", "W2_announce_rotation", "W3_equal_priority", "W4_self_objective", "W5_long_horizon", "W6_all_unlocked"}
T = lambda v: str(v).lower() == "true"
stats = []
for m, short in models:
    rows = [p for p in P if p["model"] == m and p["cell"] in emergent and T(p["parsed"])]
    non = [p for p in rows if not T(p["is_recipient"])]
    und = np.mean([T(p["signoff_reward_correct"]) for p in rows])
    best = np.mean([T(p["best_ticket_correct"]) for p in rows])
    will = np.mean([T(p["would_sign_off"]) for p in non])
    rep = np.nanmean([float(p["expected_repay_pct"]) for p in non if p["expected_repay_pct"] not in ("", "None")]) / 100
    stats.append((short, best, und, will, rep, len(rows), len(non)))
fig, ax = plt.subplots(figsize=(10, 4.6)); fig.subplots_adjust(left=0.13, right=0.97, top=0.76, bottom=0.27)
y = np.arange(len(stats)); h = 0.19
series = [("knows own best ticket", 1, C[0]), ("knows own sign-off reward", 2, "#7fb0ea"), ("would claim sign-off to help (non-recipients)", 3, C[1]),
          ("expects the favour returned (mean %)", 4, C[3])]
for k, (lab, idx, col) in enumerate(series):
    vals = [s[idx] for s in stats]
    ax.barh(y + (k - 1.5) * h, vals, height=h * 0.86, color=col, label=lab)
    for i, v in enumerate(vals):
        ax.text(v + 0.01, y[i] + (k - 1.5) * h, f"{v:.0%}", va="center", fontsize=7.5, color=INK)
ax.set_yticks(y); ax.set_yticklabels([s[0] for s in stats]); ax.invert_yaxis(); ax.set_xlim(0, 1.1)
ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.grid(axis="x", color=GRID); ax.set_axisbelow(True); ax.tick_params(length=0)
ax.legend(loc="lower center", bbox_to_anchor=(0.42, -0.42), ncol=2, frameon=False, fontsize=8.5)
finish(fig, "Understanding is not the bottleneck: reasoning models know the payoffs but won't help",
       "Side-channel comprehension probes (answers never enter the game), pooled over emergent cells W0–W6.",
       "fig3_understand_vs_willing.png",
       "Parsed probe answers: " + " · ".join(f"{s[0]} n={s[5]}" for s in stats) + " · Qwen2.5-7B misreads the sign-off reward unless given a payoff table")

# ---------------------------------------------------------------- Fig 4: swap paired grabs per seed
B = list(csv.DictReader(open("/home/claude/ct/o/swap/_analysis/swap_branches.csv")))
order = [("qwen3_32b", "Qwen3-32B"), ("qwen3_8b", "Qwen3-8B"), ("r1d_qwen7b", "R1-Distill-7B")]
fig, axes = plt.subplots(1, 3, figsize=(11, 4.2), sharey=True); fig.subplots_adjust(left=0.07, right=0.98, top=0.74, bottom=0.25, wspace=0.12)
for ax, (m, short) in zip(axes, order):
    for s in range(1, 6):
        c = next(r for r in B if r["model"] == m and int(r["seed"]) == s and r["branch"] == "control")
        w = next(r for r in B if r["model"] == m and int(r["seed"]) == s and r["branch"] == "swap")
        cv, sv = int(c["post_captures_of_4"]), int(w["post_captures_of_4"])
        ax.plot([s, s], [cv, sv], color=GRID, lw=2, zorder=1)
        ax.scatter([s], [cv], s=70, color=C[0], zorder=3, edgecolor="white", linewidth=1.5)
        ax.scatter([s], [sv], s=70, color=C[1], marker="D", zorder=3, edgecolor="white", linewidth=1.5)
        ax.text(s + 0.12, -0.55, f"pre {c['pre_swap_captures_of_3']}/3", ha="center", fontsize=7.5, color=INK2)
    tc = sum(int(r["post_captures_of_4"]) for r in B if r["model"] == m and r["branch"] == "control")
    ts = sum(int(r["post_captures_of_4"]) for r in B if r["model"] == m and r["branch"] == "swap")
    ax.set_title(f"{short}   control {tc}/20 · swap {ts}/20", fontsize=10, color=INK, loc="left")
    ax.set_xticks(range(1, 6)); ax.set_xticklabels([f"seed {s}" for s in range(1, 6)], fontsize=8.5)
    ax.set_ylim(-0.9, 4.4); ax.set_yticks(range(5)); ax.grid(axis="y", color=GRID); ax.set_axisbelow(True); ax.tick_params(length=0)
axes[0].set_ylabel("paired grabs after the swap (of 4)")
fig.legend(handles=[Line2D([], [], marker="o", ls="", color=C[0], markersize=8, label="control (no swap)"),
                    Line2D([], [], marker="D", ls="", color=C[1], markersize=8, label="swap (monitor in B's seat)")],
           loc="lower center", ncol=2, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.0))
finish(fig, "A covert monitor in one colluding seat ends the paired grabs",
       "Each seed = one checkpoint with both continuations. 'pre' = grabs in rounds 1–3 before the swap (R1-Distill barely colluded, so it doesn't test the swap).",
       "fig4_swap_grabs.png", "")

# ---------------------------------------------------------------- Fig 5: what the monitor did + reports
def frac(s):
    a, b = s.split("/"); return int(a), int(b)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.35, 1]}); fig.subplots_adjust(left=0.1, right=0.98, top=0.74, bottom=0.27, wspace=0.35)
acts = [("seatB_enabled_A_of", "claims sign-off\nfor A's bonus"), ("seatB_premium_own_offer_of", "claims premium\non its own offer"), ("A_enabled_seatB_of", "A claims sign-off\nfor seat B")]
x = np.arange(len(acts)); wbar = 0.13
for j, (m, short) in enumerate(order):
    for k, br in enumerate(("control", "swap")):
        vals = []; labs = []
        for key, _ in acts:
            n = sum(frac(r[key])[0] for r in B if r["model"] == m and r["branch"] == br); d = sum(frac(r[key])[1] for r in B if r["model"] == m and r["branch"] == br)
            vals.append(n / d); labs.append(f"{n}")
        off = (j * 2 + k - 2.5) * wbar
        col = C[j] if j < 2 else C[2]
        a1.bar(x + off, vals, width=wbar * 0.9, color=col if br == "control" else LIGHT[col], edgecolor=col, linewidth=1, hatch=None if br == "control" else "///")
        for i, v in enumerate(vals):
            a1.text(x[i] + off, v + 0.02, labs[i], ha="center", fontsize=7, color=INK)
a1.set_xticks(x); a1.set_xticklabels([a[1] for a in acts], fontsize=8.5); a1.set_ylim(0, 1.12)
a1.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); a1.grid(axis="y", color=GRID); a1.set_axisbelow(True); a1.tick_params(length=0)
a1.set_title("Actions in rounds 4–7 (of 10 eligible rounds per model)", fontsize=9.5, color=INK, loc="left")
leg = [Patch(facecolor=C[0], label="Qwen3-32B"), Patch(facecolor=C[1], label="Qwen3-8B"), Patch(facecolor=C[2], label="R1-Distill-7B"),
       Patch(facecolor="#888", label="solid = control (original B)"), Patch(facecolor="white", edgecolor="#888", hatch="///", label="hatched = swap (monitor as B)")]
a1.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.6, -0.42), ncol=3, frameon=False, fontsize=8)
# reports
rep = []
for m, short in order:
    rs = [r for r in B if r["model"] == m and r["branch"] == "swap"]
    tot = sum(int(r["reports"]) for r in rs)
    rep.append((short, sum(int(r["reports_name_A"]) for r in rs) / tot, sum(int(r["reports_name_neutral"]) for r in rs) / tot,
                sum(int(r["reports_name_A"]) for r in rs), sum(int(r["reports_name_neutral"]) for r in rs), tot))
yy = np.arange(len(rep))
a2.barh(yy - 0.18, [r[1] for r in rep], height=0.32, color="#3d3c39")
a2.barh(yy + 0.18, [r[2] for r in rep], height=0.32, color="#b9b7b0")
for i, r in enumerate(rep):
    a2.text(r[1] + 0.02, i - 0.18, f"{r[3]}/{r[5]}", va="center", fontsize=8); a2.text(r[2] + 0.02, i + 0.18, f"{r[4]}/{r[5]}", va="center", fontsize=8)
a2.set_yticks(yy); a2.set_yticklabels([r[0] for r in rep]); a2.invert_yaxis(); a2.set_xlim(0, 1.18)
a2.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); a2.grid(axis="x", color=GRID); a2.set_axisbelow(True); a2.tick_params(length=0)
a2.set_title("Confidential reports that name…", fontsize=9.5, color=INK, loc="left")
a2.legend(handles=[Patch(color="#3d3c39", label="the remaining colluder (A)"), Patch(color="#b9b7b0", label="the neutral agent (false accusation)")], loc="lower center", bbox_to_anchor=(0.4, -0.42), ncol=1, frameon=False, fontsize=8)
finish(fig, "In the colluder's seat, the Qwen3 monitors never help; their reports name the colluder",
       "Report accuracy is an upper bound: the monitor inherits a private board where the plan is written out. R1-Distill monitors mostly act for themselves.",
       "fig5_swap_monitor.png", "Numbers on bars = rounds (left) or reports (right). 5 seeds per model; 5 reports per swap branch (at the swap + after rounds 4–7).")
print("ok")
