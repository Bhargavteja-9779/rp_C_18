"""Equity of adaptive testing (deviations.md item 55). Arsenic > 10 ug/L, held-out states.
Usage: python code/src/equity_check.py [seeds=5]"""
import sys, os, re, numpy as np, pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import wilcoxon
import lightgbm as lgb

NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 5
CONT = sys.argv[2] if len(sys.argv) > 2 else "as"; YCOL = {"as": "y10", "f": "y2", "n": "y10", "u": "y10"}[CONT]
STRATA = os.environ.get("STRATA", "county"); FRONTIER = os.environ.get("FRONTIER") == "1"
FLAGS = ("low_inc", "high_pov") if STRATA == "county" else ("high_soc", "high_svi")
LAMS = (0.0, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
METHODS = ("M1", "F1", "H1", "F1EQ", "H1EQ") if not FRONTIER else tuple(f"{b}L{l}" for b in ("F1", "H1") for l in LAMS)
OUT = ("results/equity" if CONT == "as" else f"results/equity_{CONT}") if STRATA == "county" else f"results/equity_svi_{CONT}"
if FRONTIER: OUT = f"results/equity_frontier_{STRATA}_{CONT}"
MAXN = 6000; os.makedirs(OUT, exist_ok=True); BATCH = 10; BUF = 25.0; H = 5.0

def norm(s): return re.sub(r"[^a-z]", "", str(s).lower().replace("saint", "st"))

def load():
    w = pd.read_csv(f"data/processed/wells_{CONT}.csv")
    w = w.dropna(subset=["lat", "lon"]).drop_duplicates("Location_Identifier").reset_index(drop=True)
    x = pd.read_excel("data/raw/saipe/est22all.xls", header=3)
    x = x[x["County FIPS Code"] != 0].copy()
    x["key"] = x["Postal Code"] + "|" + x["Name"].map(norm)
    x["inc"] = pd.to_numeric(x["Median Household Income"], errors="coerce"); x["pov"] = pd.to_numeric(x["Poverty Percent, All Ages"], errors="coerce")
    w["key"] = w.state + "|" + w.county.map(norm)
    w = w.merge(x[["key", "inc", "pov"]], on="key", how="left")
    match = w.inc.notna().mean()
    lat0 = np.deg2rad(38.0); w["x"] = w.lon * 111.32 * np.cos(lat0); w["yk"] = w.lat * 110.57
    w["aq"] = w.aquifer.fillna("NA").astype("category").cat.codes
    w["y"] = w[YCOL].astype(int)
    # state-relative low-income flags (median over the state's counties that contain wells)
    c = w.dropna(subset=["inc"]).drop_duplicates("key")
    med_inc = c.groupby("state").inc.median(); med_pov = c.groupby("state").pov.median()
    w["low_inc"] = (w.inc < w.state.map(med_inc)).astype(float).where(w.inc.notna())
    w["high_pov"] = (w.pov > w.state.map(med_pov)).astype(float).where(w.pov.notna())
    if STRATA == "svi":   # deviation 62: tract SVI, national percentiles
        v = pd.read_csv(f"data/processed/wells_svi_{CONT}.csv")
        w = w.merge(v, on="Location_Identifier", how="left")
        w["high_svi"] = (w.RPL_THEMES >= 0.75).astype(float); w["high_soc"] = (w.RPL_THEME1 >= 0.75).astype(float)
    return w, match

def map_scores(D, s):
    tw = D[D.state == s]; tree = cKDTree(tw[["x", "yk"]].values)
    tr = D[D.state != s]; tr = tr[tree.query(tr[["x", "yk"]].values, distance_upper_bound=BUF)[0] > BUF]
    m = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, verbose=-1)
    m.fit(tr[["lat", "lon", "aq"]], tr.y, categorical_feature=["aq"])
    return m.predict_proba(tw[["lat", "lon", "aq"]])[:, 1]

def map_scores_sub(D, s, W):
    tree = cKDTree(D[D.state == s][["x", "yk"]].values)
    tr = D[D.state != s]; tr = tr[tree.query(tr[["x", "yk"]].values, distance_upper_bound=BUF)[0] > BUF]
    m = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, verbose=-1)
    m.fit(tr[["lat", "lon", "aq"]], tr.y, categorical_feature=["aq"])
    return m.predict_proba(W[["lat", "lon", "aq"]])[:, 1]

def order(W, K, y, method, seed, ms, L=None):
    n = len(W); rng = np.random.default_rng(seed); noise = rng.random(n) * 1e-9
    T = list(rng.choice(n, BATCH, replace=False)); stop = int(np.ceil(0.2 * n))
    lam = 1.0 if method.endswith("EQ") else (float(method.split("L")[1]) if "L" in method else 0.0)
    base = method.replace("EQ", "").split("L")[0]
    while len(T) < stop:
        U = np.setdiff1d(np.arange(n), T); Ta = np.array(T); b = min(BATCH, stop - len(T))
        if base == "M1": s = ms[U]
        else:
            k = K[np.ix_(U, Ta)]
            s = (0.1 + k @ y[Ta]) / (1 + k.sum(1)) if base == "F1" else k @ y[Ta]
        s = s + noise[U]
        if lam > 0:
            inL = L[U]; exact = min(b, lam * b * inL.mean()); nL = int(np.floor(exact)) + (1 if exact - np.floor(exact) >= 0.5 else 0)
            nL = min(nL, int(inL.sum())); nO = min(b - nL, int((~inL).sum())); nL = b - nO if nO < b - nL else nL
            UL, UO = U[inL], U[~inL]; sL, sO = s[inL], s[~inL]
            pick = list(UL[np.argsort(-sL)[:nL]]) + list(UO[np.argsort(-sO)[:nO]])
        else:
            pick = list(U[np.argsort(-s)[:b]])
        T += pick
    return np.array(T[:stop])

def main():
    D, match = load(); print("county match rate", round(match, 4), "strata", STRATA, "frontier", FRONTIER, OUT, flush=True)
    st = D.groupby("state").y.agg(["size", "sum"]); units = st[(st["size"] >= 100) & (st["sum"] >= 15)].index
    rows = []; done = set()
    if os.path.exists(f"{OUT}/raw.csv") and os.environ.get("RESUME") == "1":   # resume after an interrupted run (same seeds, deterministic)
        old = pd.read_csv(f"{OUT}/raw.csv"); cnt = old.groupby("state").size()
        done = set(cnt[cnt == len(FLAGS) * NSEED * len(METHODS)].index); rows = old[old.state.isin(done)].to_dict("records"); print("resuming; states done", len(done), flush=True)
    for s in units:
        if s in done: continue
        W = D[D.state == s]
        if len(W) > MAXN: W = W.sample(MAXN, random_state=0); print("  subsampled", s, flush=True)
        W = W.reset_index(drop=True); y = W.y.values; X = W[["x", "yk"]].values
        K = np.exp(-((X[:, None] - X[None]) ** 2).sum(-1) / (2 * H * H)); np.fill_diagonal(K, 0)
        ms = map_scores(D, s); ms = ms[:len(W)] if len(ms) == len(W) else map_scores_sub(D, s, W); k20 = int(np.ceil(0.2 * len(W)))
        for flag in FLAGS:
            L = W[flag].fillna(0).values == 1; y = y.astype(bool).astype(int); nlow = int((y & L).sum())
            for seed in range(NSEED):
                for m in METHODS:
                    T = order(W, K, y, m, seed, ms, L); found = y[T]; fl = found & L[T]
                    exp_low = (y & L).sum() * k20 / len(W)
                    rows.append(dict(state=s, flag=flag, seed=seed, method=m, n=len(W), n_unsafe=int(y.sum()), n_unsafe_low=nlow,
                                     enr_all=found.sum() / (y.mean() * k20), enr_low=fl.sum() / exp_low if exp_low > 0 else np.nan,
                                     share_found_low=fl.sum() / max(found.sum(), 1), share_all_low=nlow / y.sum()))
        print(" ", s, len(W), int(y.sum()), flush=True)
        pd.DataFrame(rows).to_csv(f"{OUT}/raw.csv", index=False)
    R = pd.DataFrame(rows); R["rep_ratio"] = R.share_found_low / R.share_all_low
    out = []
    if FRONTIER:
        for (flag, m), g in R[R.n_unsafe_low >= 5].groupby(["flag", "method"]):
            u = g.groupby("state")[["enr_all", "enr_low", "rep_ratio"]].mean()
            out.append(dict(flag=flag, method=m, base=m.split("L")[0], lam=float(m.split("L")[1]), n_states=len(u), enr_all=u.enr_all.mean(), enr_low=u.enr_low.mean(), rep_ratio_mean=u.rep_ratio.mean()))
        S = pd.DataFrame(out); S.to_csv(f"{OUT}/summary.csv", index=False); print(S.round(3).to_string()); return
    for flag, g in R[R.n_unsafe_low >= 5].groupby("flag"):
        u = g.groupby(["method", "state"])[["enr_all", "enr_low", "rep_ratio"]].mean()
        el = u.enr_low.unstack(0); rr = u.rep_ratio.unstack(0)
        p = {m: wilcoxon(el[m], el.M1).pvalue for m in ("F1", "H1")}
        hol = dict(zip(sorted(p, key=p.get), np.minimum(1, np.maximum.accumulate([p[k] * (2 - i) for i, k in enumerate(sorted(p, key=p.get))]))))
        ea = u.enr_all.unstack(0)
        for m in ("F1", "H1"):
            out.append(dict(flag=flag, method=m + "EQ_vs_" + m, n_states=len(el), enr_all=(ea[m + "EQ"] - ea[m]).mean(), enr_low=(el[m + "EQ"] - el[m]).mean(),
                            p_rep_vs_1=wilcoxon(ea[m + "EQ"], ea[m]).pvalue))
        for m in ("M1", "F1", "H1", "F1EQ", "H1EQ"):
            out.append(dict(flag=flag, method=m, n_states=len(el), enr_all=u.enr_all.unstack(0)[m].mean(), enr_low=el[m].mean(),
                            rep_ratio_mean=rr[m].mean(), rep_ratio_median=rr[m].median(),
                            p_rep_vs_1=wilcoxon(rr[m] - 1).pvalue, holm_enr_low_vs_map=hol.get(m)))
    S = pd.DataFrame(out); S.to_csv(f"{OUT}/summary.csv", index=False); print(S.round(3).to_string())

if __name__ == "__main__":
    main()
