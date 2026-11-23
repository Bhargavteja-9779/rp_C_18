"""Reproduce everything. Usage: python run_all.py --mode quick|full  [--skip-download]
Run from the code/ directory. Paths are relative to the submission root (../)."""
import argparse, os, subprocess, sys
ap=argparse.ArgumentParser(); ap.add_argument("--mode",default="quick"); ap.add_argument("--skip-download",action="store_true"); a=ap.parse_args()
root=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
def run(cmd): print(">>"," ".join(cmd),flush=True); subprocess.run(cmd,cwd=root,check=True)
py=sys.executable; c="code/"
if not a.skip_download and not os.path.isdir(f"{root}/data/raw/as"): run([py,c+"download_usgs.py","Arsenic","data/raw/as"])
os.makedirs(f"{root}/data/processed",exist_ok=True)
run([py,c+"src/build_dataset.py","data/raw/as","data/processed/wells_as.csv"])
if a.mode=="quick":
    run([py,c+"src/experiment.py","--data","data/processed/wells_as.csv","--label","y10","--out","results/quick","--mode","quick","--jobs","2"]); run([py,c+"src/analyze.py","results/quick","tables"]); sys.exit()
run([py,"-c","import pandas as pd,numpy as np;w=pd.read_csv('data/processed/wells_as.csv');x=w.lon*111.32*np.cos(np.radians(w.lat));y=w.lat*110.57;w['cell']=np.floor(x).astype(int).astype(str)+'_'+np.floor(y).astype(int).astype(str);w.sort_values('date').drop_duplicates('cell').drop(columns='cell').to_csv('data/processed/wells_as_thin1km.csv',index=False)"])
run([py,c+"src/experiment.py","--data","data/processed/wells_as.csv","--label","y10","--out","results/as10"])
run([py,c+"src/experiment.py","--data","data/processed/wells_as.csv","--label","y5","--out","results/as5"])
run([py,c+"src/experiment.py","--data","data/processed/wells_as.csv","--label","y10","--out","results/as10_blocks","--units","kmeans","--tuned","results/as10/tuning.json"])
run([py,c+"src/experiment.py","--data","data/processed/wells_as_thin1km.csv","--label","y10","--out","results/as10_thin"])
run([py,c+"src/extra_experiments.py","y10","results/extra_as10"]); run([py,c+"src/extra_experiments.py","y5","results/extra_as5"])
run([py,c+"src/extra_checks.py"]); run([py,c+"src/m7_weight_check.py"])
# uranium: python code/download_usgs.py Uranium data/raw/u ; python code/src/build_dataset.py data/raw/u data/processed/wells_u.csv Uranium 30 10 ; then experiment.py --label y30 --ntune 4 --out results/u30 and --label y10 --out results/u10 (optional)
for r in ("as10","as5","as10_blocks","as10_thin"): run([py,c+"src/analyze.py",f"results/{r}","tables"])
run([py,c+"src/analyze_extra.py","results/extra_as10","as10"]); run([py,c+"src/analyze_extra.py","results/extra_as5","as5"])
run([py,c+"src/make_report_assets.py"]); run([py,c+"src/make_extra_figures.py"]); run([py,c+"src/make_manuscript.py"])
