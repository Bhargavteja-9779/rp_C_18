"""Date-window download with recursive bisection for requests that time out. Usage: download_chunked.py <characteristic> <outdir> <startYear> <endYear> <window_years> <state codes...>"""
import sys, os, io, time, datetime as dt, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
char,outdir,y0,y1,win=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]); states=sys.argv[6:]; os.makedirs(outdir,exist_ok=True)
def fetch(s,a,b,depth=0):
    try:
        r=requests.get("https://api.waterdata.usgs.gov/samples-data/results/fullphyschem",params={"stateFips":f"US:{s}","characteristic":char,"mimeType":"text/csv","activityStartDateLower":a.isoformat(),"activityStartDateUpper":b.isoformat()},timeout=240)
        if r.status_code==200:
            if len(r.content)<80: return []
            return [pd.read_csv(io.BytesIO(r.content),dtype=str,low_memory=False)]
    except Exception: pass
    if (b-a).days<=31: return None
    m=a+(b-a)/2; L=fetch(s,a,m,depth+1); R=fetch(s,m+dt.timedelta(days=1),b,depth+1)
    return None if L is None or R is None else L+R
def do_state(s):
    f=f"{outdir}/{s}.csv"
    if os.path.exists(f) and os.path.getsize(f)>0: return s,"cached"
    parts=[]; ok=True
    for y in range(y0,y1+1,win):
        r=fetch(s,dt.date(y,1,1),dt.date(min(y+win-1,y1),12,31))
        if r is None: ok=False; break
        parts+=r
    if not ok: return s,"FAILED"
    if parts: pd.concat(parts).drop_duplicates().to_csv(f,index=False)
    else: open(f,"w").write("")
    return s,"ok"
with ThreadPoolExecutor(6) as ex:
    for s,st in ex.map(do_state,states): print(s,st,flush=True)
