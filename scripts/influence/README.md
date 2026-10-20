# Influence scan

How `data/influence.csv` and `data/influence-parliament.csv` were built: `enumerate.py` lists GOV.UK transparency releases, `scan.py` searches each attachment for Palantir, `returns_rows.py` and `rows.py` turn matches into rows, `curated.py` and `augment.py` add hand-checked rows, `build.py` writes the CSVs. `fetch_all_parl.sh` and `lords.sh` pull the parliamentary record from the Parliament APIs. Downloaded attachments are cached locally and not published.
