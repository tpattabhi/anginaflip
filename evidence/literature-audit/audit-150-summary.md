# E8: literature audit, full sample of 150 (18 Nov 2026)

Per `PROTOCOL-literature-audit.md`: the first 150 of the seeded order, staged coding. Items 0–79 were first coded overnight (`pilot40-coding.md`). On 18 Nov the remaining items were coded, and inaccessible ones retried, using the user's University of the Cumberlands library access; rows are in `coding-80-149-and-retries.tsv`. No item was replaced or re-ordered. Inaccessible items are counted, not replaced.

> **Update, round 3 (18 Nov, later):** 16 of the 46 inaccessible items were recovered through UC Primo → EBSCO Academic Search Complete, open repository copies, and preprint servers. Details are in `round3-access-notes.md`.
> - After the user cleared the ScienceDirect check and accepted the Sage terms (round 3b), 4 more items became accessible, including k16, which is wrong.
> - **Now 124 accessible; 26 inaccessible.**
> - **32 state a direction; 25 are wrong (78%; 95% Wilson 61–89%); 9 of the 25 are rationalised.**
> - **Sensitivity: 20 of 27 (74%; 55–87%).**
> - The tables below are the round-2 figures (104 accessible) plus the round-3 additions listed in that file.

## Access
- **Accessible full text: 104 of 150 (round 2); 120 after round 3.** **Inaccessible: 46 (round 2); 30 after round 3.**
- **The library added IEEE Xplore** (all 27 IEEE items now read) **and ProQuest Dissertations** (4 theses).
- **UC has no Springer, Elsevier, Wiley, T&F, World Scientific, SPIE or IGI subscription.** Those items remain inaccessible unless open access.
- **Not bypassed:** bot challenges (ScienceDirect "Are you a robot?", medRxiv/bioRxiv Cloudflare, ResearchGate, DiVA). Items behind them are coded inaccessible.
- **Scholar links truncated or wrong in three cases** (k28, k91, k106). The correct full texts were located by title or DOI and coded.

## Result (accessible full texts that state a direction for a named chest-pain category)
| | n |
|---|---|
| States a direction | **25** |
| Clinically **wrong** | **19 (76%; 95% Wilson 57–89%)** |
| Clinically right as stated | 6 |
| Wrong direction explained clinically ("rationalised") | 8 of 19 |
| Sensitivity: drop the illustrative, hedged and single-patient cases (k68, k138, k131) | 16 of 22 = 73% (52–87%) |

**Wrong (19):** k1, k17, k18, k20, k21, k29, k36, k46, k54, k57, k63, k65, k68, k98, k106, k117, k123, k131, k138.

**Right as stated (6):** k23, k81, k88, k110, k111, k144. None of the six is a clean reading of the true coding:
- k23 and k111 **contradict their own coding tables** (each documents 1 = typical angina … 4 = asymptomatic, then calls the high-risk category typical angina).
- k88 and k144 use **Kaggle copies whose outcome is also reversed**, so the stated direction comes from two reversals.
- k110 labels high normalised cp as typical angina but **also inverts the slope labels**, so its mapping is unreliable.
- k81 states typical angina has the greatest "impact" without saying which copy it used.

**So no paper in the sample identifies the reversal.** Correct-sounding statements arise from self-contradiction or compensating errors.

**Round-3 additions:**

| Outcome | Items | Notes |
|---|---|---|
| Wrong (6) | k93, k25, k85, k44, k51, k16 | k85 rationalised. k25 is mixed. k51 uses an idiosyncratic mapping. k44's error comes from the Kaggle outcome reversal. |
| Right as stated (1) | k96 | Contradicts the Cleveland counts. |
| Indeterminate | k77 | |
| Not counted | k73, k120, k147, k145 | |

**Round-3 totals:**
- **32 direction-stating; 25 wrong (78%, 61–89%); 7 right; 9 rationalised.**
- **Sensitivity** (also dropping mixed k25 and mapping-unreliable k51): **20 of 27 (74%, 55–87%).**
- **Notable:** k73, a 2026 leakage audit devoted to the UCI heart data, calls asymptomatic chest pain a "clinically plausible" top SHAP feature and does not notice the reversal.

**Not counted** (importance without sign, numeric-only, single middle-category case, error analysis): k12, k58, k62, k70, k82, k84, k87, k113, k124, k130. **Indeterminate** (middle category only): k134.

## Strongest examples (verbatim, ≤25 words)
- **k123**, arXiv 2020, cited 188: "This may seem counterintuitive, but asymptomatic chest pain is actually the most severe out of the four types".
- **k29**, *J. Big Data* 2023, cited 256: "Patients with asymptomatic chest pain (ASY) are about six times more likely to suffer heart disease…"
- **k63**, IEEE 2026: "Asymptomatic chest pain is most predictive of heart disease … highlighting the need for proactive screening."
- **k65**, IEEE 2025: "…even the absence of classic chest pain can indicate a higher underlying risk."
- **k138**, *Sci. Rep.* 2026: proposes "reducing chest pain type" as an actionable intervention after cp = 4 "asymptomatic" drives a positive prediction.
- **k106**, ADCAIJ 2023: "Patients with asymptomatic chest pain type, which is encoded to 0 … are more likely to have heart disease". Code 0 in that Kaggle copy is UCI 4, which is truly typical angina.

## By copy (wrong statements)
- **UCI codes or UCI word labels** (Cleveland, Statlog, 4-site): k1, k18, k20, k21, k46, k54, k57, k68, k123, k131, k138.
- **fedesoriano 918 (ASY/TA words):** k17, k29, k36, k63, k65, k117.
- **Kaggle 1,025 (0 = UCI 4, 1 = UCI 2, 2 = UCI 3, 3 = UCI 1):** k98, k106.

## Limits
- **31% inaccessible**, concentrated in Springer, Elsevier and ResearchGate.
- **Screening relies on a regex sentence filter followed by hand reading.** Claims that appear only inside figures (SHAP plots) are not captured, so the counts are lower bounds.
- **The "not included" rows include papers whose figures may show a direction.**
