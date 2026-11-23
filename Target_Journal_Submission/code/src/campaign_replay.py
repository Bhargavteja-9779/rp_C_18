"""Real-campaign replay (deviation 43). Usage: campaign_replay.py <scenario>  scenario in as10, as5, f2, u10   (WELL_FEATS=base)"""
import glob, json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf
SC={"as10":("data/processed/wells_as.csv","y10","data/raw/as","Arsenic","ug/L","results/as10/tuning.json",5),"as5":("data/processed/wells_as.csv","y5","data/raw/as","Arsenic","ug/L","results/as5/tuning.json",5),
    "f2":("data/processed/wells_f.csv","y2","data/raw/f_all","Fluoride","mg/L","results/f2/tuning.json",3),"u10":("data/processed/wells_u.csv","y10","data/raw/u","Uranium","ug/L","results/u10/tuning.json",5)}
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
    n=len(y); rng=np.random.default_rng(seed); tested=np.zeros(n,bool); order=[]; a=np.zeros(n); b=rng.choice(n,min(10,n),replace=False)
    while True:
        for i in b: tested[i]=True; order.append(i)
        if len(order)>=n: break
        ti=np.array(b); d2=((coords[:,None,:]-coords[ti][None,:,:])**2).sum(-1); a+=np.exp(-d2/(2*hh*hh))@y[ti]
        b=np.argsort(-np.where(tested,-np.inf,a+1e-6*rng.random(n)))[:min(10,n-len(order))]
    return np.array(order)
BUD=(0.05,0.10,0.20,0.30)
def state_seed(s,seed,camps):
    sidx=w.index[w.state==s].values; tr=w[E.train_mask(w,sidx)]; p0=float(tr.y.mean()); pm=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(w.loc[sidx,E.FEATS])[:,1]; pmap=pd.Series(pm,index=sidx); rows=[]
    for cid in camps:
        te=w[w.camp==cid]; te=te.dropna(subset=["d0"]); y=te.y.values; coords=te[["x","yk"]].values; p=pmap.loc[te.index].values; rng=np.random.default_rng(seed)
        real={b:np.mean([enr(y,np.lexsort((rng.random(len(y)),te.d0.values.astype("int64"))),b) for _ in range(20)]) for b in BUD}
        o_abf=abf.abf_campaign(y,coords,p,p0,seed,"full"); o_m4=E.campaign(y,coords,None,"adaptive",h,k,seed); o_h1=hot(y,coords,h,seed); o_m1=np.argsort(-p,kind="stable")
        for b in BUD: rows.append(dict(scenario=sc,camp=cid,state=s,seed=seed,budget=b,n=len(y),unsafe=int(y.sum()),real=real[b],map=enr(y,o_m1,b),feedback=enr(y,o_m4,b),follow=enr(y,o_h1,b),ABF=enr(y,o_abf,b)))
    return rows
bystate={s:list(c.index[c.state==s]) for s in c.state.unique()}
res=[x for rs in Parallel(n_jobs=4)(delayed(state_seed)(s,sd,cl) for s,cl in bystate.items() for sd in range(nseeds)) for x in rs]
d=pd.DataFrame(res); d.to_csv(f"results/replay/replay_{sc}.csv",index=False); json.dump(dict(scenario=sc,rule=rule,n_campaigns=int(len(c)),n_states=int(c.state.nunique())),open(f"results/replay/replay_{sc}_meta.json","w"))
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
t.to_csv(f"results/replay/replay_{sc}_summary.csv",index=False); print(t.round(3).T.to_string())
