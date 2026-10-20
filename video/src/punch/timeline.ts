// Timing for the 30-second punch cut. Pure data: the scenes read it for their
// animation and scripts/punch-audio.ts reads it to place every tick, thud and
// pulse, so picture and sound stay locked together.
//
// Everything sits on a beat grid of 17 frames at 30fps (105.9 bpm). Every beat
// starts on a grid line, so every hard cut lands on the pulse.

export const FPS = 30;
export const B = 17; // frames per beat
export const BPM = (60 * FPS) / B;

export const T = {
  hook: { beats: 6, count: [0, 14], zoom: [16, 34], stamp: 36 },
  revenue: { beats: 5, count: [0, 12] },
  tax: { beats: 6, slam: 8, bars: [36, 48] },
  cents: { beats: 5, slam: 4, sliver: 30 },
  buying: { beats: 6, words: [0, 6, 13, 21], response: 17, who: 34 },
  neso: { beats: 6, type: [4, 30], stamp: 51 },
  nhs: { beats: 7, count: [0, 12], swap: 3 * B },
  people: { beats: 5, count: [0, 22] },
  closing: { beats: 7, line2: 3 * B },
  end: { beats: 5 },
} as const;

export type PunchId = keyof typeof T;

export const PUNCH_ORDER: PunchId[] = ["hook", "revenue", "tax", "cents", "buying", "neso", "nhs", "people", "closing", "end"];

export const PUNCH_LABELS: Record<PunchId, string> = {
  hook: "01 £647m · 40% no competition",
  revenue: "02 UK revenue",
  tax: "03 UK income tax",
  cents: "04 Per $100",
  buying: "05 Buying our way in",
  neso: "06 NESO lock-in",
  nhs: "07 NHS exit",
  people: "08 Revolving door",
  closing: "09 Closing line",
  end: "10 End card",
};

export const PUNCH_SCHEDULE = (() => {
  let at = 0;
  return PUNCH_ORDER.map((id) => {
    const duration = T[id].beats * B;
    const s = { id, from: at, duration, label: PUNCH_LABELS[id] };
    at += duration;
    return s;
  });
})();

export const PUNCH_FRAMES = PUNCH_SCHEDULE.reduce((s, b) => s + b.duration, 0);

export const punchStart = (id: PunchId) => PUNCH_SCHEDULE.find((s) => s.id === id)!.from;

/** One still per beat for the contact sheet, after everything has landed. */
export const PUNCH_STILLS = PUNCH_SCHEDULE.flatMap((s) => {
  const late = s.from + s.duration - 6;
  // Two-part beats get a frame from each half.
  if (s.id === "nhs") return [{ frame: s.from + T.nhs.swap - 4, label: `${s.label} (1)` }, { frame: late, label: `${s.label} (2)` }];
  if (s.id === "closing") return [{ frame: s.from + T.closing.line2 - 4, label: `${s.label} (1)` }, { frame: late, label: `${s.label} (2)` }];
  return [{ frame: late, label: s.label }];
});

/* ------------------------------------------------------------ sound cues */

export type Cue =
  | { kind: "pulse"; frame: number; accent: boolean; level: number }
  | { kind: "tick"; frame: number; level: number }
  | { kind: "thud"; frame: number }
  | { kind: "hit"; frame: number; level: number };

/** Every sound event, in frames from the start of the punch cut. */
export const punchCues = (): Cue[] => {
  const cues: Cue[] = [];
  const at = (id: PunchId, f: number) => punchStart(id) + f;
  const ticks = (id: PunchId, [a, b]: readonly number[], every = 1, level = 1) => {
    for (let f = a; f <= b; f += every) cues.push({ kind: "tick", frame: at(id, f), level });
  };

  // The pulse: one soft kick per beat, accented at each cut. It drops to half
  // for the closing line and stops for the end card.
  for (const s of PUNCH_SCHEDULE) {
    if (s.id === "end") continue;
    for (let f = 0; f < s.duration; f += B) {
      const level = s.id === "closing" ? 0.5 : 1;
      cues.push({ kind: "pulse", frame: s.from + f, accent: f === 0, level });
    }
  }

  // Receipt-printer ticks under every count and the typed quote.
  ticks("hook", T.hook.count);
  ticks("revenue", T.revenue.count);
  ticks("nhs", T.nhs.count);
  ticks("people", T.people.count, 1.5, 0.9);
  ticks("neso", T.neso.type, 1, 0.8);

  // Stamps land with a thud; big type lands with a hit.
  cues.push({ kind: "thud", frame: at("hook", T.hook.stamp) });
  cues.push({ kind: "thud", frame: at("neso", T.neso.stamp) });
  cues.push({ kind: "hit", frame: at("tax", T.tax.slam), level: 0.8 });
  cues.push({ kind: "hit", frame: at("cents", T.cents.slam), level: 0.8 });
  for (const w of T.buying.words) cues.push({ kind: "hit", frame: at("buying", w), level: 0.55 });
  cues.push({ kind: "hit", frame: at("nhs", T.nhs.swap), level: 0.8 });
  cues.push({ kind: "hit", frame: at("closing", T.closing.line2), level: 1 });
  cues.push({ kind: "hit", frame: at("end", 0), level: 0.7 });

  return cues.map((c) => ({ ...c, frame: Math.round(c.frame) })).sort((a, b) => a.frame - b.frame);
};
