# Final rejection-risk report
| Area | Risk | Evidence | Severity | Mitigation | Fixed? |
|---|---|---|---|---|---|
| Novelty | Simple rule; related adaptive/active search exists; novelty gate 20/30 (was 18) | novelty_scorecard.md | FATAL for Water Research | Add process insight/prospective test or choose another venue | NO |
| Journal scope | ML evaluation vs process-insight journal | journal_level_profile.md (abstract-level) | HIGH | Re-target | NO |
| 72-day timeline | Median 81 d, p75 103 d (Water Research); no non-Frontiers journal tested passed | acceptance_time_evidence.csv, journal_comparison.md | HIGH (rule unmet) | None available | NO |
| JCR Q1/IF | Not verified | journal_verification.md | MEDIUM | Author to verify | NO |
| Methodology | Sound; spatial non-independence of states; tuning not nested | review_03, review_04 | MODERATE | Disclosed | PARTLY |
| Dataset | Non-random USGS wells; no depth; CA, CO missing | limitations | HIGH | Disclosed; thinning check | PARTLY |
| Statistics | Paired tests, Holm, CIs | statistics_*.csv | LOW | - | YES |
| Reproducibility | run_all.py quick mode tested; full mode run in pieces by hand (same commands) | code/run_all.py | LOW | Authors should rerun full mode once | PARTLY |
| Baselines | Heuristic H1 added; no geology-informed baseline | review_08 | MEDIUM | Needs geology data/agency input | PARTLY |
| Generalization | Arsenic plus uranium (9-12 states, underpowered); one country | review_05 | MEDIUM-HIGH | Nitrate download failed | PARTLY |
| Writing/formatting | Docx generated, not in journal template; author fields blank; abstract long | review_07 | MEDIUM | Apply Elsevier template | NO |
| Citations | 15 refs; 11 metadata-verified, none read in full | citation_audit.md | MEDIUM | Read and extend | PARTLY |
| Integrity/compliance | AI-use disclosed; similarity check not done | plagiarism_and_ai_text_check.md | MEDIUM | Run iThenticate | NO |
No claim of zero risk or guaranteed acceptance is made.
