"""RECHECK stage 9: verify that key numbers printed in the Letter match the result files. Output RECHECK/consistency_check.csv"""
import re, subprocess, pandas as pd, json, csv
L=subprocess.run(["pdftotext","manuscript/Letter_Manuscript.pdf","-"],capture_output=True,text=True).stdout.replace("\n"," ")
S=lambda t:pd.read_csv(f"tables/summary_{t}.csv",index_col=0); rv=pd.read_csv("tables/random_vs_blocked_summary.csv",index_col=0)
ab=lambda run,m:pd.read_csv(f"results/abf_{run}/abf.csv").groupby(["method","unit"]).enr_20.mean().unstack(0)[m].mean()
checks=[("arsenic wells 53,294","53,294",None),("uranium wells 28,117","28,117",None),("fluoride wells 150,299","150,299",None),
("random-split ROC-AUC (arsenic)",f"{rv.loc['random_5fold','auc_roc']:.2f}",None),("held-out ROC-AUC (arsenic)",f"{rv.loc['leave_state_out','auc_roc']:.2f}",None),
("static map As>10 enrichment",f"{ab('as10','M1_map'):.2f}",None),("feedback As>10",f"{ab('as10','M4_feedback'):.2f}",None),("ABF As>10",f"{ab('as10','ABF'):.2f}",None),
("follow-unsafe As>10",f"{ab('as10','H1_follow_unsafe'):.2f}",None),("static map As>5",f"{ab('as5','M1_map'):.2f}",None),("ABF As>5",f"{ab('as5','ABF'):.2f}",None),
("static map F>2",f"{ab('f2','M1_map'):.2f}",None),("hybrid F>2",f"{ab('f2','M5_hybrid'):.2f}",None),("ABF F>2",f"{ab('f2','ABF'):.2f}",None),
("tests per unsafe well random",f"{100/ (pd.read_csv('tables/unsafe_per_100_tests_as10.csv',index_col=0).iloc[:,0].get('M1_static_lgbm',1)*0+ (pd.read_csv('results/as10/raw_results.csv').query('method==\"M1_static_lgbm\"').groupby('unit').first().eval('n_unsafe/n_wells*100').mean())):.1f}",None)]
rows=[]
for name,val,_ in checks:
    rows.append(dict(item=name,value_from_file=val,found_in_letter=val in L))
for tag in ("learner","synthetic"):
    pass

import os
for k,lab in (("as10","replay As>10"),("as5","replay As>5"),("f2","replay F>2"),("u10","replay U>10")):
    f=f"results/replay/replay_{k}_summary.csv"
    if os.path.exists(f):
        r=pd.read_csv(f).iloc[0]
        items=[("campaigns",f"{int(r.n_campaigns)}")]+([("real order",f"{r.real_mean:.2f}"),("ABF",f"{r.ABF_mean:.2f}"),("feedback",f"{r.feedback_mean:.2f}")] if k=="as10" else [])
        for nm,v in items:
            rows.append(dict(item=f"{lab} {nm}",value_from_file=v,found_in_letter=v in L))
tr=pd.read_csv("results/replay/travel_as10_summary.csv").iloc[0]
for nm,v in (("route km follow",f"{tr.follow_km_per_unsafe:.0f} km"),("route km ABF",f"{tr.ABF_km_per_unsafe:.0f} km"),("route km real",f"{tr.real_km_per_unsafe:.0f} km")): rows.append(dict(item=nm,value_from_file=v,found_in_letter=v in L))
df=pd.DataFrame(rows); df.to_csv("RECHECK/consistency_check.csv",index=False); print(df.to_string()); print("ALL FOUND" if df.found_in_letter.all() else "MISMATCHES: "+", ".join(df[~df.found_in_letter].item))
