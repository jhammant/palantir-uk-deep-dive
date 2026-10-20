import React from "react";
import { useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { Slip } from "../components/Slip";
import { Big, Eyebrow, Source } from "../components/parts";
import { ease, rise } from "../components/anim";
import { F } from "../data";

const ROLES_AT = 12;
const ROLE_STEP = 4;
const P = F.people;
const STATS_AT = ROLES_AT + P.roles.length * ROLE_STEP + 8;

// Beat 8. The revolving door: roles only, no names.
export const People: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  return (
    <Slip duration={duration} height={1210}>
      <Eyebrow>The revolving door</Eyebrow>
      <div style={{ font: `800 40px/1.2 ${SANS}`, marginTop: 22, marginBottom: 16, ...rise(frame, 4) }}>
        From UK public roles to Palantir:
      </div>
      <div>
        {P.roles.map((r, i) => (
          <div
            key={`${r.label}-${i}`}
            style={{
              display: "grid",
              gridTemplateColumns: "34px 1fr",
              font: `500 29px/1.36 ${SANS}`,
              ...rise(frame, ROLES_AT + i * ROLE_STEP, -18, 8),
            }}
          >
            <span style={{ font: `700 26px/1.55 ${MONO}`, color: COLOR.muted }}>→</span>
            <span>
              {r.label}
              {r.reported && <span style={{ color: COLOR.muted, fontWeight: 400 }}> (reported)</span>}
            </span>
          </div>
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", columnGap: 40, borderTop: `3px solid ${COLOR.ink}`, marginTop: 24, paddingTop: 18, opacity: ease(frame, STATS_AT - 4, 8) }}>
        <div style={rise(frame, STATS_AT, 20)}>
          <Big size={124}>{P.count}</Big>
          <div style={{ font: `500 30px/1.25 ${SANS}`, marginTop: 8 }}>people made the move</div>
        </div>
        <div style={rise(frame, STATS_AT + 14, 20)}>
          <Big size={124}>{P.meetings.count}</Big>
          <div style={{ font: `500 30px/1.25 ${SANS}`, marginTop: 8 }}>
            ministerial meetings or events with Palantir on record, {P.meetings.from}–{P.meetings.to}
          </div>
        </div>
      </div>
      <Source start={30}>Sources: ACOBA, departmental returns and registers. (reported) = press reports only</Source>
    </Slip>
  );
};
