"""ABF with larger testing rounds (late results). Usage: abf_batch.py <run>"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf
CFG={"as10":("data/processed/wells_as.csv","y10"),"f2":("data/processed/wells_f.csv","y2")}
run=sys.argv[1]; data,label=CFG[run]; w=E.load(data,label); T=json.load(open(f"results/{run}/tuning.json")); params=T["params"]
def enr(y,o): c=E.curve_from_order(y,o); return E.found_at(c,len(y),0.2)/(0.2*y.sum())
def unit(s,seed):
    idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; X=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]; p0=float(tr.y.mean())
    p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1]; r=dict(unit=s,seed=seed,M1=enr(y,np.argsort(-p,kind="stable")))
    for B in (10,50,200): r[f"ABF_batch{B}"]=enr(y,abf.abf_campaign(y,X,p,p0,seed,"full",batch=B))
    return r
res=Parallel(n_jobs=3)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(3)); d=pd.DataFrame(res); os.makedirs("results/robust_checks",exist_ok=True); d.to_csv(f"results/robust_checks/abf_batch_{run}.csv",index=False)
print(run,d.groupby("unit").mean(numeric_only=True).drop(columns="seed").mean().round(3).to_dict())
