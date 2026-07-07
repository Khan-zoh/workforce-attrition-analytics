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
                "risk_decile", "top_shap_driver", "Department", "JobRole",
                "OverTime", "MonthlyIncome", "Age", "YearsAtCompany",
                "JobSatisfaction"}
    assert required.issubset(scores.columns)


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
    assert set(d["verdict"]) <= {"meaningful driver", "significant but trivial",
                                 "not significant"}
    # the headline drivers must survive the battery, or the memo story is broken
    meaningful = set(d.loc[d["verdict"] == "meaningful driver", "driver"])
    assert "OverTime" in meaningful
    assert "MonthlyIncome" in meaningful
