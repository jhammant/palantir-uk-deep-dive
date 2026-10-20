// Every figure the video shows, computed from the site's data bundle
// (window.PUK in ../site/assets/bundle.js). Nothing here is typed in by hand:
// numbers, dates and quotes are read from the bundle, and each claim the
// script makes ("both direct awards", "five months later", "2nd-largest") is
// checked against the data. If the data changes so a claim no longer holds,
// the build stops with an error instead of rendering a wrong caption.

/* ------------------------------------------------------------------ types */

export interface Contract {
  awarded: string;
  buyer: string;
  title: string;
  value: number;
  year: string;
  route: string;
  procedure_rationale: string;
  notes: string;
  source: string;
}
interface Payment { payer: string; amount: number; counted: boolean }
interface Reconciliation { payer: string; paid: number; last: string; no_notice_found: boolean }
interface MarketRow { payer: string; period: string; palantir_share_of_it: string; coverage_note: string }
interface MarketTop { payer: string; period: string; rank: string; supplier: string }
interface GroupTax { year: string; jurisdiction: string; measure: string; amount: number; note: string }
interface Revolving { person: string; direction: string; former_role: string; former_org: string; source_type: string }
interface Quote { who: string; role: string; date: string; quote: string; context: string; source_type: string }

export interface Puk {
  generated: string;
  contracts: Contract[];
  payments: Payment[];
  reconciliation: Reconciliation[];
  market: MarketRow[];
  marketTop: MarketTop[];
  groupTax: GroupTax[];
  revolving: Revolving[];
  quotes: Quote[];
  notes: Record<string, string>;
}

/* ---------------------------------------------------------------- helpers */

function need<T>(value: T | undefined | null | false, message: string): T {
  if (value === undefined || value === null || value === false) {
    throw new Error(`Video data check failed: ${message}`);
  }
  return value as T;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTH_INDEX: Record<string, number> = Object.fromEntries(MONTHS.map((m, i) => [m, i]));
const NUMBER_WORDS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve"];

/** £240.6m */
export const gbpM = (v: number) => `£${(v / 1e6).toFixed(1)}m`;
/** $427.4m */
export const usdM = (v: number) => `$${(v / 1e6).toFixed(1)}m`;
/** An upper bound, rounded up so "under $X" stays true: 1,084,300 -> "$1.1m". */
export const usdMCeil = (v: number) => `$${(Math.ceil(v / 1e5) / 10).toFixed(1)}m`;
export const pct0 = (f: number) => `${Math.round(f * 100)}%`;
export const pct1 = (f: number) => `${(f * 100).toFixed(1)}%`;
/** "2025-12-17" -> "Dec 2025" */
export const monthYear = (iso: string) => `${MONTHS[Number(iso.slice(5, 7)) - 1]} ${iso.slice(0, 4)}`;
const ordinal = (n: number) => `${n}${n % 100 >= 11 && n % 100 <= 13 ? "th" : ["th", "st", "nd", "rd"][n % 10] ?? "th"}`;
const stripTags = (html: string) => html.replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const titleCase = (s: string) =>
  s.replace(/\b(LTD|LIMITED|PLC)\b\.?/g, "").trim().toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
/** Drop a leading conjunction/connective and capitalise: "And the NHS…" -> "The NHS…". */
const tidyQuote = (q: string) => {
  const t = q.trim().replace(/^[“"]|[”"]$/g, "").replace(/^(And|Most importantly,)\s+/, "");
  return t.charAt(0).toUpperCase() + t.slice(1);
};

/* ---------------------------------------------------------- receipt lines */

// Short labels for the largest awards. Each matcher must hit exactly one of the
// top awards; the year and value always come from the contract itself.
const RECEIPT_LABELS: { match: (c: Contract) => boolean; label: string }[] = [
  { match: (c) => /enterprise agreement/i.test(c.title) && /defence/i.test(c.buyer), label: "MoD enterprise agreement" },
  { match: (c) => /federated data platform/i.test(c.title), label: "NHS Federated Data Platform" },
  { match: (c) => /crown commercial service/i.test(c.buyer), label: "Crown Commercial Service" },
  { match: (c) => /transition & exit/i.test(c.title), label: "NHS “Transition & Exit” from Palantir" },
  { match: (c) => /commissioning board/i.test(c.title), label: "NHS Covid data platform" },
  { match: (c) => /energy system operator/i.test(c.buyer), label: "NESO, the grid operator" },
];
const RECEIPT_LINES = 7;

const shortBuyer = (buyer: string) =>
  /defence/i.test(buyer) ? "MoD" : /energy system operator/i.test(buyer) ? "NESO" : need(null, `no short name for buyer ${buyer}`);

/* ------------------------------------------------------------------ roles */

// Short, readable versions of `former_role` for the revolving-door cascade.
// Each one is matched against the data's own wording, in display order.
const ROLE_LABELS: { match: RegExp; label: string }[] = [
  { match: /^Minister of State for the Armed Forces/, label: "Former Armed Forces Minister" },
  { match: /^Chief of the Secret Intelligence Service/, label: "Former Chief of the Secret Intelligence Service" },
  { match: /^Second Permanent Secretary, MOD/, label: "Former MoD Second Permanent Secretary" },
  { match: /^Director General, AUKUS/, label: "Former Director General, AUKUS" },
  { match: /^Lieutenant General, British Army \(former Director Special Forces\)/, label: "Former Director Special Forces" },
  { match: /^Director \(Major General\)/, label: "Former Major General, MoD" },
  { match: /^Special Adviser \(to the Prime Minister/, label: "Former Special Adviser to the Prime Minister" },
  { match: /^Special Adviser to the Prime Minister.*Defence/, label: "Former Special Adviser, No 10 and Defence" },
  { match: /^Legal Adviser to the Foreign and Commonwealth Office/, label: "Former Legal Adviser, Foreign Office" },
  { match: /^Strategy Director$/, label: "Former Strategy Director, MoD" },
  { match: /^Director Policy$/, label: "Former Director of Policy, MoD" },
  { match: /^Deputy Director, Commercial$/, label: "Former Deputy Director, Commercial, Cabinet Office" },
  { match: /^Director of AI, NHSX/, label: "Former Director of AI, NHSX" },
  { match: /^Councillor, Royal Borough of Kensington and Chelsea/, label: "Former Councillor, Kensington and Chelsea" },
];

/* ------------------------------------------------------------------- main */

export function computeFigures(puk: Puk) {
  const C = puk.contracts;
  const generatedIso = need(puk.generated.match(/^\d{4}-\d{2}-\d{2}/)?.[0], "bundle.generated has no date");

  /* Contract awards */
  const total = C.reduce((s, c) => s + c.value, 0);
  const years = C.map((c) => c.year).sort();
  const byValue = [...C].sort((a, b) => b.value - a.value);

  const receiptLines = byValue.slice(0, RECEIPT_LINES).map((c) => {
    const hits = RECEIPT_LABELS.filter((l) => l.match(c));
    need(hits.length === 1, `top award "${c.title}" (${gbpM(c.value)}) needs exactly one receipt label`);
    return { label: `${hits[0].label}, ${c.year}`, value: c.value, noCompetition: c.route === "Direct award" };
  });
  const rest = byValue.slice(RECEIPT_LINES);
  const restValue = rest.reduce((s, c) => s + c.value, 0);

  const routeTotals = new Map<string, number>();
  for (const c of C) routeTotals.set(c.route, (routeTotals.get(c.route) ?? 0) + c.value);
  const routes = [...routeTotals.entries()]
    .map(([route, value]) => ({ route, value, share: value / total, isDirect: route === "Direct award" }))
    .sort((a, b) => Number(b.isDirect) - Number(a.isDirect) || b.value - a.value);
  const direct = need(routes.find((r) => r.isDirect), "no Direct award route");

  // The two biggest awards of the 12 months before the bundle was built.
  const yearAgo = `${Number(generatedIso.slice(0, 4)) - 1}${generatedIso.slice(4)}`;
  const recent = byValue.filter((c) => c.awarded > yearAgo).slice(0, 2);
  need(recent.length === 2 && recent.every((c) => c.route === "Direct award"),
    "the two biggest awards of the past 12 months are no longer both direct awards");
  const recentDirect = recent.map((c) => ({ buyer: shortBuyer(c.buyer), value: c.value, date: monthYear(c.awarded) }));

  /* Payments */
  const counted = puk.payments.filter((p) => p.counted);
  const paidTotal = counted.reduce((s, p) => s + p.amount, 0);
  const paidBodies = new Set(counted.map((p) => p.payer)).size;
  const noNotice = puk.reconciliation.filter((r) => r.no_notice_found);
  const mod = need(puk.reconciliation.find((r) => r.payer === "Ministry of Defence"), "no MoD reconciliation row");

  /* Lock-in */
  const neso = need(C.find((c) => /energy system operator/i.test(c.buyer)), "no NESO contract");
  const nesoQuote1 = "proprietary architecture licensed exclusively by Palantir";
  const nesoQuote2 = "Transitioning to an alternative supplier is not possible without significant cost";
  need(neso.procedure_rationale.includes(nesoQuote1), "NESO rationale no longer contains the proprietary-architecture quote");
  need(neso.procedure_rationale.includes(nesoQuote2), "NESO rationale no longer contains the transitioning quote");
  const exit = need(C.find((c) => /transition & exit/i.test(c.title)), "no NHS Transition & Exit contract");
  const fdp = need(C.find((c) => /federated data platform/i.test(c.title)), "no FDP contract");
  const months = (Number(fdp.awarded.slice(0, 4)) - Number(exit.awarded.slice(0, 4))) * 12
    + Number(fdp.awarded.slice(5, 7)) - Number(exit.awarded.slice(5, 7));
  need(months > 0 && months < NUMBER_WORDS.length, "FDP award no longer follows the exit contract within a year");
  const exitPurpose = "for the transition from the Palantir Foundry platform";
  need(exit.notes.includes(exitPurpose), "exit contract notice no longer describes the transition from Foundry");
  need(stripTags(puk.notes["sovereignty-notes"] ?? "").includes("Palantir-led consortium"),
    "sovereignty notes no longer say the FDP went to a Palantir-led consortium");

  /* Market share */
  const nhsRow = need(puk.market.find((m) => m.payer === "NHS England" && m.period === "all"), "no NHS England market row");
  const win = need(nhsRow.coverage_note.match(/IT figures cover (\w{3}) (\d{4}) to (\w{3}) (\d{4}) only/),
    "NHS England coverage note no longer gives the IT window");
  const itWindow = win[2] === win[4] ? `${win[1]}–${win[3]} ${win[4]}` : `${win[1]} ${win[2]}–${win[3]} ${win[4]}`;
  need(MONTH_INDEX[win[1]] !== undefined && MONTH_INDEX[win[3]] !== undefined, "unreadable IT window months");
  const nhsTop = puk.marketTop.filter((t) => t.payer === "NHS England" && t.period === "all");
  const nhsRank = Number(need(nhsTop.find((t) => /palantir/i.test(t.supplier)), "Palantir not in NHS England top suppliers").rank);
  const nhsLeader = need(nhsTop.find((t) => t.rank === "1"), "no NHS England top supplier");
  const coYears = puk.market.filter((m) => m.payer === "Cabinet Office" && m.period !== "all" && m.palantir_share_of_it !== "");
  const coBest = need([...coYears].sort((a, b) => Number(b.palantir_share_of_it) - Number(a.palantir_share_of_it))[0],
    "no Cabinet Office yearly market rows");

  /* Tax (Palantir's 2025 10-K) */
  const gt = puk.groupTax.filter((g) => g.year === "2025");
  const ukRevenue = need(gt.find((g) => g.jurisdiction === "United Kingdom" && g.measure === "revenue"), "no UK revenue");
  const ukUpper = need(gt.find((g) => g.jurisdiction === "United Kingdom" && g.measure === "cash_income_tax_upper_bound"),
    "no UK income tax upper bound");
  const taxTotal = need(gt.find((g) => g.measure === "cash_income_tax" && /^Total/.test(g.jurisdiction)), "no total income tax");
  const thresholdPct = Number(need(ukUpper.note.match(/(\d+)% or more/), "upper-bound note has no threshold")[1]);
  const countries = gt
    .filter((g) => g.measure === "cash_income_tax" && !/\(US\)|^All other|^Total/.test(g.jurisdiction))
    .sort((a, b) => b.amount - a.amount);
  need(countries.length > 0 && countries.every((g) => g.amount > ukUpper.amount),
    "a separately listed country now paid less income tax than the UK upper bound");

  /* People */
  const toPalantir = puk.revolving.filter((r) => r.direction === "gov-to-palantir");
  const people = [...new Set(toPalantir.map((r) => r.person))];
  const roles = people
    .map((person) => {
      const rows = toPalantir.filter((r) => r.person === person);
      const role = rows[0].former_role;
      const idx = ROLE_LABELS.findIndex((l) => l.match.test(role));
      const generic = `Former ${role.split(/;| \(/)[0].trim()}`;
      return {
        label: idx >= 0 ? ROLE_LABELS[idx].label : generic,
        reported: rows.every((r) => r.source_type === "press"),
        order: idx >= 0 ? idx : ROLE_LABELS.length,
      };
    })
    .sort((a, b) => a.order - b.order)
    .map(({ label, reported }) => ({ label, reported }));
  const influence = stripTags(need(puk.notes["influence-notes"], "no influence notes"));
  const mm = need(influence.match(/list (\d+) ministerial meetings or events with Palantir between (\w+) (\d{4}) and (\w+) (\d{4})/),
    "influence notes no longer give the ministerial meetings count");

  /* Quotes */
  const find = (who: string, text: string) =>
    need(puk.quotes.find((q) => q.who === who && q.quote.includes(text)), `no quote from ${who} containing "${text}"`);
  const buying = find("Louis Mosley", "Buying our way in");
  const regrettable = need(buying.context.match(/language was '([^']+)'/), "no Palantir response to the email")[1];
  const later = need(buying.context.match(/In (\w{3} \d{4}) Mosley called it '([^']+)'/), "no later Mosley response");
  const reporter = need(buying.context.match(/reported by (Bloomberg)/), "email no longer attributed to Bloomberg")[1];
  const reportedOn = need(buying.context.match(/first reported by Bloomberg on (\d+ \w+ \d{4})/), "no Bloomberg report date")[1];
  const via = need(buying.source_type.match(/\((Liberty Investigates)/), "no secondary source for the email")[1];
  const laterRow = need(
    puk.quotes.find((q) => q !== buying && q.who === "Louis Mosley" && /Buying our way in/.test(q.context) && q.context.toLowerCase().includes(later[2].toLowerCase())),
    "no source row for Mosley's later response",
  );
  const laterSource = need(laterRow.source_type.match(/\(([^;)]+?) video/), "later response source unreadable")[1];
  const sick = find("Peter Thiel", "NHS makes people sick");
  need(/Oxford Union/.test(sick.context), "NHS quote no longer from the Oxford Union");
  const democracy = find("Peter Thiel", "freedom and democracy are compatible");
  need(/Cato/.test(democracy.context), "democracy quote no longer from Cato Unbound");
  need(/co-founder and chairman/.test(sick.role), "Thiel's role changed");

  const genDate = `${Number(generatedIso.slice(8, 10))} ${monthYear(generatedIso)}`;

  return {
    generated: genDate,
    contracts: {
      total,
      count: C.length,
      firstYear: years[0],
      lastYear: years[years.length - 1],
      sources: [...new Set(C.map((c) => c.source))].sort(),
    },
    receipt: { lines: receiptLines, rest: { count: rest.length, value: restValue } },
    routes,
    direct: { value: direct.value, share: direct.share },
    recentDirect,
    paid: { total: paidTotal, bodies: paidBodies, modLast: monthYear(mod.last) },
    noNotice: { total: noNotice.reduce((s, r) => s + r.paid, 0), bodies: noNotice.length },
    lockin: {
      nesoQuote1,
      nesoQuote2,
      nesoDate: monthYear(neso.awarded),
      nesoValue: neso.value,
      nesoTitle: neso.title,
      nesoSource: neso.source,
      exitDate: monthYear(exit.awarded),
      exitValue: exit.value,
      exitPurpose,
      fdpDate: monthYear(fdp.awarded),
      fdpValue: fdp.value,
      monthsLaterWord: NUMBER_WORDS[months],
    },
    market: {
      nhsShare: Number(nhsRow.palantir_share_of_it),
      nhsWindow: itWindow,
      nhsRank: ordinal(nhsRank),
      nhsLeader: titleCase(nhsLeader.supplier),
      coShare: Number(coBest.palantir_share_of_it),
      coYear: coBest.period,
    },
    tax: {
      year: ukRevenue.year,
      ukRevenue: ukRevenue.amount,
      ukUpper: ukUpper.amount,
      total: taxTotal.amount,
      thresholdPct,
      countries: countries.map((g) => ({ name: g.jurisdiction, value: g.amount })),
    },
    people: {
      count: people.length,
      roles,
      meetings: { count: Number(mm[1]), from: mm[3], to: mm[5] },
    },
    quotes: {
      mosley: {
        text: tidyQuote(buying.quote),
        year: buying.date.slice(0, 4),
        reporter,
        regrettable,
        laterDate: later[1],
        later: later[2],
        reportedOn,
        via,
        laterSource,
      },
      thielSick: { text: tidyQuote(sick.quote), year: sick.date.slice(0, 4) },
      thielDemocracy: { text: tidyQuote(democracy.quote), year: democracy.date.slice(0, 4) },
    },
  };
}

export type Figures = ReturnType<typeof computeFigures>;
