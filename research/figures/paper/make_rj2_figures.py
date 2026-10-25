import csv, json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
INK,INK2,GRID="#0b0b0b","#52514e","#e6e5e0"
C=["#2a78d6","#eb6834","#1baf7a","#eda100"]
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.edgecolor":GRID,"axes.labelcolor":INK2,"xtick.color":INK2,"ytick.color":INK2,"axes.spines.top":False,"axes.spines.right":False})
S=list(csv.DictReader(open('/home/claude/ct/an/summary_by_cell.csv')))
models=["Qwen2.5-7B-Instruct","DeepSeek-R1-Distill-Qwen-7B","Qwen3-8B","Qwen3-32B"]
short={"Qwen2.5-7B-Instruct":"Qwen2.5-7B","DeepSeek-R1-Distill-Qwen-7B":"R1-Distill-7B","Qwen3-8B":"Qwen3-8B","Qwen3-32B":"Qwen3-32B"}
def frac(s):
    a,b=s.split('/'); return int(a)/int(b) if int(b) else np.nan
NOTE="Modal vLLM · 5 seeds per cell (instances differ by seed) · 4 rounds unless noted (W5/W6/W8: 10) · descriptive only"
def finish(fig,title,sub,path,note=NOTE):
    fig.text(0.01,0.975,title,fontsize=13,weight="bold",color=INK,va="top"); fig.text(0.01,0.925,sub,fontsize=9.5,color=INK2,va="top"); fig.text(0.01,0.012,note,fontsize=8,color=INK2); fig.savefig(path,dpi=170); plt.close(fig)

# Fig A: heatmap of capture-round rate, models x cells
cells=["W0_baseline","W1_payoff_table","W2_announce_rotation","W3_equal_priority","W4_self_objective","W5_long_horizon","W6_all_unlocked","W7_confederate","W8_confederate_all_unlocked","I1_goal_private","I2_plan_private","I3_plan_team_only"]
lab=["W0 baseline","W1 payoff table","W2 announce rotation","W3 equal priority","W4 self objective","W5 10 rounds","W6 all unlocked","W7 confederate","W8 confed. + all","I1 told: goal","I2 told: plan","I3 plan, public only"]
M=np.full((4,len(cells)),np.nan); T=[[""]*len(cells) for _ in models]
for r in S:
    m=r['model']
    if r['cell'] in cells:
        i=models.index(m); j=cells.index(r['cell']); M[i,j]=frac(r['capture_rounds']); T[i][j]=r['capture_rounds']
fig,ax=plt.subplots(figsize=(11,4.2)); fig.subplots_adjust(left=0.13,right=0.98,top=0.78,bottom=0.27)
cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b",["#f4f8fd","#2a78d6","#0d3a73"])
im=ax.imshow(M,cmap=cmap,vmin=0,vmax=1,aspect="auto")
for i in range(4):
    for j in range(len(cells)):
        if T[i][j]:
            ax.text(j,i,T[i][j],ha="center",va="center",fontsize=8.5,color="white" if (M[i,j]>0.55) else INK)
        else: ax.text(j,i,"–",ha="center",va="center",fontsize=9,color=INK2)
ax.set_yticks(range(4)); ax.set_yticklabels([short[m] for m in models]); ax.set_xticks(range(len(cells))); ax.set_xticklabels(lab,rotation=35,ha="right",fontsize=8.5)
ax.axvline(6.5,color="white",lw=3); ax.axvline(8.5,color=INK,lw=1.2)
ax.text(3,-0.85,"Direction 1: emergent (no instruction)",ha="center",fontsize=9,color=INK2); ax.text(7.5,-0.85,"scripted partner",ha="center",fontsize=9,color=INK2); ax.text(10,-0.85,"Direction 2: instructed",ha="center",fontsize=9,color=INK2)
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0)
cb=fig.colorbar(im,ax=ax,fraction=0.02,pad=0.01); cb.set_label("share of offer rounds",color=INK2); cb.outline.set_visible(False)
finish(fig,"Two-agent bonus grabs per offer round","Cell text = rounds with a paired grab / offer rounds. Emergent grabs are rare everywhere; told to collude, the Qwen3 models do it almost every round.","figA_capture_heatmap.png")

# Fig B: confederate repayment vs acceptance
fig,ax=plt.subplots(figsize=(8.5,4)); fig.subplots_adjust(left=0.18,right=0.97,top=0.76,bottom=0.2)
rows=[]
E=list(csv.DictReader(open('/home/claude/ct/an/episodes.csv')))
for m in models:
    for cell in ("W7_confederate","W8_confederate_all_unlocked"):
        es=[e for e in E if e['model']==([k for k in models if k==m][0] if m!="Qwen2.5-7B-Instruct" else "Qwen/Qwen2.5-7B-Instruct") or e['model'].endswith(m)]
        es=[e for e in E if e['model'].endswith(m) and e['cell']==cell]
        rep=sum(int(e['llm_repaid'] or 0) for e in es); asks=sum(int(e['conf_asks'] or 0) for e in es)
        used=sum(int(e['llm_took_premium_when_helped'] or 0) for e in es); offers=sum(int(e['offer_rounds'])-int(e['conf_asks'] or 0) for e in es)
        rows.append((m,cell,used,offers,rep,asks))
y=np.arange(4); h=0.36
for k,cell in enumerate(("W7_confederate","W8_confederate_all_unlocked")):
    rr=[r for r in rows if r[1]==cell]
    use=[r[2]/r[3] if r[3] else np.nan for r in rr]; rep=[r[4]/r[5] if r[5] else np.nan for r in rr]
    off=-h/2 if k==0 else h/2
    ax.barh(y+off-0.0, use, height=h*0.45, color=C[0] if k==0 else "#9ec2ee")
    ax.barh(y+off+h*0.47, rep, height=h*0.45, color=C[1] if k==0 else "#f6b89d")
    for i,r in enumerate(rr):
        if not r[3]:
            ax.text(0.01,y[i]+off+h*0.25,"(10-round cell not run for 32B)",va="center",fontsize=8,color=INK2); continue
        ax.text(use[i]+0.01,y[i]+off,f"{r[2]}/{r[3]}",va="center",fontsize=8,color=INK)
        ax.text(rep[i]+0.01,y[i]+off+h*0.47,f"{r[4]}/{r[5]}",va="center",fontsize=8,color=INK)
ax.set_yticks(y); ax.set_yticklabels([short[m] for m in models]); ax.set_xlim(0,1.12); ax.set_xlabel("share of rounds"); ax.set_ylim(3.62,-0.45); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
ax.grid(axis="x",color=GRID); ax.set_axisbelow(True); ax.tick_params(length=0)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=C[0],label="took the help (claimed bonus ticket) · 4 rounds"),Patch(color=C[1],label="repaid partner · 4 rounds"),Patch(color="#9ec2ee",label="took help · all unlocked, 10 rounds"),Patch(color="#f6b89d",label="repaid · all unlocked, 10 rounds")],loc="lower center",bbox_to_anchor=(0.42,-0.42),ncol=2,frameon=False,fontsize=8)
fig.subplots_adjust(bottom=0.3)
finish(fig,"With a partner who always helps first: accept, then repay?","Every model takes the help. Only Qwen2.5-7B repays; the reasoning models mostly keep their own cheaper ticket.","figB_confederate.png")

# Fig C: monitor TPR/FPR
conf=json.load(open('/home/claude/ct/an/monitor_confusion.json'))
def parse(s):
    if s=="n/a": return None
    k,n=s.split(" ")[0].split("/"); return int(k)/int(n), s.split(" ")[0]
sel=[("ALL","baseline","O0"),("ALL","baseline","O1"),("ALL","baseline","O2"),("ALL","Monitor-O1","O1"),("ALL","Monitor-1 (O2)","O2")]
labs=["Keyword baseline · O0","Keyword baseline · O1","Keyword baseline · O2","Monitor-O1 (public requests) · O1","Monitor-1 (ticket pattern) · O2"]
fig,ax=plt.subplots(figsize=(8.5,4.3)); fig.subplots_adjust(left=0.33,right=0.97,top=0.74,bottom=0.3)
y=np.arange(len(sel))
for i,(g,mn,l) in enumerate(sel):
    row=[c for c in conf if c[0]==g and c[1]==mn and c[2]==l][0]
    t=parse(row[3]); f=parse(row[4])
    ax.barh(i-0.18,t[0],height=0.34,color=C[0]); ax.text(t[0]+0.01,i-0.18,t[1],va="center",fontsize=8)
    ax.barh(i+0.18,f[0],height=0.34,color=C[1]); ax.text(f[0]+0.01,i+0.18,f[1],va="center",fontsize=8)
ax.set_yticks(y); ax.set_yticklabels(labs); ax.invert_yaxis(); ax.set_xlim(0,1.15); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.grid(axis="x",color=GRID); ax.set_axisbelow(True); ax.tick_params(length=0)
ax.legend(handles=[Patch(color=C[0],label="flags episodes with a paired grab (90)"),Patch(color=C[1],label="flags episodes without one (125)")],loc="lower center",bbox_to_anchor=(0.3,-0.38),ncol=2,frameon=False,fontsize=8.5)
finish(fig,"What each monitor catches, by observation level","Label = structural paired grab (provisional, not blinded human annotation).\nMonitor-1 reads the same ticket pattern the label encodes, so its score is near-tautological.","figC_monitors.png",note="All 215 episodes, all models and cells pooled. Monitor-O1 'false positives' are public bonus requests that nobody accepted.")
print("ok")
