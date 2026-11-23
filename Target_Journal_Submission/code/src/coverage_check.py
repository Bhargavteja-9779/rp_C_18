"""Distinct 5-km cells with >=1 unsafe well found at 20% tested, relative to random order. Usage: coverage_check.py <run>"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf
CFG={"as10":("data/processed/wells_as.csv","y10"),"f2":("data/processed/wells_f.csv","y2"),"as5":("data/processed/wells_as.csv","y5")}
run=sys.argv[1]; data,label=CFG[run]; w=E.load(data,label); T=json.load(open(f"results/{run}/tuning.json")); params=T["params"]; h,k=T["h_kappa"]
def hot(y,coords,hh,seed):
    n=len(y); rng=np.random.default_rng(seed); tested=np.zeros(n,bool); order=[]; a=np.zeros(n); b=rng.choice(n,min(10,n),replace=False)
    while True:
        for i in b: tested[i]=True; order.append(i)
        if len(order)>=n: break
        ti=np.array(b); d2=((coords[:,None,:]-coords[ti][None,:,:])**2).sum(-1); a+=np.exp(-d2/(2*hh*hh))@y[ti]
        b=np.argsort(-np.where(tested,-np.inf,a+1e-6*rng.random(n)))[:min(10,n-len(order))]
    return np.array(order)
def unit(s,seed):
    idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; X=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]; p0=float(tr.y.mean())
    cell=(np.floor(X[:,0]/5).astype(int).astype(str)+"_"+np.floor(X[:,1]/5).astype(int).astype(str)); k20=int(round(0.2*len(y)))
    def cells(o): sel=o[:k20]; return len(set(cell[sel][y[sel]==1]))
    p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1]; rng=np.random.default_rng(seed)
    rand=np.mean([cells(rng.permutation(len(y))) for _ in range(20)]); tot=len(set(cell[y==1]))
    r=dict(unit=s,seed=seed,total_cells=tot,random=rand,map=cells(np.argsort(-p,kind="stable")),feedback=cells(E.campaign(y,X,None,"adaptive",h,k,seed)),follow=cells(hot(y,X,h,seed)),ABF=cells(abf.abf_campaign(y,X,p,p0,seed,"full")))
    return r
res=Parallel(n_jobs=3)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(3)); d=pd.DataFrame(res); os.makedirs("results/robust_checks",exist_ok=True); d.to_csv(f"results/robust_checks/coverage_{run}.csv",index=False)
u=d.groupby("unit").mean(numeric_only=True); rel=u[["map","feedback","follow","ABF"]].div(u.random,axis=0); print(run,len(u),"mean distinct unsafe cells found / random:\n",rel.mean().round(3).to_string()); print("share of all unsafe cells found (random, ABF):",round((u.random/u.total_cells).mean(),3),round((u.ABF/u.total_cells).mean(),3))
