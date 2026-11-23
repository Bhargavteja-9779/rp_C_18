"""Fetch NASA POWER annual climatology (precip, T2M, RH2M, solar) and elevation at 0.5-degree cell centres that contain wells."""
import pandas as pd, numpy as np, requests, time, os, sys
from concurrent.futures import ThreadPoolExecutor
cells=set()
for f in ("data/processed/wells_as.csv","data/processed/wells_u.csv","data/processed/wells_f.csv","data/processed/wells_as_full.csv"):
    w=pd.read_csv(f,usecols=["lat","lon"]); cells|=set(zip((np.round(w.lat*2)/2).tolist(),(np.round(w.lon*2)/2).tolist()))
cells=sorted(cells); print(len(cells),"cells",flush=True); out="data/processed/climate_cells.csv"
done=pd.read_csv(out) if os.path.exists(out) else pd.DataFrame(columns=["lat","lon"]); have=set(zip(done.lat,done.lon)); todo=[c for c in cells if c not in have]
def get(c):
    for t in range(5):
        try:
            r=requests.get("https://power.larc.nasa.gov/api/temporal/climatology/point",params={"parameters":"PRECTOTCORR,T2M,RH2M,ALLSKY_SFC_SW_DWN","community":"AG","longitude":c[1],"latitude":c[0],"format":"JSON"},timeout=60)
            if r.status_code==200:
                j=r.json(); p=j["properties"]["parameter"]; return dict(lat=c[0],lon=c[1],precip=p["PRECTOTCORR"]["ANN"],temp=p["T2M"]["ANN"],rh=p["RH2M"]["ANN"],solar=p["ALLSKY_SFC_SW_DWN"]["ANN"],elev=j["geometry"]["coordinates"][2])
        except Exception: pass
        time.sleep(2+2*t)
    return None
rows=[]
with ThreadPoolExecutor(6) as ex:
    for i,r in enumerate(ex.map(get,todo)):
        if r: rows.append(r)
        if i%500==0: print(i,len(rows),flush=True)
pd.concat([done,pd.DataFrame(rows)]).to_csv(out,index=False); print("saved",len(rows),"new;",len(todo)-len(rows),"failed")
