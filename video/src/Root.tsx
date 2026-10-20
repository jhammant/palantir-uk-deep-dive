import React from "react";
import { Composition } from "remotion";
import { PalantirBill } from "./Video";
import { FPS, HEIGHT, WIDTH } from "./theme";
import { TOTAL_FRAMES } from "./timeline";

export const Root: React.FC = () => (
  <Composition id="PalantirBill-4x5" component={PalantirBill} durationInFrames={TOTAL_FRAMES} fps={FPS} width={WIDTH} height={HEIGHT} />
);
