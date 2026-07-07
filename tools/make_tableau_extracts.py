# Builds outputs/drivers-summary.csv — the tidy per-level driver table behind
# the Tableau "driver explorer" sheet. One row per (driver, level): group size,
# attrition rate, and the driver-level effect size from the Phase 2 battery.
# Usage: .venv/Scripts/python tools/make_tableau_extracts.py
import pandas as pd

hr = pd.read_csv("data/hr-attrition.csv")
tests = pd.read_csv("outputs/driver-tests.csv")

# Categorical drivers as-is; key numeric drivers banded so they chart cleanly.
hr = hr.assign(
    TenureBand=pd.cut(hr["YearsAtCompany"], [-1, 1, 3, 6, 10, 100],
                      labels=["0-1 yr", "2-3 yrs", "4-6 yrs", "7-10 yrs", "10+ yrs"]),
    IncomeQuartile=pd.qcut(hr["MonthlyIncome"], 4,
                           labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]),
    AgeBand=pd.cut(hr["Age"], [17, 25, 35, 45, 60],
                   labels=["18-25", "26-35", "36-45", "46-60"]),
)

DRIVERS = {  # display driver -> (column, effect-size lookup in driver-tests.csv)
    "Overtime": ("OverTime", "OverTime"),
    "Job role": ("JobRole", "JobRole"),
    "Department": ("Department", "Department"),
    "Business travel": ("BusinessTravel", "BusinessTravel"),
    "Marital status": ("MaritalStatus", "MaritalStatus"),
    "Work-life balance (1=worst)": ("WorkLifeBalance", "WorkLifeBalance"),
    "Job satisfaction (1=worst)": ("JobSatisfaction", "JobSatisfaction"),
    "Stock option level": ("StockOptionLevel", "StockOptionLevel"),
    "Tenure at company": ("TenureBand", "YearsAtCompany"),
    "Monthly income": ("IncomeQuartile", "MonthlyIncome"),
    "Age": ("AgeBand", "Age"),
}

effect = tests.set_index("driver")[["effect_size", "effect_metric", "verdict"]]

rows = []
for display, (col, test_key) in DRIVERS.items():
    g = (hr.groupby(col, observed=True)
           .agg(n=("Attrition", "size"),
                leavers=("Attrition", lambda s: s.eq("Yes").sum()))
           .reset_index())
    g["attrition_rate"] = (g["leavers"] / g["n"]).round(4)
    g = g.rename(columns={col: "level"})
    g.insert(0, "driver", display)
    for meta in ("effect_size", "effect_metric", "verdict"):
        g[meta] = effect.loc[test_key, meta]
    rows.append(g)

out = pd.concat(rows, ignore_index=True)
out["level"] = out["level"].astype(str)
out.to_csv("outputs/drivers-summary.csv", index=False)
print(f"wrote outputs/drivers-summary.csv: {len(out)} rows, "
      f"{out['driver'].nunique()} drivers")
