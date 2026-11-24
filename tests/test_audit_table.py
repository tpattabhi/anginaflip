"""The consolidated audit table reproduces the counts reported in Section 4 of the paper."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import audit_stats  # noqa: E402
import audit_table  # noqa: E402


def test_table_reproduces_paper_counts():
    t = audit_table.build()
    inc = [r for r in t if r["verdict"] == "inconsistent"]
    doc = [r for r in inc if r["cause"] == "documented labels"]
    sens = [r for r in t if r["in_sensitivity_set"] == "yes"]
    assert len(t) == audit_stats.PRIMARY[1] == 32
    assert len(inc) == audit_stats.PRIMARY[0] == 25
    assert len(doc) == audit_stats.ATTRIBUTABLE[0] == 22
    assert sum(r["rationalised"].lower().startswith("yes") for r in doc) == 9
    assert len(sens) == audit_stats.SENSITIVITY_SYMMETRIC[1] == 26
    assert (
        sum(r["cause"] == "documented labels" for r in sens) == audit_stats.SENSITIVITY_ATTRIBUTABLE_SYMMETRIC[0] == 18
    )
