"""Consolidate the 32 direction-stating papers of the literature audit into one table.

Sources (later ones override earlier ones for the same k):
  evidence/literature-audit/pilot40-coding.md          (k 0-39, pilot coding)
  evidence/literature-audit/coding-80-149-and-retries.tsv (k 40-149 and retries)
  evidence/literature-audit/round3-access-notes.md     (round 3: newly accessed papers)
Writes evidence/literature-audit/direction-stating-32.tsv.

Sensitivity columns (Section 4 of the paper):
  in_sensitivity_set_27  main sensitivity set: all 32 minus the five dropped inconsistent statements
                         (k68, k131, k138, k25, k51); gives 18 of 27 attributable and 20 of 27 inconsistent.
  in_sensitivity_set_26  the same criteria applied to the correct-sounding statements as well, which also
                         drops k110; gives 18 of 26 attributable.
Run: uv run python code/audit_table.py
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "evidence" / "literature-audit"
OUT = AUDIT / "direction-stating-32.tsv"

# Not caused by the documented labels (see the paper, Section 4).
OTHER_CAUSE = {
    44: "outcome reversal in a Kaggle copy",
    51: "own mapping (ASY = type 2)",
    98: "outcome reversal in the Kaggle 1,025 copy",
}
# Year as given by the full text where the Scholar listing is wrong (k51: listed 2030, full text 2025; k123: 2011 read from its arXiv ID 2011.03195, paper 2020).
YEAR_FIX = {51: "2025", 123: "2020"}
# Copy as identified from the paper itself where the coding sheet was imprecise
# (k123: Dave et al. 2020, footnote 3, kaggle.com/cherngs/heart-disease-cleveland-uci, 297 rows, code = UCI - 1).
COPY_FIX = {123: "Kaggle cherngs 297 (UCI codes minus 1)"}
# Copy group used for the by-copy breakdown in Section 4.
UCI_LABELS, FEDESORIANO, RECODED, UNIDENTIFIED = (
    "UCI codes or labels (incl. 1,190-row merges, Statlog)",
    "fedesoriano 918 (ASY/TA words)",
    "recoded Kaggle copy (cp 0-3)",
    "copy not identified",
)
COPY_GROUP = {
    **dict.fromkeys([1, 16, 18, 21, 25, 46, 54, 68, 85, 93, 96, 111, 131, 138], UCI_LABELS),
    **dict.fromkeys([23, 29, 36, 63, 65, 117], FEDESORIANO),
    **dict.fromkeys([20, 44, 51, 88, 98, 106, 123, 144], RECODED),
    **dict.fromkeys([17, 57, 81, 110], UNIDENTIFIED),
}
# Dropped in the sensitivity analysis (hedged, illustrative, single-patient, mixed, inconsistently mapped).
SENSITIVITY_DROP_27 = {68, 131, 138, 25, 51}  # inconsistent statements only (main sensitivity set)
SENSITIVITY_DROP_26 = SENSITIVITY_DROP_27 | {110}  # criteria also applied to correct-sounding statements


def _verdict(cell: str) -> str | None:
    cell = cell.replace("*", "").strip()
    if cell.startswith("No"):
        return "inconsistent"
    if cell.startswith("Yes"):
        return "correct-sounding"
    return None


def _md_rows(path: Path, correct_col: int, rat_col: int | None, claim_col: int, copy_col: int, venue_col: int):
    for line in path.read_text().splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        v = _verdict(cells[correct_col]) if len(cells) > correct_col else None
        if v:
            rat = cells[rat_col].replace("*", "").strip() if rat_col is not None and len(cells) > rat_col else ""
            yield int(cells[0]), {
                "venue": cells[venue_col],
                "copy": cells[copy_col],
                "claim": cells[claim_col],
                "verdict": v,
                "rationalised": rat,
            }


def build() -> list[dict]:
    rows: dict[int, dict] = {}
    for k, r in _md_rows(AUDIT / "pilot40-coding.md", 6, 7, 5, 3, 2):
        rows[k] = r
    with open(AUDIT / "coding-80-149-and-retries.tsv", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            v = _verdict(r["clinically_correct"])
            if v:
                rows[int(r["k"])] = {
                    "venue": r["venue"],
                    "copy": r["copy"],
                    "claim": r["claim_verbatim"].replace("\\\\", "").replace('\\"', '"'),
                    "verdict": v,
                    "rationalised": r["rationalised"],
                }
    for k, r in _md_rows(AUDIT / "round3-access-notes.md", 6, 7, 4, 3, 1):
        rows[k] = r
    titles = {}
    with open(AUDIT / "worklist-150.tsv", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            titles[int(r["k"])] = (r["title"].strip('" '), r["link"], r["year"])
    out = []
    for k in sorted(rows):
        r = rows[k]
        cause = ""
        if r["verdict"] == "inconsistent":
            cause = OTHER_CAUSE.get(k, "documented labels")
        title, link, year = titles.get(k, ("", "", ""))
        year = YEAR_FIX.get(k, year)
        if k in COPY_FIX:
            r["copy"] = COPY_FIX[k]
        out.append(
            {
                "k": k,
                "year": year,
                "title": title,
                "link": link,
                **r,
                "cause": cause,
                "copy_group": COPY_GROUP[k],
                "in_sensitivity_set_27": "no" if k in SENSITIVITY_DROP_27 else "yes",
                "in_sensitivity_set_26": "no" if k in SENSITIVITY_DROP_26 else "yes",
            }
        )
    return out


if __name__ == "__main__":
    table = build()
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=list(table[0]), delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, escapechar="\\"
        )
        w.writeheader()
        w.writerows(table)
    inc = [r for r in table if r["verdict"] == "inconsistent"]
    doc = [r for r in inc if r["cause"] == "documented labels"]
    rat = [r for r in doc if r["rationalised"].lower().startswith("yes")]
    sens = [r for r in table if r["in_sensitivity_set_26"] == "yes"]
    print(
        f"direction-stating {len(table)}; inconsistent {len(inc)}; attributable {len(doc)}; rationalised among attributable {len(rat)}"
    )
    print(
        f"sensitivity set {len(sens)}; inconsistent {sum(r['verdict']=='inconsistent' for r in sens)}; attributable {sum(r['cause']=='documented labels' for r in sens)}"
    )
    print("k list:", [r["k"] for r in table])
