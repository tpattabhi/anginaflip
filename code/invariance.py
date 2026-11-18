"""E9(a-b): standard models score identically under the documented and corrected chest-pain codes; only the
meaning of their explanations changes.

Run: uv run python code/invariance.py  (writes results/invariance.json)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_probe as lp  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "evidence" / "uci-raw-archive" / "heart+disease.zip"
SEED = 20261117
FEATURES = ["age", "sex", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]


def design(df, cp_codes, one_hot: bool):
    """Feature matrix; chest pain either as the integer code or as one-hot columns named by documented label."""
    X = df[FEATURES].copy()
    X = X.fillna(X.median())
    if one_hot:
        names = []
        for k in (1, 2, 3, 4):
            col = f"cp_{lp.CP_DOCUMENTED[k].replace(' ', '_')}"
            X[col] = (cp_codes == k).astype(int)
            names.append(col)
    else:
        X["cp"] = cp_codes
    return X


def models():
    return {
        "logistic_ordinal": (False, make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))),
        "logistic_onehot": (True, make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))),
        "random_forest": (True, RandomForestClassifier(n_estimators=500, random_state=SEED)),
        "gradient_boosting": (True, GradientBoostingClassifier(random_state=SEED)),
    }


def run() -> dict:
    df = lp.load_uci(str(ZIP))
    y = df["cad"].to_numpy()
    documented = df["cp"].to_numpy()  # code k read with the UCI labels
    corrected = 5 - documented  # the same patients, codes re-mapped so the UCI labels become true
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    out = {"n": int(len(df)), "models": {}}
    for name, (one_hot, est) in models().items():
        rec = {}
        for tag, codes in [("documented", documented), ("corrected", corrected)]:
            X = design(df, codes, one_hot)
            p = cross_val_predict(est, X, y, cv=cv, method="predict_proba")[:, 1]
            rec[f"auc_{tag}"] = float(roc_auc_score(y, p))
            rec[f"pred_{tag}"] = p
        rec["max_abs_pred_diff"] = float(np.max(np.abs(rec.pop("pred_documented") - rec.pop("pred_corrected"))))
        out["models"][name] = rec
    # what a reader of the documented labels concludes from a one-hot logistic model
    X = design(df, documented, True)
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X, y)
    coefs = dict(zip(X.columns, lr[-1].coef_[0]))
    out["documented_onehot_logistic_cp_coefs"] = {
        k: round(float(v), 3) for k, v in coefs.items() if k.startswith("cp_")
    }
    out["cad_rate_by_documented_label"] = {
        lp.CP_DOCUMENTED[k]: round(float(y[documented == k].mean()), 3) for k in (1, 2, 3, 4)
    }
    out["cad_rate_by_true_label"] = {
        lp.CP_DOCUMENTED[5 - k]: round(float(y[documented == k].mean()), 3) for k in (1, 2, 3, 4)
    }
    return out


if __name__ == "__main__":
    res = run()
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "invariance.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
