"""Negative control (outcomes shuffled within state) and per-method timing. Output: results/extra_checks.json"""
import json, time, sys, os, numpy as np, pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E
w=E.load("data/processed/wells_as.csv","y10"); T=json.load(open("results/as10/tuning.json")); h,k=T["h_kappa"]; params=T["params"]
rng=np.random.default_rng(123); res=[]
for s in T["eval_states"]:
    te=w[w.state==s]; coords=te[["x","yk"]].values; y0=te.y.values
    for rep in range(5):
        y=rng.permutation(y0); o=E.campaign(y,coords,None,"adaptive",h,k,rep); cum=E.curve_from_order(y,o)
        res.append(E.found_at(cum,len(y),0.2)/(0.2*y.sum()))
out={"negative_control_M4_enrichment20_mean":float(np.mean(res)),"ci":[float(x) for x in np.percentile([np.mean(rng.choice(res,len(res))) for _ in range(2000)],[2.5,97.5])],"n_runs":len(res)}
st=max(T["eval_states"],key=lambda s:(w.state==s).sum()); idx=w.index[w.state==st].values; te=w.loc[idx]; y=te.y.values; coords=te[["x","yk"]].values
tr=w[E.train_mask(w,idx)]; tm={}
t=time.time(); m=E.fit_lgb(tr[E.FEATS],tr.y,params,0); p=m.predict_proba(te[E.FEATS])[:,1]; tm["M1_fit_and_score_s"]=time.time()-t
t=time.time(); E.campaign(y,coords,None,"adaptive",h,k,0); tm["M4_campaign_s"]=time.time()-t
t=time.time(); E.campaign(y,coords,p,"adaptive",h,k,0); tm["M5_campaign_s_excluding_prior_fit"]=time.time()-t
t=time.time(); E.campaign_refit(tr,te,params,0,y,te[E.FEATS]); tm["M7_online_refit_s"]=time.time()-t
out["timing_state"]=st; out["timing_n_wells"]=int(len(te)); out["timing_n_train"]=int(len(tr)); out["timing"]=tm
json.dump(out,open("results/extra_checks.json","w"),indent=1); print(json.dumps(out,indent=1))
