# Novelty scorecard (round 3, 2026-11-23; topic: well-testing campaigns for arsenic)

Evidence: `novelty_map.csv`: 33 papers, 22 of them with the abstract read (PubMed/arXiv), the rest title/metadata or search snippets; three documents read as text (Lombard, Appiah, CDC/Vermont). The brief asked for 30 closest papers; this is met in count but not in depth of reading.

New close prior art found in round 3: Cao et al. 2024 (transferability of fluoride models between basins; surface predictors fail, adding target-region samples helps), Usman et al. 2026 (buffered validation; negligible national transfer for environmental-only models), MacDonald & Tippett 2020 (neighbour-exceedance letters raise testing), O'Neill et al. 2022 (history-based outreach). The finding that maps trained elsewhere do not transfer is therefore corroboration, not a new result.

| # | Criterion | Round 1 | Round 2 | Round 3 | Evidence |
|---|---|---|---|---|---|
| 1 | Distance from closest 5 papers | 3 | 3 | 3 | Campaign metric, feedback/heuristic/hybrid comparison on national US data held out by state, warm start and late-batch effect are not in the papers read; the transfer finding is. |
| 2 | Problem strength | 4 | 4 | 4 | Verified burden (about 40 million private-well users), documented practice of neighbour/history targeting, 33.9% sensitivity of the national map verified in the full text. |
| 3 | Depth of idea | 2 | 3 | 3 | Mechanism now tested three ways (across-state clustering correlation, weight-on-map sweep, synthetic fields with controlled correlation length), plus geology and warm-start tests. No new method or theory. |
| 4 | Evidence strength | 4 | 4 | 4 | 29-31 test states, 11 methods + heuristics, 5 seeds, Holm-corrected paired tests, 3 data designs, extended CA/CO run, regional, timing, availability, forward-in-time and negative-control checks. Single data source. |
| 5 | Generality | 3 | 3 | 4 | Three contaminants and six thresholds: arsenic (29-31 states), fluoride (31 and 17 states, 3 seeds), uranium (9 and 12 states, underpowered). The answer differs by contaminant (fluoride maps transfer), which the paper reports. Nitrate infeasible; one country; Kansas/Colorado/California gaps disclosed. |
| 6 | Journal-level match | 2 | 3 | 3 | Four Water Research papers cited, 45 references (journal median 52), geology tested; no geochemical process model; Guide for Authors unavailable. |

**Total 21/30 (round 1: 18; round 2: 20; round 3: 21). Gate 22/30 with no score below 3: NOT PASSED on the total (no individual score is below 3).** I did not raise scores that the evidence does not support. Reaching 22 would need depth that I cannot supply honestly from public data alone: hydrochemical predictors, a mechanism-level model, or a prospective agency pilot.
Novelty types claimed: N1 (campaign formulation, weak), N5 (held-out-state budgeted protocol, moderate), N7 (findings: feedback and local history help, hybrid and geology do not reliably add, late results erase much of the gain; moderate). N2 not claimed.

## Reviewer-zero sentences (desk rejection)
1. "A kernel neighbour update is a textbook idea; adaptive and active-search sampling for arsenic and hotspots already exist."
2. "Water Research publishes process understanding; this paper shows no geochemistry and no new mechanism."
3. "Random order is a weak baseline: agencies already use geology and prior results to choose wells."

Replies with evidence from the novelty map: (1) partly answerable: the contribution is the measured comparison on national held-out data, not the rule; (2) partly answerable after round 2 (clustering and regional analyses give a mechanism, but no geochemistry); (3) now answered in part: a hot-spot-following heuristic (H1) was tested and matches the kernel rule; no geology-informed baseline was tested. The paper is therefore at high risk of desk rejection at this journal.

## Honest claim chain
WHAT EXISTS: national ML arsenic maps (evaluated with random or within-region tests) and adaptive sampling designs. WHAT IT FAILS TO DO (as far as I found): quantify map transfer to a new state in budgeted campaign terms, or the gain from feedback relative to the map. WHY IT MATTERS: agencies choose testing order with limited budgets. WHAT THIS WORK ADDS: held-out-state campaign simulation and its numbers. HOW IT IS PROVEN: `results/` and `tables/`. No claim of "first".
