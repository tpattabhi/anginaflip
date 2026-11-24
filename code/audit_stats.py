"""Headline statistics of the E8 literature audit (Section 4 of the paper)."""

from math import sqrt


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion k/n."""
    if n <= 0 or not 0 <= k <= n:
        raise ValueError("need 0 <= k <= n and n > 0")
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return center - half, center + half


# Refinement defined after coding (v4): inconsistent statements attributable to the documented labels
# (all 25 except k44 and k98, outcome reversal in a Kaggle copy, and k51, idiosyncratic mapping).
# Derived row by row in evidence/literature-audit/direction-stating-32.tsv (code/audit_table.py).
ATTRIBUTABLE = (22, 32)
# Pre-specified primary outcome: all inconsistent statements, including k44, k51 and k98.
PRIMARY = (25, 32)
# Sensitivity analysis (drops k68, k131, k138, k25, k51), and the same criteria
# applied symmetrically to the correct-sounding statements (also drops k110).
SENSITIVITY = (20, 27)
SENSITIVITY_SYMMETRIC = (20, 26)
# Sensitivity on the attributable estimand (k44 and k98 removed from the 20 retained).
SENSITIVITY_ATTRIBUTABLE = (18, 27)
SENSITIVITY_ATTRIBUTABLE_SYMMETRIC = (18, 26)

if __name__ == "__main__":
    for name, (k, n) in {
        "attributable": ATTRIBUTABLE,
        "primary": PRIMARY,
        "sensitivity": SENSITIVITY,
        "sensitivity_symmetric": SENSITIVITY_SYMMETRIC,
        "sensitivity_attributable": SENSITIVITY_ATTRIBUTABLE,
        "sensitivity_attributable_symmetric": SENSITIVITY_ATTRIBUTABLE_SYMMETRIC,
    }.items():
        lo, hi = wilson(k, n)
        print(f"{name}: {k}/{n} = {k / n:.1%} [{lo:.1%}, {hi:.1%}]")
