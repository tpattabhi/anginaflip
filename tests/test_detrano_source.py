"""The Detrano et al. 1986 values hard-coded in code/evidence_checks.py, checked against the published PDF.

The PDF is not redistributed (see .gitignore). Put it at the path below to run these tests; otherwise they skip.
"""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import evidence_checks as ec  # noqa: E402

PDF = ROOT / "evidence" / "detrano1986" / "detrano1986_circulation_73-5-970.pdf"
NUM = r"-?\d+(?:\.\d+)?"


@pytest.fixture(scope="module")
def text():
    if not PDF.exists():
        pytest.skip("Detrano 1986 PDF not present (not redistributed)")
    from pypdf import PdfReader

    raw = "".join((p.extract_text() or "") for p in PdfReader(str(PDF)).pages)
    return re.sub(r"\s+", "", raw)


def _between(text: str, start: str, end: str) -> str:
    i = text.index(start)
    return text[i : text.index(end, i)]


def test_table1_percentages_and_group_sizes(text):
    block = _between(text, "TABLE1", "CAD=coronary").replace("+", "±")
    rows = {
        (1, True): _between(block, "WithCADMen", "Women"),
        (0, True): _between(block, "Women", "WithoutCAD"),
        (1, False): _between(block, "WithoutCADMen", "Women"),
        (0, False): block[block.rindex("Women") :],
    }
    for key, row in rows.items():
        pcts, (n1, n2) = ec.DETRANO_TABLE1[key]
        expected = "".join(f"{a}±\\d+{b}±\\d+" for a, b in pcts)
        tail = re.sub(r"^(WithCAD|WithoutCAD)?(Men|Women)", "", row)
        assert re.match(expected + f"{n1}{n2}", tail), (key, tail)


def test_table2_vessel_counts(text):
    """Group I and group II counts (n/% pairs) appear in row order; the PDF glues SE digits to them."""
    block = _between(text, "TABLE2", "Total")
    group1, group2 = (25, 17, 24, 5), (30, 19, 11, 8)
    pct1, pct2 = (35, 24, 34, 7), (44, 28, 16, 12)
    pos = 0
    for a, pa, b, pb in zip(group1, pct1, group2, pct2):
        for frag in (f"{a}/{pa}", f"{b}/{pb}"):
            pos = block.index(frag, pos) + len(frag)
    assert tuple(a + b for a, b in zip(group1, group2)) == ec.DETRANO_TABLE2_VESSELS


def test_table8_subsets_1_and_8(text):
    block = _between(text, "TABLE8", "Subsets:")

    def row(label: str, end: str) -> list[float]:
        return [float(x) for x in re.findall(r"-?\d\.\d\d", _between(block, label, end)[len(label) :])]

    age = row("Age(continuous)", "Sex")
    sex = row("Sex(male=-1;female1)", "Pain")
    pain = row("Pain(1-4)", "Test")
    const = [float(x) for x in re.findall(r"-?\d\.\d\d", block.split("Constant")[1])]
    st = row("ST(continuous)", "TIl")
    t11 = row("TIl(-1,0,1)", "T12")
    t12 = row("T12(-1,0,1)", "normal")
    cf = row("arteries", "Constant")
    assert (const[0], age[0], sex[0], pain[0]) == ec.DETRANO_TABLE8_SUBSET1
    assert (const[7], age[7], sex[7], pain[7], st[-1], t11[-1], t12[-1], cf[-1]) == ec.DETRANO_TABLE8_SUBSET8
