# Pre-registered protocol (written 2026-11-22, BEFORE any model was run on the data)

## Problem and question
A state agency can test only a fraction of the wells in a region for arsenic. Which wells should be tested first, and does using the results of wells already tested in the same campaign help beyond a static risk map?
- RQ1: How much do random-split evaluations overstate well-ranking performance compared with spatially blocked evaluation?
- RQ2: With a fixed test budget, does a static ML risk map find more unsafe wells than random order, in unseen regions?
- RQ3: Does adaptive ordering (using outcomes of wells tested earlier in the campaign) find more unsafe wells than the static map?
- RQ4: Does the effect hold across outcome definitions (As>10, As>5 ug/L; nitrate>10 mg/L-N if data are obtained), and across regions?
- RQ5: Which part of the proposed method matters (ablation), and what is its cost?

## Data
USGS Samples API (api.waterdata.usgs.gov), characteristic Arsenic (and Nitrate if time allows), Location_Type = Well, medium water, unit ug/L (mg/L for nitrate), 51 state codes. Wells are the unit. The earliest valid sample per well gives the label. Non-detects are labeled safe (below any threshold >= their detection limit; wells whose detection limit exceeds the threshold are dropped). Known flaw: USGS wells are not a random sample of private wells (selection bias); stated as a limitation.

## Features (what a planner knows before testing)
latitude, longitude, sampling depth (if present), aquifer code (if present, else "unknown"), state. No co-measured chemistry (would not be known before testing).

## Splits (fixed in advance)
Spatial blocks: cluster well coordinates with KMeans (k=60 blocks) per partition; 5 partitions with seeds 0-4. In each partition, each block is held out once; training wells exclude those within 25 km of the block's wells (buffer). Blocks with <60 wells or <5 unsafe wells are skipped (reported). Random-split comparison: 5-fold random K-fold with the same learner.

## Methods (all get the same tuning budget: 20 random-search trials, picked by validation on training blocks only)
M0 random order. M1 static LightGBM risk map. M2 static logistic regression (coordinates, depth). M3 static kNN regional-prevalence prior. M4 neighbor-only adaptive (kernel over tested wells in the block). M5 proposed: adaptive hybrid = ML prior (M1 output as logit) + kernel-weighted evidence from tested wells with beta shrinkage, bandwidth chosen on training blocks. M6 Thompson-sampling variant of M5. M7 online refit LightGBM (refit with tested wells each batch). Ablations: M5 without prior, M5 without shrinkage, M5 with fixed (not tuned) bandwidth.
Campaign: batch size 10, first batch = top of prior (M1-based methods) or random (M0, M4).

## Metrics
Primary: unsafe wells found when 20% of wells in the block have been tested, divided by the number found by random order (enrichment). Secondary: recall at 5/10/30%; area under the discovery curve; tests per unsafe well found; ROC-AUC / PR-AUC of the static scores; runtime. Real-world measure: unsafe wells found per 100 tests.

## Statistics
Unit of analysis = held-out block (averaged over 5 partitions). Paired Wilcoxon signed-rank vs M1 and vs M0, Holm correction over the family of comparisons; bootstrap 95% CI (10,000 resamples of blocks) of the median paired difference; effect size = median paired difference and rank-biserial r. No claim of significance without adjusted p<0.05.

## Rules
No post-hoc change of metrics, budgets, methods or thresholds. Failed/negative results will be reported. Any deviation is listed in `experiments/deviations.md`.
