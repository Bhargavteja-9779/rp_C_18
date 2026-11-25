"""Assign wells to 2022 census tracts and attach CDC/ATSDR SVI 2022 (deviation 62)."""
import glob, pandas as pd, geopandas as gpd
svi = pd.read_csv("data/raw/svi/SVI_2022_US.csv", usecols=["FIPS", "RPL_THEMES", "RPL_THEME1"], dtype={"FIPS": str})
svi["FIPS"] = svi.FIPS.str.zfill(11)
T = pd.concat([gpd.read_file(f)[["GEOID", "geometry"]] for f in sorted(glob.glob("data/raw/tracts/*.zip"))]).to_crs(4326)
T = gpd.GeoDataFrame(T, geometry="geometry", crs=4326)
for c in ("as", "f", "n", "u"):
    w = pd.read_csv(f"data/processed/wells_{c}.csv", usecols=["Location_Identifier", "lat", "lon"]).dropna().drop_duplicates("Location_Identifier")
    g = gpd.GeoDataFrame(w, geometry=gpd.points_from_xy(w.lon, w.lat), crs=4326)
    j = gpd.sjoin(g, T, how="left", predicate="within").drop_duplicates("Location_Identifier")
    j = j.merge(svi, left_on="GEOID", right_on="FIPS", how="left")
    for k in ("RPL_THEMES", "RPL_THEME1"): j.loc[j[k] < 0, k] = float("nan")
    j[["Location_Identifier", "GEOID", "RPL_THEMES", "RPL_THEME1"]].to_csv(f"data/processed/wells_svi_{c}.csv", index=False)
    print(c, len(j), "in tract", round(j.GEOID.notna().mean(), 4), "with SVI", round(j.RPL_THEMES.notna().mean(), 4), "high-SVI share", round((j.RPL_THEMES >= 0.75).mean(), 3))
