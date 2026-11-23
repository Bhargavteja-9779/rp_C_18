"""RECHECK stage 6: re-verify every reference against Crossref/arXiv (DOI resolves, title and year match). Output RECHECK/reference_verification.csv"""
import json, re, requests, time, difflib, csv, sys
H={"User-Agent":"research-bot/1.0"}; refs=json.load(open("manuscript/references.json")); out=[]
def norm(s): return " ".join(re.sub(r"[^a-z0-9 ]"," ",re.sub("<[^>]+>"," ",s).lower()).split())
def sim_of(a,b):
    m=difflib.SequenceMatcher(None,a,b,autojunk=False).find_longest_match(0,len(a),0,len(b)); return m.size/max(1,len(a))
for r in refs:
    t=r["text"]; m=re.search(r"https://doi.org/(\S+?)(?:\s|$)",t); a=re.search(r"arXiv:(\d{4}\.\d{4,5})",t); res=dict(key=r["key"],kind="",status="",detail="")
    try:
        if m:
            doi=m.group(1).rstrip(".)"); res["kind"]="DOI "+doi
            if doi.startswith("10.5066/"):
                x=requests.get(f"https://api.datacite.org/dois/{doi}",timeout=40); res["status"]="OK" if x.status_code==200 and "state geologic map" in x.text.lower() else f"DataCite HTTP {x.status_code}"; res["detail"]="DataCite record "+("found" if x.status_code==200 else "missing"); out.append(res); continue
            for _try in range(5):
                x=requests.get(f"https://api.crossref.org/works/{doi}",headers=H,timeout=40)
                if x.status_code!=429: break
                time.sleep(5+5*_try)
            if x.status_code==200:
                msg=x.json()["message"]; ct=(msg.get("title") or [""])[0]; yr=msg["issued"]["date-parts"][0][0]
                sim=sim_of(norm(ct),norm(t))
                res["status"]="OK" if sim>0.7 and abs(yr-r["year"])<=1 else "CHECK"; res["detail"]=f"crossref title={ct[:60]!r} year={yr} title-in-ref={sim:.2f}"
            elif x.status_code in (404,): res["status"]="DOI NOT FOUND"
            else: res["status"]=f"HTTP {x.status_code} (rate limit? recheck)"
        elif a:
            res["kind"]="arXiv "+a.group(1)
            x=requests.get("https://export.arxiv.org/api/query",params={"id_list":a.group(1)},timeout=60).text
            ti=re.search(r"<title>(.*?)</title>",x.split("<entry>")[1] if "<entry>" in x else "",re.S)
            if ti:
                at=" ".join(ti.group(1).split()); sim=sim_of(norm(at),norm(t)); res["status"]="OK" if sim>0.7 else "CHECK"; res["detail"]=f"arxiv title={at[:60]!r} title-in-ref={sim:.2f}"
            else: res["status"]="arXiv ID NOT FOUND"
            time.sleep(3)
        else: res["kind"]="no DOI/arXiv (document or web source)"; res["status"]="MANUAL"; res["detail"]=t[:90]
    except Exception as e: res["status"]="ERROR "+str(e)[:50]
    out.append(res); time.sleep(0.3)
with open("RECHECK/reference_verification.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["key","kind","status","detail"]); w.writeheader(); w.writerows(out)
from collections import Counter; print(Counter(o["status"] for o in out)); [print(o) for o in out if o["status"] not in("OK",)]
