# Final audit and decision (round 3, 2026-11-23)
## FINAL DECISION: NOT READY FOR SUBMISSION to Water Research
Reasons (each traceable):
1. Novelty gate not passed: 17/30, 18/30, 20/30, now 21/30 (gate 22; no single score below 3). Close prior work exists (transferability of fluoride models, buffered validation, neighbour-targeted outreach).
2. Journal fit unconfirmed: the Guide for Authors and the publisher page returned HTTP 403; the paper has no geochemical process model.
3. 72-day limit unmet for every non-Frontiers journal measured (Water Research: median 81 d, p75 103 d). JCR could not be checked; secondary sources give IF 12.8 and Q1.
4. No prospective test; non-random wells; one data source; uranium underpowered; nitrate infeasible; Kansas missing for fluoride; fluoride used 3 seeds.
5. Not in the Elsevier template; author, funding, CRediT and conflict fields are blank placeholders; commercial similarity check not run.
What is now done (round 3): verified reference list (45), full-text reads of key documents, 33-row novelty map (22 abstracts read), geologic predictors and lithology baseline, warm start with and without geology, heuristic and kappa analyses, synthetic-field test of the mechanism, delay/availability/leave-one-region/forward-in-time checks, extended California/Colorado run, uranium and fluoride, a tested planning tool, highlights, graphical abstract, cover letter, partial similarity check (clean), rewritten manuscript (16 pages).
Items that cannot be completed by me: official JCR/Guide-for-Authors verification, a prospective agency pilot, hydrochemical predictors from an agency, commercial similarity check, filling author declarations, final template formatting. These are listed so that nothing is silently dropped.
## Consistency audit
Every number in `manuscript/Final_Manuscript.docx` is produced by `code/src/make_manuscript.py` from `tables/` and `results/`; the script asserts that each highlight is at most 85 characters. Claims without a file are labelled (claim_evidence_audit.md). The protocol listed KMeans blocks as primary; the primary became leave-one-state-out; all 25 deviations are dated and explained in `code/experiments/deviations.md`.
## Reproducibility audit
`run_all.py --mode quick --skip-download` and `pytest` (5 tests) were run. Full runs were executed stepwise with the commands listed in `code/README.md`; data download depends on a slow API (about 30-60 minutes per contaminant; some states needed date-window requests). `data/raw/` is not committed; `data/processed/` is.
