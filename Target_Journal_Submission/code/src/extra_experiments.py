"""Added experiments (logged in deviations.md items 13-16): kappa sweep, heuristic baselines, warm start, spatial-clustering mechanism.
Usage: python extra_experiments.py <label y10|y5> <out_dir>   (reads tuning from results/as10 or as5)"""
import json, os, sys, numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.spatial import cKDTree
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E
label,out=sys.argv[1],sys.argv[2]; os.makedirs(out,exist_ok=True)
tdir=sys.argv[3] if len(sys.argv)>3 else ("results/as10" if label=="y10" else "results/as5")
w=E.load(os.environ.get("DATA","data/processed/wells_as.csv"),label); T=json.load(open(f"{tdir}/tuning.json")); params=T["params"]; H=T["h_kappa"][0]
KAPPAS=[0.5,2,10,50,200,1000]; SEEDS=3
def enr(y,o,f=0.2): cum=E.curve_from_order(y,o); return E.found_at(cum,len(y),f)/(f*y.sum())
def campaign_hot(y,coords,h,seed):                         # H1: follow unsafe results only
    n=len(y); rng=np.random.default_rng(seed); tested=np.zeros(n,bool); order=[]; a=np.zeros(n); batch=rng.choice(n,min(E.BATCH,n),replace=False)
    while True:
        for i in batch: tested[i]=True; order.append(i)
        if len(order)>=n: break
        ti=np.array(batch); d2=((coords[:,None,:]-coords[ti][None,:,:])**2).sum(-1); a+=np.exp(-d2/(2*h*h))@y[ti]
        s=np.where(tested,-np.inf,a+1e-6*rng.random(n)); batch=np.argsort(-s)[:min(E.BATCH,n-len(order))]
    return np.array(order)
def campaign_spread(coords,seed):                          # H2: systematic spatial coverage (greedy maximin), uses no outcomes
    n=len(coords); rng=np.random.default_rng(seed); first=rng.integers(n); order=[first]; dmin=((coords-coords[first])**2).sum(1)
    while len(order)<n:
        dmin[order[-1]]=-1; j=int(np.argmax(dmin)); order.append(j); dmin=np.minimum(dmin,((coords-coords[j])**2).sum(1)); dmin[order]=-1
    return np.array(order)
def unit(s,seed):
    idx=w.index[w.state==s].values; te=w.loc[idx]; y=te.y.values; coords=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]
    p=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(te[E.FEATS])[:,1]
    r=dict(unit=s,seed=seed,n=len(y),M1=enr(y,np.argsort(-p,kind="stable")),H1_follow_unsafe=enr(y,campaign_hot(y,coords,H,seed)),H2_spread=enr(y,campaign_spread(coords,seed)))
    for k in KAPPAS: r[f"M5_kappa{k}"]=enr(y,E.campaign(y,coords,p,"adaptive",H,k,seed))
    r["M4"]=enr(y,E.campaign(y,coords,None,"adaptive",H,0.5,seed))
    return r
res=Parallel(n_jobs=4)(delayed(unit)(s,sd) for s in T["eval_states"] for sd in range(SEEDS))
d=pd.DataFrame(res); d.to_csv(f"{out}/sweep_heuristics.csv",index=False)
print(d.drop(columns=["unit","seed","n"]).mean().round(3).to_string())
# mechanism: spatial clustering of unsafe wells (lift of unsafe given unsafe neighbour within r km) vs feedback gain
rows=[]
for s in T["eval_states"]:
    te=w[w.state==s]; X=te[["x","yk"]].values; y=te.y.values; t=cKDTree(X); r={"unit":s,"n":len(y),"prev":y.mean()}
    for rad in (2,5,20):
        pairs=t.query_pairs(rad,output_type="ndarray")
        if len(pairs)<50: r[f"lift_{rad}km"]=np.nan; continue
        a,b=y[pairs[:,0]],y[pairs[:,1]]; pu=((a==1)&(b==1)).sum()*2/max(1,(a.sum()*0+ (a+b).sum())) if (a+b).sum()>0 else np.nan  # P(neighbour unsafe | unsafe)
        r[f"lift_{rad}km"]=pu/y.mean()
    rows.append(r)
m=pd.DataFrame(rows); g=d.groupby("unit")[["M1","M4"]].mean(); m=m.merge(g,left_on="unit",right_index=True); m["gain_feedback_minus_static"]=m.M4-m.M1; m.to_csv(f"{out}/mechanism.csv",index=False)
from scipy.stats import spearmanr
for c in ("lift_2km","lift_5km","lift_20km"):
    ok=m[[c,"M4"]].dropna(); print(c,"Spearman with M4 enrichment",np.round(spearmanr(ok[c],ok.M4),3).tolist(),"n",len(ok))
# warm start: earliest 50% of each state's wells (by sample date) are 'history'; campaign on the later 50%
def warm(s,seed):
    te=w[w.state==s].sort_values("date"); half=len(te)//2; hist,new=te.iloc[:half],te.iloc[half:]
    if len(new)<100 or new.y.sum()<10: return None
    y=new.y.values; coords=new[["x","yk"]].values
    outside=w[(w.state!=s)]
    tr_all=pd.concat([outside,hist]); tr_loc=hist
    p_all=E.fit_lgb(tr_all[E.FEATS],tr_all.y,params,seed).predict_proba(new[E.FEATS])[:,1]
    p_loc=E.fit_lgb(tr_loc[E.FEATS],tr_loc.y,params,seed).predict_proba(new[E.FEATS])[:,1] if tr_loc.y.nunique()>1 else np.full(len(new),tr_loc.y.mean())
    p_out=E.fit_lgb(outside[E.FEATS],outside.y,params,seed).predict_proba(new[E.FEATS])[:,1]
    # history as kernel evidence (distance from history wells)
    tree=cKDTree(hist[["x","yk"]].values); 
    def hist_evidence(h):
        a=np.zeros(len(new)); b=np.zeros(len(new)); hc=hist[["x","yk"]].values; hy=hist.y.values
        for i in range(0,len(new),500):
            d2=((coords[i:i+500,None,:]-hc[None,:,:])**2).sum(-1); wg=np.exp(-d2/(2*h*h)); a[i:i+500]=wg@hy; b[i:i+500]=wg@(1-hy)
        return a,b
    a0,b0=hist_evidence(H); prior_h=(0.5*p_all+a0)/(0.5+a0+b0)
    r=dict(unit=s,seed=seed,n_new=len(y),W0_random=1.0,W1_map_outside_only=enr(y,np.argsort(-p_out,kind="stable")),W2_map_with_history=enr(y,np.argsort(-p_all,kind="stable")),
       W3_map_local_history_only=enr(y,np.argsort(-p_loc,kind="stable")),W4_history_kernel_static=enr(y,np.argsort(-prior_h,kind="stable")),
       W5_cold_feedback=enr(y,E.campaign(y,coords,None,"adaptive",H,0.5,seed)),W6_history_prior_plus_feedback=enr(y,E.campaign(y,coords,prior_h,"adaptive",H,0.5,seed)))
    return r
wr=[r for r in Parallel(n_jobs=4)(delayed(warm)(s,sd) for s in T["eval_states"] for sd in range(SEEDS)) if r]
wd=pd.DataFrame(wr); wd.to_csv(f"{out}/warm_start.csv",index=False); print("warm-start units",wd.unit.nunique()); print(wd.drop(columns=["unit","seed","n_new"]).mean().round(3).to_string())
