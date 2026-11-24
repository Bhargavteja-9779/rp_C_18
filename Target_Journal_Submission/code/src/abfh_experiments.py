"""Hierarchical ABF experiments (deviation 44). Usage: abfh_experiments.py <run> [batch]   run in as10, as5, u30, u10, f2, f4   (WELL_FEATS=base)"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf, abfh
CFG={"as10":("data/processed/wells_as.csv","y10",5),"as5":("data/processed/wells_as.csv","y5",5),"u30":("data/processed/wells_u.csv","y30",5),"u10":("data/processed/wells_u.csv","y10",5),"f2":("data/processed/wells_f.csv","y2",3),"f4":("data/processed/wells_f.csv","y4",3)}
run=sys.argv[1]; BATCH=int(sys.argv[2]) if len(sys.argv)>2 else 10; data,label,nseeds=CFG[run]
if BATCH!=10: nseeds=min(nseeds,3)
out=f"results/abfh_{run}"+("" if BATCH==10 else f"_b{BATCH}"); os.makedirs(out,exist_ok=True)
w=E.load(data,label); T=json.load(open(f"results/{run}/tuning.json")); params=T["params"]; EV=T["eval_states"]; TU=T["tune_states"]; ALL=EV+TU
TAUS=(0.1,0.3,1.0); NEXP=len(abf.make_experts("full"))
def enr(y,o,f=0.2): c=E.curve_from_order(y,o); return E.found_at(c,len(y),f)/(f*y.sum())
def prep(s,seed):
    idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; coords=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]; p0=float(tr.y.mean())
    p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1]; return y,coords,p,p0
def step1(s,seed):
    y,coords,p,p0=prep(s,seed); o,(Ld,nt)=abfh.abf_campaign_h(y,coords,p,p0,seed,batch=BATCH,return_loss=True); l=Ld/nt
    return dict(state=s,seed=seed,delta=(l-l.min()),enr_ABF=enr(y,o))
def step2(s,seed,delta_by_state,tau):
    donors=[v for k,v in delta_by_state.items() if k!=s]; db=np.mean(donors,axis=0); lp=abfh.prior_from_donors(db,tau); y,coords,p,p0=prep(s,seed)
    return dict(state=s,seed=seed,tau=tau,enr=enr(y,abfh.abf_campaign_h(y,coords,p,p0,seed,log_prior=lp,batch=BATCH)))
s1=Parallel(n_jobs=4)(delayed(step1)(s,sd) for s in ALL for sd in range(nseeds)); S1=pd.DataFrame([{k:v for k,v in r.items() if k!="delta"} for r in s1])
delta_by_state={s:np.mean([r["delta"] for r in s1 if r["state"]==s],axis=0) for s in ALL}
tu=Parallel(n_jobs=4)(delayed(step2)(s,sd,delta_by_state,t) for s in TU for sd in range(nseeds) for t in TAUS); TU_df=pd.DataFrame(tu)
base_tu=S1[S1.state.isin(TU)].enr_ABF.mean(); cand={0.0:base_tu,**{t:TU_df[TU_df.tau==t].enr.mean() for t in TAUS}}; tau_star=max(sorted(cand),key=lambda t:(cand[t],-t)); print(run,"batch",BATCH,"tau selection on tuning states:",{k:round(v,3) for k,v in cand.items()},"-> tau*",tau_star,flush=True)
ev=Parallel(n_jobs=4)(delayed(step2)(s,sd,delta_by_state,tau_star) for s in EV for sd in range(nseeds)); EV_df=pd.DataFrame(ev)
m=EV_df.groupby("state").enr.mean().rename("ABF_H").to_frame().join(S1[S1.state.isin(EV)].groupby("state").enr_ABF.mean().rename("ABF"))
ref=pd.read_csv(f"results/abf_{run}/abf.csv"); ref=ref.groupby(["method","unit"]).enr_20.mean().unstack(0)[["M1_map","M4_feedback","M5_hybrid","H1_follow_unsafe"]]; m=m.join(ref)
m.to_csv(f"{out}/per_state.csv"); json.dump(dict(run=run,batch=BATCH,tau_star=tau_star,tau_candidates=cand,n_seeds=nseeds,n_eval=len(EV),n_tune=len(TU)),open(f"{out}/meta.json","w"),indent=1)
from scipy.stats import wilcoxon
x=(m.ABF_H-m.ABF).values; best=m[["M1_map","M4_feedback","M5_hybrid","H1_follow_unsafe"]].max(axis=1)
res=dict(run=run,batch=BATCH,tau_star=tau_star,mean_ABF=m.ABF.mean(),mean_ABF_H=m.ABF_H.mean(),mean_gain=x.mean(),median_gain=float(np.median(x)),p=wilcoxon(x).pvalue if np.any(x!=0) else 1.0,states_better=int((x>0).sum()),n=len(x),
         gap_ABF=float((best-m.ABF).mean()),gap_ABF_H=float((best-m.ABF_H).mean()),worst_gap_ABF=float((best-m.ABF).max()) if False else float(((best-m.ABF).mean())),best_fixed_mean=m[["M1_map","M4_feedback","M5_hybrid","H1_follow_unsafe"]].mean().max())
pd.DataFrame([res]).to_csv(f"{out}/summary.csv",index=False); print(pd.DataFrame([res]).round(3).T.to_string())
