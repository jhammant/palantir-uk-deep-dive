import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { CARD, COLOR, SANS, WIDTH } from "../theme";

// Torn top and bottom edges, as on the receipt image.
const TORN_MASK =
  "conic-gradient(from -45deg at bottom, #0000, #000 1deg 89deg, #0000 90deg) bottom/24px 51% repeat-x," +
  "conic-gradient(from 135deg at top, #0000, #000 1deg 89deg, #0000 90deg) top/24px 51% repeat-x";

export const ENTER = 14;
export const EXIT = 12;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Slide-in / slide-out for a whole beat. */
export const useBeatMotion = (duration: number, enter = true, exit = true) => {
  const frame = useCurrentFrame();
  const inP = enter ? interpolate(frame, [0, ENTER], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) }) : 1;
  const inFade = enter ? interpolate(frame, [0, 4], [0, 1], clamp) : 1;
  const outP = exit ? interpolate(frame, [duration - EXIT, duration], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) }) : 0;
  // The incoming slip is opaque almost at once and slides up over the outgoing
  // one, which drifts up and fades underneath: no see-through ghosting.
  return {
    opacity: inFade * (1 - outP),
    transform: `translateY(${(1 - inP) * 240 - outP * 90}px)`,
  };
};

/** A paper slip on the dark background. Every beat is one slip. */
export const Slip: React.FC<{
  duration: number;
  enter?: boolean;
  exit?: boolean;
  width?: number;
  top?: number;
  height?: number;
  /** Grow with the content instead of using a fixed height. */
  fit?: boolean;
  padTop?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
  outerStyle?: React.CSSProperties;
}> = ({ duration, enter, exit, width = CARD.width, top = CARD.top, height = CARD.height, fit, padTop = 72, children, style, outerStyle }) => {
  const motion = useBeatMotion(duration, enter, exit);
  return (
    <AbsoluteFill style={motion}>
      <div
        style={{
          position: "absolute",
          left: (WIDTH - width) / 2,
          top,
          width,
          height: fit ? undefined : height,
          filter: "drop-shadow(0 28px 40px rgba(0,0,0,.55))",
          ...outerStyle,
        }}
      >
        <div
          style={{
            position: "relative",
            height: fit ? undefined : "100%",
            boxSizing: "border-box",
            background: `linear-gradient(180deg, #f7f4ea 0%, ${COLOR.paper} 45%, #f1ecdf 100%)`,
            WebkitMask: TORN_MASK,
            mask: TORN_MASK,
            padding: `${padTop}px ${CARD.padX}px 58px`,
            display: "flex",
            flexDirection: "column",
            fontFamily: SANS,
            color: COLOR.ink,
            ...style,
          }}
        >
          {children}
        </div>
      </div>
    </AbsoluteFill>
  );
};
