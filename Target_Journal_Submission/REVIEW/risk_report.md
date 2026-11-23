# Final rejection-risk report (round 3, 2026-11-23)
| Area | Risk | Evidence | Severity | Mitigation | Fixed? |
|---|---|---|---|---|---|
| Novelty | Related transfer/targeting work exists; no new method; gate 21/30 | novelty_scorecard.md | HIGH (fatal at a high-IF journal) | Add new data (hydrochemistry, prospective pilot) or target an evaluation-friendly venue | NO |
| Journal scope | ML evaluation study vs process-insight journal; Guide for Authors unreadable | journal_verification.md | HIGH | Check scope statement; consider another venue | NO |
| 72-day timeline | Median 81 d, p75 103 d (Water Research); no non-Frontiers journal tested passed | acceptance_time_evidence.csv, journal_comparison.md | HIGH (rule unmet) | None available | NO |
| JCR Q1/IF | Secondary sources: IF 12.8, Q1; official JCR unreachable | journal_verification.md | MEDIUM | Author to confirm in JCR | PARTLY |
| Methodology | Sound; states not independent; tuning not nested; simple grids | review_03, review_04 | MODERATE | Disclosed; LORO, extended run | PARTLY |
| Dataset | Non-random USGS wells; no depth/hydrochemistry; nitrate infeasible | limitations | HIGH | Thinning, forward-in-time, availability checks; disclosed | PARTLY |
| Statistics | Paired tests, Holm, CIs; robustness checks use 3 seeds, untested | statistics_*.csv | LOW-MODERATE | - | MOSTLY |
| Reproducibility | quick mode tested; full runs executed stepwise with the same commands; data download is slow and API-dependent | code/README.md, run_all.py | LOW-MODERATE | Authors re-run full mode once | PARTLY |
| Baselines | Heuristics H1, H2, lithology rule G0 added; no agency-protocol baseline | review_08 | MEDIUM | Needs agency input | PARTLY |
| Generalization | Arsenic, uranium (underpowered) and fluoride (3 seeds, Kansas missing); answers differ by contaminant; one country | review_05 | MEDIUM | Reported with limits; nitrate infeasible | PARTLY |
| Writing/formatting | Docx generated, not in Elsevier template; author fields blank | review_07 | MEDIUM | Apply template; Guide for Authors unavailable | NO |
| Citations | 45 refs, metadata-verified; 22 abstracts read; some metadata-only | citation_audit.md | LOW-MEDIUM | Read metadata-only papers | MOSTLY |
| Integrity/compliance | AI use disclosed; commercial similarity check not run; partial check clean | plagiarism_and_ai_text_check.md | MEDIUM | Run iThenticate | PARTLY |
No claim of zero risk or guaranteed acceptance is made.
