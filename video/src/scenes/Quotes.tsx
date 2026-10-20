import React from "react";
import { useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { Slip } from "../components/Slip";
import { Eyebrow, Source } from "../components/parts";
import { ease, rise, slam } from "../components/anim";
import { F } from "../data";

const Q = F.quotes;

// Beat 9a. "Buying our way in…!", always shown with Palantir's responses.
export const QuoteMosley: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const s = slam(frame, 8);
  return (
    <Slip duration={duration} height={1210}>
      <Eyebrow>In their own words</Eyebrow>
      <div
        style={{
          font: `800 138px/0.97 ${SANS}`,
          letterSpacing: "-.04em",
          marginTop: 56,
          transformOrigin: "0% 50%",
          transform: `scale(${1.25 - 0.25 * s})`,
          opacity: Math.min(1, s * 1.5),
        }}
      >
        “{Q.mosley.text}”
      </div>
      <div style={{ font: `500 39px/1.32 ${SANS}`, marginTop: 44, ...rise(frame, 26) }}>
        Subject line of a {Q.mosley.year} internal email about the NHS from Louis Mosley, who runs Palantir in the UK. Reported by{" "}
        {Q.mosley.reporter}.
      </div>
      <div style={{ borderLeft: `8px solid ${COLOR.rule}`, paddingLeft: 30, marginTop: 60, display: "grid", gap: 34, opacity: ease(frame, 52, 8) }}>
        <div style={{ font: `400 38px/1.3 ${SANS}`, ...rise(frame, 56) }}>
          <span style={{ font: `700 24px/1 ${MONO}`, letterSpacing: ".14em", color: COLOR.muted, display: "block", marginBottom: 8 }}>
            PALANTIR'S RESPONSE
          </span>
          It called the language “{Q.mosley.regrettable}”.
        </div>
        <div style={{ font: `400 38px/1.3 ${SANS}`, ...rise(frame, 72) }}>
          <span style={{ font: `700 24px/1 ${MONO}`, letterSpacing: ".14em", color: COLOR.muted, display: "block", marginBottom: 8 }}>
            MOSLEY, {Q.mosley.laterDate.toUpperCase()}
          </span>
          “{Q.mosley.later.charAt(0).toUpperCase() + Q.mosley.later.slice(1)}”
        </div>
      </div>
      <Source start={30}>
        Sources: {Q.mosley.reporter}, {Q.mosley.reportedOn}, via {Q.mosley.via}; {Q.mosley.laterSource}, {Q.mosley.laterDate}
      </Source>
    </Slip>
  );
};

const ThielQuote: React.FC<{ text: string; cite: string; at: number; size: number }> = ({ text, cite, at, size }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ marginTop: 70, ...rise(frame, at, 26, 14) }}>
      <div style={{ font: `800 ${size}px/1.06 ${SANS}`, letterSpacing: "-.03em" }}>“{text}”</div>
      <div style={{ font: `400 30px/1.3 ${MONO}`, color: COLOR.muted, marginTop: 20 }}>{cite}</div>
    </div>
  );
};

// Beat 9b. Palantir's chairman and co-founder.
export const QuoteThiel: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  return (
    <Slip duration={duration} height={1210}>
      <Eyebrow>Palantir's chairman and co-founder</Eyebrow>
      <div style={{ font: `800 70px/1 ${SANS}`, letterSpacing: "-.025em", marginTop: 24, ...rise(frame, 2) }}>Peter Thiel</div>
      <ThielQuote text={Q.thielSick.text} cite={`Oxford Union address, ${Q.thielSick.year}`} at={14} size={102} />
      <ThielQuote text={Q.thielDemocracy.text} cite={`Essay for the Cato Institute, ${Q.thielDemocracy.year}`} at={58} size={84} />
      <Source start={30}>Sources: Oxford Union video; Cato Unbound</Source>
    </Slip>
  );
};
