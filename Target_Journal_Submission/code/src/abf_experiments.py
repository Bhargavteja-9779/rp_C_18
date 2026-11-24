"""Evaluate ABF against M1/M4/M5/H1 on the same states and seeds. Usage: abf_experiments.py <run> [quick]  (run in {as10,as5,u30,u10,f2,f4} optionally with suffix _geo / _env via WELL_FEATS)"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf
CFG={"as10":("data/processed/wells_as.csv","y10",5),"as5":("data/processed/wells_as.csv","y5",5),"u30":("data/processed/wells_u.csv","y30",5),"u10":("data/processed/wells_u.csv","y10",5),"f2":("data/processed/wells_f.csv","y2",3),"f4":("data/processed/wells_f.csv","y4",3),"n10":("data/processed/wells_n.csv","y10",3),"n5":("data/processed/wells_n.csv","y5",3)}
run=sys.argv[1]; quick=len(sys.argv)>2; tag=run; data,label,nseeds=CFG[run.split("_")[0]]
tdir=f"results/{run}"; DATA=os.environ.get("DATA",data); out=f"results/abf_{tag}"; os.makedirs(out,exist_ok=True)
w=E.load(DATA,label); T=json.load(open(f"{tdir}/tuning.json")); params=T["params"]; h,k=T["h_kappa"]
def enr(y,o):
    c=E.curve_from_order(y,o); n=len(y); return {f"enr_{b}":E.found_at(c,n,b/100)/(b/100*y.sum()) for b in (5,10,20,30)}
def hot(y,coords,hh,seed):
    n=len(y); rng=np.random.default_rng(seed); tested=np.zeros(n,bool); order=[]; a=np.zeros(n); b=rng.choice(n,min(10,n),replace=False)
    while True:
        for i in b: tested[i]=True; order.append(i)
        if len(order)>=n: break
        ti=np.array(b); d2=((coords[:,None,:]-coords[ti][None,:,:])**2).sum(-1); a+=np.exp(-d2/(2*hh*hh))@y[ti]
        b=np.argsort(-np.where(tested,-np.inf,a+1e-6*rng.random(n)))[:min(10,n-len(order))]
    return np.array(order)
def unit(s,seed):
    idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; coords=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]; p0=float(tr.y.mean())
    p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1]; rows=[]
    def rec(name,o,info=None): r=dict(unit=s,seed=seed,method=name,n=len(y),**enr(y,o)); r.update(info or {}); rows.append(r)
    rec("M1_map",np.argsort(-p,kind="stable")); rec("M4_feedback",E.campaign(y,coords,None,"adaptive",h,k,seed)); rec("M5_hybrid",E.campaign(y,coords,p,"adaptive",h,k,seed)); rec("H1_follow_unsafe",hot(y,coords,h,seed))
    o,i=abf.abf_campaign(y,coords,p,p0,seed,"full",return_info=True); rec("ABF",o,i)
    o,i=abf.abf_campaign(y,coords,None,p0,seed,"nomap",return_info=True); rec("ABF_nomap",o,i)
    o,i=abf.abf_campaign(y,coords,p,p0,seed,"fixedh",return_info=True); rec("ABF_fixed_h",o,i)
    return rows
states=T["eval_states"][:3] if quick else T["eval_states"]; seeds=1 if quick else nseeds
res=[x for rs in Parallel(n_jobs=4)(delayed(unit)(s,sd) for s in states for sd in range(seeds)) for x in rs]
d=pd.DataFrame(res); d.to_csv(f"{out}/abf.csv",index=False)
u=d.groupby(["method","unit"]).mean(numeric_only=True).reset_index(); m=u.pivot(index="unit",columns="method",values="enr_20")
print(run,"states",len(m)); print(m.mean().round(3).to_string())
inf=d[d.method=="ABF"]; print("ABF mean weights free/map/maponly:",inf[["w_free","w_map","w_maponly"]].mean().round(3).to_dict(),"| max regret nats",round(inf.regret_nats.max(),2),"vs ln N",round(inf.ln_N.iloc[0],2))
