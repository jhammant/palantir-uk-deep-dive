import { Easing, interpolate, spring } from "remotion";
import { FPS } from "../theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** 0 -> 1 between `start` and `start + duration`, eased out. */
export const ease = (frame: number, start: number, duration: number) =>
  interpolate(frame, [start, start + duration], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });

/** Linear 0 -> 1. */
export const lin = (frame: number, start: number, duration: number) =>
  interpolate(frame, [start, start + duration], [0, 1], clamp);

/** A quick fade-and-rise used for most text as it lands. */
export const rise = (frame: number, start: number, distance = 24, duration = 12) => {
  const p = ease(frame, start, duration);
  return { opacity: p, transform: `translateY(${(1 - p) * distance}px)` };
};

/** A heavy spring for stamps slamming down. */
export const slam = (frame: number, start: number) =>
  spring({ frame: frame - start, fps: FPS, config: { damping: 13, stiffness: 260, mass: 0.9 } });

/** Count a value up from 0, eased out. */
export const countUp = (frame: number, start: number, duration: number, value: number) =>
  value * ease(frame, start, duration);
