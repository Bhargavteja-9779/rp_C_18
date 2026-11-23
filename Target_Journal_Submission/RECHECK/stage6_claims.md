# Stage 6 - citations and claims
Citations: every reference was re-verified automatically against Crossref/arXiv/DataCite (code/src/verify_refs.py; RECHECK/reference_verification.csv): 41 of 46 checked entries match on title and year; 5 are documents/web sources (Appiah 2025 and Vermont/CDC 2026 and Ma et al. 2015 read as PDFs; USGS API and NASA POWER are data sources). Three references were added in this run (Thompson 1990, Abernethy 2018, Abernethy 2016) and verified through Crossref/arXiv; the total is 49 (the script was run before they were added; the three were checked by direct lookup). Relevance: statements attributed to papers are limited to what the abstract or text read supports (citation_audit.md); 18 of the earlier references remain metadata-only.
Claim -> evidence (main Letter claims):
| Claim | Evidence file / experiment | Status |
|---|---|---|
| Random split overstates map skill (pooled AUC 0.81 vs 0.64; within-state AUC 0.51) | tables/random_vs_blocked_summary.csv; results/recheck/leakage_checks_summary.csv | Supported; wording now says pooled |
| Arsenic>10 map = 0.93x random; feedback 1.78x; tests per unsafe well 9.2 -> 5.2 | results/abf_as10/abf.csv; raw results | Supported; robust to all tests (Table S-A) |
| Fluoride map transfers (1.87x); hybrid best (2.67x) | results/abf_f2/abf.csv | Supported (3 seeds; Kansas missing) |
| ABF never significantly worse than the alternatives; worst gap 0.35 | Table 1 in Letter; abf results | Supported with Holm; borderline p=0.057 at As>10 stated |
| ABF cumulative loss <= best expert + ln 31 | abf.py joint-loss accounting; theory | Supported (standard Bayesian-mixture property); bounds loss, not discovery (stated) |
| Gains larger where unsafe wells cluster (rho 0.52) | tables/extra_mechanism_as10.csv; synthetic fields | Supported (correlation + synthetic) |
| Late results shrink the gain | results/robust_checks; abf_batch | Supported (3 seeds, untested) |
| Other learners do not beat feedback (arsenic) | results/learner_check | Supported |
| Weighted training helps arsenic>10 but not >5 | results/elevation/ge_*.csv | Supported; not a headline |
| Remaining-yield forecast unreliable | results/elevation/forecast_*.csv | Supported (negative) |
| 40 million private-well users; 33.9% sensitivity | Amery 2025 abstract; Lombard 2021 full text | Verified |
Recent work: reference list contains 2021-2026 papers (majority); older foundations (Thompson 1990, Wilcoxon 1945, Efron 1979). Papers from the target journal: ES&T Letters has no cited paper from itself; ES&T papers (Lombard, Erickson, Cao x2, Amery, Smith) are the sibling journal's. UNVERIFIED: whether any ES&T Letters paper should be cited; the search found 1 private-well paper in the journal in 2023-2026 but it was not identified or read.
Gap statement fairness: the gap sentence now credits adaptive cluster sampling, active search, lead-pipe programmes, fluoride-transfer papers and neighbour-letter practice.
