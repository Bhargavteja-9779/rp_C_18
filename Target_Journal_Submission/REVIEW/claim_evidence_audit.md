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
