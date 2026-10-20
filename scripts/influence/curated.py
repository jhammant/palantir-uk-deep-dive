"""Hand-checked rows for data/influence.csv. Every source_url was opened during the research run.

Fields: date, category, who, organisation, summary, source_url, source_type, notes
"""

PQ = "https://questions-statements-api.parliament.uk/api/writtenquestions/questions/"
WQ_WEB = "https://questions-statements.parliament.uk/written-questions/detail/"
HAPI = "https://hansard-api.parliament.uk/debates/debate/"
G = "https://www.theguardian.com"
HA1 = "https://assets.publishing.service.gov.uk/media/6a213331a0006190a6f098c5/E03595100_HA_Volume_II_Part_I_Web.pdf"
HA2 = "https://assets.publishing.service.gov.uk/media/6a4e5daf43f694ee291df7e6/HA_Volume_II_Part_II_-_Corrected.pdf"
HA3 = "https://assets.publishing.service.gov.uk/media/6a4e5df0559c26eacf438ef8/HA_Volume_II_Part_III_-_Corrected.pdf"
HA_PUB = "https://www.gov.uk/government/publications/update-on-the-government-response-to-the-humble-address-motion"
ORCL = "https://orcl.my.site.com/CLR_Annual_Returns_Downloads"
CAPI = "https://committees-api.parliament.uk/api/"


def pq(qid, date, uin, extra=""):
    note = f"PQ {uin}. Web page: {WQ_WEB}{date}/{uin}"
    return PQ + str(qid), "official", (note + ". " + extra).strip() if extra else note


ROWS = []


def add(date, category, who, organisation, summary, source_url, source_type, notes=""):
    ROWS.append(dict(date=date, category=category, who=who, organisation=organisation, summary=summary,
                     source_url=source_url, source_type=source_type, notes=notes))


# ---------------------------------------------------------------- ACOBA advice letters
add("2020-08", "acoba", "Sajid Javid (former Chancellor of the Exchequer)", "HM Treasury",
    "ACOBA's advice on Sajid Javid's adviser role at C3.ai records that his only relevant meeting with a C3.ai competitor in office was a January 2020 'get-to-know you meeting' with Palantir; HM Treasury told the Committee he 'dropped into the Palantir pavilion' for a short meeting with Alex Karp.",
    "https://assets.publishing.service.gov.uk/media/5fa2c26ad3bf7f03a40fe57d/Final_Advice_Letter_-_SJ_C3.ai.pdf", "official",
    "Letter dated August 2020. Not a Palantir appointment; Palantir appears as a competitor of C3.ai. HMT said Karp set out Palantir's engagement with US/UK governments and Mr Javid thanked him for Palantir's work on tackling child sexual exploitation. Publication: https://www.gov.uk/government/publications/javid-sajid-chancellor-of-the-exchequer-hm-treasury-acoba-advice")
add("2023-01", "acoba", "Matthew Gould (former Director General for Digital Transformation, DHSC and NHS England)", "Department of Health and Social Care",
    "ACOBA's advice on Matthew Gould's advisory board role at Quantexa records that he 'was involved in procurement during the pandemic for the NHS data store, which involved making recommendations to award a contract to a competitor of Quantexa - Palantir'; DHSC contacted Palantir as the main competitor, which did not object.",
    "https://assets.publishing.service.gov.uk/media/6493058eb32b9e000ca96bba/ACOBA_Advice_Letter_-_Matthew_Gould__Quantexa.pdf", "official",
    "Letter dated January 2023. Not a Palantir appointment. The letter notes Quantexa and Palantir were both reported to be bidding for the Federated Data Platform. Publication: https://www.gov.uk/government/publications/gould-matthew-director-general-for-digital-transformation-at-dhsc-and-national-director-for-digital-transformation-at-nhs-england-acoba-advice")
add("2024-02", "acoba", "Laurence Lee (former Director General, FCDO; Second Permanent Secretary, MOD, March 2021 to May 2023)", "Ministry of Defence; Foreign, Commonwealth and Development Office",
    "ACOBA advised on Laurence Lee's paid role as Geostrategic Advisor to Palantir's CEO, imposing a six-month waiting period and a two-year bar on working on UK defence and national security matters or engaging with UK government for Palantir. The letter records nine meetings with Palantir between June 2021 and February 2023 and that the MOD's Palantir enterprise agreement (£25 million a year over three years) was signed in November 2022 while he was Second Permanent Secretary; the MOD said he had no direct involvement in the contract.",
    "https://www.gov.uk/government/publications/lee-laurence-director-general-at-the-foreign-commonwealth-and-development-office-acoba-advice/advice-letter-laurence-lee-geostrategic-advisor-to-the-ceo-palantir-technologies-limited", "official",
    "ACOBA page: letter sent February 2024, appointment taken up later that month; publication dated 27 March 2024. Mr Lee told ACOBA he approached Palantir about a role. PDF: https://assets.publishing.service.gov.uk/media/68b1a692d723ba6f74dba816/Advice_Letter__Laurence_Lee__Geostrategic_Advisor_to_the_CEO__Palantir_Technologies_Limited.pdf")
add("2025-02", "acoba", "Leo Docherty (former Minister of State for the Armed Forces; previously FCDO Parliamentary Under Secretary of State for Europe)", "Ministry of Defence; Foreign, Commonwealth and Development Office",
    "ACOBA advised on Leo Docherty's paid role as an Advisor to Palantir Technologies UK, with two-year conditions barring lobbying, advice on the UK defence sector and any engagement with the UK government on Palantir's behalf. He told the Committee he had known Palantir's CEO since before he was an MP, had no involvement in decisions specific to Palantir and did not meet them in office; the MOD said the 2022 enterprise agreement (£80M) predated his time there.",
    "https://www.gov.uk/government/publications/docherty-leo-minister-of-state-for-the-armed-forces-at-the-ministry-of-defence-acoba-advice/advice-letter-leo-docherty-advisor-palantir-technologies-uk-ltd", "official",
    "ACOBA page: he left the MOD in July 2024; letter sent February 2025; appointment taken up later that month. Transparency returns separately list a 26 May 2022 meeting between Mr Docherty (then a defence minister) and Palantir about veterans (see meeting row); that date is outside the last two years in office that the Rules cover. PDF: https://assets.publishing.service.gov.uk/media/67e3ef08d052ace7e8977638/Advice_Letter_-_Leo_Docherty_-_Advisor__Palantir_Technologies_UK_Ltd.pdf")
add("2025-06", "acoba", "Damian Parmenter CBE (former Director General, AUKUS, MOD)", "Ministry of Defence",
    "ACOBA advised on Damian Parmenter's paid role as Senior Counsellor at Palantir Technologies UK (international markets), with two-year conditions including no advice on the UK defence sector and no direct engagement with the UK government for Palantir. The letter records occasional contact with Palantir in office, including meeting it on attracting private investment into AUKUS programmes and a Palantir briefing on its Ukraine work; the MOD said he made no decisions specific to Palantir.",
    "https://www.gov.uk/government/publications/parmenter-damian-director-general-aukus-ministry-of-defence-acoba-advice/advice-letter-damian-parmenter-senior-counsellor-palantir-technologies-uk", "official",
    "ACOBA page: left the MOD in July 2025; letter sent June 2025; appointment taken up July 2025; published 3 September 2025. PDF: https://assets.publishing.service.gov.uk/media/689f4b65b4b6acd341133a95/Advice_Letter_-_Damian_Parmenter__Senior_Counsellor__Palantir.pdf")

# ---------------------------------------------------------------- Revolving door (official records first)
add("2013-11-04", "revolving-door", "Sir Daniel Bethlehem", "Foreign and Commonwealth Office (former)",
    "Companies House lists Sir Daniel Bethlehem as a director of Palantir Technologies UK, Ltd (07042994) from 4 November 2013 to 10 March 2024.",
    "https://find-and-update.company-information.service.gov.uk/company/07042994/officers", "official",
    "Former principal Legal Adviser of the Foreign & Commonwealth Office, May 2006 to May 2011, per his Berkeley Law biography: https://www.law.berkeley.edu/files/bio--bethlehem.pdf. Companies House also lists Alexander Karp as a director from 14 October 2009 to 22 December 2021.")
add("2018-10-01", "revolving-door", "Major General James Robert Chiswell", "Ministry of Defence",
    "MOD's business appointment record lists Major General James Chiswell, former MOD Director (last day in service 25 September 2018), taking up an Advisor/Consultant role with Palantir Technologies Inc on 1 October 2018, with one-year bars on lobbying and on HMG and MOD-facing work for Palantir.",
    "https://www.gov.uk/government/publications/mod-business-appointment-rules-applications-completed-from-july-to-september-2018/mod-business-appointment-rules-applications-completed-from-july-to-september-2018", "official",
    "Departmental (not ACOBA) decision. The record says the one-year bar on MOD-facing activity ran from his last day in post (March 2018).")
add("2022-04-22", "revolving-door", "Indra Joshi (former NHSX director of AI)", "NHSX / NHS England",
    "ITPro reported that Indra Joshi, NHSX's former AI director who left on 31 March 2022, had been hired by Palantir while it was competing for NHS England's Federated Data Platform contract; the report quoted critics including the Open Rights Group.",
    "https://www.itpro.com/data-insights/big-data-analytics/367470/palantirs-poaching-of-former-nhsx-ai-chief-branded-scandalous", "press",
    "Trade press report, 22 April 2022 (Sabina Weston). In the Lords on 22 June 2023 Baroness Brinton said two senior NHS staff had moved to Palantir the previous year (see parliament row).")
add("2022-11-28", "revolving-door", "Polly Scully", "Ministry of Defence",
    "MOD's business appointment record lists Polly Scully, former MOD Strategy Director (left 14 November 2022), as Senior Counsellor UKG at Palantir from 28 November 2022; conditions included 12-month bars on using contacts and advising on MOD bids, and no MOD-facing activity until the enterprise agreement was signed.",
    "https://www.gov.uk/government/publications/mod-business-appointment-rules-applications-completed-from-october-to-december-2022/mod-business-appointment-rules-applications-completed-from-october-to-december-2022", "official",
    "Departmental decision. An MOD senior officials' meetings return records a 3 April 2025 Palantir visit for James Hockenhull 'hosted by PollySculy, Palantair' (as published).")
add("2022-12-05", "revolving-door", "Sal Uddin", "Cabinet Office",
    "Cabinet Office business appointment advice lists Sal Uddin, former Deputy Director, Commercial (left 29 November 2022), as Commercial Lead at Palantir from 5 December 2022, with a two-year lobbying bar and a one-year bar on working on government contracts or bids.",
    "https://www.gov.uk/government/publications/cabinet-office-business-appointment-rules-advice-october-to-december-2022/cabinet-office-business-appointment-rules-advice-october-to-december-2022", "official",
    "Departmental decision.")
add("2025-02-24", "revolving-door", "Jon Trickett MP (questions); departmental answers", "Whitehall departments",
    "In answers to 18 written questions tabled on 24 February 2025, departments said they had no staff seconded from Palantir since July 2024; the Cabinet Office said secondments are held at business-unit level and later said there was no central record of any Palantir secondees.",
    PQ + "1777440", "official",
    "Cabinet Office answer PQ 32929 (12 March 2025) and follow-up PQ 37981 (21 March 2025): " + PQ + "1784401. The Cabinet Office also answered (PQ 73200, 25 September 2025) that there had been no secondments from non-Civil Service organisations to Downing Street since July 2024: " + PQ + "1829957. Other departments' answers are in data/influence-parliament.csv.")
add("2025-09-09", "revolving-door", "Barnaby Kistruck", "Ministry of Defence",
    "MOD's business appointment record lists Barnaby Kistruck, former MOD Director Policy (left 31 August 2025), as Senior Counsellor at Palantir from 9 September 2025; conditions included not drawing on information about the Defence Industrial Strategy ahead of its publication and 12-month bars on using contacts and advising on MOD bids.",
    "https://www.gov.uk/government/publications/mod-business-appointment-rules-applications-completed-from-july-to-september-2025/mod-business-appointment-rules-applications-completed-from-july-to-september-2025", "official",
    "Departmental decision. MOD's hospitality return separately lists him receiving drinks from Palantir on 16 October 2024 (see hospitality row).")
add("2026-02-02", "revolving-door", "Luke Gardiner", "Cabinet Office (special adviser)",
    "Cabinet Office business appointment advice lists Luke Gardiner, a former special adviser who left on 24 May 2024, as a Capture Strategist at Palantir from 2 February 2026, barred for two years from lobbying government for Palantir or working on bids for government contracts.",
    "https://www.gov.uk/government/publications/cabinet-office-business-appointment-rules-advice-january-to-march-2026/cabinet-office-business-appointment-rules-advice-january-to-march-2026", "official",
    "The record does not say which minister he advised.")
add("2016", "revolving-door", "Louis Mosley (Palantir Executive Vice President, UK and Europe)", "Conservative politics (former)",
    "The Guardian reported that before joining Palantir in 2016 Louis Mosley worked in Conservative politics, including as an assistant to Rory Stewart and as a councillor in Kensington and Chelsea, and that he now leads Palantir's UK and Europe business.",
    G + "/technology/2026/may/09/who-is-louis-mosley-defending-palantir-critics", "press",
    "Guardian profile, 9 May 2026 (Robert Booth).")
add("2026-04-24", "revolving-door", "The Nerve (investigation)", "UK government and public sector",
    "The Nerve reported that Palantir had recruited 32 UK government and public sector officials and an additional 37 current mid-ranking staff from the military, the NHS and government departments, and that four members of the House of Lords had advised Palantir.",
    "https://www.thenerve.news/p/palantir-revolving-doors-peter-thiel-transparency-corruption-risk", "press",
    "24 April 2026 (Charlie Young, Ian Tucker, Carole Cadwalladr). The article does not set out its method; individual names it gives are not reproduced here unless confirmed by an official record or other reputable press.")
add("2026-09-18", "revolving-door", "Lord Watson of Wyre Forest (Tom Watson)", "House of Lords; former Labour deputy leader and minister",
    "The Guardian reported that Palantir appointed the Labour peer and former deputy leader Tom Watson as a senior vice-president working alongside Louis Mosley; it reported he had been a part-time adviser to Palantir since 2024 and that he had taken a leave of absence from the House of Lords.",
    G + "/politics/2026/sep/18/former-labour-deputy-leader-tom-watson-joins-palantir", "press",
    "Parliament's Members API lists his status as 'Leave of Absence' and his register entry as 'On leave of absence; exempt from registration' (dated 14 May 2026): https://members-api.parliament.uk/api/Members/1463/RegisteredInterests. A written question tabled 9 October 2026 (PQ 31148) asks about DHSC/NHS England contacts with Palantir 'including Lord Watson' since 18 September 2026. Guardian, 9 Oct 2026: " + G + "/technology/2026/oct/09/palantir-tom-watson-mob-rule-government-contracts")

# ---------------------------------------------------------------- Lobbying: Register of Consultant Lobbyists
_orcl = {
    "Q1 2023": "https://orcl.file.force.com/sfc/dist/version/download/?oid=00D24000000JWyS&ids=0684J00000iTeBz&d=%2Fa%2F4J000000j6j0%2Fa.vVd2pnzVz6lHzvZ38zMH7AlkqMuIp2ZnLYDdj5hRA&asPdf=false",
    "Q4 2023": "https://orcl.file.force.com/sfc/dist/version/download/?oid=00D24000000JWyS&ids=068Tu0000046Psu&d=%2Fa%2FTu000000SFov%2FtDK8o1hxtJqBDf5eFPze6JMPQUkQYhtxNyTg5tGkd7Y&asPdf=false",
    "Q1 2024": "https://orcl.file.force.com/sfc/dist/version/download/?oid=00D24000000JWyS&ids=068Tu00000E1o68&d=%2Fa%2FTu000001L8LO%2FjnhrCePeI3DGPX6VNSnxbFVB5Pg.ElYifcaybcpDCE8&asPdf=false",
    "Q3 2024": "https://orcl.file.force.com/sfc/dist/version/download/?oid=00D24000000JWyS&ids=068Tu00000Kj7d1&d=%2Fa%2FTu000002HG2P%2FJcCxLm4ZXSzEkqY9vqGh1191hAhzP_RREoO478cJ7Q8&asPdf=false",
    "Q2 2025": "https://orcl.file.force.com/sfc/dist/version/download/?oid=00D24000000JWyS&ids=068P20000171Tmb&d=%2Fa%2FP200000BOCbB%2Fvlc0GYfneWqmdLn2GNzbQfVm9YBT5poB__6h5bwgmI4&asPdf=false",
    "Q3 2025": "https://orcl.file.force.com/sfc/dist/version/download/?oid=00D24000000JWyS&ids=068P20000171Tkz&d=%2Fa%2FP200000BOCZZ%2F1yZfXAXFZ0iYifxmsSiKntTPYkurEAu5VY3jxQios4w&asPdf=false",
    "Q4 2025": "https://orcl.file.force.com/sfc/dist/version/download/?oid=00D24000000JWyS&ids=068P200000ps05q&d=%2Fa%2FP2000005iTQ3%2FXht0WgOxmMNQGTEtFszyrYQjJ3ErmFAml65GkhYZPqs&asPdf=false",
}
_qstart = {"Q1": "01", "Q2": "04", "Q3": "07", "Q4": "10"}
for q, firm, client in [("Q1 2023", "Fleetwood Strategy Limited", "Palantir Technologies UK Limited"),
                        ("Q4 2023", "Fleetwood Strategy Limited", "Palantir Technologies UK Limited"),
                        ("Q1 2024", "Fleetwood Strategy Limited", "Palantir Technologies UK Limited"),
                        ("Q3 2024", "Global Counsel Ltd", "Palantir"),
                        ("Q2 2025", "Lodestone Oxford Limited", "Palantir"),
                        ("Q3 2025", "Global Counsel Ltd", "Palantir"),
                        ("Q4 2025", "Global Counsel Ltd", "Palantir")]:
    qq, yy = q.split()
    add(f"{yy}-{_qstart[qq]}", "lobbying", firm, firm,
        f"The Register of Consultant Lobbyists' {q} return lists '{client}' as a client of {firm}.",
        _orcl[q], "official",
        f"Quarterly return, {q}. Index of returns: {ORCL}. The register only covers consultant lobbying of ministers and permanent secretaries. The published Q2 2023, Q3 2023, Q4 2024 and Q1 2025 files are short and appear incomplete, so absence from them is not evidence of no client relationship; returns before 2023 were not available on the register site.")

# ---------------------------------------------------------------- Lobbying: Mandelson / Global Counsel (official papers)
add("2025-02-20", "lobbying", "Peter Mandelson (then HM Ambassador to the US)", "British Embassy Washington (FCDO)",
    "Emails released under the Humble Address show a programme for a Washington visit by Matthew Doyle listing '7pm - HMA / Plantir tech dinner' on Friday 21 February 2025; Mandelson wrote on 20 February: 'Dinner is not for Palantir it is for Jacob Helberg at the State Department.'",
    HA1, "official",
    "Return to an Address (HC 2-I), Volume II Part I, document 80, pages 224-225 (image pages, read by OCR; spelling 'Plantir' as published). A written answer (PQ 5980, 10 June 2026) did not confirm the dinner's attendees. Publication page: " + HA_PUB)
add("2025-02-26", "lobbying", "John Healey (Defence Secretary); Peter Mandelson", "Ministry of Defence",
    "In a letter released under the Humble Address, John Healey replied to Mandelson's 20 February letter on a UK-US defence industrial partnership, suggesting that in Washington the Prime Minister 'might look to set out our ambition to work with the US on defence industries of the future, with companies — such as Palantir and Anduril — already driving productivity and innovation'.",
    HA1, "official",
    "Volume II Part I, document 102, page 309 (image page, read by OCR). PQ 5981 (10 June 2026) refers to this letter. Publication page: " + HA_PUB)
add("2025-03-05", "lobbying", "Peter Mandelson; Louis Mosley (Palantir)", "British Embassy Washington (FCDO)",
    "An email released under the Humble Address, sent by a partner at 137 Ventures to Mandelson and Louis Mosley, asks the Hill & Valley Forum 2025 to invite 'Ambassador Mandelson' to its daytime forum and dinner, saying 'He is coming with Louis'.",
    HA1, "official",
    "Volume II Part I, document 113, page 334 (image page, read by OCR). The FCDO said (PQ 5981, 10 June 2026) that Mandelson attended the Hill and Valley Forum on 2 May 2025 and that Louis Mosley was also scheduled to attend: " + PQ + "1911180")
add("2025-07-10", "lobbying", "Peter Mandelson; Andy Start (National Armaments Director)", "Ministry of Defence",
    "An embassy note released under the Humble Address records that at a 10 July 2025 meeting the National Armaments Director said 'US companies like Palantir and Anduril have good engagement with UK innovation and capabilities teams', and that Mandelson asked whether any procurements could be announced at the State Visit.",
    HA2, "official",
    "Volume II Part II (corrected), document 318, page 435. Publication page: " + HA_PUB)
add("2025-08-27", "lobbying", "Peter Mandelson; James Roscoe (Deputy Head of Mission)", "British Embassy Washington (FCDO); Ministry of Defence",
    "Emails released under the Humble Address on draft State Visit joint-statement language show MOD officials asking 'who is the MOD lead on the potential Palantir announcement?' and the embassy's deputy head of mission asking Mandelson to raise it with the Defence Secretary; Mandelson replied: 'I am reluctant to intervene on Palantir.'",
    HA3, "official",
    "Volume II Part III (corrected), document 360, pages 26-28; parts redacted. Publication page: " + HA_PUB)
add("2026-02-04", "lobbying", "Peter Mandelson; Global Counsel", "Global Counsel",
    "The Guardian reported that Global Counsel, the lobbying company Mandelson co-founded and part-owns, works for Palantir, and that although he resigned as a director in May 2024 he continued to hold shares according to Companies House; campaigners asked the Cabinet Secretary to release information on his role in the February 2025 Palantir visit.",
    G + "/politics/2026/feb/04/peter-mandelson-palantir-jeffrey-epstein-government", "press",
    "Robert Booth and Dan Sabbagh, 4 Feb 2026. On 10 Feb 2026 the Guardian reported Global Counsel's statement that it had 'publicly declared all relevant work with clients': " + G + "/politics/2026/feb/10/uk-signed-deals-with-us-firms-that-were-clients-of-mandelson-lobbying-company")

# ---------------------------------------------------------------- Lobbying: approaches to ministers
add("2019", "lobbying", "Louis Mosley (Palantir)", "Cabinet Office; Ministry of Justice",
    "The Guardian reported that in 2019 Mosley won a government contract to help with Brexit planning 'after pitching directly to Michael Gove', and that when Rory Stewart was prisons minister Palantir pitched software to manage prisoner data, initially on a no-cost basis.",
    G + "/technology/2026/may/09/who-is-louis-mosley-defending-palantir-critics", "press",
    "Guardian profile, 9 May 2026. Rory Stewart's prisons role is not dated in the article. The Cabinet Office return lists a Gove meeting with Palantir on 2 September 2019 'to discuss Brexit readiness' (see meeting row).")
add("2024-07", "lobbying", "Alex Karp; Palantir executives", "HM Treasury; DSIT; Ministry of Justice; DBT",
    "The Guardian reported letters released under FOI showing that after the July 2024 election a Palantir executive wrote to prisons minister James Timpson about prison data and reoffending risk, and Alex Karp wrote to Rachel Reeves and Peter Kyle asking to meet; it reported the government said Kyle and Reeves had not met Palantir as ministers.",
    G + "/technology/2024/nov/16/tech-firm-palantir-spoke-with-moj-about-calculating-prisoners-reoffending-risks", "press",
    "Ben Quinn, 16 Nov 2024. The article also says Palantir wrote to Darren Jones and Douglas Alexander. Later returns list Kyle meeting Palantir on 6 May 2025 and Reeves attending a defence roundtable including Palantir on 28 February 2025.")
add("2025-03-03", "lobbying", "Louis Mosley (Palantir)", "Department of Health and Social Care",
    "DHSC said in a written answer that the Health Secretary received a letter from Louis Mosley, Palantir's Executive Vice President for the UK and Europe, on 3 March 2025 offering to meet to discuss the roll-out of the NHS Federated Data Platform.",
    *pq(1821384, "2025-07-09", "66353", "Answered 16 July 2025."))
add("2026-02-12", "lobbying", "Wes Streeting; Louis Mosley", "Department of Health and Social Care",
    "The Guardian reported that a DHSC briefing for Wes Streeting before his June 2025 meeting with Louis Mosley said public perception of the Federated Data Platform 'has been affected by the profile of Palantir', and that WhatsApp messages Streeting published with Mandelson did not mention Palantir.",
    G + "/society/2026/feb/12/nhs-deal-with-ai-firm-palantir-called-into-question-after-officials-concerns-revealed", "press",
    "Robert Booth, 12 Feb 2026.")
add("2026-10-02", "lobbying", "Lodestone Oxford Limited", "Lodestone",
    "The Guardian reported that the public affairs firm Lodestone worked for Palantir in 2024 and 2025, including on events in Parliament where Palantir engineers demonstrated systems to MPs, and that a Lodestone co-founder later worked on Andy Burnham's leadership campaign; Lodestone said she had no contact with clients during that time.",
    G + "/technology/2026/oct/02/lobbyist-palantir-martha-dalton-andy-burnham", "press",
    "Robert Booth and Henry Dyer, 2 Oct 2026 (the article names the co-founder). It says Tom Watson had been on Lodestone's 'strategic advisory council'. The Register of Consultant Lobbyists lists Palantir as a Lodestone client in Q2 2025. A Palantir spokesperson said Lodestone's work included 'parliamentary events that enable MPs to see demonstrations of our software'.")

# ---------------------------------------------------------------- Meetings not in departmental returns, or with extra detail
add("2019-08-28", "meeting", "Boris Johnson; Dominic Cummings; Peter Thiel", "Prime Minister's Office, 10 Downing Street",
    "The Guardian reported that leaked files indicate Boris Johnson and Dominic Cummings held an hour-long meeting with Peter Thiel in Downing Street on 28 August 2019, marked 'private' in Johnson's diary and not disclosed in the government's published log of meetings.",
    G + "/uk-news/2025/sep/08/boris-johnson-dominic-cummings-secret-meeting-palantir-peter-thiel", "press",
    "Rowena Mason and Henry Dyer, 8 Sep 2025. Source: 'Boris Files' obtained by Distributed Denial of Secrets. Johnson's statement to the Guardian did not respond directly on the meeting; Thiel did not respond.")
add("2023-06-02", "meeting", "Chloe Smith (Science Secretary); Louis Mosley", "Department for Science, Innovation and Technology",
    "A GOV.UK press release on a roundtable chaired by the Science Secretary with AI companies lists Louis Mosley of Palantir among the attendees.",
    "https://www.gov.uk/government/news/technology-secretary-holds-roundtable-with-leading-ai-innovators", "official", "")
add("2025-02-27", "meeting", "Sir Keir Starmer; Peter Mandelson; Alex Karp", "Prime Minister's Office, 10 Downing Street",
    "The Cabinet Office said the Prime Minister's visit to Palantir's Washington office with Lord Mandelson on 27 February 2025 'was not a formal meeting', so no minutes are held; he 'listened to a short presentation about Palantir's work, followed by a tour of the premises and an introduction to members of staff'.",
    PQ + "1877971", "official",
    "PQ 110411 (5 Mar 2026). 'Not a formal meeting': PQ 77563, " + PQ + "1835620. The visit is not in the PM's quarterly meetings return. The UK Defence Attaché attended (PQ 110806, " + PQ + "1878515) and about 11 MOD uniformed personnel and civil servants observed a technology demonstration (PQ 119908, " + PQ + "1890013). Global Counsel staff were not present (PQ 129003). Palantir was not at the White House meeting (PQ 2049).")
add("2025-06-04", "meeting", "Wes Streeting", "Department of Health and Social Care",
    "DHSC said the Health Secretary met Palantir representatives on 4 June 2025 to discuss the rollout of the Federated Data Platform, including progress towards onboarding all trusts, and that the meeting did not discuss combining data functions under a single NHS data contract.",
    *pq(1822776, "2025-07-14", "67613"))
add("2025-06-09", "meeting", "Louis Mosley (member)", "Ministry of Defence (Defence Industrial Joint Council)",
    "The MOD's list of Defence Industrial Joint Council members, published for its first meeting in June 2025 and on the council's GOV.UK page, includes Louis Mosley of Palantir.",
    "https://www.gov.uk/government/news/first-meeting-of-defence-industry-body-to-forge-new-partnership-and-industry-mobilisation", "official",
    "Standing membership of an MOD-industry council. Current members page (Dec 2025): https://www.gov.uk/government/groups/defence-industrial-joint-council")
add("2025-07-08", "parliament", "Louis Mosley", "Science, Innovation and Technology Committee (Commons)",
    "In oral evidence on the digital centre of government, Louis Mosley told the committee the Prime Minister's visit to Palantir's Washington office was not arranged by Lord Mandelson ('it was done through the proper channels') and that Palantir continued to use Global Counsel 'as one of a number of companies we work with'.",
    CAPI + "OralEvidence/16290", "official",
    "Questions 141-143. Transcript: " + CAPI + "OralEvidence/16290/Document/Html. Web page: https://committees.parliament.uk/oralevidence/16290/html/. He also said Palantir was invited to No 10 with other tech companies in February 2020 at the start of the pandemic.")
add("2025-09-28", "meeting", "John Healey (Defence Secretary); Palantir CEO", "Ministry of Defence",
    "The MOD said the Defence Secretary's 28 September 2025 meeting with Palantir's CEO in London related solely to the non-binding Strategic Partnership Arrangement; an internal briefing referenced the later Enterprise Agreement but it was not discussed.",
    *pq(1881674, "2026-02-12", "113369", "The MOD's July-September 2025 ministerial return separately lists a Healey meeting with Palantir on 10 September 2025 ('Discussion of strategic defence partnership')."))
add("2026-02-05", "meeting", "Downing Street; government spokesperson", "Prime Minister's Office, 10 Downing Street",
    "The Guardian reported that Downing Street refused FOI requests for briefings before the Prime Minister's visit to Palantir in Washington, saying in October 2025 there were no briefings or minutes 'as this was not a formal meeting'; a government spokesperson said 'Palantir is a longstanding investor in the UK'.",
    G + "/politics/2026/feb/05/calls-to-halt-uk-palantir-contracts-grow-amid-lack-of-transparency-over-deals", "press",
    "Robert Booth, 5 Feb 2026. The article says requests about meetings between Palantir's leadership and Starmer and Boris Johnson were refused.")

# ---------------------------------------------------------------- Announcements
add("2022-07-14", "announcement", "Cabinet Office / Border and Protocol Delivery Group", "Cabinet Office",
    "GOV.UK announced six 'Ecosystem of Trust' border pilots, one of them led by Palantir.",
    "https://www.gov.uk/government/news/transformational-border-pilots-to-create-an-ecosystem-of-trust", "official",
    "Cabinet Office returns list Jacob Rees-Mogg meeting Palantir on 30 March and 12 July 2022 'to discuss borders' as a Brexit opportunity.")
add("2023-06-07", "announcement", "Prime Minister's Office; Alex Karp", "Prime Minister's Office, 10 Downing Street",
    "A GOV.UK press release announcing the UK's AI safety summit said Palantir would make the UK its new European HQ for AI development, that it already employed more than 800 people in the UK, and quoted Alex Karp.",
    "https://www.gov.uk/government/news/uk-to-host-first-global-summit-on-artificial-intelligence", "official", "")
add("2023-11-21", "announcement", "Victoria Atkins (Health Secretary)", "Department of Health and Social Care",
    "In a written statement the Health Secretary announced that NHS England had awarded the Federated Data Platform contract to a group led by Palantir Technologies UK, with up to £330 million of investment over seven years.",
    "https://questions-statements-api.parliament.uk/api/writtenstatements/statements/1671624", "official",
    "HCWS57. Web page: https://questions-statements.parliament.uk/written-statements/detail/2023-11-21/hcws57. DHSC's return lists Atkins attending a Palantir demonstration of the platform on 11 December 2023.")
add("2025-09-17", "announcement", "HM Government (US State Visit)", "Department for Business and Trade",
    "A GOV.UK press release on £150bn of US investment announced during the State Visit listed 'Palantir to invest up to £1.5 billion to help make the UK a defence innovation leader and create up to 350 new jobs'.",
    "https://www.gov.uk/government/news/record-breaking-150bn-investment-unveiled-during-us-state-visit", "official",
    "The Prime Minister's Chequers return lists Palantir among guests at a US State Visit business reception on 18 September 2025.")
add("2025-09-18", "announcement", "John Healey (Defence Secretary)", "Ministry of Defence",
    "The MOD announced a strategic partnership with Palantir, signed by the Defence Secretary, to unlock up to £1.5bn of investment, with Palantir making London its European defence headquarters and creating up to 350 jobs, and developing AI capabilities for decision-making, planning and targeting.",
    "https://www.gov.uk/government/news/new-strategic-partnership-to-unlock-billions-and-boost-military-ai-and-innovation", "official",
    "The MOD later described this as 'a nonbinding statement of intent' with no financial commitments (PQ 113367). A three-year Enterprise Agreement, direct-awarded, was signed on 30 December 2025.")
add("2025-11-10", "announcement", "Palantir Technologies UK Ltd", "Ministry of Defence (Armed Forces Covenant)",
    "GOV.UK lists Palantir Technologies UK Ltd as a signatory of the Armed Forces Corporate Covenant.",
    "https://www.gov.uk/armed-forces-covenant-businesses/palantir-technologies-uk-ltd", "official", "")
add("2026-09-24", "announcement", "Defence Secretary", "Ministry of Defence",
    "A GOV.UK news story on work and training placements for young people says the Defence Secretary was joined by representatives of defence companies including Palantir.",
    "https://www.gov.uk/government/news/thousands-of-work-and-training-placements-for-young-people", "official", "")
add("2026-10-20", "announcement", "Palantir", "Palantir (company)",
    "Palantir's UK web page states that 'Palantir has supported HMG deliver its mission for over a decade' and that UK customer data is stored and processed in the UK.",
    "https://www.palantir.com/uk/", "company", "Date is when the page was read.")

# ---------------------------------------------------------------- Parliament (curated; full index in data/influence-parliament.csv)
add("2023-06-22", "parliament", "Lord Markham (DHSC minister); Baroness Brinton", "House of Lords",
    "In a Lords question on the NHS Palantir contract, the minister said the new transition contract with Palantir was procured by direct award through a Crown Commercial Service framework; Baroness Brinton said two senior NHS staff had moved to Palantir the previous year.",
    HAPI + "5CDE47DE-C0BB-454B-90F6-E994C0FC7869.json", "official",
    "Web page: https://hansard.parliament.uk/Lords/2023-06-22/debates/5CDE47DE-C0BB-454B-90F6-E994C0FC7869/NHSProcurementPalantirContract")
add("2026-02-10", "parliament", "Luke Pollard (Defence minister); James Cartlidge; Jon Trickett and others", "House of Commons",
    "Answering an urgent question on MOD contracts with Palantir, the minister said the new enterprise agreement was a direct award justified under the Procurement Act 2023, that the decision was the Defence Secretary's alone and that 'Peter Mandelson had no influence on the decision to award this contract'. Jon Trickett MP said he was aware that 'at least five or six senior civil servants in the Ministry of Defence have gone to work with Palantir'.",
    HAPI + "FECED111-4FA8-4343-BFAF-18D6C13808D0.json", "official",
    "Web page: https://hansard.parliament.uk/Commons/2026-02-10/debates/FECED111-4FA8-4343-BFAF-18D6C13808D0/MinistryOfDefencePalantirContracts. Pollard replied that departing staff have obligations and that Palantir 'employs an awful lot of UK veterans'. Dr Ellie Chowns referred to a Times report of a Palantir party for MOD officials the next day.")
add("2026-02-11", "parliament", "Lord Coaker (Defence minister); Baroness Goldie; Lord Bellingham", "House of Lords",
    "In the Lords the defence minister said no minutes were taken of the Prime Minister's visit to Palantir with the then ambassador, which he described as 'a routine visit', and that the decision to award the contract was made by the Defence Secretary alone.",
    HAPI + "2F5D01F1-7B47-4CCA-A470-E02C764C5DCD.json", "official",
    "Web page: https://hansard.parliament.uk/Lords/2026-02-11/debates/2F5D01F1-7B47-4CCA-A470-E02C764C5DCD/MinistryOfDefencePalantirContracts")
add("2026-02-17", "parliament", "Luke Pollard; Martin Wrigley MP", "Ministry of Defence",
    "The MOD said the Palantir Enterprise Agreement was direct-awarded under Section 41 and Schedule 5 (paragraphs 6 and 7) of the Procurement Act 2023, that no ministers or former officials with prior links to Palantir were involved at any stage, and that the award decision was the Defence Secretary's.",
    *pq(1879654, "2026-02-09", "111951"))
add("2026-02-24", "parliament", "Luke Pollard; James Cartlidge MP", "Ministry of Defence",
    "The MOD said the Strategic Partnership Arrangement announced on 18 September 2025 was 'a nonbinding statement of intent' that created no financial commitments, and that the contract signed on 30 December 2025 followed full commercial and governance processes.",
    *pq(1881672, "2026-02-12", "113367"))
add("2026-03-02", "parliament", "Clive Lewis MP; DHSC, Home Office, DSIT and MOD", "Department of Health and Social Care",
    "DHSC said neither the Health Secretary nor any members of the department had met or corresponded with Lord Mandelson on Palantir; the Home Office said 'No such meetings took place'; DSIT gave a general answer on supplier due diligence; the MOD referred to the Humble Address process.",
    *pq(1879212, "2026-02-05", "111174"))
add("2026-03-06", "parliament", "Luke Pollard; Bradley Thomas MP", "Ministry of Defence",
    "The MOD said: 'As the Secretary of State has publicly said, Peter Mandelson had no influence or involvement in the Defence Enterprise Agreement with Palantir.'",
    *pq(1884867, "2026-02-25", "115875"))
add("2026-03-17", "parliament", "Baroness Anderson of Stoke-on-Trent (Cabinet Office minister); Baroness Finn", "Cabinet Office",
    "Asked why the Palantir visit was not in the Prime Minister's transparency return, Cabinet Office ministers said 'it was not a meeting, and so minutes were not taken'.",
    *pq(1876391, "2026-01-28", "HL14055", "Follows PQ 102820, which asked why the visit was out of scope of the PM's January-March 2025 return."))
add("2026-03-17", "parliament", "Luke Pollard; Mike Wood MP", "Ministry of Defence",
    "The MOD said the Office of the UK Defence Attaché 'holds no record of the meeting as no formal record of the meeting was produced'.",
    *pq(1888730, "2026-03-09", "118785"))
add("2026-03-18", "parliament", "Chris Ward (Cabinet Office minister); Martin Wrigley MP", "Cabinet Office",
    "The Cabinet Office said Palantir is not a strategic supplier to government, with no plans to classify it as one, and that the two largest UK public sector contracts with Palantir, the NHS Federated Data Platform and the MOD Enterprise Agreement, were initially awarded by the previous government.",
    *pq(1887477, "2026-03-04", "117971"))
add("2026-03-23", "parliament", "Luke Pollard; Martin Wrigley MP", "Ministry of Defence",
    "The MOD said its relationship with Palantir had developed over the last decade and that the first formal Enterprise Agreement was signed in November 2022 under the previous government, following earlier operational use of Palantir software.",
    *pq(1890369, "2026-03-11", "120127"))
add("2026-04-13", "parliament", "Chris Ward; Mike Wood MP", "Cabinet Office",
    "The Cabinet Office said it wrote to two MPs about the Palantir contract on 25 February 2026, noting that the Member for Brentwood and Ongar 'personally signed off the original spending approval for the contract during his time at the Cabinet Office under the previous Conservative government'.",
    *pq(1888574, "2026-03-09", "118775"))
add("2026-04-23", "parliament", "Luke Pollard; Charlie Dewhirst MP", "Ministry of Defence",
    "The MOD said that, based on the information it holds, it is not aware of any communications sent by Lord Mandelson in relation to the contract with Palantir.",
    *pq(1901521, "2026-04-20", "128584"))
add("2026-04-28", "parliament", "Luke Pollard; Charlie Dewhirst MP", "Ministry of Defence",
    "The MOD said Global Counsel staff were not present at the Prime Minister's visit to Palantir on 27 February 2025 and that the UK Defence Attaché had not corresponded or met with Global Counsel representatives since July 2024.",
    *pq(1901968, "2026-04-21", "129003"))
add("2026-04-30", "parliament", "Jon Trickett MP", "Cabinet Office",
    "Jon Trickett asked what meetings the Prime Minister has had with Palantir since May 2024; no answer is recorded in Parliament's written questions service as at 20 October 2026 (answer due 30 April 2026).",
    *pq(1903556, "2026-04-28", "130041"))
add("2026-05-20", "parliament", "Lord Hendy (minister)", "House of Lords",
    "Closing a King's Speech debate, a government minister said: 'We are reviewing the federated data platform contract in advance of the break point.'",
    HAPI + "268969E3-3EFA-4C4F-97E2-1DDE9C1CBE30.json", "official",
    "Web page: https://hansard.parliament.uk/Lords/2026-05-20/debates/268969E3-3EFA-4C4F-97E2-1DDE9C1CBE30/KingSSpeech")
add("2026-06-01", "parliament", "Darren Jones (Chief Secretary to the Prime Minister)", "House of Commons",
    "Presenting the second tranche of Humble Address documents, the minister said references to Palantir and Anduril had not been redacted outside the Intelligence and Security Committee process, and said he challenged 'the assumption that the Government are developing a \"close relationship\" with Palantir'.",
    HAPI + "D3A5D4C6-EC00-460C-A981-39C17B72A73C.json", "official",
    "Web page: https://hansard.parliament.uk/Commons/2026-06-01/debates/D3A5D4C6-EC00-460C-A981-39C17B72A73C/LordMandelsonHumbleAddressGovernmentResponse. The volumes' methodology statement (para 38) says there 'has been particular public interest in information involving Global Counsel and Palantir': " + HA1)
add("2026-06-08", "parliament", "Sarah Jones (Home Office minister); Martin Wrigley MP", "House of Commons",
    "The minister said Palantir was the preferred supplier for the National Firearms Licensing Management System after an open and competitive process run by the Police Digital Service and BlueLight Commercial, and that 'Palantir is not buying the job'.",
    HAPI + "110C9C82-8170-4BCC-9294-B070D2482E30.json", "official",
    "Web page: https://hansard.parliament.uk/Commons/2026-06-08/debates/110C9C82-8170-4BCC-9294-B070D2482E30/PoliceAITrials. Mr Wrigley said Palantir's £7.5 million bid was 44% of the estimated £17 million value.")
add("2026-06-10", "parliament", "Baroness Merron (DHSC minister); Lord Pack", "Department of Health and Social Care",
    "DHSC said three Palantir contractors have administrative permissions in NHS England's National Data Integration Tenant, and that 19 of 22 non-NHS England contractors doing data engineering are employed by Palantir or its supplier consortium.",
    *pq(1907717, "2026-05-19", "HL286"))
add("2026-06-16", "parliament", "Preet Kaur Gill (DHSC minister); Lee Dillon MP", "Department of Health and Social Care",
    "DHSC said ministers were not informed of routine access arrangements in the National Data Integration Tenant of the Federated Data Platform before May 2026.",
    *pq(1910903, "2026-06-01", "5804"))
add("2026-06-19", "parliament", "Stephen Doughty (FCDO minister); Mike Wood and Charlie Dewhirst MPs", "Foreign, Commonwealth and Development Office",
    "The FCDO said no correspondence or contact between the British Embassy and Global Counsel had been identified in relation to the Prime Minister's visit to Palantir.",
    *pq(1914567, "2026-06-10", "8550"))
add("2026-06-29", "parliament", "Lord Coaker (Defence minister); Lord Gove; Baroness Chakrabarti", "House of Lords",
    "In a Lords question on Palantir contracts, the defence minister said officials told him Palantir was 'the only available platform' for the MOD's needs; Lord Gove said that as a minister he saw how Palantir's technology 'helped to save lives in the NHS' and 'helped to ensure that those fleeing persecution from the Ukraine war could have a safe home in this country'.",
    HAPI + "886A7BA6-14FD-4D70-8F56-2827D9B44053.json", "official",
    "Web page: https://hansard.parliament.uk/Lords/2026-06-29/debates/886A7BA6-14FD-4D70-8F56-2827D9B44053/PalantirPublicServiceContracts")
add("2026-09-08", "parliament", "Luke Pollard; Mike Wood MP", "Ministry of Defence",
    "The MOD said the Palantir visit 'was organised by Ministry of Defence officials as part of the former Prime Minister's trip to Washington' and that defence officials invited the Defence Attaché; in November 2025 the FCDO had said 'Officials from our Embassy in Washington arranged this trip in the normal way'.",
    *pq(1931664, "2026-08-28", "21148"))
add("2026-09-08", "parliament", "Luke Pollard; Mike Wood MP", "Ministry of Defence",
    "The MOD said it has no record of any meetings or correspondence involving Lord Mandelson in relation to the award of the Defence Enterprise Agreement with Palantir, and no formal correspondence with Global Counsel while he was ambassador.",
    *pq(1931634, "2026-08-28", "21118"))
add("2026-10-09", "parliament", "Gregory Stafford MP", "Department of Health and Social Care",
    "A written question asks what meetings, calls and correspondence have taken place since 18 September 2026 between Palantir Technologies UK, 'including Lord Watson', and DHSC and NHS England ministers and officials; it was unanswered as at 20 October 2026.",
    *pq(1945078, "2026-10-09", "31148"))
add("2026-03-18", "parliament", "Lord Scriven; Baroness Merron (DHSC minister)", "Department of Health and Social Care",
    "A Lords question cited reports that the Joint Chair of the North West London Acute Provider Collaborative had advised Palantir while advocating integration of patient-level data into its platform; the minister's answer set out NHS conflict-of-interest guidance.",
    *pq(1892763, "2026-03-18", "HL15727"))

# ---------------------------------------------------------------- Select committees
add("2022-03-24", "parliament", "Palantir Technologies UK, Ltd", "Parliamentary committee inquiry 'The right to privacy: digital data'",
    "Palantir Technologies UK submitted written evidence to the inquiry 'The right to privacy: digital data'.",
    CAPI + "WrittenEvidence/107376", "official",
    "Committee shown in Parliament's committees API as the Science and Technology Committee (Commons). Web page: https://committees.parliament.uk/writtenevidence/107376/html/")
add("2023-04-20", "parliament", "Palantir Technologies UK, Ltd (Global Director of Privacy and Civil Liberties Engineering)", "AI in Weapon Systems Committee (Lords)",
    "Palantir gave oral evidence to the Lords AI in Weapon Systems Committee on 20 April 2023 and later submitted written evidence (published 8 June 2023).",
    CAPI + "OralEvidence/13042", "official",
    "Written evidence: " + CAPI + "WrittenEvidence/120296. Web page: https://committees.parliament.uk/oralevidence/13042/html/")
add("2024-02-27", "parliament", "Palantir Technologies Ltd (Head of Defence AI, UK)", "Defence Committee (Defence Sub-Committee)",
    "Palantir's UK head of defence AI gave oral evidence to the Defence Sub-Committee inquiry on developing AI capacity in UK defence, alongside Lockheed Martin, Leonardo, Anduril and Faculty; Palantir also submitted written evidence (published 24 January 2024).",
    CAPI + "OralEvidence/14358", "official",
    "Written evidence: " + CAPI + "WrittenEvidence/127784. Web page: https://committees.parliament.uk/oralevidence/14358/html/")
add("2026-06-03", "parliament", "Science, Innovation and Technology Committee (Commons)", "Science, Innovation and Technology Committee (Commons)",
    "The committee's report 'Rewiring the state: Delivering digital government' (HC 61) concluded that 'Palantir should not have such a significant role in the UK public sector', recommended exercising the February 2027 break clause in the Federated Data Platform contract, and asked the government to explain the £240 million direct award to Palantir.",
    CAPI + "Publications/53352/Document/298462/OriginalFormat", "official",
    "First Report of Session 2026-27, paragraphs 92-98. Publication record: " + CAPI + "Publications/53352")
add("2026-07-08", "parliament", "Health and Social Care Committee (Commons); Preet Kaur Gill (minister)", "Health and Social Care Committee (Commons)",
    "After a 16 June 2026 evidence session, the Health and Social Care Committee wrote to the minister recommending that Palantir's Federated Data Platform contract not be extended when it ends in March 2027, citing mistrust, contested evidence of benefits and alternative tools.",
    CAPI + "Publications/54095/Document/302120/OriginalFormat", "official",
    "Letter dated 8 July 2026, published 9 July 2026. The letter says the minister apologised at the committee for not telling the public Palantir had access to patient-identifiable data. Publication record: " + CAPI + "Publications/54095")
