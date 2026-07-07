# Phase 3c — Model Comparison: An Honest Tradeoff

Two models, two stacks, one question each. Logistic regression (R, `03-model-R.Rmd`) exists to **explain**;
XGBoost (Python, `04-model-python.ipynb`) exists to **predict**. Both were evaluated on the identical
held-out 20% test set (n=294, 47 leavers), defined once in `data/train-test-split.csv` (seed 42,
stratified). Neither model saw a test row before evaluation.

## The numbers

| Metric (test set) | Logistic regression (R) | XGBoost (Python) | Better |
|---|---|---|---|
| AUC | **0.865** | 0.825 | Logistic |
| Brier score (calibration; lower = better) | **0.087** | 0.184 | Logistic |
| Accuracy @ 0.5 | **0.901** | 0.810 | Logistic |
| Precision @ 0.5 | **0.846** | 0.437 | Logistic |
| Recall @ 0.5 | 0.468 | **0.660** | XGBoost |
| Top-decile capture | **48.9%** | 42.6% | Logistic |
| Top-decile lift | **4.9×** | 4.3× | Logistic |

## The result you don't see on Kaggle leaderboards

**The simple model won.** On 1,470 rows of clean, mostly-linear tabular data, gradient boosting has
nothing to exploit that logistic regression can't already capture, and it pays a variance penalty for
trying. This is a well-documented pattern for small tabular datasets, and the honest conclusion beats
a tuned-until-it-wins one.

Two caveats on reading the table:

- **The Brier/precision/recall gaps are partly a design choice, not pure model quality.** XGBoost was
  trained with `scale_pos_weight ≈ 5.2` to counter the 16% class imbalance. That deliberately inflates
  predicted probabilities toward the positive class: recall rises (0.66 vs 0.47), while precision and
  calibration fall. The R model was left unweighted. At the 0.5 threshold, the two models are answering
  differently-weighted questions — which is exactly why the threshold-free metrics (AUC, top-decile lift)
  are the fair comparison, and logistic regression wins those too.
- **The 0.5 threshold itself is arbitrary** for a 16%-base-rate problem. In production you'd pick the
  threshold from costs: if a retention conversation costs ~$500 and a departure ~$15,000, you should
  tolerate ~30 false alarms per true save, implying a much lower threshold (higher recall) than 0.5
  for either model. The watch-list framing (top decile) sidesteps the threshold question entirely,
  which is why the dashboard uses deciles.

## What each model is for

- **Policy conversations → logistic regression.** Odds ratios with confidence intervals
  (`outputs/logreg-odds-ratios.csv`) translate directly into statements an HR director can act on and
  defend ("controlling for everything else we measure, overtime multiplies the odds of leaving by ~3-4×").
  It is also the better-ranked and better-calibrated scorer here.
- **Per-employee "why" → XGBoost + SHAP.** SHAP attribution gives each flagged employee a top driver
  (`top_shap_driver` in `outputs/attrition-risk-scores.csv`) — the column that makes the dashboard's
  at-risk table actionable rather than just a ranked list of names. Its ranking quality (lift 4.3×)
  remains strong enough for this job, and the two models' driver stories agree (overtime, early tenure,
  low income/level, sales-rep role), which is the real validation.

**Headline numbers for the memo and README come from the logistic regression** (AUC 0.865, top decile
captures 49% of leavers ≈ 4.9× better than random outreach). The dashboard risk list keeps XGBoost scores
so every row carries a SHAP explanation; if it were rebuilt for a production deployment, the first
experiment would be logistic-regression scores with SHAP computed on a calibrated GBM as the explainer.

## Limitations that apply to both

- The dataset is synthetic (IBM sample) and small; findings demonstrate method, not industry truth.
- One 80/20 split, not cross-validation — adequate for a portfolio comparison, but CIs on the AUC gap
  would need repeated splits (the gap here, ~0.04, is within what split-to-split noise can produce at
  n_test=294).
- No temporal dimension: this is a snapshot, so "predicts attrition" really means "distinguishes leavers
  in the same period," and true deployment would need time-split validation.
