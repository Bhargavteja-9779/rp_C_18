# Final rejection-risk report (round 4, 2026-11-23)
| Area | Risk | Evidence | Severity | Mitigation | Fixed? |
|---|---|---|---|---|---|
| Editorial desk rejection (ES&T Letters) | Fast triage (secondary source: median 3.8 d); simulation study; simple rule | novelty_scorecard.md, review_09 | HIGH | Cover letter stresses measured decision-relevant effect sizes, 3 contaminants, ABF with bound, failure modes; fallback journals | PARTLY |
| Novelty | Close prior work on transfer and neighbour targeting; ABF is standard aggregation | novelty_map.csv | MEDIUM-HIGH | Claims limited to measured comparison; no 'first' claim | PARTLY |
| 72-day timeline | Met on median 47 d / p75 66 d (n=121); some years p75 ~72 | acceptance_time_evidence.csv | MEDIUM | None needed; survivorship caveat | YES (with margin risk) |
| Format/length | Limits from a search snippet; Guide for Authors blocked | journal_verification.md | MEDIUM | Author to check; Letter is 2,435 word-equivalents | PARTLY |
| JCR Q1/IF | Secondary sources only | journal_verification.md | MEDIUM | Author to confirm | NO |
| Methodology | Error found and fixed (aquifer code); states not independent; simple grids | deviations 33, review_03 | LOW-MODERATE | Reran everything; LORO; disclosed | MOSTLY |
| Dataset | Non-random USGS wells; no hydrochemistry; nitrate infeasible; Kansas missing (fluoride) | limits | HIGH | Thinning, forward-in-time, availability checks; disclosed | PARTLY |
| Statistics | Paired tests, Holm, CIs; borderline ABF vs feedback (As>10) reported | statistics_*.csv, abf_statistics.csv | LOW | - | YES |
| Reproducibility | Code on request only (user choice); API slow | code/README.md | MEDIUM (editors favour open code) | Code package prepared | PARTLY |
| Baselines | Heuristics, lithology rule, stronger maps added; no agency protocol | review_08 | MEDIUM | Needs agency input | PARTLY |
| Generalization | Three contaminants; one country; uranium underpowered | review_05 | MEDIUM | Reported | PARTLY |
| Writing/formatting | ACS template not applied; author fields blank | review_07 | MEDIUM | Author step | NO |
| Citations | 45 refs in SI, 29 in Letter; metadata-verified; 22 abstracts read | citation_audit.md | LOW-MEDIUM | Read metadata-only papers | MOSTLY |
| Integrity/compliance | AI use disclosed; partial similarity clean; commercial check not run | plagiarism_and_ai_text_check.md | MEDIUM | Author step | PARTLY |
No claim of zero risk or guaranteed acceptance is made.
