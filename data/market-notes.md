# Palantir's share of IT, software and data spend: notes

This file explains three data files:

- `data/market-share.csv`: for each public body, its total spend in IT, software and data categories, its total spend of any kind, the amount paid to Palantir, and Palantir's share of each. One row for the whole period (`period` is `all`) and one row per calendar year.
- `data/market-top-suppliers.csv`: the ten largest suppliers in each body's IT, software and data categories, for the whole period and for each year.
- `data/market-categories.csv`: every published category label counted as IT, software or data, every borderline label that was left out, and the reason for each.

All figures come from the bodies' own published spend files: the same 1,083 files listed in `data/payments-files-checked.csv` that were searched for `data/payments.csv`. Nothing was estimated. Where a figure cannot be computed from the files, the cell is blank and `coverage_note` says why.

Checked up to 20 October 2026. Built by `scripts/market/build_market.py`.

## How to read the files

- Amounts are in pounds, as published, net of credit notes.
- `palantir_share_of_it` and `palantir_share_of_all` are fractions from 0 to 1, to six decimal places: `0.106428` means 10.6428%. The percentages in these notes are the same figures, rounded to three decimal places.
- `palantir_gbp` is the sum of every line whose supplier name contains "palantir", in every category. It matches `data/payments.csv` for every payer (see "Checks").
- `palantir_share_of_it` counts only the Palantir lines that sit under an IT, software or data label, in months whose files can separate IT spend. This keeps it a true share of `it_total_gbp`. Where some of Palantir's lines carry other labels, `coverage_note` gives those labels and amounts.
- `it_rows` and `all_rows` are the payment lines counted. `files` is the number of files with at least one line in the period.
- In `market-categories.csv`, the columns `category_column`, `rows` and `amount_gbp` (after removing repeats) show where each label comes from and how much money it carries. Rows whose label is in brackets describe files with no usable category at all.

## Method

### Reading the files

- Every saved spend file was read line by line, one file at a time. CSV and XLSX files were read with `rows_from()` from `scripts/payments/fetch_scan.py`. ODS files were read with a streaming reader in `scripts/market/readers.py`, because odfpy (which `rows_from()` needs for ODS) is not installed here and pandas loads a whole ODS file into memory.
- 97 files are PDF reports from three police bodies. Their text was taken with `pdftotext -layout` and read line by line (`scripts/market/pdf_tables.py`). A PDF was used only if every line carrying a money amount matched a payment row; otherwise the whole file was left out, never part of it. 96 PDFs could be read. One Cambridgeshire report (Period 6 2023, September 2023) uses a font with no character map, so its text cannot be extracted.
- In each sheet, the header row was found and each field was picked by column name. The names differ by publisher and by year. For example, the amount is "AP Amount (£)" for NHS England, "Amount in Sterling" for MHCLG, "Total" for the MoD and "Net Value" for Hertfordshire. Two files have no usable header row and were read in the column order of that payer's other files: Bedfordshire Police, February 2020, and Cabinet Office, January 2024.
- Blank lines, repeated header lines and total lines were skipped. A total line is one with no supplier and no date, or one labelled "Total" with no supplier. Three total lines were skipped, all in NHS Improvement sheets.
- Eight lines were left out because their amount cannot be read as pounds:
  - three Defra lines from September 2022 (European Space Imaging), published in US dollars
  - four London Ambulance Service lines from May 2025, which give only a VAT-inclusive figure
  - one MHCLG line from October 2021, which has no amount
- After repeated files and lines were removed, 1,668,878 payment lines from 1,060 files were counted. 100,338 of them are in IT, software or data categories.

### Dates and calendar years

- Lines are placed in a calendar year by the payment date as published. The column is the payment date where a file has one, and otherwise the file's main date column (for example "Date", "Transaction Date" or "Invoice Date").
- Each file's dates were checked for day/month or month/day order. A date above 12 in the first or second position settles the order. 17 London Ambulance Service files, 15 Cambridgeshire files and one MoD file use month/day order in some or all lines. A date that is impossible in its file's order but valid the other way round (for example 17/06/2025 in a month/day file) was read the only way it can be. This happened nine times. Swapping day and month never changes the year.
- 35 lines have no readable date and are counted only in the whole-period row: 2 MoD, 15 UKHSA (a payment date of 1 January 1900, the spreadsheet value for an empty cell) and 18 Hertfordshire (the payment date is blank in the report).
- Some lines carry dates in years for which the payer has no monthly file (for example a Coventry line dated 2007, or one dated 2028). They are counted only in the whole-period row, and its `coverage_note` gives the number and amount. This affects 32 Bedfordshire, 26 Cambridgeshire and 342 Coventry lines.
- The months a payer's files cover come from each file's own name or title, not from the payment dates. Police reports titled "Period N" use the police financial year, so Period 1 is April. Bedfordshire's year comes from its financial-year page: its "march2021-revised" file is on the 2021/22 page, so it is March 2022. Two MoD files whose names begin "20220315" are named "November_2022" and "December_2022", but their payment dates are November and December 2021. They were treated as the 2021 months.

### Repeated files and repeated lines

- **Repeated files.** 20 files repeat another file and were not counted:
  - 15 Home Office files from 2020 and 2021: the Home Office published these months as both CSV and ODS. For 14 months the ODS copy was dropped. For January 2020 the CSV was dropped, because it rounds some amounts to whole pounds and the ODS gives pence.
  - UKHSA's September 2020 file: all its lines are also in the August 2020 file, which holds August, September and some October lines
  - NHS Improvement's single-month files for February and March 2020 are inside the 2019/20 year file
  - Cambridgeshire's file named "p8" (titled Period 9 2024) is part of the Period 9 report
  - Hertfordshire's December 2024 report is identical to its January 2025 report, and both hold January and February 2025 payments
- A file counts as a repeat when at least 90% of its lines are in one other file, matching on date, supplier, reference and amount to the nearest pound.
- **Repeated lines.** A line was removed when a later file repeats it exactly: same payer, date, supplier, amount and transaction reference. This removed 447 lines (£26,095,696.39): UKHSA 223 (October 2020 lines also in the August 2020 file), Cabinet Office 181 (mostly July 2021 lines also in the August 2021 file), MoD 18, Home Office 14 and Defra 11. Lines with no transaction reference cannot be matched this way. They are removed only when their whole file is a repeat.
- **Lines repeated inside one file were kept.** 185,721 lines (£660,340,513.00) are identical in every column to another line in the same file. Each is a separate line in the published file, so each was counted, as `data/payments.csv` counts every published line. 179,893 of them are Coventry lines. In the two Coventry files checked, they are mostly home-care and client-support payments of the same value, mostly in groups of four, paid under one transaction number. That pattern fits weekly invoices, not copies. No Palantir line is repeated inside a file.
- **DHSC, December 2020.** The December 2020 file lists four Palantir invoices that also appear in earlier files: INV-003633 (July 2020), INV-003686 (August 2020), INV-003723 and INVE00100771 (October 2020). The December lines carry new payment dates (22 and 23 December 2020) and a different label ("Outsourcing Contract"; the earlier lines are "Professional fees" or "Agency staff (temp admin)"). Because the dates differ, they are not exact repeats under the rule above, so they are kept, as in `data/payments.csv`. The files do not say whether the December lines are repeat postings. If they are, DHSC's Palantir total is £1,990,000.01 rather than £3,080,000.02, and its 2020 total is £1,090,000.01. Its share of IT spend does not change, because none of these lines is under an IT label.
- **Same reference, different date.** Across all payers, 2,214 lines match a line in another file on supplier, amount and transaction reference but have a different date. They were kept. Many of the references are short numbers reused for different payments (for example "11" or "30" in some Cabinet Office files) or are spoiled by spreadsheet formatting (for example "6.23E+11"), so a match does not show a repeat. The largest groups are NHS England (1,515 lines), the Cabinet Office (345) and DHSC (178).

### IT, software and data categories

- For each payer, one published column holds the category label:
  - "Expense Type" for most central government and NHS files ("Expense Type for report" in NHS England's 2025 files)
  - "Account Code Description" for most HM Treasury files ("Expense Type" in the others)
  - "Subjective Level 4" for UKHSA's files from mid-2023 to February 2025
  - "Account Code(T)" for Coventry
  - "Purpose Of Expenditure" for Hertfordshire
  - "Category Description" for Bedfordshire and Cambridgeshire
- Descriptions typed for single payments were not used.
- Each label was classified by the rules in `scripts/market/categories.py`, in this order:
  1. a decision for that payer and that exact label, made after looking at who was paid under it
  2. labels that say "non-IT", district heating ("Whitehall Systems") or a commission share are left out
  3. labels that name IT, ICT, computing or software are included
  4. labels for telecoms or telephony, printing, marketing, research, document scanning, field data collection, non-software licences and income are left out, unless they also name IT, ICT, computing or software
  5. labels for digital services, technology services, data services, databases, hosting, cloud, websites, data networks, IT security, information systems, named software products and geospatial data are included
  6. other labels that could be read as IT, such as intangible assets under construction, technical services, outsourcing and unnamed licences, are left out and listed as borderline
- Telecoms are left out. Where one label combines telecoms with IT (for example the MoD's "Telecomms + IT non capital"), the whole label is included, because the files do not split it.
- A label's money counts as IT only in files whose category column can separate IT spend. That rules out:
  - **Bedfordshire Police and Cambridgeshire Constabulary:** "Category Description" is the supplier's type ("PROVISION OF SERVICE", "TELEPHONE PROVIDER", "CONSULTANCY"), not the purpose of the payment. Palantir's lines are "PROVISION OF GOODS & SERVICE". Only the all-spend total is computed for these two.
  - **NHS England, January 2020 to March 2025:** the files use broad NHS expense groups with no IT group. From April 2025 they have "Digital Procurement and Services". At the same change, "Establishment" lines fell from about 200 a month to about 20, so IT spend was inside "Establishment" before. But "Establishment" also holds other administration costs, so it cannot stand in for IT.
  - **NHS Improvement, April 2021 to June 2022:** broad NHS expense groups.
  - **Files with no category column:** MHCLG February to April 2025, HM Treasury April to June 2023, and UKHSA March 2025 to August 2026.
- For those months, only the all-spend total and Palantir's amount are computed. The IT columns are blank where no month in the period can separate IT.

### Palantir lines

- A Palantir line is one whose published supplier name contains "palantir" in any case, as in `data/payments.csv`. Lines that mention Palantir only in a description (for example DHSC's payment to NHS England for "Foundry (Palantir)") are not Palantir lines.
- Credit notes (negative lines) are kept and netted.

### Top suppliers

- Suppliers are ranked by their total in the IT, software and data categories, in months whose files can separate IT spend.
- Obvious variants of one name were merged. The merge ignores case, punctuation, "&" against "and", a leading supplier code (for example "00000870-Softcat PLC") and a trailing legal form (Ltd, Limited, PLC, LLP, Inc, Co, Corporation). The names merged are listed in `raw_names_merged`, and the name shown is the variant with the most money.
- Nothing else was merged. Different legal entities stay apart: "Accenture PLC" and "Accenture (UK) Ltd", "Amazon Web Services" and "Amazon Web Services EMEA SARL", "Microsoft Ltd" and "Microsoft Ireland Operations Ltd".
- Payments from a body to itself or to another public body appear as published (for example "CABINET OFFICE" in the Cabinet Office's list, and DVLA, which the Cabinet Office paid mainly under its GOV.UK Notify line).

### Checks

- Palantir's whole-period amount for every payer equals the sum of that payer's Palantir-supplier rows in `data/payments.csv`, to the penny. This covers 235 rows. The MoD's FOI aggregate and the four rows naming another supplier are excluded, as in `data/payments-notes.md`.
- Running the build twice gives identical output files.

## Payers and months covered

Months are those whose published file was read. Spend over £25,000 unless stated.

- **Ministry of Defence:** January 2020 to March 2026, all 75 months.
- **Department of Health and Social Care:** January 2020 to April 2026, all 76 months.
- **Cabinet Office:** January 2020 to August 2026, all 80 months. From April to July 2025 there are extra files for business units that left the Cabinet Office; they are included.
- **MHCLG (DLUHC September 2021 to July 2024):** January 2020 to June 2026, all 78 months. MHCLG's files list payments over £250 as well as over £25,000. IT figures are not computable for February to April 2025.
- **Defra:** April 2020 to February 2026, all 71 months. For January and March 2020 a data.gov.uk web page was saved instead of the spend file, and no file was saved for February 2020. The files cover the Defra group, including the Environment Agency, Natural England, APHA, Kew and the RPA.
- **HM Treasury:** January 2020 to March 2026, all 75 months. IT figures are not computable for April to June 2023. The files include GIAA, the DMO, UKGI, the NIC and UKIB.
- **Home Office:** January 2020 to July 2026, except July 2025 (78 months). Some files include the Disclosure and Barring Service.
- **UKHSA (Public Health England before October 2021):** January 2020 to August 2026, all 80 months. IT figures cover January 2020 to February 2025 only.
- **Department for Business and Trade:** March 2023 to July 2026, except April to July 2023 (37 months).
- **NHS England:** January 2020 to September 2025, all 69 months. Files after September 2025 had not been published when checked. IT figures cover April to September 2025 only. The files include the commissioning support units.
- **Monitor and NHS TDA (NHS Improvement):** December 2019 to March 2020, July 2020, and April 2021 to June 2022, from the two bodies' files combined (Monitor's start in January 2020). No files were saved for April 2020 to March 2021 other than July 2020. IT figures cover December 2019 to March 2020 and July 2020 only.
- **Chelsea and Westminster Hospital NHS FT:** January 2022 to August 2026, all 56 months.
- **London Ambulance Service NHS Trust:** January 2020 to August 2026, except July 2024, February 2025, May 2026 and June 2026 (76 months).
- **Bedfordshire Police (over £500):** February 2020 to September 2026, all 80 months. IT figures not computable.
- **Cambridgeshire Constabulary (over £500, force and PCC):** April 2021 to September 2026, except September 2023 (unreadable PDF) and November 2024 (its file is part of the December 2024 report): 64 months. IT figures not computable.
- **Police and Crime Commissioner for Hertfordshire (over £500, PCC office only):** January 2023 to June 2025, except December 2024, whose file repeats January 2025 (29 months).
- **Coventry City Council (over £500):** October 2024 to September 2026, all 24 months.

## Category labels used

`data/market-categories.csv` lists all 311 included labels and 137 borderline labels left out, plus 7 rows (labels in brackets) for files without a usable category. The main choices:

- **Ministry of Defence** (Expense Type, 25 labels): mainly "Telecomms + IT non capital", "IT and communication services", "IT+Comms Equipment", "Intangible ICT Non SUME" and "Computer maintenance & hire". Left out: "Assets under Construction", "Design services and minor equipment purchases" and "Intangibles Non SUME" (Palantir's 2020 and 2022 lines carry the last two).
- **DHSC** (11 labels): "Service charge - ICT", "Additions-SW LIC", "Addition Clearing - SW LIC", "Additions-IT", "IT minor costs non capital". Left out: "Outsourcing Contract", "Professional fees" and "Agency staff (temp admin)", which carry Palantir's 2020 lines, and "Telephone costs".
- **Cabinet Office** (75 labels): mainly "Other ICT costs", "Other ICT costs - computer software", "Geospatial data services - capital", "IT Development Costs", "IA - Information Technology - software additions", "Licence Costs" (paid mainly to software vendors and resellers) and the many "IT - ..." and "Digital and Technology Services" labels. Left out: telecoms, building assets under construction, "IA - POA & AUC - cost - additions" (paid mainly to consultancies), the records-storage line, and the "MOU Commission Share" lines.
- **MHCLG** (12 labels): "IT - Service Contracts", "Software Licences", "IT Consultancy", "IT - Software Maintenance", "IT - PC, Network & Hardware", "IT SUPPORT", "Web Services". Left out: telecoms, copyright and other non-software licences.
- **Defra** (62 labels): mainly "ICT outsourcing & maint/support" and its sub-labels, "End user software and hardware", the "CIS Capgemini contract" support line (paid entirely to Capgemini UK PLC), "Hosting", "Networking", and cartographic and geospatial data. Left out: "Consultancy - technical", "Data collection services" (surveys and field monitoring), telecoms, and "IA - POA & AUC - cost - additions". The last is borderline: its largest payees are IT firms, and Palantir's Defra lines carry it, but the label does not say software.
- **HM Treasury** (20 labels): "IT software services & maintenance" and "IT hardware services & maintenance" (VAT recoverable and not), software licences, "IT/office equipment" (combined in the label), DMO market data services, and "Corp. subscriptions and other information services". The last is borderline: its top payees are data and software providers, alongside OECD and FT subscriptions. Left out: telephony.
- **Home Office** (11 labels): "IT RUN COST", "OTHER ICT COSTS", "END USER COMPUTER SOFTWARE", "HOSTING", "SPECIALIST USER SOFTWARE & HARDWARE", "IT", "NETWORKING". Under "IT RUN COST" the Home Office books the Airwave emergency-services radio network and EE. These two are its largest IT payees. Left out: "SYSTEM CLEARING" (£2.54 billion; an accounting clearing account whose top payees include IBM and Galliford Try Construction), telephones and offender electronic monitoring.
- **UKHSA** (16 labels): "IT" (in both the expense type and Subjective Level 4 formats), "Computer Services: Specialized", "IT Licences", software maintenance and computer equipment. Left out: outsourced services, telecoms and "Social Marketing - Digital" (advertising).
- **Department for Business and Trade** (22 labels): "Other ICT Costs", "IT Software Licences and Software Maintenance", computer equipment, hosting, application development and on-line databases. Left out: technical advice and professional services, telecoms.
- **NHS England** (1 label): "Digital Procurement and Services", April to September 2025. Left out: "Establishment" (see above), and the other broad groups that carry Palantir lines ("Capital", "Purchase of healthcare from non-NHS bodies", "Supplies and services – general", "Other professional fees").
- **NHS Improvement** (6 labels): computer network, software, hardware and maintenance, and "External Data Contracts".
- **Chelsea and Westminster** (22 labels): "I.T. Expenditure", "General Computer Software", "Computer Maintenance Contracts", "IT Shared Service" (Palantir's 2024 and 2026 lines) and "Software" (Palantir's 2022 line), plus named software systems. Left out: "Intangible Expenditure", "Managed Service Contract" (Medtronic) and telephony.
- **London Ambulance Service** (21 labels): computer software, hardware and maintenance, capitalised software, data networks, and the computer-aided dispatch and patient transport control systems (paid to IT suppliers). Left out: "Professional Fees & Services" (Palantir's 2023 line), telephony and mobile phones, and "Consultancy/Professional Sw" (vehicle conversions).
- **Coventry City Council** (6 labels): "Computing - Software" (Palantir's lines), "Computing - IT Hardware", "Computing - Infrastructure", "IT Hardware", "IT Software", "Network Installation". Left out: "Services - Licences" (mixed), "Books, Publications and Digital Media" and telephones.
- **Hertfordshire PCC** (1 label): "Hardware - Purchase" (Computacenter, SCC). Left out: "Network Services", which is paid mostly to Hertfordshire County Council, another PCC, and advertising and film companies.
- **Bedfordshire Police, Cambridgeshire Constabulary:** none (see above).

## Caveats

- **Only published spend is covered.** Central government and NHS bodies publish payments over £25,000. MHCLG also lists smaller payments in many months. Police and councils publish payments over £500. Spend below the threshold, card spend, and payments a body withholds are not in the totals. So `it_total_gbp` and `all_total_gbp` are the published totals, not the bodies' full budgets.
- **VAT treatment varies by publisher, and most files do not say.** Hertfordshire publishes "Net Value". HM Treasury's labels separate VAT-recoverable from non-recoverable IT spend. London Ambulance Service's May 2025 file has an "Amount" column and separate "Analysed VAT" and "Analysed Amount plus VAT" columns; the "Amount" column was used. Totals mix whatever each publisher chose.
- **NHS England has published only to September 2025.** Its 2025 row covers January to September. Its IT figures cover only April to September 2025, because earlier files have no IT category.
- **Departments categorise differently.** A label that counts as IT for one body may be split, combined or missing at another. For example, the MoD combines telecoms with IT, and the Home Office books its emergency-services radio network as IT. So the shares are comparable within a payer over time, not across payers.
- **Palantir's own lines are not always under IT labels.** The share of IT spend counts only Palantir lines under IT labels, so it is a true share. Where Palantir lines carry other labels, the share understates what Palantir was paid as a share of IT. The headline results below also give the share with those lines added to both sides. That figure is computed from the files, but it treats Palantir's lines differently from other suppliers' lines under the same labels.
- **All-spend totals include grants and transfers.** DHSC's total (£1.16 trillion over the period) includes its funding of NHS England and other bodies. MHCLG's includes grants to councils. Shares of all spend are therefore very small for these funders.
- **Payments between public bodies are included as published.** Examples are DVLA in the Cabinet Office list and DESNZ in the DBT list.
- **PDF reports** were read from extracted text. A file was used only when every money line matched a payment row.

## Headline results

Whole period first, then the latest calendar year with a file for every month. "Share of IT" is Palantir's lines under IT labels as a percentage of IT, software and data spend.

- **NHS England** (January 2020 to September 2025)
  - Whole period: Palantir £213,787,695.47, which is 0.123% of all published spend (£173.20 billion).
  - IT figures exist only for April to September 2025. In those six months, Palantir's lines under "Digital Procurement and Services" were £45,716,107.05 of £429,548,152.38, a 10.643% share of IT. Counting also its lines under "Establishment" (£10,078,690.20) and "Capital" (£3,058,260.22) in those months gives 13.295%.
  - Palantir was the second-largest IT supplier in those six months, after Bytes Software Services.
  - Latest full year, 2024: Palantir £40,897,430.60, 0.127% of all spend. Share of IT not computable.
- **Cabinet Office** (January 2020 to August 2026)
  - Whole period: Palantir £31,906,662.50, 3.450% of IT spend (£924,761,064.09) and 0.300% of all spend. All of Palantir's lines are under IT labels.
  - By year: 10.004% of IT in 2021, 5.542% in 2022, 6.059% in 2023, and nothing from 2024.
  - Latest full year, 2025: Palantir £0 of £181,570,041.95 IT spend.
- **MHCLG** (January 2020 to June 2026)
  - Whole period: Palantir £15,625,000.00, 4.163% of IT spend and 0.006% of all spend.
  - By year: 7.616% of IT in 2022, 5.609% in 2023 and 5.661% in 2024.
  - Latest full year, 2025: Palantir £2,500,000.00. That is 3.453% of IT spend in the nine months with labels; £625,000.00 fell in February to April 2025, which have no labels. It is 0.006% of all spend.
- **Chelsea and Westminster Hospital NHS FT** (January 2022 to August 2026)
  - Whole period: Palantir £2,310,000.00, 4.273% of IT spend (£54,058,721.02) and 0.144% of all spend.
  - By year: 7.518% of IT in 2022, 7.593% in 2024, and 5.499% in January to August 2026.
  - Latest full year, 2025: Palantir £0.
- **Coventry City Council** (October 2024 to September 2026)
  - Whole period: Palantir £1,250,000.00, 5.281% of IT spend (£23,667,685.43) and 0.099% of all spend. Palantir is the third-largest IT supplier over the period.
  - Latest full year, 2025: £500,000.00, 4.243% of IT spend (£11,784,575.39) and 0.079% of all spend.
  - January to September 2026: 8.281% of IT spend.
- **Bedfordshire Police** (February 2020 to September 2026)
  - Whole period: Palantir £3,594,000.00, 0.813% of all published spend (£441,924,851.67). IT share not computable.
  - By year: 2.511% of all spend in 2024.
  - Latest full year, 2025: £1,290,000.00, 1.862% of all spend.
- **Ministry of Defence** (January 2020 to March 2026)
  - Whole period: Palantir £7,666,100.00, 0.012% of all spend. Only £2,599,600.00 of it (2022, "Telecomms + IT non capital") is under an IT label, so the share of IT spend (£3,766,313,203.09) is 0.069%. With Palantir's other lines included, it is 0.203%.
  - By year: 0.438% of IT spend in 2022. In 2020, Palantir's £4,816,500.00 is under "Design services and minor equipment purchases", so the 2020 share of IT is 0.000%.
  - Latest full year, 2025: Palantir £0.
- **DHSC** (January 2020 to April 2026)
  - Whole period: Palantir £3,080,000.02, of which £900,000.00 (March 2022, "Additions-SW LIC") is under an IT label. That is 0.075% of IT spend (£1,194,357,997.24), or 0.257% with Palantir's other lines included. As a share of all spend it is under 0.001%.
  - See "DHSC, December 2020" above for the four re-dated lines.
  - Latest full year, 2025: Palantir £0.
- **Defra** (April 2020 to February 2026)
  - Whole period: Palantir £346,875.00, 0.001% of all spend. All of Palantir's lines are under "IA - POA & AUC - cost - additions", which is not counted as IT, so the share of IT is 0.000%. With them included, it is 0.017%.
  - Latest full year, 2025: Palantir £0.
- **London Ambulance Service** (January 2020 to August 2026)
  - Whole period: Palantir £100,200.00 (April 2023, "Professional Fees & Services"), 0.010% of all spend. Share of IT 0.000%, or 0.090% with that line included.
  - Latest full year, 2023: 0.069% of all spend.
- **Cambridgeshire Constabulary** (April 2021 to September 2026)
  - Whole period: Palantir £11,998.80 (August 2025), 0.003% of all spend. IT share not computable.
  - Latest full year, 2025: 0.014% of all spend.
- **No Palantir lines:** HM Treasury, Home Office, UKHSA, Department for Business and Trade, NHS Improvement and the Hertfordshire PCC office. Their shares are 0.000%. Hertfordshire's 2023 share of IT is blank because its IT spend that year was £0.

## Rebuilding the files

From the project root, with the spend files saved under `sources/raw/payments/`, run `python3 scripts/market/build_market.py`. It needs Python 3 with openpyxl, and `pdftotext` (poppler). It takes about four minutes. An optional argument gives a path for a JSON file of the checks behind these notes.
