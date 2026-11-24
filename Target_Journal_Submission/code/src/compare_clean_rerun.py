"""Compare clean-environment reruns with stored results. Usage: compare_clean_rerun.py <clean_dir> <scenario...>. Output results/recheck/clean_rerun_all.json"""
import sys, json, os, pandas as pd
cd=sys.argv[1]; out={}
if os.path.exists("results/recheck/clean_rerun_all.json"): out=json.load(open("results/recheck/clean_rerun_all.json"))
for sc in sys.argv[2:]:
    a=f"results/{sc}/raw_results.csv"; b=f"{cd}/results/{sc}/raw_results.csv"
    if not (os.path.exists(a) and os.path.exists(b)): print(sc,"missing"); continue
    A=pd.read_csv(a); B=pd.read_csv(b)
    for d in (A,B): d["e"]=d.found_20/(0.2*d.n_unsafe)
    ma=A.groupby(["method","unit"]).e.mean().unstack(0); mb=B.groupby(["method","unit"]).e.mean().unstack(0)
    ta=json.load(open(f"results/{sc}/tuning.json")); tb=json.load(open(f"{cd}/results/{sc}/tuning.json"))
    out[sc]=dict(tuning_identical=bool(ta["params"]==tb["params"] and ta["h_kappa"]==tb["h_kappa"] and ta["eval_states"]==tb["eval_states"]),max_abs_diff=float((ma-mb.reindex(ma.index)).abs().max().max()),n_methods=int(ma.shape[1]),n_states=int(ma.shape[0]))
    print(sc,out[sc])
json.dump(out,open("results/recheck/clean_rerun_all.json","w"),indent=1)
