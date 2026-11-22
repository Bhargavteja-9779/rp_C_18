"""Fairness check for M7: vary the weight on tested wells (1, 20, 100); 3 seeds; leave-state-out As>10. Output results/m7_weight_check.csv"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E
w=E.load("data/processed/wells_as.csv","y10"); T=json.load(open("results/as10/tuning.json"))
def one(s,wt,sd):
    E.TESTED_WEIGHT=wt; idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; tr=w[E.train_mask(w,idx)]
    o=E.campaign_refit(tr,te,T["params"],sd,y,te[E.FEATS]); cum=E.curve_from_order(y,o)
    return dict(unit=s,weight=wt,seed=sd,enr20=E.found_at(cum,len(y),0.2)/(0.2*y.sum()))
r=Parallel(n_jobs=4)(delayed(one)(s,wt,sd) for s in T["eval_states"] for wt in (1.0,20.0,100.0) for sd in range(3))
pd.DataFrame(r).to_csv("results/m7_weight_check.csv",index=False); print(pd.DataFrame(r).groupby("weight").enr20.mean())
