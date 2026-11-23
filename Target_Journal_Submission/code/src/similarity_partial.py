"""Partial similarity check: shared 5- and 8-word sequences between the manuscript body and retrieved sources. Not a substitute for iThenticate."""
import json, re, sys, subprocess, glob
def toks(t): return re.findall(r"[a-z0-9µ]+",t.lower())
def sh(t,n): w=toks(t); return {" ".join(w[i:i+n]) for i in range(len(w)-n+1)}
ms=subprocess.run(["pdftotext","manuscript/Final_Manuscript.pdf","-"],capture_output=True,text=True).stdout.split("\nReferences")[0]
srcs={}
for f in sys.argv[1:]:
    if f.endswith(".json"):
        for c in json.load(open(f)):
            if c.get("abstract"): srcs[c["title"][:70]]=c["abstract"]
    else: srcs[f[-30:]]=subprocess.run(["pdftotext",f,"-"],capture_output=True,text=True).stdout
srcs["Lombard quote"]="The BRT 10 μg/L model estimates for testing data have an overall accuracy of 91.2%, sensitivity of 33.9%, and specificity of 98.2%."
M8,M5=sh(ms,8),sh(ms,5); rows=sorted(((len(M8&sh(t,8)),len(M5&sh(t,5)),k) for k,t in srcs.items()),reverse=True)
hits=[s for s in M8 if any(s in sh(t,8) for t in srcs.values())]
out=dict(n_sources=len(srcs),manuscript_8grams=len(M8),shared_8grams_total=len(hits),top=rows[:6],examples=hits[:10]); json.dump(out,open("results/similarity_partial.json","w"),indent=1); print(json.dumps(out,indent=1)[:900])
