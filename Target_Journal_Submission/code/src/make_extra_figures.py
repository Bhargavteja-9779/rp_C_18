import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
# Story figure (schematic, no data)
fig,ax=plt.subplots(figsize=(9,3.2)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,3.4)
def box(x,y,w,h,t,fc): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.05",fc=fc,ec="k",lw=.8)); ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=7.5)
box(0.1,1.2,2.0,1.4,"1. Problem\nAgency can test only\n~20% of private wells\nfor arsenic.\nWhich wells first?","#f2f2f2")
box(2.7,2.0,2.3,1.1,"2a. Static risk map\n(trained elsewhere)","#d9e6f2"); box(2.7,0.5,2.3,1.1,"2b. Feedback rule\n(follow unsafe results)","#fbe3c8")
box(5.6,1.2,1.9,1.4,"3. Test a batch\nof 10 wells,\nread results,\nre-rank the rest","#e4efd9")
box(8.0,1.2,1.9,1.4,"4. Score:\nunsafe wells found\nper 100 tests\n(vs random order)","#f2f2f2")
for a,b in [((2.15,1.9),(2.65,2.5)),((2.15,1.9),(2.65,1.05)),((5.05,2.5),(5.55,2.1)),((5.05,1.05),(5.55,1.7)),((7.55,1.9),(7.95,1.9))]: ax.add_patch(FancyArrowPatch(a,b,arrowstyle="->",mutation_scale=10,lw=1))
ax.add_patch(FancyArrowPatch((6.5,1.15),(6.5,0.45),arrowstyle="->",mutation_scale=10,lw=1,connectionstyle="arc3,rad=0")); ax.add_patch(FancyArrowPatch((6.5,0.45),(5.1,0.8),arrowstyle="->",mutation_scale=10,lw=1,ls="--"))
ax.text(6.55,0.3,"feedback loop",fontsize=7,ha="left")
plt.tight_layout(); plt.savefig("figures/fig_story.png",dpi=300); plt.close()
# kappa sweep
K=[0.5,2,10,50,200,1000]; fig,ax=plt.subplots(1,2,figsize=(8,3.2))
for a,(tag,tt) in zip(ax,[("as10","As > 10 µg/L"),("as5","As > 5 µg/L")]):
    u=pd.read_csv(f"results/extra_{tag}/sweep_heuristics.csv").groupby("unit").mean(numeric_only=True)
    m=[u[f"M5_kappa{k}"].mean() for k in K]; a.plot(range(len(K)),m,"o-",color="#e07a1f",label="Prior + feedback (M5)")
    a.axhline(u.M1.mean(),color="#2a6f97",ls="--",label="Static map (M1)"); a.axhline(u.H1_follow_unsafe.mean(),color="#6a994e",ls=":",label="Follow unsafe results only (H1)"); a.axhline(1,color="0.5",lw=.8)
    a.set_xticks(range(len(K))); a.set_xticklabels(K); a.set_xlabel("κ: weight given to the map"); a.set_title(tt,fontsize=9); a.set_ylabel("Enrichment at 20% budget" if tag=="as10" else "")
ax[0].legend(fontsize=6.5); plt.tight_layout(); plt.savefig("figures/fig_kappa_sweep.png",dpi=300); plt.close()
# warm start
names=["W1_map_outside_only","W2_map_with_history","W3_map_local_history_only","W5_cold_feedback","W6_history_prior_plus_feedback"]; lab=["Map from\nother states","Map: other states\n+ own history","Map: own\nhistory only","Feedback only\n(cold)","Own-history prior\n+ feedback"]
fig,ax=plt.subplots(1,2,figsize=(8.5,3.4),sharey=True)
for a,(tag,tt) in zip(ax,[("as10","As > 10 µg/L"),("as5","As > 5 µg/L")]):
    u=pd.read_csv(f"results/extra_{tag}/warm_start.csv").groupby("unit").mean(numeric_only=True); mu=[u[n].mean() for n in names]; se=[u[n].std()/np.sqrt(len(u)) for n in names]
    a.bar(range(5),mu,yerr=[1.96*s for s in se],color=["#999999","#c7a77b","#2a6f97","#e07a1f","#6a994e"],edgecolor="k",capsize=2); a.axhline(1,ls="--",color="k",lw=.8); a.set_xticks(range(5)); a.set_xticklabels(lab,fontsize=6); a.set_title(f"{tt} (n={len(u)} states)",fontsize=9)
ax[0].set_ylabel("Enrichment at 20% budget,\nlater half of each state's wells"); plt.tight_layout(); plt.savefig("figures/fig_warm_start.png",dpi=300); plt.close()
# mechanism
from scipy.stats import spearmanr
m=pd.read_csv("results/extra_as10/mechanism.csv").dropna(subset=["lift_20km"]); fig,ax=plt.subplots(figsize=(4.4,3.8)); ax.scatter(m.lift_20km,m.M4,s=18,color="#2a6f97"); r=spearmanr(m.lift_20km,m.M4)
for _,q in m.iterrows():
    if q.unit in ("MN","FL","WA","OH"): ax.annotate(q.unit,(q.lift_20km,q.M4),fontsize=7,xytext=(3,3),textcoords="offset points")
ax.axhline(1,ls="--",color="0.5"); ax.set_xlabel("Spatial clustering of unsafe wells\n(P(neighbour unsafe | unsafe) / prevalence, ≤20 km)",fontsize=8); ax.set_ylabel("Feedback enrichment at 20% budget",fontsize=8); ax.set_title(f"Spearman ρ = {r.statistic:.2f}, p = {r.pvalue:.3f} (n={len(m)})",fontsize=8); plt.tight_layout(); plt.savefig("figures/fig_mechanism.png",dpi=300); plt.close(); print("figs ok")
