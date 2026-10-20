import React from "react";
import { COLOR } from "../theme";

export interface Segment {
  value: number;
  color: string;
}

const polar = (cx: number, cy: number, r: number, a: number) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];

const arc = (cx: number, cy: number, R: number, r: number, a0: number, a1: number) => {
  const large = a1 - a0 > Math.PI ? 1 : 0;
  const [x0, y0] = polar(cx, cy, R, a0);
  const [x1, y1] = polar(cx, cy, R, a1);
  const [x2, y2] = polar(cx, cy, r, a1);
  const [x3, y3] = polar(cx, cy, r, a0);
  return `M${x0},${y0}A${R},${R} 0 ${large} 1 ${x1},${y1}L${x2},${y2}A${r},${r} 0 ${large} 0 ${x3},${y3}Z`;
};

/**
 * Donut chart that sweeps clockwise from 12 o'clock as `progress` goes 0 -> 1.
 * Segments are drawn in order with a paper-coloured gap between them.
 */
export const Donut: React.FC<{
  segments: Segment[];
  size: number;
  thickness: number;
  progress: number;
  children?: React.ReactNode;
}> = ({ segments, size, thickness, progress, children }) => {
  const total = segments.reduce((s, x) => s + x.value, 0);
  const c = size / 2;
  const R = c - 2;
  const r = R - thickness;
  const start = -Math.PI / 2;
  const sweep = Math.PI * 2 * progress;
  let acc = 0;
  const paths = segments.map((seg, i) => {
    const a0 = start + (acc / total) * Math.PI * 2;
    acc += seg.value;
    const a1Full = start + (acc / total) * Math.PI * 2;
    const a1 = Math.min(a1Full, start + sweep);
    if (a1 <= a0 + 0.0005) return null;
    // A full ring needs two halves; a single segment never reaches 2π here.
    return <path key={i} d={arc(c, c, R, r, a0, Math.min(a1, a0 + Math.PI * 2 - 0.0001))} fill={seg.color} stroke={COLOR.paper} strokeWidth={4} />;
  });
  return (
    <div style={{ position: "relative", width: size, height: size, flex: "none" }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ position: "absolute", inset: 0 }}>
        <circle cx={c} cy={c} r={R - thickness / 2} fill="none" stroke="#e7e1d3" strokeWidth={thickness} />
        {paths}
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
        {children}
      </div>
    </div>
  );
};
