# Review 04: ML methodology and code

MODERATE: M5 hyperparameters (h=5 km, kappa=0.5) come from 8 tuning states; kappa=0.5 means the prior is weak, which may explain why the prior adds nothing (hypothesis, not tested). LightGBM tuned with 20 trials only. Code-vs-paper check: batch size 10, 25 km buffer, earliest sample per well, non-detect rules all match code. One tested weakness: the original M7 checkpoint condition was convoluted; it was rewritten and unit-tested indirectly only.
MINOR: Ties broken by stable sort.
ACTIONS TAKEN: unit tests (4) pass; negative control gives 1.01 (shuffled outcomes), ruling out an ordering artefact. NOT FIXED: sensitivity of the conclusion to larger kappa grids.
