import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { Slip } from "../components/Slip";
import { Eyebrow, Rule, Stamp } from "../components/parts";
import { countUp, ease, rise } from "../components/anim";
import { F, gbpM } from "../data";

const FIRST = 20; // first line prints
const GAP = 17; // frames between lines
const STAMP_DELAY = 12;

const lines = [
  ...F.receipt.lines.map((l) => ({ ...l, small: false })),
  { label: `${F.receipt.rest.count} smaller awards`, value: F.receipt.rest.value, noCompetition: false, small: true },
];
export const RECEIPT_TOTAL_AT = FIRST + lines.length * GAP + 8;
const TOTAL_COUNT = 28;
const stampTimes = lines.flatMap((l, i) => (l.noCompetition ? [FIRST + i * GAP + STAMP_DELAY] : []));

const Line: React.FC<{ label: string; value: number; at: number; noCompetition: boolean; small: boolean }> = ({
  label,
  value,
  at,
  noCompetition,
  small,
}) => {
  const frame = useCurrentFrame();
  if (frame < at) return null;
  const chars = Math.min(label.length, Math.ceil((frame - at) * 3.2));
  const amount = countUp(frame, at + 2, 16, value);
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr auto",
        columnGap: 24,
        alignItems: "baseline",
        padding: "9px 0",
        font: `400 33px/1.28 ${MONO}`,
        color: small ? COLOR.muted : COLOR.ink,
        ...rise(frame, at, 10, 6),
      }}
    >
      <div>
        <span>{label.slice(0, chars)}</span>
        <span style={{ color: "transparent" }}>{label.slice(chars)}</span>
        {noCompetition && (
          <div style={{ marginTop: 18, height: 46 }}>
            <Stamp at={at + STAMP_DELAY} size={24} origin="0% 50%" rotate={-3} />
          </div>
        )}
      </div>
      <div style={{ fontWeight: 700, fontVariantNumeric: "tabular-nums", textAlign: "right" }}>{gbpM(amount)}</div>
    </div>
  );
};

// Beats 2 and 3a. The receipt prints line by line; NO COMPETITION stamps slam
// onto the direct awards; the total counts up.
export const Receipt: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  // A small jolt each time a stamp lands.
  const jolt = stampTimes.reduce((s, t) => {
    const d = frame - t - 3;
    return d >= 0 && d < 8 ? s + Math.sin(d * 2.4) * (8 - d) * 0.9 : s;
  }, 0);
  const totalShown = frame >= RECEIPT_TOTAL_AT;
  return (
    <AbsoluteFill style={{ transform: `translate(${jolt * 0.4}px, ${jolt}px)` }}>
      <Slip duration={duration} fit top={92} padTop={56} style={{ paddingBottom: 46 }}>
        <div style={{ textAlign: "center" }}>
          <Eyebrow>UK public sector → Palantir</Eyebrow>
          <div style={{ font: `800 66px/1.02 ${SANS}`, letterSpacing: "-.025em", margin: "12px 0 8px" }}>The UK's Palantir bill</div>
          <div style={{ font: `400 26px/1.3 ${MONO}`, color: COLOR.muted }}>
            Published contract awards, {F.contracts.firstYear}–{F.contracts.lastYear}
          </div>
        </div>
        <Rule start={4} style={{ margin: "22px 0 10px" }} />
        {lines.map((l, i) => (
          <Line key={l.label} {...l} at={FIRST + i * GAP} />
        ))}
        {totalShown && (
          <>
            <Rule start={RECEIPT_TOTAL_AT} style={{ margin: "12px 0 12px" }} />
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "baseline",
                font: `800 44px/1 ${MONO}`,
                ...rise(frame, RECEIPT_TOTAL_AT, 12, 8),
              }}
            >
              <span>TOTAL</span>
              <span style={{ fontSize: 76, letterSpacing: "-.02em", fontVariantNumeric: "tabular-nums" }}>
                {gbpM(countUp(frame, RECEIPT_TOTAL_AT + 2, TOTAL_COUNT, F.contracts.total))}
              </span>
            </div>
            <div
              style={{
                marginTop: 12,
                textAlign: "right",
                font: `400 25px/1.3 ${MONO}`,
                color: COLOR.muted,
                opacity: ease(frame, RECEIPT_TOTAL_AT + TOTAL_COUNT, 10),
              }}
            >
              {F.contracts.count} awards · values as published
              <br />
              Sources: {F.contracts.sources.join(" and ")}
            </div>
          </>
        )}
      </Slip>
    </AbsoluteFill>
  );
};
