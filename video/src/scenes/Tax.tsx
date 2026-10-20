import React from "react";
import { useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { Slip } from "../components/Slip";
import { Big, Eyebrow, Source } from "../components/parts";
import { countUp, ease, rise } from "../components/anim";
import { F, usdM, usdMCeil } from "../data";

const BARS_AT = 56;
const STEP = 8;
const BAR_MAX = 400;
const t = F.tax;
const maxValue = Math.max(...t.countries.map((c) => c.value));
const UK_AT = BARS_AT + t.countries.length * STEP + 10;

const Bar: React.FC<{ name: string; value: number; label: string; at: number; uk?: boolean }> = ({ name, value, label, at, uk }) => {
  const frame = useCurrentFrame();
  const p = ease(frame, at, 18);
  const w = Math.max(6, (value / maxValue) * BAR_MAX * p);
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "268px 1fr",
        alignItems: "center",
        columnGap: 18,
        height: 64,
        opacity: ease(frame, at, 6),
      }}
    >
      <div style={{ font: `${uk ? 800 : 500} 31px/1.1 ${SANS}`, whiteSpace: "nowrap", color: uk ? COLOR.red : COLOR.ink }}>{name}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <div
          style={{
            width: w,
            height: 42,
            borderRadius: 3,
            background: uk
              ? `repeating-linear-gradient(-45deg, ${COLOR.red} 0 7px, transparent 7px 13px)`
              : COLOR.grey1,
            border: uk ? `3px solid ${COLOR.red}` : undefined,
            boxSizing: "border-box",
          }}
        />
        <div
          style={{
            font: `800 ${uk ? 36 : 31}px/1 ${MONO}`,
            color: uk ? COLOR.red : COLOR.ink,
            whiteSpace: "nowrap",
            opacity: ease(frame, at + 10, 8),
          }}
        >
          {label}
        </div>
      </div>
    </div>
  );
};

// Beat 7. UK revenue against income tax paid, from Palantir's own 10-K.
export const Tax: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  return (
    <Slip duration={duration} height={1210}>
      <Eyebrow>Income tax · Palantir's own {t.year} 10-K</Eyebrow>
      <Big size={190} style={{ marginTop: 40, ...rise(frame, 8, 20, 10) }}>
        {usdM(countUp(frame, 10, 30, t.ukRevenue))}
      </Big>
      <div style={{ font: `500 40px/1.25 ${SANS}`, marginTop: 20, ...rise(frame, 24) }}>revenue from UK customers in {t.year}</div>

      <div style={{ borderTop: `3px solid ${COLOR.ink}`, marginTop: 50, paddingTop: 26, opacity: ease(frame, BARS_AT - 10, 8) }}>
        <div style={{ font: `800 38px/1.2 ${SANS}`, marginBottom: 18, ...rise(frame, BARS_AT - 8) }}>Cash income tax paid in {t.year}</div>
        {t.countries.map((c, i) => (
          <Bar key={c.name} name={c.name} value={c.value} label={usdM(c.value)} at={BARS_AT + i * STEP} />
        ))}
        <Bar name="United Kingdom" value={t.ukUpper} label={`under ${usdMCeil(t.ukUpper)}`} at={UK_AT} uk />
      </div>
      <div style={{ font: `400 27px/1.4 ${MONO}`, color: COLOR.muted, marginTop: 26, ...rise(frame, UK_AT + 14) }}>
        The UK isn't listed separately, so it paid under {t.thresholdPct}% of the {usdM(t.total)} total: an upper bound.
      </div>
      <Source start={30}>Source: Palantir Technologies Inc. annual report (10-K) for {t.year}, SEC</Source>
    </Slip>
  );
};
