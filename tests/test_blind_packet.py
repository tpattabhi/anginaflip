import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import blind_packet as bp  # noqa: E402


def test_kappa_perfect_agreement():
    assert bp.cohen_kappa(["wrong", "none", "right"], ["wrong", "none", "right"]) == 1.0


def test_kappa_known_value():
    a = ["y", "y", "n", "n"]
    b = ["y", "n", "n", "n"]
    # po = 0.75; pe = 0.5*0.25 + 0.5*0.75 = 0.5; kappa = 0.5
    assert bp.cohen_kappa(a, b) == pytest.approx(0.5)


def test_kappa_rejects_mismatch():
    with pytest.raises(ValueError):
        bp.cohen_kappa(["a"], ["a", "b"])


def test_selection_has_all_direction_items_and_is_deterministic():
    ks = list(range(150))
    s1 = bp.select(ks)
    s2 = bp.select(ks)
    assert s1 == s2
    stating = (bp.WRONG | bp.RIGHT) - bp.INACCESSIBLE
    assert stating <= set(s1)
    assert len(s1) == len(stating) + bp.N_OTHERS
    assert not set(s1) & bp.INACCESSIBLE


def test_primary_code_sets_are_disjoint():
    assert not bp.WRONG & bp.RIGHT
    assert len(bp.WRONG) == 25 and len(bp.RIGHT) == 7
    assert bp.RATIONALISED <= bp.WRONG


def test_worklist_loads_all_150_rows():
    assert sorted(bp.load_worklist()) == list(range(150))


def test_coder_primary():
    assert bp.coder_primary({"states_direction": "N", "clinically_correct": ""}) == "none"
    assert bp.coder_primary({"states_direction": "Y", "clinically_correct": "N"}) == "wrong"
    assert bp.coder_primary({"states_direction": "yes", "clinically_correct": "yes"}) == "right"
