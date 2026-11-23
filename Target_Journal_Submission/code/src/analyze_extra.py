"""Statistics for extra experiments. Usage: analyze_extra.py <extra_dir> <tag>"""
import sys, numpy as np, pandas as pd
from scipy.stats import wilcoxon, spearmanr
d_,tag=sys.argv[1],sys.argv[2]; rng=np.random.default_rng(0)
REG={"Northeast":"CT ME MA NH RI VT NJ NY PA","Midwest":"IL IN MI OH WI IA KS MN MO NE ND SD","South":"DE FL GA MD NC SC VA WV AL KY MS TN AR LA OK TX","West":"AZ CO ID MT NV NM UT WY OR WA ID"}
reg={s:r for r,v in REG.items() for s in v.split()}
def boot(x): return np.percentile([np.median(rng.choice(x,len(x))) for _ in range(10000)],[2.5,97.5])
def comp(u,pairs,name):
    rows=[]
    for a,b in pairs:
        x=(u[a]-(1.0 if b=="random" else u[b])).values; p=wilcoxon(x).pvalue; lo,hi=boot(x)
        rows.append(dict(A=a,B=b,n=len(x),median_diff=np.median(x),ci_lo=lo,ci_hi=hi,p=p,A_better=int((x>0).sum())))
    t=pd.DataFrame(rows); o=t.p.argsort().values; m=len(t); h=np.zeros(m); 
    for rank,i in enumerate(o): h[i]=(m-rank)*t.p[i]
    t["holm_p"]=np.minimum(1,np.maximum.accumulate(h[o]))[np.argsort(o)]; t.to_csv(f"tables/extra_{name}_{tag}.csv",index=False); return t
sw=pd.read_csv(f"{d_}/sweep_heuristics.csv"); u=sw.groupby("unit").mean(numeric_only=True).drop(columns=["seed","n"])
u.mean().round(3).to_csv(f"tables/extra_sweep_means_{tag}.csv")
t1=comp(u,[("H1_follow_unsafe","M4"),("H1_follow_unsafe","M1"),("H1_follow_unsafe","random"),("H2_spread","random"),("M5_kappa0.5","M5_kappa1000"),("M5_kappa0.5","M5_kappa10"),("M4","M5_kappa0.5")],"sweep"); print(t1.round(3).to_string())
m=pd.read_csv(f"{d_}/mechanism.csv"); rows=[]
for c in ("lift_2km","lift_5km","lift_20km"):
    ok=m[[c,"M4","gain_feedback_minus_static"]].dropna(); r1=spearmanr(ok[c],ok.M4); r2=spearmanr(ok[c],ok.gain_feedback_minus_static)
    rows.append(dict(measure=c,n=len(ok),rho_vs_feedback_enrichment=r1.statistic,p1=r1.pvalue,rho_vs_gain_over_static=r2.statistic,p2=r2.pvalue))
pd.DataFrame(rows).to_csv(f"tables/extra_mechanism_{tag}.csv",index=False); print(pd.DataFrame(rows).round(3).to_string())
wd=pd.read_csv(f"{d_}/warm_start.csv"); uw=wd.groupby("unit").mean(numeric_only=True).drop(columns=["seed","n_new"])
uw.mean().round(3).to_csv(f"tables/extra_warm_means_{tag}.csv")
t2=comp(uw,[("W2_map_with_history","W1_map_outside_only"),("W6_history_prior_plus_feedback","W2_map_with_history"),("W6_history_prior_plus_feedback","W5_cold_feedback"),("W2_map_with_history","W5_cold_feedback"),("W2_map_with_history","W3_map_local_history_only"),("W2_map_with_history","random"),("W5_cold_feedback","W1_map_outside_only")],"warm"); print(t2.round(3).to_string())
# regional consistency of feedback gain (cold start) from main results
main=pd.read_csv(f"tables/per_state_enr20_{tag}.csv",index_col=0); main["region"]=[reg.get(s,"West") for s in main.index]
r=main.assign(diff=main.M4_neighbor_only-main.M1_static_lgbm).groupby("region").agg(n=("diff","size"),median_diff=("diff","median"),states_positive=("diff",lambda x:int((x>0).sum()))); r.to_csv(f"tables/extra_regional_{tag}.csv"); print(r)
