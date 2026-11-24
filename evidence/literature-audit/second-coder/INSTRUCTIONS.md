# Second-coder instructions (E8 literature audit)

**Purpose:** an independent check of the primary coding.
- There are 52 papers in random order, in `form.tsv`.
- Code each one from the paper itself.
- **Do not open `KEY-do-not-open-until-done.tsv`, `audit-150-summary.md`, `round3-access-notes.md`, `direction-stating-32.tsv` or the coding files until you have finished.**

**Time:** about 3 to 4 minutes per paper; most papers need only a word search.

## How to read each paper
1. Open the link.
   - IEEE and ProQuest items: sign in through the UC library first.
   - If a link fails: search the title in Google Scholar, or in UC Primo (ucumberlands.primo.exlibrisgroup.com).
2. Search the full text (Cmd-F) for "asymptomatic", "typical angina", "chest pain", "cp", "ASY" and "TA".
3. Read the results, discussion and explanation sections around those hits, including SHAP or LIME text and tables of rates by category.

## What to fill in (one row per paper)

| Column | What to write |
|---|---|
| **copy** | The dataset copy: UCI Cleveland 303/297, UCI 4-site 920, Statlog 270, the 1,190 merge, Kaggle 303 or 1,025 (cp coded 0–3), fedesoriano 918 (TA/ATA/NAP/ASY words), or unclear. Row counts and code ranges tell them apart. |
| **states_direction** | **Y** if the paper states which chest-pain category goes with more (or less) heart disease, from its data or model. Examples: "asymptomatic patients are more likely to have heart disease"; "cp = 4 has a positive SHAP value"; "typical angina lowers the predicted risk"; a rate by category given in words. **N** for importance without a sign ("chest pain type is the top feature"), numeric-only statements ("higher cp raises risk" with no category named), or background text not drawn from the paper's own data. |
| **category_named** | The category the statement names, in the paper's own label (e.g. "asymptomatic", "cp=0", "type 4", "ASY"). |
| **direction** | **higher** or **lower** risk, for that category. |
| **clinically_correct** | Is that statement medically sensible as written? Typical angina is the highest-likelihood presentation of coronary disease; asymptomatic, i.e. no chest pain, is the lowest. So "asymptomatic → higher risk" is **N**, and "typical angina → higher risk" is **Y**. Judge the statement as written; do not try to correct for data coding. |
| **rationalised** | **Y** if the paper explains the direction with a clinical reason (e.g. "silent ischaemia", "easily missed", "aligns with clinical findings"); otherwise **N**. |
| **quote** | The sentence, 25 words or fewer. |
| **notes** | Anything uncertain: hedged statements, single-patient explanations, contradictions. |

If a paper states more than one direction, code the clearest data-derived one and mention the rest in notes.

When you're done, tell Claude. It will run `uv run python code/blind_packet.py score`. It reports raw agreement and Cohen's kappa for the three-way outcome (no direction / wrong / right), for whether a paper states a direction, for the verdict, for rationalised and for the copy group; recomputes each of the paper's audit figures from your codes; and lists every disagreement for joint review.

## Form conventions
- **states_direction:** Y, N, or NA if you could not read the paper. When it is Y, **clinically_correct** and **rationalised** must each be Y or N.
- Keep `form.tsv` tab-separated. If you edit it in a spreadsheet, export as tab-separated text (UTF-8 if offered), not .xlsx or .csv.
- Fill **copy** for every paper you read (a blank copy is left out of the copy comparison). Use the names above (for example "UCI Cleveland 303", "Kaggle 1,025", "fedesoriano 918", "unclear"); the scorer maps them onto the paper's copy groups.
- Leave a row blank if you have not coded it yet; the scorer reports how many are done.
