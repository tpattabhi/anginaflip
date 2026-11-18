# Protocol: do the wrong chest-pain labels change what LLMs predict? (E9c)

**Fixed 17 Nov 2026, before any model was run.** Any later change is logged at the end with its date and reason.

## Question

LLM-based tabular methods turn each patient into text and rely on the model's medical knowledge. If the UCI chest-pain codes are read as documented, a patient with typical angina is described as "asymptomatic" and the reverse. Does that change the predictions?

## Data

- Primary: UCI Cleveland, 303 patients; outcome CAD = `num` > 0.
- Secondary (reported only if the primary result holds): UCI Hungarian, 294 patients.
- Source: the files in `evidence/uci-raw-archive/heart+disease.zip`. Missing values are written as "unknown".

## Conditions (chest-pain line only; everything else is identical)

| Condition | Text for code k |
|---|---|
| **D (documented)** | 1 typical angina, 2 atypical angina, 3 non-anginal pain, 4 asymptomatic (the UCI documentation) |
| **C (corrected)** | the same labels applied to 5 − k (verified against Detrano 1986 and the raw pain features) |
| **O (omitted)** | no chest-pain line |

## Templates

- **full:** all 13 predictors in clinical words, with units.
- **minimal:** age, sex and chest-pain type only (the predictors of Detrano 1986, Table 8).

## Models (open weights, run on free Google Colab)

Qwen2.5-7B-Instruct, OLMo-2-1124-7B-Instruct and Phi-3.5-mini-instruct. These need no licence acceptance. MedGemma-4B-it is optional and needs the user to accept its licence on Hugging Face. The 7B models are loaded in 4-bit (NF4); Phi-3.5 in fp16.

## Prediction

Zero-shot. The prompt ends with a yes/no question about CAD (more than 50% narrowing). The score is P(Yes) = p("Yes") / (p("Yes") + p("No")) from the first answer token's logits, so there is no sampling and no parsing. Each model's chat template is used.

## Outcomes

- **Primary:** ΔAUC = AUC(C) − AUC(D), full template, Cleveland, per model.
- **Secondary:** Δ log loss and Δ Brier score; the same for the minimal template; mean P(Yes) by chest-pain code under D and C.
- **Uncertainty:** paired bootstrap over patients, 2,000 resamples (seed 20261117), 95% percentile intervals.

## Hypotheses

- **H1:** AUC(C) > AUC(D) on the full template, with a 95% interval excluding 0, in at least 2 of 3 models.
- **H2:** the gap is larger with the minimal template than with the full one.
- **H3:** under C, mean P(Yes) rises from code 1 to code 4; under D it falls or stays flat.
- **Reported either way.** A null result is reported as one: if the models ignore chest-pain type, that is a finding too.

## What would count as "worthwhile" (decides whether to scale up on RunPod)

H1 holds in at least 2 models with ΔAUC ≥ 0.02, or H3 shows a reversal in at least 2 models.

## Change log

- **17 Nov 2026, ~22:55, before any model output existed.** The first Colab run's runtime disconnected while downloading the full-precision Qwen2.5-7B (probably out of memory on the free tier's 12.7 GB of RAM). No scores were produced. Changes:
  - **Pre-quantized 4-bit (bitsandbytes NF4) copies, pinned by commit:** `unsloth/Qwen2.5-7B-Instruct-bnb-4bit` (bdd404162d), `unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit` (f15c379fb3), `unsloth/Phi-3.5-mini-instruct-bnb-4bit` (5c20803aa1).
  - **OLMo-2-1124-7B-Instruct is replaced by Llama-3.1-8B-Instruct,** because no pre-quantized OLMo-2 copy exists. Phi-3.5 is now 4-bit instead of fp16.
  - One notebook cell per model, each printing its own summary.
  - Hypotheses, conditions, templates, prompts, metrics and thresholds are unchanged.
