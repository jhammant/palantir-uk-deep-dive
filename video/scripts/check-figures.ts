// Recomputes every on-screen figure from ../site/assets/bundle.js and checks it
// against the figures in the brief. Run: npm run check
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { computeFigures, gbpM, usdM, usdMCeil, pct0, pct1, type Puk } from "../src/data/figures";

const require = createRequire(import.meta.url);
const { parsePukBundle } = require("./puk-bundle-loader.cjs");

const bundlePath = path.resolve(process.cwd(), "../site/assets/bundle.js");
const puk = parsePukBundle(fs.readFileSync(bundlePath, "utf8")) as Puk;
const F = computeFigures(puk);

const L = F.receipt.lines;
const expected: [string, string, string][] = [
  ["Total awarded", gbpM(F.contracts.total), "£647.1m"],
  ["Awards", String(F.contracts.count), "30"],
  ["Years", `${F.contracts.firstYear}–${F.contracts.lastYear}`, "2015–2026"],
  ["Direct award value", gbpM(F.direct.value), "£261.8m"],
  ["Direct award share", pct0(F.direct.share), "40%"],
  ["Recent direct 1", `${F.recentDirect[0].buyer} ${gbpM(F.recentDirect[0].value)} (${F.recentDirect[0].date})`, "MoD £240.6m (Dec 2025)"],
  ["Recent direct 2", `${F.recentDirect[1].buyer} ${gbpM(F.recentDirect[1].value)} (${F.recentDirect[1].date})`, "NESO £21.2m (Aug 2026)"],
  ["Receipt 1", `${L[0].label} ${gbpM(L[0].value)}${L[0].noCompetition ? " NC" : ""}`, "MoD enterprise agreement, 2025 £240.6m NC"],
  ["Receipt 2", `${L[1].label} ${gbpM(L[1].value)}${L[1].noCompetition ? " NC" : ""}`, "NHS Federated Data Platform, 2023 £182.2m"],
  ["Receipt 3", `${L[2].label} ${gbpM(L[2].value)}${L[2].noCompetition ? " NC" : ""}`, "MoD enterprise agreement, 2022 £75.2m"],
  ["Receipt 4", `${L[3].label} ${gbpM(L[3].value)}${L[3].noCompetition ? " NC" : ""}`, "Crown Commercial Service, 2020 £26.2m"],
  ["Receipt 5", `${L[4].label} ${gbpM(L[4].value)}${L[4].noCompetition ? " NC" : ""}`, "NHS “Transition & Exit” from Palantir, 2023 £24.9m"],
  ["Receipt 6", `${L[5].label} ${gbpM(L[5].value)}${L[5].noCompetition ? " NC" : ""}`, "NHS Covid data platform, 2020 £23.5m"],
  ["Receipt 7", `${L[6].label} ${gbpM(L[6].value)}${L[6].noCompetition ? " NC" : ""}`, "NESO, the grid operator, 2026 £21.2m NC"],
  ["Paid", gbpM(F.paid.total), "£278.6m"],
  ["Paid, no notice found", gbpM(F.noNotice.total), "£5.9m"],
  ["NHS exit contract", `${gbpM(F.lockin.exitValue)} ${F.lockin.exitDate}`, "£24.9m Jun 2023"],
  ["FDP award", `${F.lockin.fdpDate} (${F.lockin.monthsLaterWord} months later)`, "Nov 2023 (Five months later)"],
  ["NHS England share of IT", `${pct1(F.market.nhsShare)} ${F.market.nhsWindow} ${F.market.nhsRank}`, "10.6% Apr–Sep 2025 2nd"],
  ["Cabinet Office share of IT", `${pct1(F.market.coShare)} ${F.market.coYear}`, "10.0% 2021"],
  ["UK revenue", usdM(F.tax.ukRevenue), "$427.4m"],
  ["UK income tax upper bound", usdMCeil(F.tax.ukUpper), "$1.1m"],
  ["Income tax by country", F.tax.countries.map((c) => `${c.name} ${usdM(c.value)}`).join(", "),
    "South Korea $5.8m, Japan $4.8m, France $2.8m, Germany $1.7m"],
  ["People to Palantir", String(F.people.count), "14"],
  ["Ministerial meetings", String(F.people.meetings.count), "37"],
  ["Mosley quote", F.quotes.mosley.text, "Buying our way in…!"],
  ["Mosley email year", F.quotes.mosley.year, "2021"],
  ["Palantir response", F.quotes.mosley.regrettable, "regrettable"],
  ["Thiel NHS", `${F.quotes.thielSick.text} ${F.quotes.thielSick.year}`, "The NHS makes people sick. 2023"],
  ["Thiel democracy", `${F.quotes.thielDemocracy.text} ${F.quotes.thielDemocracy.year}`,
    "I no longer believe that freedom and democracy are compatible. 2009"],
];

let failed = 0;
for (const [what, got, want] of expected) {
  const ok = got === want;
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"}  ${what.padEnd(28)} ${got}${ok ? "" : `   (brief: ${want})`}`);
}
console.log(`\nRoles (${F.people.roles.length}):`);
for (const r of F.people.roles) console.log(`      ${r.label}${r.reported ? " (reported)" : ""}`);
console.log(`\nRoutes: ${F.routes.map((r) => `${r.route} ${gbpM(r.value)} ${pct0(r.share)}`).join(" · ")}`);
console.log(`Receipt rest: ${F.receipt.rest.count} awards ${gbpM(F.receipt.rest.value)}`);
console.log(`Paid bodies: ${F.paid.bodies}; MoD last: ${F.paid.modLast}; no-notice bodies: ${F.noNotice.bodies}`);
console.log(`Tax total ${usdM(F.tax.total)}, threshold ${F.tax.thresholdPct}%; NHS leader: ${F.market.nhsLeader}`);
console.log(`Meetings window: ${F.people.meetings.from}–${F.people.meetings.to}; Mosley later (${F.quotes.mosley.laterDate}): "${F.quotes.mosley.later}"`);
console.log(`Data generated: ${F.generated}`);
console.log(`Mosley sources: ${F.quotes.mosley.reporter} ${F.quotes.mosley.reportedOn} via ${F.quotes.mosley.via}; ${F.quotes.mosley.laterSource} ${F.quotes.mosley.laterDate}`);
if (failed) {
  console.error(`\n${failed} figure(s) differ from the brief. The video shows the bundle's values; check the wording still fits.`);
  process.exit(1);
}
console.log("\nAll figures match the brief.");
