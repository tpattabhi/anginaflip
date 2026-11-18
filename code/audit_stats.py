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


# Primary analysis and sensitivity analysis (drops k68, k131, k138, k25, k51).
PRIMARY = (25, 32)
SENSITIVITY = (20, 27)

if __name__ == "__main__":
    for name, (k, n) in {"primary": PRIMARY, "sensitivity": SENSITIVITY}.items():
        lo, hi = wilson(k, n)
        print(f"{name}: {k}/{n} = {k / n:.1%} [{lo:.1%}, {hi:.1%}]")
