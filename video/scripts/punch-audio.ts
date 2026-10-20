// Synthesises the punch cut's soundtrack from scratch: no music, no samples.
// Every sound comes from the cue list in src/punch/timeline.ts, so it lands on
// the same frames as the picture:
//   pulse  a soft low kick on every beat (105.9 bpm), accented on each cut
//   tick   a receipt-printer tick under every count and the typed quote
//   thud   a low thud for each stamp
//   hit    a shorter low hit when big type lands
// The mix is then set to -16 LUFS integrated with ffmpeg (volume + limiter),
// measured with ebur128. Output: public/punch-audio.wav
//
// Run: npm run punch:audio
import { execFileSync, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { FPS, PUNCH_FRAMES, B, punchCues, PUNCH_SCHEDULE } from "../src/punch/timeline";

const SR = 48000;
const TARGET_LUFS = -16;
const root = process.cwd();
const cacheDir = path.join(root, "node_modules", ".cache");
const rawPath = path.join(cacheDir, "punch-raw.wav");
const outPath = path.join(root, "public", "punch-audio.wav");
fs.mkdirSync(cacheDir, { recursive: true });
fs.mkdirSync(path.dirname(outPath), { recursive: true });

const seconds = PUNCH_FRAMES / FPS;
const N = Math.ceil(seconds * SR);
const L = new Float32Array(N);
const R = new Float32Array(N);

// Deterministic noise, so every build makes the same file.
let seed = 0x5eed1234;
const rand = () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const noise = () => rand() * 2 - 1;
const sat = (x: number, d: number) => Math.tanh(d * x) / Math.tanh(d);

const add = (start: number, len: number, fn: (t: number, i: number) => number, pan = 0) => {
  const s0 = Math.round(start * SR);
  const gl = Math.cos(((pan + 1) * Math.PI) / 4) * Math.SQRT2;
  const gr = Math.sin(((pan + 1) * Math.PI) / 4) * Math.SQRT2;
  for (let i = 0; i < len * SR; i++) {
    const j = s0 + i;
    if (j < 0 || j >= N) continue;
    const v = fn(i / SR, i);
    L[j] += v * gl;
    R[j] += v * gr;
  }
};

/** Low kick with a pitch drop; saturation adds harmonics phone speakers can play. */
const kick = (t0: number, amp: number, accent: boolean) => {
  let phase = 0;
  add(t0, 0.5, (t) => {
    const f = 46 + 95 * Math.exp(-t / 0.028);
    phase += (2 * Math.PI * f) / SR;
    const env = Math.exp(-t / (accent ? 0.2 : 0.13)) * Math.min(1, t / 0.0015);
    const click = t < 0.006 ? noise() * Math.exp(-t / 0.0012) * 0.18 : 0;
    return amp * (sat(Math.sin(phase) * env, 2.4) + click);
  });
};

/** Quiet off-beat shaker that keeps the tempo moving between kicks. */
const shaker = (t0: number, amp: number) => {
  let prev = 0;
  add(t0, 0.05, (t) => {
    const n = noise();
    const hp = n - prev;
    prev = n;
    return amp * hp * Math.exp(-t / 0.012) * Math.min(1, t / 0.004);
  }, 0.15);
};

/** Receipt-printer tick: a tiny high click with a short metallic ring. */
const tick = (t0: number, amp: number, pan: number) => {
  let prev = 0;
  const ring = 3400 + rand() * 900;
  add(t0, 0.012, (t) => {
    const n = noise();
    const hp = n - prev;
    prev = n;
    return amp * (hp * 0.7 * Math.exp(-t / 0.0009) + Math.sin(2 * Math.PI * ring * t) * 0.45 * Math.exp(-t / 0.0022));
  }, pan);
};

/** Stamp: a deep thud with a papery slap on top. */
const thud = (t0: number) => {
  let phase = 0;
  let lp = 0;
  add(t0, 1.1, (t) => {
    const f = 34 + 75 * Math.exp(-t / 0.045);
    phase += (2 * Math.PI * f) / SR;
    const body = sat(Math.sin(phase) * Math.exp(-t / 0.32) * Math.min(1, t / 0.001), 3.2);
    lp += 0.09 * (noise() - lp);
    const slap = lp * 2.2 * Math.exp(-t / 0.028);
    const crack = noise() * 0.35 * Math.exp(-t / 0.0035);
    return 0.95 * body + slap + crack;
  });
};

/** Big type landing: shorter and a little brighter than a stamp. */
const hit = (t0: number, level: number) => {
  let phase = 0;
  add(t0, 0.7, (t) => {
    const f = 50 + 110 * Math.exp(-t / 0.032);
    phase += (2 * Math.PI * f) / SR;
    const body = sat(Math.sin(phase) * Math.exp(-t / 0.18) * Math.min(1, t / 0.001), 2.6);
    const crack = noise() * 0.22 * Math.exp(-t / 0.003);
    return level * 0.8 * (body + crack);
  });
};

/* ------------------------------------------------------------ the mix */

const cues = punchCues();
let tickSide = 1;
for (const c of cues) {
  const t0 = c.frame / FPS;
  if (c.kind === "pulse") kick(t0, (c.accent ? 0.36 : 0.24) * c.level, c.accent);
  if (c.kind === "tick") tick(t0, 0.13 * c.level * (0.8 + rand() * 0.4), (tickSide = -tickSide) * 0.25);
  if (c.kind === "thud") thud(t0);
  if (c.kind === "hit") hit(t0, c.level);
}
// Off-beat shakers through the driving part (not under the closing line or end card).
for (const s of PUNCH_SCHEDULE) {
  if (s.id === "closing" || s.id === "end") continue;
  for (let f = B / 2; f < s.duration; f += B) shaker((s.from + f) / FPS, 0.07);
}
// Short fade at the very end so the file never stops on a click.
const fade = Math.round(0.25 * SR);
for (let i = 0; i < fade; i++) {
  const g = i / fade;
  L[N - 1 - i] *= g;
  R[N - 1 - i] *= g;
}

const writeWav = (file: string, l: Float32Array, r: Float32Array) => {
  let peak = 0;
  for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(l[i]), Math.abs(r[i]));
  const norm = peak > 0 ? 0.7 / peak : 1;
  const buf = Buffer.alloc(44 + N * 4);
  buf.write("RIFF", 0);
  buf.writeUInt32LE(36 + N * 4, 4);
  buf.write("WAVE", 8);
  buf.write("fmt ", 12);
  buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 4, 28);
  buf.writeUInt16LE(4, 32);
  buf.writeUInt16LE(16, 34);
  buf.write("data", 36);
  buf.writeUInt32LE(N * 4, 40);
  for (let i = 0; i < N; i++) {
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, l[i] * norm)) * 32767), 44 + i * 4);
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, r[i] * norm)) * 32767), 46 + i * 4);
  }
  fs.writeFileSync(file, buf);
};
writeWav(rawPath, L, R);

/* --------------------------------------------------- loudness to -16 LUFS */

const ebur = (file: string) => {
  const r = spawnSync("ffmpeg", ["-hide_banner", "-nostats", "-i", file, "-af", "ebur128=peak=true", "-f", "null", "-"], {
    encoding: "utf8",
  });
  const text: string = r.stderr;
  const summary = text.slice(text.lastIndexOf("Summary:"));
  const I = Number(summary.match(/I:\s+(-?[\d.]+) LUFS/)?.[1]);
  const peak = Number(summary.match(/Peak:\s+(-?[\d.]+) dBFS/)?.[1]);
  if (!Number.isFinite(I)) throw new Error(`could not read loudness for ${file}`);
  return { I, peak };
};

let gain = TARGET_LUFS - ebur(rawPath).I;
let result = { I: 0, peak: 0 };
for (let pass = 0; pass < 4; pass++) {
  execFileSync("ffmpeg", [
    "-y", "-loglevel", "error", "-i", rawPath,
    "-af", `volume=${gain.toFixed(2)}dB,alimiter=limit=0.79:attack=2:release=60:level=0`,
    "-ar", String(SR), "-c:a", "pcm_s16le", outPath,
  ]);
  result = ebur(outPath);
  const miss = TARGET_LUFS - result.I;
  if (Math.abs(miss) < 0.3) break;
  gain += miss;
}
console.log(
  `public/punch-audio.wav: ${seconds.toFixed(2)} s, ${cues.length} cues, ` +
    `${result.I.toFixed(1)} LUFS integrated, true peak ${result.peak.toFixed(1)} dBFS (target ${TARGET_LUFS} LUFS)`,
);
