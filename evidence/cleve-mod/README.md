# E3: `cleve.mod` (John Gennari, March 1990)

`cleve.mod` is the word-labelled Cleveland file in `../uci-raw-archive/heart+disease.zip`. Joined to `processed.cleveland.data`, all 303 rows map code 1 to `angina`, 2 to `abnang`, 3 to `notang` and 4 to `asympt`.

The check is in `code/evidence_checks.py` (`check_cleve_mod`) and is tested in `tests/test_evidence.py`. `result.txt` is the original output from 17 Nov 2026.
