# Review 04: ML methodology and code

## ROUND 4 (final, 2026-11-23)
MODERATE: M7 weight was untuned (checked: 1/20/100, no change); ABF experts and grid were fixed before evaluation, and variants chosen on tuning states only (pre-specified version won again after the correction); bound verified numerically (maximum regret 3.43 of 3.43 nats, 0 violations); 7 unit tests pass; negative control 1.01; synthetic fields give 0.99 at 1 km.
NOT FIXED: kernel and expert grids are simple.

---
Earlier rounds (kept for the record; some numbers superseded by the corrected runs):

MODERATE: M5 hyperparameters (h=5 km, kappa=0.5) come from 8 tuning states; kappa=0.5 means the prior is weak, which may explain why the prior adds nothing (hypothesis, not tested). LightGBM tuned with 20 trials only. Code-vs-paper check: batch size 10, 25 km buffer, earliest sample per well, non-detect rules all match code. One tested weakness: the original M7 checkpoint condition was convoluted; it was rewritten and unit-tested indirectly only.
MINOR: Ties broken by stable sort.
ACTIONS TAKEN: unit tests (4) pass; negative control gives 1.01 (shuffled outcomes), ruling out an ordering artefact. NOT FIXED: sensitivity of the conclusion to larger kappa grids.

ROUND 3: methodological gaps closed where possible: M7 weight check; geology features added to the same pipeline with re-tuning on the tuning states only; categorical handling in LightGBM; unit tests (5) pass; negative control 1.01; synthetic fields (1 km correlation length gives 0.99, so no spurious gain). Open: kappa grid for tuning is small (but the sweep to 1000 shows the trend is monotone).
