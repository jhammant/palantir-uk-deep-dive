import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { COLOR } from "../theme";
import { PUNCH_SCHEDULE, type PunchId } from "./timeline";
import { Buying, Cents, Closing, End, Hook, Neso, Nhs, People, Revenue, Tax } from "./scenes";

const SCENES: Record<PunchId, React.FC<{ duration: number }>> = {
  hook: Hook,
  revenue: Revenue,
  tax: Tax,
  cents: Cents,
  buying: Buying,
  neso: Neso,
  nhs: Nhs,
  people: People,
  closing: Closing,
  end: End,
};

/** File written by scripts/punch-audio.ts (npm run punch:audio). */
export const PUNCH_AUDIO = "punch-audio.wav";

// The 30-second punch cut: hard cuts on the beat, no fades between beats.
export const PalantirPunch: React.FC<{ withAudio?: boolean }> = ({ withAudio = true }) => (
  <AbsoluteFill style={{ background: COLOR.paper }}>
    {PUNCH_SCHEDULE.map((s) => {
      const Scene = SCENES[s.id];
      return (
        <Sequence key={s.id} from={s.from} durationInFrames={s.duration} name={s.label}>
          <Scene duration={s.duration} />
        </Sequence>
      );
    })}
    {withAudio && <Audio src={staticFile(PUNCH_AUDIO)} />}
  </AbsoluteFill>
);
