# Review stakeholder: Real-world stakeholder: state private-well programme officer

## ROUND 4 (final, 2026-11-23)
I would use the guide: seed the rule with my own earlier results, test in small batches, and check whether a map transfers before trusting it. The planner tool turns that into a next-batch list. Missing: cost per test and travel, refusals beyond the 30% check, and a field pilot. ABF needs batches of about 10 wells, which may be hard if the laboratory returns results in weeks.

---
Earlier rounds (kept for the record; some numbers superseded by the corrected runs):

Would I use it? Partly. A rule that says 'after each batch, follow the hot spots' matches field instinct and the numbers (about 19 vs 11 unsafe per 100 tests) are in units I understand.
What is missing: (1) my state already holds past results, so cold start is rare; a warm-start analysis is more relevant. (2) Cost per test, travel, owner refusals. (3) A tool I can run, not code. (4) Wells I can test are private wells, not USGS study wells.
ACTIONS TAKEN: limitations list items 1-2. NOT FIXED: warm-start analysis, tool.

ROUND 2: warm-start analysis added (agency with its own past results): local history makes the map useful (2.05x) and history plus feedback is best on average (2.17x); pooled national data did not help (10 ug/L) or hurt (5 ug/L). Still open: cost per test, a usable tool.

ROUND 3: a command-line planner (code/campaign_planner.py, tested) now turns candidate wells, results so far and optional history into the next batch. Warm-start analysis and the batch-size result translate into advice: use history as a prior, test in small batches, expect no gain if results return late. Still open: cost per test and refusals beyond the 30% availability check; field validation.
