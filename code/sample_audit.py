"""Screening outcome and the random audit sample for E8 (see PROTOCOL-literature-audit.md)."""

import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "evidence" / "literature-scholar" / "frame-Q1-2026-11-17.tsv"
OUT = ROOT / "evidence" / "literature-audit"

# Title/snippet screening, 17 Nov 2026 (before any full text was read).
EXCLUDED_OFF_TOPIC = [
    19,
    54,
    57,
    66,
    76,
    100,
    123,
    143,
    144,
    176,
    183,
    208,
    221,
    225,
    233,
    239,
    246,
    248,
    249,
    250,
    252,
    254,
    256,
    257,
    261,
    262,
    264,
    265,
    266,
    267,
    268,
]
EXCLUDED_DUPLICATE = {10: 0, 40: 11, 43: 31, 186: 171, 175: 170, 195: 177, 230: 202, 141: 113}
SEED = 20261117


def main():
    rows = list(csv.DictReader(open(FRAME), delimiter="\t", quoting=csv.QUOTE_NONE))
    excluded = set(EXCLUDED_OFF_TOPIC) | set(EXCLUDED_DUPLICATE)
    eligible = [int(r["idx"]) for r in rows if int(r["idx"]) not in excluded]
    order = eligible[:]
    random.Random(SEED).shuffle(order)
    res = {
        "frame": len(rows),
        "excluded_off_topic": len(EXCLUDED_OFF_TOPIC),
        "excluded_duplicate": len(EXCLUDED_DUPLICATE),
        "eligible": len(eligible),
        "random_order": order,
        "pilot_40": order[:40],
        "sample_150": order[:150],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sample.json").write_text(json.dumps(res, indent=1))
    print({k: v for k, v in res.items() if k not in ("random_order", "sample_150")})


if __name__ == "__main__":
    main()
