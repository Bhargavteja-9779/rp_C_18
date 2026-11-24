# Novelty scorecard - before and after the re-check
| Item | First run (round 4) | Re-check start | After re-check | Evidence |
|---|---|---|---|---|
| 1 Distance from closest 5 papers | 3 | 3 | 2 | ActiveRemediation, Thompson 1990, Cao 2024, Usman 2026, MacDonald 2020 are close; the qualitative idea is not new. |
| 2 Problem strength | 4 | 4 | 4 | verified burden and practice |
| 3 Depth of idea | 4 | 3 | 3 | ABF is a standard Bayesian mixture with a standard bound; explanatory analyses are good; two new ideas tested in this run failed their pre-registered checks |
| 4 Strength of evidence | 4 | 4 | 4 | clean reproduction, leakage checks, stress tests added; one data source, no field trial |
| 5 Generality | 4 | 4 | 4 | three contaminants; one country |
| 6 Journal match | 3 | 3 | 3 | scope plausible (1 private-well paper in 157 recent ES&T Letters papers), unusual for the journal |
| Total | 23 | 21 | **20** | |
Stop rule (26/30, distance >= 4, evidence >= 4) NOT reached after 2 elevation rounds. Label: strongest honest version. The first run's depth score of 4 is withdrawn.

## Correction after reading ActiveRemediation in full (2026-11-24)
The full text shows that ActiveRemediation already combines a model with sequential active learning, backtests it against the order actually used in Flint, compares greedy and uniform exploration and checks batch-size robustness. The replay of real campaigns is therefore NOT a new kind of evidence, and the pipeline structure is not new. 'Distance from closest papers' is lowered from 3 to 2 and the total from 21 to 20/30. What remains different: groundwater contaminants and private wells, held-out-state transfer of maps, the contaminant dependence, ABF with a loss bound, and the measured failure conditions.
