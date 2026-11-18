# Protocol: how does the published literature interpret chest-pain type? (E8)

**Fixed 17 Nov 2026, before any full text was read.** Later changes are logged at the end.

## Question

Among papers that analyse the UCI heart-disease data or a copy of it and **state a direction** for chest-pain type, how many present the coding artifact as a clinical finding, and in which direction?

## Sampling frame

Google Scholar, in the user's signed-in Chrome; no CAPTCHA is solved. If Scholar blocks the session, stop and record how far the search got. Two pre-set queries, 2010–2026, all result pages:

- **Q1 (explainable AI):** `"chest pain" "asymptomatic" "Cleveland" "heart disease" "SHAP"`
- **Q2 (any method):** `"chest pain" ("asymptomatic" OR "typical angina") ("UCI" OR "Cleveland" OR "Kaggle") "heart disease" "risk"`

Each result is screened. If the combined frame exceeds 300 records, a random sample of 150 is drawn (seed 20261117) before any full text is read.

## Inclusion

1. It analyses the UCI Heart Disease data (any site), Statlog (Heart), or a copy derived from them (OpenML, Kaggle, etc.).
2. The full text is accessible (open access, or through the user's library).
3. It states a direction for at least one chest-pain category (for example "asymptomatic patients had the highest risk", a SHAP or coefficient sign, an association rule, or a rate by category).

## Coding (one row per included paper)

- **copy:** the copy used (UCI / OpenML / Kaggle slug / Statlog / unclear), inferred from the paper's text, row count and code values
- **label_source:** the code-to-label mapping the paper applies (UCI documentation / Kaggle page / its own / not stated)
- **claim:** the verbatim sentence, 25 words or fewer, with its page or section
- **direction:** what the paper says is highest risk (asymptomatic / typical angina / other)
- **clinically_correct:** whether that direction is correct once the true coding is known (the true coding: UCI codes reversed; the Kaggle 1,025- and 303-row copies use code = 4 − UCI)
- **rationalised:** whether the paper explains the direction clinically (for example "silent ischaemia" or "biologically sound"): yes / no
- **venue, year, citations** (Scholar count on the screening date), **doi**

## Outcomes

- Share of included papers whose stated direction is clinically wrong, with a 95% Wilson interval.
- Share of those that rationalise the wrong direction clinically.
- The same, split by copy, showing the literature contradicting itself across copies.
- Citation-weighted totals (descriptive only).

## Reporting

- Each paper is described factually ("states X; uses copy Y"), with no judgement of its authors.
- The paper lists every included work in a supplementary table.

## Change log

- **17 Nov 2026, before any full text was read.** Q2 returned about 5,420 results (2010 onward), mostly clinical papers unrelated to the dataset, and Scholar shows only the first 1,000, so no fair random sample can be drawn from it. Q2 is dropped. **The frame is Q1 only** (about 270 results, 2010 onward), enumerated in full. If more than 150 of them pass screening, a random sample of 150 (seed 20261117) goes to full-text coding.
- **17 Nov 2026 ~23:59, before any full text was read.** Title/snippet screening: 31 off-topic, 8 duplicates, **230 eligible** (`code/sample_audit.py`, `evidence/literature-audit/sample.json`). Because 230 > 150, the 150 are the first 150 of a seeded shuffle (seed 20261117). **Staged coding:** the first 40 of that order (the pilot) are coded first and reported as an interim estimate; coding then continues in the same order to 150. No record is skipped or re-ordered after its full text is seen. Records whose full text is inaccessible are counted as such, not replaced.
- **18 Nov 2026, during coding of items 40–149 (after the pilot).** Coding continued in the seeded order to 150 using the user's University of the Cumberlands library access (IEEE Xplore, ProQuest Dissertations, Sage, EBSCO records). Previously inaccessible pilot items were retried; nothing was replaced. Full texts were read in the browser (HTML, or PDF parsed in-page). Sentence screening used the same v2 regex, plus a filter that drops pure label-definition sentences (e.g. "1 = typical angina, 2 = atypical angina …") before hand reading. Bot challenges (ScienceDirect, medRxiv/bioRxiv, ResearchGate, DiVA) were not bypassed; those items are coded inaccessible. Three Scholar links were truncated or pointed to the wrong article (k28, k91, k106); the correct full texts were located by title/DOI. Single-patient explanations that name a category and a direction were counted (k131, k138); importance without sign and numeric-only statements were not, as in the pilot. A sensitivity analysis excludes the illustrative, hedged and single-patient cases (k68, k131, k138).
- **18 Nov 2026, later (round 3, after the 150 were coded).** The 46 inaccessible items were retried, in the same seeded order, with nothing replaced. 16 were recovered (`evidence/literature-audit/round3-access-notes.md`) through:
  - UC Primo's link resolver, which found full text in EBSCO Academic Search Complete for some Springer and Wiley journals, and the UC Sage Premier holding;
  - open copies (Zenodo, author PDFs on ResearchGate located through Google Scholar, publisher OA sites, DiVA);
  - medRxiv and bioRxiv, which no longer showed a challenge.

  No challenge was bypassed. The DiVA proof-of-work page resolved by itself on reload. ScienceDirect's challenge and Sage's terms-consent page were left for the user.

  The coding rules are unchanged, with two additions to the pre-existing sensitivity analysis: a mixed statement (k25) and one with an idiosyncratic label mapping (k51). Statements in a data dictionary that are not presented as findings (k120) are not counted, by analogy with background statements.
- **18 Nov 2026, round 3b.** The user cleared the ScienceDirect bot check by hand and accepted Sage's terms-consent page. Claude did neither.
  - 4 more items became readable: k16, k102, k11 and k112.
  - k50, k80, k108, k116 and k149 turned out to be abstract-only, because UC has no Elsevier subscription. They stay inaccessible, now for a paywall reason.
- **18 Nov 2026, correction of a description (no coding change).**
  - The protocol's "true coding" line says the Kaggle 1,025- and 303-row copies use code = 4 − UCI. Row matching (`code/evidence_checks.py`) shows the exact mapping is 0 = UCI 4, 1 = UCI 2, 2 = UCI 3, 3 = UCI 1: the end codes are swapped and the middle codes keep their order.
  - Every coded statement in the audit concerns an end category (typical angina or asymptomatic), or was judged as written, so no code changes.
