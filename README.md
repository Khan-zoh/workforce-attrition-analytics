# Workforce Attrition Analytics

Diagnostic, predictive, and prescriptive analysis of employee attrition, packaged the way a consulting team would hand it to an HR director.

**Status:** Analysis complete. Tableau Public dashboard: build guide ready, publish pending ([docs/tableau-build-guide.md](docs/tableau-build-guide.md)).

## Headline Finding

**16.1% of the workforce left (237 of 1,470) — ~$3.6M/year at a conservative $15K per leaver — and the loss concentrates in four driver themes: overtime work (30.5% vs 10.4% attrition, ~6× adjusted odds), first-year tenure (34.9%), the bottom pay quartile (29.3% vs 10.3%), and the Sales Representative role (39.8%).** A logistic-regression risk model puts 49% of actual leavers inside a watch list covering just 10% of employees (held-out AUC 0.865, top-decile lift 4.9×) — and that same model's scores power the dashboard watch list, so the headline and the product are one model. Full story: [memo.md](memo.md).

Also notable: the "fancier" model lost. XGBoost underperformed logistic regression on the shared held-out split (AUC 0.825 vs 0.865) — the honest small-tabular-data result, written up in [05-model-comparison.md](05-model-comparison.md). XGBoost still earns its keep via SHAP: every employee on the watch list carries a named risk pattern from the clearly-labeled companion model.

## Problem

Voluntary attrition is one of the most expensive line items a mid-size company carries, and most HR teams can name the symptoms without naming the drivers. This project takes a public HR dataset (IBM, n=1,470) and answers three questions an HR director actually asks:

1. Who is leaving, and which groups are leaving fastest?
2. What predicts whether a given employee will leave?
3. Where should the next dollar of retention spend go?

## Live Dashboard

*Publish pending — the two dashboard extracts (`outputs/attrition-risk-scores.csv`, `outputs/drivers-summary.csv`) and a click-by-click build guide ([docs/tableau-build-guide.md](docs/tableau-build-guide.md)) are ready; the Tableau Public link and preview screenshot land here after publishing.*

## Repo Structure

```
workforce-attrition-analytics/
├── data/
│   ├── hr-attrition.csv           # IBM HR dataset (see data/README.md for provenance)
│   └── train-test-split.csv       # shared 80/20 split (seed 42) used by BOTH models
├── 01-eda.Rmd                     # Phase 1: exploratory analysis (R)
├── 02-hypothesis-tests.Rmd        # Phase 2: chi-sq, Welch t, Bonferroni, effect sizes (R)
├── 03-model-R.Rmd                 # Phase 3a: logistic regression, odds ratios (R)
├── 04-model-python.ipynb          # Phase 3b: XGBoost + SHAP + DuckDB SQL EDA (Python)
├── 05-model-comparison.md         # Phase 3c: honest model tradeoff writeup
├── memo.md / memo.html            # Phase 5: 2-page executive memo
├── outputs/
│   ├── reports/                   # knitted HTML for all three .Rmd phases
│   ├── figures/                   # key charts incl. SHAP plots
│   ├── attrition-risk-scores.csv  # per-employee: logistic risk score + decile, companion-GBM xgb_score + SHAP risk pattern
│   ├── logreg-scores.csv          # full-population logistic scores (source of risk_score above)
│   ├── drivers-summary.csv        # per-driver-level rates + effect sizes (Tableau feed)
│   ├── driver-tests.csv           # full 30-test battery results
│   ├── logreg-*.csv / xgb-metrics.csv
│   ├── resume-bullets.md
│   └── interview-script.md
├── docs/tableau-build-guide.md    # click-by-click dashboard instructions
├── tests/test_outputs.py          # output contracts (pytest)
└── tools/                         # render.R, build_notebook.py, make_tableau_extracts.py
```

## Methodology

- **EDA and hypothesis testing** in R (tidyverse, ggplot2, patchwork, corrplot, effsize). Chi-squared tests for categorical drivers, Welch's t-tests for numeric drivers, Bonferroni correction across the full 30-test battery, Cramér's V / Cohen's d for effect sizes — with "significant but trivial" results labeled as such rather than reported as drivers.
- **Predictive modeling in two stacks** for an honest comparison on one shared held-out test set (stratified 80/20, seed 42, committed to the repo). Logistic regression in R for interpretable odds ratios with CIs — including a collinearity stability check (refit without the nested/redundant fields) covering every coefficient the memo interprets. XGBoost in Python (class-weighted, early stopping) with SHAP for per-employee attribution.
- **SQL** analytical queries (DuckDB) reproduce the headline EDA cuts inside the Python notebook.
- **Evaluation:** AUC, Brier score, confusion matrix at 0.5, and top-decile capture/lift — the operational metric for a watch-list use case.
- **Communication:** 2-page executive memo (memo.md) and a Tableau dashboard (KPI overview, driver explorer filtered to statistically meaningful drivers, at-risk table with SHAP "why" column).

## How to Reproduce

```bash
# Python (3.11): venv + deps
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt        # Windows paths; adjust on mac/linux

# R (4.4): packages install to the user library
Rscript -e "install.packages(c('tidyverse','patchwork','corrplot','effsize','broom','rmarkdown','knitr','janitor','scales','pROC'), repos='https://cloud.r-project.org')"

# Phases in order (R renders write to outputs/reports/)
Rscript tools/render.R 01-eda.Rmd
Rscript tools/render.R 02-hypothesis-tests.Rmd
Rscript tools/render.R 03-model-R.Rmd               # also writes data/train-test-split.csv
.venv/Scripts/python tools/build_notebook.py         # regenerates the .ipynb source
.venv/Scripts/jupyter nbconvert --to notebook --execute --inplace 04-model-python.ipynb
.venv/Scripts/python tools/make_tableau_extracts.py

# Verify the output contracts
.venv/Scripts/python -m pytest
```

Note: `tools/render.R` points `RSTUDIO_PANDOC` at the RStudio-bundled pandoc; if you have pandoc on PATH, delete that line.

## Limitations

- The IBM HR dataset is synthetic and widely studied. Findings illustrate method, not industry truth.
- n=1,470 is small. Several relationships reach statistical significance with trivial effect sizes; the analysis flags these explicitly rather than over-claiming (see the verdict column in `outputs/driver-tests.csv`).
- Replacement cost is modeled as a flat $15K per leaver, exposed as a parameter in the dashboard. Real costs vary widely by role.
- Snapshot data, single split: a production model would need time-split validation and repeated splits for CIs on the model comparison.

## Author

Zohair Khan. Industrial Engineering, Texas A&M, May 2027.
