"""Attach USGS SGMC geology (generalized lithology, age) to wells by point-in-polygon join. Usage: build_geology.py in.csv out.csv"""
import sys, pandas as pd, geopandas as gpd
w=pd.read_csv(sys.argv[1]); g=gpd.read_file("data/raw/sgmc/USGS_SGMC_Shapefiles/SGMC_Geology.shp",columns=["GENERALIZE","AGE_MIN","AGE_MAX","MAJOR1","geometry"])
pts=gpd.GeoDataFrame(w,geometry=gpd.points_from_xy(w.lon,w.lat),crs="EPSG:4326").to_crs(g.crs)
j=gpd.sjoin(pts,g,how="left",predicate="within").drop_duplicates(subset="Location_Identifier")
out=j.drop(columns=["geometry","index_right"]).rename(columns={"GENERALIZE":"geo_lith","AGE_MIN":"geo_age_min","AGE_MAX":"geo_age_max","MAJOR1":"geo_major"})
for c in ("geo_lith","geo_age_min","geo_age_max","geo_major"): out[c]=out[c].fillna("unknown")
out.to_csv(sys.argv[2],index=False); print(len(w),"->",len(out),"| matched",(out.geo_lith!="unknown").mean().round(3),"| lithology classes",out.geo_lith.nunique(),"| age classes",out.geo_age_min.nunique())
print(out.groupby("geo_lith").y10.agg(["size","mean"]).sort_values("size",ascending=False).head(8).round(3) if "y10" in out else "")
