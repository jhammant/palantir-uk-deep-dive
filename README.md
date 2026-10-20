# Palantir UK Deep Dive

Palantir in the UK, from the public record.

An open dataset of what UK public bodies have bought from Palantir, what they paid, what Palantir
UK pays in tax, and what its leaders have said. Every row traces to a public source: a contract
notice, a set of filed accounts, a transparency release, or a published quote.

The rule for this project is simple: **if it isn't in a public record we can link to, it isn't in
the data.** Opinion belongs in commentary, never in the dataset.

## What's here

| File | What it holds | Source |
|---|---|---|
| `data/contracts.csv` / `.json` | Every contract award where Palantir is the sole named supplier: buyer, value, dates, procurement route, the buyer's stated reason for any direct award, and a link to the notice | Contracts Finder, Find a Tender |
| `data/tax.csv` | Palantir Technologies UK, Ltd. turnover, UK turnover, profit, tax charge and UK corporation tax by year, with page references | Companies House 07042994 filed accounts |
| `data/quotes.json` | Verbatim quotes from Palantir's founders and leaders, with context and any later clarification | Their own writing, recordings, transcripts, reports |
| `data/payments.csv` | Money actually paid, from departmental and local spend files and FOI answers (in progress) | GOV.UK spend data, police, NHS and council spend files, WhatDoTheyKnow |
| `data/influence.csv` | Ministerial meetings, ACOBA advice, lobbying registers, the parliamentary record (in progress) | GOV.UK transparency releases, ACOBA, Hansard |
| `data/timeline.csv` | UK events from 2009 to today (in progress) | Official and press sources, marked |
| `sources/` | The raw API responses, the accounts PDFs and the OCR text of every page a figure came from | |
| `img/` | Shareable graphics built from the data (HTML source + rendered PNG) | |

## Headline numbers (20 Oct 2026)

- **30 contract awards since 2015, £647.1m as published.** Values are as each buyer published them;
  some are ex-VAT and some inc-VAT, and framework places with dozens of suppliers are left out.
- **The two biggest awards of the past year were direct awards with no competition:** the MoD's
  £240.6m enterprise agreement (Dec 2025) and NESO's £21.2m interim contract (Aug 2026).
- **NESO's own justification:** its systems are "underpinned by proprietary architecture licensed
  exclusively by Palantir", and "Transitioning to an alternative supplier is not possible without
  significant cost, resource commitment and delivery risk".
- **NHS England** signed a £24.9m "Palantir Foundry Transition & Exit Contract" in June 2023 to move
  off Palantir Foundry to the winner of the new Federated Data Platform. Palantir won that platform
  in November 2023.
- **Palantir UK's 2025 accounts** (filed 7 Oct 2026): UK turnover £236.4m, profit before tax £25.1m,
  UK corporation tax £1.4m (total tax charge £1.9m against £6.3m at the 25% headline rate). The
  accounts' tax reconciliation gives share option timing differences and unrecognised deferred tax
  as the main reasons. This is lawful.

## The site

`site/` is a static site that lets anyone explore the data: an overview, a contracts explorer
(search, filter by sector, route and year, shareable links, CSV download), payments, tax, lock-in,
people, influence, a timeline and the method. No framework and no server.

```bash
python3 scripts/build_site.py   # bundle data/ into site/assets/bundle.js
open site/index.html            # works straight from disk
```

`.github/workflows/pages.yml` publishes `site/` to GitHub Pages on every push to `main`, and
refreshes the contracts from the government APIs once a day.

## Rebuild the contracts data

```bash
python3 scripts/fetch_contracts.py
```

It searches Contracts Finder for awarded notices naming Palantir, reads each one in full, then reads
every Find a Tender procurement listed in `sources/fts_ocids.txt`. To track a new procurement, add
its OCID to that file and rerun. Raw responses land in `sources/raw/`.

## Known gaps

- Find a Tender has no keyword API, so procurements that appear only there have to be added to
  `sources/fts_ocids.txt` by hand. Police pilots bought through other routes (e.g. Project Nectar)
  may not appear in notices at all; `data/payments.csv` is where they show up.
- Contract values are ceilings or estimates at award; payments can be lower or higher.
- Press reports put the total of UK public contracts with Palantir at close to £1bn; the gap is
  partly notices outside these two services and partly how extensions are counted.

## Corrections

If a figure here is wrong, open an issue with the source and it will be fixed and noted in the
changelog. Palantir and any public body named are welcome to send corrections the same way.

## Disclosure

Compiled by Jon Hammant, CEO of Orbital, a UK data integration company that works in the same
market as Palantir. Everything in `data/` is public record so that anyone can check it rather than
take anyone's word for it.

## Licence

Data: public sector information under the Open Government Licence v3.0, plus our compilation under
CC BY 4.0. Code: MIT.
