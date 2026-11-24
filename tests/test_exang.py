"""Exercise-induced angina by stored chest-pain code (Section 2): code 4 is highest at every site."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import evidence_checks as ec  # noqa: E402


def test_exang_highest_in_code_4_at_every_site():
    code4, others = [], []
    for site in ("cleveland", "hungarian", "switzerland", "va"):
        d = ec.load_processed(site)
        e = pd.to_numeric(d["exang"], errors="coerce")
        rate = {int(k): round(float((g.dropna() == 1).mean()) * 100) for k, g in e.groupby(d["cp"].astype(int))}
        assert rate[4] > max(rate[k] for k in (1, 2, 3))
        code4.append(rate[4])
        others += [rate[k] for k in (1, 2, 3)]
    assert (min(code4), max(code4)) == (51, 71)  # paper: 51--71%
    assert (min(others), max(others)) == (0, 55)  # paper: 0--55%
