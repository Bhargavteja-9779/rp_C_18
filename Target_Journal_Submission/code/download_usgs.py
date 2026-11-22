"""Download USGS Samples results (discrete water-quality) per state for one characteristic, validating each file parses."""
import sys, os, io, time, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
char, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
STATES = "01 02 04 05 06 08 09 10 11 12 13 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 44 45 46 47 48 49 50 51 53 54 55 56".split()
def get(s):
    f=f"{outdir}/{s}.csv"
    if os.path.exists(f):
        try: pd.read_csv(f,dtype=str,low_memory=False); return s,"cached"
        except Exception: os.remove(f)
    for t in range(4):
        try:
            r=requests.get("https://api.waterdata.usgs.gov/samples-data/results/fullphyschem",
                params={"stateFips":f"US:{s}","characteristic":char,"mimeType":"text/csv"},timeout=600)
            if r.status_code==200:
                if len(r.content)<50: open(f,"w").write(""); return s,"empty"
                pd.read_csv(io.BytesIO(r.content),dtype=str,low_memory=False)
                open(f,"wb").write(r.content); return s,"ok"
        except Exception as e: err=str(e)[:60]
        time.sleep(5*(t+1))
    return s,"FAILED"
with ThreadPoolExecutor(8) as ex:
    for s,st in ex.map(get,STATES): print(s,st,flush=True)
