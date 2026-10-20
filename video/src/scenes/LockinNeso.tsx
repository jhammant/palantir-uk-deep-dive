import React from "react";
import { useCurrentFrame } from "remotion";
import { COLOR, SANS } from "../theme";
import { Slip } from "../components/Slip";
import { Eyebrow, Source, Typed } from "../components/parts";
import { ease, rise } from "../components/anim";
import { F, gbpM } from "../data";

const Q1_AT = 22;
const Q1_SPEED = 1.6;
const q1 = `“…${F.lockin.nesoQuote1}”`;
const Q2_AT = Q1_AT + Math.ceil(q1.length / Q1_SPEED) + 12;
const q2 = `“${F.lockin.nesoQuote2}…”`;

// Beat 5a. Lock-in, in NESO's own published words.
export const LockinNeso: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  return (
    <Slip duration={duration} height={1210}>
      <Eyebrow>Lock-in</Eyebrow>
      <div style={{ font: `500 40px/1.3 ${SANS}`, color: COLOR.inkSoft, marginTop: 34, ...rise(frame, 6) }}>
        In {F.lockin.nesoDate}, NESO, the grid operator, awarded Palantir {gbpM(F.lockin.nesoValue)} with{" "}
        <b style={{ color: COLOR.red }}>no competition</b>. Its published reason:
      </div>
      <div style={{ borderLeft: `8px solid ${COLOR.ink}`, paddingLeft: 34, marginTop: 64, borderLeftColor: `rgba(28,28,28,${ease(frame, Q1_AT - 4, 6)})` }}>
        <Typed text={q1} start={Q1_AT} perFrame={Q1_SPEED} style={{ font: `800 88px/1.06 ${SANS}`, letterSpacing: "-.025em" }} />
      </div>
      <div style={{ borderLeft: `8px solid ${COLOR.rule}`, paddingLeft: 34, marginTop: 64, borderLeftColor: `rgba(201,193,174,${ease(frame, Q2_AT - 4, 6)})` }}>
        <Typed text={q2} start={Q2_AT} perFrame={3} style={{ font: `700 54px/1.18 ${SANS}`, letterSpacing: "-.01em" }} />
      </div>
      <Source start={Q1_AT}>
        Source: “{F.lockin.nesoTitle}” direct award notice, {F.lockin.nesoSource}
      </Source>
    </Slip>
  );
};
