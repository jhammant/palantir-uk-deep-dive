// Renders the poster and a contact sheet (one frame per beat) from a single
// Remotion bundle. Run: npm run stills
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { POSTER_FRAME, STILLS } from "../src/timeline";

const root = process.cwd();
const out = path.join(root, "out");
const frames = path.join(out, "frames");
const bundleDir = path.join(root, "node_modules", ".cache", "stills-bundle");
fs.mkdirSync(frames, { recursive: true });

const remotion = (...args: string[]) => execFileSync("npx", ["remotion", ...args], { stdio: ["ignore", "ignore", "inherit"], cwd: root });

console.log("Bundling…");
remotion("bundle", "--out-dir", bundleDir);

const only = process.argv.slice(2).map(Number).filter((n) => Number.isFinite(n));
const list = only.length ? STILLS.filter((_, i) => only.includes(i)) : STILLS;
for (const s of list) {
  const i = STILLS.indexOf(s);
  const file = path.join(frames, `${String(i).padStart(2, "0")}.png`);
  console.log(`frame ${s.frame}  ${s.label}`);
  remotion("still", bundleDir, "PalantirBill-4x5", file, `--frame=${s.frame}`);
}

if (!only.length) {
  remotion("still", bundleDir, "PalantirBill-4x5", path.join(out, "poster.png"), `--frame=${POSTER_FRAME}`);
  const cols = Math.ceil(STILLS.length / 2);
  execFileSync("ffmpeg", [
    "-y", "-loglevel", "error",
    "-framerate", "1", "-start_number", "0", "-i", path.join(frames, "%02d.png"),
    "-vf", `scale=432:540:flags=lanczos,tile=${cols}x2:padding=12:margin=12:color=0x0b0c0e`,
    "-frames:v", "1", path.join(out, "contact-sheet.png"),
  ]);
  fs.writeFileSync(
    path.join(frames, "index.txt"),
    STILLS.map((s, i) => `${String(i).padStart(2, "0")}  frame ${s.frame}  ${(s.frame / 30).toFixed(1)}s  ${s.label}`).join("\n") + "\n",
  );
  console.log(`Wrote out/poster.png (frame ${POSTER_FRAME}) and out/contact-sheet.png (${STILLS.length} frames)`);
}
