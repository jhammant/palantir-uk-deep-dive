// Renders a poster and a contact sheet (one frame per beat) from one Remotion
// bundle.
//   npm run stills          73-second version -> out/poster.png, out/contact-sheet.png
//   npm run punch:stills    punch cut         -> out/punch-poster.png, out/punch-contact-sheet.png
// Extra numeric arguments render only those still indexes (for quick checks).
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { POSTER_FRAME, STILLS } from "../src/timeline";
import { PUNCH_STILLS, T, punchStart } from "../src/punch/timeline";

const punch = process.argv[2] === "punch";
const args = process.argv.slice(punch ? 3 : 2);
const cfg = punch
  ? {
      id: "PalantirPunch-4x5",
      stills: PUNCH_STILLS,
      poster: punchStart("hook") + T.hook.stamp + 30,
      frames: "punch-frames",
      posterFile: "punch-poster.png",
      sheetFile: "punch-contact-sheet.png",
      rows: 2,
    }
  : { id: "PalantirBill-4x5", stills: STILLS, poster: POSTER_FRAME, frames: "frames", posterFile: "poster.png", sheetFile: "contact-sheet.png", rows: 2 };

const root = process.cwd();
const out = path.join(root, "out");
const frames = path.join(out, cfg.frames);
const bundleDir = path.join(root, "node_modules", ".cache", "stills-bundle");
fs.mkdirSync(frames, { recursive: true });

const remotion = (...a: string[]) => execFileSync("npx", ["remotion", ...a], { stdio: ["ignore", "ignore", "inherit"], cwd: root });

console.log("Bundling…");
remotion("bundle", "--out-dir", bundleDir);

const only = args.map(Number).filter((n) => Number.isFinite(n));
const list = only.length ? cfg.stills.filter((_, i) => only.includes(i)) : cfg.stills;
for (const s of list) {
  const i = cfg.stills.indexOf(s);
  const file = path.join(frames, `${String(i).padStart(2, "0")}.png`);
  console.log(`frame ${s.frame}  ${s.label}`);
  remotion("still", bundleDir, cfg.id, file, `--frame=${s.frame}`);
}

if (!only.length) {
  remotion("still", bundleDir, cfg.id, path.join(out, cfg.posterFile), `--frame=${cfg.poster}`);
  const cols = Math.ceil(cfg.stills.length / cfg.rows);
  execFileSync("ffmpeg", [
    "-y", "-loglevel", "error",
    "-framerate", "1", "-start_number", "0", "-i", path.join(frames, "%02d.png"),
    "-vf", `scale=432:540:flags=lanczos,tile=${cols}x${cfg.rows}:padding=12:margin=12:color=0x0b0c0e`,
    "-frames:v", "1", path.join(out, cfg.sheetFile),
  ]);
  fs.writeFileSync(
    path.join(frames, "index.txt"),
    cfg.stills.map((s, i) => `${String(i).padStart(2, "0")}  frame ${s.frame}  ${(s.frame / 30).toFixed(1)}s  ${s.label}`).join("\n") + "\n",
  );
  console.log(`Wrote out/${cfg.posterFile} (frame ${cfg.poster}) and out/${cfg.sheetFile} (${cfg.stills.length} frames)`);
}
