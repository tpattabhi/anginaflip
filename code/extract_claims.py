"""Pull chest-pain sentences and dataset clues out of a paper's text (PDF or plain text), for E8 coding."""

import re
import sys

from pypdf import PdfReader

TOPIC = re.compile(r"asymptomatic|typical angina|chest[- ]pain|\bASY\b|\bcp\b|anginal", re.I)
DIRECTION = re.compile(
    r"asymptomatic|typical angina|\bASY\b|\bTA\b|cp[_ =]?[0-4]|type[ _-]?[0-4]"
    r"|(high|higher|low|lower|increas|decreas)[^.]{0,25}\b(cp|chest pain)\b"
    r"|\b(cp|chest pain( type)?)\b[^.]{0,35}(high|higher|low|lower|increas|decreas|positive|negative)",
    re.I,
)
SIZE = re.compile(r"[^.]{0,60}\b(303|297|1025|1,025|918|270|920|1190|1,190)\b[^.]{0,40}")


def text_of(path: str) -> str:
    if path.lower().endswith(".pdf"):
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    return open(path, errors="replace").read()


def main(path: str):
    t = re.sub(r"\s+", " ", text_of(path))
    sents = re.split(r"(?<=[.!?])\s+", t)
    hits = [s[:230] for s in sents if TOPIC.search(s) and DIRECTION.search(s)]
    print(f"chars={len(t)} kaggle={'kaggle' in t.lower()}")
    for h in hits[:10]:
        print(" -", h)
    for m in list(SIZE.finditer(t))[:4]:
        print(" size:", m.group(0))


if __name__ == "__main__":
    main(sys.argv[1])
