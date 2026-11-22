# PROGRESS (2026-11-22)

## Phase 0 — journal (done, with an unmet rule)
- Measured received->accepted days by script (PubMed/Crossref history dates) for 27 journals. Only Frontiers titles were near 72 days.
- Chosen provisionally: Frontiers in Plant Science (median 54.5 d, p75 76 d). **p75 > 72: rule unmet.** JCR Q1/IF UNVERIFIED (JCR unreachable).
- All tested Springer Nature, Elsevier, OUP, JMIR, PLOS journals failed by a wide margin (medians 86-275 d). A strict 72-day limit with Q1 and a non-Frontiers publisher was not achievable with the evidence I could collect.

## Phase 1 — benchmark / style: NOT DONE

## Phase 2-3 — topic and novelty (gate FAILED)
- Idea: severity-weighted miss-risk control for national crop-shortfall alerts (FAOSTAT + NASA POWER, both verified downloadable).
- Search found a closer paper than expected: "Average Coverage Hides Failing Years ... Year-Level Conformal Procedure" (Zenodo 24274873, dated 2026-11-16). Scorecard <= 17/30, below the 22 gate. Per the brief, the idea is abandoned instead of being dressed up.
- No experiments, no manuscript, no reviews were produced. Nothing in this folder reports a result.

## Next
Pick a different problem (or read the 2026 paper in full to find a real gap), rebuild the novelty map to 30 papers, run the benchmark, then continue from Gate 3.
Tools in `code/` (`pubmed_dates.py`, `journal_dates.py`) are reusable and verified.
