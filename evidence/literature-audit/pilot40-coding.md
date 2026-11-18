# E8 pilot: full-text coding of the first 40 of the seeded sample (18 Nov 2026, ~00:30 PST)

Method: per `PROTOCOL-literature-audit.md`. Text extracted with the v2 rules (`code/extract_claims.py`, and the same regex run in the browser for HTML pages). Every flagged sentence was read and coded by hand. "Not included" = full text read, but no direction stated for a named chest-pain category (inclusion criterion 3). "Inaccessible" = no full text without a subscription or a bot challenge (no access was attempted beyond the publisher's page); these are counted, not replaced.

**True coding** (from E1–E3): the UCI codes are reversed; fedesoriano/redwankarimsony "ASY"/"asymptomatic" = truly typical angina; Kaggle 303/1,025 copies: code 0 = UCI 4 = truly typical angina.

| k | idx | Venue (year) | Copy used | Access | Stated direction (verbatim, ≤25 words) | Clinically correct? | Rationalised? |
|---|---|---|---|---|---|---|---|
| 2 | 99 | Sci. Rep. (2025) | UCI Cleveland, 297 | full text | none | n/a (not included) | — |
| 10 | 153 | Front. Med. (2025) | 1,190 merge | full text | none (documents "0 = Typical angina … 3 = Asymptomatic") | n/a (not included) | — |
| 12 | 13 | Discover Computing (2026) | Kaggle/UCI (4 sites) | full text | only hypothetical "high … 'cp' … as high risk", no category | n/a (not included) | — |
| 15 | 146 | Engineering Reports (2026) | Kaggle 1,025 + UCI 303 | full text | none from data | n/a (not included) | — |
| 18 | 105 | IJSREM (2026) | 1,190 merge | full text (PDF) | "asymptomatic presentation (type 4) paradoxically signals higher risk, consistent with the silent ischaemia literature" | **No** | **Yes** (silent ischaemia) |
| 20 | 30 | ESTIN repository (2026) | Kaggle (cp 0–3) | full text (PDF) | "asymptomatic chest pain (cp=3) … highly prevalent in CVD cases"; "Typical angina (low cp): Negative SHAP (linked to Healthy)" | **No** | No |
| 21 | 87 | Vasc. Endovasc. Rev. (2026) | 920 UCI (word labels) | full text (PDF) | "asymptomatic chest pain is clinically important simply because it can be so easily missed" (among top RF features) | **No** | **Yes** |
| 23 | 74 | medRxiv (2026) | 918 (fedesoriano) | full text (PDF) | "typical angina symptoms captured here by the cp variable are among the strongest independent predictors" | Yes (but contradicts its own coding, where higher cp = ASY) | Yes (literature) |
| 26 | 191 | Genet. Mol. Res. (2026) | 1,190 merge | full text (PDF) | none from data (toy example only) | n/a (not included) | — |
| 29 | 93 | J. Big Data (2023), cited 256 | 918 (fedesoriano) | full text | "Patients with asymptomatic chest pain (ASY) are about six times more likely to suffer heart disease than those with Atypical Angina" | **No** | No (stated as a clinical finding) |
| 31 | 206 | SciTePress (2025) | Kaggle | full text (PDF) | none | n/a (not included) | — |
| 34 | 247 | Sci. Rep. (2026) | Kaggle 1,025 | full text | none | n/a (not included) | — |
| 35 | 168 | Research Square (2026) | ? | full text (PDF) | none | n/a (not included) | — |
| 36 | 213 | Processes (MDPI, 2022), cited 74 | 918 (fedesoriano) | full text | "the number of people with apparently asymptomatic angina is predominant" with high SHAP contribution | **No** | No |
| 37 | 173 | J. Intell. Syst. (2024) | 1,190 merge | full text | none | n/a (not included) | — |
| 39 | 115 | Sci. Rep. (2026) | Cleveland | full text | none | n/a (not included) | — |
| 0, 30 | 164, 113 | Google Books | — | inaccessible | — | — | — |
| 1, 3, 5, 9, 17, 19, 24, 32, 33, 38 | 75, 64, 116, 50, 25, 94, 185, 68, 255, 28 | IEEE Xplore | — | inaccessible (paywall; no institutional access in the session) | — | — | — |
| 6, 22 | 217, 81 | ProQuest theses | — | inaccessible (preview only) | — | — | — |
| 7, 8, 13 | 90, 234, 242 | Springer chapters | — | inaccessible (paywall) | — | — | — |
| 11, 16 | 18, 106 | ScienceDirect | — | inaccessible (bot challenge; not bypassed) | — | — | — |
| 27 | 260 | Univ. of Benin repository | — | inaccessible (HTTP 403) | — | — | — |
| 4, 14, 25, 28 | 211, 127, 8, 216 | T&F, SPIE, ResearchGate, SCIRP | — | not yet attempted / link incomplete | — | — | — |

## Interim result (pilot, accessible full texts only)
- Accessible full texts: 16 of 40.
- **Stated a direction for a chest-pain category: 6 of 16.**
- **Clinically wrong: 5 of 6** (83%; 95% Wilson interval 44–97%).
- Explained the wrong direction clinically: 2 of 5 (silent ischaemia; "easily missed"). One more (k29, cited 256 times) states it as a plain clinical finding.
- The one "correct" statement (k23) contradicts its own coding.
- **Access bias:** 24 of 40 are behind paywalls or bot checks. Library access would raise the coverage.

## Continuation: sample items 40–79 (same order, same rules), 18 Nov 2026 ~00:45

| k | idx | Venue (year) | Copy | Access | Stated direction (verbatim, ≤25 words) | Correct? | Rationalised? |
|---|---|---|---|---|---|---|---|
| 43 | 88 | Research Square (2025) | ? | full text | none | n/a | — |
| 46 | 14 | J. Cognition & AI (2026) | UCI Cleveland 303 | full text (PDF) | SHAP table, "Clinical Interpretation": "asymptomatic presentation strongly predicts disease" | **No** | **Yes** (presented as clinical interpretation) |
| 47 | 202 | Electronics (MDPI, 2022), cited 170 | Cleveland 303 | full text | none | n/a | — |
| 52 | 17 | Sci. Rep. (2022) | Kaggle 1,025 | full text | none | n/a | — |
| 54 | 126 | Sci. Rep. (2025) | Cleveland 303 | full text | "The majority of patients who experienced typical angina (cp = 1) do not have heart disease" | **No** | No |
| 58 | 7 | AI in Medicine (MDPI, 2026) | UCI Cleveland 297 | full text | "The asymptomatic chest-pain category (cp_4.0) received the highest relative importance" | importance only (no sign); not counted | — |
| 59 | 5 | Mach. Learn.: Sci. Technol. (IOP, 2025) | Kaggle 303 (0 = typical … 3 = asymptomatic: accidentally right for this copy) | full text | clinical background only | n/a | — |
| 62 | 263 | PMLR (2021) | Cleveland | full text (PDF) | rule: "although the patient is asymptomatic (no chest pain), the thallium stress test reveals …", giving disease | borderline (sensitivity only) | — |
| 69 | 204 | Health Sci. Rep. (2024) | Cleveland 303 | full text | "Most of the participants have asymptomatic angina" (prevalence only) | n/a | — |
| 70 | 163 | Discover AI (2026) | ? | full text | "higher values of … 'cp' … tend to increase the predicted risk" (numeric only) | not counted | — |
| 71 | 167 | arXiv (2026) | Kaggle 1,025 | full text (PDF) | none | n/a | — |
| 76 | 219 | Front. Med. (2023), cited 200 | 918 (fedesoriano) | full text | none (documents TA/ATA/NAP/ASY) | n/a | — |
| 73 | 121 | ResearchGate | — | inaccessible (403) | — | — | — |
| 40–42, 44, 45, 48–51, 53, 55–57, 60, 61, 63–68, 72, 74, 75, 77–79 | | | | not yet attempted (most are IEEE/Springer/Elsevier/T&F paywalls) | | | |

## Running tally (items 0–79; accessible full texts coded: 28)
- **Stated a direction for a named chest-pain category: 8.**
- **Clinically wrong: 7 of 8** (87.5%; 95% Wilson interval 53–98%): k18, k20, k21, k29, k36, k46, k54.
- **Correct: 1** (k23), and it contradicts its own coding.
- **Wrong direction explained clinically:** 3 of 7 (silent ischaemia; "easily missed"; "clinical interpretation"). k29 (cited 256 times) states it as a clinical finding.
- **Also flagged, not counted:** asymptomatic named as the most important category without a sign (k58); numeric-only "higher cp → higher risk" (k12, k70); rule-based borderline (k62).
- **20 of 28 accessible papers state no direction at all.** The claim is made by a minority of papers, but when it is made, it is almost always wrong.
- **Coverage limit:** about 55% of the sample is paywalled or behind bot checks. Library/IEEE institutional access would allow the full 150.
