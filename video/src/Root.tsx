import React from "react";
import { Composition } from "remotion";
import { PalantirBill } from "./Video";
import { PalantirPunch } from "./punch/Punch";
import { FPS, HEIGHT, WIDTH } from "./theme";
import { TOTAL_FRAMES } from "./timeline";
import { PUNCH_FRAMES } from "./punch/timeline";

export const Root: React.FC = () => (
  <>
    <Composition id="PalantirBill-4x5" component={PalantirBill} durationInFrames={TOTAL_FRAMES} fps={FPS} width={WIDTH} height={HEIGHT} />
    <Composition
      id="PalantirPunch-4x5"
      component={PalantirPunch}
      durationInFrames={PUNCH_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
      defaultProps={{ withAudio: true }}
    />
  </>
);
