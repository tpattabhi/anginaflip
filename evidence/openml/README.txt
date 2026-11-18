OpenML copies downloaded 2026-11-17 via https://www.openml.org/api/v1/json/data/<id>.
49 heart-c (Cleveland, word labels), 51 heart-h (Hungarian, word labels), 53 heart-statlog, 194 and 786 cleveland (numeric codes), 1574 heart (unnamed attributes, 270 rows).
The check needs the UCI processed files: unzip ../uci-raw-archive/heart+disease.zip and pass that folder as the 2nd argument.

The check now lives in `code/evidence_checks.py` (tested in `tests/test_evidence.py`). `result.txt`, if present, is the original output from 17 Nov 2026.
