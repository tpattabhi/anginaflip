# E2: stored chest-pain code vs. the raw angina features

Sites: Budapest (`hungarian.data`), Switzerland and Long Beach.

The raw 76-attribute records in `../uci-raw-archive/heart+disease.zip` include `painloc`, `painexer` and `relrest` (attributes 5–7): substernal location, provocation by exertion and relief by rest. These three features define typical angina.

The check is in `code/evidence_checks.py` (`check_raw_features`) and is tested in `tests/test_evidence.py`. `result.txt` is the original output from 17 Nov 2026.
