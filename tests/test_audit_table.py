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
    sens = [r for r in t if r["in_sensitivity_set_26"] == "yes"]
    assert len(t) == audit_stats.PRIMARY[1] == 32
    assert len(inc) == audit_stats.PRIMARY[0] == 25
    assert len(doc) == audit_stats.ATTRIBUTABLE[0] == 22
    assert sum(r["rationalised"].lower().startswith("yes") for r in doc) == 9
    assert len(sens) == audit_stats.SENSITIVITY_SYMMETRIC[1] == 26
    assert (
        sum(r["cause"] == "documented labels" for r in sens) == audit_stats.SENSITIVITY_ATTRIBUTABLE_SYMMETRIC[0] == 18
    )


def test_copy_groups_match_paper():
    """Section 4: 12 UCI-coded or -labeled, 5 fedesoriano, 6 recoded Kaggle (3 other cause), 2 unidentified."""
    inc = [r for r in audit_table.build() if r["verdict"] == "inconsistent"]
    count = {g: sum(r["copy_group"] == g for r in inc) for g in {r["copy_group"] for r in inc}}
    assert count == {
        audit_table.UCI_LABELS: 12,
        audit_table.FEDESORIANO: 5,
        audit_table.RECODED: 6,
        audit_table.UNIDENTIFIED: 2,
    }
    recoded_other = [r for r in inc if r["copy_group"] == audit_table.RECODED and r["cause"] != "documented labels"]
    assert len(recoded_other) == 3


def test_main_sensitivity_set_27():
    """Section 4: the main sensitivity set gives 18 of 27 attributable and 20 of 27 inconsistent."""
    sens = [r for r in audit_table.build() if r["in_sensitivity_set_27"] == "yes"]
    assert len(sens) == audit_stats.SENSITIVITY[1] == audit_stats.SENSITIVITY_ATTRIBUTABLE[1] == 27
    assert sum(r["verdict"] == "inconsistent" for r in sens) == audit_stats.SENSITIVITY[0] == 20
    assert sum(r["cause"] == "documented labels" for r in sens) == audit_stats.SENSITIVITY_ATTRIBUTABLE[0] == 18
