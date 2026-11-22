"""Received->Accepted days from PubMed history dates. Usage: pubmed_dates.py "<ISSN>" N out.csv [mindate maxdate]"""
import sys, requests, random, csv, time, statistics as st, datetime as dt, xml.etree.ElementTree as ET
issn,n,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
E="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
W0=sys.argv[4] if len(sys.argv)>4 else "2025/01/01"
term=f'{issn}[ISSN] AND journal article[pt] AND ("{W0}"[dp]:"2026/11/22"[dp])'
ids=requests.get(E+"esearch.fcgi",params={"db":"pubmed","term":term,"retmax":3000,"retmode":"json"},timeout=60).json()["esearchresult"]["idlist"]
random.seed(0); random.shuffle(ids); ids=ids[:int(n*1.6)]
rows=[]
for i in range(0,len(ids),150):
    for t in range(5):
        x=requests.post(E+"efetch.fcgi",data={"db":"pubmed","id":",".join(ids[i:i+150]),"retmode":"xml"},timeout=120).text
        if x.lstrip().startswith("<?xml"): break
        time.sleep(2+3*t)
    else: continue
    for a in ET.fromstring(x).iter("PubmedArticle"):
        h={p.get("PubStatus"):p for p in a.iter("PubMedPubDate")}
        if "received" in h and "accepted" in h:
            g=lambda p:dt.date(int(p.find("Year").text),int(p.find("Month").text),int(p.find("Day").text))
            d1,d2=g(h["received"]),g(h["accepted"])
            doi=next((e.text for e in a.iter("ArticleId") if e.get("IdType")=="doi"),"")
            rows.append((a.findtext(".//Journal/Title"),(a.findtext(".//ArticleTitle") or "")[:150],doi,d1,d2,(d2-d1).days))
    time.sleep(0.4)
rows=rows[:n]; d=sorted(r[5] for r in rows)
if d: print(issn,"n",len(d),"median",st.median(d),"p75",d[int(.75*len(d))],"max",d[-1])
else: print(issn,"no dated records; ids",len(ids))
csv.writer(open(out,"w",newline="")).writerows([["journal","title","doi","received","accepted","days"]]+rows)
