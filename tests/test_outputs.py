"""Output contracts: every downstream consumer (Tableau, memo, README) reads
these files, so their shape is pinned here. Run after re-generating any output."""

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def scores():
    return pd.read_csv(ROOT / "outputs" / "attrition-risk-scores.csv")


@pytest.fixture(scope="module")
def split():
    return pd.read_csv(ROOT / "data" / "train-test-split.csv")


def test_risk_scores_cover_every_employee(scores):
    assert len(scores) == 1470
    assert scores["EmployeeNumber"].is_unique


def test_risk_scores_are_probabilities(scores):
    assert scores["risk_score"].between(0, 1).all()


def test_risk_deciles_are_balanced(scores):
    counts = scores["risk_decile"].value_counts()
    assert sorted(counts.index) == list(range(1, 11))
    assert counts.max() - counts.min() <= 1  # qcut on ranks -> near-equal bins


def test_risk_scores_required_columns(scores):
    required = {"EmployeeNumber", "set", "Attrition", "risk_score",
                "risk_decile", "xgb_score", "top_shap_driver", "Department",
                "JobRole", "OverTime", "MonthlyIncome", "Age",
                "YearsAtCompany", "JobSatisfaction"}
    assert required.issubset(scores.columns)
    assert scores["xgb_score"].between(0, 1).all()


def test_dashboard_score_is_the_headline_model(scores):
    """The decision score in the extract must be the logistic model's —
    that's the model the README/memo headline metrics come from."""
    logreg = pd.read_csv(ROOT / "outputs" / "logreg-scores.csv")
    merged = scores.merge(logreg, on="EmployeeNumber")
    assert (merged["risk_score"] == merged["logreg_score"]).all()


def test_split_contract(split):
    assert len(split) == 1470
    assert split["EmployeeNumber"].is_unique
    assert set(split["set"]) == {"train", "test"}
    assert (split["set"] == "test").sum() == 294


def test_split_is_stratified(split, scores):
    merged = split.merge(scores[["EmployeeNumber", "Attrition"]],
                         on="EmployeeNumber")
    rates = merged.groupby("set")["Attrition"].apply(lambda s: s.eq("Yes").mean())
    assert abs(rates["train"] - rates["test"]) < 0.01


@pytest.mark.parametrize("fname", ["logreg-metrics.csv", "xgb-metrics.csv"])
def test_model_metrics_sane(fname):
    m = pd.read_csv(ROOT / "outputs" / fname)
    assert len(m) == 1
    row = m.iloc[0]
    assert 0.5 < row["auc"] <= 1.0
    assert 0 <= row["brier"] <= 0.25
    assert row["n_test"] == 294
    assert 1.0 <= row["top_decile_lift"] <= 10.0


def test_driver_tests_battery():
    d = pd.read_csv(ROOT / "outputs" / "driver-tests.csv")
    assert (d["p_adjusted"] >= d["p_raw"] - 1e-12).all()
    assert "direction" in d.columns and d["direction"].notna().all()
    assert set(d["verdict"]) <= {"meaningful driver", "significant but trivial",
                                 "not significant"}
    # the headline drivers must survive the battery, or the memo story is broken
    meaningful = set(d.loc[d["verdict"] == "meaningful driver", "driver"])
    assert "OverTime" in meaningful
    assert "MonthlyIncome" in meaningful


def test_html_dashboard_is_current():
    html = (ROOT / "dashboard" / "attrition-dashboard.html").read_text(encoding="utf-8")
    assert "const LEAVERS=237" in html          # headline count baked in
    assert "risk scores = logistic regression" in html
    scores = pd.read_csv(ROOT / "outputs" / "attrition-risk-scores.csv")
    n_watch = len(scores[(scores["Attrition"] == "No") & (scores["risk_decile"] >= 10)])
    assert html.count('"top_shap_driver"') >= 1 and n_watch > 0


def test_drivers_summary_schema():
    d = pd.read_csv(ROOT / "outputs" / "drivers-summary.csv")
    required = {"driver", "level", "n", "leavers", "attrition_rate",
                "effect_size", "effect_metric", "verdict"}
    assert required.issubset(d.columns)
    assert d["attrition_rate"].between(0, 1).all()
    assert (d.groupby("driver")["n"].sum() == 1470).all()


def test_published_headline_numbers_still_hold():
    """Every number quoted in README.md / memo.md, pinned with tolerances.
    If any of these fail, the docs are lying — fix the docs or the pipeline."""
    logreg = pd.read_csv(ROOT / "outputs" / "logreg-metrics.csv").iloc[0]
    assert abs(logreg["auc"] - 0.865) < 0.005
    assert abs(logreg["top_decile_capture"] - 0.489) < 0.005
    assert abs(logreg["top_decile_lift"] - 4.89) < 0.05

    xgb = pd.read_csv(ROOT / "outputs" / "xgb-metrics.csv").iloc[0]
    assert abs(xgb["auc"] - 0.825) < 0.01  # slightly looser: hardware variance

    scores = pd.read_csv(ROOT / "outputs" / "attrition-risk-scores.csv")
    n_leavers = scores["Attrition"].eq("Yes").sum()
    assert n_leavers == 237                      # 16.1% of 1470
    assert abs(n_leavers / len(scores) - 0.161) < 0.001

    d = pd.read_csv(ROOT / "outputs" / "drivers-summary.csv")
    ot = d[d["driver"] == "Overtime"].set_index("level")["attrition_rate"]
    assert abs(ot["Yes"] - 0.305) < 0.001        # 30.5% vs 10.4%
    assert abs(ot["No"] - 0.104) < 0.001
