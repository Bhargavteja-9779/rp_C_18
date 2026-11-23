"""RECHECK stage 5: deliberate leakage checks for the static map (arsenic > 10, base predictors).
(a) shuffled-label test: train on permuted labels -> held-out ROC-AUC should be ~0.5 and enrichment ~1.
(b) buffer sweep: 0, 5, 25, 100 km around the held-out state; if neighbours leaked, skill would rise as the buffer shrinks."""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.spatial import cKDTree
from sklearn.metrics import roc_auc_score
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E
w=E.load("data/processed/wells_as.csv","y10"); T=json.load(open("results/as10/tuning.json")); params=T["params"]
def enr(y,p,f=0.2): o=np.argsort(-p,kind="stable"); c=E.curve_from_order(y,o); return E.found_at(c,len(y),f)/(f*y.sum())
def mask(idx,km):
    if km==0: return ~w.index.isin(idx)                                   # no buffer: only exclude the state itself
    t=cKDTree(w.loc[idx,["x","yk"]].values); d,_=t.query(w[["x","yk"]].values,k=1); return d>km
def unit(s,seed):
    idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; rows=[]
    for km in (0,5,25,100):
        tr=w[mask(idx,km)]; p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1]
        rows.append(dict(unit=s,seed=seed,test=f"buffer_{km}km",auc=roc_auc_score(y,p),enr=enr(y,p),n_train=len(tr)))
    tr=w[mask(idx,25)]; yp=np.random.default_rng(seed).permutation(tr.y.values); m=E.fit_lgb(tr[E.FEATS],pd.Series(yp,index=tr.index),params,seed); p=m.predict_proba(te[E.FEATS])[:,1]
    rows.append(dict(unit=s,seed=seed,test="shuffled_labels",auc=roc_auc_score(y,p),enr=enr(y,p),n_train=len(tr)))
    return rows
res=[x for rs in Parallel(n_jobs=2)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(2)) for x in rs]
d=pd.DataFrame(res); os.makedirs("results/recheck",exist_ok=True); d.to_csv("results/recheck/leakage_checks.csv",index=False)
t=d.groupby("test").agg(mean_auc=("auc","mean"),mean_enr=("enr","mean"),n_states=("unit","nunique")).round(3); t.to_csv("results/recheck/leakage_checks_summary.csv"); print(t.to_string())
