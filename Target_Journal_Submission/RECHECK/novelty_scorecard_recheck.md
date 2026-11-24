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

## Re-score after rounds 7-8 (2026-11-24; items 51-58)
New evidence: (1) multi-contaminant panel feedback (pre-registered; arsenic negative; nitrate gain NOT confirmed on 9,082 independent wells; redox coefficient signs replicated); (2) equity analysis with Census SAIPE: follow-unsafe under-served high-poverty counties (ratio 0.82, p = 0.002); pre-registered equity-stratified batches restored proportionality (0.97) at a cost of 0.02 and raised unsafe wells found in poor counties (1.52 -> 1.79 x random). Prior-art check: testing-promotion disparities are documented (Flanagan et al. 2016) and fairness-aware sampling exists in ML (Cai et al. 2022); no study found that tests the equity of adaptive testing rules for wells.
| Criterion | Before | Now | Why |
|---|---|---|---|
| Distance from closest work | 2 | 3 | equity of adaptive rules + fix is new in this domain; feedback itself still classical |
| Real problem | 4 | 5 | private-well exposure + environmental justice |
| Depth | 3 | 4 | confirmation test, harm criterion with pre-declared mitigation |
| Evidence | 4 | 4 | still no field trial |
| Generality | 4 | 4 | equity check arsenic only |
| Journal match | 3 | 4 | plain-language rewrite, map, EJ angle |
| Total | 20 | 24 | stop rule 26 NOT met; user's target 25 NOT met; label: strongest honest version |
