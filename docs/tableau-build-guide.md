# Tableau Dashboard — Build Guide

Everything the dashboard needs is already computed and sitting in two CSVs:

| File | Feeds | Grain |
|---|---|---|
| `outputs/attrition-risk-scores.csv` | KPI overview + at-risk table | one row per employee (n=1,470), with XGBoost `risk_score`, `risk_decile` (10 = riskiest), and `top_shap_driver` |
| `outputs/drivers-summary.csv` | driver explorer | one row per (driver, level) with group size, attrition rate, effect size, and the Phase-2 verdict |

Total build time: roughly 45–60 minutes the first time.

## 0. Install & account (one-time, ~10 min)

1. Create a free account at https://public.tableau.com (this is also where the dashboard gets published).
2. Download **Tableau Public** (Desktop) from that site and install. Note: Tableau Public saves **only to the cloud** — there is no local save. That's fine for a portfolio; the workbook lives at your public profile URL.

## 1. Connect the data (~5 min)

1. Open Tableau Public → **Connect → Text file** → pick `outputs/attrition-risk-scores.csv`.
2. In the data-source screen, click **Add** (next to Connections) → **Text file** → `outputs/drivers-summary.csv`. Two independent data sources, no join/relationship needed (each sheet uses one of them).
3. On `attrition-risk-scores`: check that `risk_score` is a number (decimal), `risk_decile` a whole number, `EmployeeNumber` a whole number — set `EmployeeNumber` to **Dimension** (right-click the field → Convert to Dimension) so it doesn't get summed.
4. Go to Sheet 1.

## 2. The cost parameter (~3 min)

The memo prices attrition at a flat $15K per leaver and this should be adjustable live:

1. In the Data pane, click the ▼ menu (top right of the pane) → **Create Parameter…**
2. Name: `Cost per Leaver`. Data type: Integer. Current value: `15000`. Allowable values: Range, min `5000`, max `50000`, step `5000`. OK.
3. Right-click the new parameter → **Show Parameter** (do this again on the dashboard later).

## 3. Sheet 1 — "Overview" KPIs (~10 min)

Data source: `attrition-risk-scores`.

1. Create the calculated fields you'll need (Analysis menu → Create Calculated Field):
   - `Is Leaver` = `IF [Attrition] = "Yes" THEN 1 ELSE 0 END`
   - `Attrition Rate` = `SUM([Is Leaver]) / COUNT([EmployeeNumber])`
   - `Annual Attrition Cost` = `SUM([Is Leaver]) * [Cost per Leaver]`
2. **BAN (big number) row.** Simplest robust pattern — three tiny sheets:
   - Sheet "KPI – Rate": drag `Attrition Rate` to **Text** on the Marks card. Format as percentage, 1 decimal. Font size ~28, bold.
   - Sheet "KPI – Leavers": drag `Is Leaver` (SUM) to Text.
   - Sheet "KPI – Cost": drag `Annual Attrition Cost` to Text; format as currency, custom `$#,##0,,.0"M"` if you want millions.
3. Sheet "Attrition by Department": `Department` to **Rows**, `Attrition Rate` to **Columns**; sort descending; drag `Attrition Rate` to **Label**; add a constant reference line at the company rate (right-click the axis → Add Reference Line → Constant = your overall rate, e.g. 0.161) so every bar reads against the average.

## 4. Sheet 2 — "Why people leave" driver explorer (~10 min)

Data source: `drivers-summary`.

1. Drag `driver` to **Rows**, then `level` to **Rows** (to the right of driver).
2. Drag `attrition_rate` to **Columns** (it will aggregate; each driver×level is one row in the CSV, so AVG = the value itself).
3. Drag `attrition_rate` to **Color** (red sequential palette) and to **Label** (format %, 1 decimal). Drag `n` to **Tooltip** so small groups are visible for what they are.
4. Drag `verdict` to **Filter** → keep `meaningful driver` (this is the point of Phase 2: the explorer only shows drivers that survived testing; add the others back deliberately if you want the contrast).
5. Sort: right-click `driver` on Rows → Sort → by field, `effect_size`, descending — strongest evidence on top.
6. Title: "Attrition rate by driver — only statistically meaningful drivers shown (sorted by effect size)".

## 5. Sheet 3 — "Who to talk to" at-risk table (~10 min)

Data source: `attrition-risk-scores`. This is the watch list: **current employees** the model rates riskiest, each with its SHAP "why".

1. Filters shelf: `Attrition` = **No** (leavers can't be retained), `risk_decile` = **10** (top decile; add 9 if you want a longer list).
2. **Rows:** `EmployeeNumber`, `Department`, `JobRole`, `OverTime`, `top_shap_driver` (all as dimensions — you'll get a text table).
3. Drag `risk_score` to **Text** (AVG), format 2 decimals; drag `risk_score` to **Color** on the Marks card (red sequential) with Marks type **Square** for a heat-table look; drag `MonthlyIncome`, `Age`, `YearsAtCompany`, `JobSatisfaction` to **Tooltip**.
4. Sort by `risk_score` descending (toolbar sort button, or right-click `EmployeeNumber` → Sort by field `risk_score` desc).
5. Title: "Highest-risk current employees — 'Top driver' = largest SHAP attribution for that person".

## 6. Dashboard assembly (~10 min)

1. New Dashboard (bottom tab bar). Size: **Automatic** (or Fixed 1400×900 for pixel control).
2. Layout, top to bottom:
   - Horizontal container: the three KPI BANs side by side.
   - "Attrition by Department" bar chart.
   - Side-by-side (horizontal container): driver explorer (left, ~60%) and at-risk table (right, ~40%).
3. Drag the `Cost per Leaver` parameter control next to the KPI row (Dashboard pane → your parameter shows under "Objects/Parameters" once used; or on any sheet right-click parameter → Show Parameter, then it appears on the dashboard).
4. Add a text object at the bottom: *"IBM HR sample data (synthetic, n=1,470). Risk scores: XGBoost; drivers validated with chi-squared/Welch tests, Bonferroni-corrected. Full analysis: github.com/Khan-zoh/workforce-attrition-analytics"*.
5. Enable "Use as Filter" (funnel icon) on the Department bar chart so clicking a department filters the at-risk table — an easy interactivity win for demos.

## 7. Publish (~5 min)

1. **File → Save to Tableau Public As…** → name it `Workforce Attrition Analytics`. It uploads and opens in the browser.
2. On the published page: **Edit Details** → write a 2-line description with the repo link → under Settings ensure **"Show workbook sheets as tabs"** is off (dashboard only) and toggle **"Allow workbook and its data to be downloaded"** as you prefer.
3. Copy the public URL → paste it into `README.md` under **Live Dashboard**.
4. Take a full-dashboard screenshot → save as `outputs/tableau-preview.png` → commit. (The README already references this filename.)

## Sanity checklist before calling it done

- [ ] KPI rate matches the README headline (16.1%).
- [ ] Cost BAN responds when the parameter is moved.
- [ ] Driver explorer shows only meaningful drivers, effect-size sorted, overtime at/near top.
- [ ] At-risk table contains **no** `Attrition = Yes` rows and every row has a top driver.
- [ ] Dashboard link works in a private/incognito window (i.e., truly public).
