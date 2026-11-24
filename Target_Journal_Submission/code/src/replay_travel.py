"""Travel-distance proxy on replayed campaigns (deviation 48). Usage: replay_travel.py <scenario> (WELL_FEATS=base)"""
import os, sys, json, glob, numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.spatial.distance import pdist, squareform
from scipy.sparse.csgraph import minimum_spanning_tree
sys.path.insert(0,os.path.dirname(__file__))
# reuse the campaign table logic of campaign_replay.py by executing its definitions up to the state loop
src=open(os.path.join(os.path.dirname(__file__),"campaign_replay.py")).read(); head=src[:src.index("def state_seed(")]
sys.argv=[sys.argv[0],sys.argv[1]]; exec(head)
def mst_km(X): 
    if len(X)<2: return 0.0
    return float(minimum_spanning_tree(squareform(pdist(X))).sum())
def run(s,seed,camps):
    sidx=w.index[w.state==s].values; tr=w[E.train_mask(w,sidx)]; p0=float(tr.y.mean())
    pm=E.fit_lgb(tr[E.FEATS],tr.y,params,seed).predict_proba(w.loc[sidx,E.FEATS])[:,1]; pmap=pd.Series(pm,index=sidx); rows=[]
    for cid in camps:
        te=w[w.camp==cid].dropna(subset=["d0"]); y=te.y.values; X=te[["x","yk"]].values; n=len(y); k20=max(1,int(round(0.2*n))); rng=np.random.default_rng(seed); p=pmap.loc[te.index].values
        orders={"real":np.lexsort((rng.random(n),te.d0.values.astype("int64"))),"follow":hot(y,X,h,seed),"feedback":E.campaign(y,X,None,"adaptive",h,k,seed),"ABF":abf.abf_campaign(y,X,p,p0,seed,"full")}
        rnd=[rng.permutation(n)[:k20] for _ in range(20)]
        r_len=np.mean([mst_km(X[i]) for i in rnd]); r_unsafe=np.mean([y[i].sum() for i in rnd])
        row=dict(camp=cid,state=s,seed=seed,n=n,k20=k20,random_len=r_len,random_unsafe=r_unsafe,random_km_per_unsafe=r_len/max(r_unsafe,1e-9))
        for nm,o in orders.items():
            i=o[:k20]; L=mst_km(X[i]); u=y[i].sum(); row[f"{nm}_len"]=L; row[f"{nm}_unsafe"]=int(u); row[f"{nm}_km_per_unsafe"]=L/max(u,1)
        rows.append(row)
    return rows
bystate={s:list(c.index[c.state==s]) for s in c.state.unique()}
res=[x for rs in Parallel(n_jobs=4)(delayed(run)(s,sd,cl) for s,cl in bystate.items() for sd in range(3)) for x in rs]
d=pd.DataFrame(res); d.to_csv(f"results/replay/travel_{sc}.csv",index=False)
u=d.groupby("camp").mean(numeric_only=True); from scipy.stats import wilcoxon
rows=[dict(scenario=sc,n_campaigns=len(u),random_km_per_unsafe=u.random_km_per_unsafe.median(),real_km_per_unsafe=u.real_km_per_unsafe.median())]
ps={}
for m in ("follow","feedback","ABF"):
    x=(u[f"{m}_km_per_unsafe"]-u.real_km_per_unsafe).values; ps[m]=wilcoxon(x).pvalue; rows[0][f"{m}_km_per_unsafe"]=u[f"{m}_km_per_unsafe"].median(); rows[0][f"{m}_len_ratio_to_real"]=float((u[f"{m}_len"]/u.real_len).median()); rows[0][f"{m}_lower_in"]=int((x<0).sum()); rows[0][f"{m}_p"]=ps[m]
srt=sorted(ps.values())
for m,pv in ps.items(): rows[0][f"{m}_holm"]=min(1,pv*(len(srt)-srt.index(pv)))
t=pd.DataFrame(rows); t.to_csv(f"results/replay/travel_{sc}_summary.csv",index=False); print(t.round(3).T.to_string())
