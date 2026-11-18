# Round 3: retrying the 46 inaccessible items (18 Nov 2026, later)

Same protocol and coding rules as `audit-150-summary.md`. No item was replaced or re-ordered. No bot check was bypassed: pages still showing a challenge stay inaccessible unless the user clears them by hand. The DiVA check is a proof-of-work page that resolved by itself on reload, with no input.

**Routes that worked:**
- **UC Primo discovery's link resolver**, which led to:
  - EBSCO Academic Search Complete full text for some Springer and Wiley journals (the library does not subscribe to those publishers directly);
  - Sage Premier;
  - PubMed Central.
- **Open copies:**
  - Zenodo;
  - author-uploaded PDFs on ResearchGate, located through Google Scholar;
  - the publisher's own open-access site (Springer OA, WARSE, Tech Science Press);
  - DiVA.
- **Preprint servers** (medRxiv, bioRxiv), which showed no challenge on retry.

## Newly accessible: 16 items

| k | Venue | Route | Copy | Claim (verbatim, ≤25 words) | Coded | Correct? | Rationalised? |
|---|---|---|---|---|---|---|---|
| 93 | bioRxiv 2025 | bioRxiv | 1,190 merge (UCI words, 4 = asymptomatic) | "Chest pain type is a strong differentiator, with asymptomatic pain being more prevalent in heart disease cases (55.8% vs. 19.5%, P<0.001)." | direction | **No** | No |
| 25 | ResearchGate → Zenodo 10.5281/zenodo.17632137 | open copy | Kaggle 1,190 merge | "asymptomatic and typical angina categories are strongly correlated with positive cases, whereas non-anginal pain types dominate in healthy cases" | direction (mixed) | **No** (asymptomatic part) | No |
| 85 | Comput. Intell. 41(5), 2025 (Wiley) | EBSCO ASC via Primo | 1,190 merge + Cleveland 303 | "asymptomatic cases (type 4) being the most predictive of heart disease, aligning with clinical findings that many severe cardiovascular conditions present with minimal symptoms" | direction | **No** | **Yes** |
| 44 | DiVA BSc thesis 2020 (Dalarna) | DiVA | Kaggle 303 (cp 0 labelled typical angina; outcome reversed) | "when the chest pain type is typical of angina, the model predicts that the patient is less likely to have heart disease" | direction | **No** (caused by the outcome reversal; the cp label happens to be right) | No |
| 51 | ResearchGate (author PDF) 2025 | open copy | Kaggle 303/1,025 with its own mapping (ASY = type 2) | "individuals with type 2 chest pain are more susceptible to cardiovascular diseases" (type 2 = "asymptomatic (ASY type 2)") | direction | **No** (mapping idiosyncratic) | No |
| 96 | Arab. J. Sci. Eng. 51(5), 2026 (Springer) | EBSCO ASC | Cleveland 303 (UCI codes) | "type 1: typical angina has the highest percentage of relationship with the disease, but type 4: asymptomatic has 47.81% of the data volume" | direction | Yes as stated (contradicts the Cleveland counts, where code 1 has the lowest disease share) | No |
| 77 | ResearchGate (J. Inst. Res. Big Data Anal. Innov.) | open copy | fedesoriano 918 | "(ChestPainType = 1) likely represents an atypical or non-anginal pain category that the model has learned to associate with higher risk" | indeterminate (middle category, hedged guess, one patient) | — | (yes: "red flag") |
| 73 | ResearchGate (leakage audit of UCI heart data, 2026) | open copy | UCI 4-site / Kaggle 1,025 / 918 | "The most influential SHAP features for XGBoost are clinically plausible: asymptomatic chest pain, exercise-induced angina, ST depression…" | not counted (importance without sign) | — | **notable**: a dedicated data-quality audit of this dataset calls it plausible and does not notice the reversal |
| 120 | Comput. Mater. Contin. 88(3), 2026 (OA) | ResearchGate author PDF | fedesoriano 918 | data dictionary: "Silent ischemia and increased risk are often associated with the so-called asymptomatic (ASY) presentations." | not counted (background statement, not a finding) | — | — |
| 147 | medRxiv 2025 | medRxiv | Kaggle 1,025 | "cp_0 (asymptomatic chest pain) … also influenced the model as expected" (no sign; own legend says cp0 = typical angina) | not counted (importance only) | — | — |
| 145 | Int. J. Comput. Intell. Syst. 2026 (Springer OA) | publisher OA PDF | UCI 920 | "Chest Pain Type (CP) make positive contributions toward the prediction of HD" | not counted (numeric only) | — | — |
| 136 | medRxiv 2025 | medRxiv | Kaggle 1,025 + 303 | none | not included | — | — |
| 61 | J. Supercomput. 79(16), 2023 (Springer) | EBSCO ASC | Kaggle 1,025 | none in text (per-patient SHAP table only) | not included | — | — |
| 118 | ResearchGate (author PDF) 2026 | open copy | Kaggle 303 | none | not included | — | — |
| 141 | ResearchGate (J. Res. Rev. Quantum Comput.) 2026 | open copy | Cleveland 303 | none | not included | — | — |
| 95 | IJATCSE 11(3), 2022 | WARSE OA site (academia.edu was a login wall) | Kaggle 303 | none (SHAP importance only) | not included | — | — |

## Round 3b: after the user cleared the ScienceDirect check and accepted the Sage terms (4 more accessible)

| k | Venue | Route | Copy | Claim (verbatim, ≤25 words) | Coded | Correct? | Rationalised? |
|---|---|---|---|---|---|---|---|
| 16 | Data Knowl. Eng. 2024 (Elsevier, OA) | ScienceDirect | 1,190 merge (UCI codes) | "Chest pain type 4, cholesterol, max heart rate, and oldpeak were the variables that contributed most to the positive prediction"; "Chest pain of type 4, which is an asymptomatic type of pain" | direction | **No** | No |
| 102 | Healthcare Analytics 2025 (Elsevier, OA) | ScienceDirect | Cleveland 303 | none | not included | — | — |
| 11 | Elsevier OA journal 2026 | ScienceDirect | a different 303-row risk-factor dataset | none | not included | — | — |
| 112 | Proc. HFES 2024 (Sage) | UC Sage Premier (terms accepted by the user) | Kaggle 303 | none | not included | — | — |

**Abstract only, no UC Elsevier subscription:** k50, k80, k108, k116, k149. These remain inaccessible, now for a paywall reason rather than the bot check.

**Totals after 3b:**
- **124 accessible; 26 inaccessible.**
- **32 direction-stating; 25 wrong (78%; 95% Wilson 61–89%); 7 right; 9 rationalised.**
- **Sensitivity** (dropping k68, k131, k138, k25, k51): **20 of 27 (74%; 55–87%).**

## Still inaccessible: 26 items

| Reason | Items |
|---|---|
| Elsevier paywall (abstract only; UC has no Elsevier subscription) | k50, k80, k108, k116, k149 |
| Not in any UC database; no open copy found (Springer) | k45, k86, k90, k66 (in PMC, but within the 1-year embargo) |
| Indexed in EBSCO as a citation only, no full text (T&F) | k4, k48 |
| Not in UC databases (World Scientific, Wiley CPE, SPIE, IGI) | k49, k79, k14, k122 |
| Book chapters not in UC e-book collections (Springer) | k7, k8, k13, k53, k89 |
| Google Books preview only | k0, k30, k97 |
| Site down or blank, or PDF link dead | k78, k119 |
| Repository viewer only | k137 |
