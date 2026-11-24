"""Real-campaign replay (deviation 43). Usage: campaign_replay.py <scenario>  scenario in as10, as5, f2, u10   (WELL_FEATS=base)"""
import glob, json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf
SC={"as10":("data/processed/wells_as.csv","y10","data/raw/as","Arsenic","ug/L","results/as10/tuning.json",5),"as5":("data/processed/wells_as.csv","y5","data/raw/as","Arsenic","ug/L","results/as5/tuning.json",5),
    "f2":("data/processed/wells_f.csv","y2","data/raw/f_all","Fluoride","mg/L","results/f2/tuning.json",3),"u10":("data/processed/wells_u.csv","y10","data/raw/u","Uranium","ug/L","results/u10/tuning.json",5),"n10":("data/processed/wells_n.csv","y10","data/raw/no3","Nitrate","mg/L","results/n10/tuning.json",3)}
BATCHSZ=int(os.environ.get("REPLAY_BATCH","10")); PROSP=os.environ.get("REPLAY_PROSPECTIVE","0")=="1"; SUF=("_prosp" if PROSP else "")+("" if BATCHSZ==10 else f"_b{BATCHSZ}")
sc=sys.argv[1]; data,label,rawdir,char,unit_,tun,nseeds=SC[sc]; os.makedirs("results/replay",exist_ok=True)
w=E.load(data,label); T=json.load(open(tun)); params=T["params"]; h,k=T["h_kappa"]
# campaign id of each well's earliest valid result (same ordering rule as build_dataset)
cols=["Location_Identifier","Org_Identifier","Project_Identifier","Location_Type","Activity_Media","Activity_StartDate","Result_Characteristic","Result_Measure","Result_MeasureUnit","Result_ResultDetectionCondition"]
parts=[]
for f in sorted(glob.glob(rawdir+"/*.csv")):
    try: d=pd.read_csv(f,usecols=lambda c:c in cols,dtype=str,low_memory=False)
    except Exception: continue
    d=d[(d.Location_Type=="Well")&(d.Activity_Media=="Water")&(d.Result_Characteristic==char)]; parts.append(d[["Location_Identifier","Org_Identifier","Project_Identifier","Activity_StartDate"]])
raw=pd.concat(parts); raw["date"]=pd.to_datetime(raw.Activity_StartDate,errors="coerce"); raw=raw.dropna(subset=["date"]).sort_values(["Location_Identifier","date"]).groupby("Location_Identifier").first().reset_index()
w=w.merge(raw[["Location_Identifier","Org_Identifier","Project_Identifier","date"]].rename(columns={"date":"d0"}),on="Location_Identifier",how="left")
w["camp"]=w.state+"|"+w.Org_Identifier.fillna("?")+"|"+w.Project_Identifier.fillna("?")
def campaigns(minw,minu,mind):
    g=w.dropna(subset=["d0"]).groupby("camp").agg(n=("y","size"),u=("y","sum"),dates=("d0","nunique"),state=("state","first")); return g[(g.n>=minw)&(g.u>=minu)&(g.dates>=mind)]
c=campaigns(100,10,30); rule="primary (>=100 wells, >=10 unsafe, >=30 dates)"
if len(c)<15: c=campaigns(60,8,20); rule="FALLBACK (>=60 wells, >=8 unsafe, >=20 dates)"
print(sc,rule,"campaigns:",len(c),"states:",c.state.nunique(),flush=True)
def enr(y,o,f): cu=E.curve_from_order(y,o); return E.found_at(cu,len(y),f)/(f*y.sum())
def hot(y,coords,hh,seed):
    BS=BATCHSZ; n=len(y); rng=np.random.default_rng(seed); tested=np.zeros(n,bool); order=[]; a=np.zeros(n); b=rng.choice(n,min(BS,n),replace=False)
    while True:
        for i in b: tested[i]=True; order.append(i)
        if len(order)>=n: break
        ti=np.array(b); d2=((coords[:,None,:]-coords[ti][None,:,:])**2).sum(-1); a+=np.exp(-d2/(2*hh*hh))@y[ti]
        b=np.argsort(-np.where(tested,-np.inf,a+1e-6*rng.random(n)))[:min(BS,n-len(order))]
    return np.array(order)
BUD=(0.05,0.10,0.20,0.30)
def state_seed(s,seed,camps):
    E.BATCH=BATCHSZ
    sidx=w.index[w.state==s].values; tr=w[E.train_mask(w,sidx)]; p0=float(tr.y.mean()); rows=[]; dropped=0
    trd=pd.to_datetime(tr.date,errors="coerce")
    if not PROSP:
        pm=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(w.loc[sidx,E.FEATS])[:,1]; pmap=pd.Series(pm,index=sidx)
    for cid in camps:
        te=w[w.camp==cid].dropna(subset=["d0"]); y=te.y.values; coords=te[["x","yk"]].values; rng=np.random.default_rng(seed)
        if PROSP:
            start=te.d0.min(); trc=tr[trd<start]
            if len(trc)<1000 or trc.y.sum()<50: dropped+=1; continue
            p=E.fit_lgb(trc[E.FEATS],trc.y,params,seed).predict_proba(te[E.FEATS])[:,1]; p0c=float(trc.y.mean())
        else: p=pmap.loc[te.index].values; p0c=p0
        real={b:np.mean([enr(y,np.lexsort((rng.random(len(y)),te.d0.values.astype("int64"))),b) for _ in range(20)]) for b in BUD}
        o_abf=abf.abf_campaign(y,coords,p,p0c,seed,"full",batch=BATCHSZ); o_m4=E.campaign(y,coords,None,"adaptive",h,k,seed); o_h1=hot(y,coords,h,seed); o_m1=np.argsort(-p,kind="stable")
        for b in BUD: rows.append(dict(scenario=sc,camp=cid,state=s,seed=seed,budget=b,n=len(y),unsafe=int(y.sum()),real=real[b],map=enr(y,o_m1,b),feedback=enr(y,o_m4,b),follow=enr(y,o_h1,b),ABF=enr(y,o_abf,b)))
    return rows+([dict(scenario=sc,camp="__dropped__",state=s,seed=seed,budget=-1,n=dropped)] if PROSP else [])
bystate={s:list(c.index[c.state==s]) for s in c.state.unique()}
res=[x for rs in Parallel(n_jobs=4)(delayed(state_seed)(s,sd,cl) for s,cl in bystate.items() for sd in range(nseeds if BATCHSZ==10 else min(nseeds,3))) for x in rs]
d=pd.DataFrame(res); dropped=int(d[d.camp=="__dropped__"].groupby("state").n.first().sum()) if (d.camp=="__dropped__").any() else 0; d=d[d.camp!="__dropped__"]; d.to_csv(f"results/replay/replay_{sc}{SUF}.csv",index=False); c=c[c.index.isin(d.camp.unique())]; json.dump(dict(scenario=sc,rule=rule,n_campaigns=int(len(c)),n_states=int(c.state.nunique()),dropped_campaigns=dropped,prospective=PROSP,batch=BATCHSZ),open(f"results/replay/replay_{sc}{SUF}_meta.json","w"))
from scipy.stats import wilcoxon
u=d[d.budget==0.2].groupby("camp")[["real","map","feedback","follow","ABF"]].mean(); rows=[dict(scenario=sc,rule=rule,n_campaigns=len(u),n_states=c.state.nunique(),real_median=u.real.median(),real_mean=u.real.mean(),map_mean=u["map"].mean(),feedback_mean=u.feedback.mean(),follow_mean=u.follow.mean(),ABF_mean=u.ABF.mean())]
t=pd.DataFrame(rows); pv={}
for m in ("map","feedback","follow","ABF"):
    x=(u[m]-u.real).values; pv[m]=(wilcoxon(x).pvalue,int((x>0).sum()),float(np.median(x)))
t["holm_base"]=0
for m,(p,nb,md) in pv.items(): t[f"{m}_vs_real_p"]=p; t[f"{m}_better_in"]=nb; t[f"{m}_median_diff"]=md
ps=sorted(v[0] for v in pv.values())
for m,(p,_,_) in pv.items(): t[f"{m}_vs_real_holm"]=min(1,p*(len(ps)-ps.index(p)))
ust=d[d.budget==0.2].groupby(["state","camp"])[["real","ABF"]].mean().groupby("state").mean(); t["state_level_ABF_minus_real_median"]=float((ust.ABF-ust.real).median()); t["states_ABF_better"]=int((ust.ABF>ust.real).sum()); t["n_state_units"]=len(ust)
t["dropped_campaigns"]=dropped; t.to_csv(f"results/replay/replay_{sc}{SUF}_summary.csv",index=False); print(t.round(3).T.to_string())
