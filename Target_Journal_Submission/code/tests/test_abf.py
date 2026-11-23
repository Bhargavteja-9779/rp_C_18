import sys, os, numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","src"))
import abf, experiment as E
def test_abf_regret_bound_and_gain():
    rng=np.random.default_rng(1); n=600; X=rng.uniform(0,60,(n,2)); f=np.cos(X@rng.normal(0,1/8,(2,40))+rng.uniform(0,6.28,40)).sum(1); y=(f>=np.quantile(f,.85)).astype(int)
    o,info=abf.abf_campaign(y,X,None,y.mean(),0,"full",return_info=True)
    assert sorted(o.tolist())==list(range(n)) and info["regret_nats"]<=info["ln_N"]+1e-6   # mixture within ln N of the best expert
    c=E.curve_from_order(y,o); assert E.found_at(c,n,0.2)>1.5*0.2*y.sum()                    # beats random on a clustered signal
def test_abf_trusts_good_map_and_ignores_bad_map():
    rng=np.random.default_rng(2); n=800; X=rng.uniform(0,80,(n,2)); y=(rng.random(n)<0.1).astype(int)   # no spatial structure
    good=np.where(y==1,0.7,0.05); _,i1=abf.abf_campaign(y,X,good,y.mean(),0,return_info=True)
    bad=rng.random(n)*0.3; _,i2=abf.abf_campaign(y,X,bad,y.mean(),0,return_info=True)
    assert i1["w_map"]+i1["w_maponly"]>i2["w_map"]+i2["w_maponly"]
