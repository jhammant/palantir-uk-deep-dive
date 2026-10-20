# Payments to Palantir by UK public bodies: notes

This file explains `data/payments.csv`. That file lists money actually paid to Palantir, as shown in published spend files ("spend over £25,000" for central government and the NHS, "over £500" for police and councils) and in Freedom of Information (FOI) responses. Contract notices are in `data/contracts.csv` and are not repeated here.

Checked up to 20 October 2026.

## How the data was built

- Every spend file listed below was downloaded and every row was searched for the text "palantir" (in any column, any case).
- Each matching row became one row in `payments.csv`, with the amount, date, supplier name and descriptive columns copied as published.
- All 240 rows were checked again against their saved source files. The saved copies are under `sources/raw/payments/<payer>/` with their original file names. That folder is kept locally and is not published (see `.gitignore`); each row's `source_file_url` is the official address of its file.
- `sources/raw/payments/manifest.csv` lists every file checked, including the ones with no Palantir rows. For each it gives the source URL, the saved path, the SHA-256 hash, the number of rows scanned, the number of rows that mention Palantir, and any fetch error. The manifest is the record of what was searched and came back empty.
- No amount was estimated or inferred. Dates are converted to ISO format (`YYYY-MM-DD`); each row's `notes` column also gives the date exactly as published.

## Totals

These totals count only rows where the published supplier name is Palantir. They are net of credit notes: there are 7 negative rows totalling -£6,270,023.23, all from NHS England. The FOI figure is reported separately in its own section, because it is an aggregate and overlaps the spend-file rows.

### By payer

| Payer | Rows | Total (£) | First row | Last row |
|---|---:|---:|---|---|
| NHS England (includes Arden & GEM CSU and North of England CSU entities) | 138 | 213,787,695.47 | 2020-09-30 | 2025-09-30 |
| Cabinet Office | 47 | 31,906,662.50 | 2021-01-20 | 2023-11-21 |
| MHCLG (DLUHC from Sep 2021 to Jul 2024) | 14 | 15,625,000.00 | 2022-10-27 | 2025-09-30 |
| Ministry of Defence | 8 | 7,666,100.00 | 2020-05-21 | 2022-10-14 |
| Bedfordshire Police | 8 | 3,594,000.00 | 2023-11-14 | 2025-11-30 |
| Department of Health and Social Care | 9 | 3,080,000.02 | 2020-07-13 | 2022-03-31 |
| Chelsea and Westminster Hospital NHS FT | 3 | 2,310,000.00 | 2022-06-07 | 2026-03-17 |
| Coventry City Council | 3 | 1,250,000.00 | 2025-03-20 | 2026-08-04 |
| Defra | 3 | 346,875.00 | 2023-11-02 | 2024-06-13 |
| London Ambulance Service NHS Trust | 1 | 100,200.00 | 2023-04-14 | 2023-04-14 |
| Cambridgeshire Constabulary | 1 | 11,998.80 | 2025-08-05 | 2025-08-05 |
| **Total** | **235** | **279,678,531.79** | | |

### By calendar year (date of payment as published)

| Year | Total (£) |
|---|---:|
| 2020 | 7,896,500.02 |
| 2021 | 48,601,250.00 |
| 2022 | 28,427,610.81 |
| 2023 | 58,938,518.76 |
| 2024 | 48,960,649.35 |
| 2025 | 85,504,002.85 |
| 2026 (to September) | 1,350,000.00 |

The 2025 and 2026 figures are incomplete. NHS England, the largest payer, had published files only to September 2025 when this was checked (its 2026 page returned "not found").

### By payer and year (£)

| Payer | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|
| NHS England | 900,000.00 | 31,800,000.00 | 13,321,760.81 | 45,666,500.01 | 40,897,430.60 | 81,202,004.05 | not yet published |
| Cabinet Office | | 16,801,250.00 | 7,006,250.00 | 8,099,162.50 | | | |
| MHCLG / DLUHC | | | 3,600,000.00 | 4,650,000.00 | 4,875,000.00 | 2,500,000.00 | |
| Ministry of Defence | 4,816,500.00 | | 2,849,600.00 | | | | |
| Bedfordshire Police | | | | 300,000.00 | 2,004,000.00 | 1,290,000.00 | |
| DHSC | 2,180,000.02 | | 900,000.00 | | | | |
| Chelsea and Westminster | | | 750,000.00 | | 960,000.00 | | 600,000.00 |
| Coventry City Council | | | | | | 500,000.00 | 750,000.00 |
| Defra | | | | 122,656.25 | 224,218.75 | | |
| London Ambulance Service | | | | 100,200.00 | | | |
| Cambridgeshire Constabulary | | | | | | 11,998.80 | |

### Detail within the largest payers

- **NHS England, by entity:** NHS England £210,682,695.47; Arden & GEM CSU £1,800,000.00 (2020–2021); NHS North of England CSU £1,305,000.00 (2022–2023).
- **NHS England, by expense area as published:** NHS England Central Programme Costs £93,270,169.89; Digital Transformation £58,358,363.47; CSUs £33,280,360.82; Public Health £22,771,000.00; NHS England Running Costs £5,613,107.29; Specialised Commissioning £494,694.00.
- **Cabinet Office, by expense area as published:** BPDG – Future Borders £13,020,000.00; Border Flow Service £9,692,062.50; BPDG – Contingency £8,625,000.00; BPDG – Border Readiness £569,600.00.

### Rows to read with care

- **DHSC, 2020:** the December 2020 file lists four invoices that also appear in earlier DHSC files: INV-003633 (July 2020), INV-003686 (August 2020), and INV-003723 and INVE00100771 (October 2020). Each is £272,500.00 or £272,500.01, and the four together come to £1,090,000.01. All eight rows are kept as published and counted in the totals. The files do not say whether the December rows are repeat postings.
- **NHS England, February 2021:** transaction 35613340 (£300,000) appears twice in the same file, under two different expense areas (CSUs, and NHS England Running Costs). Both rows are kept.
- **Credit notes:** NHS England publishes credit notes as negative rows (for example, CME00101375 for -£1,050,000 in August 2023, against invoice INVE00101375). They are kept and netted in the totals.
- **Cabinet Office:** several transaction numbers cover more than one line in the same file. For example, 1037145647 in August 2022 has five lines. Each line has its own row number in the published file and is kept.

## Rows excluded from the totals

These rows mention Palantir only in their description; the published supplier is a different body. They are in `payments.csv` and flagged "SUPPLIER IS NOT PALANTIR" in the `notes` column.

| Payer | Date | £ | Supplier as published | Description as published |
|---|---|---:|---|---|
| DHSC | 2022-07-05 | 2,064,705.89 | NHS ENGLAND CBA033 | Foundry (Palantir) 2020-21 |
| Defra | 2023-02-01 | 325,833.33 | CABINET OFFICE | Recharges Cabinet Officer to Northern Ireland Directorate for Extension of Palantir contract |
| UKHSA | 2021-09-21 | 50,000.00 | MOZAIC SERVICES LIMITED | Dashbd from Palantir to EDGE |
| UKHSA | 2021-09-30 | 50,000.00 | MOZAIC SERVICES LIMITED | Dashbd from Palantir to EDGE |

## FOI disclosures of amounts paid

| Body | FOI reference | What it says | Request URL |
|---|---|---|---|
| Ministry of Defence | FOI2024/04261, response dated 3 July 2024 | "The amount spent from 01/01/2021, for contracts that can be published, is £79,100,169.11." | https://www.whatdotheyknow.com/request/palantir_contracts_foi_request_u_19 |

The request asked for payments since 1 January 2022, but the response gives a figure from 1 January 2021. The figure covers only contracts "that can be published"; details of other contracts were withheld under FOIA sections 24, 26 and 43. This is one row in `payments.csv` and it is not included in the totals above.

Other FOI material read, none of which disclosed an amount paid to Palantir:

- **WhatDoTheyKnow requests** (request pages and the response attachments that could be retrieved):
  - Ministry of Defence: `palantir_22`, `agreement_awarded_to_palantir_te`
  - Leicestershire Constabulary: `palantir_contract`, `palantir_contract_correspondence`, `redacted_palantir_contract`, `palantir_nectar_systems`. The redacted contract released through the last two contains liability caps (£1,000,000 and £5,000,000) but no charges or payments.
  - Cabinet Office: `palantir_technologies_use_by_cab`, `contracts_with_palantir`
  - Other police: Civil Nuclear Police Authority `palantir_technologies_active_con`; Northumbria Police `use_of_palantir_technologies_sof_31`; Metropolitan Police Service `palantir_technologies_products_u_4`; Devon and Cornwall Police `palantir_48`; Bedfordshire Police (joint Bedfordshire, Cambridgeshire and Hertfordshire response) `use_of_palantir_technologies_sof_2`
  - Other central bodies: University of Nottingham `uon_and_palantir`; HMRC `palantir_pilot_project_agreement`; DWP `access_or_use_of_palantir_techno`; Home Office `palantir_technologies_products_u_3`, `data_processing_by_palantir_for`
  - NHS: NHS England `nhs_england_and_palantir`; Oxford University Hospitals `palantir_and_nhs_foi_request_73`; Doncaster and Bassetlaw `palantir_and_nhs_foi_request_21`; North West Anglia `information_regarding_palantir`; Imperial College Healthcare `palantirfederated_data_platform`; Tavistock and Portman `foi_request_to_the_trust_regardi_97`; Chelsea and Westminster `freedom_of_information_request_a_1774`

  Each is at `https://www.whatdotheyknow.com/request/<name>`.
- **Attachments not retrieved:** one attachment returned "forbidden" (the Tavistock and Portman response) and is not covered. All other document attachments on these requests were read.
- **University Hospitals of North Midlands, FOI 2024/25-073** (5 August 2024, published by the trust): it states "No capital spend for Palantir Foundry" to the end of April 2024. Saved at `sources/raw/payments/university-hospitals-of-north-midlands/`. It is not a payment row.

## Coverage achieved

| Source | Files checked | Months covered | Rows naming Palantir as supplier |
|---|---:|---|---:|
| Ministry of Defence, spend over £25,000 (GOV.UK) | 75 | Jan 2020 – Mar 2026 | 8 |
| DHSC, spending over £25,000 (GOV.UK) | 76 | Jan 2020 – Apr 2026 | 9 |
| Cabinet Office, spend data over £25,000 (GOV.UK) | 84 | Jan 2020 – Aug 2026 | 47 |
| MHCLG / DLUHC, spending over £250 / £25,000 (GOV.UK) | 78 | Jan 2020 – Jun 2026 | 14 |
| Defra, spending over £25,000 (GOV.UK) | 73 | Jan 2020 – Feb 2026 (no files listed for Feb and Jun 2020) | 3 |
| HM Treasury, spend over £25,000 (GOV.UK) | 75 | Jan 2020 – Mar 2026 | 0 |
| Home Office, spending over £25,000, core department files only (GOV.UK) | 93 | Jan 2020 – Jul 2026 (no file listed for Jul 2025) | 0 |
| UKHSA / PHE, spend over £25,000 (GOV.UK) | 80 | Jan 2020 – Aug 2026 | 0 |
| Department for Business and Trade, spending over £25,000 (GOV.UK) | 37 | Mar 2023 – Jul 2026 (no files listed for Apr–Jul 2023) | 0 |
| NHS England, payments over £25k reports (england.nhs.uk) | 69 | Jan 2020 – Sep 2025 | 138 |
| Monitor and NHS TDA (NHS Improvement), expenditure over £25,000 | 11 | 2019/20 – 2022/23 files | 0 |
| Chelsea and Westminster Hospital NHS FT, expenditure over £25,000 | 56 | Jan 2022 – Aug 2026 | 3 |
| London Ambulance Service NHS Trust, spend over £25,000 | 76 | Jan 2020 – Aug 2026 (Jul 2024, May 2026 and Jun 2026 links returned "not found"; the Jan and Feb 2025 links point to the same file) | 1 |
| Bedfordshire Police, payments over £500 (beds.police.uk) | 80 | Feb 2020 – Sep 2026 | 8 |
| Cambridgeshire PCC, transactions over £500 (force and PCC) | 66 | Apr 2021 – Sep 2026 | 1 |
| Hertfordshire PCC, transaction disclosure reports (PCC office only) | 30 | Jan 2023 – Jun 2025 | 0 |
| Coventry City Council, spend over £500 | 24 | Oct 2024 – Sep 2026 | 3 |

In total, 1,083 spend files and 2 FOI documents were saved (about 288 MB).

## What is missing

- **Ministry of Defence after October 2022.** The MoD files from November 2022 to March 2026 contain no row naming Palantir. The MoD's finance transparency collection includes a 2010 publication titled "MOD spending over £25,000: exemptions": https://www.gov.uk/government/publications/ministry-of-defence-and-mod-family-spend
- **NHS England after September 2025.** Not yet published when checked.
- **Hertfordshire Constabulary (force spend).** The force's list of expenditure over £500 is served through a search endpoint that the site's robots.txt disallows for automated agents. Only the PCC office reports, which have predictable addresses, were checked. PCC reports from July 2025 onward were not found at those addresses.
- **Leicestershire Police / East Midlands Special Operations Unit.** The Leicestershire PCC says its £500 payments are on the force website "(input 500 into search box)". That search uses the same disallowed endpoint. Not covered. No separate EMSOU spend publication was found.
- **Metropolitan Police / MOPAC.** No current monthly spend publication was found. The MOPAC "spending over £500" page links only a 2015 FOI response. Not covered.
- **Financial Conduct Authority.** Its "what we spend" pages cover hospitality, event costs and expenses. No supplier payment file was found.
- **NESO.** No spend publication was found.
- **Crown Commercial Service.** No spend over £25,000 publication was found on GOV.UK.
- **NHS Digital (before its February 2023 merger into NHS England), NHS Shared Business Services, Police Digital Service, Northumbria Healthcare NHS FT** (whose spend page could not be found), **and the other trusts and integrated care boards using the Federated Data Platform:** not checked.
- **Councils other than Coventry:** not checked.
- **360Giving GrantNav:** the search page is disallowed by robots.txt and returned "too many requests". A web search found no grant records naming Palantir.
- **Anything before 2020.** Not covered. For example, a WhatDoTheyKnow request text cites a 2016 Cabinet Office G-Cloud payment of £100,000; this was not verified.
- **Card-payment data:** government procurement card and ePC over £500 data were not checked.
- **Home Office arm's-length bodies:** the Home Office collection's Independent Office for Police Conduct (IOPC) and Security Industry Authority (SIA) files were not checked.

## Contract values compared with payments

The files do not consistently say whether amounts include VAT. Contract values in `contracts.csv` are as published: mostly without a stated VAT basis, with some marked "inc. VAT". These comparisons therefore show the published figures side by side; they are not a reconciliation.

- **Ministry of Defence.**
  - The MoD's spend files for January 2021 to June 2024 contain Palantir rows totalling £2,849,600.00.
  - For a similar period, the FOI response gives £79,100,169.11 "spent from 01/01/2021, for contracts that can be published".
  - `contracts.csv` lists the £75,215,711.11 enterprise agreement (December 2022 to November 2025) and the £240,600,000 inc. VAT agreement (April 2026 to March 2029). No spend-file row names Palantir after October 2022.
- **NHS England.**
  - Rows for January 2020 to September 2025 total £213,787,695.47.
  - The NHS England, Arden & GEM CSU and North of England CSU notices in `contracts.csv` total £244,617,760, including the £182,242,760 Federated Data Platform notice.
  - Rows dated up to December 2022 total £46,021,760.81. The Arden & GEM notices for June 2020 to December 2022 total £25,000,000.
  - Rows dated January 2024 to September 2025 total £122,099,434.65.
- **Cabinet Office.**
  - Rows total £31,906,662.50 (January 2021 to November 2023), under the expense areas Border Flow Service and BPDG (as published).
  - `contracts.csv` has no Cabinet Office notice. The nearest is the Crown Commercial Service notice "Provision of a Foundry Data Connector - Technical Feasibility" for £26,185,733 (August 2020 to March 2024). The files do not link the payments to that notice.
- **MHCLG / DLUHC.**
  - Rows total £15,625,000.00 (October 2022 to September 2025).
  - `contracts.csv` lists "Palantir Foundry Enterprise" at £4,500,000 (September 2022 to September 2023) and the Ukraine case management system at £0.
  - Rows dated after September 2023 total £10,375,000.00. No later MHCLG/DLUHC notice is in `contracts.csv`.
- **DHSC.**
  - 2020 rows total £2,180,000.02; this includes the four repeated invoices, which come to £1,090,000.01. The DHSC notice "Provision of Palantir Foundry Services" is £908,333.33 (June to September 2020).
  - A further £900,000 was paid in March 2022, described as "Provision of Palantir Foundry ASC Dashboard". No matching notice is in `contracts.csv`.
- **Defra.** Rows total £346,875.00 (November 2023 to June 2024), described as hosting and maintaining the Foundry platform for the Northern Ireland Directorate. `contracts.csv` lists "Trade Analytics Solution" at £1,500,000 (November 2023 to March 2024). The descriptions do not mention trade analytics.
- **Bedfordshire Police.** £3,594,000.00 paid (November 2023 to November 2025). No Bedfordshire notice is in `contracts.csv`.
- **Chelsea and Westminster Hospital NHS FT.** £2,310,000.00 paid (June 2022, September 2024, March 2026). No notice is in `contracts.csv`.
- **Coventry City Council.** £1,250,000.00 paid (March 2025 to August 2026). The notice "Strategic AI Platform" is £500,000 (February 2025 to February 2030).
- **London Ambulance Service.** £100,200.00 paid in April 2023. The notice "Palantir Foundry Support" is £83,500; £100,200 is 1.2 times £83,500.
- **Cambridgeshire Constabulary.** £11,998.80 paid (August 2025). No notice is in `contracts.csv`.
- **Notices with no payment data available here:**
  - Metropolitan Police £489,999
  - Financial Conduct Authority £375,001
  - NESO £21,240,324 inc. VAT
  - Police Digital Service £9,000,000 inc. VAT
  - Northumbria Healthcare £412,500
  - NHS Shared Business Services £137,500
  - Crown Commercial Service £26,185,733 (published files are not available as Crown Commercial Service spend; see the Cabinet Office comparison above)

## How the site counts these

- The site's total is **£278,588,531.78 across 231 lines**, £1,090,000.01 lower than the table above. Four DHSC invoices (INV-003633, INV-003686, INV-003723 and INVE00100771) appear in their original month and again in the December 2020 file. The site counts each invoice once, so the total stays a floor.
- Comparing payments with contract notices needs care with VAT. Notices are often published without VAT, while spend files usually show the gross amount paid. For example, London Ambulance Service's £100,200 payment is exactly its £83,500 notice plus 20% VAT. The Competition page adds 20% to notice values before reporting anything as paid beyond them, and ignores differences under 5%.
