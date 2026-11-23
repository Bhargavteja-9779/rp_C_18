"""Attach NASA POWER climatology (0.5-degree cell) and elevation to geology-joined wells. Usage: build_env.py in_geo.csv out_env.csv"""
import sys, numpy as np, pandas as pd
w=pd.read_csv(sys.argv[1]); c=pd.read_csv("data/processed/climate_cells.csv")
w["clat"]=np.round(w.lat*2)/2; w["clon"]=np.round(w.lon*2)/2
m=w.merge(c.rename(columns={"lat":"clat","lon":"clon","precip":"clim_precip","temp":"clim_temp","rh":"clim_rh","solar":"clim_solar","elev":"elev_m"}),on=["clat","clon"],how="left").drop(columns=["clat","clon"])
print(len(w),"->",len(m),"| missing climate:",int(m.clim_precip.isna().sum()),"| precip range",m.clim_precip.min(),m.clim_precip.max())
m.to_csv(sys.argv[2],index=False)
