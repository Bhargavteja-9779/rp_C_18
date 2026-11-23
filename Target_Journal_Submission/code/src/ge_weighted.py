"""Idea 1 (deviation 39): geographically weighted map training. Usage: ge_weighted.py data label tuning out seeds_start seeds_end"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E
data,label,tun,out,s0,s1=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]),int(sys.argv[6])
w=E.load(data,label); T=json.load(open(tun)); params=T["params"]; LS=(250.,500.,1000.,2000.)
def enr(y,o,f=0.2): c=E.curve_from_order(y,o); return E.found_at(c,len(y),f)/(f*y.sum())
def unit(s,seed):
    idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; tr=w[E.train_mask(w,idx)]; cx,cy=te.x.mean(),te.yk.mean()
    d=np.hypot(tr.x.values-cx,tr.yk.values-cy); r=dict(unit=s,seed=seed)
    r["unweighted"]=enr(y,np.argsort(-E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1],kind="stable"))
    for L in LS:
        wt=np.exp(-(d/L)**2); wt=wt/wt.mean(); r[f"L{int(L)}"]=enr(y,np.argsort(-E.fit_lgb(tr[E.FEATS],tr.y,params,seed,wt).predict_proba(te[E.FEATS])[:,1],kind="stable"))
    return r
res=Parallel(n_jobs=4)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(s0,s1))
d=pd.DataFrame(res); os.makedirs(os.path.dirname(out),exist_ok=True); d.to_csv(out,index=False); u=d.groupby("unit").mean(numeric_only=True).drop(columns="seed")
from scipy.stats import wilcoxon
rows=[dict(method="unweighted",mean=u.unweighted.mean())]
for L in LS:
    x=(u[f"L{int(L)}"]-u.unweighted).values; rows.append(dict(method=f"L{int(L)}",mean=u[f"L{int(L)}"].mean(),gain_mean=x.mean(),gain_median=float(np.median(x)),p=wilcoxon(x).pvalue,units_better=int((x>0).sum()),n=len(x)))
t=pd.DataFrame(rows); t["holm_p"]=np.minimum(1,t.p*len(LS)); t.to_csv(out.replace(".csv","_summary.csv"),index=False); print(out); print(t.round(3).to_string())
