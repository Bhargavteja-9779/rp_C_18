# Well-testing campaigns (arsenic, uranium): code and data pipeline
Everything runs from the submission root unless stated. Python 3.13; see `requirements.txt` (adds geopandas, pyogrio, shapely for the geology join).

## Quick check (about 2 minutes once data exist)
```
cd code && pip install -r requirements.txt && python run_all.py --mode quick --skip-download && pytest tests
```
## Full reproduction (hours; USGS API is slow)
```
python code/run_all.py --mode full
```
`run_all.py` downloads arsenic by state (`download_usgs.py`), builds the well table (`src/build_dataset.py`), runs the main leave-one-state-out, 5 µg/L, block and thinned experiments (`src/experiment.py`), the added experiments (`src/extra_experiments.py`, `src/analyze_extra.py`), robustness checks (`src/robust_checks.py`, `src/temporal_check.py`, `src/synthetic_mechanism.py`, `src/extra_checks.py`, `src/m7_weight_check.py`), tables and figures, and the manuscript.

Steps run by hand and not wrapped in run_all (same commands, logs in `results/experiment_logs/`):
- Uranium: `python code/download_usgs.py Uranium data/raw/u`; `python code/src/build_dataset.py data/raw/u data/processed/wells_u.csv Uranium 30 10`; `python code/src/experiment.py --data data/processed/wells_u.csv --label y30 --ntune 4 --out results/u30` (and `--label y10 --out results/u10`).
- Geology: download the SGMC shapefiles from ScienceBase (item 5888bf4fe4b05ccb964bab9d) into `data/raw/sgmc/`; `python code/src/build_geology.py data/processed/wells_as.csv data/processed/wells_as_geo.csv`; run experiments with `WELL_FEATS=geo` and the `_geo` data files; `python code/src/analyze_geology.py`.
- California/Colorado arsenic: `python code/download_chunked.py Arsenic data/raw/as_ca_co 1960 2026 4 06 08`, merge, rebuild, and run `--out results/as10_full`.
- Fluoride (mg/L): `python code/download_usgs.py Fluoride data/raw/f` (large states time out: refill with `python code/download_chunked.py Fluoride data/raw/f_chunk 1960 2026 6 <state codes>`; Kansas could not be retrieved), merge the files, `python code/src/build_dataset.py data/raw/f_all data/processed/wells_f.csv Fluoride 4 2 mg/L`, then `python code/src/experiment.py --data data/processed/wells_f.csv --label y2 --seeds 3 --out results/f2` (and `--label y4 --out results/f4`).
- References: `python code/src/refs.py` (Crossref/arXiv lookups).

## Planner for agencies (research tool)
```
python code/campaign_planner.py --wells candidate_wells.csv --results tested_so_far.csv --history earlier_state_wells.csv --batch 10 --bandwidth 5
```
Inputs: `well_id,lat,lon` for candidates; `well_id,unsafe` for tested wells; optional `lat,lon,unsafe` history. Output: the next batch ranked by kernel-weighted unsafe results (follow-unsafe rule); with no unsafe result yet it spreads tests in space. It is the rule evaluated in the paper, not a validated public-health product. Results should come back in small batches (see paper).

Protocol: `experiments/protocol.md`; every deviation, with date and reason: `experiments/deviations.md`.
