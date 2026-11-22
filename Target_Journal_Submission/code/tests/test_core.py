import sys, numpy as np, pandas as pd
import os; sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","src"))
import experiment as E
def test_curve_and_found():
    y=np.array([0,1,0,1,1]); c=E.curve_from_order(y,np.array([1,3,4,0,2])); assert c.tolist()==[1,2,3,3,3]; assert E.found_at(c,5,0.4)==2
def test_campaign_covers_all_once_and_adapts():
    rng=np.random.default_rng(0); n=200; coords=rng.uniform(0,100,(n,2)); y=(coords[:,0]>80).astype(int)
    prior=np.full(n,0.2)+1e-6*rng.random(n); o=E.campaign(y,coords,prior,"adaptive",10.,1.,0)
    assert sorted(o.tolist())==list(range(n))                       # each well tested exactly once
    cum=E.curve_from_order(y,o); assert E.found_at(cum,n,0.25)>0.25*y.sum()*1.5   # feedback beats random on clustered signal
def test_static_is_pure_sort():
    p=np.array([.1,.9,.5]); o=E.campaign(np.array([0,1,0]),np.zeros((3,2)),p,"static",1.,1.,0)
    assert o.tolist()==[1,2,0]
def test_buffer_excludes_neighbors():
    w=pd.DataFrame({"x":[0,10,100.],"yk":[0,0,0.]}); m=E.train_mask(w,[0]); assert m.tolist()==[False,False,True]
