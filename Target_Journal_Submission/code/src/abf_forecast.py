"""Idea 2 (deviation 40): calibrated remaining-yield forecast during an ABF campaign. Usage: abf_forecast.py run  (run in as10, as5, f2)"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf
CFG={"as10":("data/processed/wells_as.csv","y10",5),"as5":("data/processed/wells_as.csv","y5",5),"f2":("data/processed/wells_f.csv","y2",3)}
run=sys.argv[1]; data,label,nseeds=CFG[run]; w=E.load(data,label); T=json.load(open(f"results/{run}/tuning.json")); params=T["params"]
CPS=(0.10,0.20,0.30); Z=1.2816
def campaign_forecast(y,coords,prior,p0,seed,batch=10,cfg=abf.V1):
    """Same logic as abf.abf_campaign (variant 'full'); additionally records forecasts at checkpoints."""
    n=len(y); rng=np.random.default_rng(seed); ex=abf.make_experts("full",cfg); hs=sorted({e[1] for e in ex if e[1]})
    A={h:np.zeros(n) for h in hs}; B={h:np.zeros(n) for h in hs}; L=np.zeros(len(ex)); tested=np.zeros(n,bool); order=[]; pr=prior; eta=cfg["eta"]; fc={}; cps=[int(round(c*n)) for c in CPS]
    def preds(idx):
        P=np.empty((len(ex),len(idx)))
        for i,(typ,h,k) in enumerate(ex):
            if typ=="maponly": P[i]=pr[idx]
            elif typ=="hot": P[i]=p0+(1-p0)*(1-np.exp(-A[h][idx]))
            else:
                base=pr[idx] if typ=="map" else p0; P[i]=(k*base+A[h][idx])/(k+A[h][idx]+B[h][idx])
        return np.clip(P,1e-3,1-1e-3)
    b=np.argsort(-pr,kind="stable")[:batch]
    while True:
        P=preds(b); yb=y[b]; ll=(yb[None,:]*np.log(P)+(1-yb[None,:])*np.log(1-P)).sum(1); L+=-ll
        for i in b: tested[i]=True; order.append(i)
        if len(order)>=n: break
        d2=((coords[:,None,:]-coords[b][None,:,:])**2).sum(-1)
        for h in hs: K=np.exp(-d2/(2*h*h)); A[h]+=K@y[b]; B[h]+=K@(1-y[b])
        wts=np.exp(-eta*(L-L.min())); wts/=wts.sum(); un=np.where(~tested)[0]; s=(wts[:,None]*preds(un)).sum(0)
        for ci,c in zip(CPS,cps):
            if ci not in fc and len(order)>=c:
                found=float(y[tested].sum()); fc[ci]=dict(found=found,m=found+s.sum(),sd=float(np.sqrt((s*(1-s)).sum())),m_map=found+float(pr[un].sum()),m_naive=found/(len(order)/n))
        sc=np.full(n,-np.inf); sc[un]=s; b=np.argsort(-sc,kind="stable")[:min(batch,len(un))]
    return np.array(order),fc
def unit(s,seed):
    idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; coords=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]; p0=float(tr.y.mean())
    p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1]; o,fc=campaign_forecast(y,coords,p,p0,seed)
    o2=abf.abf_campaign(y,coords,p,p0,seed,"full"); assert (o==o2).all(),"forecast campaign differs from ABF campaign"      # same ordering as the main ABF code
    rows=[]; T_=float(y.sum())
    for ci,f in fc.items(): rows.append(dict(unit=s,seed=seed,cp=ci,truth=T_,**f))
    return rows
res=[x for rs in Parallel(n_jobs=4)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(nseeds)) for x in rs]
d=pd.DataFrame(res); os.makedirs("results/elevation",exist_ok=True); d.to_csv(f"results/elevation/forecast_{run}.csv",index=False)
for k in ("m","m_map","m_naive"): d[f"err_{k}"]=(d[k]-d.truth).abs()/d.truth
d["cover"]=((d.truth>=d.m-Z*d.sd)&(d.truth<=d.m+Z*d.sd)).astype(int); d["width_rel"]=2*Z*d.sd/d.truth
from scipy.stats import wilcoxon
rows=[]
for cp,g in d.groupby("cp"):
    u=g.groupby("unit")[["err_m","err_m_map","err_m_naive","cover","width_rel"]].mean()
    rows.append(dict(run=run,cp=cp,n_units=len(u),median_err_ABF=u.err_m.median(),median_err_map=u.err_m_map.median(),median_err_naive=u.err_m_naive.median(),
        p_vs_naive=wilcoxon(u.err_m-u.err_m_naive).pvalue,p_vs_map=wilcoxon(u.err_m-u.err_m_map).pvalue,coverage80=g.cover.mean(),median_width_rel=u.width_rel.median()))
t=pd.DataFrame(rows); t.to_csv(f"results/elevation/forecast_{run}_summary.csv",index=False); print(t.round(3).to_string())

# ---- item 41: conformal recalibration on the tuning states
def unit_calib(s,seed): return unit(s,seed)
cal=[x for rs in Parallel(n_jobs=4)(delayed(unit_calib)(s,sd) for s in T["tune_states"] for sd in range(nseeds)) for x in rs]
c=pd.DataFrame(cal); c["z"]=(c.truth-c.m).abs()/c.sd; mult=c.groupby("cp").z.quantile(0.8).to_dict()
d["mult"]=d.cp.map(mult); d["cover_cal"]=((d.truth>=d.m-d.mult*d.sd)&(d.truth<=d.m+d.mult*d.sd)).astype(int); d["width_cal_rel"]=2*d.mult*d.sd/d.truth
rows=[]
for cp,g in d.groupby("cp"):
    u=g.groupby("unit")[["width_cal_rel"]].median(); rows.append(dict(run=run,cp=cp,multiplier=mult[cp],n_calib_rows=int((c.cp==cp).sum()),n_units=len(u),coverage80_calibrated=g.cover_cal.mean(),median_rel_width=u.width_cal_rel.median()))
t2=pd.DataFrame(rows); t2.to_csv(f"results/elevation/forecast_{run}_calibrated.csv",index=False); print(t2.round(3).to_string())
