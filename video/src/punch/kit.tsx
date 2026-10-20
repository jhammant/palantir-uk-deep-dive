import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame } from "remotion";
import { COLOR, SANS } from "../theme";
import { B, FPS } from "./timeline";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const PAD = 80; // side margin
export const INK = COLOR.ink;
export const RED = COLOR.red;
export const MUTED = COLOR.muted;

/** Snappy spring, 0 -> ~1 with a little overshoot. */
export const snap = (frame: number, at: number, stiffness = 320) =>
  frame < at ? 0 : spring({ frame: frame - at, fps: FPS, config: { damping: 14, stiffness, mass: 0.7 } });

export const easeOut = (frame: number, at: number, dur: number) =>
  interpolate(frame, [at, at + dur], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });

/** Big type slamming in: scales down from `from` and snaps into place. */
export const slamIn = (frame: number, at: number, from = 1.7): React.CSSProperties => {
  const s = snap(frame, at);
  return {
    opacity: frame < at ? 0 : Math.min(1, s * 2.5),
    transform: `scale(${interpolate(s, [0, 1], [from, 1])})`,
  };
};

/** Slide in from an offset (px), snapping into place. */
export const slideIn = (frame: number, at: number, dx = 0, dy = 120): React.CSSProperties => {
  const s = snap(frame, at, 260);
  return {
    opacity: frame < at ? 0 : Math.min(1, s * 2),
    transform: `translate(${(1 - s) * dx}px, ${(1 - s) * dy}px)`,
  };
};

/** A small kick on every beat of the pulse, so hero type breathes with the sound. */
export const beatBounce = (frame: number, amount = 0.018) => {
  const d = frame % B;
  return 1 + amount * Math.exp(-d / 3.5);
};

/** Screen shake after each impact frame. */
export const shake = (frame: number, impacts: number[], strength = 1) => {
  let x = 0;
  let y = 0;
  for (const t of impacts) {
    const d = frame - t;
    if (d >= 0 && d < 10) {
      const a = (10 - d) * 1.6 * strength;
      x += Math.sin(d * 2.9) * a;
      y += Math.cos(d * 3.7) * a * 0.7;
    }
  }
  return `translate(${x}px, ${y}px)`;
};

/**
 * One beat: full-bleed paper (or ink), a hard cut in, a quick camera snap on
 * the cut and a slow push for the rest of the beat, so nothing sits still.
 */
export const Beat: React.FC<{ duration: number; dark?: boolean; impacts?: number[]; children: React.ReactNode }> = ({
  duration,
  dark,
  impacts = [],
  children,
}) => {
  const frame = useCurrentFrame();
  const push = 1 + 0.035 * interpolate(frame, [0, duration], [0, 1], clamp);
  const cut = 1 + 0.06 * (1 - easeOut(frame, 0, 8));
  return (
    <AbsoluteFill
      style={{
        background: dark
          ? `radial-gradient(110% 80% at 50% 45%, #1f2226 0%, ${COLOR.bg} 70%)`
          : `radial-gradient(120% 90% at 50% 40%, #faf7ef 0%, ${COLOR.paper} 55%, #ece6d8 100%)`,
        overflow: "hidden",
        fontFamily: SANS,
        color: dark ? COLOR.paper : INK,
      }}
    >
      <AbsoluteFill style={{ transform: `${shake(frame, impacts)} scale(${push * cut})` }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Small attribution / source line. Kept short and quiet. */
export const Small: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ font: `500 34px/1.3 ${SANS}`, color: MUTED, ...style }}>{children}</div>
);

/** Red rubber stamp, big. */
export const BigStamp: React.FC<{ at: number; lines: { text: string; size: number }[]; rotate?: number; style?: React.CSSProperties }> = ({
  at,
  lines,
  rotate = -7,
  style,
}) => {
  const frame = useCurrentFrame();
  const s = snap(frame, at, 420);
  if (frame < at) return null;
  return (
    <div
      style={{
        position: "absolute",
        border: `11px solid ${RED}`,
        borderRadius: 10,
        padding: "18px 34px 14px",
        color: RED,
        background: "rgba(250,247,239,.86)",
        textAlign: "center",
        transform: `rotate(${rotate + (1 - s) * -8}deg) scale(${interpolate(s, [0, 1], [3, 1])})`,
        opacity: Math.min(1, s * 3),
        boxShadow: "0 0 0 4px rgba(181,16,43,.12)",
        ...style,
      }}
    >
      {lines.map((l) => (
        <div key={l.text} style={{ font: `900 ${l.size}px/1 ${SANS}`, letterSpacing: l.size < 100 ? ".06em" : "-.03em" }}>
          {l.text}
        </div>
      ))}
    </div>
  );
};
