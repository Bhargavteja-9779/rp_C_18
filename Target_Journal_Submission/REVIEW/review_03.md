# Review 03: Statistics and fairness

MAJOR: Held-out states are not fully independent (neighbouring states share aquifers), so Wilcoxon p-values may be optimistic. Tuning used 8 states but not a nested design; the M7 weight was untuned.
MODERATE: Holm family differs per scenario; the thinned run has only 26 units and low power (edge over static p=0.10 reported as not significant). Random-vs-blocked used 3 seeds and no buffer on the random split.
MINOR: Random baseline is analytic.
ACTIONS TAKEN: M7 weight check (1/20/100): no change in conclusion; thinned result reported with its non-significance; deviations logged. NOT FIXED: spatial dependence among states (could add region-level clustered bootstrap).
