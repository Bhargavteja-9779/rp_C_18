"""Consolidated tables and figures from machine-generated result files."""
import glob, os, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
runs={"As>10, leave-state-out":"as10","As>5, leave-state-out":"as5","As>10, spatial blocks":"as10_blocks","As>10, thinned to 1 km":"as10_thin","Nitrate>10, leave-state-out":"no3"}
M=["M1_static_lgbm","M3_static_knn","M4_neighbor_only","M5_proposed","M7_online_refit","A1_no_prior"]
rows=[]
for lab,r in runs.items():
    f=f"tables/summary_{r}.csv"
    if not os.path.exists(f): continue
    s=pd.read_csv(f,index_col=0); n=pd.read_csv(f"tables/per_state_enr20_{r}.csv").shape[0]
    for m in M: rows.append(dict(scenario=lab,units=n,method=m,enr20=s.loc[m,"enr_20_mean"],lo=s.loc[m,"enr_20_ci_lo"],hi=s.loc[m,"enr_20_ci_hi"]))
t=pd.DataFrame(rows); t.to_csv("tables/main_table.csv",index=False)
fig,ax=plt.subplots(figsize=(8,4)); sc=list(dict.fromkeys(t.scenario)); wd=0.8/len(M); cols=["#999999","#c7a77b","#2a6f97","#e07a1f","#6a994e","#7b2d8b"]
for j,m in enumerate(M):
    d=t[t.method==m].set_index("scenario").loc[sc]; ax.bar(np.arange(len(sc))+j*wd,d.enr20,wd,yerr=[d.enr20-d.lo,d.hi-d.enr20],color=cols[j],label=m.replace("_"," "),capsize=1.5,hatch=["","//","","\\\\","..","xx"][j],edgecolor="k",linewidth=.4)
ax.axhline(1,ls="--",color="k",lw=.8); ax.set_xticks(np.arange(len(sc))+wd*2.5); ax.set_xticklabels([s.replace(", ","\n") for s in sc],fontsize=7); ax.set_ylabel("Unsafe wells found at 20% budget\n(x random order, mean, 95% CI)")
ax.legend(fontsize=6,ncol=3,loc="upper left"); plt.tight_layout(); plt.savefig("figures/fig_generality.png",dpi=300); plt.close()
rv=pd.read_csv("results/as10/random_vs_blocked.csv").groupby("split").mean().drop(columns="seed"); rv.to_csv("tables/random_vs_blocked_summary.csv")
fig,ax=plt.subplots(1,3,figsize=(8,3))
for a,c,tt in zip(ax,["auc_roc","auc_pr","recall_at_20"],["ROC-AUC","PR-AUC","Recall at 20% tested"]):
    a.bar(["random\n5-fold","leave-state-\nout"],[rv.loc["random_5fold",c],rv.loc["leave_state_out",c]],color=["#999999","#2a6f97"],edgecolor="k"); a.set_title(tt,fontsize=9); a.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig("figures/fig_random_vs_blocked.png",dpi=300); plt.close()
for f in glob.glob("tables/fig_*as10.png"): os.replace(f,"figures/"+os.path.basename(f))
print(t.pivot(index="method",columns="scenario",values="enr20").round(2).to_string()); print(rv.round(3))
