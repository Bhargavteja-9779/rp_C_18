# FINAL RE-CHECK REPORT (2026-11-23)

## 1. What changed since the first run, and why
- Journal: re-measured from scratch. ES&T Letters kept (pooled median 47 d, p75 66 d, n=143; last 6 months median 38, p75 68, n=10). Seven alternatives measured: none passes. Two calendar years (2024: p75 74; 2026 to date: p75 73) exceed 72 d, so the first run's '71.75' figure is replaced by 73. Official pages (JCR, scope, APC, guidelines) are still unreadable (HTTP 403): UNVERIFIED.
- Prior art: search repeated with new keywords and other fields; map extended from 33 to 53 papers. New CLOSE CALLS: ActiveRemediation (lead pipes, same problem structure), Thompson 1990 adaptive cluster sampling (classical form of the follow-unsafe rule). The Letter, cover letter and scorecard were rewritten to claim only what is different.
- Experiments: clean-environment rerun (identical), leakage hunt, stress tests, learner check, two new idea tests, forecast calibration, reproducibility bugs fixed.
- Claims/text: pooled-AUC wording; feedback gain described as borderline outside arsenic>10; negative results added; references 46 -> 49, all re-verified.

## 2. Bugs and errors found and fixed (this run)
1. README quick mode needed raw data a stranger lacks; run_all.py now falls back to data/processed. 2. run_all.py failed on a clean checkout (no tables/ folder); fixed. 3. Letter's 'ROC-AUC 0.64 held-out' is pooled over states; within-state AUC is 0.51; now stated. 4. In-text citation 'Horton, 2017' lacked a verified reference and NASA POWER had none (fixed before this run, rechecked here). 5. A reference-matching script false-alarmed (SequenceMatcher autojunk; 429 rate limits; DataCite DOI) - fixed and rerun. 6. First-run depth score of 4 withdrawn (now 3). 7. A duplicate method started in a parallel continuation was discarded earlier (deviation 35).
Earlier (round 4) error: aquifer code treated as a number in early runs; all affected runs repeated.

## 3. Novelty scorecard
Before (first run): 23/30. After re-check: **21/30** (distance 3, problem 4, depth 3, evidence 4, generality 4, journal match 3). Evidence in RECHECK/novelty_scorecard_recheck.md. Elevation stop rule (26/30 with distance and evidence >= 4) not reached; 2 of 6 rounds used; label: STRONGEST HONEST VERSION.

## 4. Closest competing papers and how this work differs
See RECHECK/novelty_map_50.csv (53 rows, close-call column) and stage3_priorart.md. In one line each: ActiveRemediation (same structure, different hazard and no held-out-region/contaminant comparison); Thompson 1990 (classical rule; no maps, no well data); Cao 2024a and Usman 2026 (fluoride transfer; no campaign metric); MacDonald and Tippett 2020 (practice, not measured); Yin 2021 (static design).

## 5. Negative results and failed ideas (kept)
- Region-weighted map training: +0.38 for arsenic>10 (Holm 0.019, replicated on fresh seeds) but -0.11 for arsenic>5; not adopted; still below feedback.
- Remaining-yield forecast: better than naive scale-up (error 0.24 vs 0.48 at 20% tested, arsenic>10; fluoride 0.30 vs 1.58) but not better than map-only; 80% intervals cover 6-27% uncalibrated; conformal recalibration gives coverage 0.65-0.97 with widths up to 1.7 times the truth. No stopping rule offered.
- Hybrid map+feedback: not better than feedback for arsenic and uranium; geology helps only modestly; other learners do not beat feedback.
- ABF: not the best rule in any outcome except arsenic>5; its worst gap is 0.35 (arsenic>10); more sensitive to late results.
- Ideas generated 8, tested 2 (+1 recalibration variant), confirmed 0.

## 6. Remaining risks
| Area | RISK | EVIDENCE | SEVERITY | MITIGATION | FIXED? |
|---|---|---|---|---|---|
| Novelty | idea of feedback is classical; closest papers found | map, scorecard 21/30 | HIGH (main desk-rejection reason) | repositioned honestly | NO |
| Methodology | states not independent; tuning not nested; ABF bound is on loss | R3 | MODERATE | stress tests, disclosure | PARTLY |
| Dataset | USGS study wells, not random; no hydrochemistry; one country; nitrate missing; Kansas missing | limits | HIGH | thinning, forward-in-time, availability checks | PARTLY |
| Statistics | uranium 9-12 states; plain feedback borderline outside arsenic>10 | Table S-A | MODERATE | stated | YES (stated) |
| Reproducibility | only arsenic>10 re-run from scratch; raw download slow; code on request | R5 | MODERATE | README fixed; clean rerun | PARTLY |
| Baselines | no GP active-search or commercial lead-pipe comparator | stage5 | MODERATE | UNVERIFIED comparison to top-3 published methods | NO |
| Generalization | no field trial | R1/R4 | HIGH | planner, pilot recommended | NO |
| Writing | intro dense; 33 refs vs journal 46; not in ACS template | stage7 | MODERATE | partial | PARTLY |
| Formatting | live guide unreadable; limits unverified | stage1 | MODERATE | check live guide | NO |
| Citations | 41/46 auto-verified; 18 metadata-only (abstract unread); 3 new verified by lookup | stage6 | LOW-MODERATE | read them | MOSTLY |
| Journal scope | 1 private-well paper in 157; mostly chemistry | stage1 | HIGH | none possible | NO |
| Journal-specific reviewer | will want measurements, not simulation | R1 | HIGH | none possible | NO |
| Integrity | PubMed shows 0 retraction/concern notices; Scopus/WoS/publisher notices unchecked | stage1 | LOW | check | PARTLY |
| 72-day timeline | pooled p75 66 (met); 2024 and 2026 p75 73-74 (not met); survivorship | stage1 | MODERATE | none | PARTLY |
Submission checklist (live guide unreadable, every item UNVERIFIED): word-equivalent limit (2,673 vs assumed 3,000), synopsis (~20 words: present), TOC graphic (present), abstract format, SI file (present), reference style, data/code statements (code on request), AI-use disclosure (present), author/ORCID/funding/conflict fields (placeholders), cover letter (present), similarity check (partial only).

## 7. Items still UNVERIFIED
JCR quartile, impact factor and category; scope statement; APC; Letters length/format rules; SI, data, code and AI policies; Scopus/WoS status and publisher notices; comparison with 'the three best published methods' (no GP active-search or lead-pipe system baselines); whole-package full rerun; commercial similarity check; whether a recent ES&T Letters paper should be cited; abstracts of 18 references; non-arsenic scenarios re-run from scratch; Letter file separately similarity-checked.

## 8. Final decision
**NOT READY: ADDITIONAL WORK REQUIRED.** By this prompt's own criteria the novelty stop rule was not reached (21/30; distance 3), the official journal items remain unverified, and two single-year acceptance-time p75 values exceed 72 d. The remaining work cannot be done honestly with public data and the tools available here: it needs a field pilot or agency data, hydrochemical predictors, and access to the live guide and JCR. Two elevation rounds with pre-registered tests produced no confirmed gain, and I did not inflate scores. The package itself is complete and internally consistent, and the authors can submit it at their own judgement, accepting a high desk-rejection risk; no acceptance is implied.

## ADDENDUM (round 6, 2026-11-23): response to 'make the paper stronger and more novel at the ES&T Letters level'
- Journal: ES&T Letters kept at the user's confirmation. Four more candidates measured: Environmental Health median 124 d, p75 184 d; Risk Analysis 272/398; Int. J. Hygiene and Environmental Health 118/152; none passes 72 d (a fourth measurement, Water Research X, was killed before finishing).
- New evidence: real-campaign replay (53, 59, 49 and 25 campaigns; see novelty log). Real historical order was about random (1.0-1.2); adaptive reordering gave 1.4-1.6 (arsenic) and 2.2 (fluoride), significant after Holm for arsenic and fluoride, not for uranium. Added to the Letter (one paragraph, 2,820 word-equivalents of an assumed 3,000 limit) and the SI (Table S-R); cover letter and consistency check updated (30 replay numbers verified against files).
- New documents: field pilot protocol with sample sizes from the replay (22-52 programmes for 80% power depending on the rule; RECHECK/field_pilot_protocol.md, NOT RUN) and a pre-submission inquiry draft (whether ES&T Letters accepts inquiries is UNVERIFIED).
- Decision unchanged: NOT READY by the stated criteria (novelty 21/30; official journal facts unverified). The package is stronger on real-world evidence, which was the largest evidence gap an editor could cite; the idea-level novelty and journal-scope risks remain and cannot be removed by analysis. No acceptance is implied.

## ADDENDUM 2 (2026-11-24): ActiveRemediation read in full; hierarchical ABF; replay robustness
- CORRECTION: ActiveRemediation (Abernethy et al. 2018, arXiv 1806.10692, full text read) already combines a predictive model with sequential importance-weighted active learning, backtests against the order actually used in Flint (hit rate 98.0% vs 81.2%), compares greedy and uniform exploration and checks batch-size robustness. The replay of real campaigns is not new in kind; the Letter, cover letter and SI now say so. Novelty score lowered to 20/30 (distance 2).
- Hierarchical ABF (starting weights learned from other states; deviation 44): no gain in any of 9 runs; significantly worse for uranium > 30; idea dropped (negative result).
- Replay with maps trained on earlier years only: arsenic > 10 keeps 32 of 53 campaigns; only follow-unsafe stays significant after Holm (feedback p = 0.056, ABF 0.143); same-campaign comparison shows the weaker result comes from fewer campaigns, not from future data in the map. Arsenic > 5 and fluoride hold.
- Replay with larger batches: arsenic > 10 gain holds at 50 wells per round, disappears at 200 (feedback 1.03); fluoride holds at 200 (1.71); ABF was better than feedback at 200 for fluoride (falsifier of the pre-registered hypothesis).
- Connecticut private-well data release (674 wells): coordinates withheld; cannot be used.
- Nitrate: background download still running (very slow; each 3-year window takes minutes).

## ADDENDUM 3 (2026-11-24, long run): nitrate, route length, clean reruns
- Nitrate (fourth contaminant): 47,375 wells in 49 states, downloaded in 3-year windows over about 3.5 hours, processed under rules fixed beforehand (NO3 converted to N). Held-out states: map 1.17x random at both 10 and 5 mg/L as N; feedback 1.66 and 1.76; ABF 1.75 and 1.73 (ABF beats the map, unadjusted p 0.0025 and 0.0002). Replay (28 campaigns, 20 states): real order 1.00; follow-unsafe 1.46, feedback 1.36, ABF 1.33; not significant after Holm (p 0.09-0.16), like uranium.
- Route length (minimum spanning tree of tested wells per unsafe well found, replayed campaigns): arsenic > 10: real 156 km, random 179, follow-unsafe 74 (Holm 0.006), ABF 97 (0.044), feedback 117 (n.s.); arsenic > 5 and fluoride > 2: adaptive rules lower (Holm <= 0.04). Straight-line proxy only.
- Clean-environment reruns: arsenic > 10, > 5, uranium 30 and 10, fluoride 2 and 4 (held-out-state experiment), ABF for arsenic > 10 and the arsenic > 10 replay all reproduced the stored results exactly (maximum difference 0.0000; identical tuning). Not re-run from scratch: geology/environment runs, extended CA/CO run, learner check, forecast, hierarchical ABF, replay variants, nitrate.
- New negative results: hierarchical ABF (no gain, 9 runs); replay with maps trained only on earlier years (weaker for arsenic > 10 because 21 campaigns are dropped); replay with 200-well rounds (arsenic gain gone; fluoride persists).
- Connecticut private-well data release unusable (coordinates withheld). ActiveRemediation read in full (see Addendum 2): novelty score 20/30.
- Decision unchanged: NOT READY by the stated criteria; the package is more complete and better verified; no acceptance is implied.
