"""Build verified reference list (Crossref / arXiv / DataCite metadata) -> manuscript/references.json"""
import requests, time, json, html, re, xml.etree.ElementTree as ET
H={"User-Agent":"research-bot/1.0"}
DOIS="""10.1021/acs.est.4c01327 10.1021/acs.est.1c08682 10.1016/j.jhazmat.2026.144066 10.1016/j.ecoenv.2026.120627 10.1007/s10653-026-03004-2 10.1007/s10653-026-03510-3 10.1007/s10661-026-15974-y
10.1016/j.scitotenv.2022.158277 10.1002/tox.70005 10.1016/j.scitotenv.2022.159360 10.1021/acs.est.6c02761 10.1021/acs.est.5c07661 10.2166/wh.2020.059 10.1097/PHH.0000000000001575 10.2166/wh.2021.018
10.1016/j.watres.2024.121848 10.1016/j.watres.2023.119745 10.1016/j.watres.2024.122498 10.1016/j.watres.2022.118787 10.1016/j.watres.2024.122404
10.1021/acs.est.0c05239 10.1021/acs.est.0c06740 10.1029/2025GH001666 10.1111/gwat.13020 10.1126/science.aba1510
10.1080/01621459.1990.10474975 10.1021/acs.estlett.5c00503 10.1021/acs.estlett.3c00504 10.1145/3219819.3219896 10.1111/ecog.02881 10.1111/2041-210X.13650 10.1016/j.ecolmodel.2021.109692 10.1038/s41467-020-18321-y 10.1111/2041-210x.13107 10.2307/3001968 10.1214/aos/1176344552""".split()
ARX="1610.00580 2102.11118 2605.08113 2602.17605 2303.00141 2604.22787 2503.22771 2410.19865 1206.6406".split()
def name(a): 
    g=a.get("given",""); ini=" ".join(p[0]+"." for p in re.split(r"[ \-]",g) if p) if g else ""
    return f"{a.get('family','')}, {ini}".strip(", ")
refs=[]
for d in DOIS:
    m=None
    for t in range(5):
        r=requests.get(f"https://api.crossref.org/works/{d}",headers=H,timeout=40)
        if r.status_code==200: m=r.json()["message"]; break
        time.sleep(3+3*t)
    if not m: print("FAILED",d); continue
    au=m.get("author",[]); als=[name(a) for a in au]; fam=au[0]["family"] if au else "Anon"; yr=m["issued"]["date-parts"][0][0]
    authors=", ".join(als[:6])+(", et al." if len(als)>6 else "")
    ct=html.unescape((m.get("container-title") or [""])[0]); ti=re.sub(r"\s+"," ",html.unescape(re.sub("<[^>]+>","",m["title"][0]))).strip().rstrip(".")
    vol=m.get("volume"); pg=m.get("page")
    s=f"{authors} ({yr}). {ti}. {ct}"+(f" {vol}" if vol else "")+(f", {pg}" if pg else "")+f". https://doi.org/{m['DOI']}"
    refs.append(dict(key=f"{fam} {yr}",text=s,fam=fam,year=yr,n_auth=len(als)))
A="{http://www.w3.org/2005/Atom}"
for i in ARX:
    x=requests.get("https://export.arxiv.org/api/query",params={"id_list":i},timeout=60).text; e=ET.fromstring(x).find(A+"entry")
    nm=[a.find(A+"name").text for a in e.findall(A+"author")]; fam=nm[0].split()[-1]; yr=e.find(A+"published").text[:4]
    ini=lambda n:", ".join([n.split()[-1]])+", "+" ".join(p[0]+"." for p in n.split()[:-1])
    s=f"{', '.join(ini(n) for n in nm[:6])}{', et al.' if len(nm)>6 else ''} ({yr}). {' '.join(e.find(A+'title').text.split())}. arXiv:{i}"
    refs.append(dict(key=f"{fam} {yr}",text=s,fam=fam,year=int(yr),n_auth=len(nm))); time.sleep(3)
# manual entries whose metadata were read from the documents themselves (see REVIEW/citation_audit.md)
refs+= [dict(key="Appiah 2025",fam="Appiah",year=2025,n_auth=5,text="Appiah, P., Engle, M.A., Mariani, M.C., Ma, L., Lopez, N. (2025). Machine learning for predicting groundwater quality and understanding controls on contaminants. Preprint, University of Texas at El Paso, https://www.cs.utep.edu/vladik/utepnmsu25appiah.pdf."),
 dict(key="Ma 2015",fam="Ma",year=2015,n_auth=4,text="Ma, Y., Sutherland, D.J., Garnett, R., Schneider, J. (2015). Active pointillistic pattern search. Proceedings of the International Conference on Artificial Intelligence and Statistics (AISTATS), 2015."),
 dict(key="NASA 2026",fam="NASA",year=2026,n_auth=0,text="NASA Langley Research Center (2026). Prediction Of Worldwide Energy Resources (POWER) Project: annual climatology (precipitation, 2-m temperature, relative humidity, all-sky solar radiation; community AG) and elevation at 0.5-degree cell centres. https://power.larc.nasa.gov, accessed 23 November 2026."),
 dict(key="CDC 2026",fam="CDC",year=2026,n_auth=0,text="Vermont Department of Health, in: CDC (2026). Private well ranking indices. Centers for Disease Control and Prevention, https://www.cdc.gov/environmental-health-practice/media/pdfs/2026/07/Private-Well-Ranking-Indices-508.pdf."),
 dict(key="USGS 2026",fam="USGS",year=2026,n_auth=0,text="U.S. Geological Survey (2026). USGS Samples Data API (discrete water-quality results), https://api.waterdata.usgs.gov/samples-data, accessed 22–23 November 2026."),
 dict(key="Horton 2017",fam="Horton",year=2017,n_auth=1,text="Horton, J.D. (2017). The State Geologic Map Compilation (SGMC) geodatabase of the conterminous United States (ver. 1.1, August 2017). U.S. Geological Survey data release. https://doi.org/10.5066/F7WH2N65")]
refs.sort(key=lambda r:(r["fam"].lower(),r["year"]))
json.dump(refs,open("manuscript/references.json","w"),indent=1); print(len(refs),"references")
for r in refs: print(" ",r["key"],"|",r["text"][:110])
