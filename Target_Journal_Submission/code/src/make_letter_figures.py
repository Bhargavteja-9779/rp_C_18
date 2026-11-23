"""Figures for the Letter (main text) from result files."""
import os, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng=np.random.default_rng(0); C={"M1":"#999999","G":"#c7a77b","H1":"#6a994e","M4":"#2a6f97","M5":"#e07a1f","ABF":"#7b2d8b"}
plt.rcParams.update({"font.size":8,"axes.spines.top":False,"axes.spines.right":False})
def ci(x): return np.percentile([rng.choice(x,len(x)).mean() for _ in range(3000)],[2.5,97.5])
def panel(ax,run,title):
    d=pd.read_csv(f"results/abf_{run}/abf.csv"); u=d.groupby(["unit","method"]).enr_20.mean().unstack()
    meths=[("M1_map","Map from\nother states","M1"),("H1_follow_unsafe","Follow\nunsafe results","H1"),("M4_feedback","Kernel\nfeedback","M4"),("M5_hybrid","Map +\nfeedback","M5"),("ABF","ABF\n(adaptive)","ABF")]
    for i,(k,l,c) in enumerate(meths):
        m=u[k].mean(); lo,hi=ci(u[k].values); ax.bar(i,m,color=C[c],edgecolor="k",lw=.5); ax.errorbar(i,m,yerr=[[m-lo],[hi-m]],color="k",capsize=2,lw=.8)
    ax.axhline(1,ls="--",color="k",lw=.8); ax.set_xticks(range(len(meths))); ax.set_xticklabels([l for _,l,_ in meths],fontsize=6); ax.set_title(f"{title} ({len(u)} states)",fontsize=8); ax.set_ylim(0,3.1)
fig,ax=plt.subplots(1,2,figsize=(7.2,2.9),sharey=True); panel(ax[0],"as10","Arsenic > 10 µg/L"); panel(ax[1],"f2","Fluoride > 2 mg/L"); ax[0].set_ylabel("Unsafe wells found at 20% of wells tested\n(× random order; mean, 95% CI)")
plt.tight_layout(); plt.savefig("figures/letter_fig1.png",dpi=300); plt.close()
# Fig 2: mechanism, delay, warm start
fig,ax=plt.subplots(1,3,figsize=(7.4,2.6))
s=pd.read_csv("results/robust_checks/synthetic_mechanism.csv").groupby("L")[["M4","H1"]].agg(["mean","std"])
for c,col,lab in (("M4",C["M4"],"Kernel feedback"),("H1",C["H1"],"Follow unsafe")): ax[0].errorbar(s.index,s[c]["mean"],yerr=1.96*s[c]["std"]/np.sqrt(40),marker="o",ms=3,color=col,label=lab,capsize=1.5)
ax[0].set_xscale("log"); ax[0].axhline(1,ls="--",color="0.5",lw=.8); ax[0].set_xlabel("Spatial clustering of unsafe wells\n(correlation length, km)"); ax[0].set_ylabel("Enrichment at 20%"); ax[0].legend(fontsize=6); ax[0].set_title("a  Synthetic fields",fontsize=8,loc="left")
rb=pd.read_csv("results/robust_checks/delay_availability_means.csv",index_col=0).loc[1.0]; x=[10,50,200]
ab=pd.read_csv("results/robust_checks/abf_batch_as10.csv").groupby("unit").mean(numeric_only=True).mean(); ax[1].plot(x,[ab[f"ABF_batch{b}"] for b in x],"o-",color=C["ABF"],ms=3,label="ABF (adaptive)")
ax[1].plot(x,[rb[f"M4_batch{b}"] for b in x],"o-",color=C["M4"],ms=3,label="Kernel feedback"); ax[1].plot(x,[rb[f"H1_batch{b}"] for b in x],"o-",color=C["H1"],ms=3,label="Follow unsafe"); ax[1].axhline(rb["M1"],color=C["M1"],ls=":",label="Map from other states"); ax[1].axhline(1,ls="--",color="0.5",lw=.8)
ax[1].set_xscale("log"); ax[1].set_xticks(x); ax[1].set_xticklabels(x); ax[1].set_xlabel("Wells per testing round\n(late results = larger rounds)"); ax[1].legend(fontsize=6); ax[1].set_title("b  Late results",fontsize=8,loc="left")
wm=pd.read_csv("results/extra_as10/warm_start.csv").groupby("unit").mean(numeric_only=True); names=[("W1_map_outside_only","Map,\nother\nstates",C["M1"]),("W2_map_with_history","Map +\nown\nhistory",C["G"]),("W5_cold_feedback","Feedback\nonly",C["M4"]),("W6_history_prior_plus_feedback","History\n+ feed-\nback",C["ABF"])]
for i,(k,l,c) in enumerate(names): m=wm[k].mean(); lo,hi=ci(wm[k].values); ax[2].bar(i,m,color=c,edgecolor="k",lw=.5); ax[2].errorbar(i,m,yerr=[[m-lo],[hi-m]],color="k",capsize=2,lw=.8)
ax[2].axhline(1,ls="--",color="0.5",lw=.8); ax[2].set_xticks(range(4)); ax[2].set_xticklabels([l for _,l,_ in names],fontsize=6); ax[2].set_title("c  A state's own earlier wells (As)",fontsize=8,loc="left")
plt.tight_layout(); plt.savefig("figures/letter_fig2.png",dpi=300); plt.close(); print("letter figs 1-2 ok")
# Fig 3: static-map ladder vs feedback
import os
rows=[("As>10","as10"),("As>5","as5"),("U>10","u10"),("F>2","f2")]; sets=[("","Coordinates\n+ aquifer","#999999"),("_geo","+ geology","#c7a77b"),("_env","+ climate,\nelevation","#a1887f"),("_envnc","Environment only\n(no coordinates)","#6d4c41")]
fig,ax=plt.subplots(1,4,figsize=(7.4,2.6),sharey=True)
for a,(lab,r) in zip(ax,rows):
    for i,(sfx,l,c) in enumerate(sets):
        fn=f"tables/summary_{r}{sfx}.csv"
        if not os.path.exists(fn): continue
        sm=pd.read_csv(fn,index_col=0); m=sm.loc["M1_static_lgbm","enr_20_mean"]; lo,hi=sm.loc["M1_static_lgbm","enr_20_ci_lo"],sm.loc["M1_static_lgbm","enr_20_ci_hi"]
        a.bar(i,m,color=c,edgecolor="k",lw=.5); a.errorbar(i,m,yerr=[[m-lo],[hi-m]],color="k",capsize=2,lw=.8)
    fb=pd.read_csv(f"tables/summary_{r}.csv",index_col=0).loc["M4_neighbor_only","enr_20_mean"]; a.axhline(fb,color=C["M4"],lw=1.5,label="Kernel feedback"); a.axhline(1,ls="--",color="0.4",lw=.8)
    a.set_title(lab,fontsize=8); a.set_xticks(range(4)); a.set_xticklabels(["Coord.","+Geol.","+Clim.","Env.\nonly"],fontsize=6)
ax[0].set_ylabel("Static-map enrichment at 20%\n(× random order)"); ax[0].legend(fontsize=6,loc="upper left"); plt.tight_layout(); plt.savefig("figures/letter_fig3.png",dpi=300); plt.close(); print("fig3 ok")
