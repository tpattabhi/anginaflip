# PMLB (EpistasisLab/pmlb, master branch), downloaded 17 Nov 2026 via the GitHub API

- Current datasets: `heart_disease_cleveland` (303), `heart_disease_hungarian` (294), `heart_disease_va_long_beach` (200), `heart_disease_zurich` (123).
- Their `metadata.yaml` says, for `chest_pain_type`: "0 = typical angina, 1 = atypical angina, 2 = non-anginal pain, 3 = asymptomatic".
- Rows matched to the UCI processed files (age, resting BP, cholesterol; unique matches only): **chest_pain_type = UCI cp − 1** at all four sites (Cleveland 303/303 matched; Hungarian 268; Long Beach 98; Zurich 96, matched on age and BP only).
- So PMLB's documented labels inherit the reversal: its "typical angina" (0) is UCI code 1, which is no pain.
- The older `_deprecated_cleve`, `_deprecated_heart_c`, `_deprecated_heart_h`, `_deprecated_heart_statlog` and `_deprecated_hungarian` folders remain in the repository; they were not checked.
