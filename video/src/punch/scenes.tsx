import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { F, gbpM, gbpM0, usdM, usdM0, usdMCeil, pct0 } from "../data";
import { countUp } from "../components/anim";
import { Stamp } from "../components/parts";
import { Beat, BigStamp, MUTED, PAD, RED, Small, beatBounce, easeOut, slamIn, slideIn, snap } from "./kit";
import { T } from "./timeline";

type P = { duration: number };

/* ------------------------------------------------------------- 01 hook */

const SLIP_TOP = 70;
const ROW_TOP = 210;
const ROW_H = 66;
const AMT_TOP = 850;
const AMT_SIZE = 230;
const FOCUS_Y = SLIP_TOP + AMT_TOP + AMT_SIZE / 2;
const ZOOM_FROM = 1.5;

const receiptRows = [
  ...F.receipt.lines.map((l) => ({ label: l.short, value: l.value, nc: l.noCompetition })),
  { label: `${F.receipt.rest.count} more awards`, value: F.receipt.rest.value, nc: false },
];

export const Hook: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  const [z0, z1] = T.hook.zoom;
  const k = 1 - interpolate(frame, [z0, z1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  });
  const zoom = 1 + (ZOOM_FROM - 1) * k;
  const dy = (675 - FOCUS_Y) * k;
  const total = countUp(frame, T.hook.count[0], T.hook.count[1] - T.hook.count[0], F.contracts.total);
  const land = snap(frame, 0, 380);
  return (
    <Beat duration={duration} impacts={[T.hook.stamp]}>
      {/* the receipt, filmed tight on the total and then pulled back */}
      <AbsoluteFill style={{ transformOrigin: `540px ${FOCUS_Y}px`, transform: `translateY(${dy}px) scale(${zoom})` }}>
        <div
          style={{
            position: "absolute",
            left: 110,
            top: SLIP_TOP,
            width: 860,
            height: 1200,
            filter: "drop-shadow(0 18px 30px rgba(60,48,30,.28))",
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "#fcfaf4",
              WebkitMask:
                "conic-gradient(from -45deg at bottom, #0000, #000 1deg 89deg, #0000 90deg) bottom/26px 51% repeat-x," +
                "conic-gradient(from 135deg at top, #0000, #000 1deg 89deg, #0000 90deg) top/26px 51% repeat-x",
            }}
          >
            <div style={{ position: "absolute", top: 64, width: "100%", textAlign: "center", font: `800 62px/1 ${SANS}`, letterSpacing: "-.025em" }}>
              The UK's Palantir bill
            </div>
            <div style={{ position: "absolute", top: 160, left: 60, right: 60, borderTop: `3px dashed ${COLOR.rule}` }} />
            {receiptRows.map((r, i) => (
              <div
                key={r.label}
                style={{
                  position: "absolute",
                  top: ROW_TOP + i * ROW_H,
                  left: 60,
                  right: 60,
                  display: "flex",
                  alignItems: "center",
                  font: `500 40px/1 ${MONO}`,
                  color: i === receiptRows.length - 1 ? MUTED : COLOR.ink,
                }}
              >
                <span>{r.label}</span>
                {r.nc && <Stamp at={-100} size={18} rotate={-4} style={{ marginLeft: 22 }} />}
                <span style={{ marginLeft: "auto", fontWeight: 700 }}>{gbpM0(r.value)}</span>
              </div>
            ))}
            <div style={{ position: "absolute", top: ROW_TOP + receiptRows.length * ROW_H + 12, left: 60, right: 60, borderTop: `3px dashed ${COLOR.rule}` }} />
            <div style={{ position: "absolute", top: AMT_TOP - 58, left: 60, font: `800 40px/1 ${MONO}`, letterSpacing: ".1em" }}>TOTAL</div>
            <div
              style={{
                position: "absolute",
                top: AMT_TOP,
                width: "100%",
                textAlign: "center",
                font: `900 ${AMT_SIZE}px/1 ${SANS}`,
                letterSpacing: "-.045em",
                fontVariantNumeric: "tabular-nums",
                transformOrigin: "50% 100%",
                transform: `scale(${interpolate(land, [0, 1], [1.2, 1]) * beatBounce(frame, 0.012)})`,
              }}
            >
              {gbpM0(total)}
            </div>
            <div
              style={{
                position: "absolute",
                top: AMT_TOP + AMT_SIZE + 6,
                width: "100%",
                textAlign: "center",
                font: `500 34px/1 ${SANS}`,
                color: MUTED,
                opacity: easeOut(frame, T.hook.count[1], 6),
              }}
            >
              {F.contracts.count} UK public contracts, {F.contracts.firstYear}–{F.contracts.lastYear}
            </div>
          </div>
        </div>
      </AbsoluteFill>
      <BigStamp
        at={T.hook.stamp}
        lines={[
          { text: pct0(F.direct.share), size: 230 },
          { text: "NO COMPETITION", size: 70 },
        ]}
        style={{ left: 150, top: 330, width: 780 }}
      />
    </Beat>
  );
};

/* ---------------------------------------------------------- 02 revenue */

export const Revenue: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  const [a, b] = T.revenue.count;
  return (
    <Beat duration={duration}>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 330 }}>
        <div style={{ ...slideIn(frame, 0, 260, 0) }}>
          <div
            style={{
              font: `900 288px/0.9 ${SANS}`,
              letterSpacing: "-.05em",
              fontVariantNumeric: "tabular-nums",
              transformOrigin: "0% 50%",
              transform: `scale(${beatBounce(frame)})`,
            }}
          >
            {usdM0(countUp(frame, a, b - a, F.tax.ukRevenue))}
          </div>
        </div>
        <div style={{ font: `800 136px/1 ${SANS}`, letterSpacing: "-.035em", marginTop: 44, ...slideIn(frame, 7, 0, 90) }}>
          from UK
          <br />
          customers
        </div>
      </div>
      <Small style={{ position: "absolute", left: PAD, bottom: 70, ...slideIn(frame, 14, 0, 30) }}>
        Palantir's {F.tax.year} revenue by customer location · its 10-K
      </Small>
    </Beat>
  );
};

/* -------------------------------------------------------------- 03 tax */

const TaxBar: React.FC<{ name: string; value: number; label: string; at: number; max: number; uk?: boolean }> = ({ name, value, label, at, max, uk }) => {
  const frame = useCurrentFrame();
  const p = easeOut(frame, at, 12);
  const color = uk ? RED : COLOR.ink;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", alignItems: "center", height: 104, opacity: frame < at ? 0 : 1 }}>
      <div style={{ font: `800 64px/1 ${SANS}`, color, letterSpacing: "-.02em", whiteSpace: "nowrap" }}>{name}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
        <div
          style={{
            width: Math.max(8, (value / max) * 330 * p),
            height: 70,
            background: uk ? `repeating-linear-gradient(-45deg, ${RED} 0 9px, transparent 9px 17px)` : COLOR.grey1,
            border: uk ? `4px solid ${RED}` : undefined,
            boxSizing: "border-box",
          }}
        />
        <div style={{ font: `800 60px/1 ${SANS}`, color, whiteSpace: "nowrap", opacity: easeOut(frame, at + 6, 6) }}>{label}</div>
      </div>
    </div>
  );
};

export const Tax: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  const t = F.tax;
  const low = F.punch.lowestCountry;
  const max = Math.max(low.value, t.ukUpper);
  return (
    <Beat duration={duration} impacts={[T.tax.slam]}>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 110 }}>
        <div style={{ font: `800 110px/1 ${SANS}`, letterSpacing: "-.03em", ...slideIn(frame, 0, -240, 0) }}>UK income tax</div>
        <div style={{ color: RED, marginTop: 34, transformOrigin: "0% 50%", ...slamIn(frame, T.tax.slam) }}>
          <div style={{ font: `800 120px/1 ${SANS}`, letterSpacing: "-.03em" }}>under</div>
          <div style={{ font: `900 310px/0.9 ${SANS}`, letterSpacing: "-.05em", transformOrigin: "0% 50%", transform: `scale(${beatBounce(frame)})` }}>
            {usdMCeil(t.ukUpper)}
          </div>
        </div>
      </div>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 860 }}>
        <TaxBar name={low.name} value={low.value} label={usdM(low.value)} at={T.tax.bars[0]} max={max} />
        <TaxBar name="UK" value={t.ukUpper} label={`under ${usdMCeil(t.ukUpper)}`} at={T.tax.bars[1]} max={max} uk />
      </div>
      <Small style={{ position: "absolute", left: PAD, right: PAD, bottom: 64, ...slideIn(frame, T.tax.bars[1], 0, 30) }}>
        Cash income tax paid, {t.year}, from Palantir's 10-K. The UK isn't listed separately: under {usdMCeil(t.ukUpper)} is an upper bound.
      </Small>
    </Beat>
  );
};

/* ------------------------------------------------------------ 04 cents */

export const Cents: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  const c = F.punch.centsPer100;
  const bar = easeOut(frame, T.cents.sliver, 10);
  return (
    <Beat duration={duration} impacts={[T.cents.slam]}>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 120 }}>
        <div style={{ font: `800 100px/1 ${SANS}`, letterSpacing: "-.03em", ...slideIn(frame, 0, -200, 0) }}>UK income tax:</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 30, color: RED, marginTop: 20, transformOrigin: "0% 60%", ...slamIn(frame, T.cents.slam, 1.9) }}>
          <span style={{ font: `800 120px/1 ${SANS}`, letterSpacing: "-.03em" }}>under</span>
          <span style={{ font: `900 330px/0.92 ${SANS}`, letterSpacing: "-.06em", display: "inline-block", transformOrigin: "0% 60%", transform: `scale(${beatBounce(frame)})` }}>
            {c}¢
          </span>
        </div>
        <div style={{ font: `800 116px/1 ${SANS}`, letterSpacing: "-.035em", marginTop: 6, ...slideIn(frame, 12, 0, 80) }}>in every $100</div>
      </div>
      {/* $100 of revenue as a bar; the income tax is the red sliver at its left end */}
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 900, opacity: frame < T.cents.sliver ? 0 : 1 }}>
        <div style={{ position: "relative", height: 76, width: `${bar * 100}%`, background: COLOR.grey4 }}>
          <div style={{ position: "absolute", left: 0, top: -14, bottom: -14, width: Math.max(5, (c / 10000) * 920), background: RED }} />
        </div>
        <Small style={{ marginTop: 22, opacity: easeOut(frame, T.cents.sliver + 6, 8) }}>
          $100 of UK revenue, {F.tax.year}. Red: the most it paid in UK income tax.
        </Small>
      </div>
    </Beat>
  );
};

/* ----------------------------------------------------------- 05 buying */

export const Buying: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  const Q = F.quotes.mosley;
  const words = Q.text.split(" ");
  const [w0, w1, w2, w3] = T.buying.words;
  const at = [w0, w1, w2, w3];
  const word = (i: number) => (
    <span key={i} style={{ display: "inline-block", marginRight: "0.22em", transformOrigin: "50% 70%", ...slamIn(frame, at[Math.min(i, at.length - 1)], 1.8) }}>
      {i === 0 ? "“" : ""}
      {words[i]}
      {i === words.length - 1 ? "”" : ""}
    </span>
  );
  return (
    <Beat duration={duration} impacts={[at[at.length - 1]]}>
      <div
        style={{
          position: "absolute",
          right: PAD,
          top: 76,
          border: `5px solid ${COLOR.ink}`,
          padding: "14px 24px 12px",
          font: `700 44px/1.1 ${SANS}`,
          ...slideIn(frame, T.buying.response, 260, 0),
        }}
      >
        Palantir: “{Q.regrettable}”
      </div>
      <div style={{ position: "absolute", left: PAD, right: PAD - 20, top: 330, font: `900 156px/1.02 ${SANS}`, letterSpacing: "-.045em" }}>
        {words.slice(0, 2).map((_, i) => word(i))}
        <br />
        {words.slice(2).map((_, i) => word(i + 2))}
      </div>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 720, ...slideIn(frame, T.buying.who, 0, 40) }}>
        <div style={{ font: `800 56px/1.15 ${SANS}` }}>Louis Mosley, Palantir UK</div>
        <div style={{ font: `500 44px/1.3 ${SANS}`, color: MUTED, marginTop: 8 }}>
          {Q.year} internal email about the NHS ({Q.reporter})
        </div>
      </div>
    </Beat>
  );
};

/* ------------------------------------------------------------- 06 NESO */

const nesoText = `“${F.lockin.nesoQuote1}”`;

export const Neso: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  const [a, b] = T.neso.type;
  const n = Math.round(interpolate(frame, [a, b], [0, nesoText.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  return (
    <Beat duration={duration} impacts={[T.neso.stamp]}>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 110, font: `800 54px/1.2 ${SANS}`, ...slideIn(frame, 0, -200, 0) }}>
        NESO, the grid operator, on why its Palantir contract had no competition:
      </div>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 330, font: `900 118px/1.02 ${SANS}`, letterSpacing: "-.04em" }}>
        <span>{nesoText.slice(0, n)}</span>
        <span style={{ color: "transparent" }}>{nesoText.slice(n)}</span>
      </div>
      <BigStamp at={T.neso.stamp} lines={[{ text: "NO COMPETITION", size: 64 }]} rotate={-5} style={{ left: PAD, top: 1040 }} />
      <Small style={{ position: "absolute", left: PAD, top: 1200, ...slideIn(frame, T.neso.stamp + 4, 0, 30) }}>
        Direct award, {F.lockin.nesoDate}
      </Small>
    </Beat>
  );
};

/* -------------------------------------------------------------- 07 NHS */

export const Nhs: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  const [a, b] = T.nhs.count;
  const swap = snap(frame, T.nhs.swap, 240);
  return (
    <Beat duration={duration} impacts={[T.nhs.swap]}>
      <div
        style={{
          position: "absolute",
          left: PAD,
          right: PAD,
          top: interpolate(swap, [0, 1], [220, 80]),
          transformOrigin: "0% 0%",
          transform: `scale(${interpolate(swap, [0, 1], [1, 0.5])})`,
        }}
      >
        <div style={{ font: `800 110px/1 ${SANS}`, letterSpacing: "-.03em", ...slideIn(frame, 0, -200, 0) }}>NHS England:</div>
        <div style={{ font: `900 276px/0.92 ${SANS}`, letterSpacing: "-.05em", fontVariantNumeric: "tabular-nums", marginTop: 16, ...slideIn(frame, 0, 260, 0) }}>
          {gbpM(countUp(frame, a, b - a, F.lockin.exitValue))}
        </div>
        <div style={{ font: `800 116px/1 ${SANS}`, letterSpacing: "-.035em", marginTop: 26, ...slideIn(frame, 8, 0, 80) }}>to exit Palantir</div>
      </div>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 470, ...slideIn(frame, T.nhs.swap, 0, 260) }}>
        <div style={{ font: `800 110px/1 ${MONO}`, color: MUTED }}>↓</div>
        <div style={{ font: `900 136px/1.0 ${SANS}`, letterSpacing: "-.045em", marginTop: 14 }}>
          Palantir
          <br />
          won the
          <br />
          replacement.
        </div>
      </div>
      <Small style={{ position: "absolute", left: PAD, right: PAD, bottom: 64, ...slideIn(frame, T.nhs.swap + 10, 0, 30) }}>
        “Transition & Exit” contract, {F.lockin.exitDate}. Federated Data Platform to a Palantir-led consortium, {F.lockin.fdpDate}.
      </Small>
    </Beat>
  );
};

/* ----------------------------------------------------------- 08 people */

export const People: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  const [a, b] = T.people.count;
  const n = Math.round(interpolate(frame, [a, b], [0, F.people.count], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const role = F.punch.leadRole.replace(/^Former /, "former ");
  return (
    <Beat duration={duration}>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 110 }}>
        <div
          style={{
            font: `900 480px/0.86 ${SANS}`,
            letterSpacing: "-.06em",
            fontVariantNumeric: "tabular-nums",
            transformOrigin: "0% 60%",
            ...slamIn(frame, 0, 1.4),
          }}
        >
          <span style={{ display: "inline-block", transform: `scale(${beatBounce(frame)})`, transformOrigin: "0% 60%" }}>{n}</span>
        </div>
        <div style={{ font: `800 112px/1.02 ${SANS}`, letterSpacing: "-.035em", marginTop: 30, ...slideIn(frame, 8, 0, 90) }}>
          people from UK
          <br />
          public roles
        </div>
        <div style={{ font: `900 128px/1 ${SANS}`, letterSpacing: "-.04em", marginTop: 24, ...slideIn(frame, 17, -260, 0) }}>→ Palantir</div>
      </div>
      <Small style={{ position: "absolute", left: PAD, right: PAD, bottom: 64, font: `600 40px/1.3 ${SANS}`, ...slideIn(frame, 26, 0, 30) }}>
        including a {role}
      </Small>
    </Beat>
  );
};

/* ---------------------------------------------------------- 09 closing */

export const Closing: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  const l2 = T.closing.line2;
  return (
    <Beat duration={duration} dark impacts={[l2]}>
      <div
        style={{
          position: "absolute",
          left: PAD,
          right: PAD,
          top: 250,
          font: `800 104px/1.04 ${SANS}`,
          letterSpacing: "-.035em",
          color: "#d9d3c4",
          opacity: frame >= l2 ? 0.62 : 1,
          ...slideIn(frame, 2, 0, 90),
        }}
      >
        Sovereignty
        <br />
        isn't where the
        <br />
        servers sit.
      </div>
      <div
        style={{
          position: "absolute",
          left: PAD,
          right: PAD,
          top: 740,
          font: `900 120px/1.02 ${SANS}`,
          letterSpacing: "-.045em",
          transformOrigin: "0% 50%",
          ...slamIn(frame, l2, 1.5),
        }}
      >
        It's whether
        <br />
        you can leave.
      </div>
    </Beat>
  );
};

/* -------------------------------------------------------------- 10 end */

export const End: React.FC<P> = ({ duration }) => {
  const frame = useCurrentFrame();
  return (
    <Beat duration={duration}>
      <div style={{ position: "absolute", left: PAD, right: PAD, top: 330 }}>
        <div style={{ font: `800 60px/1.1 ${SANS}`, color: MUTED, ...slideIn(frame, 0, 0, 40) }}>The UK's Palantir bill</div>
        <div style={{ font: `900 84px/1.08 ${SANS}`, letterSpacing: "-.035em", marginTop: 28, ...slideIn(frame, 3, 0, 80) }}>
          jhammant.github.io/
          <br />
          palantir-uk-deep-dive
        </div>
        <div style={{ height: 6, background: COLOR.ink, marginTop: 46, width: `${easeOut(frame, 8, 14) * 100}%` }} />
        <div style={{ font: `700 54px/1.2 ${SANS}`, marginTop: 40, ...slideIn(frame, 12, 0, 40) }}>Every figure links to its public source.</div>
      </div>
      <Small style={{ position: "absolute", left: PAD, right: PAD, bottom: 80, font: `600 40px/1.3 ${SANS}`, ...slideIn(frame, 18, 0, 30) }}>
        Compiled by Jon Hammant (Orbital)
      </Small>
    </Beat>
  );
};
