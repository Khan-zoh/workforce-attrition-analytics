# Resume bullets

Pick 2–3. Every number is real output of this repo (see README / outputs/*.csv); all skills listed are demonstrated in the code, per the only-demonstrated-skills rule.

**Project line:** Workforce Attrition Analytics — R, Python, SQL, Tableau · github.com/Khan-zoh/workforce-attrition-analytics

- Analyzed attrition for a 1,470-employee HR dataset in R and SQL (DuckDB), isolating 4 actionable drivers from 30 candidates via a Bonferroni-corrected battery of chi-squared and Welch tests with effect sizes — e.g., overtime work carried a ~6× adjusted odds of exit (30.5% vs 10.4% attrition).
- Built and honestly compared two attrition models on a shared held-out test set — interpretable logistic regression in R (AUC 0.865) vs class-weighted XGBoost + SHAP in Python (AUC 0.825) — and documented why the simpler model won and where each belongs in production.
- Delivered results as decision tools, not notebooks: a per-employee risk watch list capturing 49% of actual leavers in the top decile (4.9× lift), a SHAP-attributed "top risk driver" per employee, a Tableau dashboard, and a 2-page executive memo pricing attrition at ~$3.6M/yr with 4 targeted interventions.

**Shorter variants (one-line, for a crowded resume):**

- Quantified attrition drivers for 1,470 employees (R, SQL, chi-sq/t-test battery w/ effect sizes) and built a risk model whose top decile captures 49% of leavers (AUC 0.87); shipped Tableau dashboard + executive memo.
- Compared logistic regression (R) vs XGBoost+SHAP (Python) for attrition prediction on a shared held-out set; packaged findings as a $3.6M/yr cost case with 4 targeted retention actions.
