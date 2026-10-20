import React from "react";
import { useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { Slip } from "../components/Slip";
import { Donut } from "../components/Donut";
import { Eyebrow, Source, Stamp } from "../components/parts";
import { ease, rise } from "../components/anim";
import { F, gbpM, pct0 } from "../data";

const GREYS = [COLOR.grey1, COLOR.grey2, COLOR.grey3, COLOR.grey4];
const routes = (() => {
  let g = 0;
  return F.routes.map((r) => ({ ...r, color: r.isDirect ? COLOR.red : GREYS[Math.min(g++, GREYS.length - 1)] }));
})();

const RECENT_AT = 70;

// Beat 3. How the total was awarded: the direct-award slice in red.
export const Awarded: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const sweep = ease(frame, 10, 34);
  return (
    <Slip duration={duration} height={1210}>
      <Eyebrow>How it was awarded</Eyebrow>
      <div style={{ font: `800 62px/1.05 ${SANS}`, letterSpacing: "-.025em", margin: "16px 0 34px" }}>
        How the {gbpM(F.contracts.total)} was awarded
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 44 }}>
        <Donut size={430} thickness={74} progress={sweep} segments={routes.map((r) => ({ value: r.value, color: r.color }))}>
          <div style={{ ...rise(frame, 38, 14, 10) }}>
            <div style={{ font: `800 104px/0.9 ${SANS}`, letterSpacing: "-.04em", color: COLOR.red }}>{pct0(F.direct.share)}</div>
            <div style={{ font: `800 21px/1.25 ${MONO}`, letterSpacing: ".12em", color: COLOR.red, marginTop: 10 }}>
              NO
              <br />
              COMPETITION
            </div>
          </div>
        </Donut>
        <div style={{ display: "grid", gap: 16, flex: 1 }}>
          {routes.map((r, i) => (
            <div key={r.route} style={{ display: "grid", gridTemplateColumns: "22px 1fr", columnGap: 14, ...rise(frame, 22 + i * 5, 12, 10) }}>
              <span style={{ width: 22, height: 22, borderRadius: 4, background: r.color, marginTop: 7 }} />
              <div>
                <div style={{ font: `${r.isDirect ? 800 : 500} 30px/1.15 ${SANS}`, color: r.isDirect ? COLOR.red : COLOR.ink }}>
                  {r.isDirect ? "Direct award" : r.route}
                </div>
                <div style={{ font: `700 25px/1.3 ${MONO}`, color: r.isDirect ? COLOR.red : COLOR.muted }}>
                  {gbpM(r.value)} · {pct0(r.share)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 46, borderTop: `3px solid ${COLOR.ink}`, paddingTop: 22, ...rise(frame, RECENT_AT, 16, 12) }}>
        <div style={{ font: `800 38px/1.2 ${SANS}`, letterSpacing: "-.01em" }}>
          The two biggest awards of the past 12 months were both direct awards
        </div>
        {F.recentDirect.map((r, i) => (
          <div
            key={r.buyer}
            style={{
              display: "grid",
              gridTemplateColumns: "1fr auto auto",
              alignItems: "center",
              columnGap: 22,
              marginTop: i === 0 ? 20 : 10,
              font: `400 33px/1.3 ${MONO}`,
              opacity: ease(frame, RECENT_AT + 8 + i * 10, 8),
            }}
          >
            <span>
              {r.buyer} · {r.date}
            </span>
            <Stamp at={RECENT_AT + 14 + i * 10} size={20} />
            <span style={{ fontWeight: 700, minWidth: 170, textAlign: "right" }}>{gbpM(r.value)}</span>
          </div>
        ))}
      </div>
      <Source start={RECENT_AT}>
        Route as stated in each notice. Sources: {F.contracts.sources.join(" and ")}
      </Source>
    </Slip>
  );
};
