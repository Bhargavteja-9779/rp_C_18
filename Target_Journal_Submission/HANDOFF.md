# HANDOFF (read first in a new account)
Repo root: rp_C_18; project: Target_Journal_Submission; branch claude/zealous-johnson-kxpouu. Also read STANDING_INSTRUCTIONS.md, PROGRESS.md, RECHECK/final_recheck_report.md, AUTHOR_CHECKLIST.md.
## State (2026-11-24)
- Study: adaptive ("feedback") testing vs transferred risk maps for private wells (USGS Samples data; arsenic/uranium/fluoride/nitrate; leave-one-state-out). Honest novelty 20/30 ("strongest honest version"); decision NOT READY by stated criteria (modest novelty; closest prior work ActiveRemediation, Abernethy 2018).
- Letter rewritten for ES&T Letters readers (plain language, new US map Figure 1 `figures/letter_map_as10.png`, abstract 204 words, stale "nitrate not retrieved" text fixed). Letter title: "Adaptive Testing Finds Unsafe Private Wells Faster Than Risk Maps from Other States".
- ES&T Letters timing: pooled median 47 d, p75 66 d; calendar-year p75 2024=74, 2026=73 (>72) -> rule met only pooled. Official ACS/JCR/APC pages were HTTP 403: UNVERIFIED.
## Commands (run from Target_Journal_Submission)
- Letter + cover: `python3 code/src/make_letter.py`; SI/manuscript: `python3 code/src/make_manuscript.py`; package: `python3 code/src/build_package.py`.
- Benchmark: PubMed esearch `2328-8930[ISSN] AND 2025:2026[dp] AND pubmed pmc[sb]`, esummary articleids->PMC, efetch PMC XML (see STYLE_BENCH/README.md).
- Raw data (data/raw, ~1.6 GB) is NOT in git: re-download with code/download_usgs.py / code/download_chunked.py; data/processed IS in git so quick mode runs: `python3 code/run_all.py --mode quick`.
## Pending work (next ideas)
1. Add more verified references (median ES&T Letters ~47; ours 32) and a second environmental-science figure if useful.
2. Re-run adversarial reviews of the rewritten Letter as an ES&T Letters editor; fix SI/Final_Manuscript wording to match plain-language Letter; rebuild package.
3. Possible genuine new methods: field-pilot design (RECHECK/field_pilot_protocol.md), pre-submission inquiry (RECHECK/presubmission_inquiry_draft.md). Pre-register each in code/experiments/deviations.md (items 1-50 used) before running; report negatives.
4. Authors must fill: second author name/department/email, ORCIDs, date; verify live ACS rules, IF/quartile, APC; run commercial similarity check.

## Update 2026-11-24 (2)
Letter now cites 40 references (journal median ~47); R7 editor screen added (RECHECK/review_R7_ESTL_editor.md); novelty stays 20/30 (target 25 not reached; needs field pilot).

## Update 2026-11-24 (3)
Items 51-54: multi-contaminant panel feedback. Redox signature transfers between states, but no confirmed search gain (P2X confirmation failed). SI 4.24 + one Letter sentence. Letter 2,998 word-equivalents.
