import React from "react";
import { useCurrentFrame } from "remotion";
import { COLOR, MONO } from "../theme";
import { Slip } from "../components/Slip";
import { Eyebrow, Rule } from "../components/parts";
import { ease } from "../components/anim";

// Beat 1. Fully drawn on frame 0 so LinkedIn's autoplay preview is never blank.
export const Title: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const drift = 1 + ease(frame, 0, duration) * 0.025;
  return (
    <Slip duration={duration} enter={false} top={335} height={660} padTop={84} style={{ textAlign: "center", alignItems: "center" }}>
      <Eyebrow>UK public sector → Palantir</Eyebrow>
      <div
        style={{
          font: `800 136px/0.98 "Helvetica Neue", Helvetica, Arial, sans-serif`,
          letterSpacing: "-.035em",
          margin: "34px 0 30px",
          transform: `scale(${drift})`,
        }}
      >
        The UK's
        <br />
        Palantir bill
      </div>
      <div style={{ font: `400 36px/1.3 ${MONO}`, color: COLOR.muted }}>Itemised from the public record</div>
      <Rule style={{ width: "100%", margin: "40px 0 22px" }} />
      <div style={{ width: "100%", display: "flex", justifyContent: "space-between", font: `600 24px/1 ${MONO}`, letterSpacing: ".2em", color: COLOR.muted }}>
        <span>ITEM</span>
        <span>AMOUNT</span>
      </div>
    </Slip>
  );
};
