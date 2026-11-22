# Journal level profile — Water Research (abstract-level only)

Source: 30 ML-related papers from 2024-2026 (`journal_benchmark.csv`), read through PubMed titles and abstracts only. Full texts (datasets, baselines, seeds, tests, code) were NOT readable here, so those numbers are UNVERIFIED. The brief asked for 25 full papers; this is a weaker substitute.

- Median title length 15 words; median abstract 233 words.
- 20/30 abstracts name a field setting (plant, river, utility, catchment, wastewater).
- 20/30 mention uncertainty, generalization, transfer, robustness or spatial aspects.
- Only 13/30 explicitly say they compared against other methods; 2/30 state a dataset size in the abstract.
- Titles lean on hybrid ideas: physics-informed, hydrology-guided, transfer learning, uncertainty-guided, interpretability.
- Reading: the journal expects a water-science question plus evidence of robustness, not a leaderboard gain. My paper must therefore (a) frame a water-supply decision, (b) test spatial transfer, (c) explain why the method works.
- Targets I set for myself (not journal-verified): >=3 outcome definitions, >=6 baselines, >=5 seeds/repeats, spatial blocked holdout, ablation, cost analysis.
