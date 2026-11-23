"""Stage 1: recompute received->accepted days for ES&T Letters from PubMed history dates; integrity counts; newest papers."""
import requests, time, random, csv, statistics as st, datetime as dt, xml.etree.ElementTree as ET, sys, json
E="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"; ISSN=sys.argv[1] if len(sys.argv)>1 else "2328-8930"; tag=sys.argv[2] if len(sys.argv)>2 else "estl"
def get(url,**k):
    for t in range(6):
        r=requests.request(k.pop("method","GET"),url,timeout=90,**k)
        if r.status_code==200 and ("esearchresult" in r.text or r.text.lstrip().startswith("<?xml")): return r
        time.sleep(3+3*t)
    return r
def ids(q,n=3000): return get(E+"esearch.fcgi",params={"db":"pubmed","term":q,"retmax":n,"retmode":"json"}).json()["esearchresult"]["idlist"]
def fetch(idl):
    out=[]
    for i in range(0,len(idl),150):
        r=get(E+"efetch.fcgi",method="POST",data={"db":"pubmed","id":",".join(idl[i:i+150]),"retmode":"xml"})
        for a in ET.fromstring(r.text).iter("PubmedArticle"):
            h={p.get("PubStatus"):p for p in a.iter("PubMedPubDate")}
            g=lambda p:dt.date(int(p.find("Year").text),int(p.find("Month").text),int(p.find("Day").text))
            doi=next((e.text for e in a.iter("ArticleId") if e.get("IdType")=="doi"),"")
            out.append(dict(title="".join(a.find(".//ArticleTitle").itertext())[:140],doi=doi,received=g(h["received"]) if "received" in h else None,accepted=g(h["accepted"]) if "accepted" in h else None,pubtype=[x.text for x in a.iter("PublicationType")]))
        time.sleep(0.5)
    return out
base=f'{ISSN}[ISSN] AND journal article[pt]'
allp=fetch(ids(base+' AND 2022:2026[dp]'))
rows=[r for r in allp if r["received"] and r["accepted"] and "Retracted Publication" not in r["pubtype"]]
for r in rows: r["days"]=(r["accepted"]-r["received"]).days
rows=[r for r in rows if r["days"]>=0]
d=sorted(r["days"] for r in rows); q=lambda p:d[min(len(d)-1,int(p*len(d)))]
res=dict(issn=ISSN,n_all=len(allp),n_dated=len(rows),median=st.median(d),p75=q(.75),p90=q(.9),max=d[-1])
cut=dt.date(2026,5,23); rec=[r["days"] for r in rows if r["accepted"]>=cut]
res["last6m_n"]=len(rec); 
if rec: res["last6m_median"]=st.median(rec); sr=sorted(rec); res["last6m_p75"]=sr[min(len(sr)-1,int(.75*len(sr)))]
byy={}
for r in rows: byy.setdefault(r["accepted"].year,[]).append(r["days"])
res["by_accept_year"]={y:dict(n=len(v),median=st.median(v),p75=sorted(v)[min(len(v)-1,int(.75*len(v)))]) for y,v in sorted(byy.items())}
res["retraction_notices_2022_2026"]=len(ids(f'{ISSN}[ISSN] AND (retraction of publication[pt] OR retracted publication[pt] OR expression of concern[pt])'))
json.dump(res,open(f"RECHECK/journal_{tag}_stats.json","w"),indent=1,default=str); print(json.dumps(res,indent=1,default=str))
random.seed(1); samp=random.sample(rows,min(40,len(rows)))
with open(f"RECHECK/acceptance_time_{tag}_sample.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["title","doi","received","accepted","days"]); [w.writerow([r["title"],r["doi"],r["received"],r["accepted"],r["days"]]) for r in samp]
newest=sorted([r for r in rows],key=lambda r:r["accepted"],reverse=True)[:10]
json.dump([dict(title=r["title"],doi=r["doi"],accepted=str(r["accepted"]),days=r["days"]) for r in newest],open(f"RECHECK/journal_{tag}_newest10.json","w"),indent=1)
