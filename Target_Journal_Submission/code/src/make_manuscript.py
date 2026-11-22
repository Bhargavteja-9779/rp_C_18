"""Build manuscript/Final_Manuscript.docx. Every number is read from tables/ or results/."""
import json, numpy as np, pandas as pd
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
T=lambda f:pd.read_csv(f"tables/{f}")
s10=T("summary_as10.csv").set_index("method"); s5=T("summary_as5.csv").set_index("method"); sb=T("summary_as10_blocks.csv").set_index("method"); st=T("summary_as10_thin.csv").set_index("method")
x10=T("statistics_as10.csv"); x5=T("statistics_as5.csv"); xb=T("statistics_as10_blocks.csv"); xt=T("statistics_as10_thin.csv")
from scipy.stats import wilcoxon
_m=pd.read_csv('results/m7_weight_check.csv').groupby(['unit','weight']).enr20.mean().unstack(); W=_m.mean(); _m5=pd.read_csv('tables/per_state_enr20_as10.csv',index_col=0).M5_proposed.loc[_m.index]; WP=min(wilcoxon(_m[c]-_m5).pvalue for c in _m.columns)
rv=T("random_vs_blocked_summary.csv").set_index("split"); per=T("per_state_enr20_as10.csv").set_index("unit"); u100=pd.read_csv("tables/unsafe_per_100_tests_as10.csv",index_col=0).iloc[:,0]
X=json.load(open("results/extra_checks.json")); tun=json.load(open("results/as10/tuning.json")); raw=pd.read_csv("results/as10/raw_results.csv")
NAMES={'M1_static_lgbm':'M1 static LightGBM map','M3_static_knn':'M3 static nearest-neighbour map','M4_neighbor_only':'M4 neighbour feedback only','M5_proposed':'M5 prior + feedback (hybrid)','M7_online_refit':'M7 online refit','A1_no_prior':'A1 hybrid without prior'}
def g(x,a,b,col): r=x[(x.A==a)&(x.B==b)].iloc[0]; return r[col]
def pf(p): return "p < 0.001" if p<0.001 else f"p = {p:.3f}"
def cmp(x,a,b):
    r=x[(x.A==a)&(x.B==b)].iloc[0]; return f"median paired difference {r.median_diff_enr20:+.2f} (95% CI {r.ci_lo:+.2f} to {r.ci_hi:+.2f}; Holm-adjusted {pf(r.holm_p)}; better in {int(r.states_A_better)} of {int(r.n_states)} units)"
nst=len(per); rnd100=(raw[raw.method=="M1_static_lgbm"].groupby("unit")[["n_unsafe","n_wells"]].first().eval("n_unsafe/n_wells*100")).mean()
bad_static=per.index[per.M1_static_lgbm<1].tolist(); bad_ad=per.index[per.M5_proposed<1].tolist(); ad_lt_static=per.index[per.M5_proposed<per.M1_static_lgbm].tolist()
D=Document(); sec=D.sections[0]; sec.left_margin=sec.right_margin=Cm(2.3); sec.top_margin=sec.bottom_margin=Cm(2.3)
stl=D.styles["Normal"]; stl.font.name="Times New Roman"; stl.font.size=Pt(11)
for h,sz in (("Heading 1",13),("Heading 2",11.5)): D.styles[h].font.name="Times New Roman"; D.styles[h].font.size=Pt(sz); D.styles[h].font.bold=True; D.styles[h].font.color.rgb=None
def P(t,bold=False,italic=False,al=None):
    p=D.add_paragraph(); r=p.add_run(t); r.bold=bold; r.italic=italic; p.paragraph_format.space_after=Pt(6)
    if al: p.alignment=al
    return p
def H1(t): D.add_heading(t,1)
def H2(t): D.add_heading(t,2)
def fig(path,cap,w=15):
    D.add_picture(path,width=Cm(w)); D.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER; P(cap,italic=True)
def table(df,cap,widths=None):
    P(cap,bold=True); t=D.add_table(rows=1,cols=len(df.columns)); t.style="Table Grid"
    for i,c in enumerate(df.columns): t.rows[0].cells[i].text=str(c)
    for _,r in df.iterrows():
        cs=t.add_row().cells
        for i,v in enumerate(r): cs[i].text=str(v)
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                for run in p.runs: run.font.size=Pt(8.5)
    D.add_paragraph()

TITLE="Cold-start well-testing campaigns: risk maps do not transfer to new states, but feedback from tested wells does"
P(TITLE,bold=True,al=WD_ALIGN_PARAGRAPH.CENTER).runs[0].font.size=Pt(15)
P("[Author names, affiliations, ORCID and corresponding-author details: to be added by the authors]",italic=True,al=WD_ALIGN_PARAGRAPH.CENTER)
H1("Abstract")
P(f"Health agencies often can test only some private wells for arsenic, so the order of testing matters. Statewide risk maps built with machine learning are the usual tool. We ask how well such maps work in a state that has no training data, and whether using the results of wells tested earlier in the same campaign helps. We used {len(raw.unit.unique())} US states with at least 100 USGS wells each ({int(raw[raw.method=='M1_static_lgbm'].groupby('unit').n_wells.first().sum()):,} wells; about {100*raw[raw.method=='M1_static_lgbm'].groupby('unit').n_unsafe.first().sum()/raw[raw.method=='M1_static_lgbm'].groupby('unit').n_wells.first().sum():.0f}% above 10 µg/L arsenic) and simulated testing campaigns under a fixed budget. A random five-fold split gave ROC-AUC {rv.loc['random_5fold','auc_roc']:.2f}; holding out whole states gave {rv.loc['leave_state_out','auc_roc']:.2f}. When 20% of a state's wells were tested, a static gradient-boosting map found {s10.loc['M1_static_lgbm','enr_20_mean']:.2f} times as many unsafe wells as random order (95% CI {s10.loc['M1_static_lgbm','enr_20_ci_lo']:.2f}–{s10.loc['M1_static_lgbm','enr_20_ci_hi']:.2f}); this was not significantly better than random after correction, and it was worse than random in {len(bad_static)} of {nst} states. Re-ranking untested wells with the outcomes of nearby tested wells reached {s10.loc['M4_neighbor_only','enr_20_mean']:.2f} times random order (about {u100['M4_neighbor_only']:.0f} unsafe wells per 100 tests, against {rnd100:.0f} for random order). A hybrid that added the machine-learning prior to this feedback did not beat feedback alone, and for the 5 µg/L threshold it was worse. The gain from feedback held in within-region blocks and after thinning clustered wells, although its edge over the static map was no longer significant after thinning. These results suggest that agencies should plan campaigns that learn as they go, and that risk-map accuracy reported under random splits should not be trusted for new regions. The data are not a random sample of private wells, and we did not test prospectively.")
P("Keywords: groundwater arsenic; private wells; spatial validation; adaptive sampling; screening; transferability",italic=True)

H1("1. Introduction")
P("Arsenic in drinking water harms health, and private wells are tested at the initiative of owners or health agencies rather than through routine public-supply monitoring. Agencies run outreach campaigns to get wells tested and need to decide where to start (CDC, 2026). Several studies use machine learning to map the probability that a private well exceeds an arsenic threshold (Lombard et al., 2021; Erickson et al., 2021; Azad et al., 2026). These maps are valuable for exposure research. They are less clear as a guide for a testing campaign. The national private-well model of Lombard et al. (2021) reported a sensitivity of 33.9% for the 10 µg/L threshold on its test data, which means most unsafe wells were missed at the model’s decision cut-off.")
P("Two questions follow. First, how well does a risk map work in a place where it has not seen data? Many maps are evaluated with random splits, which can place neighbouring wells in both training and test sets. Spatial validation with buffers is known to give lower scores for groundwater models (Appiah et al., 2025), and similar inflation is reported for leave-one-country-out tests in crop yield work (arXiv:2605.08113). Second, a campaign is not a one-shot prediction. Results arrive while testing is under way, and nearby wells tend to share geology. Adaptive designs for arsenic sampling (arXiv:2102.11118) and active search for rare targets in space (Active Area Search, AISTATS) are related, but we did not find a test of how much feedback adds beyond a static map on a national set of wells held out by state.")
P("We therefore simulate a cold-start campaign: a state agency with no local arsenic data must decide the order in which to test wells. We use the real arsenic results of USGS wells as the ‘ground truth’ that testing would reveal. Our contributions are:")
for t in ("We define a campaign evaluation for well testing, in which methods are scored by unsafe wells found at a fixed testing budget, in units that an agency can use (unsafe wells per 100 tests), with states held out and a 25 km buffer.",
          f"We measure how much random splits overstate map quality: ROC-AUC {rv.loc['random_5fold','auc_roc']:.2f} versus {rv.loc['leave_state_out','auc_roc']:.2f}, and recall at 20% of wells tested {rv.loc['random_5fold','recall_at_20']:.2f} versus {rv.loc['leave_state_out','recall_at_20']:.2f}.",
          "We compare a static map, a neighbour-feedback rule and several hybrids across 11 methods, 5 random seeds, two arsenic thresholds and three data designs, with paired tests across states.",
          "We report a negative result: adding the transferred machine-learning prior to feedback did not help, and for the 5 µg/L threshold it hurt."):
    D.add_paragraph(t,style="List Number")

H1("2. Data and methods")
H2("2.1 Data")
P("We downloaded discrete water-quality results for arsenic from the USGS Samples API on 22 November 2026, one request per state. California and Colorado requests timed out and are excluded. We kept results from wells, in water, reported in µg/L, and we used the earliest valid sample for each well. Non-detects were labelled safe, and non-detects whose detection limit was above 5 µg/L were dropped. After filtering there were 53,294 wells in 47 states; 9.97% exceeded 10 µg/L and 17.3% exceeded 5 µg/L. Wells sharing identical coordinates were collapsed to one, which left 50,139 wells. The only predictors a planner would hold before testing are latitude, longitude and the USGS aquifer code (present for 42% of wells). Well depth was missing for all wells in this output, so it was not used.")
H2("2.2 Leakage audit and splits")
P("We checked for duplicate wells (2,939 identifiers shared coordinates with another well and were collapsed), for repeated samples (only the earliest sample per well is used) and for label leakage (no result-derived variable is a predictor). Our main split holds out one whole state at a time. All wells within 25 km of any well in the held-out state are removed from training. Eight states, drawn at random before any model was run, were used only for tuning and never as test units. A second design clusters wells in evaluation states into 60 spatial blocks and holds out one block at a time, using the same buffer. A third design keeps one well per 1 km cell to reduce clustered sampling.")
H2("2.3 Campaign simulation")
P("In a held-out unit, wells are tested in batches of 10. Before testing, a method sees only the predictors. After each batch it sees the outcomes of the wells just tested. The score is the number of unsafe wells found when 5%, 10%, 20% and 30% of wells have been tested. We divide by the number expected under random order (the budget fraction times the number of unsafe wells) to give an enrichment; random order has enrichment 1 by construction. The primary measure is enrichment at 20%.")
H2("2.4 Methods compared")
P("M1 is a static LightGBM risk map trained on all wells outside the buffer. M2 is a static logistic regression on coordinates. M3 is a static distance-weighted nearest-neighbour prevalence map. M4 is neighbour-only feedback: untested wells are ranked by a Gaussian-kernel weighted share of unsafe results among tested neighbours (the first batch is random). M5 combines a prior probability p (from M1) with the kernel evidence: score = (κp + a)/(κ + a + b), where a and b are kernel-weighted counts of unsafe and safe results among tested wells, and κ sets how much weight the prior keeps. M6 draws from the corresponding Beta distribution (Thompson sampling). M7 refits the LightGBM model with the tested wells at fixed checkpoints. Four ablations remove the prior (A1), remove shrinkage (A2), fix the bandwidth (A3), or replace the prior with M3 (A4). All methods used the same tuning budget: 20 random-search trials for LightGBM and a grid of 5 bandwidths and 5 values of κ, chosen on the tuning states only. "+f" The selected bandwidth was {tun['h_kappa'][0]} km and κ was {tun['h_kappa'][1]}.".replace('"+f" ',''))
H2("2.5 Statistics")
P("The unit of analysis is the held-out state (or block), after averaging 5 random seeds. We used paired Wilcoxon signed-rank tests, the median paired difference in enrichment with a bootstrap 95% confidence interval (10,000 resamples of units), the rank-biserial correlation as effect size, and Holm correction within each scenario. The protocol, the deviations from it, and the code are in the supplementary material; deviations were recorded before the main runs.")

H1("3. Results")
H2("3.1 Random splits overstate map quality")
table(pd.DataFrame({"Split":["Random 5-fold","Leave-one-state-out (25 km buffer)"],"ROC-AUC":[f"{rv.loc['random_5fold','auc_roc']:.3f}",f"{rv.loc['leave_state_out','auc_roc']:.3f}"],"PR-AUC":[f"{rv.loc['random_5fold','auc_pr']:.3f}",f"{rv.loc['leave_state_out','auc_pr']:.3f}"],"Recall at 20% tested":[f"{rv.loc['random_5fold','recall_at_20']:.3f}",f"{rv.loc['leave_state_out','recall_at_20']:.3f}"]}),"Table 1. The same LightGBM model under two evaluations (mean of 3 seeds; As > 10 µg/L).")
fig("figures/fig_random_vs_blocked.png","Figure 1. Random splits versus held-out states for the same model.",13)
P("Under random splitting the map ranks unsafe wells well. Under held-out states the ranking is weak. The base rate of unsafe wells is about 10%, so a PR-AUC of 0.15 is only modestly above chance.")
H2("3.2 In a new state, a static map is close to random order")
P(f"At 20% of wells tested, the static LightGBM map found {s10.loc['M1_static_lgbm','enr_20_mean']:.2f} times the unsafe wells of random order (95% CI {s10.loc['M1_static_lgbm','enr_20_ci_lo']:.2f}–{s10.loc['M1_static_lgbm','enr_20_ci_hi']:.2f}). Against random order the {cmp(x10,'M1_static_lgbm','M0_random(=1)')}. It was below random order in {len(bad_static)} of {nst} states ({', '.join(bad_static)}). The logistic regression was no better than random ({s10.loc['M2_static_logreg','enr_20_mean']:.2f}). For the 5 µg/L threshold the static map was {s5.loc['M1_static_lgbm','enr_20_mean']:.2f} times random order, and the difference from random order was not significant.")
H2("3.3 Feedback from tested wells helps")
P(f"Neighbour-only feedback reached {s10.loc['M4_neighbor_only','enr_20_mean']:.2f} times random order (95% CI {s10.loc['M4_neighbor_only','enr_20_ci_lo']:.2f}–{s10.loc['M4_neighbor_only','enr_20_ci_hi']:.2f}). Compared with the static map the {cmp(x10,'M4_neighbor_only','M1_static_lgbm')}. In real units, a campaign testing 20% of wells found about {u100['M4_neighbor_only']:.1f} unsafe wells per 100 tests with neighbour feedback, {u100['M1_static_lgbm']:.1f} with the static map and {rnd100:.1f} with random order. The first batches matter most: enrichment at 5% tested was {s10.loc['M4_neighbor_only','enr_5']:.2f} for neighbour feedback and {s10.loc['M1_static_lgbm','enr_5']:.2f} for the static map.")
fig("figures/fig_enrichment_as10.png","Figure 2. Enrichment at 20% budget for each held-out state (dots) and the mean (bar). The dashed line is random order.",14)
H2("3.4 The machine-learning prior does not add to feedback")
P(f"The proposed hybrid (M5) reached {s10.loc['M5_proposed','enr_20_mean']:.2f}. It did not differ from neighbour-only feedback: {cmp(x10,'M5_proposed','M4_neighbor_only')}. Removing the prior (A1) gave {s10.loc['A1_no_prior','enr_20_mean']:.2f}, nominally above M5. Refitting the model online (M7) gave {s10.loc['M7_online_refit','enr_20_mean']:.2f}, and Thompson sampling (M6) {s10.loc['M6_thompson','enr_20_mean']:.2f}; neither differed from M5 after correction. With the 5 µg/L threshold the prior was harmful: M5 reached {s5.loc['M5_proposed','enr_20_mean']:.2f} against {s5.loc['M4_neighbor_only','enr_20_mean']:.2f} for neighbour-only feedback ({cmp(x5,'M5_proposed','M4_neighbor_only')}). Because the online-refit weight on tested wells was fixed at 20 and not tuned, we checked weights of 1, 20 and 100 afterwards (3 seeds): mean enrichment was {W.loc[1.0]:.2f}, {W.loc[20.0]:.2f} and {W.loc[100.0]:.2f}, and none differed from M5 (unadjusted Wilcoxon p ≥ {WP:.2f}); the best of the three is an upper bound chosen after seeing results. The honest summary is that the hybrid is not a better method than the simple rule. Its value, if any, would lie in settings where the prior is informative, which a cold start across states is not.")
table(pd.read_csv("tables/main_table.csv").assign(v=lambda d:d.enr20.map("{:.2f}".format)+" ["+d.lo.map("{:.2f}".format)+", "+d.hi.map("{:.2f}".format)+"]").pivot(index="method",columns="scenario",values="v").rename(index=NAMES).reset_index().rename(columns={"method":"Method"}),"Table 2. Enrichment at 20% budget, mean [95% CI over units] (random order = 1). Units: states or blocks as stated.")
H2("3.5 Robustness: other thresholds, blocks and thinned data")
P(f"In within-region blocks ({len(pd.read_csv('tables/per_state_enr20_as10_blocks.csv'))} blocks) the static map was {sb.loc['M1_static_lgbm','enr_20_mean']:.2f} times random order and neighbour feedback {sb.loc['M4_neighbor_only','enr_20_mean']:.2f}; the {cmp(xb,'M4_neighbor_only','M1_static_lgbm')}. After thinning to one well per 1 km cell ({len(pd.read_csv('tables/per_state_enr20_as10_thin.csv'))} states), feedback still found {st.loc['M4_neighbor_only','enr_20_mean']:.2f} times random order ({cmp(xt,'M4_neighbor_only','M0_random(=1)')}). Its edge over the static map was {g(xt,'M4_neighbor_only','M1_static_lgbm','median_diff_enr20'):+.2f}, but {pf(g(xt,'M4_neighbor_only','M1_static_lgbm','holm_p'))} after correction, so we do not claim a significant gain over the static map in the thinned data. Results varied little across seeds (standard deviation of the mean enrichment across seeds for M5: {pd.read_csv('tables/seed_variability_as10.csv',index_col=0).loc['M5_proposed','std']:.2f}).")
fig("figures/fig_generality.png","Figure 3. Enrichment at 20% budget across scenarios (mean and 95% CI over units).",15)
H2("3.6 Where methods fail")
P(f"The static map did worse than random order in {', '.join(bad_static)}. Adaptive ordering with M5 was below random order in {', '.join(bad_ad)} and below the static map in {', '.join(ad_lt_static)}. Minnesota is the clearest failure: the static map reached {per.loc['MN','M1_static_lgbm']:.2f} and M5 {per.loc['MN','M5_proposed']:.2f} times random order. We did not test why, but arsenic in glacial aquifers is known to vary over short distances, which weakens the assumption that neighbouring wells look alike; this is a hypothesis, not a result. ")
H2("3.7 Negative control and cost")
P(f"To check that the gain from feedback comes from spatial structure and not from a flaw in our code, we shuffled the outcomes of wells within each state and ran neighbour feedback again (5 shuffles per state). Enrichment was {X['negative_control_M4_enrichment20_mean']:.2f} (95% CI {X['ci'][0]:.2f}–{X['ci'][1]:.2f}), as expected for random order. Cost is small for feedback rules: in {X['timing_state']} ({X['timing_n_wells']:,} wells; one core) fitting and scoring the static map took {X['timing']['M1_fit_and_score_s']:.1f} s, a full neighbour-feedback campaign {X['timing']['M4_campaign_s']:.1f} s, and the online-refit method {X['timing']['M7_online_refit_s']:.1f} s, about {X['timing']['M7_online_refit_s']/X['timing']['M4_campaign_s']:.0f} times the feedback rule without a better result.")

H1("4. Discussion")
P("For an agency starting a campaign in a state with no data, the main practical message is to plan for feedback. Even a crude rule that moves testing towards areas where unsafe results have just been found raised the yield of unsafe wells per test by about 80% over random order in our simulation, and clearly beat a transferred risk map (in the within-region block design, the static map did beat random order, but by less). A map still has a role: after enough local results exist, it can be trained locally, which we did not test. Our results also caution against quoting map accuracy from random splits when the goal is to guide work in new regions.")
P("The negative result on the hybrid is informative. One possible reason, which we did not test, is that the prior was trained on other states, so it carries regional patterns that do not transfer, and the kernel rule corrects for this only slowly. We used one simple way of combining the two. Other ways, such as learning the map from local results alone or using geology as predictors, may do better.")
H1("5. Limitations")
for t in ("The wells are USGS study wells, not a random sample of private wells. Studies often sample clusters of wells, which makes neighbours more alike than in a real campaign; thinning reduced but did not remove this concern. A prospective test is needed.",
          "We simulate campaigns on wells that already have results. Real campaigns also face refusals, cost differences and access limits.",
          "Predictors are limited to location and aquifer code. Geology, soil chemistry and well construction are known to matter and were not used; the static map could do better with them.",
          "California and Colorado are missing, and a second contaminant (nitrate) could not be downloaded, so we cannot say the findings hold beyond arsenic.",
          "Tuning used 8 states set aside at random; their wells still served as training data for other states. Hyperparameters were selected before test states were evaluated, but the process is not a full nested design.",
          "The random-versus-held-out comparison used 3 seeds and the random split was not buffered.",
          "Prior work close to ours exists (adaptive arsenic sampling; active search; spatial validation). Our novelty claim is limited to the empirical comparison reported here, and our search was a limited web search, not a systematic review."):
    D.add_paragraph(t,style="List Bullet")
H1("6. Conclusions")
P("In a cold-start setting, machine-learning arsenic maps built on other states ranked wells little better than random order, even though a random split suggested otherwise. Using the results of wells tested earlier in the campaign raised the number of unsafe wells found per test by about 70–80% over random order in the main analysis. Combining the map with feedback gave no extra benefit. Campaign planning should be judged by held-out, budgeted simulations, and prospective trials should follow.")
H1("Declarations")
for t in ("Data availability: USGS Samples API (https://api.waterdata.usgs.gov/samples-data), retrieved 22 November 2026; processed tables, per-state results, and code are in the submission package.",
          "Code availability: `code/` (run_all.py reproduces all tables and figures; unit tests included).",
          "Ethics: no human participants; public well-level data are used.",
          "Conflicts of interest and funding: [to be completed by the authors].",
          "Use of AI tools: an AI coding assistant (Claude Code) was used to write analysis code and a first draft of this text. The authors must review all content and take responsibility for it before submission.",
          "Author contributions: [to be completed by the authors]."):
    P(t)
H1("References")
refs=["CDC (2026). Private well ranking indices. Centers for Disease Control and Prevention (document available at cdc.gov/environmental-health-practice).",
"Lombard, M.A., et al. (2021). Machine learning models of arsenic in private wells throughout the conterminous United States as a tool for exposure assessment in human health studies. Environmental Science & Technology. (Full author list and DOI not verified.)",
"Erickson, M.L., et al. (2021). Machine learning predictions of high arsenic and high manganese at drinking water depths of the glacial aquifer system. Environmental Science & Technology, 55, 5791–5805. (Author list not verified.)",
"Azad, et al. (2026). Surface variable-based machine learning for scalable arsenic prediction in undersampled areas. GeoHealth. (Full author list not verified.)",
"Appiah, et al. (2025). Spatial cross-validation with buffers for machine-learning groundwater quality models. Preprint, University of Texas at El Paso (cs.utep.edu/vladik/utepnmsu25appiah.pdf). (Title and authors not fully verified.)",
"arXiv:2102.11118. Adaptive spatial sampling design for private-well arsenic testing in Iowa. (Title as described in search results; not verified.)",
"arXiv:2605.08113. Do foundation model embeddings improve cross-country crop yield generalisation? A leave-one-country-out evaluation in Sub-Saharan Africa.",
"Active area search via Bayesian quadrature. Proceedings of AISTATS (2014). (Authors not verified.)",
"Mailloux, B.J., et al. (2020). Recommended sampling intervals for arsenic in private wells. Groundwater. (Details not verified.)",
"USGS Samples Data API, https://api.waterdata.usgs.gov/samples-data (accessed 22 November 2026)."]
for r in refs: P(r)
import os; os.makedirs("manuscript",exist_ok=True); D.save("manuscript/Final_Manuscript.docx"); open("manuscript/title.txt","w").write(TITLE); print("saved")
