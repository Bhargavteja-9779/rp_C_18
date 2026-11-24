"""Multi-contaminant, chemistry-informed adaptive testing (deviations.md item 51).
Usage: python code/src/panel_feedback.py [panel=P4|P2] [seeds=5]
Each simulated test reveals the whole analyte panel of a well."""
import sys, os, json, numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.spatial import cKDTree
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
from scipy.stats import wilcoxon

PANEL = sys.argv[1] if len(sys.argv) > 1 else "P4"
NSEED = int(sys.argv[2]) if len(sys.argv) > 2 else 5
OUT = f"results/panel/{PANEL}"; os.makedirs(OUT, exist_ok=True)
THR = {"as": 10.0, "u": 30.0, "f": 4.0, "n": 10.0}
AN = ["as", "u", "f", "n"] if PANEL == "P4" else ["as", "n"]
TARGETS = {"P4": ["as", "u", "n", "any"], "P2": ["as", "n"]}[PANEL]
H = (5.0, 20.0); BATCH = 10; BUF = 25.0

def load():
    base = None
    for a in AN:
        d = pd.read_csv(f"data/processed/wells_{a}.csv", usecols=["Location_Identifier", "lat", "lon", "state", "aquifer", "val"])
        d = d.rename(columns={"val": a}).drop_duplicates("Location_Identifier")
        base = d if base is None else base.merge(d[["Location_Identifier", a]], on="Location_Identifier")
    base = base.dropna(subset=AN + ["lat", "lon"])
    for a in AN: base["y_" + a] = (base[a] > THR[a]).astype(int)
    if PANEL == "P4": base["y_any"] = base[["y_as", "y_u", "y_f", "y_n"]].max(axis=1)
    lat0 = np.deg2rad(38.0)
    base["x"] = base.lon * 111.32 * np.cos(lat0); base["yk"] = base.lat * 110.57
    base["aq"] = base.aquifer.fillna("NA").astype("category").cat.codes
    return base.reset_index(drop=True)

def kern(X):
    d2 = ((X[:, None, :] - X[None, :, :]) ** 2).sum(-1)
    Ks = [np.exp(-d2 / (2 * h * h)) for h in H]
    for K in Ks: np.fill_diagonal(K, 0.0)
    return Ks

def zmat(W): return np.column_stack([np.log10(1 + np.clip(W[a].values, 0, None) / THR[a]) for a in AN])

def feats(Ks, Z, T, rows):
    """features of wells `rows` given tested set T (diag of K is 0 -> leave-self-out)."""
    out = []
    for K in Ks:
        k = K[np.ix_(rows, T)]; m = k.sum(1)
        out.append((k @ Z[T]) / (1 + m)[:, None]); out.append(np.log1p(m)[:, None])
    return np.hstack(out)

def fname():
    n = []
    for h in H: n += [f"z_{a}_h{int(h)}" for a in AN] + [f"mass_h{int(h)}"]
    return n

def fit_prior_logit(Xs, y, w0, b0):
    def f(p):
        w, b = p[:-1], p[-1]; s = Xs @ w + b
        ll = np.logaddexp(0, s).sum() - (y * s).sum()
        r = w - w0
        g = 1 / (1 + np.exp(-s)) - y
        return ll + 0.5 * (r @ r) + 0.5 * (b - b0) ** 2, np.append(Xs.T @ g + r, g.sum() + (b - b0))
    p = minimize(f, np.append(w0, b0), jac=True, method="L-BFGS-B").x
    return p[:-1], p[-1]

CACHE = {}
def state_data(D, s):
    if s not in CACHE:
        g = D[D.state == s].reset_index(drop=True); CACHE[s] = (g, kern(g[["x", "yk"]].values), zmat(g))
    return CACHE[s]

def transfer_model(D, tgt_state, target, seed):
    """F3: logistic model of target from neighbour chemistry, fitted on other states."""
    rng = np.random.default_rng(seed + 1000)
    tw = D[D.state == tgt_state][["x", "yk"]].values; tree = cKDTree(tw)
    Xs, ys = [], []
    for s in sorted(D.state.unique()):
        if s == tgt_state or (D.state == s).sum() < 30: continue
        g, Ks, Z = state_data(D, s)
        T = np.sort(rng.choice(len(g), max(5, int(0.3 * len(g))), replace=False))
        F = feats(Ks, Z, T, np.arange(len(g)))
        keep = tree.query(g[["x", "yk"]].values, distance_upper_bound=BUF)[0] > BUF
        Xs.append(F[keep]); ys.append(g["y_" + target].values[keep])
    X = np.vstack(Xs); y = np.concatenate(ys)
    sc = StandardScaler().fit(X); m = LogisticRegression(C=1.0, max_iter=2000).fit(sc.transform(X), y)
    return sc, m.coef_[0].copy(), float(m.intercept_[0])

def map_scores(D, tgt_state, target):
    tw = D[D.state == tgt_state]; tree = cKDTree(tw[["x", "yk"]].values)
    tr = D[D.state != tgt_state]; tr = tr[tree.query(tr[["x", "yk"]].values, distance_upper_bound=BUF)[0] > BUF]
    m = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, verbose=-1)
    m.fit(tr[["lat", "lon", "aq"]], tr["y_" + target], categorical_feature=["aq"])
    return m.predict_proba(tw[["lat", "lon", "aq"]])[:, 1]

def campaign(W, Ks, Z, y, method, seed, first, ti, tmodel=None, mscore=None):
    n = len(W); rng = np.random.default_rng(seed); noise = rng.random(n) * 1e-9
    T = list(first); stop = int(np.ceil(0.3 * n)); K5 = Ks[0]
    while len(T) < stop:
        U = np.setdiff1d(np.arange(n), T); Ta = np.array(T)
        if method == "F1":
            k = K5[np.ix_(U, Ta)]; s = (0.1 + k @ y[Ta]) / (1 + k.sum(1))
        elif method == "F1c":
            F = feats(Ks, Z, Ta, U); s = F[:, ti] + F[:, len(AN) + 1 + ti]
        elif method == "M1":
            s = mscore[U]
        elif method in ("F2", "F3", "F4"):
            FU = feats(Ks, Z, Ta, U)
            if method == "F3":
                sc, w, b = tmodel; s = sc.transform(FU) @ w + b
            else:
                yt = y[Ta]
                if method == "F2" and (yt.sum() < 3 or (1 - yt).sum() < 3):
                    s = FU[:, ti] + FU[:, len(AN) + 1 + ti]
                else:
                    FT = feats(Ks, Z, Ta, Ta)
                    if method == "F2":
                        sc = StandardScaler().fit(FT); m = LogisticRegression(C=1.0, max_iter=2000).fit(sc.transform(FT), yt)
                        s = m.decision_function(sc.transform(FU))
                    else:
                        sc, w0, b0 = tmodel; w, b = fit_prior_logit(sc.transform(FT), yt, w0, b0)
                        s = sc.transform(FU) @ w + b
        s = s + noise[U]
        T += list(U[np.argsort(-s)[:min(BATCH, stop - len(T))]])
    T = np.array(T); res = {}
    for f in (0.1, 0.2, 0.3):
        k = int(np.ceil(f * n)); exp = y.mean() * k
        res[f"enr{int(f*100)}"] = y[T[:k]].sum() / exp
    res["tests_per_unsafe20"] = int(np.ceil(0.2 * n)) / max(y[T[:int(np.ceil(0.2 * n))]].sum(), 0.5)
    return res

def main():
    D = load(); print(PANEL, "wells", len(D), {t: int(D["y_" + t].sum()) for t in TARGETS})
    rows, coefs = [], []
    for target in TARGETS:
        ti = AN.index(target) if target in AN else AN.index("as")
        st = D.groupby("state")["y_" + target].agg(["size", "sum"]); units = st[(st["size"] >= 100) & (st["sum"] >= 10)].index.tolist()
        print(target, "states", len(units), flush=True)
        for s in units:
            W, Ks, Z = state_data(D, s); y = W["y_" + target].values
            ms = map_scores(D, s, target) if target != "any" else None
            for seed in range(NSEED):
                tm = transfer_model(D, s, target, seed)
                coefs.append(dict(target=target, state=s, seed=seed, **dict(zip(fname(), tm[1]))))
                first = np.random.default_rng(seed).choice(len(W), BATCH, replace=False)
                for meth in ["F1", "F1c", "F2", "F3", "F4"] + (["M1"] if ms is not None else []):
                    r = campaign(W, Ks, Z, y, meth, seed, first, ti, tm, ms)
                    rows.append(dict(target=target, state=s, seed=seed, method=meth, n=len(W), n_unsafe=int(y.sum()), **r))
            pd.DataFrame(rows).to_csv(f"{OUT}/raw.csv", index=False); pd.DataFrame(coefs).to_csv(f"{OUT}/transfer_coefs.csv", index=False)
            print(" ", target, s, len(W), int(y.sum()), flush=True)
    R = pd.DataFrame(rows); summ = []
    for target, g in R.groupby("target"):
        u = g.groupby(["method", "state"])[["enr10", "enr20", "tests_per_unsafe20"]].mean()
        for col in ("enr10", "enr20"):
            t = u[col].unstack(0); ps = {}
            for m in t.columns:
                if m == "F1": continue
                try: ps[m] = wilcoxon(t[m], t["F1"]).pvalue
                except ValueError: ps[m] = 1.0
            order = sorted(ps, key=ps.get); holm = {}; run = 0
            for i, m in enumerate(order): run = max(run, min(1, ps[m] * (len(order) - i))); holm[m] = run
            for m in t.columns:
                summ.append(dict(target=target, metric=col, method=m, n_states=len(t), mean=t[m].mean(), median=t[m].median(),
                                 better_than_F1=int((t[m] > t["F1"]).sum()) if m != "F1" else None,
                                 p_vs_F1=ps.get(m), holm_vs_F1=holm.get(m),
                                 tests_per_unsafe=u["tests_per_unsafe20"].unstack(0)[m].mean()))
    S = pd.DataFrame(summ); S.to_csv(f"{OUT}/summary.csv", index=False); print(S.to_string())

if __name__ == "__main__":
    main()
