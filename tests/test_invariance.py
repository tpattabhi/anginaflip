"""E9(a-b): the paper's claims about conventional models, recomputed from the data."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import invariance  # noqa: E402


@pytest.fixture(scope="module")
def res():
    return invariance.run()


def test_logistic_predictions_identical(res):
    for name in ("logistic_ordinal", "logistic_onehot"):
        m = res["models"][name]
        assert m["max_abs_pred_diff"] < 1e-9
        assert m["auc_documented"] == pytest.approx(m["auc_corrected"])
    assert res["models"]["logistic_ordinal"]["auc_documented"] == pytest.approx(0.903, abs=0.0005)
    assert res["models"]["logistic_onehot"]["auc_documented"] == pytest.approx(0.911, abs=0.0005)


def test_tree_models_differ_by_at_most_0002(res):
    for name in ("random_forest", "gradient_boosting"):
        m = res["models"][name]
        assert abs(m["auc_documented"] - m["auc_corrected"]) <= 0.002


def test_documented_labels_give_backwards_coefficients(res):
    coefs = res["documented_onehot_logistic_cp_coefs"]
    assert max(coefs, key=coefs.get) == "cp_asymptomatic"
    assert coefs["cp_asymptomatic"] == pytest.approx(0.48, abs=0.005)
    assert coefs["cp_typical_angina"] < 0


# Logistic models are deterministic up to floating point. Tree ensembles can differ slightly across
# platforms and library versions (see "environment" in results/invariance.json), so they get a tolerance.
SAVED_AUC_TOLERANCE = {
    "logistic_ordinal": 1e-12,
    "logistic_onehot": 1e-12,
    "random_forest": 2e-4,
    "gradient_boosting": 2e-4,
}


@pytest.mark.parametrize("name,tolerance", SAVED_AUC_TOLERANCE.items())
def test_saved_results_match_a_fresh_run(res, name, tolerance):
    saved = json.loads((ROOT / "results" / "invariance.json").read_text())
    for condition in ("documented", "corrected"):
        key = f"auc_{condition}"
        assert saved["models"][name][key] == pytest.approx(res["models"][name][key], abs=tolerance)


@pytest.mark.parametrize("name", ["random_forest", "gradient_boosting"])
def test_tree_models_discrimination_unchanged_in_a_fresh_run(res, name):
    """The paper's claim, tested directly: relabeling chest pain changes tree-model AUC by at most 0.002."""
    m = res["models"][name]
    assert abs(m["auc_documented"] - m["auc_corrected"]) <= 0.002
