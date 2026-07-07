# Interview script

## The 60-second walkthrough

"I built an attrition analysis the way a consulting team would deliver it — not a notebook, a decision package. Public IBM HR dataset, 1,470 employees, 16% attrition, which prices out around $3.6M a year at a conservative $15K per leaver.

Three layers. **Diagnostic:** I tested 30 candidate drivers with chi-squared and Welch tests, Bonferroni-corrected, and reported effect sizes next to every p-value — four drivers survived as both real and big: overtime, first-year tenure, bottom-quartile pay, and the Sales Rep role. **Predictive:** two models on one shared held-out split — logistic regression in R for odds ratios, XGBoost with SHAP in Python for per-person attribution. The interesting result: logistic regression won, AUC 0.865 vs 0.825 — small clean tabular data, boosting had nothing extra to find. I kept XGBoost anyway, because SHAP gives each person on the watch list a named top risk factor. **Prescriptive:** top decile of the risk list captures 49% of actual leavers — a retention budget aimed there works five times harder than spreading it evenly — and the memo turns the four drivers into four funded actions."

## Questions to expect

**"Why did logistic regression beat XGBoost?"**
n≈1,200 training rows, mostly monotone/linear relationships, no strong interactions worth the variance cost. Boosting shines on large data with structure to exploit; here it just paid an overfitting penalty. Also my class re-weighting (`scale_pos_weight`) deliberately traded calibration for recall, which hurt its Brier score — the threshold-free metrics are the fair comparison, and it still lost those. The bigger point: I'd rather report the true result than tune until the fancy model wins.

**"Your accuracy at 0.5 looks fine — why do you keep talking about deciles and lift?"**
16% base rate makes both accuracy and the 0.5 threshold nearly meaningless — predicting "nobody leaves" gets you 84% accuracy. The real use case is a ranked watch list under a limited outreach budget, so the operational metric is capture in the top decile: 49% of leavers in 10% of the workforce, 4.9× random.

**"Significant but trivial — what do you mean?"**
With n=1,470, tiny differences clear p<.05. I labeled every driver that passed significance but had a negligible effect size (|d|<0.2 or Cramér's V<0.1) as 'significant but trivial' and excluded them from recommendations. Example of the discipline: the analysis explicitly names factors like commute distance as *not* worth retention budget, even though a naive read of the p-values could sell them.

**"How would you validate this for real deployment?"** (the A/B-shaped question)
Two things. Time-split validation first — this is snapshot data, so 'predicts leaving' really means 'distinguishes leavers in-period'; a real model trains on period t and predicts t+1. Then an experiment on the intervention, not just the model: randomize the top-decile watch list into outreach vs no-outreach arms (unit = employee, stratified by department), pre-register retention at 12 months as the primary metric, and power it for the ~15-point base-rate difference we expect. The model can rank perfectly and the *program* can still be worthless — only the experiment tells you the retention conversations actually work.

**"What would you do with more time?"**
Calibrated probabilities (isotonic/Platt on a validation fold) so the scores read as true probabilities; repeated splits or CV for a CI on the AUC gap; survival analysis (time-to-attrition) instead of binary classification; and cost-sensitive threshold selection using role-specific replacement costs instead of the flat $15K.
