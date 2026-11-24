"""Consolidate the 32 direction-stating papers of the literature audit into one table.

Sources (later ones override earlier ones for the same k):
  evidence/literature-audit/pilot40-coding.md          (k 0-39, pilot coding)
  evidence/literature-audit/coding-80-149-and-retries.tsv (k 40-149 and retries)
  evidence/literature-audit/round3-access-notes.md     (round 3: newly accessed papers)
Writes evidence/literature-audit/direction-stating-32.tsv.
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
# Year as given by the full text where the Scholar listing is wrong (k51: listed 2030, full text 2025).
YEAR_FIX = {51: "2025"}
# Dropped in the sensitivity analysis (hedged, illustrative, single-patient, mixed, inconsistently mapped).
SENSITIVITY_DROP = {68, 131, 138, 25, 51, 110}


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
        out.append(
            {
                "k": k,
                "year": year,
                "title": title,
                "link": link,
                **r,
                "cause": cause,
                "in_sensitivity_set": "no" if k in SENSITIVITY_DROP else "yes",
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
    sens = [r for r in table if r["in_sensitivity_set"] == "yes"]
    print(
        f"direction-stating {len(table)}; inconsistent {len(inc)}; attributable {len(doc)}; rationalised among attributable {len(rat)}"
    )
    print(
        f"sensitivity set {len(sens)}; inconsistent {sum(r['verdict']=='inconsistent' for r in sens)}; attributable {sum(r['cause']=='documented labels' for r in sens)}"
    )
    print("k list:", [r["k"] for r in table])
