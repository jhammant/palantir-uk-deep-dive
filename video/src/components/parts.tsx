import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { COLOR, MONO, SANS } from "../theme";
import { ease, slam } from "./anim";

export const Eyebrow: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ font: `600 24px/1.2 ${MONO}`, letterSpacing: ".22em", color: COLOR.muted, textTransform: "uppercase", ...style }}>
    {children}
  </div>
);

/** Dashed rule that draws from left to right. */
export const Rule: React.FC<{ start?: number; style?: React.CSSProperties; solid?: boolean }> = ({ start = -100, style, solid }) => {
  const frame = useCurrentFrame();
  const p = ease(frame, start, 14);
  return (
    <div style={{ position: "relative", height: 3, margin: "26px 0", ...style }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: `${p * 100}%`,
          borderTop: solid ? `3px solid ${COLOR.ink}` : `3px dashed ${COLOR.rule}`,
        }}
      />
    </div>
  );
};

/** Red rubber stamp. `at` is the frame it slams down. */
export const Stamp: React.FC<{
  at: number;
  text?: string;
  size?: number;
  color?: string;
  rotate?: number;
  /** transform-origin; "0% 50%" grows from the left edge so it never leaves the slip */
  origin?: string;
  /** starting scale before it slams down */
  from?: number;
  style?: React.CSSProperties;
}> = ({
  at,
  text = "NO COMPETITION",
  size = 22,
  color = COLOR.red,
  rotate = -4,
  origin = "50% 50%",
  from = 2.4,
  style,
}) => {
  const frame = useCurrentFrame();
  const s = slam(frame, at);
  const visible = frame >= at;
  const scale = interpolate(s, [0, 1], [from, 1]);
  return (
    <span
      style={{
        display: "inline-block",
        border: `${Math.max(3, size / 6)}px solid ${color}`,
        color,
        font: `800 ${size}px/1 ${MONO}`,
        letterSpacing: ".12em",
        padding: `${size * 0.32}px ${size * 0.45}px ${size * 0.26}px`,
        borderRadius: 4,
        transform: `rotate(${rotate - (1 - s) * 6}deg) scale(${scale})`,
        transformOrigin: origin,
        opacity: visible ? Math.min(1, s * 1.6) * 0.94 : 0,
        mixBlendMode: "multiply",
        whiteSpace: "nowrap",
        ...style,
      }}
    >
      {text}
    </span>
  );
};

/** Small source line at the foot of a slip. */
export const Source: React.FC<{ children: React.ReactNode; start?: number }> = ({ children, start = 20 }) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        marginTop: "auto",
        paddingTop: 18,
        borderTop: `2px dashed ${COLOR.rule}`,
        font: `400 22px/1.45 ${MONO}`,
        color: COLOR.muted,
        opacity: ease(frame, start, 12),
      }}
    >
      {children}
    </div>
  );
};

/** Text that types out character by character, with a caret while typing. */
export const Typed: React.FC<{ text: string; start: number; perFrame?: number; style?: React.CSSProperties }> = ({
  text,
  start,
  perFrame = 1.2,
  style,
}) => {
  const frame = useCurrentFrame();
  const n = Math.max(0, Math.min(text.length, Math.floor((frame - start) * perFrame)));
  const typing = frame >= start && n < text.length;
  const caretOn = typing || (n === text.length && Math.floor((frame - start) / 8) % 2 === 0 && frame < start + text.length / perFrame + 24);
  return (
    <span style={style}>
      {/* Lay out the full text so lines never re-wrap while typing. */}
      <span>{text.slice(0, n)}</span>
      <span style={{ position: "relative" }}>
        {frame >= start && (
          <span
            style={{
              position: "absolute",
              left: "0.02em",
              top: "0.08em",
              width: "0.07em",
              height: "0.95em",
              background: COLOR.ink,
              opacity: caretOn ? 1 : 0,
            }}
          />
        )}
      </span>
      <span style={{ color: "transparent" }}>{text.slice(n)}</span>
    </span>
  );
};

/** Big headline number. */
export const Big: React.FC<{ children: React.ReactNode; size?: number; color?: string; style?: React.CSSProperties }> = ({
  children,
  size = 200,
  color = COLOR.ink,
  style,
}) => (
  <div
    style={{
      font: `800 ${size}px/0.95 ${SANS}`,
      letterSpacing: "-.035em",
      color,
      fontVariantNumeric: "tabular-nums",
      ...style,
    }}
  >
    {children}
  </div>
);
