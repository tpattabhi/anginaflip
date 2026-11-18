import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

import llm_probe as lp  # noqa: E402

ZIP = ROOT / "evidence" / "uci-raw-archive" / "heart+disease.zip"


@pytest.fixture(scope="module")
def cle():
    return lp.load_uci(str(ZIP))


def test_load_cleveland(cle):
    assert len(cle) == 303
    assert cle["cad"].sum() == 139
    assert sorted(cle["cp"].unique()) == [1, 2, 3, 4]


def test_load_hungarian():
    hu = lp.load_uci(str(ZIP), "processed.hungarian.data")
    assert len(hu) == 294


@pytest.mark.parametrize(
    "code,doc,cor",
    [
        (1, "typical angina", "asymptomatic"),
        (4, "asymptomatic", "typical angina"),
        (2, "atypical angina", "non-anginal pain"),
    ],
)
def test_cp_text(code, doc, cor):
    assert lp.cp_text(code, "D") == doc
    assert lp.cp_text(code, "C") == cor
    assert lp.cp_text(code, "O") is None


def test_cp_text_rejects_unknown():
    with pytest.raises(ValueError):
        lp.cp_text(1, "X")


def test_conditions_differ_only_in_chest_pain_line(cle):
    row = cle.iloc[0]
    d = lp.build_prompt(row, "D", "full").splitlines()
    c = lp.build_prompt(row, "C", "full").splitlines()
    o = lp.build_prompt(row, "O", "full").splitlines()
    assert len(d) == len(c) == len(o) + 1
    diff = [(a, b) for a, b in zip(d, c) if a != b]
    assert len(diff) == 1 and diff[0][0].startswith("Chest pain type:")
    assert [line for line in d if not line.startswith("Chest pain type:")] == o


def test_minimal_template(cle):
    lines = lp.patient_lines(cle.iloc[0], "C", "minimal")
    assert [line.split(":")[0] for line in lines] == ["Age", "Sex", "Chest pain type"]


def test_missing_values_say_unknown():
    row = pd.Series({c: np.nan for c in lp.COLUMNS} | {"cp": 4, "age": 50.0, "sex": 1.0})
    text = lp.build_prompt(row, "C", "full")
    assert "Thallium stress scan: unknown" in text
    assert "Number of major vessels colored by fluoroscopy: unknown" in text


def test_build_jobs_shape(cle):
    jobs = lp.build_jobs(cle.head(5))
    assert len(jobs) == 5 * len(lp.CONDITIONS) * len(lp.TEMPLATES)
    w = jobs.pivot_table(index=["pid", "template"], columns="condition", values="prompt", aggfunc="first")
    assert (w["D"] != w["C"]).all() and (w["C"] != w["O"]).all()
    assert set(jobs["condition"]) == set(lp.CONDITIONS)


def test_metrics_known_values():
    y = np.array([0, 0, 1, 1])
    assert lp.auc(y, np.array([0.1, 0.4, 0.35, 0.8])) == pytest.approx(0.75)
    assert lp.auc(y, np.array([0.5, 0.5, 0.5, 0.5])) == pytest.approx(0.5)
    assert lp.brier(y, np.array([0, 0, 1, 1])) == 0
    assert lp.log_loss(y, np.full(4, 0.5)) == pytest.approx(np.log(2))


def test_p_yes():
    assert lp.p_yes(np.array([0.0]), np.array([0.0]))[0] == pytest.approx(0.5)
    assert lp.p_yes(np.array([2.0]), np.array([0.0]))[0] > 0.8


def test_summary_detects_planted_effect():
    rng = np.random.default_rng(0)
    n = 300
    y = rng.integers(0, 2, n)
    rows = []
    for pid in range(n):
        for cond, noise in [("C", 0.2), ("D", 1.0), ("O", 0.6)]:
            for t in lp.TEMPLATES:
                p = 1 / (1 + np.exp(-(2 * y[pid] - 1 + rng.normal(0, noise * 2))))
                rows.append(
                    {"model": "m", "template": t, "condition": cond, "pid": pid, "cad": y[pid], "cp": 1, "p_yes": p}
                )
    s = lp.summarise(pd.DataFrame(rows))
    full = s[s.template == "full"].iloc[0]
    assert full["d_auc_C_minus_D"] > 0 and full["d_auc_lo"] > 0


def test_bootstrap_zero_when_identical():
    y = np.array([0, 1] * 20)
    p = np.linspace(0.1, 0.9, 40)
    bs = lp.paired_bootstrap(y, p, p, lp.auc, n_boot=50)
    assert bs["diff"] == 0 and bs["lo"] == 0 and bs["hi"] == 0
