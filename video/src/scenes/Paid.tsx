import React from "react";
import { useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { Slip } from "../components/Slip";
import { Big, Eyebrow, Source, Stamp } from "../components/parts";
import { countUp, rise } from "../components/anim";
import { F, gbpM } from "../data";

const NO_NOTICE_AT = 80;

// Beat 4. What was actually paid: a floor, not a total.
export const Paid: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  return (
    <Slip duration={duration} height={1210}>
      <Eyebrow>What was actually paid</Eyebrow>
      <Big size={196} style={{ marginTop: 40, ...rise(frame, 8, 20, 10) }}>
        {gbpM(countUp(frame, 10, 30, F.paid.total))}
      </Big>
      <div style={{ font: `500 40px/1.25 ${SANS}`, marginTop: 22, maxWidth: 820, ...rise(frame, 26) }}>
        paid to Palantir, in the published spending files of {F.paid.bodies} public bodies
      </div>
      <div style={{ marginTop: 34, height: 64 }}>
        <Stamp at={46} text="A FLOOR, NOT A TOTAL" size={30} color={COLOR.ink} rotate={-2} />
      </div>
      <div style={{ font: `400 29px/1.4 ${MONO}`, color: COLOR.muted, marginTop: 18, maxWidth: 830, ...rise(frame, 56) }}>
        Some bodies publish no spending files. The MoD's name no Palantir payment after {F.paid.modLast}.
      </div>

      <div style={{ borderTop: `3px solid ${COLOR.ink}`, marginTop: 50, paddingTop: 34, ...rise(frame, NO_NOTICE_AT - 4, 16) }}>
        <Big size={150}>{gbpM(countUp(frame, NO_NOTICE_AT, 18, F.noNotice.total))}</Big>
        <div style={{ font: `500 40px/1.25 ${SANS}`, marginTop: 20, maxWidth: 820, ...rise(frame, NO_NOTICE_AT + 8) }}>
          paid by {F.noNotice.bodies} public bodies with no Palantir contract notice found
        </div>
      </div>
      <Source start={30}>Source: published spending files and FOI responses, net of credit notes</Source>
    </Slip>
  );
};
