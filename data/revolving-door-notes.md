# Palantir and UK public office: the revolving-door record

This note summarises `revolving-door.csv`. It reports what the records say. Moving between public office and a
private company is lawful. The conditions in an ACOBA letter or a departmental decision show the risks that ACOBA or the
department identified. They are not findings of wrongdoing. No official body has found that anyone in this file broke a
rule.

Collected 20 October 2026.

## The file

`revolving-door.csv` has one row per person per move: **19 rows covering 18 people**. Lord Watson has two rows: his
advisory board role from 2024 and his full-time post from September 2026.

| Column | Contents |
| --- | --- |
| `person` | Name as the record gives it |
| `direction` | `gov-to-palantir`, `palantir-to-gov` or `concurrent` (a Palantir role held alongside a public office) |
| `former_role`, `former_org` | The public role and body |
| `left_public_office`, `joined_palantir` | `YYYY-MM-DD`, `YYYY-MM` or `YYYY` as precise as the source allows, `not stated`, or `n/a (concurrent)`; any qualifier is in `notes` |
| `palantir_role` | As the record words it |
| `approval_route` | `ACOBA`, `departmental business appointment rules` or `none published` |
| `conditions` | A short verbatim extract |
| `conditions_until` | The date the last condition ends, worked out from the record's dates; blank where it gives none (details in `notes`) |
| `recorded_contact_with_palantir_in_office` | Verbatim from the letter, where it says anything |
| `source_url`, `source_type` | The record that documents the move (`official` or `press`) |
| `notes` | Context, other sources and cross-references |

Every `source_url` was opened during collection. `scripts/revolving/check_sources.py` re-opens them: on 20 October 2026
all 19 returned HTTP 200 and named the person, and 40 of the 41 URLs in the file returned HTTP 200. The other URL is a
Hansard web page, which blocks automated clients; its API record is cited in its place.

## How we searched

- **ACOBA and departmental releases.** We listed 1,219 GOV.UK publications: 706 from ACOBA, and 513 business appointment
  releases and related pages from about 40 departments and agencies. The departmental releases run from May to December
  2015 (published February 2016) up to April to June 2026 (published 24 September 2026).
  - We read every page body and all 4,124 attachments (2,177 PDF, 1,838 HTML, 37 CSV, 25 DOC, 23 DOCX, 18 XLSX, 5 ODT and
    1 ODS).
  - We searched the text for "Palantir" and common misspellings.
  - We OCR'd the 424 PDFs that had little or no text layer, and converted four DOC files that the first pass could not
    read.
  - Ten publications match. Five are ACOBA letters and five are departmental releases. OCR found nothing further.
- **Companies House.** We checked current and resigned officers of Palantir Technologies UK, Ltd. (07042994) and Palantir
  Technologies UK - Eagle, Ltd. (10515288, a holding company at the same address). None of the other companies returned
  by a Companies House search for "Palantir technologies" shares that address; their officers were not checked.
- **House of Lords.** We searched Parliament's Register of Lords' Interests API, including deleted entries (these go back
  to early 2018), for "Palantir", "Global Counsel", "Lodestone" and "Powerful Street". We also read all 98 Hansard debate
  sections that mention Palantir, looking for declarations of interest.
- **House of Commons.** We searched every edition of the Register of Members' Financial Interests from 14 January 2009 to
  12 October 2026: 353 editions, from the parsed copies that mySociety publishes for TheyWorkForYou. No entry mentions
  Palantir.
- **Special advisers.** We read the Cabinet Office lists and annual reports of special advisers (2012 to 2026) and its
  publications of special advisers' interests (2020-21 to 2025-26). No special adviser declared a Palantir interest.
- **NHS.** We read Chelsea and Westminster Hospital NHS Foundation Trust board papers (2019, 2020, 2021 and July 2022), the
  North West London Acute Provider Collaborative's 2024-25 board register, and NHS England's current board register of
  interests.
- **The other direction.** We read the written answers on secondments from Palantir and searched GOV.UK for appointment
  notices that mention Palantir.
- **Press.** We used reputable outlets only where the official record is silent, and attribute each one: The Guardian,
  the London Review of Books, Liberty Investigates (also published by Prospect), openDemocracy, ITPro and The Nerve.
  LinkedIn was not used.

The scripts are in `scripts/revolving/`:

- `enumerate_pubs.py`, `scan_pubs.py` and `ocr_pass.py` list, download and search the GOV.UK publications;
- `lords_register.py` and `commons_regmem.py` search the registers;
- `check_sources.py` re-checks the sources.

## How many moves

| | Rows |
| --- | --- |
| Gov-to-Palantir | 14 |
| Concurrent (Palantir role held alongside a public office) | 5 |
| Palantir-to-gov | 0 |
| **Total** | **19** |

| Approval route | Rows |
| --- | --- |
| ACOBA | 3 (Lee, Docherty, Parmenter) |
| Departmental business appointment rules | 5 (Chiswell, Scully, Uddin, Kistruck, Gardiner) |
| None published | 11 |

**Source.** 12 rows rest on an official record:

- ACOBA letters;
- departmental releases;
- Companies House;
- the Lords register;
- Hansard;
- an NHS trust board register.

7 rest on press reports: Lamb, Mosley, Mascall, Sawers, Blackwood, Joshi and Watson's 2026 post. For Mascall and Joshi,
the former role itself is confirmed by an official record.

### By former department

| Former body | Rows | People |
| --- | --- | --- |
| Ministry of Defence and armed forces | 7 | Lamb, Chiswell, Scully, Lee, Docherty, Parmenter, Kistruck |
| House of Lords (concurrent) | 4 | Walney, Blackwood, Watson (two rows) |
| Cabinet Office and No 10 | 3 | Mascall (special adviser), Uddin, Gardiner (special adviser) |
| Health (NHSX, NHS trusts) | 2 | Joshi, Swindells |
| Foreign Office | 1 | Bethlehem |
| Secret Intelligence Service | 1 | Sawers |
| Local government | 1 | Mosley |

Lee and Docherty also held FCDO posts. Lord Walney held a Home Office adviser post, and Baroness Blackwood was a DHSC
minister and later chair of Genomics England.

### By year

The table uses the year the Palantir role began, as recorded. For concurrent roles, it uses the year of the earliest
record.

| Year | Rows | People |
| --- | --- | --- |
| 2013 | 1 | Bethlehem |
| by 2014 | 1 | Lamb |
| 2016 | 1 | Mosley |
| 2018 | 1 | Chiswell |
| 2019 | 2 | Sawers (reported 2019 meeting), Swindells (Global Counsel from September 2019) |
| 2020 | 1 | Blackwood (Global Counsel engagements, 2020-21) |
| 2022 | 4 | Joshi, Walney (declared June 2022), Scully, Uddin |
| 2024 | 2 | Lee, Watson (advisory board) |
| 2025 | 3 | Docherty, Parmenter, Kistruck |
| 2026 | 2 | Gardiner, Watson (senior vice-president) |
| not stated | 1 | Mascall |

The eight moves with an ACOBA or departmental decision fall in 2018 (1), 2022 (2), 2024 (1), 2025 (3) and 2026 (1).
Six of the eight are former MOD staff or ministers: Chiswell, Scully, Lee, Docherty, Parmenter and Kistruck. Three of
these six (Docherty, Parmenter and Kistruck) took up their Palantir roles between February and September 2025.

## The most senior moves

| Former role | Person | Record |
| --- | --- | --- |
| MOD Second Permanent Secretary, then FCDO Director General | Laurence Lee | ACOBA letter (February 2024) |
| Chief of the Secret Intelligence Service | Sir John Sawers | Press only (openDemocracy, The Nerve, LRB): a reported 2019 adviser or services role |
| Minister of State for the Armed Forces | Leo Docherty | ACOBA letter (February 2025) |
| Lieutenant General, British Army | Sir Graeme Lamb | Press only (Liberty Investigates, The Nerve) |
| Director General, AUKUS, MOD | Damian Parmenter | ACOBA letter (June 2025) |
| Legal Adviser to the Foreign and Commonwealth Office | Sir Daniel Bethlehem | Companies House (director, 2013-2024) |
| NHS England deputy chief executive (as reported); NHS trust Chair in Common | Matthew Swindells | Trust register of interests (June 2022) |
| Peer; former deputy leader of the Labour Party and minister | Lord Watson | Lords register (2024); Guardian (2026) |

## Common conditions

The eight ACOBA and departmental decisions share these elements:

- **No use of privileged information.** This is in all eight; for Gardiner it is a reminder of his ongoing
  responsibilities rather than a condition.
- **No lobbying of the UK government for Palantir.**
  - Two years in the three ACOBA letters and the two Cabinet Office decisions (Uddin, Gardiner).
  - One year in the MOD decisions (Chiswell, Scully, Kistruck).
- **No advice on UK government or MOD bids and contracts.** This is in all eight: two years in the ACOBA letters and for
  Gardiner, and one year in the other departmental decisions.
- **No direct engagement with the UK government on Palantir's behalf.** All three ACOBA letters say this. ACOBA wrote of
  Docherty and Parmenter: "Palantir has a significant commercial interest in the UK government."
- **No advice on the UK defence sector.**
  - Docherty and Parmenter: no advice on the UK defence sector.
  - Lee: no work on UK defence and national security matters.
  - Lee's and Parmenter's roles were described to ACOBA as outside the UK.
- **A waiting period.** Only Lee had one: "a waiting period of at least six months from his last day in post as Second
  Permanent Secretary at the MOD".
- **MOD-specific terms.**
  - Scully was not to complete "any MOD facing activity until the Enterprise Agreement is signed".
  - Kistruck was not to use "any information relating to the Defence Industrial Strategy ahead of its publication".
  - Both were told that future interactions must be "within the governance model that has been set out by the Defence
    Digital".
- **Palantir's undertakings.** In all three ACOBA cases Palantir confirmed to the Committee that it would comply. In
  Lee's case:
  "Palantir will ensure that it does not ask Mr Lee to undertake any activity that might be a breach of any of his
  restrictions or conditions."

**Matthew Swindells (not a Business Appointment Rules case).** His NHS trust recorded its own mitigation in its
register: "To be excluded from any decision making in relation to Palantir with whom Chelwest work."

### Recorded contact in office

- **Lee.** ACOBA records "meetings with Palantir on nine occasions between June 2021 and February 2023". It also records
  that the MOD signed its enterprise agreement with Palantir in November 2022, while he was Second Permanent Secretary.
  The letter says he "had no direct involvement in the contract".
- **Parmenter.** ACOBA records "occasional contact with Palantir whilst in office", including a Palantir briefing on its
  Ukraine work.
- **Docherty.** He told ACOBA he had known Palantir's CEO "since before your time as an MP and then a minister" and "did
  not meet them in office".
- **Departmental releases.** These do not record contact in office.
- **Transparency returns.** These separately list:
  - drinks from Palantir for Kistruck on 16 October 2024, while he was at the MOD;
  - a meeting with Palantir for Docherty on 26 May 2022, in an earlier ministerial post. This is outside the last two
    years in office that his ACOBA letter covers.

  See the notes column for both.

## Recorded breaches

None. No ACOBA publication and no departmental release records a breach of a condition, or a failure to seek advice,
in connection with Palantir. The scan covered all 706 ACOBA publications: every decision page and its attachments, 87
correspondence items and 14 corporate reports, including the annual reports.

## Peers

The Nerve reported that "Four members of the House of Lords have advised Palantir". It named Tom Watson, John Woodcock
(Lord Walney) and Nicola Blackwood, alongside Lord Mandelson.

- **Lord Watson of Wyre Forest.** The Lords register lists "Member, Public Services Advisory Board, Palantir UK Ltd
  (software)". The entry was created on 25 October 2024 and removed on 14 May 2026, when he was on leave of absence. The
  Guardian reported his appointment as senior vice-president in September 2026.
- **Lord Walney.** In the Lords on 23 June 2022 he said: "I declare an interest in that a consultancy of which I am a
  director works with Palantir". His register entries list one consultancy directorship, Powerful Street Ltd. They do not
  list its clients.
- **Baroness Blackwood of North Oxford.** Her register lists paid Global Counsel webinars (May to July 2020) and a Global
  Counsel health roundtable (February 2021), without naming a client.
  - The Nerve reported she "consulted for the company through Mandelson’s Global Counsel".
  - The LRB reported she "received payments from Global Counsel to attend events where the guests included Palantir".
- **Lord Mandelson.** Global Counsel, which he co-founded, is listed as a Palantir client in the Register of Consultant
  Lobbyists (see `influence.csv`). No official record gives him a personal Palantir role, so he has no row here. He
  retired from the Lords on 4 February 2026, and the Lords register API no longer returns his entries.
- **Lord O'Neill of Gatley.** The register records a shareholding: "Palantir Technologies Inc (technology) (interest
  ceased 24 May 2023)". It is a shareholding, not a role, so it is not a row.

## Other records that mention Palantir but are not moves

- **Sajid Javid's ACOBA letter on C3.ai (August 2020).** It records a January 2020 meeting with Palantir's CEO.
- **Matthew Gould's ACOBA letter on Quantexa (January 2023).** It records that he "was involved in procurement during
  the pandemic for the NHS data store, which involved making recommendations to award a contract to a competitor of
  Quantexa - Palantir".
- **Louis Mosley.** He is listed as a member of the MOD's Defence Industrial Joint Council, an industry advisory body.
- **Sir Daniel Bethlehem.** In 2020, while he was a Palantir UK director, he was appointed to the UK's ICSID panel of
  arbitrators.

## The Nerve's count

The Nerve (24 April 2026) reported that Palantir "has recruited 32 UK government and public sector officials", plus "an
additional 37 current mid-ranking staff". The article names 31 people in its text and lists.

- **16 have rows here.** They held senior or public roles, or appear in an official record.
- **13 are not named here.** Their former roles, as The Nerve or the LRB describes them, are mid-ranking, or of a
  seniority that no official record confirms. Under this project's privacy rule they are counted, not named. By former
  employer, as The Nerve describes them:
  - armed forces and MOD: 4;
  - NHS England and NHS Wales: 3;
  - Foreign Office: 2 (one also lists Cabinet Office work);
  - Home Office: 2 (one also lists the Metropolitan Police);
  - No 10: 1;
  - Secret Intelligence Service: 1.

- **Two have no row:**
  - one co-founded a consultancy that Palantir hired; his political roles were party campaign posts, not public office;
  - the other is Lord Mandelson, covered above.

Palantir told The Nerve: "We were supplied 32 names spanning around 15 years – a period in which thousands of people
have worked for Palantir in the UK. Of those, 14 no longer work for, or with, us, some of whom stopped as long as five
years ago. Six are ex-armed forces veterans".

Two people in this file, Leo Docherty and Louis Mosley, are not in The Nerve's lists.

## The other direction: Palantir to government

No move from Palantir into a UK public office was found in the official record.

- **Written answers to 18 questions tabled on 24 February 2025.** The departments said they had no staff seconded from
  Palantir since July 2024. The Attorney General's Office said it "has never seconded any staff from Palantir". The
  Cabinet Office first said that secondment data are held at business-unit level.
- **Cabinet Office (21 March 2025).** It said that "based on the information held centrally, there is no record of any
  secondees from Palantir".
- **Downing Street (25 September 2025).** It said there had been "no secondments from non-Civil Service organisations to
  Downing Street since July 2024".
- **Before July 2024.** No published figures were found.
- **Appointment notices.** No GOV.UK appointment notice names a former Palantir employee.

The nearest case is Matthew Swindells. He became Chair in Common of the four north-west London trusts on 1 April 2022,
while his register entry recorded that he chaired Palantir's Health Advisory Panel. He is filed as `concurrent`.

## Gaps in coverage

- **Grade thresholds.**
  - Departments publish decisions only for SCS1 and SCS2 (Deputy Director and Director) and equivalents, which includes
    one- and two-star officers and special advisers of equivalent level.
  - ACOBA covers the most senior grades and ministers.
  - Moves by staff below these grades leave no published record. This covers most of the 13 people not named here, and
    the 37 people The Nerve counted without naming them.
- **The NHS.** NHS bodies are outside the Civil Service rules. In the Lords on 22 June 2023, Baroness Brinton said
  "senior NHS leaders are excluded from any restrictions when they move to providers, as happened last year when two
  senior staff moved to Palantir".
  - NHS England publishes no business appointment decisions.
  - Trust registers cover board members only.
  - No official record of Indra Joshi's 2022 move was found.
- **Intelligence agencies.** No business appointment releases from SIS, GCHQ or MI5 were found on GOV.UK.
- **Time limits.** The Rules apply for one year after leaving (grade 6 and below) or two years (SCS1 and above, and
  ministers). Later moves need no approval and leave no record.
  - Bethlehem became a director about two and a half years after leaving the FCO.
  - Sawers' reported 2019 role came more than four years after he left SIS.
- **Advisers and consultants.** These do not appear at Companies House, and Palantir does not publish a list of its
  advisers. Lamb, Sawers, Mascall and Watson's 2026 post rest on press reports.
- **Lords register limits.**
  - The earliest entries the API returns, including deleted ones, date from early 2018.
  - Former members, such as Lord Mandelson, are not returned.
  - Clients of a member's own consultancy are often not listed (Walney, Blackwood).
- **Publication lag.**
  - Departmental releases run to June 2026.
  - ACOBA publishes a letter only once a role is announced or taken up.
  - A move made after June 2026 by a civil servant below ACOBA's level would not yet appear.
- **Transparency returns.**
  - openDemocracy reported a 2019 meeting between Palantir's CEO and John Manzoni, arranged by Sir John Sawers.
  - The Cabinet Office published four returns of permanent secretaries' meetings covering January to December 2019.
    Together they list 51 meetings for Manzoni, and none is with Palantir.
- **Secondments.** There is no central record (Cabinet Office), and no published figures before July 2024.
- **Lamb's 2014 evidence.** Liberty Investigates reported that Lamb gave select committee evidence by 2014. It was not
  found in Parliament's committees API.
- **Not searched.** Devolved governments and NHS Scotland and Wales were not searched for business appointment records,
  and local government has no business appointment regime. Historical NHS England board registers were not searched.
