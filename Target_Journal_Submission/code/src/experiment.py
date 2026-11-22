"""Well-testing campaign experiments (see experiments/protocol.md and deviations.md)."""
import argparse, json, os, sys, time, warnings
import numpy as np, pandas as pd, lightgbm as lgb
from scipy.spatial import cKDTree
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score
from joblib import Parallel, delayed
warnings.filterwarnings("ignore")
BUDGETS=[0.05,0.10,0.20,0.30]; BATCH=10; BUF_KM=25.0
BW_GRID=[2,5,10,20,50]; KAPPA_GRID=[0.5,1,2,5,10]

def load(path,label):
    w=pd.read_csv(path)
    w["xr"]=np.round(w.lat,4).astype(str)+"_"+np.round(w.lon,4).astype(str)
    w=w.drop_duplicates("xr").reset_index(drop=True)          # leakage audit: identical coordinates
    w["x"]=(w.lon*111.32*np.cos(np.radians(w.lat))); w["yk"]=w.lat*110.57
    w["aq_known"]=w.aquifer.notna().astype(int)
    w["aq_code"]=pd.factorize(w.aquifer)[0]                    # -1 for unknown
    w["y"]=w[label].astype(int)
    return w
FEATS=["lat","lon","aq_known","aq_code"]

def train_mask(w,held_idx):
    t=cKDTree(w.loc[held_idx,["x","yk"]].values); d,_=t.query(w[["x","yk"]].values,k=1)
    return d>BUF_KM
def fit_lgb(Xtr,ytr,params,seed,w=None):
    m=lgb.LGBMClassifier(**params,random_state=seed,n_jobs=1,verbose=-1); m.fit(Xtr,ytr,sample_weight=w); return m
def sample_params(rng):
    return dict(n_estimators=int(rng.choice([100,200,300])),learning_rate=float(rng.choice([0.03,0.06,0.1])),num_leaves=int(rng.choice([8,16,31,63])),
                min_child_samples=int(rng.choice([20,50,100])),subsample=float(rng.choice([0.7,1.0])),subsample_freq=1,colsample_bytree=float(rng.choice([0.7,1.0])),reg_lambda=float(rng.choice([0,1,10])))

def curve_from_order(y,order):
    return np.cumsum(y[order])
def found_at(cum,n,frac):
    k=max(1,int(round(frac*n))); return cum[k-1]

def campaign(y,coords,prior,mode,h=10.,kappa=2.,seed=0,refit=None):
    """Sequential ordering. mode: static|adaptive|thompson. Returns order (array of indices)."""
    n=len(y); rng=np.random.default_rng(seed)
    tested=np.zeros(n,bool); order=[]
    a=np.zeros(n); b=np.zeros(n)
    first=np.argsort(-prior,kind="stable")[:BATCH] if prior is not None else rng.choice(n,min(BATCH,n),replace=False)
    batch=first
    while True:
        for i in batch: tested[i]=True; order.append(i)
        if len(order)>=n: break
        if mode!="static":
            # kernel evidence from newly tested wells
            ti=np.array(batch); d2=((coords[:,None,:]-coords[ti][None,:,:])**2).sum(-1)
            wgt=np.exp(-d2/(2*h*h)); a+=wgt@y[ti]; b+=wgt@(1-y[ti])
            p=prior if prior is not None else np.full(n,0.1)
            if mode=="adaptive": s=(kappa*p+a)/(kappa+a+b)
            else: s=rng.beta(np.maximum(kappa*p+a,1e-3),np.maximum(kappa*(1-p)+b,1e-3))
        else: s=prior
        s=np.where(tested,-np.inf,s); k=min(BATCH,n-len(order))
        batch=np.argsort(-s,kind="stable")[:k]
    return np.array(order)

TESTED_WEIGHT=20.0
def campaign_refit(w_tr,w_te,params,seed,y,Xte):
    """M7: online refit of LightGBM with tested wells at checkpoints; between checkpoints keep last scores."""
    n=len(y); tested=np.zeros(n,bool); order=[]
    m=fit_lgb(w_tr[FEATS],w_tr.y,params,seed); s=m.predict_proba(Xte)[:,1]
    checks=[int(round(f*n)) for f in (0.025,0.05,0.10,0.15,0.20,0.25)]
    batch=np.argsort(-s,kind="stable")[:BATCH]
    while True:
        for i in batch: tested[i]=True; order.append(i)
        if len(order)>=n: break
        due=False
        while checks and len(order)>=checks[0]: checks.pop(0); due=True
        if due:
            ti=np.where(tested)[0]
            Xa=pd.concat([w_tr[FEATS],Xte.iloc[ti]]); ya=np.concatenate([w_tr.y.values,y[ti]]); wa=np.concatenate([np.ones(len(w_tr)),np.full(len(ti),TESTED_WEIGHT)])
            m=fit_lgb(Xa,ya,params,seed,wa); s=m.predict_proba(Xte)[:,1]
        s2=np.where(tested,-np.inf,s); batch=np.argsort(-s2,kind="stable")[:min(BATCH,n-len(order))]
    return np.array(order)

def knn_prior(w_tr,coords_te,k=50):
    t=cKDTree(w_tr[["x","yk"]].values); d,i=t.query(coords_te,k=k); wt=1/(d+1.0)
    return (wt*w_tr.y.values[i]).sum(1)/wt.sum(1)

def eval_unit(w,unit_idx,params,seed,hk,quick=False,refit=True):
    """Evaluate all methods on wells unit_idx (held out + buffer). hk=(h,kappa) tuned."""
    h,kappa=hk; te=w.loc[unit_idx]; y=te.y.values; n=len(y); coords=te[["x","yk"]].values
    tr=w[train_mask(w,unit_idx)]; Xte=te[FEATS]
    rows=[]
    def rec(method,order,extra=None):
        cum=curve_from_order(y,order); r={"method":method,"n_wells":n,"n_unsafe":int(y.sum()),"seed":seed}
        for b in BUDGETS: r[f"found_{int(b*100)}"]=int(found_at(cum,n,b))
        r["auc_curve"]=float(cum.sum()/(y.sum()*n)) if y.sum() else np.nan   # area under discovery curve (0.5 = random)
        if extra: r.update(extra)
        rows.append(r)
    m=fit_lgb(tr[FEATS],tr.y,params,seed); p1=m.predict_proba(Xte)[:,1]
    lr=LogisticRegression(max_iter=300); Z=lambda d_:np.c_[d_.lat,d_.lon,d_.lat**2,d_.lon**2,d_.lat*d_.lon,d_.aq_known]
    mu,sd=Z(tr).mean(0),Z(tr).std(0)+1e-9; lr.fit((Z(tr)-mu)/sd,tr.y); p2=lr.predict_proba((Z(te)-mu)/sd)[:,1]
    p3=knn_prior(tr,coords)
    ext={}
    if len(np.unique(y))>1: 
        for nm,p in (("M1",p1),("M2",p2),("M3",p3)): ext[nm]=(roc_auc_score(y,p),average_precision_score(y,p))
    prev=float(tr.y.mean())
    rng=np.random.default_rng(seed)
    rec("M1_static_lgbm",np.argsort(-p1,kind="stable"),{"auc_roc":ext.get("M1",(np.nan,np.nan))[0],"auc_pr":ext.get("M1",(np.nan,np.nan))[1]})
    rec("M2_static_logreg",np.argsort(-p2,kind="stable"),{"auc_roc":ext.get("M2",(np.nan,np.nan))[0],"auc_pr":ext.get("M2",(np.nan,np.nan))[1]})
    rec("M3_static_knn",np.argsort(-p3,kind="stable"),{"auc_roc":ext.get("M3",(np.nan,np.nan))[0],"auc_pr":ext.get("M3",(np.nan,np.nan))[1]})
    rec("M4_neighbor_only",campaign(y,coords,None,"adaptive",h,kappa,seed))
    rec("M5_proposed",campaign(y,coords,p1,"adaptive",h,kappa,seed))
    rec("M6_thompson",campaign(y,coords,p1,"thompson",h,kappa,seed))
    rec("A1_no_prior",campaign(y,coords,np.full(n,prev)+1e-6*rng.random(n),"adaptive",h,kappa,seed))
    rec("A2_no_shrinkage",campaign(y,coords,p1,"adaptive",h,0.01,seed))
    rec("A3_fixed_bandwidth",campaign(y,coords,p1,"adaptive",10.,2.,seed))
    rec("A4_knn_prior",campaign(y,coords,p3,"adaptive",h,kappa,seed))
    if refit: rec("M7_online_refit",campaign_refit(tr,te,params,seed,y,Xte))
    return rows

def tune(w,tune_idx_by_unit,params_trials,seed):
    """Select LightGBM params (20 trials) and (h,kappa) on tuning units only."""
    all_t=np.concatenate(list(tune_idx_by_unit.values())); rng=np.random.default_rng(seed)
    base=w.drop(index=all_t); best=None
    for t in range(params_trials):
        p=sample_params(rng); sc=[]
        for u,idx in tune_idx_by_unit.items():
            te=w.loc[idx]; tr=base[train_mask(w,idx)[base.index]]
            if te.y.sum()<5: continue
            m=fit_lgb(tr[FEATS],tr.y,p,seed); sc.append(average_precision_score(te.y,m.predict_proba(te[FEATS])[:,1]))
        s=float(np.mean(sc)); 
        if best is None or s>best[0]: best=(s,p)
    params=best[1]; res={}
    pri={}
    for u,idx in tune_idx_by_unit.items():
        te=w.loc[idx]; tr=base[train_mask(w,idx)[base.index]]; m=fit_lgb(tr[FEATS],tr.y,params,seed); pri[u]=m.predict_proba(te[FEATS])[:,1]
    for h in BW_GRID:
        for k in KAPPA_GRID:
            sc=[]
            for u,idx in tune_idx_by_unit.items():
                te=w.loc[idx]; y=te.y.values
                if y.sum()<5: continue
                o=campaign(y,te[["x","yk"]].values,pri[u],"adaptive",h,k,seed); cum=curve_from_order(y,o)
                sc.append(found_at(cum,len(y),0.2)/(0.2*y.sum()))
            res[(h,k)]=float(np.mean(sc))
    hk=max(res,key=res.get)
    return params,hk,{"lgb_val_prauc":best[0],"hk_grid":{f"{h}_{k}":v for (h,k),v in res.items()}}

def random_vs_blocked(w,params,seed,states):
    """RQ1: same learner, random 5-fold vs leave-one-state-out(+buffer) vs KMeans blocks; AUC-PR and recall@20% pooled."""
    from sklearn.model_selection import KFold
    out=[]
    # random
    p=np.zeros(len(w))
    for tr,te in KFold(5,shuffle=True,random_state=seed).split(w):
        p[te]=fit_lgb(w.iloc[tr][FEATS],w.iloc[tr].y,params,seed).predict_proba(w.iloc[te][FEATS])[:,1]
    out.append(("random_5fold",roc_auc_score(w.y,p),average_precision_score(w.y,p),recall20(w.y.values,p,np.arange(len(w))*0)))
    # leave-state-out with buffer
    p=np.full(len(w),np.nan)
    for s in states:
        idx=w.index[w.state==s]; tr=w[train_mask(w,idx)]
        p[idx]=fit_lgb(tr[FEATS],tr.y,params,seed).predict_proba(w.loc[idx,FEATS])[:,1]
    ok=~np.isnan(p); out.append(("leave_state_out",roc_auc_score(w.y[ok],p[ok]),average_precision_score(w.y[ok],p[ok]),recall20(w.y.values[ok],p[ok],w.state.values[ok])))
    return out
def recall20(y,p,group):
    """mean over groups of recall when top 20% by score tested (group=0 -> pooled)."""
    r=[]
    for g in np.unique(group):
        m=group==g; yy,pp=y[m],p[m]
        if yy.sum()==0: continue
        k=max(1,int(round(0.2*len(yy)))); r.append(yy[np.argsort(-pp,kind="stable")[:k]].sum()/yy.sum())
    return float(np.mean(r))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data"); ap.add_argument("--label",default="y10"); ap.add_argument("--out"); ap.add_argument("--mode",default="full")
    ap.add_argument("--units",default="state"); ap.add_argument("--tuned",default=None); ap.add_argument("--seeds",type=int,default=5); ap.add_argument("--jobs",type=int,default=4); a=ap.parse_args()
    t0=time.time(); w=load(a.data,a.label); os.makedirs(a.out,exist_ok=True)
    if a.units=="state":
        cnt=w.groupby("state").y.agg(["size","sum"]); elig=cnt[(cnt["size"]>=100)&(cnt["sum"]>=15)].index.tolist()
        rng=np.random.default_rng(0); tune_states=sorted(rng.choice(elig,8,replace=False).tolist()); eval_states=[s for s in elig if s not in tune_states]
        if a.mode=="quick": eval_states=eval_states[:3]; a.seeds=1
        print("wells",len(w),"eligible",len(elig),"tune",tune_states,"eval",len(eval_states),flush=True)
        tune_idx={s:w.index[w.state==s].values for s in tune_states}
        params,hk,tinfo=tune(w,tune_idx,20 if a.mode=="full" else 3,0); print("tuned",params,hk,flush=True)
        json.dump({"params":params,"h_kappa":hk,"tune_states":tune_states,"eval_states":eval_states,**tinfo},open(f"{a.out}/tuning.json","w"),indent=1)
        w["unit"]=w.state
    else:   # KMeans blocks over wells of evaluation states only; hyperparameters reused from the state run (no retuning)
        T=json.load(open(a.tuned)); params,hk=T["params"],tuple(T["h_kappa"]); ev=w[w.state.isin(T["eval_states"])]
        km=KMeans(60,n_init=3,random_state=0).fit(ev[["x","yk"]].values); w["unit"]=-1; w.loc[ev.index,"unit"]=km.labels_
        cnt=w[w.unit>=0].groupby("unit").y.agg(["size","sum"]); eval_states=cnt[(cnt["size"]>=60)&(cnt["sum"]>=5)].index.tolist()
        print("blocks eligible",len(eval_states),"of 60",flush=True)
    jobs=[(s,sd) for s in eval_states for sd in range(a.seeds)]
    res=Parallel(n_jobs=a.jobs)(delayed(eval_unit)(w,w.index[w.unit==s].values,params,sd,hk,a.mode=="quick") for s,sd in jobs)
    rows=[]
    for (s,sd),rs in zip(jobs,res):
        for r in rs: r["unit"]=s; r["scenario"]="leave_state_out"; rows.append(r)
    pd.DataFrame(rows).to_csv(f"{a.out}/raw_results.csv",index=False)
    # RQ1
    rv=[]
    if a.units!="state": print("done",round(time.time()-t0),"s",flush=True); return
    for sd in range(min(a.seeds,3)):
        for nm,auc,pr,rc in random_vs_blocked(w,params,sd,eval_states): rv.append(dict(split=nm,seed=sd,auc_roc=auc,auc_pr=pr,recall_at_20=rc))
    pd.DataFrame(rv).to_csv(f"{a.out}/random_vs_blocked.csv",index=False)
    print("done",round(time.time()-t0),"s",flush=True)
if __name__=="__main__": main()
