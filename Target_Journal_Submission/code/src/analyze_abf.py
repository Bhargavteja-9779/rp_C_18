"""Statistics for ABF vs other methods across outcomes. Output tables/abf_*.csv"""
import sys, numpy as np, pandas as pd
from scipy.stats import wilcoxon
rng=np.random.default_rng(0); runs=sys.argv[1:] or ["as10","as5","u30","u10","f2","f4"]
NAMES={"as10":"As>10 µg/L","as5":"As>5 µg/L","u30":"U>30 µg/L","u10":"U>10 µg/L","f2":"F>2 mg/L","f4":"F>4 mg/L"}
M=["M1_map","M4_feedback","M5_hybrid","H1_follow_unsafe","ABF","ABF_nomap","ABF_fixed_h"]; rows=[]; stats=[]; summ={}
for r in runs:
    d=pd.read_csv(f"results/abf_{r}/abf.csv"); u=d.groupby(["unit","method"]).enr_20.mean().unstack()[M]; summ[r]=u.mean()
    ci={m:np.percentile([rng.choice(u[m].values,len(u)).mean() for _ in range(4000)],[2.5,97.5]) for m in M}
    for m in M: rows.append(dict(run=r,outcome=NAMES.get(r,r),method=m,units=len(u),enr20=u[m].mean(),ci_lo=ci[m][0],ci_hi=ci[m][1]))
    comps=[("ABF","M1_map"),("ABF","M4_feedback"),("ABF","M5_hybrid"),("ABF","H1_follow_unsafe"),("ABF","ABF_nomap"),("ABF","ABF_fixed_h")]; p=[]
    for a,b in comps:
        x=(u[a]-u[b]).values; lo,hi=np.percentile([np.median(rng.choice(x,len(x))) for _ in range(4000)],[2.5,97.5]); p.append(wilcoxon(x).pvalue if np.any(x!=0) else 1.0)
        stats.append(dict(run=r,A=a,B=b,n=len(x),median_diff=np.median(x),ci_lo=lo,ci_hi=hi,p=p[-1],A_higher=int((x>0).sum())))
    o=np.argsort(p); m_=len(p); h=np.zeros(m_)
    for rk,i in enumerate(o): h[i]=(m_-rk)*p[i]
    hp=np.minimum(1,np.maximum.accumulate(h[o]))[np.argsort(o)]
    for i in range(m_): stats[-m_+i]["holm_p"]=hp[i]
pd.DataFrame(rows).to_csv("tables/abf_summary.csv",index=False); pd.DataFrame(stats).to_csv("tables/abf_statistics.csv",index=False)
S=pd.DataFrame(summ).T; best=S[["M1_map","M4_feedback","M5_hybrid","H1_follow_unsafe"]].max(axis=1)
reg=pd.DataFrame({m:(best-S[m]) for m in ["M1_map","M4_feedback","M5_hybrid","H1_follow_unsafe","ABF"]}); reg.loc["worst_case"]=reg.max(); reg.loc["mean"]=reg.iloc[:-1].mean()
reg.to_csv("tables/abf_regret_vs_best_fixed.csv"); print(S.round(3).to_string()); print(reg.round(3).to_string()); print(pd.DataFrame(stats)[lambda d:d.B.isin(["M4_feedback","M5_hybrid","H1_follow_unsafe","M1_map"])].round(3).to_string())
