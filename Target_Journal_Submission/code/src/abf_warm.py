"""Warm start with ABF: earliest half of each state's wells (by date) = history; campaign on the later half. Usage: abf_warm.py <run>"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf
CFG={"as10":("data/processed/wells_as.csv","y10",3),"as5":("data/processed/wells_as.csv","y5",3),"u10":("data/processed/wells_u.csv","y10",3),"f2":("data/processed/wells_f.csv","y2",3)}
run=sys.argv[1]; data,label,ns=CFG[run]; w=E.load(data,label); T=json.load(open(f"results/{run}/tuning.json")); params=T["params"]; h,k=T["h_kappa"]
def enr(y,o): c=E.curve_from_order(y,o); return E.found_at(c,len(y),0.2)/(0.2*y.sum())
def unit(s,seed):
    te=w[w.state==s].sort_values("date"); half=len(te)//2; hist,new=te.iloc[:half],te.iloc[half:]
    if len(new)<100 or new.y.sum()<10: return None
    y=new.y.values; coords=new[["x","yk"]].values; outside=w[w.state!=s]; tr=pd.concat([outside,hist]); p0=float(tr.y.mean())
    p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(new[E.FEATS])[:,1]
    o1,i1=abf.abf_campaign(y,coords,p,p0,seed,"full",return_info=True,hist=(hist[["x","yk"]].values,hist.y.values.astype(float)))
    o2=abf.abf_campaign(y,coords,p,p0,seed,"full")
    return dict(unit=s,seed=seed,W2_map_with_history=enr(y,np.argsort(-p,kind="stable")),W5_cold_feedback=enr(y,E.campaign(y,coords,None,"adaptive",h,k,seed)),ABF_cold=enr(y,o2),ABF_warm=enr(y,o1),w_map=i1["w_map"]+i1["w_maponly"])
res=[r for r in Parallel(n_jobs=3)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(ns)) if r]
d=pd.DataFrame(res); os.makedirs("results/abf_warm",exist_ok=True); d.to_csv(f"results/abf_warm/{run}.csv",index=False); u=d.groupby("unit").mean(numeric_only=True); print(run,len(u)); print(u.mean().round(3).to_string())
