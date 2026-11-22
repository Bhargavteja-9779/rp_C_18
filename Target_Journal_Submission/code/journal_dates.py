"""Measure Received->Accepted days from Crossref metadata (Springer Nature 'ArticleHistory' assertions).
Usage: journal_dates.py ISSN N out.csv"""
import sys, requests, random, csv, datetime as dt, time
issn, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
def pd(x):
    x=x.strip()
    for f in ('%d %B %Y','%Y-%m-%d','%B %d, %Y'):
        try: return dt.datetime.strptime(x[:len(x)],f).date()
        except ValueError: pass
    raise ValueError(x)
H={"User-Agent":"research-bot/1.0"}
rows=[]; cursor="*"; seen=0
frm=(dt.date(2026,11,22)-dt.timedelta(days=548)).isoformat()
while len(rows)<400 and seen<1500:
    r=requests.get(f"https://api.crossref.org/journals/{issn}/works",params={"filter":f"type:journal-article,from-pub-date:{frm}","rows":200,"cursor":cursor,"select":"DOI,title,assertion,published,container-title"},headers=H,timeout=60)
    if r.status_code!=200: print("ERR",r.status_code); break
    m=r.json()["message"]; items=m["items"]
    if not items: break
    cursor=m["next-cursor"]; seen+=len(items)
    for it in items:
        a={x["name"]:x["value"] for x in it.get("assertion",[]) if "value" in x and "name" in x}
        rec,acc=a.get("received"),a.get("accepted")
        if rec and acc:
            try: d1=pd(rec); d2=pd(acc)
            except Exception: continue
            rows.append((it["container-title"][0] if it.get("container-title") else "",it["title"][0] if it.get("title") else "",it["DOI"],d1,d2,(d2-d1).days))
print(issn,"scanned",seen,"with dates",len(rows))
random.seed(0); random.shuffle(rows); rows=rows[:n]
import statistics as s
if rows:
    d=sorted(r[5] for r in rows); q=lambda p:d[min(len(d)-1,int(p*len(d)))]
    print("n",len(d),"median",s.median(d),"p75",q(.75),"max",d[-1])
with open(out,"w",newline="") as f:
    w=csv.writer(f); w.writerow(["journal","title","doi","received","accepted","days"]); w.writerows(rows)
