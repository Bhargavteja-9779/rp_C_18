import pandas as pd, numpy as np
from scipy.stats import wilcoxon
rng=np.random.default_rng(0); rows=[]
for r in ("as10","as5","f2","u10"):
    u=pd.read_csv(f"results/abf_warm/{r}.csv").groupby("unit").mean(numeric_only=True); ps=[]; tmp=[]
    for b in ("W2_map_with_history","W5_cold_feedback","ABF_cold"):
        x=(u.ABF_warm-u[b]).values; lo,hi=np.percentile([np.median(rng.choice(x,len(x))) for _ in range(4000)],[2.5,97.5]); p=wilcoxon(x).pvalue; ps.append(p); tmp.append(dict(run=r,A="ABF_warm",B=b,n=len(x),mean_A=u.ABF_warm.mean(),mean_B=u[b].mean(),median_diff=np.median(x),ci_lo=lo,ci_hi=hi,p=p,A_higher=int((x>0).sum())))
    o=np.argsort(ps); h=np.zeros(3)
    for rk,i in enumerate(o): h[i]=(3-rk)*ps[i]
    hp=np.minimum(1,np.maximum.accumulate(h[o]))[np.argsort(o)]
    for i,t in enumerate(tmp): t["holm_p"]=hp[i]; rows.append(t)
pd.DataFrame(rows).to_csv("tables/abf_warm_statistics.csv",index=False); print(pd.DataFrame(rows).round(3)[["run","B","n","mean_A","mean_B","holm_p"]].to_string())
