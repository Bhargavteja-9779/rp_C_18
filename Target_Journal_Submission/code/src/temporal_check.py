"""Pseudo-prospective check: train on other states' wells sampled before CUT; campaign on held-out state's wells sampled from CUT on."""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E
CUT=pd.Timestamp("2015-01-01"); w=E.load("data/processed/wells_as.csv","y10"); w["date"]=pd.to_datetime(w.date); T=json.load(open("results/as10/tuning.json")); h,k=T["h_kappa"]; params=T["params"]
def enr(y,o,f=0.2): c=E.curve_from_order(y,o); return E.found_at(c,len(y),f)/(f*y.sum())
def hot(y,coords,hh,seed):
    n=len(y); rng=np.random.default_rng(seed); tested=np.zeros(n,bool); order=[]; a=np.zeros(n); b=rng.choice(n,min(10,n),replace=False)
    while True:
        for i in b: tested[i]=True; order.append(i)
        if len(order)>=n: break
        ti=np.array(b); d2=((coords[:,None,:]-coords[ti][None,:,:])**2).sum(-1); a+=np.exp(-d2/(2*hh*hh))@y[ti]
        b=np.argsort(np.where(tested,-np.inf,a+1e-6*rng.random(n)))[::-1][:0] if False else np.argsort(-np.where(tested,-np.inf,a+1e-6*rng.random(n)))[:min(10,n-len(order))]
    return np.array(order)
def unit(s,seed):
    idx=w.index[(w.state==s)&(w.date>=CUT)].values
    if len(idx)<100 or w.loc[idx,"y"].sum()<10: return None
    te=w.loc[idx]; y=te.y.values; coords=te[["x","yk"]].values
    allidx=w.index[w.state==s].values; tr=w[E.train_mask(w,allidx)&(w.date<CUT)]
    p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1]
    return dict(unit=s,seed=seed,n=len(y),unsafe=int(y.sum()),M1=enr(y,np.argsort(-p,kind="stable")),M4=enr(y,E.campaign(y,coords,None,"adaptive",h,k,seed)),H1=enr(y,hot(y,coords,h,seed)))
res=[r for r in Parallel(n_jobs=3)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(3)) if r]
d=pd.DataFrame(res); os.makedirs("results/robust_checks",exist_ok=True); d.to_csv("results/robust_checks/temporal_cold_start.csv",index=False)
u=d.groupby("unit")[["M1","M4","H1"]].mean(); from scipy.stats import wilcoxon
out={"n_states":len(u),**{c+"_mean":float(u[c].mean()) for c in u},"M4_vs_M1_median_diff":float((u.M4-u.M1).median()),"M4_vs_M1_p":float(wilcoxon(u.M4-u.M1).pvalue),"M1_vs_random_p":float(wilcoxon(u.M1-1).pvalue),"M4_vs_random_p":float(wilcoxon(u.M4-1).pvalue)}
json.dump(out,open("results/robust_checks/temporal_cold_start.json","w"),indent=1); print(json.dumps(out,indent=1))
