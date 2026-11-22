"""Statistics, tables and figures from results/<run>/raw_results.csv (no hand-typed numbers)."""
import sys, json, numpy as np, pandas as pd
from scipy.stats import wilcoxon
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
run,out=sys.argv[1],sys.argv[2]; tag=run.rstrip("/").split("/")[-1]
d=pd.read_csv(f"{run}/raw_results.csv")
for b in (5,10,20,30): d[f"enr_{b}"]=d[f"found_{b}"]/(b/100*d.n_unsafe)       # random order = 1.0 in expectation
u=d.groupby(["unit","method"]).agg(enr_5=("enr_5","mean"),enr_10=("enr_10","mean"),enr_20=("enr_20","mean"),enr_30=("enr_30","mean"),
    auc_curve=("auc_curve","mean"),n_wells=("n_wells","first"),n_unsafe=("n_unsafe","first"),auc_roc=("auc_roc","mean"),auc_pr=("auc_pr","mean")).reset_index()
piv=u.pivot(index="unit",columns="method",values="enr_20")
rng=np.random.default_rng(0)
def boot(x,B=10000): 
    m=[np.median(rng.choice(x,len(x))) for _ in range(B)]; return np.percentile(m,[2.5,97.5])
def rbc(x):  # rank-biserial from signed ranks
    x=x[x!=0]; 
    if len(x)==0: return 0.0
    r=pd.Series(np.abs(x)).rank().values; return float((r[x>0].sum()-r[x<0].sum())/r.sum())
comps=[("M5_proposed","M1_static_lgbm"),("M5_proposed","M4_neighbor_only"),("M5_proposed","M7_online_refit"),("M5_proposed","M6_thompson"),
       ("M5_proposed","A1_no_prior"),("M5_proposed","A2_no_shrinkage"),("M5_proposed","A3_fixed_bandwidth"),("M5_proposed","A4_knn_prior"),
       ("M1_static_lgbm","M3_static_knn"),("M1_static_lgbm","M2_static_logreg"),("M4_neighbor_only","M1_static_lgbm")]
rows=[]
for a,b in comps:
    x=(piv[a]-piv[b]).values; p=wilcoxon(x).pvalue if np.any(x!=0) else 1.0; lo,hi=boot(x)
    rows.append(dict(A=a,B=b,n_states=len(x),median_diff_enr20=np.median(x),ci_lo=lo,ci_hi=hi,wilcoxon_p=p,rank_biserial=rbc(x),states_A_better=int((x>0).sum())))
for m in ["M1_static_lgbm","M4_neighbor_only","M5_proposed"]:    # vs random order (enrichment = 1)
    x=(piv[m]-1).values; rows.append(dict(A=m,B="M0_random(=1)",n_states=len(x),median_diff_enr20=np.median(x),ci_lo=boot(x)[0],ci_hi=boot(x)[1],wilcoxon_p=wilcoxon(x).pvalue,rank_biserial=rbc(x),states_A_better=int((x>0).sum())))
s=pd.DataFrame(rows).sort_values("wilcoxon_p").reset_index(drop=True); m_=len(s)
s["holm_p"]=[min(1.0,(m_-i)*p) for i,p in enumerate(s.wilcoxon_p)]; s["holm_p"]=np.maximum.accumulate(s.holm_p.values)
s=s.sort_index(); s.to_csv(f"{out}/statistics_{tag}.csv",index=False)
summ=u.groupby("method").agg(enr_5=("enr_5","mean"),enr_10=("enr_10","mean"),enr_20_mean=("enr_20","mean"),enr_20_median=("enr_20","median"),enr_30=("enr_30","mean"),auc_curve=("auc_curve","mean"),auc_roc=("auc_roc","mean"),auc_pr=("auc_pr","mean")).round(3)
for m in summ.index: x=piv[m].values; summ.loc[m,"enr_20_ci_lo"],summ.loc[m,"enr_20_ci_hi"]=np.percentile([np.mean(rng.choice(x,len(x))) for _ in range(5000)],[2.5,97.5])
summ.to_csv(f"{out}/summary_{tag}.csv"); piv.to_csv(f"{out}/per_state_enr20_{tag}.csv")
# seed variability
sv=d.groupby(["method","seed"]).enr_20.mean().groupby("method").agg(["mean","std"]); sv.to_csv(f"{out}/seed_variability_{tag}.csv")
# efficiency headline in real units: unsafe wells found per 100 tests at 20% budget
d["per100"]=d.found_20/(0.2*d.n_wells)*100; d.groupby("method").per100.mean().to_csv(f"{out}/unsafe_per_100_tests_{tag}.csv")
# figures
order=["M0_random","M1_static_lgbm","M3_static_knn","M2_static_logreg","M4_neighbor_only","M5_proposed","M6_thompson","M7_online_refit"]
fig,ax=plt.subplots(figsize=(7.5,4)); 
for i,m in enumerate([o for o in order if o!="M0_random"]):
    x=piv[m].values; ax.scatter(np.full(len(x),i)+rng.uniform(-.15,.15,len(x)),x,s=12,alpha=.5,color="0.4"); ax.plot([i-.3,i+.3],[x.mean()]*2,color="k",lw=2)
ax.axhline(1,ls="--",color="0.5"); ax.set_xticks(range(len(order)-1)); ax.set_xticklabels(["M1\nstatic\nLightGBM","M3\nstatic\nkNN","M2\nstatic\nlogistic","M4\nfeedback\nonly","M5\nprior +\nfeedback","M6\nThompson","M7\nonline\nrefit"],fontsize=7)
ax.set_ylabel("Unsafe wells found at 20% budget\n(x random order)"); ax.set_title("Each dot = one US state (unseen at training)"); plt.tight_layout(); plt.savefig(f"{out}/fig_enrichment_{tag}.png",dpi=300); plt.close()
fig,ax=plt.subplots(figsize=(4.8,4.2)); ax.scatter(piv.M1_static_lgbm,piv.M5_proposed,s=18); lim=[0,max(piv.M5_proposed.max(),piv.M1_static_lgbm.max())*1.05]
ax.plot(lim,lim,"--",color="0.5"); ax.set_xlabel("Static map (M1)"); ax.set_ylabel("Prior + feedback (M5)"); ax.set_title("Enrichment at 20% budget, per state"); plt.tight_layout(); plt.savefig(f"{out}/fig_m5_vs_m1_{tag}.png",dpi=300); plt.close()
print(summ.to_string()); print(s.round(4).to_string())
