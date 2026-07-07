# Generates dashboard/attrition-dashboard.html — a self-contained interactive
# dashboard (no dependencies, no server, no account) built from the same two
# extracts that feed the Tableau version. Open the file in any browser.
# Usage: .venv/Scripts/python tools/make_html_dashboard.py
import json

import pandas as pd

scores = pd.read_csv("outputs/attrition-risk-scores.csv")
drivers = pd.read_csv("outputs/drivers-summary.csv")

n = len(scores)
leavers = int(scores["Attrition"].eq("Yes").sum())
rate = leavers / n

dept = (scores.groupby("Department")
        .agg(n=("Attrition", "size"),
             rate=("Attrition", lambda s: s.eq("Yes").mean()))
        .reset_index().sort_values("rate", ascending=False))

watch = (scores[(scores["Attrition"] == "No") & (scores["risk_decile"] >= 10)]
         .sort_values("risk_score", ascending=False)
         [["EmployeeNumber", "Department", "JobRole", "OverTime",
           "MonthlyIncome", "Age", "YearsAtCompany", "risk_score",
           "top_shap_driver"]])

drivers_j = drivers.to_dict("records")
dept_j = dept.to_dict("records")
watch_j = watch.to_dict("records")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Workforce Attrition Analytics — Dashboard</title>
<style>
  :root {{ --red:#e15759; --dark:#2b3a55; --muted:#6b7280; --bg:#f6f7f9; --card:#ffffff; }}
  * {{ box-sizing:border-box; margin:0; }}
  body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:#1f2937; padding:24px; }}
  h1 {{ font-size:22px; color:var(--dark); }}
  .sub {{ color:var(--muted); font-size:13px; margin:4px 0 20px; }}
  .row {{ display:flex; gap:16px; flex-wrap:wrap; margin-bottom:16px; }}
  .card {{ background:var(--card); border-radius:10px; padding:18px 20px; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
  .kpi {{ flex:1; min-width:180px; text-align:center; }}
  .kpi .big {{ font-size:34px; font-weight:700; color:var(--red); }}
  .kpi .lbl {{ font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; margin-top:4px; }}
  .half {{ flex:1; min-width:420px; }}
  h2 {{ font-size:15px; color:var(--dark); margin-bottom:4px; }}
  .note {{ font-size:12px; color:var(--muted); margin-bottom:12px; }}
  .bar-row {{ display:flex; align-items:center; margin:5px 0; font-size:12.5px; }}
  .bar-label {{ width:220px; text-align:right; padding-right:10px; color:#374151; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .bar-track {{ flex:1; background:#eef0f3; border-radius:4px; height:20px; position:relative; }}
  .bar-fill {{ background:var(--red); height:100%; border-radius:4px; }}
  .bar-val {{ position:absolute; left:calc(100% + 8px); top:1px; font-size:11.5px; color:#374151; white-space:nowrap; }}
  .bar-track {{ margin-right:86px; }}
  .avg-line {{ position:absolute; top:-3px; bottom:-3px; width:2px; background:var(--dark); opacity:.55; }}
  select, input[type=range] {{ font:inherit; }}
  .controls {{ display:flex; gap:18px; align-items:center; font-size:13px; margin-bottom:10px; flex-wrap:wrap; }}
  table {{ width:100%; border-collapse:collapse; font-size:12.5px; }}
  th {{ text-align:left; color:var(--muted); font-weight:600; padding:7px 8px; border-bottom:2px solid #e5e7eb;
       cursor:pointer; user-select:none; white-space:nowrap; }}
  td {{ padding:6px 8px; border-bottom:1px solid #f0f1f3; }}
  .score {{ font-weight:700; padding:2px 8px; border-radius:4px; color:#fff; }}
  .pill {{ background:#eef2ff; color:#3730a3; border-radius:999px; padding:2px 9px; font-size:11.5px; white-space:nowrap; }}
  footer {{ font-size:11.5px; color:var(--muted); margin-top:18px; line-height:1.5; }}
</style>
</head>
<body>
<h1>Workforce Attrition Analytics</h1>
<div class="sub">IBM HR sample data (synthetic, n={n:,}) &middot; retrospective demonstration &middot;
risk scores = logistic regression (held-out AUC 0.865) &middot; risk patterns = companion XGBoost/SHAP &middot;
<a href="https://github.com/Khan-zoh/workforce-attrition-analytics">full analysis on GitHub</a></div>

<div class="row">
  <div class="card kpi"><div class="big">{rate:.1%}</div><div class="lbl">Attrition rate</div></div>
  <div class="card kpi"><div class="big">{leavers}</div><div class="lbl">Leavers (of {n:,})</div></div>
  <div class="card kpi"><div class="big" id="cost">$3.6M</div><div class="lbl">Annual cost @ <span id="costLbl">$15K</span>/leaver</div>
    <input type="range" id="costSlider" min="5000" max="50000" step="5000" value="15000" style="width:90%"></div>
  <div class="card kpi"><div class="big">4.9&times;</div><div class="lbl">Top-decile lift (test set)</div></div>
</div>

<div class="row">
  <div class="card half">
    <h2>Attrition by department</h2>
    <div class="note">Line = company average ({rate:.1%})</div>
    <div id="deptChart"></div>
  </div>
  <div class="card half">
    <h2>Why people leave — driver explorer</h2>
    <div class="controls">
      <label>Driver: <select id="driverSel"></select></label>
      <span class="note" id="driverMeta" style="margin:0"></span>
    </div>
    <div id="driverChart"></div>
  </div>
</div>

<div class="card">
  <h2>Watch list — highest-risk employees in the snapshot (top decile, stayers only)</h2>
  <div class="note">Retrospective demo: model trained on this labeled snapshot; a deployment would score an
  unlabeled current roster. "Risk pattern" is the companion model's largest SHAP attribution — a conversation
  starter, not a verdict. Click headers to sort.</div>
  <table id="watchTable"><thead><tr>
    <th data-k="EmployeeNumber">ID</th><th data-k="Department">Department</th><th data-k="JobRole">Role</th>
    <th data-k="OverTime">Overtime</th><th data-k="MonthlyIncome">Income/mo</th><th data-k="Age">Age</th>
    <th data-k="YearsAtCompany">Tenure</th><th data-k="risk_score">Risk score</th><th data-k="top_shap_driver">Risk pattern</th>
  </tr></thead><tbody></tbody></table>
</div>

<footer>Method: 30-driver hypothesis-test battery (chi-squared / Welch, Bonferroni-corrected, effect sizes) &rarr;
logistic regression (R) vs XGBoost+SHAP (Python) on a shared held-out split &rarr; this dashboard + executive memo.
Drivers shown in the explorer are limited to those that survived multiple-comparison correction with
non-trivial effect sizes, unless "show all" is chosen. Zohair Khan &middot; 2026.</footer>

<script>
const LEAVERS={leavers}, RATE={rate:.6f};
const DRIVERS={json.dumps(drivers_j)};
const DEPT={json.dumps(dept_j)};
const WATCH={json.dumps(watch_j)};

// cost KPI
const fmtM = v => '$'+(v/1e6).toFixed(1)+'M';
costSlider.oninput = () => {{
  cost.textContent = fmtM(LEAVERS*costSlider.value);
  costLbl.textContent = '$'+(costSlider.value/1000)+'K';
}};
costSlider.oninput();

function bars(el, rows, maxV) {{
  el.innerHTML = rows.map(r => `
    <div class="bar-row"><div class="bar-label" title="${{r.label}}">${{r.label}}</div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${{(100*r.v/maxV).toFixed(1)}}%"></div>
        <div class="avg-line" style="left:${{(100*RATE/maxV).toFixed(1)}}%"></div>
        <div class="bar-val">${{(100*r.v).toFixed(1)}}% (n=${{r.n}})</div>
      </div></div>`).join('');
}}

// department chart
bars(deptChart, DEPT.map(d => ({{label:d.Department, v:d.rate, n:d.n}})), 0.5);

// driver explorer
const meaningful = [...new Set(DRIVERS.filter(d => d.verdict==='meaningful driver').map(d => d.driver))];
const allDrivers = [...new Set(DRIVERS.map(d => d.driver))];
driverSel.innerHTML = meaningful.map(d => `<option>${{d}}</option>`).join('') +
  allDrivers.filter(d => !meaningful.includes(d)).map(d => `<option>${{d}} (below threshold)</option>`).join('');
function drawDriver() {{
  const name = driverSel.value.replace(' (below threshold)','');
  const rows = DRIVERS.filter(d => d.driver===name);
  bars(driverChart, rows.map(r => ({{label:r.level, v:r.attrition_rate, n:r.n}})), 0.5);
  driverMeta.textContent = `${{rows[0].effect_metric}} = ${{(+rows[0].effect_size).toFixed(2)}} · ${{rows[0].verdict}}`;
}}
driverSel.onchange = drawDriver; drawDriver();

// watch list table
let sortK='risk_score', sortAsc=false;
function heat(v) {{
  const t=(v-0.3)/0.7, c=Math.round(225-90*Math.max(0,Math.min(1,t)));
  return `background:rgb(225,${{c}},${{c}})`;
}}
function drawTable() {{
  const rows=[...WATCH].sort((a,b)=>(a[sortK]>b[sortK]?1:-1)*(sortAsc?1:-1));
  watchTable.tBodies[0].innerHTML = rows.map(r=>`<tr>
    <td>${{r.EmployeeNumber}}</td><td>${{r.Department}}</td><td>${{r.JobRole}}</td><td>${{r.OverTime}}</td>
    <td>$${{r.MonthlyIncome.toLocaleString()}}</td><td>${{r.Age}}</td><td>${{r.YearsAtCompany}} yrs</td>
    <td><span class="score" style="${{heat(r.risk_score)}}">${{r.risk_score.toFixed(2)}}</span></td>
    <td><span class="pill">${{r.top_shap_driver}}</span></td></tr>`).join('');
}}
document.querySelectorAll('#watchTable th').forEach(th => th.onclick = () => {{
  const k=th.dataset.k; sortAsc = (sortK===k) ? !sortAsc : false; sortK=k; drawTable();
}});
drawTable();
</script>
</body>
</html>
"""

with open("dashboard/attrition-dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"wrote dashboard/attrition-dashboard.html "
      f"({len(html)//1024} KB, watch list rows: {len(watch_j)})")
