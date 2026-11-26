# AnginaFlip

**The chest-pain variable in the UCI Heart Disease data is stored in reverse of its documentation.**

In all four UCI files (Cleveland, Budapest, Switzerland, Long Beach) and in Statlog (Heart):
- the code documented as "typical angina" (1) identifies patients **without** chest pain;
- the code documented as "asymptomatic" (4) identifies patients **with typical angina**.

The error has been present since at least 1990. It has spread to OpenML, PMLB and the most-voted Kaggle copies that name the categories.

This repository holds the evidence, the analyses and the paper:

> T. T. Pattabhi, *Typical Angina, Reversed: A Long-Standing Documentation Error in the UCI Heart Disease Data*. Preprint, 24 Nov 2026: arXiv:[2611.33248](https://arxiv.org/abs/2611.33248) (`paper/`). An earlier version (18 Nov 2026), titled *Typical Angina, Reversed: A Chest-Pain Coding Error in the UCI Heart Disease Data That Has Persisted Since 1990*, is on Zenodo: doi:[10.5281/zenodo.24358545](https://doi.org/10.5281/zenodo.24358545)

## The correction

| Stored `cp` (UCI files, Statlog) | Documented label | Correct label |
|---|---|---|
| 1 | typical angina | asymptomatic (no chest pain) |
| 2 | atypical angina | non-anginal pain |
| 3 | non-anginal pain | atypical angina |
| 4 | asymptomatic | typical angina |

So the correct label of stored code `k` is the documented label of `5 - k`. Copies coded 0–3 use different transformations (below).

## Evidence

| | Check | Result | Code |
|---|---|---|---|
| E1 | Cleveland vs. Detrano et al. 1986 (*Circulation* 73:970), the same 303 patients | Table 1 is consistent in 15/16 cells only with the reversed reading (0/16 as documented). The Table 8 coefficients are reproduced only with `5 - cp` | `check_detrano1986` |
| E2 | Raw angina features (substernal, exertional, relieved by rest) at Budapest, Switzerland and Long Beach | Code 4 patients have all three features: 118/123, 91/98, 126/131. Code 1 patients have none: 10/11, 4/4, 8/8 | `check_raw_features` |
| E3 | `cleve.mod` (J. Gennari, 1990) | All 303 rows label code 1 `angina` and code 4 `asympt` | `check_cleve_mod` |
| E4 | Statlog (Heart) | A 270-patient Cleveland subset with identical codes and outcomes | `check_statlog` |
| E7 | Copies | OpenML `heart-c`/`heart-h` and PMLB (`UCI - 1`) use the documented labels. Kaggle fedesoriano and redwankarimsony write them as words. Kaggle johnsmith88 (1,025 rows) maps 0 = UCI 4, 1 = UCI 2, 2 = UCI 3, 3 = UCI 1, and reverses the outcome | `check_openml`, `check_pmlb`, `check_kaggle` |
| E8 | Literature audit, pre-specified protocol, 150 sampled papers | 124 readable; 32 state a direction; 25 are inconsistent with the corrected categories (78%, 95% CI 61–89%; pre-specified), 22 of them attributable to the documented labels (69%, 51–82%; defined after coding); none identifies the reversal | `evidence/literature-audit/` |
| E9 | Consequences | Classical models: discrimination essentially unchanged, interpretations of chest-pain effects reversed. LLM classifiers: worse with the documented labels | `code/invariance.py`, `code/llm_probe.py` |

## Reproduce

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest                               # asserts every E1-E4, E7 and E9(a-b) number in the paper
uv run python code/evidence_checks.py       # prints E1-E4 and E7 (OpenML, PMLB)
uv run python code/evidence_checks.py --copies   # adds the Kaggle copies, if downloaded (see below)
uv run python code/invariance.py            # E9(a-b): classical models under both codings
```

**LLM probe (E9c).** `code/build_notebook.py` writes `notebooks/llm_label_probe.ipynb`, which ran on a free Kaggle T4 GPU. The logs are in `results/llm_probe/`. The protocol is `PROTOCOL-llm-probe.md`.

**Literature audit (E8).**
- Protocol: `PROTOCOL-literature-audit.md`. Every change after the protocol was fixed is logged with its date.
- Sampling frame, sample and coding: in `evidence/literature-scholar/` and `evidence/literature-audit/`.
- Second-coder materials: `code/blind_packet.py` builds them, and `uv run python code/blind_packet.py score` reports agreement.

**Paper.** `paper/main.tex`. Build with [Tectonic](https://tectonic-typesetting.github.io/):

```bash
tectonic -X compile paper/main.tex
```

## Data sources and what is not redistributed

| Source | Location | Note |
|---|---|---|
| UCI Heart Disease, doi:10.24432/C52P4X | `evidence/uci-raw-archive/heart+disease.zip` | Includes the raw 76-attribute files and `cleve.mod` |
| UCI Statlog (Heart), doi:10.24432/C57303 | `evidence/statlog-check/` | |
| OpenML datasets 49, 51, 53, 194, 786 and 1574 | `evidence/openml/` | |
| PMLB `heart_disease_*` | `evidence/pmlb/` | |
| **Kaggle copies** | **not redistributed** | Download from `https://www.kaggle.com/datasets/<owner>/<slug>` into `evidence/kaggle/<owner>_<slug>/`. The slugs are listed in `evidence/kaggle/README.md` |
| **Detrano et al. 1986 and other papers** | **not redistributed** | Cited in the paper |

Third-party data remain under their original terms; see each source.

## Licence

- **Code:** MIT (`LICENSE`).
- **The author's own text, tables and coding data:** CC BY 4.0.

## Citation

See `CITATION.cff`.
