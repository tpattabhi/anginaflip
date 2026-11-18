"""Checks E1-E4 and E7: is the UCI chest-pain variable (cp) stored in reverse of its documentation?

Every check reads the archived source files in ``evidence/`` and returns plain data, so the
numbers quoted in the paper can be asserted in tests (``tests/test_evidence.py``).

Usage:
    uv run python code/evidence_checks.py            # print every check
    uv run python code/evidence_checks.py --copies   # also check the downloaded Kaggle copies
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
UCI_ZIP = EVIDENCE / "uci-raw-archive" / "heart+disease.zip"
STATLOG = EVIDENCE / "statlog-check" / "heart.dat"
OPENML = EVIDENCE / "openml"
PMLB = EVIDENCE / "pmlb"
KAGGLE = EVIDENCE / "kaggle"

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
PROCESSED = {
    "cleveland": "processed.cleveland.data",
    "hungarian": "processed.hungarian.data",
    "switzerland": "processed.switzerland.data",
    "va": "processed.va.data",
}
RAW = {
    "budapest": "hungarian.data",
    "switzerland": "switzerland.data",
    "long_beach": "long-beach-va.data",
    "cleveland": "cleveland.data",
}
# Positions (1-based) in the 76-attribute raw records, from heart-disease.names.
RAW_FIELDS = {3: "age", 4: "sex", 5: "painloc", 6: "painexer", 7: "relrest", 9: "cp", 58: "num"}


def _read_member(name: str, zip_path: Path = UCI_ZIP) -> str:
    with zipfile.ZipFile(zip_path) as z:
        return z.read(name).decode("latin-1")


def load_processed(site: str = "cleveland", zip_path: Path = UCI_ZIP) -> pd.DataFrame:
    """One of the four 14-attribute processed files, with '?' as missing."""
    text = _read_member(PROCESSED[site], zip_path)
    return pd.read_csv(io.StringIO(text), header=None, names=COLUMNS, na_values="?")


def load_raw(site: str, zip_path: Path = UCI_ZIP) -> tuple[int, pd.DataFrame]:
    """Parse a 76-attribute raw file. Records end with the token 'name'; malformed records are dropped.

    Returns the number of records found and a frame of the fields in ``RAW_FIELDS``.
    """
    tokens = _read_member(RAW[site], zip_path).split()
    records, current = [], []
    for tok in tokens:
        current.append(tok)
        if tok == "name":
            records.append(current)
            current = []
    complete = [r for r in records if len(r) == 76]
    frame = pd.DataFrame([[float(x) for x in r[:75]] for r in complete], columns=range(1, 76))
    return len(records), frame[list(RAW_FIELDS)].rename(columns=RAW_FIELDS)


# --- E1: Cleveland against Detrano et al. 1986 (Circulation 73:970) -------------------------------

# Table 1: row percentages (group I, group II) for [angina pectoris, atypical angina, nonanginal pain,
# no pain], and the two group sizes, keyed by (male, has CAD).
DETRANO_TABLE1 = {
    (1, True): ([(78, 68), (12, 18), (5, 7), (5, 7)], (58, 56)),
    (0, True): ([(100, 75), (0, 8), (0, 17), (0, 0)], (13, 12)),
    (1, False): ([(26, 20), (36, 38), (26, 28), (12, 14)], (42, 50)),
    (0, False): ([(24, 27), (53, 41), (21, 24), (3, 9)], (38, 34)),
}
DETRANO_TABLE2_VESSELS = (55, 36, 35, 13)
DETRANO_TABLE8_SUBSET1 = (-2.29, 0.07, -0.85, -1.10)  # constant, age, sex, pain
# Subset 8 (n = 297): constant, age, sex, pain, ST depression, T11, T12, calcified arteries.
DETRANO_TABLE8_SUBSET8 = (-2.33, 0.02, -0.45, -0.76, 0.65, 0.89, -0.08, 1.04)


def _feasible_counts(pct: float, n: int, tol: float = 0.5) -> set[int]:
    return {k for k in range(n + 1) if abs(100 * k / n - pct) <= tol + 1e-9}


def detrano_table1_consistent(cleveland: pd.DataFrame, mapping: tuple[int, int, int, int]) -> int:
    """Number of the 16 Table 1 cells whose UCI count is consistent with the published percentages.

    ``mapping[i]`` is the stored cp code read as Detrano's category i (typical angina first).
    """
    counts = Counter(zip(cleveland.sex.astype(int), cleveland.num > 0, cleveland.cp.astype(int)))
    consistent = 0
    for (sex, cad), (pcts, (n1, n2)) in DETRANO_TABLE1.items():
        for i, (p1, p2) in enumerate(pcts):
            possible = {a + b for a in _feasible_counts(p1, n1) for b in _feasible_counts(p2, n2)}
            consistent += counts[(sex, cad, mapping[i])] in possible
    return consistent


def logistic_fit(X: np.ndarray, y: np.ndarray, iterations: int = 50) -> np.ndarray:
    """Unpenalised logistic regression by Newton-Raphson; returns [constant, slopes...]."""
    X = np.column_stack([np.ones(len(X)), X])
    beta = np.zeros(X.shape[1])
    for _ in range(iterations):
        p = 1 / (1 + np.exp(-X @ beta))
        beta += np.linalg.solve(X.T @ (X * (p * (1 - p))[:, None]), X.T @ (y - p))
    return beta


def check_detrano1986(zip_path: Path = UCI_ZIP) -> dict:
    cl = load_processed("cleveland", zip_path)
    y = (cl.num > 0).to_numpy(float)
    sex = np.where(cl.sex == 1, -1.0, 1.0)  # Detrano codes male = -1, female = +1
    age, cp = cl.age.to_numpy(float), cl.cp.to_numpy(float)
    # Subset 8 adds ST depression, two thallium contrasts and the number of calcified arteries.
    thal = cl.thal.to_numpy(float)
    t11 = np.select([thal == 3, thal == 6, thal == 7], [-1.0, 0.0, 1.0], np.nan)
    t12 = np.select([thal == 3, thal == 6, thal == 7], [-1.0, 1.0, 0.0], np.nan)
    x8 = np.column_stack([age, sex, 5 - cp, cl.oldpeak, t11, t12, cl.ca])
    complete = ~np.isnan(x8).any(axis=1)
    return {
        "n": len(cl),
        "table1_documented": detrano_table1_consistent(cl, (1, 2, 3, 4)),
        "table1_reversed": detrano_table1_consistent(cl, (4, 3, 2, 1)),
        "table2_vessels": tuple(int((cl.num == k).sum()) for k in (1, 2, 3, 4)),
        "table8_cp_as_stored": tuple(np.round(logistic_fit(np.column_stack([age, sex, cp]), y), 2)),
        "table8_cp_reversed": tuple(np.round(logistic_fit(np.column_stack([age, sex, 5 - cp]), y), 2)),
        "table8_subset8_n": int(complete.sum()),
        "table8_subset8_cp_reversed": tuple(np.round(logistic_fit(x8[complete], y[complete]), 2)),
    }


# --- E2: raw angina features at Budapest, Switzerland and Long Beach --------------------------------


def check_raw_features(zip_path: Path = UCI_ZIP) -> dict[str, pd.DataFrame]:
    """Cross-tab of stored cp against the number of classical angina features (0-3) per site."""
    out = {}
    for site in ("budapest", "switzerland", "long_beach"):
        _, df = load_raw(site, zip_path)
        full = df[(df.painloc >= 0) & (df.painexer >= 0) & (df.relrest >= 0)]
        features = (full.painloc + full.painexer + full.relrest).astype(int)
        out[site] = pd.crosstab(full.cp.astype(int), features).reindex(columns=range(4), fill_value=0)
    return out


# --- E3: cleve.mod (Gennari, 1990) -------------------------------------------------------------------


def load_cleve_mod(zip_path: Path = UCI_ZIP) -> pd.DataFrame:
    rows = [line.split() for line in _read_member("cleve.mod", zip_path).splitlines()]
    rows = [r for r in rows if r and not r[0].startswith("%")]
    frame = pd.DataFrame([r[:14] for r in rows], columns=COLUMNS[:13] + ["cls"])
    for col in ("age", "trestbps", "chol", "thalach"):
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    return frame


def check_cleve_mod(zip_path: Path = UCI_ZIP) -> dict:
    mod = load_cleve_mod(zip_path)
    proc = load_processed("cleveland", zip_path)
    joined = mod.merge(proc, on=["age", "trestbps", "chol", "thalach"], suffixes=("_mod", "_proc"))
    return {
        "rows": len(mod),
        "joined": len(joined),
        "crosstab": pd.crosstab(joined.cp_mod, joined.cp_proc.astype(int)),
        "sick_share_asympt": round(float((mod[mod.cp == "asympt"].cls == "sick").mean()), 3),
    }


# --- E4: Statlog (Heart) ------------------------------------------------------------------------------


def check_statlog(statlog_path: Path = STATLOG, zip_path: Path = UCI_ZIP) -> dict:
    st = pd.read_csv(statlog_path, sep=r"\s+", header=None, names=COLUMNS[:13] + ["y"])
    cl = load_processed("cleveland", zip_path)
    cl["y"] = (cl.num > 0).astype(int) + 1  # Statlog codes 1 = absent, 2 = present
    key = ["age", "sex", "trestbps", "chol", "thalach"]
    m = st.merge(cl, on=key, suffixes=("_st", "_cl"))
    return {
        "rows": len(st),
        "matched": len(m),
        "unique_matched": len(m.drop_duplicates(subset=key)),
        "cp_identical": bool((m.cp_st == m.cp_cl).all()),
        "outcome_identical": bool((m.y_st == m.y_cl).all()),
    }


# --- Prevalence by label ------------------------------------------------------------------------------


def cad_rate_by_code(zip_path: Path = UCI_ZIP) -> dict[int, float]:
    cl = load_processed("cleveland", zip_path)
    return {int(k): round(float(v), 3) for k, v in (cl.num > 0).groupby(cl.cp).mean().items()}


# --- E7: copies -------------------------------------------------------------------------------------


def _match_on(copy: pd.DataFrame, uci: pd.DataFrame, key: list[str], cp_col: str) -> pd.DataFrame:
    """Rows whose key matches exactly one UCI row; returns a cross-tab of copy cp against UCI cp."""
    joined = copy.merge(uci[key + ["cp"]].rename(columns={"cp": "uci_cp"}), on=key)
    unique = joined.groupby(key).uci_cp.transform("nunique") == 1
    joined = joined[unique].drop_duplicates(subset=key)
    return pd.crosstab(joined[cp_col], joined.uci_cp.astype(int))


def _read_arff(path: Path) -> pd.DataFrame:
    text = path.read_text()
    names = re.findall(r"@attribute\s+'?([^'\s]+)'?", text, flags=re.I)
    body = text[re.search(r"@data", text, re.I).end() :]
    return pd.read_csv(
        io.StringIO(body), header=None, names=names, na_values="?", quotechar="'", skipinitialspace=True, comment="%"
    )


def check_openml(openml_dir: Path = OPENML, zip_path: Path = UCI_ZIP) -> dict[str, pd.DataFrame]:
    """OpenML heart-c (49) and heart-h (51) write cp as words."""
    out = {}
    for did, site in ((49, "cleveland"), (51, "hungarian")):
        copy = _read_arff(openml_dir / f"d{did}.arff")
        copy.columns = [c.lower() for c in copy.columns]
        copy = copy.rename(columns={"chest_pain": "cp", "max_heart_rate": "thalach", "cholesterol": "chol"})
        uci = load_processed(site, zip_path)
        key = [k for k in ("age", "trestbps", "chol", "thalach") if k in copy.columns]
        out[f"openml_{did}"] = _match_on(copy.rename(columns={"cp": "copy_cp"}), uci, key, "copy_cp")
    return out


PMLB_COLUMNS = {
    "age": "age",
    "chest_pain_type": "copy_cp",
    "resting_blood_pressure": "trestbps",
    "serum_cholesterol": "chol",
}


def check_pmlb(pmlb_dir: Path = PMLB, zip_path: Path = UCI_ZIP) -> dict[str, pd.DataFrame]:
    """PMLB heart_disease_* store cp as UCI - 1 and document 0 as typical angina."""
    sites = {"cleveland": "cleveland", "hungarian": "hungarian", "va_long_beach": "va", "zurich": "switzerland"}
    out = {}
    for name, site in sites.items():
        copy = pd.read_csv(pmlb_dir / f"heart_disease_{name}.tsv.gz", sep="\t").rename(columns=PMLB_COLUMNS)
        key = [k for k in ("age", "trestbps", "chol") if k in copy.columns]
        out[name] = _match_on(copy, load_processed(site, zip_path), key, "copy_cp")
    return out


KAGGLE_COLUMNS = {
    "Age": "age",
    "ChestPainType": "copy_cp",
    "RestingBP": "trestbps",
    "Cholesterol": "chol",
    "MaxHR": "thalach",
    "chest pain type": "copy_cp",
    "resting bp s": "trestbps",
    "cholesterol": "chol",
    "max heart rate": "thalach",
    "thalch": "thalach",
    "cp": "copy_cp",
    "Chest pain type": "copy_cp",
    "BP": "trestbps",
    "Max HR": "thalach",
}


def check_kaggle(kaggle_dir: Path = KAGGLE, zip_path: Path = UCI_ZIP) -> dict[str, pd.DataFrame]:
    """Kaggle copies, if downloaded (they are not redistributed in this repository)."""
    uci = pd.concat([load_processed(s, zip_path) for s in PROCESSED], ignore_index=True)
    key = ["age", "trestbps", "chol", "thalach"]
    out = {}
    for path in sorted(kaggle_dir.glob("*/*.csv")):
        copy = pd.read_csv(path, na_values="?", encoding="utf-8-sig")
        copy.columns = [c.strip() for c in copy.columns]
        copy = copy.rename(columns=KAGGLE_COLUMNS)
        if "copy_cp" not in copy or not set(key) <= set(copy.columns):
            raise ValueError(f"{path}: unrecognized columns {list(copy.columns)}; extend KAGGLE_COLUMNS")
        for col in key:
            copy[col] = pd.to_numeric(copy[col], errors="coerce")
        out[path.parent.name] = _match_on(copy, uci, key, "copy_cp")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--copies", action="store_true", help="also check downloaded Kaggle copies")
    args = parser.parse_args()

    print("E1 Detrano 1986:", check_detrano1986())
    for site, tab in check_raw_features().items():
        print(f"\nE2 {site}: rows = stored cp, columns = number of classical angina features\n{tab}")
    e3 = check_cleve_mod()
    print(f"\nE3 cleve.mod: {e3['rows']} rows, {e3['joined']} joined\n{e3['crosstab']}")
    print("\nE4 Statlog:", check_statlog())
    print("\nCleveland CAD rate by stored cp:", cad_rate_by_code())
    for name, tab in {**check_openml(), **check_pmlb()}.items():
        print(f"\nE7 {name}: rows = copy's cp, columns = UCI cp\n{tab}")
    if args.copies:
        for name, tab in check_kaggle().items():
            print(f"\nE7 kaggle {name}:\n{tab}")


if __name__ == "__main__":
    main()
