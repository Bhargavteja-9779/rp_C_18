# Novelty scorecard (final, topic: cold-start well-testing campaigns for arsenic)

Evidence: `novelty_map.csv` (papers seen through search snippets only; 30 not reached; no paper was read in full). Scores are my honest judgement and are not checkable by a third party.

Novelty types claimed: N1 (campaign formulation, weak), N5 (held-out-state + budget protocol, moderate; spatial-validation inflation is already documented elsewhere), N7 (finding: static maps ~ random across states, feedback helps, ML prior does not add; moderate). N2 (new method): NOT claimed; the hybrid did not beat the simple rule. N3, N4, N6: none.

| # | Criterion | Score /5 | Evidence |
|---|---|---|---|
| 1 | Distance from closest 5 papers | 3 | Closest: adaptive arsenic sampling (arXiv 2102.11118), active area search (AISTATS), Lombard et al. 2021 national map, Appiah et al. spatial CV with buffers, OWL-GPS (budgeted geospatial discovery, arXiv 2602.17605). None seen doing leave-state-out campaign simulation on national USGS wells, but only snippets were read. |
| 2 | Problem strength | 4 | Real stakeholder (state health agencies); documented 33.9% sensitivity of the national map; cost data in real units not independently sourced. |
| 3 | Depth of idea | 2 | Kernel feedback is simple; no theory; the proposed hybrid failed to add value. |
| 4 | Evidence strength | 4 | 29 held-out states, 11 methods, 5 seeds, paired tests with Holm, 3 designs, negative control, timing; single data source, one contaminant. |
| 5 | Generality | 3 | As>10, As>5, blocks, thinned; nitrate failed; one country. |
| 6 | Match with journal level | 2 | Water Research ML papers (abstract-level benchmark) mostly add process insight or physics; this paper has none and no geochemical covariates. |

**Total 18/30. Gate is 22/30 with no score below 3. GATE NOT PASSED (criteria 3 and 6 are 2).**
The idea was redesigned once (from conformal yield alerts, which fell to 17/30 after finding a 2026 paper on year-level conformal yield intervals). The redesign gave 18/30, still below the gate. I continued because you asked for automatic completion; this decision is recorded, and the manuscript is a draft, not a submission-ready paper.

## Reviewer-zero sentences (desk rejection)
1. "A kernel neighbour update is a textbook idea; adaptive and active-search sampling for arsenic and hotspots already exist."
2. "Water Research publishes process understanding; this paper shows no geochemistry and no new mechanism."
3. "Random order is a weak baseline: agencies already use geology and prior results to choose wells."

Replies with evidence from the novelty map: (1) partly answerable: the contribution is the measured comparison on national held-out data, not the rule; (2) not answerable; (3) partly answerable: the static-map baselines are the published approach, but no expert-heuristic baseline was tested. The paper is therefore at high risk of desk rejection at this journal.

## Honest claim chain
WHAT EXISTS: national ML arsenic maps (evaluated with random or within-region tests) and adaptive sampling designs. WHAT IT FAILS TO DO (as far as I found): quantify map transfer to a new state in budgeted campaign terms, or the gain from feedback relative to the map. WHY IT MATTERS: agencies choose testing order with limited budgets. WHAT THIS WORK ADDS: held-out-state campaign simulation and its numbers. HOW IT IS PROVEN: `results/` and `tables/`. No claim of "first".
