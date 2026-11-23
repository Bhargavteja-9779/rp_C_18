"""RECHECK stage 8 (R3): try to make the feedback-vs-map gain disappear. Output results/recheck/statistician_attack.csv"""
import os, json, numpy as np, pandas as pd
from scipy.stats import wilcoxon, ttest_rel, binomtest
rng=np.random.default_rng(0); rows=[]
for run in ("as10","as5","u30","u10","f2","f4"):
    f=f"results/abf_{run}/abf.csv"
    if not os.path.exists(f): continue
    d=pd.read_csv(f); u=d.groupby(["method","unit"]).enr_20.mean().unstack(0); n=d[d.method=="M1_map"].groupby("unit").n.first()
    for a,b in (("M4_feedback","M1_map"),("ABF","M1_map")):
        x=(u[a]-u[b]); xv=x.values
        perm=np.mean([abs(np.mean(xv*rng.choice([-1,1],len(xv))))>=abs(xv.mean()) for _ in range(20000)])
        jack=[wilcoxon(x.drop(s)).pvalue for s in x.index]; big=x.drop(n.sort_values().index[-5:]); small=x.drop(n.sort_values().index[:5])
        per_seed=[wilcoxon(g.pivot(index="unit",columns="method",values="enr_20").eval(f"{a}-{b}")).pvalue for _,g in d.groupby("seed")]
        wavg=float(np.average(xv,weights=n.loc[x.index].values)); 
        rows.append(dict(outcome=run,comparison=f"{a} - {b}",n_states=len(x),mean_diff=xv.mean(),wilcoxon_p=wilcoxon(xv).pvalue,paired_t_p=ttest_rel(u[a],u[b]).pvalue,sign_test_p=binomtest(int((xv>0).sum()),int((xv!=0).sum()),0.5).pvalue,permutation_p=perm,
                         worst_jackknife_p=max(jack),p_without_5_largest_states=wilcoxon(big).pvalue,p_without_5_smallest_states=wilcoxon(small).pvalue,worst_single_seed_p=max(per_seed),well_weighted_mean_diff=wavg,states_positive=int((xv>0).sum())))
t=pd.DataFrame(rows); os.makedirs("results/recheck",exist_ok=True); t.to_csv("results/recheck/statistician_attack.csv",index=False); pd.set_option("display.width",250); print(t.round(4).to_string())
