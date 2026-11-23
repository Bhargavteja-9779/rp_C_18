"""Static-map learner robustness (deviation 36). Usage (env WELL_FEATS set by caller): learner_check.py data label tuning out seeds"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
data,label,tun,out,seeds=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5])
w=E.load(data,label); T=json.load(open(tun)); params=T["params"]; h,k=T["h_kappa"]
nom=[c for c in E.CATS if c in E.FEATS]; num=[c for c in E.FEATS if c not in nom]
def prep(): return ColumnTransformer([("n",StandardScaler(),num),("c",OneHotEncoder(min_frequency=50,handle_unknown="infrequent_if_exist",sparse_output=False),nom)])
def enr(y,o,f=0.2): c=E.curve_from_order(y,o); return E.found_at(c,len(y),f)/(f*y.sum())
def unit(s,seed):
    idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; coords=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]
    r=dict(unit=s,seed=seed)
    r["LightGBM"]=enr(y,np.argsort(-E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1],kind="stable"))
    for nm,mk in (("ExtraTrees",lambda:ExtraTreesClassifier(300,min_samples_leaf=5,n_jobs=1,random_state=seed)),
                  ("RandomForest",lambda:RandomForestClassifier(300,min_samples_leaf=5,class_weight="balanced_subsample",n_jobs=1,random_state=seed)),
                  ("Logistic",lambda:LogisticRegression(C=1.0,max_iter=500))):
        m=make_pipeline(prep(),mk()); m.fit(tr[E.FEATS],tr.y); r[nm]=enr(y,np.argsort(-m.predict_proba(te[E.FEATS])[:,1],kind="stable"))
    r["Kernel feedback (no map)"]=enr(y,E.campaign(y,coords,None,"adaptive",h,k,seed))
    return r
res=Parallel(n_jobs=4)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(seeds))
d=pd.DataFrame(res); os.makedirs(os.path.dirname(out),exist_ok=True); d.to_csv(out,index=False); u=d.groupby("unit").mean(numeric_only=True).drop(columns="seed")
from scipy.stats import wilcoxon
rows=[]
for c in ("LightGBM","ExtraTrees","RandomForest","Logistic"):
    x=(u["Kernel feedback (no map)"]-u[c]).values; rows.append(dict(learner=c,n_states=len(u),mean_enrichment=u[c].mean(),feedback_minus_learner_median=np.median(x),p=wilcoxon(x).pvalue,states_learner_better=int((x<0).sum()),vs_random_p=wilcoxon(u[c]-1).pvalue))
t=pd.DataFrame(rows); t["holm_p_vs_feedback"]=np.minimum(1,t.p*len(t)); t["feedback_mean"]=u["Kernel feedback (no map)"].mean(); t.to_csv(out.replace(".csv","_summary.csv"),index=False); print(out); print(t.round(3).to_string())
