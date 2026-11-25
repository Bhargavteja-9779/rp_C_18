"""Mechanism of the equity gap (deviations.md item 64).
Usage: STRATA=county|svi python code/src/equity_mechanism.py <contaminant>  (writes one CSV)
       python code/src/equity_mechanism.py summarize"""
import os, sys, numpy as np, pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import spearmanr, wilcoxon

OUT = "results/equity_mechanism"; os.makedirs(OUT, exist_ok=True)
FLAG = {"county": "high_pov", "svi": "high_svi"}

def one(cont):
    strata = os.environ.get("STRATA", "county")
    sys.argv = ["x", "3", cont]; sys.path.insert(0, os.path.dirname(__file__))
    import equity_check as E
    D, _ = E.load(); flag = FLAG[strata]
    res = f"{E.OUT}/raw.csv"; R = pd.read_csv(res); R = R[(R.flag == flag) & (R.method == "H1")]
    R["rep"] = R.share_found_low / R.share_all_low; rep = R.groupby("state").rep.mean()
    rows = []
    for s, W in D.groupby("state"):
        if s not in rep.index: continue
        U = W[W.y == 1]; L = U[flag].fillna(0).values == 1
        if L.sum() < 5 or (~L).sum() < 5: continue
        t = cKDTree(U[["x", "yk"]].values); cnt = np.array([len(v) - 1 for v in t.query_ball_point(U[["x", "yk"]].values, 5.0)])
        allt = cKDTree(W[["x", "yk"]].values); dens = np.array([len(v) - 1 for v in allt.query_ball_point(U[["x", "yk"]].values, 5.0)])
        rows.append(dict(contaminant=cont, strata=strata, state=s, follow_in=cnt[L].mean(), follow_out=cnt[~L].mean(),
                         density_in=dens[L].mean(), density_out=dens[~L].mean(), rep_H1=rep[s]))
    pd.DataFrame(rows).to_csv(f"{OUT}/{strata}_{cont}.csv", index=False); print(strata, cont, len(rows))

def summarize():
    import glob
    M = pd.concat([pd.read_csv(f) for f in glob.glob(f"{OUT}/*_*.csv") if "summary" not in f])
    M["log_follow"] = np.log((M.follow_in + 0.5) / (M.follow_out + 0.5)); M["log_dens"] = np.log((M.density_in + 0.5) / (M.density_out + 0.5))
    out = []
    for (st, c), g in list(M.groupby(["strata", "contaminant"])) + [((st, "pooled"), g) for st, g in M.groupby("strata")]:
        r = spearmanr(g.log_follow, g.rep_H1); rd = spearmanr(g.log_dens, g.rep_H1)
        out.append(dict(strata=st, contaminant=c, n_units=len(g), rho_follow=r.statistic, p_one_sided=r.pvalue / 2 if r.statistic > 0 else 1 - r.pvalue / 2,
                        rho_density=rd.statistic, p_density=rd.pvalue, median_log_follow=g.log_follow.median(), p_follow_vs_0=wilcoxon(g.log_follow).pvalue,
                        share_less_followable=(g.log_follow < 0).mean()))
    S = pd.DataFrame(out); S.to_csv(f"{OUT}/summary.csv", index=False); print(S.round(3).to_string())

if __name__ == "__main__":
    summarize() if sys.argv[1] == "summarize" else one(sys.argv[1])
