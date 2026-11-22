# Final audit and decision
## FINAL DECISION: NOT READY FOR SUBMISSION to Water Research
Reasons (each traceable): (1) novelty gate failed twice (17/30 then 18/30; gate 22); (2) journal-fit mismatch; (3) 72-day limit unmet for every non-Frontiers journal measured; (4) JCR status unverified; (5) references unverified and too few; (6) no expert-heuristic baseline, one contaminant, non-random wells.
More experiments cannot fix (1) or (2). Options for the authors: add hydrogeological covariates plus an agency-supplied warm-start and prospective test and aim for a venue that values evaluation studies; or merge with the other pending gap (a second contaminant once the API allows it).
## Consistency audit
Title <-> abstract <-> contributions <-> code <-> tables checked by construction: every number in `manuscript/Final_Manuscript.docx` is produced by `code/src/make_manuscript.py` from `tables/` and `results/`. Claims without a file are marked UNVERIFIED (claim_evidence_audit.md). Known mismatch: the protocol listed KMeans blocks as primary; the primary became leave-one-state-out (deviations.md items 3-12, all logged).
## Reproducibility audit
`python code/run_all.py --mode quick --skip-download` was executed successfully. The full runs were executed by hand with the same commands (logs in results/*.log); data download needs ~30 minutes and the USGS API sometimes times out (CA, CO). `data/raw/` is not committed (510 MB); `data/processed/` is.
## What is not done
25-paper full-text journal benchmark; 30-paper novelty map; nitrate; story figure; journal-template formatting; similarity check; DOI/author verification of references.
