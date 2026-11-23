"""TOC graphic: real state, first 20% of wells tested under random order vs adaptive (ABF) order."""
import json, os, sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E, abf
w=E.load("data/processed/wells_as.csv","y10"); T=json.load(open("results/as10/tuning.json")); p0=None
ab=pd.read_csv("results/abf_as10/abf.csv"); u=ab[ab.method=="ABF"].groupby("unit").agg(e=("enr_20","mean"),n=("n","first"))
cand=u[(u.n>=600)&(u.n<=1500)]; st=(cand.e-cand.e.median()).abs().idxmin(); print("state",st,cand.loc[st].to_dict())
idx=w.index[w.state==st].values; te=w.loc[idx]; y=te.y.values; X=te[["x","yk"]].values; tr=w[E.train_mask(w,idx)]; p0=float(tr.y.mean())
p=E.fit_lgb(tr[E.FEATS],tr.y,T["params"],0).predict_proba(te[E.FEATS])[:,1]; o=abf.abf_campaign(y,X,p,p0,0,"full"); n=len(y); k=int(0.2*n)
rnd=np.random.default_rng(1).permutation(n)[:k]; ada=o[:k]
fig,ax=plt.subplots(1,2,figsize=(7.2,3.4),sharex=True,sharey=True)
for a,sel,title in ((ax[0],rnd,"Random order"),(ax[1],ada,"Adaptive testing (ABF)")):
    a.scatter(X[:,0],X[:,1],s=3,c="#cccccc",lw=0)
    a.scatter(X[y==1,0],X[y==1,1],s=6,c="#e8a0a0",lw=0)
    t=np.zeros(n,bool); t[sel]=True
    a.scatter(X[t&(y==0),0],X[t&(y==0),1],s=9,c="#2a6f97",lw=0); a.scatter(X[t&(y==1),0],X[t&(y==1),1],s=16,c="#c1121f",lw=0)
    a.set_title(f"{title}: {int(y[sel].sum())} of {int(y.sum())} unsafe wells found",fontsize=8); a.set_xticks([]); a.set_yticks([]); a.set_aspect("equal"); [s.set_visible(False) for s in a.spines.values()]
fig.text(0.5,0.02,f"One real state ({st}), {n:,} wells: grey = untested, pink = unsafe but untested, blue = tested safe, red = tested unsafe. First 20% of wells tested.",ha="center",fontsize=6.5)
plt.tight_layout(rect=[0,0.05,1,1]); plt.savefig("figures/toc_graphic.png",dpi=300); plt.close(); open("results/toc_state.txt","w").write(f"{st}\n{y[rnd].sum()} {y[ada].sum()} {y.sum()} {n}\n")
