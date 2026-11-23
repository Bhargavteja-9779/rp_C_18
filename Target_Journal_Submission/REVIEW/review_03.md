# Review 03: Statistics and fairness

MAJOR: Held-out states are not fully independent (neighbouring states share aquifers), so Wilcoxon p-values may be optimistic. Tuning used 8 states but not a nested design; the M7 weight was untuned.
MODERATE: Holm family differs per scenario; the thinned run has only 26 units and low power (edge over static p=0.10 reported as not significant). Random-vs-blocked used 3 seeds and no buffer on the random split.
MINOR: Random baseline is analytic.
ACTIONS TAKEN: M7 weight check (1/20/100): no change in conclusion; thinned result reported with its non-significance; deviations logged. NOT FIXED: spatial dependence among states (could add region-level clustered bootstrap).

ROUND 2: added regional consistency check (South weakest: 4/7 states positive at 10 ug/L); stated that states are not fully independent. Added Holm-corrected tests for all added comparisons. Open: clustered bootstrap over regions (only 4 regions).

ROUND 3: added leave-one-region-out (effect stays significant, largest unadjusted p=0.018), extended run with California and Colorado (agrees), Holm correction for all added comparisons, paired test of the geology effect (none significant after correction, stated). Still open: states are not independent; 4 regions are too few for a cluster bootstrap.
