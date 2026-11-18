"""Prompt construction and evaluation for the AnginaFlip LLM label probe.

See PROTOCOL-llm-probe.md. This module has no model dependency, so it can be tested
locally; the Colab notebook adds the model scoring.
"""

from __future__ import annotations

import io
import math
import zipfile

import numpy as np
import pandas as pd

COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "num",
]

# UCI documentation for cp (heart-disease.names, attribute 9).
CP_DOCUMENTED = {1: "typical angina", 2: "atypical angina", 3: "non-anginal pain", 4: "asymptomatic"}

CONDITIONS = ("D", "C", "O")
TEMPLATES = ("full", "minimal")

QUESTION = (
    "Does this patient have coronary artery disease, defined as more than 50% narrowing "
    "of a major coronary artery on angiography? Answer Yes or No."
)
INTRO = "The following describes a patient referred for coronary angiography at a US hospital in the 1980s."

RESTECG = {0: "normal", 1: "ST-T wave abnormality", 2: "probable or definite left ventricular hypertrophy"}
SLOPE = {1: "upsloping", 2: "flat", 3: "downsloping"}
THAL = {3: "normal", 6: "fixed defect", 7: "reversible defect"}


def load_uci(zip_path: str, member: str = "processed.cleveland.data") -> pd.DataFrame:
    """Read one processed UCI file from the original archive; adds the binary outcome `cad`."""
    with zipfile.ZipFile(zip_path) as z:
        raw = z.read(member).decode("latin-1")
    df = pd.read_csv(io.StringIO(raw), header=None, names=COLUMNS, na_values="?")
    df = df.dropna(subset=["cp", "num"]).reset_index(drop=True)
    df["cp"] = df["cp"].astype(int)
    df["cad"] = (df["num"] > 0).astype(int)
    return df


def cp_text(code: int, condition: str) -> str | None:
    """Chest-pain wording for a code under condition D (documented), C (corrected) or O (omitted)."""
    if condition == "D":
        return CP_DOCUMENTED[code]
    if condition == "C":
        return CP_DOCUMENTED[5 - code]
    if condition == "O":
        return None
    raise ValueError(f"unknown condition {condition!r}")


def _num(x, fmt="{:.0f}", unit=""):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "unknown"
    return fmt.format(x) + unit


def _cat(x, mapping):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "unknown"
    return mapping.get(int(x), "unknown")


def patient_lines(row: pd.Series, condition: str, template: str) -> list[str]:
    """The predictor lines of one patient, in clinical words."""
    if template not in TEMPLATES:
        raise ValueError(f"unknown template {template!r}")
    lines = [f"Age: {_num(row['age'], unit=' years')}", f"Sex: {_cat(row['sex'], {0: 'female', 1: 'male'})}"]
    cp = cp_text(int(row["cp"]), condition)
    if cp is not None:
        lines.append(f"Chest pain type: {cp}")
    if template == "minimal":
        return lines
    lines += [
        f"Resting blood pressure: {_num(row['trestbps'], unit=' mm Hg')}",
        f"Serum cholesterol: {_num(row['chol'], unit=' mg/dl')}",
        f"Fasting blood sugar above 120 mg/dl: {_cat(row['fbs'], {0: 'no', 1: 'yes'})}",
        f"Resting electrocardiogram: {_cat(row['restecg'], RESTECG)}",
        f"Maximum heart rate during exercise test: {_num(row['thalach'], unit=' beats per minute')}",
        f"Exercise-induced angina: {_cat(row['exang'], {0: 'no', 1: 'yes'})}",
        f"ST depression induced by exercise relative to rest: {_num(row['oldpeak'], fmt='{:.1f}', unit=' mm')}",
        f"Slope of the peak exercise ST segment: {_cat(row['slope'], SLOPE)}",
        f"Number of major vessels colored by fluoroscopy: {_num(row['ca'])}",
        f"Thallium stress scan: {_cat(row['thal'], THAL)}",
    ]
    return lines


def build_prompt(row: pd.Series, condition: str, template: str) -> str:
    """The full user message for one patient."""
    return "\n".join([INTRO, "", *patient_lines(row, condition, template), "", QUESTION])


def build_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (patient, condition, template) with its prompt."""
    rows = []
    for i, r in df.iterrows():
        for t in TEMPLATES:
            for c in CONDITIONS:
                rows.append(
                    {
                        "pid": i,
                        "template": t,
                        "condition": c,
                        "cp": int(r["cp"]),
                        "cad": int(r["cad"]),
                        "prompt": build_prompt(r, c, t),
                    }
                )
    return pd.DataFrame(rows)


def p_yes(logit_yes: np.ndarray, logit_no: np.ndarray) -> np.ndarray:
    """P(Yes) renormalised over the two answer tokens."""
    return 1.0 / (1.0 + np.exp(np.asarray(logit_no) - np.asarray(logit_yes)))


def auc(y: np.ndarray, p: np.ndarray) -> float:
    """Area under the ROC curve (Mann-Whitney, ties counted as half)."""
    y, p = np.asarray(y), np.asarray(p)
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(gt / (len(pos) * len(neg)))


def log_loss(y: np.ndarray, p: np.ndarray, eps: float = 1e-6) -> float:
    p = np.clip(np.asarray(p, dtype=float), eps, 1 - eps)
    y = np.asarray(y)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


METRICS = {"auc": auc, "log_loss": log_loss, "brier": brier}


def paired_bootstrap(y, p_a, p_b, metric, n_boot: int = 2000, seed: int = 20261117) -> dict:
    """metric(p_a) - metric(p_b) with a 95% percentile interval, resampling patients."""
    y, p_a, p_b = map(np.asarray, (y, p_a, p_b))
    rng = np.random.default_rng(seed)
    n = len(y)
    diffs = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        diffs[b] = metric(y[idx], p_a[idx]) - metric(y[idx], p_b[idx])
    return {
        "diff": metric(y, p_a) - metric(y, p_b),
        "lo": float(np.nanpercentile(diffs, 2.5)),
        "hi": float(np.nanpercentile(diffs, 97.5)),
    }


def summarise(scored: pd.DataFrame) -> pd.DataFrame:
    """Per model and template: metrics by condition, and C-minus-D differences with intervals.

    `scored` needs columns model, template, condition, pid, cad, cp, p_yes.
    """
    out = []
    for (model, template), g in scored.groupby(["model", "template"]):
        wide = g.pivot_table(index=["pid", "cad"], columns="condition", values="p_yes").reset_index()
        y = wide["cad"].to_numpy()
        rec = {"model": model, "template": template, "n": len(wide)}
        for c in CONDITIONS:
            for name, f in METRICS.items():
                rec[f"{name}_{c}"] = f(y, wide[c].to_numpy())
        for name, f in METRICS.items():
            bs = paired_bootstrap(y, wide["C"].to_numpy(), wide["D"].to_numpy(), f)
            rec[f"d_{name}_C_minus_D"], rec[f"d_{name}_lo"], rec[f"d_{name}_hi"] = bs["diff"], bs["lo"], bs["hi"]
        out.append(rec)
    return pd.DataFrame(out)


def mean_p_by_code(scored: pd.DataFrame) -> pd.DataFrame:
    """Mean P(Yes) by UCI chest-pain code under each condition (hypothesis H3)."""
    return scored.groupby(["model", "template", "condition", "cp"])["p_yes"].mean().unstack("cp").reset_index()
