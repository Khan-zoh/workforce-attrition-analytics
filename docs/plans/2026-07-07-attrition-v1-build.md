# Workforce Attrition Analytics V1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the full analysis the README promises — R EDA, hypothesis tests, R logistic regression, Python XGBoost+SHAP, model comparison, Tableau-ready outputs, executive memo — so the repo passes the recruiter 60-second test.

**Architecture:** Analysis pipeline over a single flat CSV (IBM HR, n=1470). R (.Rmd, knitted to HTML in `outputs/reports/`) handles EDA, the hypothesis-test battery, and interpretable logistic regression. Python (executed .ipynb) handles XGBoost + SHAP and a DuckDB SQL-EDA section. A shared train/test split file (`data/train-test-split.csv`, keyed on `EmployeeNumber`, seed 42, stratified 80/20) makes the R-vs-Python model comparison honest. Everything downstream (comparison doc, risk-score CSV, Tableau guide, memo) reads from committed outputs.

**Tech Stack:** R 4.4.2 (tidyverse, effsize, patchwork, corrplot, broom, rmarkdown; pandoc from RStudio bundle), Python 3.11 venv (pandas, scikit-learn, xgboost, shap, duckdb, matplotlib, jupyter/nbclient), pytest for output-contract tests, Tableau Public (manual step, guided).

**Environment facts (verified 2026-07-07):**
- `Rscript` = `C:\Program Files\R\R-4.4.2\bin\Rscript.exe` (not on PATH — always full path)
- Pandoc: bundled under `C:\Program Files\RStudio\resources\app\bin\quarto\bin\tools` — set `RSTUDIO_PANDOC` before `rmarkdown::render`
- Tableau: NOT installed. Deliverable = extracts + `docs/tableau-build-guide.md`
- Repo: clean, on `main`, remote `Khan-zoh/workforce-attrition-analytics`

---

### Task 1: Scaffold — data, deps, gitignore

**Files:**
- Create: `data/README.md`, `data/hr-attrition.csv` (downloaded, ~220KB)
- Create: `.gitignore`, `requirements.txt`, `tools/render.R`
- Create: `outputs/`, `outputs/reports/`, `outputs/figures/` dirs

- [ ] **Step 1:** Download the IBM HR dataset from a public GitHub mirror of `WA_Fn-UseC_-HR-Employee-Attrition.csv` to `data/hr-attrition.csv`. Verify: 1470 rows × 35 cols, `Attrition` in {Yes,No}, `EmployeeNumber` unique. If mirror fails, try an alternate mirror; record source URL in `data/README.md` (note: original is IBM sample data via Kaggle `pavansubhasht/ibm-hr-analytics-attrition-dataset`).
- [ ] **Step 2:** Write `.gitignore`:

```
.venv/
__pycache__/
.pytest_cache/
.Rproj.user/
.RData
.Rhistory
*.pyc
.ipynb_checkpoints/
```

Commit the CSV itself — it's small, public sample data, and reproducibility beats purity here (README still documents the source).

- [ ] **Step 3:** Write `requirements.txt` (pinned): pandas, scikit-learn, xgboost, shap, duckdb, matplotlib, jupyter, nbclient, nbconvert, pytest, tabulate. Create `.venv`, install.
- [ ] **Step 4:** Install R packages (user library, binary): tidyverse, patchwork, corrplot, effsize, broom, rmarkdown, knitr, janitor, scales. Verify with a `library()` smoke load.
- [ ] **Step 5:** Write `tools/render.R` — helper that sets `RSTUDIO_PANDOC` and renders an Rmd to `outputs/reports/`:

```r
args <- commandArgs(trailingOnly = TRUE)
Sys.setenv(RSTUDIO_PANDOC = "C:/Program Files/RStudio/resources/app/bin/quarto/bin/tools")
rmarkdown::render(args[[1]], output_dir = "outputs/reports", envir = new.env())
```

Run: `& "C:\Program Files\R\R-4.4.2\bin\Rscript.exe" -e "cat('ok')"` → `ok`
- [ ] **Step 6:** Commit: `chore: scaffold data, deps, render tooling`

### Task 2: Phase 1 — EDA in R (`01-eda.Rmd`)

**Files:** Create `01-eda.Rmd`; outputs `outputs/reports/01-eda.html`, figures saved to `outputs/figures/`

- [ ] **Step 1:** Write `01-eda.Rmd` with sections: data load + integrity checks (row count, no NAs, drop the 4 constant/ID-ish cols `EmployeeCount, StandardHours, Over18, EmployeeNumber` from *analysis* but keep EmployeeNumber as key); overall attrition rate; attrition by Department, JobRole, OverTime, BusinessTravel, MaritalStatus (bar charts, ordered); numeric drivers (Age, MonthlyIncome, TotalWorkingYears, YearsAtCompany, DistanceFromHome) as density/box plots by attrition; tenure/income banding table; correlation plot of numerics; a closing "what we take into Phase 2" list of candidate drivers. Every chart titled in plain business English.
- [ ] **Step 2:** Render via `tools/render.R`. Expected: `outputs/reports/01-eda.html` exists, no errors.
- [ ] **Step 3:** Commit: `feat(phase1): exploratory analysis in R`

### Task 3: Phase 2 — Hypothesis tests (`02-hypothesis-tests.Rmd`)

**Files:** Create `02-hypothesis-tests.Rmd`; outputs `outputs/reports/02-hypothesis-tests.html`, `outputs/driver-tests.csv`

- [ ] **Step 1:** Write the Rmd: chi-squared tests (with Cramér's V) for every categorical driver vs Attrition; Welch t-tests + Cohen's d for every numeric driver; assemble one tidy results table (driver, test, statistic, raw p, Bonferroni-adjusted p, effect size, verdict). Explicit "significant but trivial" flagging: adjusted p < .05 but |d| < 0.2 (or V < 0.1) labeled as such in the table and prose. Write the table to `outputs/driver-tests.csv`.
- [ ] **Step 2:** Render. Verify the CSV has one row per tested driver and the report calls out the top drivers by effect size (expect OverTime, JobRole, MaritalStatus, MonthlyIncome, Age, TotalWorkingYears to lead).
- [ ] **Step 3:** Commit: `feat(phase2): hypothesis-test battery with effect sizes`

### Task 4: Shared train/test split

**Files:** Create `data/train-test-split.csv` (via a chunk in `03-model-R.Rmd`, but written before both models run)

- [ ] **Step 1:** In R (inside 03 Rmd, first chunk, seed 42): stratified 80/20 split on Attrition; write `EmployeeNumber,set` (`train`/`test`) to `data/train-test-split.csv`. Contract: 1470 rows, ~294 test rows, test attrition rate within 1pt of overall. Python MUST read this file, never re-split.
- [ ] **Step 2:** Commit together with Task 5 (same file).

### Task 5: Phase 3a — Logistic regression in R (`03-model-R.Rmd`)

**Files:** Create `03-model-R.Rmd`; outputs `outputs/reports/03-model-R.html`, `outputs/logreg-metrics.csv`, `outputs/logreg-odds-ratios.csv`

- [ ] **Step 1:** Write the Rmd: feature prep (drop constants; treat Education/JobLevel etc. ordinals as numeric; OverTime/BusinessTravel etc. as factors); fit `glm(Attrition ~ ., family=binomial)` on train; odds ratios + 95% CIs via broom, sorted, plain-English interpretation of the top 8; test-set evaluation — AUC, confusion matrix @0.5, Brier score, top-decile lift (define: share of actual leavers captured in the top 10% by predicted risk ÷ 10%). Write metrics to `outputs/logreg-metrics.csv` and odds ratios to `outputs/logreg-odds-ratios.csv`. Check separation warnings; if any coefficient explodes, note and handle (drop or collapse level) in the doc.
- [ ] **Step 2:** Render; sanity: test AUC expected ~0.80–0.87 for this dataset.
- [ ] **Step 3:** Commit: `feat(phase3a): interpretable logistic regression in R`

### Task 6: Phase 3b — XGBoost + SHAP + SQL EDA in Python (`04-model-python.ipynb`)

**Files:** Create `04-model-python.ipynb` (committed executed, with outputs); outputs `outputs/xgb-metrics.csv`, `outputs/attrition-risk-scores.csv`, `outputs/figures/shap-*.png`

- [ ] **Step 1:** Build the notebook (write JSON or py:percent → jupytext) with sections: (1) load CSV + split file, assert same test set as R; (2) **SQL EDA via duckdb** — 3–4 analytical queries (attrition by dept×overtime, income quartile rates, tenure buckets) shown as SQL strings, results as tables; (3) XGBoost binary:logistic, `scale_pos_weight` for the 16% class imbalance, early stopping on a validation fold from train; (4) test metrics: AUC, confusion @0.5, Brier, top-decile lift → `outputs/xgb-metrics.csv`; (5) SHAP TreeExplainer: beeswarm summary + top-3 dependence plots saved to `outputs/figures/`; (6) score ALL 1470 employees → `outputs/attrition-risk-scores.csv` with columns: EmployeeNumber, set, actual Attrition, risk_score, risk_decile, Department, JobRole, OverTime, MonthlyIncome, Age, YearsAtCompany, JobSatisfaction, top_shap_driver (per-row argmax |SHAP|).
- [ ] **Step 2:** Execute headlessly (`jupyter nbconvert --to notebook --execute --inplace`). Expected: runs clean, AUC ≥ logistic regression's or within noise.
- [ ] **Step 3:** Commit: `feat(phase3b): XGBoost + SHAP + SQL EDA; per-employee risk scores`

### Task 7: Output-contract tests

**Files:** Create `tests/test_outputs.py`, `pytest.ini`

- [ ] **Step 1:** Write pytest checks: risk-scores CSV has 1470 unique EmployeeNumbers; risk_score ∈ [0,1]; deciles 1–10 roughly equal-sized; split file matches contract (counts, stratification within tolerance); both metrics CSVs exist with AUC ∈ (0.5, 1.0]; driver-tests CSV has adjusted-p column ≥ raw p.
- [ ] **Step 2:** Run `pytest -q` → all pass.
- [ ] **Step 3:** Commit: `test: output contracts for scores, split, metrics`

### Task 8: Phase 3c — Model comparison (`05-model-comparison.md`)

**Files:** Create `05-model-comparison.md` (reads both metrics CSVs — numbers pasted in, doc explains)

- [ ] **Step 1:** Write the honest tradeoff doc: side-by-side metric table (AUC, Brier, confusion, top-decile lift on the SAME test set); what logistic gives (odds ratios an HR director can act on) vs XGBoost (lift + per-employee SHAP attribution); recommendation: logistic for policy conversations, XGBoost scores for the watch-list dashboard; failure modes (dataset synthetic, n small, 0.5 threshold arbitrary — show cost-based threshold thinking).
- [ ] **Step 2:** Commit: `docs(phase3c): model comparison writeup`

### Task 9: Phase 4 — Tableau extracts + build guide

**Files:** Create `docs/tableau-build-guide.md`, `outputs/drivers-summary.csv` (tidy driver table for the dashboard's driver explorer)

- [ ] **Step 1:** Write `outputs/drivers-summary.csv` from Phase 2 results + group attrition rates (driver, level, n, attrition_rate, effect_size) via a small script or notebook cell.
- [ ] **Step 2:** Write the click-by-click guide: install Tableau Public → connect both CSVs → Sheet 1 KPI overview (attrition rate BAN + by-department bars + $ cost parameter, default 15000) → Sheet 2 driver explorer (drivers-summary heat/bar, effect-size sorted) → Sheet 3 at-risk table (risk-scores filtered to top decile of current employees, colored by risk, top_shap_driver as the "why" column) → dashboard assembly → publish to Tableau Public → paste link + screenshot into README. Include exact field/shelf placements.
- [ ] **Step 3:** Commit: `docs(phase4): tableau extracts and build guide`

### Task 10: Phase 5 — Executive memo

**Files:** Create `memo.md`; render `memo.pdf` if a LaTeX/pandoc path works, else `memo.html` (pandoc bundled with RStudio)

- [ ] **Step 1:** Write the 2-page memo for an HR director: headline (attrition rate, annual cost @ $15K/leaver, top-decile capture), top 3 drivers with effect sizes translated to plain English, 3 recommended actions tied to drivers (e.g., overtime policy review, early-tenure onboarding, targeted comp review), what the risk list is and how to use it responsibly (aggregate signal, not individual punishment), caveats (synthetic data, method-demonstration).
- [ ] **Step 2:** Render to PDF/HTML with bundled pandoc. Commit: `docs(phase5): executive memo`

### Task 11: Phase 6 — README truth-up + resume bullets

**Files:** Modify `README.md`; create `outputs/resume-bullets.md`, `outputs/interview-script.md`

- [ ] **Step 1:** Rewrite README: status → complete-except-Tableau-publish; add Headline Finding (real numbers from outputs); repo-structure section matched to actual files; reproduce instructions matched to actual commands (venv, Rscript render, nbconvert, pytest); dashboard section holds the guide link until the public URL exists.
- [ ] **Step 2:** Write resume bullets (2–3, quantified, only demonstrated skills — per standing rule, no eager-to-learn framing) and a short interview script (60-sec walkthrough + 3 anticipated questions incl. the A/B/threshold question).
- [ ] **Step 3:** `pytest -q` one final time; commit: `docs(phase6): README, resume bullets, interview script`; push to origin.

### Task 12: Tableau dashboard (user-in-the-loop)

- [ ] Walk the user through `docs/tableau-build-guide.md`, or co-build via browser (Tableau Public web authoring) if they want; then README gets the live link + `outputs/tableau-preview.png`, final commit+push.

---

**Self-review notes:** All README-promised files covered (01→05, memo, outputs incl. risk scores, resume bullets, interview script). No placeholders — analysis prose is authored at execution time by design; contracts (file names, columns, seeds, split) are pinned here. Type/name consistency: `data/hr-attrition.csv`, `data/train-test-split.csv`, `outputs/attrition-risk-scores.csv` used identically across Tasks 4–9.
