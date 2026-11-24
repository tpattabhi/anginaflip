# AnginaFlip: overnight results and go/no-go (18 Nov 2026)

## Bottom line
**GO.** Every pillar is backed by data:
1. The reversal is established by two independent checks (the original 1986 study; the sites' raw angina features). The error is dated to 1990 or earlier, and Statlog (Heart) inherits it.
2. It spread to every major distribution channel (≈676K Kaggle downloads (18 Nov) across the two biggest copies, OpenML, PMLB).
3. Published papers read it as medicine: across the full 150-paper sample (124 full texts read), 25 of 32 direction-stating papers state a direction inconsistent with the corrected categories (78%, pre-specified); 22 of 32 are attributable to the documented labels (69%, defined after coding); none identifies the reversal. Row-level table: `evidence/literature-audit/direction-stating-32.tsv`.
4. **It changes LLM predictions.** With the documented labels, LLMs lose 0.12–0.33 AUC on the age/sex/chest-pain task (all 3 models, CIs exclude 0), and 0.016–0.077 on the full task in 2 of 3 models.

**Recommended route:** arXiv preprint first, then a full paper (DMLR, or the NeurIPS Datasets & Benchmarks track). Section 4 makes it an AI paper, not just an erratum.

**RunPod: not yet.** The pre-set "worthwhile" rule is strictly met by only 1 of 3 models on the full template. The next cheap step is to pull the per-patient CSVs from Kaggle to test H3 precisely, and optionally to add one larger free model on Kaggle.

## 1. The error is real: two independent checks, a dating and an inherited copy
| Check | Result | Evidence |
|---|---|---|
| Cleveland vs. the original 1986 paper (Detrano, *Circulation*) | Table 1 matches only with codes reversed (15/16 cells); Table 8 coefficients reproduced only reversed | `evidence/detrano1986/` |
| Budapest, Switzerland, Long Beach vs. their own raw pain features | "Asymptomatic" (code 4) patients have all three classic angina features (118/123, 91/98, 126/131) | `evidence/raw-pain-features/` |
| Origin | Already present in Gennari's 1990 word-labelled version (303/303 rows) | `evidence/cleve-mod/` |
| Statlog (Heart) | A 270-patient Cleveland subset with identical codes | `evidence/statlog-check/` |

## 2. It spread to every major distribution channel
| Channel | Status | Reach |
|---|---|---|
| UCI page | Still documents 1 = typical angina | 1.26M views |
| Kaggle, fedesoriano "Heart Failure Prediction" | Wrong, **in words** (TA = no pain) | 290K downloads, 1,993 notebooks, 1.58M views |
| Kaggle, David Lapp (johnsmith88) | end codes swapped (0 = UCI 4, 3 = UCI 1); **outcome also reversed** | 386K downloads, 1.64M views (18 Nov) |
| Kaggle, redwankarimsony | Wrong, in words | 112K downloads |
| OpenML heart-c, heart-h | Wrong, in words | — |
| PMLB (current) | Documents "0 = typical angina" for UCI code 1, so wrong | — |

## 3. Published papers read the error as medicine
Pre-specified protocol (`PROTOCOL-literature-audit.md`): a frame of 269 Google Scholar records, 230 eligible, seeded random order. **All 150 sampled items coded** (18 Nov, with UC library access to IEEE and ProQuest). Summary: `evidence/literature-audit/audit-150-summary.md`.
- **124 of 150 full texts accessible.**
  - Round 2: 104, read through UC IEEE and ProQuest.
  - Round 3 added 16 (`evidence/literature-audit/round3-access-notes.md`), through:
    - UC Primo's link resolver to EBSCO Academic Search Complete, which holds some Springer and Wiley journals;
    - open repository copies;
    - preprint servers.
  - Round 3b added 4 more after the user cleared the ScienceDirect check and accepted the Sage terms.
  - 26 remain inaccessible: Elsevier paywall (5), Springer/T&F/World Scientific/Wiley CPE/SPIE/IGI items not held by UC, book chapters, Google Books previews, and dead links.
- **32 state a direction for a named chest-pain category: 25 are clinically wrong (78%; 95% CI 61–89%).** Sensitivity, dropping the illustrative, hedged, single-patient, mixed and unreliable-mapping cases: 20 of 27 (74%; 55–87%).
- **9 of the 25 explain the wrong direction clinically:**
  - "silent ischaemia";
  - "asymptomatic chest pain is actually the most severe out of the four types" (arXiv 2020, cited 188);
  - "highlighting the need for proactive screening";
  - "reducing chest pain type" as an actionable intervention;
  - "aligning with clinical findings that many severe cardiovascular conditions present with minimal symptoms" (Wiley *Comput. Intell.* 2025).
- **Even a 2026 leakage audit of this exact dataset** calls asymptomatic chest pain a "clinically plausible" top SHAP feature and does not notice the reversal.
- **None of the 7 "correct" statements reflects the true coding:**
  - 3 contradict their own coding tables or their own data;
  - 2 come from Kaggle copies with a second (outcome) reversal;
  - 1 has an internally inconsistent mapping;
  - 1 names no copy.
  - **So no paper in the sample identifies the reversal.**
- The wrong statements span every copy: UCI codes and words (15), fedesoriano 918 (6), Kaggle 303/1,025 (4).
- **Limit:** figure-only claims (SHAP plots) are not captured, so the counts are lower bounds.

## 4. Consequences for models
- **E9(a–b), done:** logistic models give identical predictions under both codings; trees differ by AUC ≤ 0.002. That is why benchmark use never caught it. The explanations flip: read with the documented labels, "asymptomatic" gets coefficient +0.48.
- **E9(c), the LLM probe (protocol fixed before any run; Kaggle T4, 3 open models, 303 patients × 6 prompts each):**

| Model | Template | AUC documented | AUC corrected | AUC no chest pain | ΔAUC (C − D) [95% CI] | Δ log loss (C − D) [95% CI] |
|---|---|---|---|---|---|---|
| Qwen2.5-7B | full | 0.844 | 0.861 | 0.859 | **+0.016** [0.004, 0.030] | −0.128 [−0.215, −0.042] |
| Qwen2.5-7B | minimal | **0.458** | 0.789 | 0.637 | **+0.331** [0.240, 0.425] | −1.788 [−2.108, −1.487] |
| Llama-3.1-8B | full | 0.512 | 0.589 | 0.477 | **+0.077** [0.043, 0.114] | −0.110 [−0.139, −0.082] |
| Llama-3.1-8B | minimal | 0.542 | 0.779 | 0.626 | **+0.238** [0.145, 0.338] | −0.846 [−1.003, −0.700] |
| Phi-3.5-mini | full | 0.855 | 0.856 | 0.837 | +0.002 [−0.012, 0.016] | −0.107 [−0.148, −0.067] |
| Phi-3.5-mini | minimal | 0.673 | 0.795 | 0.638 | **+0.122** [0.056, 0.191] | −0.955 [−1.127, −0.798] |

  - **H1** (full template, corrected > documented, CI excludes 0, in ≥2 of 3 models): **supported** (Qwen, Llama; Phi not).
  - **H2** (gap larger with the minimal template): **supported in all 3**.
  - **H3** (risk rises with true severity under C, falls under D): **clear in Llama.** Minimal template, mean P(disease) by code 1→4: corrected 0.02→0.29, documented 0.29→0.02. Qwen (full): corrected 0.19→0.58, documented 0.32→0.49 (flattened, not reversed). Qwen-minimal and Phi probabilities round to 0, so a precise test needs the per-patient CSVs.
  - **Log loss** is better with the corrected labels in all 6 comparisons (every CI excludes 0).
  - With age, sex and chest pain only, the documented labels make Qwen **worse than chance (AUC 0.458)** and Qwen and Llama worse than omitting chest pain altogether.
  - **Pre-set 'worthwhile' rule** (H1 in ≥2 models with ΔAUC ≥ 0.02, or an H3 reversal in ≥2 models): met by Llama on both clauses; Qwen's full-template ΔAUC is 0.016, just under the bar. So, **strictly, met by 1 model on the full template.** The minimal-template effects (+0.12 to +0.33, all significant) are large, but the rule was written for the full template. This is reported as is, without moving the goalposts.

## Risks and open items
- **Novelty:** no prior report found (4 search passes, 16 Nov). Re-check before posting.
- **Overlap with the EMBC paper** (contribution i): cite it and disclose.
- **Literature coverage:** 17% of the sample (26 of 150) is still inaccessible: paywalls not held by UC, book chapters, previews and dead links. Interlibrary loan is the only remaining route.
- **LLM limits:** small open models (≤8B, 4-bit); a single prompt format; per-patient CSVs still on Kaggle.
