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


def test_coder_primary_rejects_ambiguous_values():
    assert bp.coder_primary({"pid": "P01", "states_direction": "NA", "clinically_correct": ""}) is None
    assert bp.coder_primary({"pid": "P01", "states_direction": "", "clinically_correct": ""}) is None
    with pytest.raises(bp.FormError):
        bp.coder_primary({"pid": "P01", "states_direction": "Y", "clinically_correct": ""})
    with pytest.raises(bp.FormError):
        bp.coder_primary({"pid": "P01", "states_direction": "maybe", "clinically_correct": "Y"})


def test_primary_sets_match_audit_table():
    import csv

    path = Path(__file__).resolve().parents[1] / "evidence" / "literature-audit" / "direction-stating-32.tsv"
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    assert bp.WRONG == {int(r["k"]) for r in rows if r["verdict"] == "inconsistent"}
    assert bp.RIGHT == {int(r["k"]) for r in rows if r["verdict"] == "correct-sounding"}
    attributable_rat = {
        int(r["k"]) for r in rows if r["cause"] == "documented labels" and r["rationalised"].lower().startswith("yes")
    }
    assert bp.RATIONALISED == attributable_rat


def test_load_form_rejects_missing_rows(tmp_path):
    form = tmp_path / "form.tsv"
    form.write_text("\t".join(bp.FORM_COLS) + "\n" + "P01" + "\t" * (len(bp.FORM_COLS) - 1) + "\n")
    with pytest.raises(bp.FormError):
        bp.load_form(form, ["P01", "P02"])


VOCAB = {
    "uci": "UCI Cleveland 303",
    "fedesoriano": "fedesoriano 918",
    "recoded": "Kaggle 1,025",
    "unidentified": "unclear",
}
KEY_PATH = bp.OUT / "KEY-do-not-open-until-done.tsv"


def _key_rows():
    import csv

    if not KEY_PATH.exists():
        pytest.skip("second-coder key is not distributed")
    with open(KEY_PATH, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _table():
    import csv

    path = bp.AUDIT / "direction-stating-32.tsv"
    with open(path, newline="") as f:
        return {int(r["k"]): r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}


def _write_form(tmp_path, rows, overrides=None, eol="\n"):
    """A form that copies the primary coding exactly, with optional per-pid overrides."""
    table = _table()
    lines = ["\t".join(bp.FORM_COLS)]
    for r in rows:
        k = int(r["k"])
        sd = "N" if r["primary"] == "none" else "Y"
        cc = {"none": "", "wrong": "N", "right": "Y"}[r["primary"]]
        rat = (
            "Y"
            if (r["rationalised"] == "yes" or table.get(k, {}).get("rationalised", "").lower().startswith("yes"))
            else "N"
        )
        copy = VOCAB[bp.TABLE_GROUP[table[k]["copy_group"]]] if k in table else ""
        cells = dict(
            pid=r["pid"], states_direction=sd, clinically_correct=cc, rationalised=rat if sd == "Y" else "", copy=copy
        )
        cells.update((overrides or {}).get(r["pid"], {}))
        lines.append("\t".join(cells.get(c, "") for c in bp.FORM_COLS))
    (tmp_path / "form.tsv").write_text(eol.join(lines) + eol)
    (tmp_path / KEY_PATH.name).write_text(KEY_PATH.read_text())


def _run(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(bp, "OUT", tmp_path)
    bp.score()
    return capsys.readouterr().out


def test_score_perfect_agreement_reproduces_every_figure(tmp_path, monkeypatch, capsys):
    rows = _key_rows()
    _write_form(tmp_path, rows, eol="\r\n")
    out = _run(tmp_path, monkeypatch, capsys)
    assert "coded 52/52" in out
    assert "three-way outcome (pre-specified): 52/52 agree; kappa 1.00" in out
    assert "rationalised (both inconsistent, attributable): 22/22 agree" in out
    for who in ("primary", "second"):
        block = out.split(f"[{who} coder]")[1].split("[second coder]")[0]
        assert "inconsistent / direction-stating (paper: 25 of 32): 25 of 32 (78%; 95% CI 61-89%)" in block
        assert "attributable / direction-stating (paper: 22 of 32): 22 of 32 (69%; 95% CI 51-82%)" in block
        assert "sensitivity set 27: inconsistent (paper: 20 of 27): 20 of 27" in block
        assert "sensitivity set 27: attributable (paper: 18 of 27): 18 of 27" in block
        assert "sensitivity set 26: attributable (paper: 18 of 26): 18 of 26" in block
        assert "sensitivity set 26: inconsistent (paper: 20 of 26): 20 of 26" in block
        assert "rationalised among attributable (paper: 9 of 22): 9 of 22" in block
    assert "outcome P" not in out and "rationalised P" not in out


def test_score_reports_disagreements_and_drops_na_items_for_both_coders(tmp_path, monkeypatch, capsys):
    rows = _key_rows()
    wrong = [r for r in rows if r["primary"] == "wrong"]
    none = [r for r in rows if r["primary"] == "none"]
    flipped, skipped = wrong[0]["pid"], wrong[1]["pid"]
    overrides = {
        flipped: {"clinically_correct": "Y"},
        skipped: {"states_direction": "NA", "clinically_correct": "", "rationalised": ""},
        none[0]["pid"]: {"states_direction": ""},  # not yet coded
    }
    _write_form(tmp_path, rows, overrides)
    out = _run(tmp_path, monkeypatch, capsys)
    assert "coded 50/52; marked not read (NA): 1" in out
    assert f"outcome {flipped} " in out and "primary=wrong second=right" in out
    # the NA item drops out of both coders' figures: 24 of 31 for primary, 23 of 31 for second
    assert out.split("[primary coder]")[1].split("[second coder]")[0].count("24 of 31") >= 1
    assert "23 of 31" in out.split("[second coder]")[1]


def test_load_form_reports_all_problems(tmp_path):
    form = tmp_path / "form.tsv"
    header = "\t".join(bp.FORM_COLS)
    form.write_text(header + "\nP01\tt\tl\t\tY\n" + "P01\n" + "P09\t\t\t\tmaybe\n")  # short rows, duplicate, bad value
    with pytest.raises(bp.FormError) as e:
        bp.load_form(form, ["P01", "P02"])
    msg = str(e.value)
    assert "P01: appears more than once" in msg
    assert "missing ['P02']" in msg and "unexpected ['P09']" in msg
    assert "P09: states_direction must be Y, N or NA" in msg


def test_load_form_short_rows_and_normalised_names(tmp_path):
    form = tmp_path / "form.tsv"
    form.write_text(" PID \tTitle\tStates_Direction \np01\n" + "P02\tx\tN\n")
    got = bp.load_form(form, ["P01", "P02"])
    assert sorted(got) == ["P01", "P02"] and bp.coder_primary(got["P01"]) is None


@pytest.mark.parametrize("encoding", ["utf-16", "latin-1", "utf-8-sig"])
def test_load_form_spreadsheet_encodings(tmp_path, encoding):
    form = tmp_path / "form.tsv"
    text = "\t".join(bp.FORM_COLS) + "\r\nP01\tCaf\u00e9 study\r\n\t\t\r\n"
    form.write_bytes(text.encode(encoding))
    assert list(bp.load_form(form, ["P01"])) == ["P01"]


def test_kappa_single_class_is_undefined(capsys):
    assert bp.cohen_kappa(["a", "a"], ["a", "a"]) != bp.cohen_kappa(["a", "a"], ["a", "a"])  # NaN
    bp._agreement("x", ["a", "a"], ["a", "a"])
    assert "kappa undefined (one class)" in capsys.readouterr().out
    bp._agreement("y", [], [])
    assert "y: no items" in capsys.readouterr().out


def test_copy_group_maps_instruction_vocabulary():
    assert bp.copy_group("UCI Cleveland 303") == bp.UCI
    assert bp.copy_group("the 1,190 merge") == bp.UCI and bp.copy_group("Kaggle 1,190") == bp.UCI
    assert bp.copy_group("Statlog 270") == bp.UCI and bp.copy_group("UCI 4-site 920") == bp.UCI
    assert bp.copy_group("Kaggle 1,025") == bp.RECODED and bp.copy_group("Kaggle 303") == bp.RECODED
    assert bp.copy_group("fedesoriano 918") == bp.FEDESORIANO
    assert bp.copy_group("unclear") == bp.UNIDENTIFIED and bp.copy_group("") == bp.UNIDENTIFIED


def test_rationalised_must_be_coded_for_stating_rows():
    assert bp.coder_rationalised({"pid": "P01", "rationalised": "Y"}) == "yes"
    assert bp.coder_rationalised({"pid": "P01", "rationalised": "no"}) == "no"
    with pytest.raises(bp.FormError):
        bp.coder_rationalised({"pid": "P01", "rationalised": ""})
    with pytest.raises(bp.FormError):
        bp.coder_rationalised({"pid": "P01"})  # short row


@pytest.mark.parametrize(
    "title_bytes",
    [
        "Deep learning\u2026 for heart".encode("cp1252"),
        "\u00d6zt\u00fcrk".encode("mac_roman"),
        "a\u2028b".encode("utf-8"),
    ],
)
def test_load_form_does_not_split_rows_inside_a_cell(tmp_path, title_bytes):
    """cp1252 '...' (0x85), MacRoman 'O-umlaut' (0x85) and U+2028 must not start a new row."""
    form = tmp_path / "form.tsv"
    head = ("\t".join(bp.FORM_COLS) + "\r\nP01\t").encode("ascii")
    form.write_bytes(head + title_bytes + b"\t\t\tN\r\n")
    got = bp.load_form(form, ["P01"])
    assert bp.coder_primary(got["P01"]) == "none"


def test_blank_copy_is_not_a_disagreement(tmp_path, monkeypatch, capsys):
    rows = _key_rows()
    target = next(r["pid"] for r in rows if r["primary"] != "none")
    _write_form(tmp_path, rows, {target: {"copy": ""}})
    out = _run(tmp_path, monkeypatch, capsys)
    assert "copy left blank for 1 primary direction-stating items" in out
    assert "copy group (primary direction-stating items): 31/31 agree" in out


def test_warns_on_na_row_with_verdict(tmp_path):
    form = {"P01": {"pid": "P01", "states_direction": "NA", "clinically_correct": "Y"}}
    assert any("NA but clinically_correct is filled" in w for w in bp.form_warnings(form))
