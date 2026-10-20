# Palantir and UK government: access and influence in the official record

This note summarises what `influence.csv` and `influence-parliament.csv` contain. It reports what the
documents say. It does not draw conclusions about motive, and an entry in a transparency return or
register is not evidence of wrongdoing.

Collected 20 October 2026.

## Files

| File | Contents |
| --- | --- |
| `influence.csv` | 215 rows: meetings, ACOBA advice, revolving-door moves, lobbying, announcements, and selected parliamentary records |
| `influence-parliament.csv` | 479 rows: every written question that mentions Palantir (372), every Hansard debate section with a contribution mentioning Palantir (98), the November 2023 FDP written statement, and committee evidence and publications (8) |

### Columns in `influence.csv`

- `date`: the date of the event or record, as precise as the source allows (`YYYY-MM-DD`, `YYYY-MM` or `YYYY`).
  Register of Consultant Lobbyists rows use the first month of the quarter.
- `category`: `meeting`, `acoba`, `revolving-door`, `lobbying`, `announcement` or `parliament`. Hospitality
  that officials received from Palantir is filed under `lobbying`. Where the same official recorded a
  meeting, hospitality and travel on the same day, the records are merged into one `meeting` row.
- `who`: the people named in the source, as the source spells them.
- `organisation`: the public body (or other organisation) on the other side of the interaction.
- `summary`: one or two factual sentences. Quoted words are verbatim from the source.
- `source_url`: a URL opened during collection. All 170 unique source URLs returned HTTP 200 on 20 October 2026.
- `source_type`: `official`, `press` or `company`.
- `notes`: context, cross-references and extra source links.

parliament.uk web pages (Hansard, written questions, committees) block automated clients. For those
records `source_url` is the official Parliament API record that was opened, and the human-readable page
is given in `notes` or the `web_url` column.

## Method

- **Ministers', senior officials' and special advisers' transparency returns.** We used the GOV.UK search API
  to list 3,989 meetings, hospitality and transparency publications from every department. We then downloaded
  each attachment (CSV, ODS, XLSX, XLS, PDF and HTML, about 15,000 files) and searched it for "Palantir",
  "Alex Karp", "Louis Mosley" and "Peter Thiel". The 101 files with a match produced 163 records, which are
  134 rows after merging duplicates.
- **ACOBA and departmental business appointment decisions.** We scanned 1,216 ACOBA and departmental "business
  appointment rules" publications (about 4,100 attachments) in the same way.
- **Register of Consultant Lobbyists.** We downloaded every quarterly and yearly file on the register's
  "previous versions" page (Q1 2023 to Q1 2026) and searched the client lists.
- **Registers of interests.** We read all 3,415 entries in the current House of Commons register via
  Parliament's interests API, and the registered interests of all 816 current members of the House of Lords
  via the Members API.
- **Parliament.** The written questions API, the Hansard API and the committees API, each searched for "Palantir".
  Every question and debate cited was then opened individually.
- **Humble Address papers.** We searched the government's Mandelson papers (laid 11 March and 1 June 2026) for
  Palantir and Global Counsel. Some pages are images and were read by OCR.
- **Press.** Guardian, ITPro and The Nerve reports, used where official records are silent. Each is attributed.

## What the record shows

### Meetings

- **Ministers.** Departmental and No 10 returns list 37 ministerial meetings or events with Palantir between
  April 2014 and September 2025. 22 were with Palantir alone and 15 were roundtables or receptions with other
  companies. They include:
  - Francis Maude (2014) and Matthew Hancock (2015) at the Cabinet Office, on cyber security and technology.
  - Jeremy Hunt (September 2015, "introductory discussion on healthcare technology").
  - Michael Gove (2 September 2019, "Brexit readiness").
  - Matt Hancock: a September 2019 health data roundtable, the 11 March 2020 COVID-19 tech roundtable (also
    attended by Boris Johnson), and Foundry demonstrations on 28 September and 8 October 2020.
  - Jacob Rees-Mogg (March and July 2022, borders "as a brexit opportunity").
  - James Heappey at the "Palantir / MOD Enterprise Agreement Launch Reception" (19 April 2023).
  - Victoria Atkins at a Federated Data Platform demonstration (11 December 2023).
  - Pat McFadden (17 April 2025), Peter Kyle (6 May 2025), Wes Streeting (4 June 2025) and John Healey
    (10 September 2025, "Discussion of strategic defence partnership").
- **2024.** No ministerial meeting with Palantir appears in the 2024 returns published so far.
- **The Prime Minister's visit to Palantir in Washington on 27 February 2025.** The visit, with the then
  ambassador Peter Mandelson, is not in the Prime Minister's meetings return.
  - Ministers said "it was not a meeting" and that no minutes or record exist. They described "a short
    presentation", a tour and introductions to staff.
  - The UK Defence Attaché attended, and about 11 MOD uniformed personnel and civil servants observed a
    technology demonstration.
  - In November 2025 the FCDO said embassy officials "arranged this trip in the normal way". In September
    2026 the MOD said the visit "was organised by Ministry of Defence officials".
  - Louis Mosley told the Science, Innovation and Technology Committee it "was done through the proper
    channels".
- **Senior officials.** Returns name 63 senior officials who met Palantir, received its hospitality or
  claimed travel to see it. The MOD accounts for 71 of the 94 officials' rows.
- **Laurence Lee.** As MOD Second Permanent Secretary he has twelve entries between August 2021 and January
  2023. They include meetings "to discuss data integration next steps and enterprise agreement" and dinners
  that Palantir provided. The ACOBA letter refers to nine meetings.
- **Other departments.** The Cabinet Office (Alex Chisholm, Vincent Devine, Andrew Forzani), the Home Office,
  the FCDO (Oliver Robbins), HM Treasury, the Department for Business and Trade, the Department for Transport,
  the Ministry of Justice, the Department for Levelling Up, Housing and Communities and HMRC also record
  officials' meetings.
  - A Cabinet Office entry for August 2025 notes that Palantir is "not a Governmental Strategic Supplier,
    but Andrew accepted a meeting with their UK VP".
- **Advisory body.** Louis Mosley is a listed member of the MOD's Defence Industrial Joint Council (2025).
- **Not in any departmental return.** The Guardian reported a 28 August 2019 Downing Street meeting between
  Boris Johnson, Dominic Cummings and Peter Thiel. The report is based on leaked files, and the meeting was
  not disclosed in the published log.

### Hospitality

- **Events and people.** 24 hospitality rows cover 41 named officials and special advisers who received
  hospitality from Palantir between 2019 and 2026. They include:
  - five MOD officials at the 19 April 2023 enterprise agreement launch reception;
  - nine MOD officials at a Palantir UK reception on 11 February 2026;
  - DfT special advisers (tickets to a dinner event, 2021);
  - a No 10 special adviser (breakfast, 2024);
  - an MOD special adviser (2026).
- **Officials who later joined Palantir.** Barnaby Kistruck received drinks from Palantir in October 2024
  and joined it as Senior Counsellor in September 2025.

### ACOBA and business appointments

- **Five ACOBA letters concern Palantir.**
  - Three are Palantir appointments:
    - Laurence Lee, former MOD Second Permanent Secretary (Geostrategic Advisor to the CEO, February 2024,
      after a six-month waiting period);
    - Leo Docherty, former Armed Forces Minister (Advisor, February 2025);
    - Damian Parmenter, former Director General AUKUS (Senior Counsellor, July 2025).
  - Each was barred for two years from lobbying, or engaging with, the UK government for Palantir.
  - The other two letters mention Palantir:
    - Sajid Javid's C3.ai letter records a January 2020 meeting with Alex Karp.
    - Matthew Gould's Quantexa letter records that he made recommendations in 2020 to award the NHS data
      store contract to Palantir.
- **Departmental business appointment records.** These list further moves to Palantir:
  - Major General James Chiswell (MOD, 2018);
  - Polly Scully (MOD Strategy Director, November 2022);
  - Sal Uddin (Cabinet Office Deputy Director Commercial, December 2022);
  - Barnaby Kistruck (MOD Director Policy, September 2025);
  - Luke Gardiner (former special adviser, February 2026).

### Other revolving-door records

- **Companies House.** Sir Daniel Bethlehem, a former principal Legal Adviser to the Foreign Office
  (2006–2011), was a director of Palantir Technologies UK from November 2013 to March 2024.
- **Press reports.**
  - Indra Joshi, NHSX's former director of AI, joined Palantir in 2022 (ITPro).
  - Louis Mosley worked in Conservative politics, including as an assistant to Rory Stewart, before joining
    Palantir in 2016 (Guardian).
  - Lord (Tom) Watson became a Palantir senior vice-president in September 2026, after being a part-time
    adviser since 2024 (Guardian). Parliament's Members API lists him on leave of absence.
  - The Nerve reported that Palantir had recruited 32 UK government and public sector officials (April
    2026). It did not set out its method.
- **The other direction.** In written answers in February and March 2025, departments said they had no staff
  seconded from Palantir since July 2024. Downing Street said it had no non-Civil Service secondees.
- **In Parliament.** On 10 February 2026 Jon Trickett MP said he was aware of "at least five or six senior
  civil servants in the Ministry of Defence" who had gone to work for Palantir. The official records above
  name five former MOD staff at Director, two-star or higher level, plus one former MOD minister.

### Lobbying

- **Register of Consultant Lobbyists.** Palantir is listed as a client of:
  - Fleetwood Strategy (Q1 2023, Q4 2023, Q1 2024);
  - Global Counsel (Q3 2024, Q3 2025, Q4 2025);
  - Lodestone Oxford (Q2 2025).
- **Global Counsel.** The firm was co-founded by Peter Mandelson. The Guardian reported that he resigned as a
  director in May 2024 but kept a shareholding. In July 2025 Louis Mosley told MPs Palantir "continue[s] to
  use Global Counsel".
- **The government's Mandelson papers (June 2026).**
  - A 20 February 2025 programme lists an "HMA / Plantir tech dinner". Mandelson wrote that the dinner "is
    not for Palantir".
  - On 26 February 2025 the Defence Secretary wrote to Mandelson suggesting the Prime Minister cite
    "companies — such as Palantir and Anduril".
  - A 5 March 2025 email invited Mandelson to a forum "with Louis", meaning Louis Mosley.
  - At a 10 July 2025 meeting Mandelson asked the National Armaments Director about procurements that could
    be announced at the State Visit.
  - On 27 August 2025 Mandelson wrote "I am reluctant to intervene on Palantir" in an email chain about a
    "potential Palantir announcement".
- **What ministers said.**
  - Ministers have said repeatedly that Mandelson had "no influence or involvement" in the December 2025 MOD
    enterprise agreement.
  - The MOD says it holds no record of meetings or correspondence with him about it.
  - The FCDO says no embassy contact with Global Counsel about the February 2025 visit has been identified.
- **Approaches to ministers.**
  - FOI material reported by the Guardian shows Palantir and Alex Karp writing to new ministers after July
    2024, including Rachel Reeves, Peter Kyle and James Timpson.
  - DHSC confirmed a 3 March 2025 letter from Louis Mosley to Wes Streeting offering to meet.

### Announcements

- **AI summit (7 June 2023).** Palantir said it would make the UK its European HQ for AI.
- **Federated Data Platform (21 November 2023).** The contract was awarded to a Palantir-led group, worth up
  to £330 million over seven years.
- **State Visit investment (17 September 2025).** Palantir was to invest up to £1.5 billion as part of the
  £150bn State Visit package.
- **MOD strategic partnership (18 September 2025).** The MOD signed the partnership with Palantir, with London
  as Palantir's European defence headquarters and up to 350 jobs. The MOD later called it "a nonbinding
  statement of intent".
- **Enterprise agreement (30 December 2025).** A three-year agreement was direct-awarded under the
  Procurement Act 2023 (Schedule 5, paragraphs 6 and 7).

### Parliament

- **Written questions.** There are 372 written questions mentioning Palantir: 21 in 2020, 3 in 2021, 11 in
  2022, 39 in 2023, 2 in 2024, 72 in 2025 and 224 in 2026 up to 20 October. Most were answered by DHSC
  (168), the Cabinet Office (64) and the MOD (61). Two questions on Palantir meetings had no recorded answer
  at collection: Jon Trickett's on the Prime Minister's meetings since May 2024, and Gregory Stafford's on
  contacts since 18 September 2026 "including Lord Watson".
- **Debates.** 98 Hansard debate sections include contributions mentioning Palantir. They include urgent
  questions on MOD Palantir contracts in both Houses (10 and 11 February 2026), a Westminster Hall debate on
  the NHS Federated Data Platform (16 April 2026) and a Lords question on Palantir's public service contracts
  (29 June 2026).
- **Committees.**
  - Palantir gave evidence to the Lords AI in Weapon Systems Committee (2023) and the Defence Sub-Committee
    (2024).
  - Louis Mosley gave evidence to the Science, Innovation and Technology Committee (July 2025).
  - That committee's June 2026 report concluded that "Palantir should not have such a significant role in the
    UK public sector" and recommended exercising the February 2027 FDP break clause.
  - The Health and Social Care Committee recommended in July 2026 that the FDP contract not be extended.
- **Strategic supplier status.** The Cabinet Office says Palantir is not a strategic supplier. It says the two
  largest contracts (the FDP and the MOD enterprise agreement) were first awarded by the previous government.

## Gaps and limits

- **Returns lag and have thresholds.** Transparency returns are published months after each quarter. The
  latest seen are January to March 2026 for MOD officials and up to April to June 2026 for some FCDO data.
  Returns cover ministers, permanent secretaries, directors general (MOD: two-star and above) and special
  advisers only, and hospitality above departmental thresholds. Meetings by more junior officials, and visits
  a department does not treat as formal meetings, are not listed.
- **Hard-to-read files.** Pre-2014 returns, and returns published only as scanned images, may have been
  missed. Attachments were searched for text, and image-only pages were not OCR'd except in the Humble
  Address papers.
- **Lobbying register coverage.** The register covers only consultant lobbying of ministers and permanent
  secretaries. Its site offers returns from 2023 only. The published Q2 2023, Q3 2023, Q4 2024 and Q1 2025
  files are much shorter than other quarters and appear incomplete.
- **Registers of interests (searched 20 October 2026).**
  - No current Commons or Lords entry mentions Palantir.
  - Earlier Commons registers (before the 2024 Parliament) and archived Lords registers were not searched.
  - Lord Watson is on leave of absence and so is exempt from registration.
- **APPGs.** The Register of All-Party Parliamentary Groups could not be retrieved because parliament.uk blocks
  automated access. A web search found no APPG record involving Palantir. This was not verified against the
  register itself.
- **Company sources.** Palantir's press releases (palantir.com, investors.palantir.com) load through
  JavaScript and could not be retrieved, so the only company row is Palantir's UK web page.
- **Contracts.** Contract values and procurement records are in `contracts.csv`. This file mentions contracts
  only where they bear on access or influence.
