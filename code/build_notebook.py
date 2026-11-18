"""Build the self-contained Colab notebook from llm_probe.py (the single source of the analysis code).

Run: uv run python code/build_notebook.py
"""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
MODULE = (ROOT / "code" / "llm_probe.py").read_text()
OUT = ROOT / "notebooks" / "llm_label_probe.ipynb"

MODELS = [
    ("unsloth/Qwen2.5-7B-Instruct-bnb-4bit", "bdd404162d94997f390efbfa660eb3f21cbbc81d"),
    ("unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit", "f15c379fb32bb402fa06a7ae9aecb1febf4b79ec"),
    ("unsloth/Phi-3.5-mini-instruct-bnb-4bit", "5c20803aa197416f43fb455e55c85178775320cb"),
]

SCORER = """import gc, time, torch, numpy as np, pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)

def first_token(tok, word):
    return tok.encode(word, add_special_tokens=False)[0]

def score_model(model_id, revision, jobs, batch_size=8):
    \"\"\"P(Yes) for every prompt; the model is a pre-quantized 4-bit checkpoint pinned by commit.\"\"\"
    tok = AutoTokenizer.from_pretrained(model_id, revision=revision)
    tok.padding_side = 'left'
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id, revision=revision, device_map='cuda').eval()
    yes, no = first_token(tok, 'Yes'), first_token(tok, 'No')
    texts = [tok.apply_chat_template([{'role': 'user', 'content': p}], tokenize=False,
                                     add_generation_prompt=True) for p in jobs.prompt]
    ly, ln = [], []
    t0 = time.time()
    for i in range(0, len(texts), batch_size):
        enc = tok(texts[i:i + batch_size], return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
        with torch.no_grad():
            logits = model(**enc).logits[:, -1, :].float()
        ly += logits[:, yes].tolist(); ln += logits[:, no].tolist()
    print(model_id, f'{time.time() - t0:.0f}s scoring', 'yes/no token ids', yes, no)
    out = jobs.drop(columns='prompt').copy()
    out['model'] = model_id.split('/')[-1]
    out['logit_yes'], out['logit_no'] = ly, ln
    out['p_yes'] = lp.p_yes(out.logit_yes, out.logit_no)
    del model; gc.collect(); torch.cuda.empty_cache()
    return out

COLS = ['model', 'template', 'auc_D', 'auc_C', 'auc_O', 'd_auc_C_minus_D', 'd_auc_lo', 'd_auc_hi',
        'd_log_loss_C_minus_D', 'd_log_loss_lo', 'd_log_loss_hi']

def report(scored):
    print(lp.summarise(scored)[COLS].round(3).to_string(index=False))
    print(lp.mean_p_by_code(scored).round(3).to_string(index=False))
"""

cells = [
    nbf.v4.new_markdown_cell(
        "# AnginaFlip: LLM label probe (E9c)\n\n"
        "Protocol: `PROTOCOL-llm-probe.md` (fixed before any run; see its change log). "
        "**Runtime > Change runtime type > T4 GPU**, then **Runtime > Run all**.\n\n"
        "Each model scores every Cleveland patient under documented (D), corrected (C) and omitted (O) "
        "chest-pain labels, with a full and a minimal template. One cell per model; each prints its own results."
    ),
    nbf.v4.new_code_cell(
        "%env HF_HUB_DISABLE_XET=1\n!pip -q install -U bitsandbytes accelerate\n"
        "!nvidia-smi --query-gpu=name,memory.total --format=csv\n!free -g | head -2\n!df -h /content | tail -1"
    ),
    nbf.v4.new_code_cell("%%writefile llm_probe.py\n" + MODULE),
    nbf.v4.new_code_cell(
        "import urllib.request, hashlib\n"
        "URL = 'https://archive.ics.uci.edu/static/public/45/heart+disease.zip'\n"
        "urllib.request.urlretrieve(URL, 'heart+disease.zip')\n"
        "print('sha256', hashlib.sha256(open('heart+disease.zip','rb').read()).hexdigest())\n"
        "import llm_probe as lp\n"
        "cle = lp.load_uci('heart+disease.zip')\n"
        "jobs = lp.build_jobs(cle)\n"
        "print(len(cle), 'patients;', len(jobs), 'prompts per model')\n"
        "print(jobs.prompt.iloc[0])"
    ),
    nbf.v4.new_code_cell(SCORER),
]
for i, (mid, rev) in enumerate(MODELS):
    name = mid.split("/")[-1]
    cells.append(
        nbf.v4.new_code_cell(
            "import os; os.environ['HF_HUB_DISABLE_XET'] = '1'\n"
            f'!HF_HUB_DISABLE_XET=1 python -c "from huggingface_hub import snapshot_download as d; '
            f"print(d('{mid}', revision='{rev}'))\" 2>&1 | tail -3\n"
            "!free -g | head -2\n"
            f"s{i} = score_model({mid!r}, {rev!r}, jobs)\n"
            f"s{i}.to_csv('scores_{name}.csv', index=False)\n"
            f"report(s{i})"
        )
    )
cells.append(
    nbf.v4.new_code_cell(
        "import glob\n"
        "scored = pd.concat([pd.read_csv(f) for f in sorted(glob.glob('scores_*.csv'))], ignore_index=True)\n"
        "scored.to_csv('all_scores.csv', index=False)\n"
        "summ = lp.summarise(scored); summ.to_csv('summary.csv', index=False)\n"
        "report(scored)"
    )
)

nb = nbf.v4.new_notebook(cells=cells, metadata={"accelerator": "GPU", "colab": {"gpuType": "T4"}})
OUT.parent.mkdir(exist_ok=True)
nbf.write(nb, OUT)
print("wrote", OUT)
