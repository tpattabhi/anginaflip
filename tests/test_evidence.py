"""The numbers the paper reports for E1-E4 and E7, asserted against the archived source files."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import evidence_checks as ec  # noqa: E402


@pytest.fixture(scope="module")
def detrano():
    return ec.check_detrano1986()


def test_detrano_table1_matches_only_reversed(detrano):
    assert detrano["n"] == 303
    assert detrano["table1_documented"] == 0
    assert detrano["table1_reversed"] == 15


def test_detrano_table2_vessels(detrano):
    assert detrano["table2_vessels"] == ec.DETRANO_TABLE2_VESSELS


def test_detrano_table8_reproduced_only_reversed(detrano):
    assert detrano["table8_cp_reversed"] == pytest.approx(ec.DETRANO_TABLE8_SUBSET1, abs=0.005)
    assert detrano["table8_cp_as_stored"] == pytest.approx((-7.77, 0.07, -0.85, 1.10), abs=0.005)


@pytest.mark.parametrize(
    "site, code4_all_three, code4_total, code1_none, code1_total",
    [("budapest", 118, 123, 10, 11), ("switzerland", 91, 98, 4, 4), ("long_beach", 126, 131, 8, 8)],
)
def test_raw_features(site, code4_all_three, code4_total, code1_none, code1_total):
    tab = ec.check_raw_features()[site]
    assert tab.loc[4, 3] == code4_all_three and tab.loc[4].sum() == code4_total
    assert tab.loc[1, 0] == code1_none and tab.loc[1].sum() == code1_total


def test_raw_features_middle_codes_swap_too():
    for site in ("budapest", "long_beach"):
        tab = ec.check_raw_features()[site]
        assert tab.loc[3].idxmax() == 2  # code 3: mostly two features (atypical angina)
        assert tab.loc[2].idxmax() == 1  # code 2: mostly one feature (non-anginal pain)


def test_cleve_mod_1990_uses_documented_labels():
    e3 = ec.check_cleve_mod()
    assert e3["rows"] == 303 and e3["joined"] == 303
    tab = e3["crosstab"]
    expected = {"angina": (1, 23), "abnang": (2, 50), "notang": (3, 87), "asympt": (4, 143)}
    for label, (code, n) in expected.items():
        assert tab.loc[label, code] == n
        assert tab.loc[label].sum() == n  # every row with this label has this code
    assert e3["sick_share_asympt"] == pytest.approx(0.73, abs=0.005)


def test_statlog_is_cleveland_subset():
    e4 = ec.check_statlog()
    assert e4 == {
        "rows": 270,
        "matched": 270,
        "unique_matched": 270,
        "cp_identical": True,
        "outcome_identical": True,
    }


def test_cad_rate_by_code():
    rates = ec.cad_rate_by_code()
    assert rates[1] == pytest.approx(0.304) and rates[4] == pytest.approx(0.729)


def _is_mapping(tab, mapping):
    """Each copy code maps to exactly one UCI code, as given."""
    return all(
        tab.loc[copy_code].astype(bool).sum() == 1 and tab.loc[copy_code, uci] > 0 for copy_code, uci in mapping.items()
    )


def test_openml_words_follow_documentation():
    for tab in ec.check_openml().values():
        assert _is_mapping(tab, {"typ_angina": 1, "atyp_angina": 2, "non_anginal": 3, "asympt": 4})


def test_pmlb_is_uci_minus_one():
    tabs = ec.check_pmlb()
    assert set(tabs) == {"cleveland", "hungarian", "va_long_beach", "zurich"}
    for tab in tabs.values():
        assert _is_mapping(tab, {0: 1, 1: 2, 2: 3, 3: 4})


KAGGLE_EXPECTED = {
    "fedesoriano_heart-failure-prediction": {"TA": 1, "ATA": 2, "NAP": 3, "ASY": 4},
    "johnsmith88_heart-disease-dataset": {0: 4, 1: 2, 2: 3, 3: 1},
    "redwankarimsony_heart-disease-data": {
        "typical angina": 1,
        "atypical angina": 2,
        "non-anginal": 3,
        "asymptomatic": 4,
    },
}


def test_kaggle_copies():
    tabs = ec.check_kaggle()
    if not tabs:
        pytest.skip("Kaggle copies are not redistributed; download them to evidence/kaggle/<owner>_<slug>/")
    for name, mapping in KAGGLE_EXPECTED.items():
        assert _is_mapping(tabs[name], mapping), name


def test_logistic_fit_recovers_known_coefficients():
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.normal(size=(5000, 1))
    p = 1 / (1 + np.exp(-(0.5 + 1.5 * x[:, 0])))
    y = (rng.random(5000) < p).astype(float)
    assert ec.logistic_fit(x, y) == pytest.approx([0.5, 1.5], abs=0.1)
