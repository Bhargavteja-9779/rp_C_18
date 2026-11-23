# Novelty scorecard (round 3, 2026-11-23; topic: well-testing campaigns for arsenic)

Evidence: `novelty_map.csv`: 33 papers, 22 of them with the abstract read (PubMed/arXiv), the rest title/metadata or search snippets; three documents read as text (Lombard, Appiah, CDC/Vermont). The brief asked for 30 closest papers; this is met in count but not in depth of reading.

New close prior art found in round 3: Cao et al. 2024 (transferability of fluoride models between basins; surface predictors fail, adding target-region samples helps), Usman et al. 2026 (buffered validation; negligible national transfer for environmental-only models), MacDonald & Tippett 2020 (neighbour-exceedance letters raise testing), O'Neill et al. 2022 (history-based outreach). The finding that maps trained elsewhere do not transfer is therefore corroboration, not a new result.

| # | Criterion | R1 | R2 | R3 | R4 | Evidence (round 4) |
|---|---|---|---|---|---|---|
| 1 | Distance from closest 5 papers | 3 | 3 | 3 | 3 | Closest: transferability of fluoride models (Cao 2024a), buffered national validation (Usman 2026), neighbour-letter outreach (MacDonald 2020), active/budgeted search (Garnett 2012; Khan 2026). None read compares map, feedback and own history on national held-out data for three contaminants. ABF is an application of standard expert mixtures. |
| 2 | Problem strength | 4 | 4 | 4 | 4 | About 40 million US private-well users (abstract of Amery 2025); 33.9% sensitivity of the national map verified in full text; agencies already target by past results. |
| 3 | Depth of idea | 2 | 3 | 3 | 4 | New adaptive rule with a stated reason and a numerically verified bound on prediction loss (not on discovery); mechanism tested three ways (state-level clustering, kappa sweep, synthetic fields with controlled correlation length); negative results (hybrid, geology, late batches) explained or labelled untested. Most contestable score. |
| 4 | Evidence strength | 4 | 4 | 4 | 4 | 29-31 test states for arsenic and fluoride, 6 outcomes, paired Holm-corrected tests, 3 split designs, extended run, regional/LORO/forward-in-time/availability/delay checks, negative control, one error found and fixed with all runs repeated. |
| 5 | Generality | 3 | 3 | 4 | 4 | Three contaminants, six outcomes; results differ by contaminant and are reported as such; one country; nitrate infeasible; uranium underpowered. |
| 6 | Journal-level match | 2 | 3 | 3 | 4 | ES&T Letters: environmental relevance clear; ES&T family published the national arsenic and transfer papers; time rule met (median 47, p75 66 days). Format limits unverified (Guide for Authors blocked). |

**Total 23/30 (R1 18, R2 20, R3 21, R4 23). Gate 22/30 with no score below 3: PASSED on the self-assessed scores.** Caveat: these are my own scores. Scores 1 and 3 are the ones an editor is most likely to dispute; if the depth score were 3 the total would be 22, still at the gate. Desk-rejection risk at ES&T Letters remains real (secondary sources report a median 3.8 days to an editorial decision without review).

## Reviewer-zero sentences (round 4)
1. "A kernel rule and an expert mixture are textbook; this is incremental." Reply: the measured effect sizes on national held-out data, the contaminant dependence, the late-results failure mode and the bound-backed rule that needs no prior knowledge are the contribution; no new learning theory is claimed.
2. "Simulation on study wells is not evidence for a real campaign." Reply: partly valid; thinning, availability, delay and forward-in-time checks and a synthetic control address artefacts, not selection bias; a field pilot is the stated next step.
3. "Why should ES&T Letters readers care?" Reply: tests per unsafe well for drinking-water protection, in 40 million users' terms, with a decision guide.

## Honest claim chain
WHAT EXISTS: national ML arsenic maps (evaluated with random or within-region tests) and adaptive sampling designs. WHAT IT FAILS TO DO (as far as I found): quantify map transfer to a new state in budgeted campaign terms, or the gain from feedback relative to the map. WHY IT MATTERS: agencies choose testing order with limited budgets. WHAT THIS WORK ADDS: held-out-state campaign simulation and its numbers. HOW IT IS PROVEN: `results/` and `tables/`. No claim of "first".
