# Literature screen 1: OpenAlex titles and abstracts (17 Nov 2026)

Queries (OpenAlex `title_and_abstract.search`, all results; script `openalex_fetch.py`):
- q1: `"chest pain" AND asymptomatic AND (Cleveland OR UCI OR Kaggle OR "heart disease dataset" OR Statlog)`: 32 works
- q2: `("typical angina" OR "asymptomatic chest pain" OR "ASY") AND ("heart disease" OR "coronary") AND (Cleveland OR UCI OR Kaggle OR dataset OR Statlog)`: 11 works
- 38 unique works. Most are clinical papers unrelated to the dataset (false positives).

## Abstracts that state a direction for chest-pain type, using the UCI data or a copy

| Work | Claim in the abstract | Reading |
|---|---|---|
| Nahar et al. 2012, *Expert Syst. Appl.*, doi:10.1016/j.eswa.2012.08.028 (431 citations, OpenAlex) | Association rules: "chest pain type being asymptomatic" as a sick factor (abstract matched via the title/abstract index; wording from the earlier Scholar search) | artifact read as clinical |
| IEEE RAAI 2021, doi:10.1109/raai52226.2021.9507928 | most relevant features include "asymptomatic chest pain" | artifact read as clinical |
| IEEE WIECON-ECE 2023, doi:10.1109/wiecon-ece60392.2023.10456373 | disease more likely "while the chest pain is asymptomatic"; healthier "while the chest pain is more anginal" | artifact read as clinical |
| IETE J. Res. 2025, doi:10.1080/03772063.2025.2517849 | "chest-pain-type is asymptomatic … belonging to the sick factor" | artifact read as clinical |
| IJARIIE 2019 (no DOI) | "chest pain being asymptomatic … indicate the likely of existence of heart disease" | artifact read as clinical |
| Boise State ScholarWorks 2026 (SHAP; no DOI) | SHAP anchored on "biologically sound … risk factors such as asymptomatic chest pain" | artifact read as clinical, explicitly called biologically sound |
| *AI in Medicine* (MDPI) 2026, doi:10.3390/aimed1040031 | large SHAP attribution for "the asymptomatic chest-pain category" | artifact read as clinical |
| AIP Conf. Proc. 2024, doi:10.1063/5.0225811 | "typical angina being the most common and asymptomatic chest pain being the least" | Kaggle copy with 0 read as typical angina: **accidentally correct** |
| Atlantis/Adv. Eng. Res. 2025, doi:10.2991/978-94-6463-884-4_73 | "typical angina having the greatest impact, while asymptomatic chest pain was the least" | likely the same Kaggle copy: accidentally correct |
| *Artif. Intell. Appl.* 2026, doi:10.47852/bonviewaia62026305 | "n ≈ 410 typical angina cases" | Kaggle 1,025-row copy, code 0 read as typical angina |
| Jurnal Pendidikan dan Pengajaran 2024, doi:10.69820/jupeja.v2i2.196 | MANOVA on fedesoriano's TA/ATA/NAP/ASY | wrong word labels, no direction stated |

**Finding:** the published literature contradicts itself depending on which copy a paper used. Full texts are not yet read; every row needs checking against the full text before it is cited.
