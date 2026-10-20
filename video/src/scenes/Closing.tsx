import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { Slip, useBeatMotion } from "../components/Slip";
import { Eyebrow, Rule } from "../components/parts";
import { ease, rise } from "../components/anim";
import { F } from "../data";

// Beat 10a. The closing line, straight on the dark background.
export const Closing: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const motion = useBeatMotion(duration);
  return (
    <AbsoluteFill style={{ ...motion, padding: "0 92px", justifyContent: "center", color: COLOR.paper, fontFamily: SANS }}>
      <div style={{ font: `700 74px/1.08 ${SANS}`, letterSpacing: "-.025em", color: "#d9d3c4", ...rise(frame, 10, 30, 16) }}>
        Sovereignty isn't where the servers sit.
      </div>
      <div style={{ font: `800 112px/1.0 ${SANS}`, letterSpacing: "-.04em", marginTop: 48, ...rise(frame, 40, 30, 16) }}>
        It's whether you can leave.
      </div>
    </AbsoluteFill>
  );
};

// Beat 10b. End card: where to check every figure.
export const EndCard: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  return (
    <Slip duration={duration} exit={false} top={215} height={880} padTop={90} style={{ textAlign: "center", alignItems: "center" }}>
      <Eyebrow>Palantir UK deep dive</Eyebrow>
      <div style={{ font: `800 84px/1.02 ${SANS}`, letterSpacing: "-.03em", margin: "26px 0 0" }}>The UK's Palantir bill</div>
      <Rule start={8} style={{ width: "100%", margin: "50px 0 54px" }} />
      <div style={{ font: `700 54px/1.25 ${MONO}`, letterSpacing: "-.01em", ...rise(frame, 10) }}>
        jhammant.github.io/
        <br />
        palantir-uk-deep-dive
      </div>
      <div style={{ font: `500 40px/1.3 ${SANS}`, marginTop: 50, ...rise(frame, 22) }}>Every figure links to its public source.</div>
      <div style={{ marginTop: "auto", opacity: ease(frame, 30, 12) }}>
        <div style={{ font: `500 32px/1.3 ${SANS}`, color: COLOR.ink }}>Compiled by Jon Hammant (Orbital)</div>
        <div style={{ font: `400 24px/1.3 ${MONO}`, color: COLOR.muted, marginTop: 14 }}>Data as of {F.generated}</div>
      </div>
    </Slip>
  );
};
