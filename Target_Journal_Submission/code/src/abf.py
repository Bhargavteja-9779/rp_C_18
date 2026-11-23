"""Adaptive Bayesian-mixture feedback (ABF). See deviations.md item 26."""
import numpy as np
H_GRID=(2.,5.,10.,20.,50.); K_FREE=(0.5,2.); K_MAP=(0.5,2.,10.,50.)
V1=dict(eta=1.0,hot=False,ext=False)
def make_experts(variant,cfg=V1):
    ex=[]
    kf=K_FREE+((0.1,) if cfg["ext"] else ()); km=K_MAP+((0.1,) if cfg["ext"] else ())
    if variant in("full","fixedh","nomap"):
        hs=(5.,) if variant=="fixedh" else H_GRID
        for h in hs:
            for k in kf: ex.append(("free",h,k))
        if cfg["hot"]:
            for h in hs: ex.append(("hot",h,None))
        if variant!="nomap":
            for h in hs:
                for k in km: ex.append(("map",h,k))
            ex.append(("maponly",None,None))
    return ex
def abf_campaign(y,coords,prior,p0,seed,variant="full",batch=10,cfg=V1,return_info=False,hist=None):
    eta=cfg["eta"]
    """y: outcomes (revealed only after testing); prior: map probabilities (or None); p0: base prevalence. Returns order (and diagnostics)."""
    n=len(y); rng=np.random.default_rng(seed); ex=make_experts(variant,cfg)
    if prior is None: ex=[e for e in ex if e[0] in("free","hot")]
    hs=sorted({e[1] for e in ex if e[1]}); A={h:np.zeros(n) for h in hs}; B={h:np.zeros(n) for h in hs}
    if hist is not None:                       # earlier wells of the same state act as evidence from the start
        hc,hy=hist
        for h in hs:
            for i in range(0,n,500):
                d2=((coords[i:i+500,None,:]-hc[None,:,:])**2).sum(-1); K=np.exp(-d2/(2*h*h)); A[h][i:i+500]+=K@hy; B[h][i:i+500]+=K@(1-hy)
    L=np.zeros(len(ex)); tested=np.zeros(n,bool); order=[]; joint_loss=0.0
    pr=prior if prior is not None else np.full(n,p0)
    def preds(idx):
        P=np.empty((len(ex),len(idx)))
        for i,(typ,h,k) in enumerate(ex):
            if typ=="maponly": P[i]=pr[idx]
            elif typ=="hot": P[i]=p0+(1-p0)*(1-np.exp(-A[h][idx]))
            else:
                base=pr[idx] if typ=="map" else p0
                P[i]=(k*base+A[h][idx])/(k+A[h][idx]+B[h][idx])
        return np.clip(P,1e-3,1-1e-3)
    b=np.argsort(-pr,kind="stable")[:batch] if prior is not None else rng.choice(n,min(batch,n),replace=False)
    while True:
        P=preds(b); yb=y[b]
        ll=(yb[None,:]*np.log(P)+(1-yb[None,:])*np.log(1-P)).sum(1)          # expert joint log-lik of this batch
        w=np.exp(-eta*(L-L.min())); w/=w.sum()
        joint_loss+=-np.log((w*np.exp(ll-ll.max())).sum())-ll.max()           # mixture joint log-loss on the batch
        L+=-ll
        for i in b: tested[i]=True; order.append(i)
        if len(order)>=n: break
        d2=((coords[:,None,:]-coords[b][None,:,:])**2).sum(-1)
        for h in hs: K=np.exp(-d2/(2*h*h)); A[h]+=K@y[b]; B[h]+=K@(1-y[b])
        w=np.exp(-eta*(L-L.min())); w/=w.sum()
        un=np.where(~tested)[0]; s=(w[:,None]*preds(un)).sum(0)
        sc=np.full(n,-np.inf); sc[un]=s; b=np.argsort(-sc,kind="stable")[:min(batch,len(un))]
    if return_info:
        best=L.min(); w=np.exp(-(L-L.min())); w/=w.sum()
        mass={t:float(sum(w[i] for i,e in enumerate(ex) if e[0]==t)) for t in("free","map","maponly","hot")}
        return np.array(order),dict(regret_nats=float(joint_loss-best),ln_N=float(np.log(len(ex))),n_experts=len(ex),**{"w_"+k:v for k,v in mass.items()})
    return np.array(order)
