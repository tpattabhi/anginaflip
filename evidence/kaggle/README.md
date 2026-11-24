# Kaggle copies (downloaded 17 Nov 2026 via https://www.kaggle.com/api/v1/datasets/download/<owner>/<slug>)

Usage counts are from the Kaggle dataset list sorted by votes, 17 Nov 2026. The coding comes from `kaggle_check.py` (rows matched to the UCI processed files on age, resting BP, cholesterol and max heart rate; only unique matches kept). Its output is in `result.txt`.

| Dataset | Rows | Downloads / notebooks | Chest-pain coding vs. UCI | What the page says the codes mean |
|---|---|---|---|---|
| fedesoriano/heart-failure-prediction | 918 (4 UCI sites + Statlog) | 290K / 1,993 (1.58M views; 19 users report "LLM fine-tuning") | Words: TA = UCI 1, ATA = 2, NAP = 3, ASY = 4 | "TA: Typical Angina … ASY: Asymptomatic", so **wrong, in words** |
| johnsmith88/heart-disease-dataset (David Lapp) | 1,025 (302 unique Cleveland rows, duplicated) | 385K (386K on 18 Nov) / 1,047 (1.64M views) | 0 = UCI 4, 1 = 2, 2 = 3, 3 = UCI 1 (end codes swapped, middle codes = UCI − 1; corrected 18 Nov, earlier notes said 4 − UCI); **outcome reversed** (target 1 = UCI no disease) | "chest pain type (4 values)", meaning not given; says "1 = disease" (contradicted by the data) |
| redwankarimsony/heart-disease-data | 920 (4 sites) | 112K / 399 | Words: "typical angina" = UCI 1 | **Wrong, in words** |
| nareshbhat/health-care-data-set-on-heart-attack-possibility | 303 | 43.3K / 181 | Same as johnsmith88; outcome reversed | Page not checked |
| cherngs/heart-disease-cleveland-uci | 297 | 44.5K / 171 | 0 = UCI 1 … 3 = UCI 4 (code = UCI − 1) | Page not checked |
| mexwell/heart-disease-dataset | 1,190 (4 sites + Statlog) | 21.2K / 98 | UCI codes unchanged | Documented labels: 1 = typical angina … 4 = asymptomatic (`documentation.pdf`) |
| imnikhilanand/heart-attack-prediction | 294 (Hungarian) | 36.6K / 91 | UCI codes unchanged | Page not checked |
| rishidamarla/heart-disease-prediction | 270 (Statlog) | 48.8K / 186 | UCI codes unchanged | Page not checked |

The check now lives in `code/evidence_checks.py` (`--copies`). The Kaggle CSVs are not redistributed; download them into `evidence/kaggle/<owner>_<slug>/` to rerun it.
