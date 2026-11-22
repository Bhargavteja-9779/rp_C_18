# Cold-start well-testing campaigns (arsenic): code
Run from `code/`:
```
pip install -r requirements.txt
python run_all.py --mode quick     # pipeline check (~2 min; downloads data if missing, ~30 min)
python run_all.py --mode full      # all experiments, tables, figures
python src/make_manuscript.py      # run from the submission root
pytest tests
```
Data: USGS Samples API (public). `download_usgs.py` fetches arsenic by state (some large states may time out). Protocol: `experiments/protocol.md`; deviations: `experiments/deviations.md`.
