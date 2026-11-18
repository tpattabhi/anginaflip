# Has anyone reported that the UCI chest-pain variable is coded in reverse? (searched 16 Nov 2026; extended search the same evening, see the end)

**Short answer: no published report found.** Nothing located states that the UCI processed files store `cp` in reverse of their own documentation, and nothing checks the coding against Detrano et al. 1986 (or any primary source). The closest items are informal notes and papers that relabel a **Kaggle copy** of the data. Several published papers interpret the artifact as a clinical finding.

Searches: web (5 queries, standard and extended), Google Scholar in Chrome (1 query, first page), plus the specific items below. Not exhaustive: Kaggle discussion threads (login needed) and the full texts marked below were not read.

## Closest precedents (informal or about a copy)
- **Kaggle-copy relabeling.** A GitHub README (smarthardik10, "Heart-Disease-UCI-Diagnosis-Prediction") and the matching Towards Data Science article ("Heart Disease UCI-Diagnosis & Prediction") give the "correct" Kaggle coding as 0 = asymptomatic … 3 = typical angina, and blame Kaggle's metadata. It doesn't claim the UCI documentation is wrong, and it cites no primary source. If the Kaggle copy is UCI's code minus 1, this relabeling is the same reversal we found, stated informally for the copy only.
  - https://github.com/smarthardik10/Heart-Disease-UCI-Diagnosis-Prediction
  - https://medium.com/data-science/heart-disease-uci-diagnosis-prediction-b1943ee835a7
- **Ogu, Ihuefo & Iheanacho 2026,** *Afr. J. Adv. Sci. Technol. Res.* 23(1):174–195, doi:10.62154/ajastr.2026.023.01023 (published 4 Nov 2026). The abstract reports that "a widely shared copy of the dataset was found to carry a reversed outcome label", so they used the UCI file. The Google Scholar snippet also says the copy "recodes chest pain type (0 in the copy corresponds to asymptomatic, …". **Full text not retrieved** (server returned HTTP 508). From the snippet, they treat the UCI file's coding as correct and the copy as different. **Verify before submission:** if they state that the copy's coding is the clinically right one, they are a partial precedent and should be cited.
- **Simmons 2021, M.S. thesis (Elizabeth City State Univ.),** "Investigating Heart Disease Datasets and Building Predictive Models". Per its abstract and search snippets it reports encoding errors and a reversed target in copies. The snippet interprets a no-chest-pain coefficient as clinical. Full text not retrieved (the repository URL redirects).

## Published work that interprets the artifact as clinical (examples for the Discussion)
- Yuan, Heiser & de Rooij 2022, *Adv. Data Anal. Classif.* (Springer), "A comparison of two dissimilarity functions for mixed-type predictor variables in the δ-machine". Scholar snippet: "asymptomatic patients were more likely to have coronary heart disease than symptomatic …". Full text not read.
- Shaw & Patidar 2022 (Springer, *Inventive Communication and Computational Technologies*): lists "asymptomatic chest pain" among disease indicators (snippet).
- Many tutorials and EDA pages describe "asymptomatic" as the highest-risk chest-pain group (e.g., Medium "Cleveland EDA").

## Also affected (same source data, not checked against a primary source)
- The Budapest, Long Beach VA and Swiss UCI files show the same pattern (exercise angina in 50–59% of patients coded "asymptomatic").
- **Statlog (Heart)**, UCI dataset 145 (270 patients, widely used on OpenML). It is described as similar to the Cleveland database and uses the same 1–4 `cp` labels, so it is probably affected. **Unverified.**

## Suggested wording for the paper
"To our knowledge, no published work has reported that the UCI files store chest-pain type in reverse of their documentation. Informal notes have relabeled the codes of a derived copy [web], and published analyses have interpreted asymptomatic patients as the highest-risk group."


## Extended search, 16 Nov 2026 evening (supersedes the notes above where they differ)
**Result: still no report found** that the UCI files store chest-pain type in reverse of their documentation. This is not proof of novelty; see "Not searched" below.

**Searched:**
- web search: 4 more extended queries;
- Google Scholar: 2 more queries, first page each;
- Semantic Scholar: 1 query (rate-limited after that);
- the UCI dataset page (no erratum, change log or discussion about `cp`);
- GitHub issue search (nothing relevant);
- full texts of Ogu et al. 2026 (`prior_art_dl/ogu2026.pdf`) and Shuaibu et al. 2026 (`prior_art_dl/shuaibu2026.pdf`).

**Corrections to the notes above:**
- **Ogu et al. 2026 is not a precedent.** They compared the UCI file row by row with the widely shared Kaggle copy: the copy reverses the outcome label and recodes chest pain so that "0 in the copy corresponds to asymptomatic, UCI code 4". Their own Table 1 uses the UCI documentation (1 typical angina … 4 asymptomatic) as correct. They are a useful related citation on provenance errors in Cleveland-data copies, but they did not find our error.
- **The smarthardik10 README / TDS article is not a precedent either.** Per Ogu et al., Kaggle 0 = UCI 4, so their "0 = asymptomatic" relabeling follows the UCI documentation, not the reversal we found.

**More published work that reads the artifact as clinical:**
- Shuaibu et al. 2026, *Medicine and Community Health Archives* 4, Art. 86: "chest pain category 4" as a significant predictor, no comment.
- Nahar et al. 2013, *Expert Syst. Appl.* (Scholar: cited 546 times): association rules with "chest pain type being asymptomatic" as a disease factor.
- arXiv 2011.03195 ("Explainable AI meets Healthcare", 2020): treats asymptomatic chest pain as "the most severe" type.
- A GitHub project (YoussefSaeed1/Heart_Disease_Project) attributes the 73% CAD rate in "asymptomatic" patients to referral selection, the same explanation this project first gave.

**Not searched (residual risk):**
- Kaggle discussion threads (need login);
- the Simmons 2021 thesis full text (repository redirect);
- Google Scholar beyond page 1;
- non-English literature;
- cardiology journals' letters sections;
- IEEE Xplore full text. The user says it is authenticated in Chrome; not yet used.

The claim in the paper, "We found no published report of it", is accurate for what was searched. "To our knowledge" wording is advisable.

## Third pass, 16 Nov 2026 (~20:00)
- **IEEE Xplore** (full text & metadata):
  - "chest pain" + Cleveland + {"coded in reverse", "reversed coding", "coding error", miscoded, mislabeled}: **0 results**;
  - "chest pain" + UCI + asymptomatic + {revers*, swapped, inverted}: 253 results, swamped by "reversible defect" (thallium); no data-quality or coding paper among the 100 titles scanned;
  - "chest pain" + UCI + Circulation + Detrano + 1986: 1 result, a conference front matter (irrelevant).
- **Google Scholar, 3 queries × up to 4 pages (~110 more results):**
  - query A ("Cleveland" "chest pain" reversed/inverted coding) is exhausted after about 24 results, none relevant;
  - query B (coding/documentation error, mislabeled, miscoded) found nothing relevant (two "mislabel" hits are about outcome labels);
  - query C (counterintuitive/paradox) found only arXiv 2011.03195, which writes that asymptomatic chest pain being riskiest "may seem counterintuitive".
- **Kaggle** (searchable without login):
  - topic searches "chest pain cp reversed" and "chest pain coding wrong" found nothing relevant;
  - "asymptomatic typical angina cp" found "The ultimate guide to this dataset!" (IntiPic, about 2019, 103 upvotes, 30 comments) on the removed `ronitf/heart-disease-uci` dataset. The live page is gone. An Internet Archive copy exists (web.archive.org/web/20220210075519/...discussion/105877), but **reading it was blocked by this session's permission settings**. Its snippet ("cp … 0: asymptomatic, 1: atypical angina, 2: non-anginal pain …") matches the UCI documentation via Ogu et al.'s mapping (Kaggle 0 = UCI 4), so it is very likely not a precedent. Its comments are unread.
- **Conclusion:** no precedent found in web, Scholar (deeper), Semantic Scholar (partial), IEEE Xplore, the UCI page, GitHub issues, or Kaggle search. Residual: the archived Kaggle comments, non-English work, and anything Scholar does not index.

## Fourth pass: Kaggle with the user's login (16 Nov 2026, evening)
- **Comment search "asymptomatic typical angina cp":** 6 comments. The relevant one is "Comment on: ca & cp values switched??" (Zhenhui Xie, about 2018), snippet "Value 4->0: asymptomatic". That is the Kaggle copy renumbering UCI code 4 to 0 (as in Ogu et al. 2026), not a claim that the UCI coding is clinically reversed. The thread was on the removed `ronitf/heart-disease-uci` dataset (live page: not found).
- **Comment searches** "chest pain reversed" and "asymptomatic counterintuitive heart disease": no results.
- **"Detrano chest pain":** 153 notebooks; the visible snippets follow the UCI documentation (e.g., "the most common type of chest pain reported is asymptomatic").
- **Pending:** the user is checking the archived discussion list of `ronitf/heart-disease-uci` in their own browser for the full text of "The ultimate guide to this dataset!" and "ca & cp values switched??".
- **Outcome (user, 16 Nov):** the archived discussion threads show no content in any capture, so the comments were not preserved. Search closed; the paper keeps "to our knowledge" wording.
