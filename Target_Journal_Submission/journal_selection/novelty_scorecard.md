# Novelty scorecard (updated 2026-11-23, round 2; topic: well-testing campaigns for arsenic)

Evidence: `novelty_map.csv` (papers seen through search snippets only; 30 not reached; no paper was read in full). Scores are my honest judgement and are not checkable by a third party.

Novelty types claimed: N1 (campaign formulation, weak), N5 (held-out-state + budget protocol, moderate; spatial-validation inflation is already documented elsewhere), N7 (finding: static maps ~ random across states, feedback helps, ML prior does not add; moderate). N2 (new method): NOT claimed; the hybrid did not beat the simple rule. N3, N4, N6: none.

| # | Criterion | Score /5 (round 1 -> round 2) | Evidence |
|---|---|---|---|
| 1 | Distance from closest 5 papers | 3 -> 3 | Closest: risk-based arsenic sampling design (arXiv 2102.11118), active area search (AISTATS), Lombard et al. 2021, Appiah et al. 2025, OWL-GPS (arXiv 2602.17605). None seen doing held-out-state campaign simulation with warm-start and heuristic comparison, but only snippets/metadata were read. |
| 2 | Problem strength | 4 -> 4 | State health agencies; documented 33.9% sensitivity of the national map; cost in money not modelled. |
| 3 | Depth of idea | 2 -> 3 | Still no new method or theory. Added explanation with evidence: weight-on-map sweep (smooth path from feedback to static map), clustering-gain correlation (rho 0.52, n=29), regional heterogeneity, warm-start result showing local history beats pooled data. Correlational. |
| 4 | Evidence strength | 4 -> 4 | 29-31 states, 11 methods + 2 heuristics, 5 seeds, paired tests with Holm, 3 designs, negative control, warm start, uranium. Single data source. |
| 5 | Generality | 3 -> 3 | Uranium added but only 9 and 12 evaluation states (underpowered); nitrate failed; one country. |
| 6 | Journal-level match | 2 -> 3 | Cites four Water Research papers and adds explanatory analyses; still no geochemical covariates or process modelling. Benchmark is abstract-level only. |

**Total 20/30 (round 1: 18). Gate 22/30 with no score below 3: NOT PASSED on total (20 < 22); no individual score is below 3.**
Novelty types claimed: N1 (campaign formulation, weak), N5 (held-out-state budgeted protocol, moderate), N7 (findings: map ~ random in new states; feedback and local history help; hybrid does not add; moderate). N2 not claimed.

## Reviewer-zero sentences (desk rejection)
1. "A kernel neighbour update is a textbook idea; adaptive and active-search sampling for arsenic and hotspots already exist."
2. "Water Research publishes process understanding; this paper shows no geochemistry and no new mechanism."
3. "Random order is a weak baseline: agencies already use geology and prior results to choose wells."

Replies with evidence from the novelty map: (1) partly answerable: the contribution is the measured comparison on national held-out data, not the rule; (2) partly answerable after round 2 (clustering and regional analyses give a mechanism, but no geochemistry); (3) now answered in part: a hot-spot-following heuristic (H1) was tested and matches the kernel rule; no geology-informed baseline was tested. The paper is therefore at high risk of desk rejection at this journal.

## Honest claim chain
WHAT EXISTS: national ML arsenic maps (evaluated with random or within-region tests) and adaptive sampling designs. WHAT IT FAILS TO DO (as far as I found): quantify map transfer to a new state in budgeted campaign terms, or the gain from feedback relative to the map. WHY IT MATTERS: agencies choose testing order with limited budgets. WHAT THIS WORK ADDS: held-out-state campaign simulation and its numbers. HOW IT IS PROVEN: `results/` and `tables/`. No claim of "first".
