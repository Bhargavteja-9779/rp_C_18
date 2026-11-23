"""Choose ABF v2 options on the TUNING states only. Output results/abf_tuning.csv and results/abf_v2_config.json"""
import itertools, json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf
CFG={"as10":("data/processed/wells_as.csv","y10",3),"as5":("data/processed/wells_as.csv","y5",3),"u30":("data/processed/wells_u.csv","y30",3),"u10":("data/processed/wells_u.csv","y10",3),"f2":("data/processed/wells_f.csv","y2",2),"f4":("data/processed/wells_f.csv","y4",2)}
VARS=[dict(eta=e,hot=h,ext=x) for e in (0.5,1.0,2.0) for h in (False,True) for x in (False,True)]
def enr(y,o):
    c=E.curve_from_order(y,o); return E.found_at(c,len(y),0.2)/(0.2*y.sum())
def work(run,s,seed):
    data,label,_=CFG[run]; w=E.load(data,label); T=json.load(open(f"results/{run}/tuning.json")); idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values
    if y.sum()<5: return []
    coords=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]; p0=float(tr.y.mean()); p=E.fit_lgb(tr[E.FEATS],tr.y,T["params"],seed).predict_proba(te[E.FEATS])[:,1]
    return [dict(run=run,unit=s,seed=seed,vi=i,**v,enr20=enr(y,abf.abf_campaign(y,coords,p,p0,seed,"full",cfg=v))) for i,v in enumerate(VARS)]
jobs=[(r,s,sd) for r,(d,l,ns) in CFG.items() for s in json.load(open(f"results/{r}/tuning.json"))["tune_states"] for sd in range(ns)]
res=[x for rs in Parallel(n_jobs=4)(delayed(work)(*j) for j in jobs) for x in rs]; d=pd.DataFrame(res); d.to_csv("results/abf_tuning.csv",index=False)
g=d.groupby(["vi","eta","hot","ext","run"]).enr20.mean().reset_index(); sc=g.groupby(["vi","eta","hot","ext"]).enr20.mean().reset_index().sort_values("enr20",ascending=False); print(sc.round(3).to_string())
best=VARS[int(sc.iloc[0].vi)]; json.dump(best,open("results/abf_v2_config.json","w")); print("CHOSEN",best)
