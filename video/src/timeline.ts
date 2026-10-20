// Beat order and timing. Each beat's slip slides out over its last frames while
// the next one slides in, so consecutive beats overlap by OVERLAP frames.
// `stills` are frames (relative to the beat) where everything has landed; the
// contact sheet uses them, and POSTER picks the finished receipt.
export const OVERLAP = 12;

export const BEATS = [
  { id: "title", label: "1 Title", duration: 90, stills: [40] },
  { id: "receipt", label: "2 Receipt", duration: 282, stills: [160, 266] },
  { id: "awarded", label: "3 Awarded", duration: 184, stills: [168] },
  { id: "paid", label: "4 Paid", duration: 188, stills: [172] },
  { id: "neso", label: "5a Lock-in: NESO", duration: 190, stills: [174] },
  { id: "nhs", label: "5b Lock-in: NHS", duration: 190, stills: [174] },
  { id: "market", label: "6 Market share", duration: 178, stills: [162] },
  { id: "tax", label: "7 Income tax", duration: 204, stills: [188] },
  { id: "people", label: "8 People", duration: 192, stills: [176] },
  { id: "mosley", label: "9a Mosley", duration: 186, stills: [170] },
  { id: "thiel", label: "9b Thiel", duration: 172, stills: [156] },
  { id: "closing", label: "10a Closing", duration: 144, stills: [128] },
  { id: "end", label: "10b End card", duration: 140, stills: [130] },
] as const;

export type BeatId = (typeof BEATS)[number]["id"];

export const SCHEDULE = (() => {
  let at = 0;
  return BEATS.map((b, i) => {
    const from = at;
    at += b.duration - (i < BEATS.length - 1 ? OVERLAP : 0);
    return { ...b, from };
  });
})();

export const TOTAL_FRAMES = SCHEDULE[SCHEDULE.length - 1].from + SCHEDULE[SCHEDULE.length - 1].duration;

/** Every contact-sheet frame, in order, with a label. */
export const STILLS = SCHEDULE.flatMap((b) => b.stills.map((f, i) => ({ frame: b.from + f, label: b.stills.length > 1 ? `${b.label} (${i + 1})` : b.label })));

/** The finished receipt, stamps and total: the strongest single frame. */
const receiptBeat = SCHEDULE[1];
const receiptStills: readonly number[] = receiptBeat.stills;
export const POSTER_FRAME = receiptBeat.from + receiptStills[receiptStills.length - 1];

export const beatStart = (id: BeatId) => {
  const b = SCHEDULE.find((s) => s.id === id);
  if (!b) throw new Error(`no beat ${id}`);
  return b.from;
};
