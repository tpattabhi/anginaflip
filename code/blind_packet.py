"""Build a blinded second-coder packet for the E8 literature audit, and score agreement.

Usage:
    python code/blind_packet.py build   # writes evidence/literature-audit/second-coder/
    python code/blind_packet.py score   # reads the filled form and prints agreement
"""

import csv
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


def coder_primary(row: dict) -> str:
    sd = row["states_direction"].strip().lower()
    if sd not in {"y", "yes"}:
        return "none"
    cc = row["clinically_correct"].strip().lower()
    return "right" if cc in {"y", "yes"} else "wrong"


def cohen_kappa(a: list[str], b: list[str]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("need two equal-length, non-empty label lists")
    n = len(a)
    labels = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(lab) / n) * (b.count(lab) / n) for lab in labels)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def score() -> None:
    with open(OUT / "form.tsv", newline="") as f:
        form = {r["pid"]: r for r in csv.DictReader(f, delimiter="\t")}
    with open(OUT / "KEY-do-not-open-until-done.tsv", newline="") as f:
        key = {r["pid"]: r for r in csv.DictReader(f, delimiter="\t")}
    done = [p for p in key if form[p]["states_direction"].strip()]
    a = [key[p]["primary"] for p in done]
    b = [coder_primary(form[p]) for p in done]
    agree = sum(x == y for x, y in zip(a, b))
    print(f"coded {len(done)}/{len(key)}; raw agreement {agree}/{len(done)}; kappa {cohen_kappa(a, b):.2f}")
    for p, x, y in zip(done, a, b):
        if x != y:
            print(f"  disagree {p} (k{key[p]['k']}): primary={x} second={y}")


if __name__ == "__main__":
    {"build": build, "score": score}[sys.argv[1]]()
