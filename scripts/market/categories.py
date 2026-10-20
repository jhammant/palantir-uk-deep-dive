#!/usr/bin/env python3
"""Which published category labels count as IT, software, licences, digital or data services.

classify(payer, label) -> (included, reason, listed)
    included: True if the label counts as IT/software/data spend
    reason:   why, in plain words
    listed:   True if the label goes into data/market-categories.csv (every included label,
              and every borderline label that was left out)

Rules are applied in this order:
 1. a decision for that payer and that exact label (PAYER_DECISIONS)
 2. a hard exclusion (HARD_EXCLUDE), even if the label also names IT
 3. a label that names IT, ICT, computing or software is included (STRONG)
 4. an exclusion (EXCLUDE): telecoms, printing, marketing, research and so on
 5. an inclusion pattern (INCLUDE): digital, data, technology, hosting, networks ...
 6. a borderline pattern (BORDERLINE): left out, but listed so the choice can be checked

Labels are compared in upper case with runs of spaces collapsed.

it_scheme(payer, labels_in_file) says whether a file's category column can separate IT
spend at all. The three Bedfordshire/Cambridgeshire police reports classify suppliers by
type ("PROVISION OF SERVICE", "TELEPHONE PROVIDER"), not spend by purpose; NHS England's
files before April 2025, and some NHS Improvement sheets, use broad NHS expense groups
("ESTABLISHMENT", "SUPPLIES AND SERVICES – GENERAL") that have no IT group.
"""
import re

STRONG = re.compile(r"\bI\.?T\.?(?=$|[^A-Z])|\bICT\b|COMPUT|SOFTWARE|SOTWARE|INFORMATION TECHNOLOGY|"
                    r"INFORMATION AND COMMUNICATIONS TECHNOLOGY")
STRONG_REASON = "names IT, ICT, computing or software"

HARD_EXCLUDE = [
    (r"NON-IT", "says non-IT"),
    (r"WHITEHALL SYSTEMS", "Whitehall district heating and building systems, not IT"),
    (r"MOU COMMISSION", "commission shared with other buying bodies under a memorandum of understanding; not a purchase"),
]

EXCLUDE = [
    (r"TELECOM|TELEPHON|\bPHONES?\b|MOBILE|\bVOICE\b|\bFAX\b|SWITCHBOARD|CALL CHARGES",
     "telecoms or telephony; left out because the question is IT, software and data"),
    (r"PRINT", "printing"),
    (r"MARKETING|PUBLICATIONS|DIGITAL MEDIA|ADVERTIS|MEDIA DATABASE", "marketing, advertising, publications or press distribution"),
    (r"PROPERTY COSTS", "property costs"),
    (r"DATA COLLECTION|DATA CAPTURE", "field data collection (surveys, monitoring), not IT or data platform services"),
    (r"RECORDS AND DATA STORAGE", "mainly a recharge to the Home Office and physical records storage"),
    (r"ROAD FUND|\bROD LICEN|COPYRIGHT|LICENCES AND CONSENTS|LICENCE FEES/LEVIES|LICS AND INSURANCE|\bTV\b|MUSIC",
     "a licence that is not a software licence"),
    (r"^INC - ", "income line, not spend"),
    (r"RESEARCH|\bR ?& ?D\b|R\+D", "research and development"),
    (r"SCANNING", "document scanning service"),
    (r"ELECTRONIC MONITORING", "offender electronic monitoring service"),
]

INCLUDE = [
    (r"\bSW LIC", "software licences (SW LIC)"),
    (r"NETWORK|DATA COMMS", "data networks"),
    (r"\bDIGITAL\b", "names digital services"),
    (r"TECHNOLOG", "names technology services"),
    (r"\bDATA\b|DATABASE", "names data services"),
    (r"HOSTING|\bCLOUD\b", "hosting or cloud services"),
    (r"\bWEB\b|\bWEB_|WEBSITE", "web services or websites"),
    (r"CYBER|PEN TEST|INFORMATION ASSURANCE|INFORMATION SECURITY", "IT security"),
    (r"\bIS (COSTS|SUPPORT|DEVELOPMENT|INFRASTRUCTURE)", "information systems (IS)"),
    (r"\bERP\b", "enterprise resource planning (ERP) system"),
    (r"MICROSOFT|ORACLE|SALESFORCE|WORKDAY", "names a software product"),
    (r"GEOSPATIAL|CARTOGRAPHIC", "geospatial data (mapping and imagery)"),
    (r"E-?FINANCIAL|EPROC|CHOOSE & BOOK|CLINICAL DECISION SYSTEM|FINANCE SYSTEM", "maintenance of a named software system"),
]

BORDERLINE = [
    (r"INTANGIBLE|^IA - |^ASSETS UNDER CONSTRUCTION$|ADDITIONS-POA & AUC",
     "intangible or capital asset additions; the label does not say software or IT"),
    (r"SHARED SERVICES OUTSOURC|OUTSOURCED SERVICES|OUTSOURC(E|ING) CONTRACT|^OUTSOURCING$|OUTSOURCED TECHNICAL",
     "outsourcing not named as ICT"),
    (r"TECHNICAL (SERVICES|SUPPORT|ADVICE|PROFESSIONAL)|CONSULTANCY - TECHNICAL|TECH SUPPORT",
     "technical services, not named as IT"),
    (r"LICEN[CS]", "licence of an unspecified kind"),
    (r"INFORMATION SERVICES|INFORMATION &", "information services, not named as IT or data"),
    (r"\bSYSTEMS?\b", "a system that is not named as IT"),
]

# (included, reason) for exact labels, per payer; the reason cites the supplier evidence
PAYER_DECISIONS = {
    "cabinet-office": {
        "LICENCE COSTS": (True, "licences; the largest payees are software licence vendors and resellers "
                                "(BravoSolution, Softcat, Workday, Mercato, Dun & Bradstreet) and NHS England/DHSC"),
        "PPE - AUC ADDITIONS": (False, "building and plant assets under construction (top payees are construction firms)"),
        "IA - POA & AUC - COST - ADDITIONS": (False, "intangible assets under construction; top payees are consultancies "
                                                    "(Deloitte, PA Consulting); the label does not say software"),
        "EXP - PURCHASE OF GOODS/SERVICES - TELECOMS - DATA COMMUNICATIONS":
            (False, "telecoms; top payees are SMS and mobile messaging firms (MMG Mobile Marketing Group, Firetext)"),
        "EXP - PURCHASE OF GOODS/SERVICES - GEOSPATIAL DATA SERVICES - CAPITAL":
            (True, "geospatial data services; top payees Ordnance Survey, Getmapping, Bluesky"),
        "DIGITAL AND TECHNOLOGY SERVICES - GOVPRINT EXPENDITURE": (False, "printing (GovPrint) under a digital heading"),
        "EXP - PURCHASE OF GOODS/SERVICES - CONSULTANCY - TECHNICAL": (False, "technical consultancy, not named as IT"),
    },
    "defra": {
        "EXP - PURCHASE OF GOODS/SERVICES - SUPPORT - CIS CAPGEMINI CONTRACT":
            (True, "support contract paid entirely to Capgemini UK PLC, Defra's IT services supplier"),
        "IA - POA & AUC - COST - ADDITIONS":
            (False, "intangible assets under construction; the label does not say software, although the largest "
                    "payees are IT firms (Capgemini, Equal Experts, Risual, Node 4, Kainos); Palantir's Defra lines are here"),
        "DATA COLLECTION SERVICES": (False, "field data collection; top payees are universities and survey firms"),
        "TECHNICAL SERVICES": (False, "technical and scientific services; top payees are research bodies"),
    },
    "home-office": {
        "SYSTEM CLEARING": (False, "accounting clearing account for capital projects of every kind "
                                   "(top payees include IBM and Galliford Try Construction)"),
        "CURFEW & ELECTRONIC MONITORING": (False, "offender tagging service, paid to the Ministry of Justice"),
    },
    "hm-treasury": {
        "CORP. SUBSCRIPTIONS AND OTHER INFORMATION SERVICES":
            (True, "information services; top payees are data and software providers (Phoenix Software, Bloomberg, "
                   "Sayari Analytics, S&P Global Market Intelligence) alongside publications (OECD, Financial Times)"),
    },
    "london-ambulance-service": {
        "CAD TOOLS MAINTENANCE": (True, "computer-aided dispatch software; payees include Priority Dispatch, "
                                        "Northrop Grumman Information Technology, NEC Software Solutions"),
        "PTS CONTROL MAINTENANCE": (True, "patient transport control system; payees are IT suppliers (Boxxe, Dell, CDW, Microsoft)"),
        "CONSULTANCY/PROFESSIONAL SW": (False, "SW here is not software: the main payee is a vehicle converter"),
        "TECHNICAL SUPPORT - CONTRACT": (False, "technical support of mixed kinds (Department of Health, Telent, Capita, BT)"),
        "MOBILE DISPLAY UNIT": (False, "vehicle telematics units (Traffilog)"),
    },
    "chelsea-and-westminster-hospital-nhs-ft": {
        "LICENSE FEE": (True, "single payee ICNH Ltd (DrDoctor), a patient-messaging software licence"),
        "TOMCAT SUPPORT": (True, "support for a cardiology software system"),
        "INTANGIBLE EXPENDITURE": (False, "intangible assets; the label does not say software, although payees include "
                                          "Softcat and Sectra"),
        "INFRASTRUCTURE UPGRADE": (False, "engineering works (JCA Engineering)"),
        "LV1 INFRASTRUCTURE UPGRADE PHASE 2": (False, "engineering works"),
        "LV1 INFRASTRUCTUREUPGRADE PHASE 2": (False, "engineering works"),
        "MANAGED SERVICE CONTRACT": (False, "medical equipment managed service (Medtronic)"),
        "PROVISION OF HEALTHCARE SYSTEM": (False, "healthcare service from another NHS trust"),
        "BMS AND MECHANICAL SYSTEMS UPGRADE": (False, "building management and mechanical systems"),
        "CHILLED WATER SYSTEM": (False, "building system"),
        "BLOOD MANAGEMENT SYSTEM": (False, "clinical system; the label does not say software"),
    },
    "nhs-england": {
        "DIGITAL PROCUREMENT AND SERVICES": (True, "NHS England's IT and digital expense group, used in its files from April 2025"),
        "ESTABLISHMENT": (False, "broad NHS expense group for administration costs; before April 2025 it held most IT "
                                 "spend (its lines fell from about 200 a month to about 20 when 'Digital Procurement and "
                                 "Services' began), but it also holds other costs, so it cannot stand in for IT"),
    },
    "coventry-city-council": {
        "SERVICES - LICENCES": (False, "licences of mixed kinds (software, copyright, education programmes)"),
    },
    "dbt": {
        "TECHNICAL ADVICE / SERVICES & SUPPORT": (False, "technical advice; not named as IT (largest payee Public Digital)"),
        "OTHER TECHNICAL PROFESSIONAL SERVICES": (False, "technical professional services, not named as IT"),
    },
    "hertfordshire-pcc": {
        "NETWORK SERVICES": (False, "paid mostly to Hertfordshire County Council, another PCC, and advertising and "
                                    "film companies; not IT networking"),
        "HARDWARE - PURCHASE": (True, "hardware bought from IT resellers (Computacenter, SCC)"),
    },
    "ministry-of-defence": {
        "INTANGIBLES SUME": (False, "single-use military equipment intangible assets"),
        "INTANGIBLES NON SUME": (False, "intangible assets other than military equipment; the label does not say software"),
        "DESIGN SERVICES AND MINOR EQUIPMENT PURCHASES": (False, "design services and minor equipment; not named as IT"),
        "PSS OTHER TECH SUPPORT EXC R+D": (False, "technical support, not named as IT"),
    },
}

# broad NHS expense groups that carry no IT group
NHS_COARSE = {
    "SERVICES FROM OTHER NHS BODIES", "EDUCATION AND TRAINING", "PURCHASE OF HEALTHCARE FROM NON-NHS BODIES",
    "SUPPLIES AND SERVICES – GENERAL", "SUPPLIES AND SERVICES - GENERAL", "GPMS/APMS AND PCTMS",
    "SUPPLIES AND SERVICES – CLINICAL", "SUPPLIES AND SERVICES - CLINICAL", "ESTABLISHMENT", "CAPITAL",
    "OTHER PROFESSIONAL FEES", "GRANTS TO OTHER PUBLIC BODIES", "PREMISES", "CONSULTANCY SERVICES",
    "GENERAL OPTHALMIC SERVICES", "GENERAL DENTAL SERVICES AND PERSONAL DENTAL SERVICES", "TRANSPORT",
    "PHARMACEUTICAL SERVICES", "RESEARCH AND DEVELOPMENT (EXCLUDING STAFF COSTS)", "OTHER",
    "NHS ENGLAND RUNNING COSTS", "EXCLUDE", "INVENTORIES",
}

NO_IT_SCHEME = {
    "bedfordshire-police": "the Category Description column classifies the supplier by type (for example "
                           "'PROVISION OF SERVICE', 'TELEPHONE PROVIDER', 'CONSULTANCY'), not the purpose of the spend; "
                           "no label means IT or software",
    "cambridgeshire-pcc": "the Category Description column classifies the supplier by type (for example "
                          "'PROVISION OF GOODS & SERVICE', 'UTILITIES'), not the purpose of the spend; no label means "
                          "IT or software",
}


def norm(label):
    return re.sub(r"\s+", " ", (label or "").replace("\xa0", " ")).strip().upper()


def classify(payer, label):
    lab = norm(label)
    if not lab:
        return False, "", False
    dec = PAYER_DECISIONS.get(payer, {}).get(lab)
    if dec:
        return dec[0], dec[1], True
    for pat, why in HARD_EXCLUDE:
        if re.search(pat, lab):
            looks = bool(STRONG.search(lab)) or any(re.search(p, lab) for p, _ in INCLUDE + BORDERLINE)
            return False, why, looks
    if STRONG.search(lab):
        return True, STRONG_REASON, True
    inc = next((why for pat, why in INCLUDE if re.search(pat, lab)), None)
    for pat, why in EXCLUDE:
        if re.search(pat, lab):
            return False, why, bool(inc) or bool(re.search(r"TELECOM|TELEPHON|PHONE|MOBILE|VOICE|LICEN|DATA", lab))
    if inc:
        return True, inc, True
    for pat, why in BORDERLINE:
        if re.search(pat, lab):
            return False, why, True
    return False, "", False


def it_scheme(payer, labels_in_file):
    """(True, '') if a file's category column can separate IT spend, else (False, reason)."""
    if payer in NO_IT_SCHEME:
        return False, NO_IT_SCHEME[payer]
    labs = {norm(x) for x in labels_in_file if x}
    if not labs:
        return False, "the file has no category column"
    if payer in ("nhs-england", "nhs-improvement-monitor-tda") and labs <= NHS_COARSE:
        return False, "the file uses broad NHS expense groups with no IT group"
    return True, ""
