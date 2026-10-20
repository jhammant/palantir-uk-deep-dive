# Payments pipeline

How `data/payments.csv` was built from published spend files and FOI answers.

1. `govuk_enum.py` / `select_jobs.py` list the spend files to check for each payer.
2. `fetch_scan.py` downloads each file into `sources/raw/payments/<payer>/` (kept locally, not published) and records it in the manifest, which is published as `data/payments-files-checked.csv`.
3. `extract.py` pulls every row that mentions Palantir; `att_text.py` and `wdtk_dl.py` handle PDF attachments and WhatDoTheyKnow FOI answers.
4. `build_payments.py` writes `data/payments.csv`; `verify.py` re-checks every row against its saved file.

Intermediate files live in `sources/raw/payments/_work/`. Some police and FOI pages sit behind bot challenges and were read by hand at a slow pace; those rows cite their page URLs.
