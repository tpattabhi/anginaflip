"""Build a blinded second-coder packet for the E8 literature audit, and score agreement.

Usage:
    python code/blind_packet.py build   # writes evidence/literature-audit/second-coder/
    python code/blind_packet.py score   # reads the filled form and prints agreement

Form values: states_direction is Y, N or NA (paper could not be read); when it is Y, clinically_correct and
rationalised must each be Y or N. Blank rows count as not yet coded. Anything else stops the scorer with the row named.
"""

import csv
import io
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "evidence" / "literature-audit"
OUT = AUDIT / "second-coder"
SEED = 20261118
N_OTHERS = 20

# Primary coder's codes (from audit-150-summary.md and round3-access-notes.md).
WRONG = {1, 17, 18, 20, 21, 29, 36, 46, 54, 57, 63, 65, 68, 98, 106, 117, 123, 131, 138, 93, 25, 85, 44, 51, 16}
RIGHT = {23, 81, 88, 110, 111, 144, 96}
RATIONALISED = {18, 21, 46, 63, 65, 68, 123, 138, 85}
INACCESSIBLE = {
    50,
    80,
    108,
    116,
    149,
    45,
    86,
    90,
    66,
    4,
    48,
    49,
    79,
    14,
    122,
    7,
    8,
    13,
    53,
    89,
    0,
    30,
    97,
    78,
    119,
    137,
}

# Better links found after the worklist was written (round 3).
LINKS = {
    25: "https://doi.org/10.5281/zenodo.17632137",
    61: "https://doi.org/10.1007/s11227-023-05356-3",
    85: "https://doi.org/10.1111/coin.70130",
    96: "https://doi.org/10.1007/s13369-025-10822-6",
    44: "https://www.diva-portal.org/smash/get/diva2:1454488/FULLTEXT01.pdf",
    51: "https://www.researchgate.net/publication/395935618",
    73: "https://www.researchgate.net/publication/417774254",
    77: "https://www.researchgate.net/publication/398902121",
    118: "https://www.researchgate.net/publication/404698952",
    120: "https://www.researchgate.net/publication/406394416",
    141: "https://www.researchgate.net/publication/404398560",
    95: "https://www.warse.org/IJATCSE/static/pdf/file/ijatcse101132022.pdf",
    145: "https://link.springer.com/article/10.1007/s44196-026-01553-z",
    93: "https://www.biorxiv.org/content/10.1101/2025.03.20.644456v1.full",
    136: "https://www.medrxiv.org/content/10.1101/2025.09.28.25336834v1.full",
    147: "https://www.medrxiv.org/content/10.1101/2025.08.03.25332878v1.full",
    112: "https://doi.org/10.1177/10711813241264252",
    16: "https://www.sciencedirect.com/science/article/pii/S0169023X24000636",
    102: "https://www.sciencedirect.com/science/article/pii/S2772442525000462",
    11: "https://www.sciencedirect.com/science/article/pii/S2666521226000104",
}

FORM_COLS = [
    "pid",
    "title",
    "link",
    "copy",
    "states_direction",
    "category_named",
    "direction",
    "clinically_correct",
    "rationalised",
    "quote",
    "notes",
]


def primary_code(k: int) -> str:
    """Three-way primary outcome: wrong / right / none."""
    if k in WRONG:
        return "wrong"
    if k in RIGHT:
        return "right"
    return "none"


def load_worklist() -> dict[int, dict]:
    with open(AUDIT / "worklist-150.tsv", newline="") as f:
        # Titles contain stray double quotes, so quoting must be off.
        rows = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        return {int(r["k"]): r for r in rows}


def select(ks: list[int], seed: int = SEED, n_others: int = N_OTHERS) -> list[int]:
    """All direction-stating items plus a seeded random sample of other accessible items, shuffled."""
    accessible = [k for k in ks if k not in INACCESSIBLE]
    stating = [k for k in accessible if k in WRONG or k in RIGHT]
    others = sorted(k for k in accessible if k not in WRONG and k not in RIGHT)
    rng = random.Random(seed)
    chosen = stating + rng.sample(others, n_others)
    rng.shuffle(chosen)
    return chosen


def build() -> None:
    wl = load_worklist()
    chosen = select(sorted(wl))
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "form.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(FORM_COLS)
        for i, k in enumerate(chosen, 1):
            r = wl[k]
            link = LINKS.get(k, r["link"])
            w.writerow([f"P{i:02d}", r["title"], link] + [""] * (len(FORM_COLS) - 3))
    with open(OUT / "KEY-do-not-open-until-done.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["pid", "k", "primary", "rationalised"])
        for i, k in enumerate(chosen, 1):
            w.writerow([f"P{i:02d}", k, primary_code(k), "yes" if k in RATIONALISED else "no"])
    print(f"wrote {len(chosen)} items to {OUT}")


YES, NO, NOT_READ = {"y", "yes"}, {"n", "no"}, {"na", "n/a"}
# Copy groups as in Section 4 of the paper and the copy_group column of direction-stating-32.tsv.
UCI, FEDESORIANO, RECODED, UNIDENTIFIED = "uci", "fedesoriano", "recoded", "unidentified"
TABLE_GROUP = {
    "UCI codes or labels (incl. 1,190-row merges, Statlog)": UCI,
    "fedesoriano 918 (ASY/TA words)": FEDESORIANO,
    "recoded Kaggle copy (cp 0-3)": RECODED,
    "copy not identified": UNIDENTIFIED,
}


class FormError(ValueError):
    """The filled form has a missing row or a value the scorer cannot read."""


def _cell(row: dict, col: str) -> str:
    return (row.get(col) or "").strip()


def coder_primary(row: dict) -> str | None:
    """Second coder's three-way outcome (wrong / right / none); None if the paper was not read or not yet coded.

    Raises FormError for values that would otherwise be misread silently.
    """
    sd = _cell(row, "states_direction").lower()
    if not sd or sd in NOT_READ:
        return None
    if sd in NO:
        return "none"
    if sd not in YES:
        raise FormError(
            f"{row.get('pid')}: states_direction must be Y, N or NA, got {_cell(row, 'states_direction')!r}"
        )
    cc = _cell(row, "clinically_correct").lower()
    if cc in YES:
        return "right"
    if cc in NO:
        return "wrong"
    raise FormError(
        f"{row.get('pid')}: states_direction is Y, so clinically_correct must be Y or N, "
        f"got {_cell(row, 'clinically_correct')!r}"
    )


def coder_rationalised(row: dict) -> str:
    """'yes' or 'no' for a direction-stating row; raises FormError if the value is missing or unreadable."""
    r = _cell(row, "rationalised").lower()
    if r in YES:
        return "yes"
    if r in NO:
        return "no"
    raise FormError(
        f"{row.get('pid')}: states_direction is Y, so rationalised must be Y or N, got {_cell(row, 'rationalised')!r}"
    )


def copy_group(text: str) -> str:
    """Map the second coder's free-text copy onto the paper's four copy groups (checked in this order)."""
    t = text.lower().replace("\u2013", "-").replace(",", "")
    if not t or "unclear" in t or "?" in t:
        return UNIDENTIFIED
    if "918" in t or "fedesoriano" in t or "ata" in t.replace("/", " ").split():
        return FEDESORIANO
    if any(w in t for w in ("1190", "statlog", "270", "920")):
        return UCI
    if any(w in t for w in ("1025", "0-3", "cherngs", "minus 1")) or ("kaggle" in t and ("303" in t or "297" in t)):
        return RECODED
    if any(w in t for w in ("303", "297", "uci", "cleveland")):
        return UCI
    return UNIDENTIFIED


def cohen_kappa(a: list[str], b: list[str]) -> float:
    """Cohen's kappa; NaN when both raters use a single, identical class (kappa is undefined)."""
    if len(a) != len(b) or not a:
        raise ValueError("need two equal-length, non-empty label lists")
    n = len(a)
    labels = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(lab) / n) * (b.count(lab) / n) for lab in labels)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def _decode(raw: bytes) -> str:
    # UTF-16 ("Unicode Text") and UTF-8 with or without a byte-order mark; otherwise Latin-1, which never fails.
    # The scored columns are ASCII, so a wrong guess can only garble titles or quotes, not codes.
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def load_form(path: Path, pids: list[str]) -> dict[str, dict]:
    """Read the filled form; header names and pids are normalised, and every problem is reported at once."""
    # io.StringIO with newline="" splits rows only on CR/LF; str.splitlines would also split on U+0085, U+2028 etc.,
    # which appear in titles (cp1252 "…" decoded as Latin-1, or text pasted from PDFs).
    reader = csv.DictReader(io.StringIO(_decode(path.read_bytes()), newline=""), delimiter="\t", restval="")
    reader.fieldnames = [(h or "").strip().lower() for h in reader.fieldnames or []]
    errors, form = [], {}
    if "pid" not in reader.fieldnames:
        raise FormError(f"form has no 'pid' column; header is {reader.fieldnames}")
    for row in reader:
        pid = _cell(row, "pid").upper()
        if not pid:
            if any(_cell(row, c) for c in row if c):
                errors.append(f"a row with content has no pid: {[_cell(row, c) for c in row if c][:3]}")
            continue
        if pid in form:
            errors.append(f"{pid}: appears more than once")
        row["pid"] = pid
        form[pid] = row
    missing = [p for p in pids if p not in form]
    extra = [p for p in form if p not in pids]
    if missing or extra:
        errors.append(f"rows do not match the key: missing {missing}, unexpected {extra}")
    for pid, row in form.items():
        try:
            if coder_primary(row) not in (None, "none"):
                coder_rationalised(row)
        except FormError as e:
            errors.append(str(e))
    if errors:
        raise FormError("form problems:\n  " + "\n  ".join(errors))
    return form


def form_warnings(form: dict[str, dict]) -> list[str]:
    """Rows that will be scored but look half-finished."""
    out = []
    for pid, row in form.items():
        sd = _cell(row, "states_direction").lower()
        filled = [c for c in ("clinically_correct", "rationalised", "category_named", "direction") if _cell(row, c)]
        if not sd and filled:
            out.append(f"{pid}: states_direction is blank but {filled} are filled; counted as not yet coded")
        if (sd in NO or sd in NOT_READ) and _cell(row, "clinically_correct"):
            out.append(f"{pid}: states_direction is {sd.upper()} but clinically_correct is filled; ignored")
    return out


def _agreement(label: str, a: list[str], b: list[str]) -> None:
    if not a:
        print(f"{label}: no items")
        return
    agree = sum(x == y for x, y in zip(a, b))
    k = cohen_kappa(a, b)
    ks = "kappa undefined (one class)" if k != k else f"kappa {k:.2f}"
    print(f"{label}: {agree}/{len(a)} agree; {ks}")


def _share(label: str, k: int, n: int) -> None:
    from audit_stats import wilson  # same interval as the paper

    if n:
        lo, hi = wilson(k, n)
        print(f"  {label}: {k} of {n} ({100 * k / n:.0f}%; 95% CI {100 * lo:.0f}-{100 * hi:.0f}%)")
    else:
        print(f"  {label}: no items")


def score() -> None:
    from audit_table import OTHER_CAUSE, SENSITIVITY_DROP_26, SENSITIVITY_DROP_27

    with open(OUT / "KEY-do-not-open-until-done.tsv", newline="") as f:
        key = {r["pid"]: r for r in csv.DictReader(f, delimiter="\t")}
    form = load_form(OUT / "form.tsv", list(key))
    with open(AUDIT / "direction-stating-32.tsv", newline="") as f:
        table = {int(r["k"]): r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
    kk = {p: int(key[p]["k"]) for p in key}

    for w in form_warnings(form):
        print("warning:", w)
    second = {p: coder_primary(form[p]) for p in key}
    first = {p: key[p]["primary"] for p in key}
    coded = [p for p in key if second[p] is not None]
    not_read = [p for p in key if _cell(form[p], "states_direction").lower() in NOT_READ]
    print(f"coded {len(coded)}/{len(key)}; marked not read (NA): {len(not_read)} {not_read}")
    print("Every figure below uses only the coded items, for both coders.")

    print("\nAgreement")
    _agreement("three-way outcome (pre-specified)", [first[p] for p in coded], [second[p] for p in coded])
    yn = {"none": "no", "wrong": "yes", "right": "yes"}
    _agreement("states a direction", [yn[first[p]] for p in coded], [yn[second[p]] for p in coded])
    both = [p for p in coded if first[p] != "none" and second[p] != "none"]
    _agreement("verdict, inconsistent or not (both stating)", [first[p] for p in both], [second[p] for p in both])
    # Rationalised: the paper's figure is "nine of the 22", among attributable inconsistent statements,
    # so compare on items both coders call inconsistent and the primary coding attributes to the labels.
    rat_items = [p for p in both if first[p] == second[p] == "wrong" and kk[p] not in OTHER_CAUSE]
    rat_a = [key[p]["rationalised"] for p in rat_items]
    rat_b = [coder_rationalised(form[p]) for p in rat_items]
    _agreement("rationalised (both inconsistent, attributable)", rat_a, rat_b)
    # Copy group: only where the second coder entered a copy (a blank cell is not a disagreement).
    in_table = [p for p in coded if kk[p] in table and _cell(form[p], "copy")]
    blank_copy = [p for p in coded if kk[p] in table and not _cell(form[p], "copy")]
    if blank_copy:
        print(f"copy left blank for {len(blank_copy)} primary direction-stating items (excluded): {blank_copy}")
    grp_a = [TABLE_GROUP[table[kk[p]]["copy_group"]] for p in in_table]
    grp_b = [copy_group(_cell(form[p], "copy")) for p in in_table]
    _agreement("copy group (primary direction-stating items)", grp_a, grp_b)

    print("\nFigures, primary vs second coder (same items)")
    print("  Verdicts are each coder's own. Cause (other than the labels) and the sensitivity exclusions are the")
    print("  primary coder's judgements, applied to both, because the form does not code them.")
    for who, codes in (("primary", first), ("second", second)):
        stating = [p for p in coded if codes[p] != "none"]
        wrong = [p for p in stating if codes[p] == "wrong"]
        attributable = [p for p in wrong if kk[p] not in OTHER_CAUSE]
        print(f" [{who} coder]")
        _share("inconsistent / direction-stating (paper: 25 of 32)", len(wrong), len(stating))
        _share("attributable / direction-stating (paper: 22 of 32)", len(attributable), len(stating))
        for label, drop, paper_inc, paper_att in (
            ("sensitivity set 27", SENSITIVITY_DROP_27, "20 of 27", "18 of 27"),
            ("sensitivity set 26", SENSITIVITY_DROP_26, "20 of 26", "18 of 26"),
        ):
            subset = [p for p in stating if kk[p] not in drop]
            w = [p for p in subset if codes[p] == "wrong"]
            _share(f"{label}: inconsistent (paper: {paper_inc})", len(w), len(subset))
            _share(
                f"{label}: attributable (paper: {paper_att})",
                len([p for p in w if kk[p] not in OTHER_CAUSE]),
                len(subset),
            )
        if who == "primary":
            rats = [p for p in attributable if key[p]["rationalised"] == "yes"]
        else:
            rats = [p for p in attributable if coder_rationalised(form[p]) == "yes"]
        print(f"  rationalised among attributable (paper: 9 of 22): {len(rats)} of {len(attributable)}")
    print(
        "  Note: items the second coder calls direction-stating that the primary coder did not are counted as"
        " attributable unless they are in the primary coder's other-cause list; review them in the list below."
    )

    print("\nDisagreements, for joint review")
    for p in coded:
        if first[p] != second[p]:
            print(f"  outcome {p} (k{kk[p]}): primary={first[p]} second={second[p]}")
    for p, x, y in zip(rat_items, rat_a, rat_b):
        if x != y:
            print(f"  rationalised {p} (k{kk[p]}): primary={x} second={y}")
    for p, x, y in zip(in_table, grp_a, grp_b):
        if x != y:
            print(f"  copy {p} (k{kk[p]}): primary={table[kk[p]]['copy']!r} second={_cell(form[p], 'copy')!r}")


if __name__ == "__main__":
    {"build": build, "score": score}[sys.argv[1]]()
