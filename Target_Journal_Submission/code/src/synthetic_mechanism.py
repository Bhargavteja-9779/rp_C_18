"""Controlled test of the clustering mechanism: unsafe wells = top 10% of a Gaussian random field with correlation length L (km).
Compare random order, spatial spread (H2), kernel feedback (M4) and follow-unsafe (H1) at 20% budget. Output results/robust_checks/synthetic_mechanism.csv"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0,os.path.dirname(__file__)); import experiment as E
rng0=np.random.default_rng(2026); N=1500; SIDE=150.0; K=200; rows=[]
def enr(y,o,f=0.2): c=E.curve_from_order(y,o); return E.found_at(c,len(y),f)/(f*y.sum())
def hot(y,coords,hh,rng):
    n=len(y); tested=np.zeros(n,bool); order=[]; a=np.zeros(n); b=rng.choice(n,10,replace=False)
    while True:
        for i in b: tested[i]=True; order.append(i)
        if len(order)>=n: break
        ti=np.array(b); d2=((coords[:,None,:]-coords[ti][None,:,:])**2).sum(-1); a+=np.exp(-d2/(2*hh*hh))@y[ti]
        b=np.argsort(-np.where(tested,-np.inf,a+1e-6*rng.random(n)))[:min(10,n-len(order))]
    return np.array(order)
for L in (1,2,5,10,20,40,80):
    for rep in range(40):
        rng=np.random.default_rng(rep*1000+L); X=rng.uniform(0,SIDE,(N,2)); W=rng.normal(0,1/L,(K,2)); B=rng.uniform(0,2*np.pi,K); f=np.sqrt(2/K)*np.cos(X@W.T+B).sum(1)
        y=(f>=np.quantile(f,0.9)).astype(int)
        for h in (5.0,):
            rows.append(dict(L=L,rep=rep,M4=enr(y,E.campaign(y,X,None,"adaptive",h,0.5,rep)),H1=enr(y,hot(y,X,h,rng))))
d=pd.DataFrame(rows); d.to_csv("results/robust_checks/synthetic_mechanism.csv",index=False); g=d.groupby("L")[["M4","H1"]].agg(["mean","std"]).round(3); print(g.to_string()); g.to_csv("results/robust_checks/synthetic_mechanism_summary.csv")
