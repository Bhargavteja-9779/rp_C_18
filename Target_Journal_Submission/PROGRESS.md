# PROGRESS (2026-11-22) — final state

## Decisions (with reasons)
- Journal: you excluded Frontiers/MDPI. Measured 36 journals by script. Every non-Frontiers journal failed 72 days (best: Water Research, median 81 d, p75 103 d). Chosen as strongest verifiable Q1 candidate; 72-day rule and JCR status are UNMET/UNVERIFIED. (journal_selection/)
- Topic 1 (conformal crop-shortfall alerts) dropped: a 2026 paper on year-level conformal yield intervals overlaps; scorecard 17/30.
- Topic 2 (cold-start arsenic well-testing campaigns): built, run, written. Scorecard 18/30 < 22 gate.
- Failed items kept in the record: California/Colorado and nitrate downloads; hybrid method did not beat feedback-only; static map ~ random in new states.

## Gates
1 journal 72-day: NOT PASSED (documented) | 2 real problem + stress test: passed with caveats | 3 novelty >= 22/30: NOT PASSED (18/30) | 4 protocol pre-registered: yes (+ deviations logged before runs) | 5 leakage audit: done | 6 reviews: 10 + stakeholder done, fixes applied where possible.

## Result: NOT READY FOR SUBMISSION (see REVIEW/final_audit.md)

## Round 2 (2026-11-23) — strengthening
- Added: heuristic baselines (H1 follow-unsafe, H2 spread), kappa sweep, clustering mechanism, regional check, warm-start design, second contaminant (uranium, 9 and 12 states), M7 fairness check, negative control, timing, story figure, shorter abstract, metadata-verified references plus four Water Research citations.
- Findings changed the paper: the hybrid method is negative; a simple heuristic matches the kernel rule; a state's own history makes the map useful; the South shows weak feedback gain; uranium is underpowered.
- Novelty scorecard now 20/30 (gate 22): NOT PASSED. Still NOT READY FOR SUBMISSION (see REVIEW/final_audit.md).
- Deviations 13-15 logged before the added runs.

## Round 3 (2026-11-23) — completing open items
Done: verified references (45) and full-text/abstract reads; 33-row novelty map; geology predictors (SGMC) and lithology baseline; warm start with geology; delay/availability/leave-one-region/forward-in-time checks; synthetic-field mechanism test; extended CA/CO arsenic; uranium and fluoride; planner tool with test; highlights, graphical abstract, cover letter; partial similarity check (clean); rewritten 16-page manuscript; updated audits and risk report.
Findings that changed the paper: geology helps only modestly; late batches cut the gain; fluoride maps DO transfer (conclusions are contaminant-specific); the 2024 transferability paper and neighbour-letter outreach reduce the novelty of the transfer result.
Could not be completed (reasons in REVIEW/final_audit.md): official JCR and Guide for Authors (HTTP 403), nitrate (API too slow), Kansas fluoride, prospective pilot, commercial similarity check, Elsevier template, author declarations.
Scorecard 21/30 (gate 22). FINAL DECISION: NOT READY FOR SUBMISSION.
