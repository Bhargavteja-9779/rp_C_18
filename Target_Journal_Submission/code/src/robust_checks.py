"""Robustness to delayed results (batch size), unavailable wells (30% hidden), and leave-one-region-out. Output results/robust_checks/*.csv"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E
os.makedirs("results/robust_checks",exist_ok=True)
w=E.load("data/processed/wells_as.csv","y10"); T=json.load(open("results/as10/tuning.json")); h,k=T["h_kappa"]; params=T["params"]
def enr(y,o,f=0.2): c=E.curve_from_order(y,o); return E.found_at(c,len(y),f)/(f*y.sum())
def hot(y,coords,hh,seed,batch):
    n=len(y); rng=np.random.default_rng(seed); tested=np.zeros(n,bool); order=[]; a=np.zeros(n); b=rng.choice(n,min(batch,n),replace=False)
    while True:
        for i in b: tested[i]=True; order.append(i)
        if len(order)>=n: break
        ti=np.array(b); d2=((coords[:,None,:]-coords[ti][None,:,:])**2).sum(-1); a+=np.exp(-d2/(2*hh*hh))@y[ti]
        s=np.where(tested,-np.inf,a+1e-6*rng.random(n)); b=np.argsort(-s)[:min(batch,n-len(order))]
    return np.array(order)
def unit(s,seed):
    idx=w.index[w.state==s].values; r=[]
    for avail in (1.0,0.7):
        rng=np.random.default_rng(1000+seed); keep=idx if avail==1.0 else rng.choice(idx,int(avail*len(idx)),replace=False)
        te=w.loc[keep]; y=te.y.values
        if y.sum()<5: continue
        coords=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]
        p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1]
        row=dict(unit=s,seed=seed,avail=avail,M1=enr(y,np.argsort(-p,kind="stable")))
        for B in (10,50,200):
            E.BATCH=B; row[f"M4_batch{B}"]=enr(y,E.campaign(y,coords,None,"adaptive",h,k,seed)); row[f"H1_batch{B}"]=enr(y,hot(y,coords,h,seed,B))
        E.BATCH=10; r.append(row)
    return r
res=[x for rs in Parallel(n_jobs=4)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(3)) for x in rs]
d=pd.DataFrame(res); d.to_csv("results/robust_checks/delay_availability.csv",index=False)
u=d.groupby(["avail","unit"]).mean(numeric_only=True).drop(columns="seed").groupby("avail").mean(); print(u.round(3).to_string()); u.to_csv("results/robust_checks/delay_availability_means.csv")
REG={"Northeast":"CT ME MA NH RI VT NJ NY PA","Midwest":"IL IN MI OH WI IA KS MN MO NE ND SD","South":"DE FL GA MD NC SC VA WV AL KY MS TN AR LA OK TX","West":"AZ CO ID MT NV NM UT WY OR WA"}
reg={s:r for r,v in REG.items() for s in v.split()}; p=pd.read_csv("tables/per_state_enr20_as10.csv",index_col=0); p["region"]=[reg.get(s,"West") for s in p.index]; p["diff"]=p.M4_neighbor_only-p.M1_static_lgbm
from scipy.stats import wilcoxon
rows=[dict(left_out="none",n=len(p),median_diff=p["diff"].median(),wilcoxon_p=wilcoxon(p["diff"]).pvalue)]
for r in REG: q=p[p.region!=r]; rows.append(dict(left_out=r,n=len(q),median_diff=q["diff"].median(),wilcoxon_p=wilcoxon(q["diff"]).pvalue))
t=pd.DataFrame(rows); t.to_csv("results/robust_checks/leave_one_region_out.csv",index=False); print(t.round(4).to_string())
