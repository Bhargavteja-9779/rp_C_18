"""Campaign planner: suggest the next wells to test.

Input  --wells  CSV with columns: well_id, lat, lon  (all candidate wells)
       --results CSV (optional) with columns: well_id, unsafe (1/0) for wells already tested
       --history CSV (optional) with columns: lat, lon, unsafe  (earlier wells of this state: used as prior evidence)
Output CSV of the next --batch wells ranked by the follow-unsafe rule (kernel-weighted unsafe count within --bandwidth km),
       with history/results as evidence. Before any unsafe result exists, wells are ordered to spread tests in space.
This is the method evaluated in the paper (H1, and M4/W6 variants). It is a research tool, not a validated public-health product."""
import argparse, numpy as np, pandas as pd
ap=argparse.ArgumentParser(); ap.add_argument("--wells",required=True); ap.add_argument("--results"); ap.add_argument("--history")
ap.add_argument("--batch",type=int,default=10); ap.add_argument("--bandwidth",type=float,default=5.0); ap.add_argument("--out",default="next_batch.csv"); a=ap.parse_args()
def xy(d): return np.c_[d.lon*111.32*np.cos(np.radians(d.lat)),d.lat*110.57]
W=pd.read_csv(a.wells); tested=pd.read_csv(a.results) if a.results else pd.DataFrame(columns=["well_id","unsafe"])
W["tested"]=W.well_id.isin(tested.well_id); X=xy(W); h=a.bandwidth; score=np.zeros(len(W)); n_unsafe=0
def add(coords,y):
    global score
    for i in range(0,len(W),2000):
        d2=((X[i:i+2000,None,:]-coords[None,:,:])**2).sum(-1); score[i:i+2000]+=np.exp(-d2/(2*h*h))@y
ev=[]
if len(tested):
    T=tested.merge(W[["well_id","lat","lon"]],on="well_id"); ev.append((xy(T),T.unsafe.values.astype(float))); n_unsafe+=int(T.unsafe.sum())
if a.history:
    H=pd.read_csv(a.history); ev.append((xy(H),H.unsafe.values.astype(float))); n_unsafe+=int(H.unsafe.sum())
for c,y in ev: add(c,y)
cand=W[~W.tested].copy(); cand["score"]=score[~W.tested.values]
if n_unsafe==0:    # no unsafe result yet: spread tests (greedy maximin from already tested wells)
    T=X[W.tested.values]; C=X[~W.tested.values]; chosen=[]; dmin=np.full(len(C),1e18) if not len(T) else ((C[:,None,:]-T[None,:,:])**2).sum(-1).min(1)
    for _ in range(min(a.batch,len(C))):
        j=int(np.argmax(dmin)); chosen.append(j); dmin=np.minimum(dmin,((C-C[j])**2).sum(1)); dmin[chosen]=-1
    out=cand.iloc[chosen]
else: out=cand.sort_values("score",ascending=False).head(a.batch)
out[["well_id","lat","lon","score"]].to_csv(a.out,index=False); print(f"wrote {len(out)} wells to {a.out}; unsafe results used as evidence: {n_unsafe}")
