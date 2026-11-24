"""Hierarchical ABF (deviation 44): ABF whose starting expert weights come from other states' campaigns."""
import numpy as np, sys, os
sys.path.insert(0,os.path.dirname(__file__)); import abf
CHECK=0.30
def abf_campaign_h(y,coords,prior,p0,seed,log_prior=None,batch=10,cfg=abf.V1,variant="full",return_loss=False):
    """Same logic as abf.abf_campaign. log_prior: array over the experts (natural log of pi_k) or None (uniform).
    If return_loss: also returns (per-expert cumulative DATA log loss at CHECK of the wells, wells tested at that point)."""
    eta=cfg["eta"]; n=len(y); rng=np.random.default_rng(seed); ex=abf.make_experts(variant,cfg)
    if prior is None: ex=[e for e in ex if e[0] in("free","hot")]
    hs=sorted({e[1] for e in ex if e[1]}); A={h:np.zeros(n) for h in hs}; B={h:np.zeros(n) for h in hs}
    L0=np.zeros(len(ex)) if log_prior is None else -np.asarray(log_prior)/eta; L=L0.copy(); Ld=np.zeros(len(ex)); tested=np.zeros(n,bool); order=[]; pr=prior if prior is not None else np.full(n,p0); snap=None
    def preds(idx):
        P=np.empty((len(ex),len(idx)))
        for i,(typ,h,k) in enumerate(ex):
            if typ=="maponly": P[i]=pr[idx]
            elif typ=="hot": P[i]=p0+(1-p0)*(1-np.exp(-A[h][idx]))
            else:
                base=pr[idx] if typ=="map" else p0; P[i]=(k*base+A[h][idx])/(k+A[h][idx]+B[h][idx])
        return np.clip(P,1e-3,1-1e-3)
    b=np.argsort(-pr,kind="stable")[:batch] if prior is not None else rng.choice(n,min(batch,n),replace=False)
    while True:
        P=preds(b); yb=y[b]; ll=(yb[None,:]*np.log(P)+(1-yb[None,:])*np.log(1-P)).sum(1); L+=-ll; Ld+=-ll
        for i in b: tested[i]=True; order.append(i)
        if snap is None and len(order)>=CHECK*n: snap=(Ld.copy(),len(order))
        if len(order)>=n: break
        d2=((coords[:,None,:]-coords[b][None,:,:])**2).sum(-1)
        for h in hs: K=np.exp(-d2/(2*h*h)); A[h]+=K@y[b]; B[h]+=K@(1-y[b])
        w=np.exp(-eta*(L-L.min())); w/=w.sum(); un=np.where(~tested)[0]; s=(w[:,None]*preds(un)).sum(0)
        sc=np.full(n,-np.inf); sc[un]=s; b=np.argsort(-sc,kind="stable")[:min(batch,len(un))]
    order=np.array(order)
    return (order,snap) if return_loss else order
def prior_from_donors(delta_bar,tau,N0=300.0):
    lp=-tau*N0*np.asarray(delta_bar); lp=lp-np.log(np.exp(lp-lp.max()).sum())-lp.max(); return lp
