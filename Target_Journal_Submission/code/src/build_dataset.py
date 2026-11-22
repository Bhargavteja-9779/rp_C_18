"""Build well-level table: earliest valid arsenic result per well; label = detected/measured > threshold."""
import glob, sys, numpy as np, pandas as pd
USE=["Location_Identifier","Location_StatePostalCode","Location_CountyName","Location_HUCEightDigitCode","Location_LatitudeStandardized","Location_LongitudeStandardized",
 "Location_Type","Activity_Media","Activity_StartDate","Activity_TopDepthMeasure","Activity_BottomDepthMeasure","Activity_BottomDepthMeasureUnit","Activity_TopDepthMeasureUnit",
 "Result_Characteristic","Result_ResultDetectionCondition","Result_Measure","Result_MeasureUnit","Result_SampleFraction","DetectionLimit_MeasureA","DetectionLimit_MeasureUnitA","USGSSampleAquifer"]
d=pd.concat([pd.read_csv(f,usecols=lambda c:c in USE,dtype=str,low_memory=False) for f in sorted(glob.glob(sys.argv[1]+"/*.csv")) if open(f).read(20)],ignore_index=True)
n0=len(d); log=[f"raw rows {n0}"]
d=d[(d.Location_Type=="Well")&(d.Activity_Media=="Water")&(d.Result_Characteristic=="Arsenic")]; log.append(f"well/water/arsenic rows {len(d)}")
d=d[d.Result_MeasureUnit.fillna("ug/L").isin(["ug/L"])|d.Result_MeasureUnit.isna()]
nd=d.Result_ResultDetectionCondition.fillna("").str.contains("Not Detected")
d["val"]=pd.to_numeric(d.Result_Measure,errors="coerce"); d["dl"]=pd.to_numeric(d.DetectionLimit_MeasureA,errors="coerce")
d.loc[nd,"val"]=0.0   # non-detect: below its detection limit; flagged below
d=d[~(d.val.isna())]
d=d[~(nd&(d.dl>5))]   # drop non-detects whose limit exceeds the strictest threshold (5 ug/L)
d["date"]=pd.to_datetime(d.Activity_StartDate,errors="coerce")
d["lat"]=pd.to_numeric(d.Location_LatitudeStandardized,errors="coerce"); d["lon"]=pd.to_numeric(d.Location_LongitudeStandardized,errors="coerce")
d=d.dropna(subset=["lat","lon","date"]); d=d[d.lat.between(24,50)&d.lon.between(-125,-66)]
dep=pd.to_numeric(d.Activity_BottomDepthMeasure,errors="coerce").fillna(pd.to_numeric(d.Activity_TopDepthMeasure,errors="coerce"))
u=d.Activity_BottomDepthMeasureUnit.fillna(d.Activity_TopDepthMeasureUnit).fillna("ft")
d["depth_ft"]=np.where(u.isin(["m","meters"]),dep*3.281,dep)
d=d.sort_values(["Location_Identifier","date"])
w=d.groupby("Location_Identifier").agg(lat=("lat","first"),lon=("lon","first"),state=("Location_StatePostalCode","first"),county=("Location_CountyName","first"),
  huc8=("Location_HUCEightDigitCode","first"),aquifer=("USGSSampleAquifer","first"),depth_ft=("depth_ft","first"),date=("date","first"),val=("val","first"),n_samples=("val","size")).reset_index()
log.append(f"wells {len(w)}; dup coordinates across ids {w.duplicated(['lat','lon']).sum()}")
w["y10"]=(w.val>10).astype(int); w["y5"]=(w.val>5).astype(int)
log.append(f"unsafe>10: {w.y10.sum()} ({w.y10.mean():.3%}); >5: {w.y5.sum()} ({w.y5.mean():.3%}); states {w.state.nunique()}")
log.append("depth available: %.1f%%; aquifer available: %.1f%%"%(100*w.depth_ft.notna().mean(),100*w.aquifer.notna().mean()))
w.to_csv(sys.argv[2],index=False); open(sys.argv[2].replace(".csv","_build_log.txt"),"w").write("\n".join(log)); print("\n".join(log))
