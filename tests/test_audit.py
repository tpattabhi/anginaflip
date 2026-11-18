"""E8: the sample is reproducible and the headline statistics match the paper."""

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import audit_stats  # noqa: E402
import blind_packet  # noqa: E402
import sample_audit  # noqa: E402

AUDIT = ROOT / "evidence" / "literature-audit"


def test_sample_is_reproducible():
    res = sample_audit.compute()
    assert (res["frame"], res["eligible"]) == (269, 230)
    saved = json.loads((AUDIT / "sample.json").read_text())
    assert res["sample_150"] == saved["sample_150"]


def test_worklist_follows_the_sample_order():
    with open(AUDIT / "worklist-150.tsv", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    assert [int(r["k"]) for r in rows] == list(range(150))
    assert [int(r["idx"]) for r in rows] == sample_audit.compute()["sample_150"]


def test_headline_counts_match_the_coding_sets():
    assert len(blind_packet.WRONG) == audit_stats.PRIMARY[0]
    assert len(blind_packet.WRONG | blind_packet.RIGHT) == audit_stats.PRIMARY[1]
    dropped = {68, 131, 138, 25, 51}
    assert dropped <= blind_packet.WRONG
    assert len(blind_packet.WRONG - dropped) == audit_stats.SENSITIVITY[0]
    assert len((blind_packet.WRONG | blind_packet.RIGHT) - dropped) == audit_stats.SENSITIVITY[1]
    assert len(blind_packet.INACCESSIBLE) == 150 - 124
    assert len(blind_packet.RATIONALISED) == 9


@pytest.mark.parametrize("k, n, lo, hi", [(25, 32, 0.612, 0.890), (20, 27, 0.553, 0.868)])
def test_wilson_intervals_in_the_paper(k, n, lo, hi):
    a, b = audit_stats.wilson(k, n)
    assert (a, b) == pytest.approx((lo, hi), abs=0.0005)


def test_wilson_rejects_bad_input():
    with pytest.raises(ValueError):
        audit_stats.wilson(5, 4)
