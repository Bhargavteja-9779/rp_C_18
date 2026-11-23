"""Paired effect of adding geology to the static map, per outcome. Output tables/geology_effect.csv"""
import numpy as np, pandas as pd
from scipy.stats import wilcoxon
rng=np.random.default_rng(0); rows=[]
for lab,a,b in (("As>10","as10","as10_geo"),("As>5","as5","as5_geo"),("U>30","u30","u30_geo"),("U>10","u10","u10_geo")):
    pa=pd.read_csv(f"tables/per_state_enr20_{a}.csv",index_col=0); pb=pd.read_csv(f"tables/per_state_enr20_{b}.csv",index_col=0); ix=pa.index.intersection(pb.index)
    d=(pb.loc[ix,"M1_static_lgbm"]-pa.loc[ix,"M1_static_lgbm"]).values; p=wilcoxon(d).pvalue; ci=np.percentile([np.median(rng.choice(d,len(d))) for _ in range(10000)],[2.5,97.5])
    g=pb.loc[ix,"M1_static_lgbm"].values-1; pg=wilcoxon(g).pvalue
    rows.append(dict(outcome=lab,n_states=len(ix),M1_base=pa.loc[ix,"M1_static_lgbm"].mean(),M1_geo=pb.loc[ix,"M1_static_lgbm"].mean(),median_gain=np.median(d),ci_lo=ci[0],ci_hi=ci[1],p_gain=p,M1_geo_vs_random_p=pg,states_improved=int((d>0).sum())))
t=pd.DataFrame(rows); t["holm_p_gain"]=np.minimum(1,np.maximum.accumulate((len(t)-np.arange(len(t)))*t.p_gain.sort_values().values))[t.p_gain.rank(method="first").astype(int).values-1]
t.to_csv("tables/geology_effect.csv",index=False); print(t.round(3).to_string())
