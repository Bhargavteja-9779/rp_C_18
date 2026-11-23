# Claim -> evidence audit (checked against files in tables/ and results/)
| Claim in paper | Evidence file | Status |
|---|---|---|
| Random 5-fold ROC-AUC 0.87 vs leave-state-out 0.63; recall@20 0.72 vs 0.25 | results/as10/random_vs_blocked.csv; tables/random_vs_blocked_summary.csv | Supported (3 seeds, random split unbuffered; stated) |
| Static map 1.25x random, not significant after Holm (p=0.203), below random in 8/29 states | tables/statistics_as10.csv, per_state_enr20_as10.csv | Supported |
| Neighbour feedback 1.81x random; +0.64 vs static, Holm p=0.003 | tables/statistics_as10.csv | Supported |
| 19.4 vs 12.4 vs 10.9 unsafe wells per 100 tests | tables/unsafe_per_100_tests_as10.csv + raw_results | Supported (random value = mean state prevalence) |
| Hybrid M5 not better than M4; worse at As>5 (Holm p=0.010) | statistics_as10.csv, statistics_as5.csv | Supported |
| Gain holds in blocks and thinned data; edge over static not significant after thinning | statistics_as10_blocks.csv, statistics_as10_thin.csv | Supported; nuance reported |
| Negative control 1.01 (0.97-1.05) | results/extra_checks.json | Supported |
| "Lombard et al. reported sensitivity 33.9%" | Search-result snippet (USGS/PMC page), paper not opened | UNVERIFIED beyond snippet |
| "Spatial validation with buffers lowers scores (Appiah et al.)" | Search snippet only | UNVERIFIED beyond snippet |
| "Private wells are tested at owner/agency initiative" | General knowledge + CDC snippet | Weakly supported; needs a proper citation |
| Minnesota explanation (glacial aquifer variability) | none | Marked as hypothesis in text |

## Round 2 additions
| Claim | Evidence file | Status |
|---|---|---|
| Follow-unsafe heuristic 1.92 vs kernel rule; Holm p=0.51 | tables/extra_sweep_as10.csv | Supported |
| Weight on map: smooth decline 1.80 -> 1.28 (kappa 0.5 -> 1000) | results/extra_as10/sweep_heuristics.csv; tables/extra_sweep_means_as10.csv | Supported |
| Clustering at 20 km correlates with feedback enrichment (rho 0.52, p=0.003, n=29) | tables/extra_mechanism_as10.csv | Supported; correlational |
| South weakest region | tables/extra_regional_as10.csv | Supported (n=7 states) |
| Warm start: map with history 2.05 vs other-states map 1.17; history + feedback 2.17 | results/extra_as10/warm_start.csv; tables/extra_warm_as10.csv | Supported (24 states; date split favours history; stated) |
| Uranium shows the same direction | tables/summary_u30.csv, summary_u10.csv, statistics_u*.csv | Supported as direction only (9 and 12 states) |
| Glacial-aquifer variability could explain Minnesota | none | Hypothesis, labelled |
| 'Local geology explains cold-start failure' | none | Labelled as untested reading |

## Round 3 additions (2026-11-23)
| Claim | Evidence | Status |
|---|---|---|
| Geology does not help As>10 (1.13 vs 1.25); helps modestly for As>5 (+0.33) and uranium, none significant after Holm | tables/geology_effect.csv, summary_*_geo.csv | Supported |
| Feedback beats geology-assisted map for both arsenic thresholds (Holm<0.001); not distinguishable for uranium | statistics_*_geo.csv | Supported |
| Late batches shrink the gain (batch 200: 1.47 vs 1.79) | results/robust_checks/delay_availability_means.csv | Supported (3 seeds, not tested) |
| 30% unavailable wells do not hurt | same file | Supported (3 seeds, not tested) |
| Leave-one-region-out keeps the effect significant | results/robust_checks/leave_one_region_out.csv | Supported (unadjusted p) |
| Forward-in-time cold start: map 1.09, feedback 1.93 | results/robust_checks/temporal_cold_start.json | Direction only (6 states) |
| Synthetic fields: no gain at 1 km correlation length, gain grows with length | results/robust_checks/synthetic_mechanism*.csv | Supported (40 repeats per length) |
| Extended CA/CO run agrees (static 0.99, feedback 1.71) | tables/summary_as10_full.csv | Supported |
| Lombard et al. sensitivity 33.9%; 70/30 stratified split, no spatial hold-out described | PMC8852770 read in full by fetch | Verified |
| Appiah et al. use buffered leave-one-group-out validation (0-10 km) | PDF text extracted | Verified |
| CDC document is a Vermont town-ranking method | PDF text extracted | Verified |
| 40 million Americans rely on unregulated private wells | abstract of Amery et al. 2025 (PubMed) | Verified from abstract |
| Fluoride: static map 1.87x random (Holm<0.001, 29/31 states); hybrid 2.67x; feedback not significantly better than map | tables/statistics_f2.csv, summary_f2.csv | Supported (3 seeds; Kansas missing) |
| Fluoride >4 mg/L: map 1.76, feedback 2.37, hybrid 2.61; no pairwise difference significant after correction | tables/statistics_f4.csv | Supported (17 states, 3 seeds) |
| 'Fluoride controls shared across states' explanation | none | Labelled untested |
| Novelty-map entries: 22 abstracts read | journal_selection/novelty_map.csv | Verified level stated per row |
