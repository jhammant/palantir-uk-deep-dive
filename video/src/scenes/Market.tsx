import React from "react";
import { useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { Slip } from "../components/Slip";
import { Donut } from "../components/Donut";
import { Eyebrow, Source } from "../components/parts";
import { ease, rise } from "../components/anim";
import { F, pct1 } from "../data";

const CO_AT = 76;

// Beat 6. Palantir's share of NHS England's IT, software and data spending.
export const Market: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const m = F.market;
  return (
    <Slip duration={duration} height={1210}>
      <Eyebrow>Market share</Eyebrow>
      <div style={{ font: `800 76px/1 ${SANS}`, letterSpacing: "-.03em", marginTop: 22 }}>NHS England</div>
      <div style={{ font: `400 31px/1.3 ${SANS}`, color: COLOR.muted, marginTop: 12 }}>
        IT, software and data spending, {m.nhsWindow}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 46, marginTop: 40 }}>
        <Donut
          size={380}
          thickness={78}
          progress={ease(frame, 10, 30)}
          segments={[
            { value: m.nhsShare, color: COLOR.red },
            { value: 1 - m.nhsShare, color: COLOR.grey4 },
          ]}
        >
          <div style={rise(frame, 30, 12, 10)}>
            <div style={{ font: `800 72px/0.95 ${SANS}`, letterSpacing: "-.04em" }}>{pct1(m.nhsShare)}</div>
            <div style={{ font: `700 22px/1.3 ${MONO}`, letterSpacing: ".1em", color: COLOR.muted, marginTop: 8 }}>TO PALANTIR</div>
          </div>
        </Donut>
        <div style={{ flex: 1, ...rise(frame, 40, 18, 12) }}>
          <div style={{ font: `500 32px/1.2 ${SANS}` }}>Palantir was its</div>
          <div style={{ font: `800 70px/1 ${SANS}`, letterSpacing: "-.035em", margin: "10px 0 12px", whiteSpace: "nowrap" }}>{m.nhsRank}-largest</div>
          <div style={{ font: `500 32px/1.25 ${SANS}` }}>IT supplier, after {m.nhsLeader}</div>
        </div>
      </div>
      <div style={{ font: `400 27px/1.4 ${MONO}`, color: COLOR.muted, marginTop: 30, ...rise(frame, 52) }}>
        {m.nhsWindow} are the only months whose files separate IT spending.
      </div>

      <div
        style={{
          borderTop: `3px solid ${COLOR.ink}`,
          marginTop: 34,
          paddingTop: 26,
          display: "flex",
          alignItems: "center",
          gap: 30,
          ...rise(frame, CO_AT, 16),
        }}
      >
        <div style={{ font: `800 100px/1 ${SANS}`, letterSpacing: "-.04em", flex: "none" }}>{pct1(m.coShare)}</div>
        <div style={{ font: `500 33px/1.25 ${SANS}` }}>of the Cabinet Office's IT spending went to Palantir in {m.coYear}</div>
      </div>
      <Source start={30}>Source: the bodies' own published spending files, every supplier counted</Source>
    </Slip>
  );
};
