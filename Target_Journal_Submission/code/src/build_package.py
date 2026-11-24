"""Assemble SUBMISSION_PACKAGE.zip (no code; code is available on request)."""
import sys, os, shutil, zipfile, glob, docx
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from authors import *
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
TITLE=open("manuscript/letter_title.txt").read().strip(); SYN=open("manuscript/letter_synopsis.txt").read().strip()
d=docx.Document(); d.styles["Normal"].font.name="Times New Roman"; d.styles["Normal"].font.size=Pt(11)
def P(t,b=False,i=False,al=None):
    p=d.add_paragraph(); r=p.add_run(t); r.bold=b; r.italic=i
    if al is not None: p.alignment=al
P(TITLE,b=True,al=WD_ALIGN_PARAGRAPH.CENTER); P(AUTH_LINE,al=WD_ALIGN_PARAGRAPH.CENTER); P(AFF_LINE,i=True,al=WD_ALIGN_PARAGRAPH.CENTER); P(CORR_LINE,i=True,al=WD_ALIGN_PARAGRAPH.CENTER)
P("Article type: Letter",i=True); P("Synopsis: "+SYN)
P("Keywords: private wells; groundwater arsenic; nitrate; uranium; fluoride; adaptive sampling; risk maps; transferability")
P("Author contributions. "+CONTRIB); P("Funding. "+FUNDING); P("Notes. "+COMPETING); P(AI_DECL); P(CODE)
P("Data availability: USGS Samples API (https://api.waterdata.usgs.gov/samples-data), USGS State Geologic Map Compilation (https://doi.org/10.5066/F7WH2N65) and NASA POWER (https://power.larc.nasa.gov), all public; result tables are provided as Supporting Data.")
P("Ethics: no human participants; public well-level data were used.")
d.core_properties.author=FIRST+"; "+SECOND; d.core_properties.last_modified_by=FIRST; d.core_properties.title="Title page and declarations"; d.core_properties.comments=""
d.save("manuscript/Title_Page_and_Declarations.docx")
for f in ("Letter_Manuscript","Supporting_Information","Supplementary_Protocol_and_Deviations","cover_letter","Title_Page_and_Declarations"): os.system(f"cd manuscript && soffice --headless --convert-to pdf {f}.docx >/dev/null 2>&1")
root="SUBMISSION_PACKAGE"; shutil.rmtree(root,ignore_errors=True)
def cp(src,dst): os.makedirs(os.path.dirname(f"{root}/{dst}"),exist_ok=True); shutil.copy(src,f"{root}/{dst}")
for ext in ("docx","pdf"):
    cp(f"manuscript/Letter_Manuscript.{ext}",f"01_Main_Manuscript/Letter_Manuscript.{ext}"); cp(f"manuscript/cover_letter.{ext}",f"02_Cover_Letter/Cover_Letter.{ext}")
    cp(f"manuscript/Supporting_Information.{ext}",f"03_Supporting_Information/Supporting_Information.{ext}"); cp(f"manuscript/Supplementary_Protocol_and_Deviations.{ext}",f"03_Supporting_Information/Supplementary_Protocol_and_Deviations.{ext}")
    cp(f"manuscript/Title_Page_and_Declarations.{ext}",f"00_Title_Page_and_Declarations/Title_Page_and_Declarations.{ext}")
cp("figures/toc_graphic.png","04_TOC_Graphic/TOC_graphic.png")
for i in (1,2,3): cp(f"figures/letter_fig{i}.png",f"05_Figures/Figure{i}.png")
data=[("tables/main_table.csv","main_table.csv")]+[(f,os.path.basename(f)) for f in sorted(glob.glob("tables/summary_*.csv"))+sorted(glob.glob("tables/statistics_*.csv"))+sorted(glob.glob("tables/abf_*.csv"))]
data+=[(f,"replay_"+os.path.basename(f)) for f in glob.glob("results/replay/*.csv")]
data+=[(f,"learner_"+os.path.basename(f)) for f in glob.glob("results/learner_check/*summary.csv")]
data+=[(f,"robustness_"+os.path.basename(f)) for f in glob.glob("results/robust_checks/*.csv")]
data+=[(f,"checks_"+os.path.basename(f)) for f in glob.glob("results/recheck/*.csv")]
data+=[(f,"hierarchical_ABF_"+f.split("/")[1]+"_"+os.path.basename(f)) for f in glob.glob("results/abfh_*/summary.csv")]
for src,name in data: cp(src,f"06_Supporting_Data_Tables/{name}")
open(f"{root}/06_Supporting_Data_Tables/README.txt","w").write("Result tables behind the Letter and Supporting Information (CSV). summary_* : enrichment at 5-30% of wells tested by method; statistics_* : paired tests with Holm correction; abf_* : adaptive Bayesian-mixture rule results; replay_* : replay of real sampling campaigns (including route length, time-respecting maps and larger batches); learner_*, robustness_*, checks_*, hierarchical_ABF_* : additional checks. Source data are public (USGS Samples API, USGS State Geologic Map Compilation, NASA POWER).\n")
with zipfile.ZipFile("SUBMISSION_PACKAGE.zip","w",zipfile.ZIP_DEFLATED) as z:
    for r,_,fs in os.walk(root):
        for f in sorted(fs): z.write(os.path.join(r,f),os.path.relpath(os.path.join(r,f),"."))
print("files:",sum(len(fs) for _,_,fs in os.walk(root)),"zip MB:",round(os.path.getsize("SUBMISSION_PACKAGE.zip")/1e6,2))
