# Stage 1 — journal re-verification (2026-11-23)
Target: Environmental Science & Technology Letters (ACS), ISSN 2328-8930. Script: RECHECK/journal_recheck.py (PubMed history dates). All numbers below were recomputed from scratch.

## Acceptance time (received -> accepted)
- Pooled 2022-2026: n = 143 dated papers (of 183 indexed): **median 47 d, 75th percentile 66 d**, 90th percentile 96 d, max 224 d.
- Last 6 months (accepted since 2026-05-23): n = 10: median 38 d, 75th percentile 68 d.
- By accepted year: 2022 n=24 median 45 p75 71; 2023 n=31 median 42 p75 64; 2024 n=34 median 57 p75 **74**; 2025 n=30 median 42 p75 62; 2026 n=22 median 44 p75 **73**.
- Verdict: pooled and last-6-months figures meet the rule (median well under 72, p75 <= 72). Two calendar years (2024, 2026 to date) have a p75 of 73-74 d, i.e. slightly OVER 72 d. The first run's statement 'p75 71.75 for 2026' is replaced by 73 d (n=22). The rule is met with little margin and is not met in every single year. Survivorship caveat unchanged: only accepted papers have dates.
- Evidence: RECHECK/acceptance_time_estl_sample.csv (40 random papers with DOI and dates), journal_estl_stats.json, journal_estl_newest10.json.

## Alternatives measured (same method), none passes
Environmental Science & Technology Water: median 111, p75 148 (n=278). Environmental Health Perspectives: 128/154 (n=27). GeoHealth: 141/202 (n=477). J. Exposure Sci. & Environ. Epidemiology: 184/246 (n=628). Communications Earth & Environment: 178/236 (n=200, Crossref). npj Clean Water: 68/88 (n=175). Nature Water: 205/300 (n=175). Earlier rounds: Water Research 81/103, Environmental Research 86/126, Environmental Pollution 90/123, J. Hazardous Materials 105/126, ES&T 112/158, Environment International 117/155, Frontiers (excluded by user), Springer Nature journals 148-266. Decision: keep ES&T Letters (the only journal that passes pooled median and p75).

## Integrity
PubMed notices (retraction, retracted publication, expression of concern) for ES&T Letters 2022-2026: 0 found. This is a PubMed-indexed-record check only; indexing status in Scopus/WoS and any ACS publisher notices were NOT checked (UNVERIFIED).

## Official-source items (all UNVERIFIED)
pubs.acs.org returned HTTP 403 to the fetch tool, again: JCR quartile, impact factor, JCR category, scope statement, APC, Letters length limit, abstract/synopsis/TOC rules, SI rules, data/code/AI policies. A search returned only third-party pages (length 'up to 3,000 word-equivalents, 200 per figure/table'; over-length manuscripts returned or rejected; TOC graphic required for Letters). Treat these as unconfirmed.

## Level of the journal: ten newest papers (accepted 2026-06 to 2026-09)
Median 46 references (range 12-159), median title 12.5 words, median abstract about 200 words. Topics: mostly experimental atmospheric and water chemistry (VMS emissions, SO2 oxidation, HAP measurements, catalysis for groundwater treatment). Scope-fit count (PubMed, 2023-2026, n=157 papers): 14 mention machine learning/data-driven methods, 16 groundwater or drinking water, 1 private wells, 4 arsenic/fluoride/uranium. Implication: a data-science Letter on private wells is within the journal's themes but is not the typical paper; scope fit is plausible, not certain. The Letter has 30 references (below the median of 46): to be raised in Stage 7 with verified, relevant entries only.
