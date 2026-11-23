import subprocess, sys, os, pandas as pd, numpy as np
def test_planner_follows_unsafe(tmp_path):
    rng=np.random.default_rng(0); W=pd.DataFrame({"well_id":range(100),"lat":45+rng.random(100)*0.5,"lon":-93+rng.random(100)*0.5}); W.to_csv(tmp_path/"w.csv",index=False)
    first=W.iloc[0]; res=pd.DataFrame({"well_id":[0],"unsafe":[1]}); res.to_csv(tmp_path/"r.csv",index=False)
    subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),"..","campaign_planner.py"),"--wells",str(tmp_path/"w.csv"),"--results",str(tmp_path/"r.csv"),"--batch","3","--bandwidth","8","--out",str(tmp_path/"o.csv")],check=True)
    o=pd.read_csv(tmp_path/"o.csv"); assert len(o)==3 and 0 not in o.well_id.values
    d=lambda r:np.hypot((r.lat-first.lat)*110.57,(r.lon-first.lon)*79); assert o.apply(d,axis=1).mean()<W.apply(d,axis=1).mean()   # picks wells nearer the unsafe one
