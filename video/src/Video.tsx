import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame } from "remotion";
import { COLOR, MONO } from "./theme";
import { SCHEDULE, beatStart, type BeatId } from "./timeline";
import { Title } from "./scenes/Title";
import { Receipt } from "./scenes/Receipt";
import { Awarded } from "./scenes/Awarded";
import { Paid } from "./scenes/Paid";
import { LockinNeso } from "./scenes/LockinNeso";
import { LockinNhs } from "./scenes/LockinNhs";
import { Market } from "./scenes/Market";
import { Tax } from "./scenes/Tax";
import { People } from "./scenes/People";
import { QuoteMosley, QuoteThiel } from "./scenes/Quotes";
import { Closing, EndCard } from "./scenes/Closing";

const SCENES: Record<BeatId, React.FC<{ duration: number }>> = {
  title: Title,
  receipt: Receipt,
  awarded: Awarded,
  paid: Paid,
  neso: LockinNeso,
  nhs: LockinNhs,
  market: Market,
  tax: Tax,
  people: People,
  mosley: QuoteMosley,
  thiel: QuoteThiel,
  closing: Closing,
  end: EndCard,
};

/** Small site address under every slip, so a clipped repost still credits the source. */
const Footer: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame >= beatStart("end")) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 26,
        textAlign: "center",
        font: `500 22px/1 ${MONO}`,
        letterSpacing: ".06em",
        color: COLOR.footer,
      }}
    >
      jhammant.github.io/palantir-uk-deep-dive
    </div>
  );
};

export const PalantirBill: React.FC = () => (
  <AbsoluteFill style={{ background: `radial-gradient(120% 90% at 50% 40%, #1d2024 0%, ${COLOR.bg} 60%, #111315 100%)` }}>
    {SCHEDULE.map((b) => {
      const Scene = SCENES[b.id];
      return (
        <Sequence key={b.id} from={b.from} durationInFrames={b.duration} name={b.label}>
          <Scene duration={b.duration} />
        </Sequence>
      );
    })}
    <Footer />
  </AbsoluteFill>
);
