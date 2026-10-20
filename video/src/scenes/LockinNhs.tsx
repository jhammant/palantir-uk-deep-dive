import React from "react";
import { useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { Slip } from "../components/Slip";
import { Eyebrow, Source } from "../components/parts";
import { ease, rise } from "../components/anim";
import { F, gbpM } from "../data";

const LINE_AT = 44;
const LATER_AT = 72;

const Dot: React.FC<{ at: number; filled?: boolean }> = ({ at, filled }) => {
  const frame = useCurrentFrame();
  const p = ease(frame, at, 10);
  return (
    <div
      style={{
        position: "absolute",
        left: -55,
        top: 4,
        width: 30,
        height: 30,
        borderRadius: 15,
        border: `5px solid ${COLOR.ink}`,
        background: filled ? COLOR.ink : COLOR.paper,
        transform: `scale(${p})`,
      }}
    />
  );
};

// Beat 5b. NHS England paid Palantir to plan its exit, then Palantir won the replacement.
export const LockinNhs: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const line = ease(frame, LINE_AT, 30);
  return (
    <Slip duration={duration} height={1210}>
      <Eyebrow>Lock-in · NHS England</Eyebrow>
      <div style={{ position: "relative", marginTop: 54, marginLeft: 70 }}>
        {/* the rail */}
        <div style={{ position: "absolute", left: -43, top: 40, width: 6, height: 430 * line, background: COLOR.ink }} />

        <div style={{ position: "relative", ...rise(frame, 10) }}>
          <Dot at={8} />
          <div style={{ font: `700 28px/1 ${MONO}`, letterSpacing: ".16em", color: COLOR.muted }}>{F.lockin.exitDate.toUpperCase()}</div>
          <div style={{ font: `800 50px/1.12 ${SANS}`, letterSpacing: "-.02em", marginTop: 14 }}>
            NHS England signed a {gbpM(F.lockin.exitValue)} “Transition & Exit” contract with Palantir
          </div>
          <div style={{ font: `400 30px/1.35 ${SANS}`, color: COLOR.muted, marginTop: 14 }}>
            “{F.lockin.exitPurpose}” to a new supplier
          </div>
        </div>

        <div
          style={{
            height: 190,
            display: "flex",
            alignItems: "center",
            font: `800 30px/1 ${MONO}`,
            letterSpacing: ".18em",
            opacity: ease(frame, LINE_AT + 10, 12),
          }}
        >
          {F.lockin.monthsLaterWord.toUpperCase()} MONTHS LATER ↓
        </div>

        <div style={{ position: "relative", ...rise(frame, LATER_AT) }}>
          <Dot at={LATER_AT} filled />
          <div style={{ font: `700 28px/1 ${MONO}`, letterSpacing: ".16em", color: COLOR.muted }}>{F.lockin.fdpDate.toUpperCase()}</div>
          <div style={{ font: `800 84px/1.0 ${SANS}`, letterSpacing: "-.035em", marginTop: 16 }}>Palantir won the replacement.</div>
          <div style={{ font: `400 30px/1.35 ${SANS}`, color: COLOR.muted, marginTop: 18, ...rise(frame, LATER_AT + 16) }}>
            The {gbpM(F.lockin.fdpValue)} Federated Data Platform, awarded to a Palantir-led consortium
          </div>
        </div>
      </div>
      <Source start={20}>Sources: {F.contracts.sources.join(" and ")}. Values as published.</Source>
    </Slip>
  );
};
