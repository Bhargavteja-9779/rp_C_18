"""Build manuscript/Supplementary_Protocol_and_Deviations.docx from code/experiments/{protocol,deviations}.md, with journal-selection notes removed and process wording neutral."""
import re, sys, os, docx
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from authors import *
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
dev=open("code/experiments/deviations.md").read(); proto=open("code/experiments/protocol.md").read()
items=re.split(r"\n(?=\d+\. )",dev); out=[]
for it in items:
    m=re.match(r"(\d+)\. ",it)
    if m and m.group(1) in ("27","28"): continue
    if m and m.group(1)=="35": it="35. (2026-11-23) A second implementation of a Bayesian-mixture feedback method (experts over bandwidth and prior trust) was started alongside the method of item 26 and discarded after producing output for two scenarios. Its results were not used anywhere, and no design choice of the method in item 26 was influenced by them."
    it=re.sub(r"\(2026-11-2\d, [^)]*?(round|RECHECK)[^)]*?\)",lambda m_:"("+re.search(r"2026-11-2\d",m_.group(0)).group(0)+")",it); it=re.sub(r", round \d+","",it)
    it=re.sub(r"Reason: reviews [^.]*\.","Reason: to test how sensitive the conclusions are to the choices made.",it)
    it=re.sub(r", added in response to a review concern about [^:]*:",", added as an additional check:",it); it=re.sub(r"\(added after the main runs, in response to a review on baseline fairness\)","(added after the main runs)",it)
    it=it.replace("the user accepted APC charges","")
    out.append(it)
txt="\n".join(out); txt=re.sub(r"# ROUND 4 PRE-REGISTRATION[^\n]*","# Pre-registration of the adaptive method (written before any run of that method)",txt)
d=docx.Document(); d.styles["Normal"].font.name="Times New Roman"; d.styles["Normal"].font.size=Pt(10.5)
for s in d.sections: s.left_margin=s.right_margin=Cm(2.3)
def P(t,b=False,i=False,al=None):
    p=d.add_paragraph(); r=p.add_run(t); r.bold=b; r.italic=i
    if al is not None: p.alignment=al
TITLE=open("manuscript/letter_title.txt").read().strip()
P("Supplementary Protocol and Deviation Log",b=True,al=WD_ALIGN_PARAGRAPH.CENTER); P("for: "+TITLE,i=True,al=WD_ALIGN_PARAGRAPH.CENTER); P(AUTH_LINE,al=WD_ALIGN_PARAGRAPH.CENTER); P(AFF_LINE,i=True,al=WD_ALIGN_PARAGRAPH.CENTER)
P("Part A. Protocol written before the first analysis. Part B. Every later deviation and addition, with its date and reason. Items were recorded before the runs they concern.",i=True)
d.add_heading("Part A. Protocol",1)
for l in proto.split("\n"):
    l=l.rstrip()
    if not l: continue
    if l.startswith("#"): d.add_heading(l.lstrip("# ").strip(),2)
    else: P(l.replace("**",""))
d.add_heading("Part B. Deviations and additions",1)
for l in txt.split("\n"):
    l=l.rstrip()
    if not l or l.startswith("# Deviations"): continue
    if l.startswith("#"): d.add_heading(l.lstrip("# ").strip(),2)
    else: P(l)
d.core_properties.author=FIRST+"; "+SECOND; d.core_properties.last_modified_by=FIRST; d.core_properties.title="Supplementary Protocol and Deviation Log"; d.core_properties.comments=""
d.save("manuscript/Supplementary_Protocol_and_Deviations.docx"); print("protocol document saved;",len(out),"items")
bad=[l[:140] for l in txt.split("\n") if re.search(r"\buser\b|session|Claude|assistant|instruction|RECHECK",l,re.I)]; print("flagged lines:",len(bad)); [print(" -",b) for b in bad]
